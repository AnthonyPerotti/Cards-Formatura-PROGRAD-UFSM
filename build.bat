@echo off
chcp 65001 > nul
echo ============================================================
echo  Build do Gerador de Cards de Formatura PROGRAD/UFSM
echo ============================================================
echo.

REM Verificar se o PyInstaller estÃ¡ instalado
pyinstaller --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] PyInstaller nÃ£o encontrado. Instalando...
    pip install pyinstaller
)

echo [1/2] Compilando o executÃ¡vel...
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=assets\logo.ico ^
    --name="Gerador de Cards PROGRAD" ^
    --add-data "assets;assets" ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERRO] A compilaÃ§Ã£o falhou. Verifique os erros acima.
    pause
    exit /b 1
)

echo.
echo [2/2] ConcluÃ­do!
echo O executÃ¡vel estÃ¡ em: dist\Gerador de Cards PROGRAD.exe
echo.
pause
