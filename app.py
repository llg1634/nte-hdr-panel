from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
import webbrowser
import winreg
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


APP_DIR = Path(__file__).resolve().parent
WEB_DIR = APP_DIR / "web"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 22533

CONFIG_SUBDIR = Path("HT") / "Saved" / "Config" / "Windows"
CONFIG_FILE = "Engine.ini"
BACKUP_ROOT = "_nte_hdr_backups"

HUD_REGISTRY_PATH = r"SOFTWARE\NVIDIA Corporation\Global\NGXCore"
HUD_REGISTRY_VALUE = "ShowDlssIndicator"
HUD_ENABLED_VALUE = 0x400
HUD_DISABLED_VALUE = 0

HDR_SECTION = "/Script/Engine.RendererSettings"
HDR_KEYS = (
    "r.HDR.EnableHDROutput",
    "r.HDR.UI.Level",
    "r.HDR.Display.MaxLuminance",
    "r.HDR.Display.MidLuminance",
)


class AppError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def safe_console_log(message: str, *, error: bool = False) -> None:
    stream = sys.stderr if error else sys.stdout
    if stream is None:
        return
    try:
        stream.write(message + "\n")
        stream.flush()
    except Exception:
        pass


def now_id() -> str:
    stamp = datetime.now()
    return stamp.strftime("%Y%m%d-%H%M%S") + f"-{stamp.microsecond // 1000:03d}"


def default_config_dir() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        return Path("%LOCALAPPDATA%") / CONFIG_SUBDIR
    return Path(local) / CONFIG_SUBDIR


def expand_path(value: str | None) -> Path:
    if value and value.strip():
        return Path(os.path.expandvars(value.strip().strip('"'))).expanduser()
    return default_config_dir()


def engine_path(config_dir_value: str | None = None) -> Path:
    base = expand_path(config_dir_value)
    if base.name.lower() == CONFIG_FILE.lower():
        return base
    return base / CONFIG_FILE


def config_dir_from_value(config_dir_value: str | None = None) -> Path:
    path = expand_path(config_dir_value)
    if path.name.lower() == CONFIG_FILE.lower():
        return path.parent
    return path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def set_writable(path: Path) -> None:
    if path.exists():
        path.chmod(path.stat().st_mode | stat.S_IWRITE)


def set_readonly(path: Path, enabled: bool) -> None:
    if not path.exists():
        return
    mode = path.stat().st_mode
    if enabled:
        path.chmod(mode & ~stat.S_IWRITE)
    else:
        path.chmod(mode | stat.S_IWRITE)


def is_readonly(path: Path) -> bool:
    if not path.exists():
        return False
    return not bool(path.stat().st_mode & stat.S_IWRITE)


def read_text_best_effort(path: Path, max_bytes: int = 64 * 1024) -> str:
    raw = path.read_bytes()[:max_bytes]
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def classify_engine_content(text: str) -> str:
    if f"[{HDR_SECTION}]" in text and "r.HDR.EnableHDROutput=1" in text:
        return "hdr-config"
    if re.search(r"^\s*\[[^\]]+\]\s*$", text, re.M):
        return "plain-ini"
    compact = "".join(text.split())
    if compact and re.fullmatch(r"[A-Za-z0-9+/=]+", compact):
        return "game-generated-or-encoded"
    return "plain-text-or-unknown"


def parse_hdr_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in HDR_KEYS:
        match = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", text, re.M)
        if match:
            values[key] = match.group(1)
    return values


def file_record(path: Path) -> dict:
    record = {
        "path": str(path),
        "existed": path.exists(),
    }
    if not path.exists():
        return record
    stat_result = path.stat()
    text = read_text_best_effort(path)
    record.update(
        {
            "size": stat_result.st_size,
            "modified": datetime.fromtimestamp(stat_result.st_mtime).isoformat(timespec="seconds"),
            "sha256": sha256(path),
            "readonly": is_readonly(path),
            "attributes": str(getattr(stat_result, "st_file_attributes", "")),
            "kind": classify_engine_content(text),
            "hdrValues": parse_hdr_values(text),
            "preview": "\n".join(text.splitlines()[:8]),
        }
    )
    return record


def copy_to_backup(source: Path, backup_dir: Path) -> dict:
    record = file_record(source)
    if source.exists():
        shutil.copy2(source, backup_dir / source.name)
        record["backup"] = source.name
    return record


def list_backups(config_dir: Path) -> list[dict]:
    root = config_dir / BACKUP_ROOT
    if not root.is_dir():
        return []

    rows = []
    for folder in sorted(root.iterdir(), reverse=True):
        manifest = folder / "manifest.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        files = data.get("files", {})
        engine = files.get(CONFIG_FILE, {})
        rows.append(
            {
                "name": folder.name,
                "path": str(folder),
                "created": data.get("created"),
                "settings": data.get("settings", {}),
                "setReadOnly": data.get("setReadOnly"),
                "engineExisted": engine.get("existed"),
                "engineKind": engine.get("kind"),
                "operations": data.get("operations", []),
            }
        )
    return rows


