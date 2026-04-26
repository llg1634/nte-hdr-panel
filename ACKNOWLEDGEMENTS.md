# 参考与致谢

## 相关社区工具

这些项目不是本工具的依赖，也没有被打包进本仓库；它们是 PC 游戏画质调整、DLSS 调整、HDR 改造领域的重要社区项目。本文档列出它们，是为了说明本工具和这些方案的边界。

### DLSSTweaks

- 项目：https://github.com/emoose/DLSSTweaks
- 发布页：https://www.nexusmods.com/site/mods/550
- 作者：emoose
- 定位：DLSS wrapper / tweak 工具，可调整 DLSS scaling ratios、DLSS presets、DLAA 等。

本项目没有包含 DLSSTweaks DLL，也不会写入 `dlsstweaks.ini`、`winmm.dll`、`dxgi.dll`、`nvngx.dll`。  
本项目只处理异环本地 UE 配置文件 `Engine.ini`。

### RenoDX

- 项目：https://github.com/clshortfuse/renodx
- Wiki：https://github.com/clshortfuse/renodx/wiki/Mods
- 作者 / 维护者：ShortFuse / RenoDX contributors
- 定位：DirectX 游戏画面改造工具集，常用于 HDR / tonemapping / shader 改造，并基于 ReShade add-on 系统工作。

本项目不是 RenoDX add-on，不注入 shader，不改 swapchain，不做 tonemapping retrofit。  
异环这里采用的是 UE 已存在的 HDR 输出配置开关。

### ReShade

- 项目：https://github.com/crosire/reshade
- 官网：https://reshade.me/
- 作者：crosire / ReShade contributors
- 定位：通用 post-processing injector 和 shader/effect 平台。

本项目不是 ReShade preset，不加载 ReShade，不使用 ReShade add-on API。  
它不会做后处理滤镜，也不会对画面进行色彩 LUT 或 shader 处理。

### Special K

- 项目：https://github.com/SpecialKO/SpecialK
- 官网：https://www.special-k.info/
- 作者：Kaldaien / Special K contributors
- 定位：PC 游戏增强和诊断工具，包含性能分析、注入、HDR 改造等能力。

本项目不是 Special K 插件，也不会使用 Special K 的 local/global injection。  
它只写入游戏用户配置目录里的 `Engine.ini`。

## 同作者参考项目

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
