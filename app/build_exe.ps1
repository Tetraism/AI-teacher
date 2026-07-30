Set-Location $PSScriptRoot
pip install --quiet --upgrade pyinstaller

# Stage 1: the app itself - opened from the Start Menu, installs Ollama on first run
pyinstaller --onefile --windowed --uac-admin --name MoreAI --add-data "web;web" launcher.py

# Stage 2: the installer - copies MoreAI.exe into place and creates Start Menu/Desktop shortcuts
pyinstaller --onefile --windowed --name MoreAI-Setup --add-data "dist/MoreAI.exe;." installer.py

Write-Host "התקנה מוכנה: dist\MoreAI-Setup.exe (זה הקובץ להפצה - הוא מטמיע את MoreAI.exe בתוכו)"
