# One-line installer / updater for my-ai-setup.
# Run in PowerShell:
#   irm https://raw.githubusercontent.com/YOUR-GITHUB-USERNAME/my-ai-setup/main/install.ps1 | iex
# Running it again later updates everything to the latest version on GitHub.

$ErrorActionPreference = "Stop"

# >>> Change this to your GitHub username/repo after you upload it <<<
$Repo   = if ($env:AI_SETUP_REPO) { $env:AI_SETUP_REPO } else { "YOUR-GITHUB-USERNAME/my-ai-setup" }
$Branch = "main"

$dest = Join-Path $env:USERPROFILE "my-ai-setup"
$zip  = Join-Path $env:TEMP "my-ai-setup.zip"
$tmp  = Join-Path $env:TEMP "my-ai-setup-extract"

Write-Host "Downloading $Repo ($Branch) from GitHub..." -ForegroundColor Cyan
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest "https://github.com/$Repo/archive/refs/heads/$Branch.zip" -OutFile $zip -UseBasicParsing

if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
Expand-Archive $zip $tmp -Force
$src = Get-ChildItem $tmp -Directory | Select-Object -First 1

New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item (Join-Path $src.FullName "*") $dest -Recurse -Force
Remove-Item $zip, $tmp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Files saved to $dest" -ForegroundColor Green

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $dest "setup.ps1")
