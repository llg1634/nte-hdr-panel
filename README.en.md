# NTE HDR Panel

Chinese name: **异环原生 HDR 一键开启工具**  
Short name: **异环 HDR 面板**  
English name: **NTE HDR Panel**

Search keywords: NTE HDR, Neverness To Everness HDR, Ananta HDR, native HDR, UE HDR, Unreal Engine HDR, Engine.ini HDR, HDR Mode Custom, DX12 HDR, Windows HDR.

This is a local WebUI for enabling Unreal Engine native HDR output in Neverness To Everness / Ananta. It writes HDR renderer settings to the local `Engine.ini`, creates manifest-based backups, restores previous state, applies optional read-only protection, and provides an NVIDIA HUD toggle for verification.

## Credits

The local WebUI structure, manifest-based backup / restore workflow, HUD verification flow, backend shutdown action, and GitHub-ready documentation layout are based on the author's related project:

- [llg1634/nte-dlss-panel](https://github.com/llg1634/nte-dlss-panel)

The two projects have different scopes:

- `nte-dlss-panel`: DLSS / DLSSTweaks low render scale deployment for NTE.
- `nte-hdr-panel`: UE native HDR `Engine.ini` configuration for NTE.

Local URL:

```text
http://127.0.0.1:22533
```

This is not an online service. The browser page is only the frontend. The local Python / exe backend handles file detection, backup, write, restore, and HUD registry operations. Closing the browser tab does not stop the backend; use the "Exit Tool" button in the UI.

## Scope

The tool only modifies:

```text
%LOCALAPPDATA%\HT\Saved\Config\Windows\Engine.ini
```

It does not copy DLL files, modify the game installation directory, or inject into the game process.

## Written Settings

Default output:

```ini
[/Script/Engine.RendererSettings]
r.HDR.EnableHDROutput=1
r.HDR.UI.Level=1.0
r.HDR.Display.MaxLuminance=1000
r.HDR.Display.MidLuminance=18
```

## Tested Behavior

Local testing showed this behavior:

1. The game-generated `Engine.ini` can be an encoded 200-byte file.
2. A plain HDR `Engine.ini` without read-only protection may be deleted or rewritten during game startup.
3. Writing the HDR config and then marking `Engine.ini` as read-only keeps the config in place.
4. NVIDIA HUD can show `DX12` and `HDR Mode: Custom` when the chain is active.

For that reason, the UI enables read-only protection by default.

## Quick Start

1. Run `NTEHDRPanel.exe` or `run.bat`.
2. Open `http://127.0.0.1:22533`.
3. Click "Detect Config".
4. Start with `1000 / 18 / 1.0`.
5. Keep "read-only after write" enabled.
6. Click "Backup and write native HDR".
7. Launch the game and verify `DX12` / `D3D12` and `HDR Mode: Custom` with NVIDIA HUD.

If the HUD toggle cannot write the registry, run `run_as_admin.bat`.

## Backups

Each write creates:

```text
%LOCALAPPDATA%\HT\Saved\Config\Windows\_nte_hdr_backups\<timestamp>
```

The backup contains `manifest.json` and the original `Engine.ini` when it existed. Restore follows the manifest instead of blindly deleting files.

## Build

```bat
build_exe.bat
```

Output:

```text
dist\NTEHDRPanel\NTEHDRPanel.exe
```
