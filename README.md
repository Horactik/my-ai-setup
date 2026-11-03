# My AI Setup (Windows)

Your own pay-as-you-go AI kit:
- **Coding agent**: VS Code + Cline. It edits files, does mods and code, and runs commands.
- **Chat app**: Open WebUI, a ChatGPT-style chat in your browser that can use any OpenRouter model.
- **Docs and sheets**: `office_tools.py`, which makes and reads real `.docx` and `.xlsx` files. Cline already knows how to use it.

Everything uses one OpenRouter key, and you pay only for what you use.

---

## 1. Get an OpenRouter key (5 min)
1. Sign up at https://openrouter.ai and add credit. $5–10 is plenty to start.
2. Go to **Keys → Create key** and **set a credit limit** on the key (e.g. $10). This is your safety net.
3. Copy the key (it starts with `sk-or-`).

## 2. Run the installer
**From GitHub (any Windows PC, one line):** open PowerShell and run

```powershell
irm https://raw.githubusercontent.com/Horactik/my-ai-setup/main/install.ps1 | iex
```

Run the same line again any time to **update** to the latest version in this repo. Your key, chats and settings are kept.

**Or offline:** download the repo as a ZIP (**Code → Download ZIP**), extract it, and double-click **INSTALL.bat**. If SmartScreen warns you, choose *More info → Run anyway*.

Paste your OpenRouter key when it asks. The key is stored only in your Windows user settings, never in this repo.

It installs VS Code, Git, uv, the Cline extension and Open WebUI. It also puts an **AI Chat** shortcut on your desktop. The whole thing takes about 5–10 minutes.

## 3. Set up Cline (coding agent)
1. Open VS Code and click the **Cline** icon in the left sidebar.
2. Choose **Use your own API key**, set **API Provider: OpenRouter**, and paste your key.
3. Pick a model (see the list below). Then open your project or mod folder (**File → Open Folder**) and tell Cline what you want.

Tips:
- Use **Plan** mode to discuss the approach and **Act** mode to let it make the changes.
- Cline asks before each file edit or command. Approve each step until you trust it.
- Your rules (Windows commands, backups before modding, the Word/Excel tools, cost-saving habits) are in `Documents\Cline\Rules\my-setup.md`. Edit that file to change them.

## 4. Use the chat app
- Double-click **AI Chat** on your desktop and keep the black window open. Your browser opens `http://localhost:8080`.
- The first time, create an account. It's stored only on your PC.
- Pick a model from the dropdown at the top. All OpenRouter models are listed there.
- Your chats are saved in `%USERPROFILE%\open-webui-data`.
- The key is read only on the first start. To change it later, go to **Admin Panel → Settings → Connections**.

## 5. Docs and sheets
The easiest way is to ask Cline, for example "make a Word report from these notes" or "turn this data into an Excel sheet with totals". You can also run the tools yourself in a terminal:

```powershell
$t = "$env:USERPROFILE\ai-tools\office_tools.py"
uv run $t md2docx notes.md report.docx      # Markdown -> Word
uv run $t docx2md report.docx               # Word -> text
uv run $t csv2xlsx data.csv data.xlsx       # CSV -> Excel (formulas like =B2*C2 kept)
uv run $t xlsxinfo data.xlsx                # peek inside a spreadsheet
uv run $t xlsx2csv data.xlsx out.csv        # Excel -> CSV
```
A handy workflow: ask the chat app to write your doc in Markdown, save it as a `.md` file, and convert it with `md2docx`.

---

## Which model to pick (as of Nov 2026, so check OpenRouter for newer ones)

| Use | Model (search the name in the dropdown) | Cost |
|---|---|---|
| Everyday coding, modding, file edits | DeepSeek V4.1 Flash, GLM 5.3 Flash | very cheap |
| Front-end and UI, harder coding | Kimi K3, DeepSeek V4 Pro | cheap |
| Stuck on a hard bug or big refactor | Claude Sonnet 5.5, then Claude Opus 5.5 | pricey |
| Questions and quick chat | Gemini 3.8 Flash, DeepSeek V4.1 Flash | cheap |
| Long docs and writing | Claude Sonnet 5.5, Kimi K3 | mid |

Habit that saves money: start cheap, and switch up only when the cheap model gets stuck.

## Optional: offline model on your GPU (8–16 GB)
Install Ollama from https://ollama.com and run `ollama pull qwen3:14b` (or a smaller version if it's slow). To use it in Cline, set **API Provider: Ollama**. To use it in the chat app, edit `start-chat.bat` and change `ENABLE_OLLAMA_API=False` to `True`. Local models are free and private, but much weaker than the cloud models above.

## Troubleshooting
- **"winget not found"**: install *App Installer* from the Microsoft Store.
- **The chat window closes immediately**: run INSTALL.bat again. The Open WebUI download may have failed.
- **Cline says the key is invalid**: check the key at openrouter.ai/keys and make sure it still has credit.
- **Something says "not recognized"**: restart your PC once after installing so Windows picks up the new programs.

---

## Putting this on GitHub (first time)
1. Create a **public** repo named `my-ai-setup` at https://github.com/new. It must be public for the one-line installer to download it.
2. Upload every file in this folder, including the hidden `.github` folder and `.gitattributes`. On the empty repo page, click **uploading an existing file** and drag everything in. Or use GitHub Desktop.
3. (Already done: the installer points at `Horactik/my-ai-setup`.)
4. The **Actions** tab automatically runs a test on Windows every time you change something.

Never commit your OpenRouter key. `.gitignore` already blocks the usual key files.
