"""
Janela principal do aplicativo Gerador de Cards PROGRAD.
"""
import os
import sys

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from core.card_data import DadosCerimonia
from core.pdf_generator import gerar_pdf_cards
from ui.data_panel import DataPanelWidget
from ui.card_preview import CardPreviewWidget, resource_path


class PdfThread(QThread):
    concluido = pyqtSignal()
    erro = pyqtSignal(str)

    def __init__(self, dados: DadosCerimonia, caminho: str):
        super().__init__()
        self.dados = dados
        self.caminho = caminho

    def run(self):
        try:
            gerar_pdf_cards(self.dados, self.caminho)
            self.concluido.emit()
        except Exception as e:
            self.erro.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._dados = DadosCerimonia()
        self._setup_ui()
        self._on_dados_alterados()

    def _setup_ui(self):
        self.setWindowTitle("Gerador de Cards — PROGRAD / UFSM")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        # Ícone da janela (ISOLOGO)
        ico_path = resource_path(os.path.join("assets", "logo.ico"))
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Cabeçalho ──────────────────────────────────────────────────────────
        header = self._criar_header()
        root.addWidget(header)

        # ── Corpo (splitter) ───────────────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #cccccc; }"
            "QSplitter::handle:hover { background-color: #1b365d; }"
        )

        # Painel esquerdo — dados
        self._data_panel = DataPanelWidget(self._dados)
        self._data_panel.dados_alterados.connect(self._on_dados_alterados)
        splitter.addWidget(self._data_panel)

        # Painel direito — preview
        self._preview = CardPreviewWidget(self._dados)
        splitter.addWidget(self._preview)

        splitter.setSizes([520, 560])
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 5)
        root.addWidget(splitter, 1)

        # ── Rodapé / barra de ação ─────────────────────────────────────────────
        footer = self._criar_footer()
        root.addWidget(footer)

    def _criar_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(
            "background-color: #1b365d; border-bottom: 3px solid #c48444;"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignVCenter)

        # Logotipo na página principal (header)
        logo_path = resource_path(os.path.join("assets", "logotipo.png"))
        if not os.path.exists(logo_path):
            logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            lbl_logo = QLabel()
            pix = QPixmap(logo_path).scaledToHeight(42, Qt.SmoothTransformation)
            lbl_logo.setPixmap(pix)
            layout.addWidget(lbl_logo)

        lbl_title = QLabel("Gerador de Cards — Colação de Grau  PROGRAD / UFSM")
        lbl_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_title)

        layout.addStretch()

        # Badge de contagem elegante e uniforme
        self._lbl_contagem = QLabel("")
        self._lbl_contagem.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.12); "
            "border: 1px solid rgba(255, 255, 255, 0.2); "
            "border-radius: 6px; padding: 5px 14px; "
            "color: #ffffff; font-size: 13px; font-weight: 500;"
        )
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

        lbl_credito = QLabel("PROGRAD UFSM • Dev: Anthony Perotti")
        lbl_credito.setStyleSheet("color: #a0a0a0; font-size: 11px; padding-right: 12px;")
        layout.addWidget(lbl_credito)

        self._btn_pdf = QPushButton("📄   Gerar PDF")
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
        """Chamado sempre que qualquer dado é modificado — atualiza preview e contagens."""
        self._preview.refresh()
        total = self._dados.total_cards()
        nf = len(self._dados.formandos)
        nm = len(self._dados.mesa)
        nh = len(self._dados.homenageados)
        self._lbl_contagem.setText(
            f"🎓 {nf} formandos  |  🏛 {nm} mesa  |  ⭐ {nh} homenageados  |  Total: {total} cards"
        )
        if total > 0:
            self._lbl_status.setText(f"Pronto — {total} cards gerados.")
        else:
            self._lbl_status.setText("Adicione participantes para começar.")

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
        self._lbl_status.setText(f"Gerando PDF com {total} cards…")

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
