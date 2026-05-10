# 异环原生 HDR 一键开启工具

中文名：**异环原生 HDR 一键开启工具**  
短名：**异环 HDR 面板**  
英文名：**NTE HDR Panel**

**搜索关键词**：异环 HDR 一键、异环原生 HDR、异环怎么开 HDR、异环 HDR 开启教程、异环 HDR Mode Custom、异环 Engine.ini HDR、异环 UE HDR、异环 DX12 HDR、异环 Windows HDR、NTE HDR Panel、Neverness To Everness HDR、Ananta HDR、UE HDR、Unreal Engine HDR、Engine.ini HDR。

异环（Neverness To Everness / Ananta）原生 HDR 本地 WebUI。它用于把 UE RendererSettings 的 HDR 输出参数写入本机 `Engine.ini`，并提供备份、恢复、只读保护和 NVIDIA HUD 验证。适合搜索“异环如何开启原生 HDR”“异环 HDR Mode Custom”“异环 Engine.ini HDR”的玩家。

English README: [README.en.md](README.en.md)

Local URL:

```text
http://127.0.0.1:22533
```

它不是在线服务，只在本机运行。网页负责显示和发起操作，Python / exe 后端负责文件检测、备份、写入、恢复和 HUD 开关。只关闭浏览器标签页不会退出后端服务，需要在面板里点“退出工具”。

## 项目定位

这个项目的重点不是“通用 HDR 注入器”，而是把异环这个具体场景里的 UE 原生 HDR 配置做成可恢复的一键流程：

- 只修改 `%LOCALAPPDATA%\HT\Saved\Config\Windows\Engine.ini`。
- 不复制 DLL，不改游戏安装目录，不注入游戏进程。
- 默认写入后开启只读保护，避免游戏启动阶段重写 `Engine.ini`。
- 每次写入前创建 manifest 备份，恢复时按清单回滚。
- 提供 NVIDIA DLSS HUD 开关，用于辅助确认 `DX12` / `HDR Mode: Custom`。

## 文档导航

第一次使用建议按顺序看：

1. [快速使用](docs/01-快速使用.md)
2. [原理与测试结论](docs/02-原理与测试结论.md)
3. [备份恢复与修改范围](docs/03-备份恢复与修改范围.md)
4. [GitHub 上传指南](docs/04-GitHub上传指南.md)
5. [常见问题](docs/05-常见问题.md)
6. [发布检查清单](docs/06-发布检查清单.md)
7. [参考与致谢](docs/07-参考与致谢.md)

## 参考与致谢

相关社区工具引用和区分：

