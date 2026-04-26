const state = {
  configDir: "",
  backups: [],
};

const $ = (id) => document.getElementById(id);

const configPath = $("configPath");
const maxLuminance = $("maxLuminance");
const midLuminance = $("midLuminance");
const uiLevel = $("uiLevel");
const readOnly = $("readOnly");
const peakPreview = $("peakPreview");
const detectCard = $("detectCard");
const hudCard = $("hudCard");
const statusStrip = $("statusStrip");
const backupSelect = $("backupSelect");
const backupDetails = $("backupDetails");
const logBox = $("logBox");
const filePlan = $("filePlan");
const assetPill = $("assetPill");
const toast = $("toast");

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function setBusy(isBusy) {
  for (const button of document.querySelectorAll("button")) {
    button.disabled = isBusy;
  }
}

function formatPath(path) {
  return path || "未找到";
}

function renderEngine(engine, summary) {
  if (!engine?.existed) {
    return "Engine.ini 不存在。开服后进入过大世界通常会自动创建，也可以由本工具新建。";
  }
  const hdr = summary?.hasHdr ? "已包含 HDR 参数" : "未检测到 HDR 明文参数";
  const lock = engine.readonly ? "只读保护已开启" : "未只读";
  return `
    文件：<code>${formatPath(engine.path)}</code><br>
    类型：${engine.kind || "unknown"}，大小：${engine.size} bytes，${lock}<br>
    状态：${hdr}<br>
    修改时间：${engine.modified || "未知"}
  `;
}

function renderDetection(status) {
  state.configDir = status.configDir;
  configPath.value = status.configDir;
  const summary = status.summary || {};
  const running = status.processes?.length
    ? status.processes.map((p) => `${p.ProcessName}#${p.Id}${p.MainWindowTitle ? `(${p.MainWindowTitle})` : ""}`).join(", ")
    : "未检测到异环进程";

  detectCard.classList.toggle("muted", !status.configDirExists);
  detectCard.innerHTML = `
    <strong>${status.configDirExists ? "配置目录已找到" : "配置目录不存在"}</strong><br>
    目录：<code>${status.configDir}</code><br>
    ${renderEngine(status.engine, summary)}<br>
    运行进程：${running}
  `;

  const enginePath = `${status.configDir}\\Engine.ini`;
  filePlan.innerHTML = `
    <strong>写入和备份范围</strong><br>
    目标文件：<code>${enginePath}</code><br>
    备份目录：<code>${status.configDir}\\_nte_hdr_backups\\时间戳</code><br>
    恢复方式：读取 <code>manifest.json</code>，存在则复制回原文件，不存在则删除工具创建的文件。<br>
    安全策略：不读游戏模块，不注入进程，不修改游戏安装目录。
  `;

  renderBackups(status.backups || [], status.configDir);
  renderStatus(status);
  renderHud(status.hud);
}

function renderStatus(status) {
  const parts = [];
  if (!status.configDirExists) parts.push("配置目录缺失");
  if (status.summary?.hasHdr) parts.push("HDR 参数存在");
  if (status.summary?.looksGameGenerated) parts.push("当前像游戏原始编码配置");
  if (status.summary?.protectedByReadonly) parts.push("只读保护");
  if (status.processes?.length) parts.push("检测到异环相关进程");
  statusStrip.innerHTML = parts.map((part) => `<span>${part}</span>`).join("");
  const engine = status.engine || {};
  logBox.textContent = engine.preview || "暂无 Engine.ini 预览。";
}

function renderBackups(backups, configDir) {
  state.backups = backups;
  backupSelect.innerHTML = "";
  if (!backups.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "暂无备份";
    backupSelect.append(option);
    backupDetails.classList.add("muted");
    backupDetails.innerHTML = `
      备份位置：<code>${configDir || "<ConfigDir>"}\\_nte_hdr_backups</code><br>
      第一次写入 HDR 时会自动创建。
    `;
    return;
  }
  for (const backup of backups) {
    const option = document.createElement("option");
    option.value = backup.name;
    option.textContent = `${backup.name}${backup.setReadOnly ? " (写入只读)" : ""}`;
    backupSelect.append(option);
  }
  backupDetails.classList.remove("muted");
  renderBackupDetails();
}

function renderBackupDetails() {
  const selected = state.backups.find((item) => item.name === backupSelect.value) || state.backups[0];
  if (!selected) return;
  const settings = selected.settings || {};
  const ops = selected.operations?.length ? selected.operations.join(" / ") : "无操作摘要";
  backupDetails.innerHTML = `
    <strong>所选备份</strong>：${selected.name}<br>
    路径：<code>${selected.path}</code><br>
    原文件：${selected.engineExisted ? selected.engineKind || "存在" : "原本不存在"}<br>
    写入参数：Max ${settings.maxLuminance || "-"} / Mid ${settings.midLuminance || "-"} / UI ${settings.uiLevel || "-"}<br>
    动作：${ops}
  `;
}

