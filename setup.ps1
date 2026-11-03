# My AI Setup - Windows installer
# Installs: VS Code + Cline (coding agent), uv (runs Python tools), Git,
# Open WebUI (chat app), and the Word/Excel helper tools.
# Run by double-clicking INSTALL.bat (or: powershell -ExecutionPolicy Bypass -File setup.ps1)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

function Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                "$env:USERPROFILE\.local\bin"
}

# 1. Programs ---------------------------------------------------------------
Step "Installing VS Code, Git and uv (skips anything already installed)"
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found. Install 'App Installer' from the Microsoft Store, then run this again." -ForegroundColor Red
    Read-Host "Press Enter to exit"; exit 1
}
foreach ($id in @("Microsoft.VisualStudioCode", "Git.Git", "astral-sh.uv")) {
    Write-Host "-> $id"
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements | Out-Null
}
Refresh-Path

# 2. OpenRouter key ---------------------------------------------------------
Step "OpenRouter API key"
$existing = [Environment]::GetEnvironmentVariable("OPENROUTER_API_KEY", "User")
if ($existing) {
    Write-Host "A key is already saved. Press Enter to keep it, or paste a new one."
}
else {
    Write-Host "Create one at https://openrouter.ai/keys (set a credit limit on it!)"
}
$key = Read-Host "Paste your OpenRouter key (starts with sk-or-)"
if ($key) {
    [Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", $key.Trim(), "User")
    $env:OPENROUTER_API_KEY = $key.Trim()
    Write-Host "Saved to your Windows user environment." -ForegroundColor Green
}

# 3. Helper tools + Cline rules --------------------------------------------
Step "Copying Word/Excel tools and Cline rules"
$tools = Join-Path $env:USERPROFILE "ai-tools"
New-Item -ItemType Directory -Force -Path $tools | Out-Null
Copy-Item "$here\office_tools.py" $tools -Force
Copy-Item "$here\start-chat.bat" $tools -Force

$docs = [Environment]::GetFolderPath("MyDocuments")
$rulesDir = Join-Path $docs "Cline\Rules"
New-Item -ItemType Directory -Force -Path $rulesDir | Out-Null
Copy-Item "$here\cline-rules.md" (Join-Path $rulesDir "my-setup.md") -Force
Write-Host "Tools: $tools"
Write-Host "Cline global rules: $rulesDir\my-setup.md"

# Pre-download the Python libraries the tools use (so the first real run is fast)
uv run "$tools\office_tools.py" --help | Out-Null

# 4. Cline extension --------------------------------------------------------
Step "Installing the Cline extension in VS Code"
$code = Get-Command code -ErrorAction SilentlyContinue
if (-not $code) { $code = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd" }
& $code --install-extension saoudrizwan.claude-dev --force

# 5. Open WebUI -------------------------------------------------------------
Step "Installing Open WebUI (chat app) - this download is big, give it a few minutes"
uv tool install --python 3.11 --upgrade open-webui

# Desktop shortcut
$desktop = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $desktop "AI Chat.lnk"))
$lnk.TargetPath = "$tools\start-chat.bat"
$lnk.WorkingDirectory = $tools
$lnk.Save()

Step "Done!"
Write-Host @"
Next:
 1. Double-click 'AI Chat' on your desktop -> browser opens at http://localhost:8080
    (first start takes a minute; create your local admin account).
 2. Open VS Code -> click the Cline icon in the left bar -> 'Use your own API key'
    -> API Provider: OpenRouter -> paste your key -> pick a model.
See README.md for model picks and tips.
"@ -ForegroundColor Green
Read-Host "Press Enter to close"
