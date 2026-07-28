@echo off
title Compilador - Gerador de Cards PROGRAD/UFSM

echo ============================================================
echo  Build do Gerador de Cards de Formatura PROGRAD/UFSM
echo ============================================================
echo.

REM Verificando PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller nao encontrado. Instalando dependencias...
    pip install -r requirements.txt
    pip install pyinstaller
)

echo [1/2] Compilando executavel autossuficiente (.exe) em modo otimizado...
pyinstaller --noconfirm "Gerador de Cards PROGRAD.spec"

if errorlevel 1 (
    echo.
    echo [INFO] Tentando compilacao alternativa...
    pyinstaller --onefile --windowed --noupx --icon=assets\logo.ico --name="Gerador de Cards PROGRAD" --add-data "assets;assets" --exclude-module tkinter --exclude-module unittest -y main.py
)

echo.
echo ============================================================
echo [2/2] Sucesso! Executavel gerado com exito.
echo O arquivo final esta localizado em:
echo %CD%\dist\Gerador de Cards PROGRAD.exe
echo ============================================================
echo.
pause