function renderHud(hud) {
  if (!hud) {
    hudCard.classList.add("muted");
    hudCard.textContent = "未读取到 HUD 状态。";
    return;
  }
  hudCard.classList.toggle("muted", !hud.enabled);
  const valueText = hud.value === null || hud.value === undefined ? "未创建" : hud.value;
  hudCard.innerHTML = `
    <strong>NVIDIA HUD：${hud.enabled ? "已开启" : "未开启"}</strong><br>
    注册表：<code>${hud.path}\\${hud.valueName}</code><br>
    当前值：<code>${valueText}</code>，模式：${hud.mode || "Unknown"}<br>
    ${hud.message || ""}
  `;
}

async function refreshState(showMessage = false) {
  try {
    const query = configPath.value.trim() ? `?configDir=${encodeURIComponent(configPath.value.trim())}` : "";
    const data = await request(`/api/state${query}`);
    renderDetection(data);
    assetPill.textContent = data.summary?.hasHdr ? "HDR config detected" : "ready";
    if (showMessage) showToast("状态已刷新。");
  } catch (error) {
    detectCard.classList.add("muted");
    detectCard.textContent = error.message;
    showToast(error.message);
  }
}

function currentPayload() {
  return {
    configDir: configPath.value.trim(),
    maxLuminance: maxLuminance.value.trim(),
    midLuminance: midLuminance.value.trim(),
    uiLevel: uiLevel.value.trim(),
    readOnly: readOnly.checked,
  };
}

async function browsePath() {
  setBusy(true);
  try {
    const data = await request("/api/browse", { method: "POST", body: "{}" });
    if (!data.cancelled && data.path) {
      configPath.value = data.path;
      await refreshState(true);
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(false);
  }
}

async function applyHdr() {
  setBusy(true);
  try {
    const data = await request("/api/apply", {
      method: "POST",
      body: JSON.stringify(currentPayload()),
    });
    renderDetection(data.status);
    showToast("HDR 配置已写入，启动游戏验证。");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(false);
  }
}

async function restoreBackup() {
  if (!backupSelect.value) {
    showToast("没有可恢复的备份。");
    return;
  }
  setBusy(true);
  try {
    const data = await request("/api/restore", {
      method: "POST",
      body: JSON.stringify({ configDir: configPath.value.trim(), backup: backupSelect.value }),
    });
    renderDetection(data.status);
    showToast("已恢复所选备份。");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(false);
  }
}

async function setProtection(enabled) {
  setBusy(true);
  try {
    const data = await request("/api/protect", {
      method: "POST",
      body: JSON.stringify({ configDir: configPath.value.trim(), readOnly: enabled }),
    });
    renderDetection(data.status);
    showToast(enabled ? "只读已开启。" : "只读已关闭。");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(false);
  }
}

async function setHud(enabled) {
  setBusy(true);
  try {
    const data = await request("/api/hud", {
      method: "POST",
      body: JSON.stringify({ enabled }),
    });
    renderHud(data.hud);
    showToast(enabled ? "HUD 已开启。" : "HUD 已关闭。");
  } catch (error) {
    showToast(error.message);
  } finally {
    setBusy(false);
  }
}

async function shutdown() {
  try {
    const data = await request("/api/shutdown", { method: "POST", body: "{}" });
    showToast(data.message || "后端正在退出。");
  } catch (error) {
    showToast(error.message);
  }
}

function applyPreset(button) {
  maxLuminance.value = button.dataset.max;
  midLuminance.value = button.dataset.mid;
  uiLevel.value = button.dataset.ui;
  peakPreview.textContent = button.dataset.max;
  document.querySelectorAll(".preset").forEach((item) => item.classList.toggle("active", item === button));
}

function toggleTheme() {
  const root = document.documentElement;
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("nte-hdr-theme", root.dataset.theme);
}

function copyPath() {
  navigator.clipboard.writeText(configPath.value || "").then(
    () => showToast("路径已复制。"),
    () => showToast("复制失败，请手动复制。"),
  );
}

$("themeToggle").addEventListener("click", toggleTheme);
$("shutdownBtn").addEventListener("click", shutdown);
$("browseBtn").addEventListener("click", browsePath);
$("detectBtn").addEventListener("click", () => refreshState(true));
$("openDirBtn").addEventListener("click", copyPath);
$("applyBtn").addEventListener("click", applyHdr);
$("restoreBtn").addEventListener("click", restoreBackup);
$("protectBtn").addEventListener("click", () => setProtection(true));
$("unprotectBtn").addEventListener("click", () => setProtection(false));
$("refreshHudBtn").addEventListener("click", () => refreshState(true));
$("enableHudBtn").addEventListener("click", () => setHud(true));
$("disableHudBtn").addEventListener("click", () => setHud(false));
backupSelect.addEventListener("change", renderBackupDetails);
maxLuminance.addEventListener("input", () => {
  peakPreview.textContent = maxLuminance.value || "1000";
});
document.querySelectorAll(".preset").forEach((button) => {
  button.addEventListener("click", () => applyPreset(button));
});

const savedTheme = localStorage.getItem("nte-hdr-theme");
if (savedTheme) document.documentElement.dataset.theme = savedTheme;
refreshState();
