import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow, resource_path


def _auto_desbloquear():
    if not hasattr(sys, "_MEIPASS"):
        return

    try:
        exe_path = sys.executable
        zone_path = exe_path + ":Zone.Identifier"
        try:
            with open(zone_path, "r"):
                pass
        except (FileNotFoundError, PermissionError, OSError):
            return

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
        pass


def main():
    _auto_desbloquear()

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Gerador de Cards PROGRAD/UFSM")
    app.setOrganizationName("UFSM PROGRAD")

    ico_path = resource_path(os.path.join("assets", "logo.ico"))
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))

    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
