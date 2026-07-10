@echo off
setlocal enabledelayedexpansion
cd /d D:\TRAINPULSE\static

REM Retry moving the file
set retry=0
:retry_loop
if %retry% geq 3 goto failed
timeout /T 2 /nobreak >nul
ren style_new.css style.css 2>nul
if exist style.css (
    echo ✓ CSS file updated successfully
    goto done
)
set /a retry=%retry%+1
goto retry_loop

:failed
echo Could not update CSS - file may be locked by VS Code or browser
echo Please restart VS Code or close any editors viewing the file
goto done

:done
dir style.css
