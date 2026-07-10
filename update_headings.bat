@echo off
setlocal enabledelayedexpansion
cd /d D:\TRAINPULSE

REM Create a backup
copy static\style.css static\style.css.bak >nul 2>&1

REM Use PowerShell to read and modify the file
powershell -Command "
\$file = 'static\style.css'
\$content = Get-Content \$file -Raw
\$content = \$content -replace 'color: #ffc9c9;', 'color: #c9213a;'
\$content = \$content -replace 'color: #ffffff;', 'color: #c9213a;'
Set-Content \$file \$content -Encoding UTF8 -Force
"

echo Heading colors updated to #c9213a
