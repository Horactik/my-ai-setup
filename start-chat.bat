@echo off
title AI Chat (Open WebUI) - close this window to stop
rem Starts Open WebUI connected to OpenRouter, then opens it in your browser.

set "DATA_DIR=%USERPROFILE%\open-webui-data"
set "OPENAI_API_BASE_URL=https://openrouter.ai/api/v1"
set "OPENAI_API_KEY=%OPENROUTER_API_KEY%"
set "ENABLE_OLLAMA_API=False"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

if "%OPENROUTER_API_KEY%"=="" (
  echo No OpenRouter key found. Run INSTALL.bat again and paste your key.
  pause
  exit /b 1
)

echo Starting... the first start can take a few minutes.
echo Your browser opens automatically as soon as the chat is ready.
echo Keep this window open while you use the chat.
start "" /min powershell -NoProfile -WindowStyle Hidden -Command "for($i=0;$i -lt 450;$i++){try{Invoke-WebRequest http://localhost:8080/health -UseBasicParsing -TimeoutSec 2 | Out-Null; Start-Process http://localhost:8080; break}catch{Start-Sleep 2}}"
open-webui serve --port 8080
pause
