# 异环原生 HDR 一键开启工具 / NTE HDR Panel vX.Y.Z

## 这是什么

异环原生 HDR 一键开启工具，用于写入 UE `Engine.ini` HDR 输出配置，支持备份、恢复、只读保护和 NVIDIA HUD 验证。

搜索关键词：异环 HDR、异环原生 HDR、异环怎么开 HDR、异环 HDR Mode Custom、异环 Engine.ini HDR、NTE HDR Panel。

## 使用方法

1. 下载 `NTEHDRPanel-vX.Y.Z.zip`。
2. 解压。
3. 双击 `NTEHDRPanel.exe`。
4. 打开页面后点击“检测配置”。
5. 点击“备份并写入原生 HDR”。

## 修改范围

```text
%LOCALAPPDATA%\HT\Saved\Config\Windows\Engine.ini
```

可选 HUD 注册表：

```text
HKLM\SOFTWARE\NVIDIA Corporation\Global\NGXCore\ShowDlssIndicator
```

## 验证

NVIDIA HUD 中看到：

```text
DX12 / D3D12
HDR Mode: Custom
```

## 恢复

面板里选择备份并点击“恢复所选备份”。

## 参考与致谢

相关社区工具引用和区分：

```text
DLSSTweaks: https://github.com/emoose/DLSSTweaks
RenoDX: https://github.com/clshortfuse/renodx
ReShade: https://github.com/crosire/reshade
Special K: https://github.com/SpecialKO/SpecialK
```

本项目不包含这些项目的二进制文件，不注入游戏进程，不修改游戏安装目录。

本项目的 WebUI、manifest 备份恢复、HUD 验证和 GitHub-ready 文档组织参考：

```text
https://github.com/llg1634/nte-dlss-panel
```
