# GitHub 上传指南

## 上传前检查

确认这些文件存在：

```text
README.md
README.en.md
CHANGELOG.md
LICENSE
NOTICE.md
CONTRIBUTING.md
SECURITY.md
requirements.txt
run.bat
run_as_admin.bat
build_exe.bat
app.py
web/index.html
web/styles.css
web/app.js
docs/
```

## 推荐中文名

```text
异环原生 HDR 一键开启工具
```

短名：

```text
异环 HDR 面板
```

英文名：

```text
NTE HDR Panel
```

## 推荐仓库名

```text
nte-hdr-panel
```

## 推荐仓库描述

```text
异环原生 HDR 一键开启工具 / NTE HDR Panel：写入 UE Engine.ini HDR 输出配置，支持备份恢复、只读保护和 NVIDIA HUD 验证。
```

## 推荐 Topics

```text
nte
neverness-to-everness
ananta
hdr
native-hdr
windows-hdr
dx12
unreal-engine
unreal-engine-hdr
engine-ini
nvidia-hud
windows
local-webui
```

## 发布 Release

1. 运行 `build_exe.bat`。
2. 压缩 `dist\NTEHDRPanel`。
3. 命名为 `NTEHDRPanel-v版本号.zip`。
4. 在 GitHub Releases 上传 zip。
5. Release notes 使用 `packaging/release-notes-template.md`。
