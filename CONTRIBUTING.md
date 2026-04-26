# Contributing

欢迎提交 issue 或 pull request。这个项目聚焦异环原生 HDR 配置，不计划扩展成通用游戏修改器。

## 开发流程

1. 修改前先确认问题能在本地复现。
2. 保持工具只修改 `Engine.ini` 和 NVIDIA HUD 注册表。
3. 不加入注入、Hook、进程模块扫描或 Process Monitor 依赖。
4. 修改 UI 后同时检查浅色和深色主题。
5. 修改恢复逻辑后必须测试写入和恢复闭环。

## 测试命令

```bat
py -3 -m py_compile app.py
run.bat
build_exe.bat
```
