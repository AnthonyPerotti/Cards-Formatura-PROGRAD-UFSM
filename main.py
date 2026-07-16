"""
Ponto de entrada do Gerador de Cards de Formatura PROGRAD/UFSM.
"""
import sys
import os
import subprocess

# Garante que o diretório raiz do projeto esteja no path (necessário para dev)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow, resource_path


def _auto_desbloquear():
    """
    Remove silenciosamente a marcação 'Zone.Identifier' do próprio executável.
    Isso elimina o aviso do SmartScreen a partir da SEGUNDA execução.
    Opera apenas quando rodando como .exe compilado (sys._MEIPASS existe).
    Sem janela de terminal — totalmente invisível para o usuário.
    """
    if not hasattr(sys, "_MEIPASS"):
        return  # Modo desenvolvimento — não faz nada

    try:
        exe_path = sys.executable

        # Verifica se o Zone.Identifier existe (arquivo veio de internet/rede)
        zone_path = exe_path + ":Zone.Identifier"
        try:
            with open(zone_path, "r") as _:
                pass  # Stream existe — precisa desbloquear
        except (FileNotFoundError, PermissionError, OSError):
            return  # Já desbloqueado ou sem permissão — encerra silenciosamente

        # Executa Unblock-File totalmente em segundo plano, sem janela
        subprocess.Popen(
            [
                "powershell",
                "-WindowStyle", "Hidden",
                "-NonInteractive",
                "-Command",
                f'Unblock-File -LiteralPath "{exe_path}" -ErrorAction SilentlyContinue',
            ],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except Exception:
        pass  # Qualquer falha é silenciosa — não interrompe o programa


def main():
    # Auto-desbloqueio silencioso (elimina SmartScreen da próxima execução)
    _auto_desbloquear()

    # Permite DPI alto em monitores modernos
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Gerador de Cards PROGRAD/UFSM")
    app.setOrganizationName("UFSM PROGRAD")

    # Ícone da aplicação
    ico_path = resource_path(os.path.join("assets", "logo.ico"))
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))

    # Estilo global da aplicação
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
