Set-Location $PSScriptRoot
pip install --quiet --upgrade pyinstaller
pyinstaller --onefile --name MoreAI --add-data "web;web" launcher.py
Write-Host "EXE נוצר בנתיב: dist\MoreAI.exe"
