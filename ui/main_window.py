"""
Janela principal do Gerador de Cards de Formatura PROGRAD/UFSM.
"""
import os
import sys

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QSplitter, QFileDialog,
    QMessageBox, QProgressDialog, QApplication
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize

from core.card_data import DadosCerimonia
from core.pdf_generator import gerar_pdf
from ui.card_preview import CardPreviewWidget
from ui.data_panel import DataPanelWidget


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


class PdfThread(QThread):
    """Thread para geraÃ§Ã£o de PDF sem travar a UI."""
    concluido = pyqtSignal()
    erro = pyqtSignal(str)

    def __init__(self, dados: DadosCerimonia, caminho: str):
        super().__init__()
        self._dados = dados
        self._caminho = caminho

    def run(self):
        try:
            gerar_pdf(self._dados, self._caminho)
            self.concluido.emit()
        except Exception as e:
            self.erro.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._dados = DadosCerimonia()
        self._pdf_thread = None
        self._setup_window()
        self._setup_ui()
        # Inicializa o contador no cabeÃ§alho logo na abertura
        self._on_dados_alterados()

    def _setup_window(self):
        self.setWindowTitle("Gerador de Cards â€” ColaÃ§Ã£o de Grau PROGRAD/UFSM")
        self.setMinimumSize(1100, 650)
        self.resize(1280, 750)

        ico_path = resource_path(os.path.join("assets", "logo.ico"))
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # â”€â”€ CabeÃ§alho â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        header = self._criar_header()
        root.addWidget(header)

        # â”€â”€ Corpo (splitter) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #cccccc; }"
            "QSplitter::handle:hover { background-color: #2c5f8a; }"
        )

        # Painel esquerdo â€” dados
        self._data_panel = DataPanelWidget(self._dados)
        self._data_panel.dados_alterados.connect(self._on_dados_alterados)
        splitter.addWidget(self._data_panel)

        # Painel direito â€” preview
        self._preview = CardPreviewWidget(self._dados)
        splitter.addWidget(self._preview)

        splitter.setSizes([520, 560])
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 5)
        root.addWidget(splitter, 1)

        # â”€â”€ RodapÃ© / barra de aÃ§Ã£o â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        footer = self._criar_footer()
        root.addWidget(footer)

    def _criar_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "  stop:0 #1a3a5c, stop:1 #2c5f8a);"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # Logo pequena no header
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            lbl_logo = QLabel()
            pix = QPixmap(logo_path).scaledToHeight(44, Qt.SmoothTransformation)
            lbl_logo.setPixmap(pix)
            layout.addWidget(lbl_logo)

        lbl_title = QLabel("Gerador de Cards â€” ColaÃ§Ã£o de Grau  PROGRAD / UFSM")
        lbl_title.setStyleSheet("color: white; font-size: 17px; font-weight: bold;")
        layout.addWidget(lbl_title)

        layout.addStretch()

        self._lbl_contagem = QLabel("")
        self._lbl_contagem.setStyleSheet("color: #c8ddf0; font-size: 13px;")
        layout.addWidget(self._lbl_contagem)

        return header

    def _criar_footer(self) -> QWidget:
        footer = QWidget()
        footer.setFixedHeight(56)
        footer.setStyleSheet(
            "background-color: #f0f0f0; border-top: 1px solid #cccccc;"
        )
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self._lbl_status = QLabel("Pronto.")
        self._lbl_status.setStyleSheet("color: #555555; font-size: 12px;")
        layout.addWidget(self._lbl_status)

        layout.addStretch()

        lbl_credito = QLabel("PROGRAD UFSM â€¢ Dev: Anthony Perotti")
        lbl_credito.setStyleSheet("color: #a0a0a0; font-size: 11px; padding-right: 12px;")
        layout.addWidget(lbl_credito)

        self._btn_pdf = QPushButton("ðŸ“„   Gerar PDF")
        self._btn_pdf.setFixedHeight(38)
        self._btn_pdf.setMinimumWidth(160)
        self._btn_pdf.setStyleSheet(
            "QPushButton {"
            "  background-color: #27ae60; color: white; border: none;"
            "  border-radius: 6px; font-size: 14px; font-weight: bold; padding: 0 24px;"
            "}"
            "QPushButton:hover { background-color: #2ecc71; }"
            "QPushButton:pressed { background-color: #1e8449; }"
            "QPushButton:disabled { background-color: #95a5a6; }"
        )
        self._btn_pdf.clicked.connect(self._gerar_pdf)
        layout.addWidget(self._btn_pdf)

        return footer

    def _on_dados_alterados(self):
        """Chamado sempre que qualquer dado Ã© modificado â€” atualiza preview e contagens."""
        self._preview.refresh()
        total = self._dados.total_cards()
        nf = len(self._dados.formandos)
        nm = len(self._dados.mesa)
        nh = len(self._dados.homenageados)
        self._lbl_contagem.setText(
            f"ðŸŽ“ {nf} formandos  |  ðŸ› {nm} mesa  |  â­ {nh} homenageados  |  Total: {total} cards"
        )
        if total > 0:
            self._lbl_status.setText(f"Pronto â€” {total} cards gerados.")
        else:
            self._lbl_status.setText("Adicione participantes para comeÃ§ar.")

    def _gerar_pdf(self):
        total = self._dados.total_cards()
        if total == 0:
            QMessageBox.warning(
                self, "Sem dados",
                "Adicione pelo menos um formando, membro da mesa ou homenageado antes de gerar o PDF."
            )
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF dos Cards",
            f"Cards_{self._dados.texto_evento.replace('/', '-')}.pdf",
            "PDF (*.pdf)"
        )
        if not caminho:
            return

        self._btn_pdf.setEnabled(False)
        self._lbl_status.setText(f"Gerando PDF com {total} cardsâ€¦")

        self._pdf_thread = PdfThread(self._dados, caminho)
        self._pdf_thread.concluido.connect(lambda: self._pdf_pronto(caminho))
        self._pdf_thread.erro.connect(self._pdf_erro)
        self._pdf_thread.start()

    def _pdf_pronto(self, caminho: str):
        self._btn_pdf.setEnabled(True)
        self._lbl_status.setText(f"PDF gerado com sucesso: {os.path.basename(caminho)}")
        resp = QMessageBox.information(
            self,
            "PDF Gerado",
            f"O PDF foi salvo em:\n{caminho}\n\nDeseja abrir o arquivo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if resp == QMessageBox.Yes:
            os.startfile(caminho)

    def _pdf_erro(self, msg: str):
        self._btn_pdf.setEnabled(True)
        self._lbl_status.setText("Erro ao gerar o PDF.")
        QMessageBox.critical(self, "Erro ao gerar PDF", f"Ocorreu um erro:\n\n{msg}")