def is_non_hdr_backup(backup: dict) -> bool:
    if not backup.get("engineExisted"):
        return False
    if backup.get("engineKind") == "hdr-config":
        return False
    return True


def find_original_backup(config_dir: Path) -> dict | None:
    candidates = list_backups(config_dir)
    # "Original" means the oldest available backup that existed before the tool
    # wrote HDR settings and did not itself contain HDR renderer parameters.
    original = [backup for backup in candidates if is_non_hdr_backup(backup)]
    if not original:
        return None
    return sorted(original, key=lambda item: item["name"])[0]


def running_processes() -> list[dict]:
    if os.name != "nt":
        return []

    # Only query ordinary process metadata. Do not inspect modules; some game
    # protections treat low-level inspection tools as suspicious.
    command = (
        "Get-Process HTGame,NTEGame,NTEBrowser,NTEWebBooster -ErrorAction SilentlyContinue | "
        "Select-Object ProcessName,Id,MainWindowTitle,StartTime | ConvertTo-Json -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=6,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        data = json.loads(proc.stdout)
        if isinstance(data, dict):
            data = [data]
        return data
    except Exception:
        return []


def read_hud_status() -> dict:
    if os.name != "nt":
        return {
            "available": False,
            "enabled": False,
            "value": None,
            "path": f"HKLM\\{HUD_REGISTRY_PATH}",
            "valueName": HUD_REGISTRY_VALUE,
            "message": "NVIDIA HUD 注册表只支持 Windows。",
        }
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, HUD_REGISTRY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, HUD_REGISTRY_VALUE)
        value_int = int(value)
        return {
            "available": True,
            "enabled": value_int != HUD_DISABLED_VALUE,
            "value": value_int,
            "mode": "EnabledAllDlls" if value_int == HUD_ENABLED_VALUE else ("Disabled" if value_int == 0 else "Custom"),
            "path": f"HKLM\\{HUD_REGISTRY_PATH}",
            "valueName": HUD_REGISTRY_VALUE,
            "message": "NVIDIA DLSS HUD 已开启。" if value_int != 0 else "NVIDIA DLSS HUD 未开启。",
        }
    except FileNotFoundError:
        return {
            "available": True,
            "enabled": False,
            "value": None,
            "mode": "Missing",
            "path": f"HKLM\\{HUD_REGISTRY_PATH}",
            "valueName": HUD_REGISTRY_VALUE,
            "message": "未找到 HUD 注册表值；开启时会自动创建。",
        }
    except PermissionError:
        return {
            "available": False,
            "enabled": False,
            "value": None,
            "path": f"HKLM\\{HUD_REGISTRY_PATH}",
            "valueName": HUD_REGISTRY_VALUE,
            "message": "没有权限读取 NVIDIA HUD 注册表。",
        }


def write_hud_status(enabled: bool) -> dict:
    if os.name != "nt":
        raise AppError("NVIDIA HUD 开关只支持 Windows。")
    try:
        access = winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, HUD_REGISTRY_PATH, 0, access) as key:
            winreg.SetValueEx(
                key,
                HUD_REGISTRY_VALUE,
                0,
                winreg.REG_DWORD,
                HUD_ENABLED_VALUE if enabled else HUD_DISABLED_VALUE,
            )
    except PermissionError as exc:
        raise AppError("没有权限写入 NVIDIA HUD 注册表。请用管理员权限运行 run_as_admin.bat 或打包 exe。", 403) from exc
    return read_hud_status()


def normalize_number(value: object, label: str, minimum: float, maximum: float, default: float) -> str:
    if value is None or str(value).strip() == "":
        number = default
    else:
        raw = str(value).strip().lower().replace("nits", "").replace("nit", "")
        try:
            number = float(raw)
        except ValueError as exc:
            raise AppError(f"{label} 不是有效数字。") from exc
    if number < minimum or number > maximum:
        raise AppError(f"{label} 需要在 {minimum:g} 到 {maximum:g} 之间。")
    if abs(number - round(number)) < 0.000001:
        return str(int(round(number)))
    return f"{number:.4f}".rstrip("0").rstrip(".")


