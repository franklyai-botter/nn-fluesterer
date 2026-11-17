@echo off
echo ========================================
echo  NNFluesterer - EXE Build
echo ========================================

:: Autostart vorher entfernen falls aktiv
python autostart.py remove 2>nul

:: Alte Build-Ordner loeschen
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: EXE bauen
pyinstaller NNFluesterer.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [FEHLER] Build fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build erfolgreich!
echo  EXE: dist\NNFluesterer.exe
echo ========================================

:: Autostart mit neuer EXE einrichten
dist\NNFluesterer.exe 2>nul & python autostart.py install

echo.
echo Autostart eingerichtet.
pause