- [DLSSTweaks](https://github.com/emoose/DLSSTweaks) / [NexusMods 发布页](https://www.nexusmods.com/site/mods/550)：DLSS wrapper / tweak 工具。本项目不包含 DLSSTweaks DLL，不写 `dlsstweaks.ini`。
- [RenoDX](https://github.com/clshortfuse/renodx)：DirectX 游戏 HDR / tonemapping / shader 改造工具集。本项目不是 RenoDX add-on。
- [ReShade](https://github.com/crosire/reshade) / [官网](https://reshade.me/)：通用 post-processing injector。本项目不是 ReShade preset，不做后处理滤镜。
- [Special K](https://github.com/SpecialKO/SpecialK) / [官网](https://www.special-k.info/)：PC 游戏增强、诊断和 HDR 改造工具。本项目不使用 Special K injection。

本项目的本地 WebUI 结构、manifest 备份恢复、HUD 验证、退出后端按钮、GitHub-ready 文档组织，参考了同作者项目：

- [llg1634/nte-dlss-panel](https://github.com/llg1634/nte-dlss-panel)

两者定位不同：

- `nte-dlss-panel`：面向异环 DLSS / DLSSTweaks 低渲染比例部署。
- `nte-hdr-panel`：面向异环 UE 原生 HDR `Engine.ini` 配置。

本项目不包含 DLSSTweaks DLL，不复制 DLL，不修改游戏安装目录。

## 项目特点

- 本机 WebUI：默认只监听 `127.0.0.1:22533`。
- 零路径配置：默认定位 `%LOCALAPPDATA%\HT\Saved\Config\Windows`。
- 原生 HDR：写入 UE RendererSettings，不使用 RTX HDR / 自动 HDR 滤镜。
- 自动备份恢复：每次写入都会生成独立 manifest。
- 原版回退按钮：可一键恢复最早那份“未配置 HDR”的原始 `Engine.ini` 备份。
- 只读保护：默认阻止游戏启动阶段清理 `Engine.ini`。
- HUD 验证：可开启/关闭 NVIDIA DLSS HUD。
- 后端退出按钮：关闭网页不等于退出工具，面板提供“退出工具”按钮。

## 写入内容

默认写入：

```ini
[/Script/Engine.RendererSettings]
r.HDR.EnableHDROutput=1
r.HDR.UI.Level=1.0
r.HDR.Display.MaxLuminance=1000
r.HDR.Display.MidLuminance=18
```

参数说明：

- `r.HDR.EnableHDROutput=1`：开启 UE HDR 输出。
- `r.HDR.UI.Level=1.0`：UI 亮度倍率，建议先保持 `1.0`。
- `r.HDR.Display.MaxLuminance=1000`：显示器 HDR 峰值亮度，单位 nits。
- `r.HDR.Display.MidLuminance=18`：中间亮度参考值，画面偏暗时优先提高。

## 本机测试结论

本机测试到的稳定路径：

1. 原始 `Engine.ini` 是 200 字节的游戏生成编码内容。
2. 直接写入明文 HDR 配置后启动游戏，游戏会删除或重写该文件。
3. 写入明文 HDR 配置并设为只读后，配置能保留。
4. NVIDIA HUD 截图中可看到 `DX12` 和 `HDR Mode: Custom`。

因此工具默认勾选“写入后设为只读”。

## 使用方法

推荐下载 Release 里的打包版：

```text
NTEHDRPanel-v版本号.zip
```

解压后双击：

```text
NTEHDRPanel.exe
```

源码方式：

```text
双击 run.bat
```

如果 HUD 开关提示没有权限：

```text
双击 run_as_admin.bat
```

页面步骤：

1. 点“检测配置”。
2. 选择 HDR 参数，先用 `1000 / 18 / 1.0`。
3. 保持“写入后设为只读”勾选。
4. 点“备份并写入原生 HDR”。
5. 如需回退到原版，不要手动挑备份，直接点“恢复未配置 HDR 的原版”。
6. 启动异环。
7. 用 NVIDIA HUD 看是否显示 `DX12` / `D3D12` 和 `HDR Mode: Custom`。

## 备份位置

每次写入都会创建独立备份目录：

```text
%LOCALAPPDATA%\HT\Saved\Config\Windows\_nte_hdr_backups\<时间戳>
```

备份目录包含：

```text
manifest.json
Engine.ini
```

`manifest.json` 记录写入前文件是否存在、原文件类型、只读状态、写入参数和操作摘要。

## 恢复逻辑

恢复不是盲删文件，而是按所选备份的 `manifest.json` 执行：

如果写入前存在 `Engine.ini`，恢复时复制回原文件。  
如果写入前不存在 `Engine.ini`，恢复时删除工具创建的文件。  
如果原文件可写，恢复后保持可写。  
如果原文件只读，恢复后保持只读。

也就是说，恢复目标是“回到那次写入之前的状态”。

另外，面板会自动识别“最早一份未配置 HDR 的原版备份”，并提供单独按钮：

```text
恢复未配置 HDR 的原版
```

这个按钮不依赖下拉框选择，固定恢复到当前识别出的原版配置候选。

## NVIDIA HUD

面板读写的注册表是：

```text
HKLM\SOFTWARE\NVIDIA Corporation\Global\NGXCore\ShowDlssIndicator
```

常见值：

```text
0       关闭
1024    开启，适用于所有 DLSS DLL
```

HUD 只用于显示状态，不控制 HDR 本身。

## 反作弊误报说明

本工具不读取游戏模块，不注入游戏进程，不使用 Process Monitor。普通状态检测只读取配置文件和普通进程名。

如果游戏提示检测到“黑客工具”，优先关闭：

```text
Procmon64 / Process Monitor
Process Explorer
x64dbg / x32dbg
Cheat Engine
IDA
Frida
```

## Python

源码运行需要 Python 3。本项目没有运行时第三方 Python 依赖。

构建 exe 需要 PyInstaller：

```bat
build_exe.bat
```

输出：

```text
dist\NTEHDRPanel\NTEHDRPanel.exe
```

完整发版打包：

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build-release.ps1 -Version 0.1.3
```

会同时生成：

```text
release-artifacts\NTEHDRPanel-v0.1.3.zip
release-artifacts\NTEHDRPanel-v0.1.3.exe
```