def build_hdr_ini(settings: dict) -> tuple[str, dict[str, str]]:
    max_luminance = normalize_number(settings.get("maxLuminance"), "显示器最大亮度", 80, 10000, 1000)
    mid_luminance = normalize_number(settings.get("midLuminance"), "中间亮度参考值", 1, 2000, 18)
    ui_level = normalize_number(settings.get("uiLevel"), "UI 亮度", 0.1, 10, 1.0)
    if ui_level == "1":
        ui_level = "1.0"
    normalized = {
        "maxLuminance": max_luminance,
        "midLuminance": mid_luminance,
        "uiLevel": ui_level,
    }
    text = (
        f"[{HDR_SECTION}]\n"
        "r.HDR.EnableHDROutput=1\n"
        f"r.HDR.UI.Level={ui_level}\n"
        f"r.HDR.Display.MaxLuminance={max_luminance}\n"
        f"r.HDR.Display.MidLuminance={mid_luminance}\n"
    )
    return text, normalized


def inspect_config(config_dir_value: str | None = None) -> dict:
    config_dir = config_dir_from_value(config_dir_value)
    original_backup = find_original_backup(config_dir) if config_dir.is_dir() else None
    engine = config_dir / CONFIG_FILE
    info = {
        "defaultConfigDir": str(default_config_dir()),
        "configDir": str(config_dir),
        "configDirExists": config_dir.is_dir(),
        "engine": file_record(engine),
        "backups": list_backups(config_dir),
        "originalBackup": original_backup,
        "processes": running_processes(),
        "hud": read_hud_status(),
    }
    engine_info = info["engine"]
    kind = engine_info.get("kind")
    values = engine_info.get("hdrValues") or {}
    has_hdr = values.get("r.HDR.EnableHDROutput") == "1"
    info["summary"] = {
        "hasHdr": has_hdr,
        "kind": kind,
        "protectedByReadonly": bool(engine_info.get("readonly")),
        "needsGameRun": not info["configDirExists"],
        "looksGameGenerated": kind == "game-generated-or-encoded",
        "hasOriginalBackup": bool(original_backup),
    }
    return info


def apply_hdr_config(config_dir_value: str | None, settings: dict) -> dict:
    config_dir = config_dir_from_value(config_dir_value)
    if not config_dir.is_dir():
        raise AppError("配置目录不存在。请先启动一次异环并进入游戏，让它生成配置目录。")

    engine = config_dir / CONFIG_FILE
    backup_dir = config_dir / BACKUP_ROOT / now_id()
    backup_dir.mkdir(parents=True, exist_ok=True)

    text, normalized = build_hdr_ini(settings or {})
    set_protection = bool((settings or {}).get("readOnly", True))
    manifest = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "tool": "nte-hdr-panel",
        "configDir": str(config_dir),
        "settings": normalized,
        "setReadOnly": set_protection,
        "files": {},
        "operations": [],
    }

    manifest["files"][CONFIG_FILE] = copy_to_backup(engine, backup_dir)
    manifest["operations"].append("备份 Engine.ini" if engine.exists() else "记录 Engine.ini 原本不存在")
    if engine.exists():
        set_writable(engine)

    engine.write_text(text, encoding="ascii", newline="\n")
    manifest["operations"].append("写入 UE HDR RendererSettings")
    set_readonly(engine, set_protection)
    manifest["operations"].append("设置 Engine.ini 只读保护" if set_protection else "保持 Engine.ini 可写")

    (backup_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "ok": True,
        "message": "已写入原生 HDR 配置。",
        "backup": str(backup_dir),
        "operations": manifest["operations"],
        "status": inspect_config(str(config_dir)),
    }


def restore_backup(config_dir_value: str | None, backup_name: str | None = None) -> dict:
    config_dir = config_dir_from_value(config_dir_value)
    if not config_dir.is_dir():
        raise AppError("配置目录不存在，无法恢复。")

    backups = list_backups(config_dir)
    if not backups:
        raise AppError("没有找到可恢复的 HDR 备份。")
    selected = backup_name or backups[0]["name"]
    backup_dir = config_dir / BACKUP_ROOT / selected
    manifest_path = backup_dir / "manifest.json"
    if not manifest_path.is_file():
        raise AppError("备份清单不存在。")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = manifest.get("files", {}).get(CONFIG_FILE, {})
    target = config_dir / CONFIG_FILE
    if target.exists():
        set_writable(target)

    operations = []
    if record.get("existed") and record.get("backup"):
        shutil.copy2(backup_dir / record["backup"], target)
        set_readonly(target, bool(record.get("readonly")))
        operations.append("恢复原 Engine.ini")
    elif target.exists():
        target.unlink()
        operations.append("删除工具创建的 Engine.ini")
    else:
        operations.append("Engine.ini 原本不存在，无需恢复")

    return {
        "ok": True,
        "message": f"已恢复备份 {selected}。",
        "restoredBackup": str(backup_dir),
        "operations": operations,
        "status": inspect_config(str(config_dir)),
    }


