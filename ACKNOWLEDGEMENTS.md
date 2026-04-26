# 参考与致谢

## nte-dlss-panel

本项目的产品结构参考了同作者项目：

```text
https://github.com/llg1634/nte-dlss-panel
```

参考内容包括：

- 本地 WebUI + Python 后端的组织方式。
- 首页按 01-05 功能区解释流程。
- manifest 备份和按清单恢复的设计。
- NVIDIA HUD 状态检测和开关。
- WebUI 内“退出工具”按钮，避免只关闭网页后后端继续运行。
- README、docs、CHANGELOG、NOTICE、SECURITY、CONTRIBUTING、GitHub Actions 等 GitHub-ready 文件组织。

## 差异说明

`nte-dlss-panel` 面向异环 DLSS / DLSSTweaks 低渲染比例部署，会处理游戏 Win64 目录和 DLSSTweaks 文件。

`nte-hdr-panel` 面向异环 UE 原生 HDR 配置，只处理：

```text
%LOCALAPPDATA%\HT\Saved\Config\Windows\Engine.ini
```

本项目不包含 DLSSTweaks DLL，不复制 DLL，不修改游戏安装目录，不注入游戏进程。
