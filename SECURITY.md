# Security Policy

## Scope

This project is a local-only tool. It listens on `127.0.0.1` by default and should not be exposed to a public network.

## What The Tool Does

- Reads and writes `%LOCALAPPDATA%\HT\Saved\Config\Windows\Engine.ini`.
- Creates backups under `_nte_hdr_backups`.
- Optionally writes NVIDIA HUD registry value `ShowDlssIndicator`.

## What The Tool Does Not Do

- It does not inject into the game process.
- It does not scan loaded game modules.
- It does not modify the game installation directory.
- It does not require Process Monitor or debugging tools.

## Reporting

Please open a GitHub issue with reproduction steps, Windows version, tool version, and relevant logs. Do not include personal paths if you do not want them public.