def restore_original_backup(config_dir_value: str | None) -> dict:
    config_dir = config_dir_from_value(config_dir_value)
    if not config_dir.is_dir():
        raise AppError("配置目录不存在，无法恢复原版配置。")

    original = find_original_backup(config_dir)
    if not original:
        raise AppError("没有找到未配置 HDR 的原版备份。")

    result = restore_backup(str(config_dir), original["name"])
    result["message"] = f"已恢复未配置 HDR 的原版配置：{original['name']}。"
    result["originalBackup"] = original
    return result


def set_engine_protection(config_dir_value: str | None, read_only: bool) -> dict:
    engine = engine_path(config_dir_value)
    if not engine.exists():
        raise AppError("Engine.ini 不存在，无法设置只读。")
    set_readonly(engine, read_only)
    return {
        "ok": True,
        "message": "已开启只读保护。" if read_only else "已关闭只读保护。",
        "status": inspect_config(str(engine.parent)),
    }


def run_native_folder_dialog() -> str | None:
    if os.name != "nt":
        raise AppError("原生文件夹选择器只支持 Windows。")

    script = r"""
Add-Type -AssemblyName System.Windows.Forms
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = '选择异环配置目录，通常是 %LOCALAPPDATA%\HT\Saved\Config\Windows'
$dialog.ShowNewFolderButton = $false
$form = New-Object System.Windows.Forms.Form
$form.TopMost = $true
$form.ShowInTaskbar = $false
$form.Width = 1
$form.Height = 1
$form.StartPosition = 'CenterScreen'
$result = $dialog.ShowDialog($form)
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $dialog.SelectedPath
}
"""
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise AppError(proc.stderr.strip() or "文件夹选择器启动失败。")
    selected = proc.stdout.strip()
    return selected or None


def schedule_shutdown(server: ThreadingHTTPServer) -> None:
    def worker() -> None:
        time.sleep(0.35)
        safe_console_log("Shutdown requested from WebUI.")
        server.shutdown()

    threading.Thread(target=worker, name="nte-hdr-shutdown", daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    server_version = "NTEHDRPanel/0.1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        safe_console_log("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def send_json(self, data: object, status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)
        try:
            self.wfile.flush()
        except OSError:
            pass

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise AppError("请求 JSON 无效。") from exc

    def handle_error(self, exc: Exception) -> None:
        if isinstance(exc, AppError):
            self.send_json({"ok": False, "error": str(exc)}, exc.status)
        else:
            self.send_json({"ok": False, "error": f"内部错误: {exc}"}, 500)

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/api/state":
                query = parse_qs(parsed.query)
                self.send_json({"ok": True, **inspect_config(query.get("configDir", [None])[0])})
                return
            if parsed.path == "/api/hud":
                self.send_json({"ok": True, "hud": read_hud_status()})
                return

            rel = unquote(parsed.path.lstrip("/")) or "index.html"
            target = (WEB_DIR / rel).resolve()
            if not str(target).startswith(str(WEB_DIR.resolve())) or not target.is_file():
                target = WEB_DIR / "index.html"
            content = target.read_bytes()
            mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as exc:
            self.handle_error(exc)

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            data = self.read_json()
            if parsed.path == "/api/browse":
                selected = run_native_folder_dialog()
                self.send_json({"ok": True, "path": selected, "cancelled": selected is None})
                return
            if parsed.path == "/api/detect":
                self.send_json({"ok": True, "status": inspect_config(data.get("configDir"))})
                return
            if parsed.path == "/api/apply":
                self.send_json(apply_hdr_config(data.get("configDir"), data))
                return
            if parsed.path == "/api/restore":
                self.send_json(restore_backup(data.get("configDir"), data.get("backup")))
                return
            if parsed.path == "/api/restore-original":
                self.send_json(restore_original_backup(data.get("configDir")))
                return
            if parsed.path == "/api/protect":
                self.send_json(set_engine_protection(data.get("configDir"), bool(data.get("readOnly"))))
                return
            if parsed.path == "/api/hud":
                self.send_json({"ok": True, "hud": write_hud_status(bool(data.get("enabled")))})
                return
            if parsed.path == "/api/shutdown":
                self.send_json(
                    {
                        "ok": True,
                        "message": "后端服务正在退出。浏览器页面可以关闭；再次使用时重新运行 NTEHDRPanel。",
                    }
                )
                schedule_shutdown(self.server)
                return
            raise AppError("未知 API。", 404)
        except Exception as exc:
            self.handle_error(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Neverness To Everness Native HDR WebUI")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not WEB_DIR.is_dir():
        safe_console_log("web directory missing", error=True)
        return 1

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    safe_console_log(f"异环原生 HDR Panel running at {url}")
    safe_console_log("Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        safe_console_log("Stopping...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
