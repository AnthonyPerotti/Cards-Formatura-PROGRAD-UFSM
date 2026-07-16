"""
Widget de preview dos cards — renderiza o card visualmente usando QPainter.
Fiel ao layout do LaTeX/TikZ original.
"""
import os
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtGui import (
    QPainter, QPen, QFont, QFontDatabase, QColor, QPixmap, QFontMetrics
)
from PyQt5.QtCore import Qt, QRect, QSize

from core.card_data import DadosCerimonia


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


# IDs das fontes Agrandir carregadas no QFontDatabase
_FONT_FAMILY = "Helvetica"  # fallback
_FONTS_LOADED = False


def _carregar_fontes_qt():
    global _FONT_FAMILY, _FONTS_LOADED
    if _FONTS_LOADED:
        return
    regular = resource_path(os.path.join("assets", "Agrandir-Regular.otf"))
    bold = resource_path(os.path.join("assets", "Agrandir-Bold.otf"))
    id_r = QFontDatabase.addApplicationFont(regular)
    id_b = QFontDatabase.addApplicationFont(bold)
    families = QFontDatabase.applicationFontFamilies(id_r)
    if families:
        _FONT_FAMILY = families[0]
    _FONTS_LOADED = True


class CardRenderer(QWidget):
    """Widget que desenha um único card usando QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        _carregar_fontes_qt()
        self._card_data = None
        self._logo_pixmap = None
        self._load_logo()
        self.setMinimumSize(480, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background: #f0f0f0; border-radius: 8px;")

    def _load_logo(self):
        path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(path):
            self._logo_pixmap = QPixmap(path)

    def set_card(self, card: dict | None):
        self._card_data = card
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w = self.width()
        h = self.height()

        # Fundo cinza claro da área de preview
        painter.fillRect(0, 0, w, h, QColor("#e8e8e8"))

        if not self._card_data:
            painter.setPen(QColor("#aaaaaa"))
            f = QFont(_FONT_FAMILY, 14)
            painter.setFont(f)
            painter.drawText(QRect(0, 0, w, h), Qt.AlignCenter, "Nenhum card para exibir")
            painter.end()
            return

        # --- Calcular dimensões do card mantendo proporção 16:10 ---
        card_ratio = 16.0 / 10.0
        padding = 30
        avail_w = w - 2 * padding
        avail_h = h - 2 * padding

        if avail_w / avail_h > card_ratio:
            card_h = avail_h
            card_w = int(card_h * card_ratio)
        else:
            card_w = avail_w
            card_h = int(card_w / card_ratio)

        card_x = (w - card_w) // 2
        card_y = (h - card_h) // 2

        # --- Fundo branco do card com sombra sutil ---
        shadow_rect = QRect(card_x + 4, card_y + 4, card_w, card_h)
        painter.fillRect(shadow_rect, QColor(180, 180, 180, 120))

        painter.fillRect(card_x, card_y, card_w, card_h, QColor("white"))

        # --- Borda preta 2pt (relativa ao tamanho do card) ---
        border_pen = QPen(QColor("black"))
        border_pen.setWidth(max(2, card_w // 200))
        painter.setPen(border_pen)
        painter.drawRect(card_x, card_y, card_w, card_h)

        card = self._card_data
        tipo = card["tipo"]
        numero_str = card["numero_str"]
        nome = card["nome"] or "—"
        subtitulo = card["subtitulo"] or ""
        rodape = card["rodape"]

        center_x = card_x + card_w // 2

        # Escala de fonte: card_w como referência (LaTeX card = ~453pt → card_w pixels)
        scale = card_w / 453.0

        # --- Número ---
        num_size = max(8, int(25 * scale))
        f_num = QFont(_FONT_FAMILY, num_size)
        f_num.setBold(True)
        painter.setFont(f_num)
        painter.setPen(QColor("black"))

        if tipo == "formando":
            num_y = card_y + int(0.13 * card_h)
            painter.drawText(
                QRect(card_x, card_y + int(0.04 * card_h), card_w, int(0.18 * card_h)),
                Qt.AlignHCenter | Qt.AlignVCenter, numero_str
            )
        else:
            num_size_h = max(7, int(18 * scale))
            f_num2 = QFont(_FONT_FAMILY, num_size_h)
            painter.setFont(f_num2)
            painter.drawText(
                QRect(card_x, card_y + int(0.04 * card_h), card_w - int(0.04 * card_w), int(0.12 * card_h)),
                Qt.AlignRight | Qt.AlignVCenter, numero_str
            )

        # --- Nome (grande, centralizado, com quebra de linha) ---
        nome_size = max(10, int(38 * scale))
        f_nome = QFont(_FONT_FAMILY, nome_size)
        f_nome.setBold(True)
        painter.setFont(f_nome)
        painter.setPen(QColor("black"))

        nome_rect_w = int(0.875 * card_w)  # 14cm de 16cm = 87.5%
        nome_center_y = card_y + int(0.40 * card_h) if tipo == "formando" else card_y + int(0.35 * card_h)
        _draw_centered_wrapped_text(painter, nome, center_x, nome_center_y, nome_rect_w, f_nome)

        # --- Subtítulo ---
        sub_size = max(7, int(22 * scale))
        f_sub = QFont(_FONT_FAMILY, sub_size)
        f_sub.setBold(False)
        painter.setFont(f_sub)
        sub_center_y = card_y + int(0.70 * card_h)
        _draw_centered_wrapped_text(painter, subtitulo, center_x, sub_center_y, nome_rect_w, f_sub)

        # --- Logo (canto inferior esquerdo) ---
        if self._logo_pixmap and not self._logo_pixmap.isNull():
            logo_h = int(0.15 * card_h)
            logo_pix = self._logo_pixmap.scaledToHeight(logo_h, Qt.SmoothTransformation)
            logo_x = card_x + int(0.03 * card_w)
            logo_y = card_y + card_h - logo_h - int(0.05 * card_h)
            painter.drawPixmap(logo_x, logo_y, logo_pix)

        # --- Texto do evento (canto inferior direito) ---
        rodape_size = max(6, int(14 * scale))
        f_rodape = QFont(_FONT_FAMILY, rodape_size)
        painter.setFont(f_rodape)
        painter.setPen(QColor("black"))
        painter.drawText(
            QRect(card_x, card_y + int(0.82 * card_h), card_w - int(0.03 * card_w), int(0.12 * card_h)),
            Qt.AlignRight | Qt.AlignVCenter, rodape
        )

        painter.end()


def _draw_centered_wrapped_text(
    painter: QPainter,
    text: str,
    center_x: int,
    center_y: int,
    max_width: int,
    font: QFont,
):
    """Desenha texto centralizado com wrap automático de linha."""
    if not text:
        return

    fm = QFontMetrics(font)
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if fm.horizontalAdvance(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    line_h = fm.height()
    total_h = len(lines) * line_h
    start_y = center_y - total_h // 2 + fm.ascent()

    for i, line in enumerate(lines):
        line_w = fm.horizontalAdvance(line)
        x = center_x - line_w // 2
        painter.drawText(x, start_y + i * line_h, line)


class CardPreviewWidget(QWidget):
    """
    Painel direito: Preview completo com navegação entre cards.
    """

    def __init__(self, dados: DadosCerimonia, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._index = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Título da seção
        title = QLabel("Preview")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #333333; "
            "padding-bottom: 4px; border-bottom: 1px solid #cccccc;"
        )
        layout.addWidget(title)

        # Renderer
        self._renderer = CardRenderer(self)
        layout.addWidget(self._renderer, 1)

        # Controles de navegação
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        self._btn_prev = QPushButton("◀  Anterior")
        self._btn_prev.setFixedHeight(36)
        self._btn_prev.clicked.connect(self._prev_card)
        self._btn_prev.setStyleSheet(self._btn_style())

        self._lbl_pos = QLabel("—")
        self._lbl_pos.setAlignment(Qt.AlignCenter)
        self._lbl_pos.setMinimumWidth(120)
        self._lbl_pos.setStyleSheet("font-size: 13px; color: #444444;")

        self._btn_next = QPushButton("Próximo  ▶")
        self._btn_next.setFixedHeight(36)
        self._btn_next.clicked.connect(self._next_card)
        self._btn_next.setStyleSheet(self._btn_style())

        nav_layout.addWidget(self._btn_prev)
        nav_layout.addStretch()
        nav_layout.addWidget(self._lbl_pos)
        nav_layout.addStretch()
        nav_layout.addWidget(self._btn_next)
        layout.addLayout(nav_layout)

        self.refresh()

    def _btn_style(self):
        return (
            "QPushButton {"
            "  background-color: #2c5f8a;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 6px;"
            "  padding: 4px 16px;"
            "  font-size: 13px;"
            "}"
            "QPushButton:hover { background-color: #3a7ab8; }"
            "QPushButton:pressed { background-color: #1e4a6e; }"
            "QPushButton:disabled { background-color: #aaaaaa; }"
        )

    def set_dados(self, dados: DadosCerimonia):
        self._dados = dados
        self._index = 0
        self.refresh()

    def refresh(self):
        total = self._dados.total_cards()
        if total == 0:
            self._renderer.set_card(None)
            self._lbl_pos.setText("0 cards")
            self._btn_prev.setEnabled(False)
            self._btn_next.setEnabled(False)
            return

        # Ajusta índice se necessário
        if self._index >= total:
            self._index = total - 1
        if self._index < 0:
            self._index = 0

        card = self._dados.get_card(self._index)
        self._renderer.set_card(card)

        tipo_label = {
            "formando": "Formando",
            "mesa": "Mesa de Honra",
            "homenageado": "Homenageado",
        }.get(card["tipo"], "")

        self._lbl_pos.setText(f"Card {self._index + 1} de {total}  ({tipo_label})")
        self._btn_prev.setEnabled(self._index > 0)
        self._btn_next.setEnabled(self._index < total - 1)

    def go_to_first(self):
        self._index = 0
        self.refresh()

    def _prev_card(self):
        if self._index > 0:
            self._index -= 1
            self.refresh()

    def _next_card(self):
        total = self._dados.total_cards()
        if self._index < total - 1:
            self._index += 1
            self.refresh()
