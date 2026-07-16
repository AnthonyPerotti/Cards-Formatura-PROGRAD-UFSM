@echo off
chcp 65001 > nul
echo ============================================================
echo  Build do Gerador de Cards de Formatura PROGRAD/UFSM
echo ============================================================
echo.

REM Verificar se o PyInstaller está instalado
pyinstaller --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] PyInstaller não encontrado. Instalando...
    pip install pyinstaller
)

echo [1/2] Compilando o executável...
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=assets\logo.ico ^
    --name="Gerador de Cards PROGRAD" ^
    --add-data "assets;assets" ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERRO] A compilação falhou. Verifique os erros acima.
    pause
    exit /b 1
)

echo.
echo [2/2] Concluído!
echo O executável está em: dist\Gerador de Cards PROGRAD.exe
echo.
pause
