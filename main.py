"""
Ponto de entrada do Gerador de Cards de Formatura PROGRAD/UFSM.
"""
import sys
import os
import subprocess

# Garante que o diretÃ³rio raiz do projeto esteja no path (necessÃ¡rio para dev)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow, resource_path


def _auto_desbloquear():
    """
    Remove silenciosamente a marcaÃ§Ã£o 'Zone.Identifier' do prÃ³prio executÃ¡vel.
    Isso elimina o aviso do SmartScreen a partir da SEGUNDA execuÃ§Ã£o.
    Opera apenas quando rodando como .exe compilado (sys._MEIPASS existe).
    Sem janela de terminal â€” totalmente invisÃ­vel para o usuÃ¡rio.
    """
    if not hasattr(sys, "_MEIPASS"):
        return  # Modo desenvolvimento â€” nÃ£o faz nada

    try:
        exe_path = sys.executable

        # Verifica se o Zone.Identifier existe (arquivo veio de internet/rede)
        zone_path = exe_path + ":Zone.Identifier"
        try:
            with open(zone_path, "r") as _:
                pass  # Stream existe â€” precisa desbloquear
        except (FileNotFoundError, PermissionError, OSError):
            return  # JÃ¡ desbloqueado ou sem permissÃ£o â€” encerra silenciosamente

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
        pass  # Qualquer falha Ã© silenciosa â€” nÃ£o interrompe o programa


def main():
    # Auto-desbloqueio silencioso (elimina SmartScreen da prÃ³xima execuÃ§Ã£o)
    _auto_desbloquear()

    # Permite DPI alto em monitores modernos
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Gerador de Cards PROGRAD/UFSM")
    app.setOrganizationName("UFSM PROGRAD")

    # Ãcone da aplicaÃ§Ã£o
    ico_path = resource_path(os.path.join("assets", "logo.ico"))
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))

    # Estilo global da aplicaÃ§Ã£o
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
