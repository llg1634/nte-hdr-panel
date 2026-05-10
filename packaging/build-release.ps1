param(
  [string]$Version = "0.1.3"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release-artifacts"
$ZipName = "NTEHDRPanel-v$Version.zip"
$ZipPath = Join-Path $ReleaseDir $ZipName
$OneFileName = "NTEHDRPanel-v$Version.exe"
$OneFilePath = Join-Path $ReleaseDir $OneFileName

Set-Location $Root
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

python -m py_compile app.py
python -m pip show pyinstaller *> $null
if ($LASTEXITCODE -ne 0) {
  python -m pip install pyinstaller
}

pyinstaller --noconfirm --name NTEHDRPanel --noconsole --add-data "web;web" app.py
pyinstaller --noconfirm --onefile --noconsole --name "NTEHDRPanel-v$Version" --add-data "web;web" app.py

$PackageRoot = Join-Path $ReleaseDir "NTEHDRPanel-v$Version"
if (Test-Path $PackageRoot) {
  Remove-Item -LiteralPath $PackageRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $PackageRoot | Out-Null

Copy-Item -LiteralPath (Join-Path $Root "dist\NTEHDRPanel") -Destination $PackageRoot -Recurse
Copy-Item -LiteralPath (Join-Path $Root "README.md") -Destination $PackageRoot
Copy-Item -LiteralPath (Join-Path $Root "README.en.md") -Destination $PackageRoot
Copy-Item -LiteralPath (Join-Path $Root "CHANGELOG.md") -Destination $PackageRoot
Copy-Item -LiteralPath (Join-Path $Root "LICENSE") -Destination $PackageRoot
Copy-Item -LiteralPath (Join-Path $Root "NOTICE.md") -Destination $PackageRoot
Copy-Item -LiteralPath (Join-Path $Root "ACKNOWLEDGEMENTS.md") -Destination $PackageRoot

$AdminBat = @"
@echo off
setlocal
cd /d "%~dp0\NTEHDRPanel"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '.\NTEHDRPanel.exe' -Verb RunAs"
"@
Set-Content -LiteralPath (Join-Path $PackageRoot "run_exe_as_admin.bat") -Value $AdminBat -Encoding ASCII

if (Test-Path $ZipPath) {
  Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -Path (Join-Path $PackageRoot "*") -DestinationPath $ZipPath

Copy-Item -LiteralPath (Join-Path $Root "dist\$OneFileName") -Destination $OneFilePath -Force

Write-Host "Release package created: $ZipPath"
Write-Host "One-file exe created: $OneFilePath"
