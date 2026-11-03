# My setup rules

## Environment
- I'm on Windows. Use PowerShell commands (not bash) in the terminal.
- Python is run through `uv`. Never tell me to install Python or pip packages globally.
  - Run a script: `uv run script.py`
  - Need a library for a one-off script: `uv run --with pandas --with requests script.py`
  - Or put a `# /// script` dependencies header at the top of the script so `uv run` installs them automatically.

## Word and Excel files
A helper is installed at `$env:USERPROFILE\ai-tools\office_tools.py`. Use it instead of writing new code when it fits:
- Make a Word doc: write the content as Markdown, then
  `uv run "$env:USERPROFILE\ai-tools\office_tools.py" md2docx input.md output.docx`
- Read a Word doc: `... docx2md input.docx` (prints Markdown)
- Make a spreadsheet: write a CSV (formulas like `=B2*C2` are kept), then `... csv2xlsx input.csv output.xlsx`
- Inspect a spreadsheet: `... xlsxinfo file.xlsx`; export a sheet: `... xlsx2csv file.xlsx [out.csv] [--sheet Name]`
- For anything fancier (charts, multiple sheets, styling, editing an existing doc in place) write a small Python script using `python-docx` or `openpyxl` and run it with `uv run --with python-docx --with openpyxl`.
- Never overwrite my original document: save edits as a new file (e.g. `report_edited.docx`) unless I say otherwise.

## Modding and editing files
- Before changing game files, configs or anything not in git, copy the original to a `_backup` folder next to it first.
- Ask before deleting files or running anything that installs software or changes system settings.
- Explain in one or two lines what you changed and where.

## Keep costs down
- Only read the files you actually need; search (grep / file search) before opening big files.
- Don't re-read files you already have unless they changed.
- If a task is going in circles after ~3 failed attempts, stop and tell me, so I can switch to a stronger model.
