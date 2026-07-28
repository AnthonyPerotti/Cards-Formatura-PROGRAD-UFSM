"""
Gerador de PDF dos Cards de Formatura PROGRAD/UFSM.
Replica fielmente o layout do main.tex (TikZ) usando ReportLab.

Layout: A4 Retrato, 2 cards por página (16cm x 10cm cada), centralizados.
Desenvolvido para PROGRAD UFSM por Anthony Perotti.
"""
import os
import sys
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.card_data import DadosCerimonia, formatar_nome_curso


def resource_path(relative: str) -> str:
    """Resolve caminho de assets — funciona tanto em dev quanto no .exe."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def registrar_fontes():
    """Registra as fontes Agrandir no ReportLab (uma vez por sessão)."""
    try:
        pdfmetrics.registerFont(
            TTFont("Agrandir-Regular", resource_path(os.path.join("assets", "Agrandir-Regular.otf")))
        )
        pdfmetrics.registerFont(
            TTFont("Agrandir-Bold", resource_path(os.path.join("assets", "Agrandir-Bold.otf")))
        )
    except Exception:
        pass  # Fallback para Helvetica


_fontes_registradas = False


def _garantir_fontes():
    global _fontes_registradas
    if not _fontes_registradas:
        registrar_fontes()
        _fontes_registradas = True


def _font_regular() -> str:
    try:
        pdfmetrics.getFont("Agrandir-Regular")
        return "Agrandir-Regular"
    except Exception:
        return "Helvetica"


def _font_bold() -> str:
    try:
        pdfmetrics.getFont("Agrandir-Bold")
        return "Agrandir-Bold"
    except Exception:
        return "Helvetica-Bold"


# ── Dimensões do card (em pontos) ─────────────────────────────────────────────
CARD_W = 16 * cm   # largura
CARD_H = 10 * cm   # altura

# A4 Retrato
PAGE_W, PAGE_H = A4  # ~595 x 842 pt

# Centralizar card horizontalmente
CARD_X = (PAGE_W - CARD_W) / 2

# 2 cards por página: espaçamento igual entre topo, meio e base
_MARGEM_V = (PAGE_H - 2 * CARD_H) / 3   # ~91pt ≈ 3.2cm de espaço em cada intervalo

# Posição inferior (cy) de cada card — ReportLab: y=0 no canto inferior esq.
CARD_CY_TOP = _MARGEM_V + CARD_H + _MARGEM_V  # card de cima
CARD_CY_BOT = _MARGEM_V                         # card de baixo


def _desenhar_card(c: rl_canvas.Canvas, card: dict, logo_path: str, logotipo_path: str, isologo_cut_path: str,
                   cx: float, cy: float):
    """
    Desenha um card na posição (cx, cy) — cy = canto inferior esquerdo do card.
    """
    # --- Marca d'água no fundo (lado esquerdo) com 10% de opacidade ---
    if os.path.exists(isologo_cut_path):
        c.saveState()
        try:
            c.setFillAlpha(0.10)
            c.setStrokeAlpha(0.10)
        except Exception:
            pass
        wm_h = CARD_H
        try:
            from PIL import Image as PILImage
            img_wm = PILImage.open(isologo_cut_path)
            wm_w = wm_h * (img_wm.width / img_wm.height)
            c.drawImage(isologo_cut_path, cx, cy, width=wm_w, height=wm_h, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
        c.restoreState()

    # --- Borda ---
    c.setLineWidth(2)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(cx, cy, CARD_W, CARD_H, stroke=1, fill=0)

    tipo = card["tipo"]
    numero_str = card["numero_str"]
    nome = card["nome"]
    subtitulo = card["subtitulo"]
    rodape = card["rodape"]

    center_x = cx + CARD_W / 2

    # --- Número ---
    c.setFillColorRGB(0, 0, 0)
    if tipo == "formando":
        c.setFont(_font_bold(), 26)
        c.drawCentredString(center_x, cy + CARD_H - 1.0 * cm, numero_str)
    else:
        tamanho = 20 if tipo == "homenageado" else 16
        c.setFont(_font_regular(), tamanho)
        c.drawRightString(cx + CARD_W - 0.5 * cm, cy + CARD_H - 0.8 * cm, numero_str)

    # --- Nome (grande, imponente e centralizado) ---
    words_nome = len(nome.split())
    if len(nome) > 28 or words_nome > 4:
        nome_font_size = 33
        nome_line_h = 33 * 1.14
    else:
        nome_font_size = 38
        nome_line_h = 38 * 1.15

    nome_y_frac = 0.60 if tipo == "formando" else 0.64
    nome_y = cy + CARD_H * nome_y_frac
    _draw_text_centered_wrapped(
        c, nome, center_x, nome_y, 15.2 * cm, nome_font_size, _font_bold(),
        line_height=nome_line_h
    )

    # --- Subtítulo (curso / cargo / título com formatação específica de cursos) ---
    subtitulo_fmt = formatar_nome_curso(subtitulo)

    sub_font_size = 24
    sub_line_h = 24 * 1.18
    sub_y = cy + CARD_H * 0.27
    _draw_text_centered_wrapped(
        c, subtitulo_fmt, center_x, sub_y, 15.8 * cm, sub_font_size, _font_regular(),
        line_height=sub_line_h
    )

    # --- Rodapé Esquerdo: Logo UFSM + Linha + LOGOTIPO ---
    logo_h = 1.25 * cm
    logo_y = cy + 0.45 * cm
    curr_x = cx + 0.45 * cm

    # 1. Logo principal UFSM PROGRAD
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            ratio = img.width / img.height
            logo_w = logo_h * ratio
            c.drawImage(logo_path, curr_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")
            curr_x += logo_w + 0.25 * cm
        except Exception:
            pass

    # 2. Linha vertical separadora (tom marrom #c48444)
    c.setLineWidth(1)
    c.setStrokeColorRGB(0.77, 0.52, 0.27)
    c.line(curr_x, logo_y, curr_x, logo_y + logo_h)
    curr_x += 0.25 * cm

    # 3. LOGOTIPO.png ao lado da linha
    if os.path.exists(logotipo_path):
        try:
            from PIL import Image as PILImage
            img_logo = PILImage.open(logotipo_path)
            logotipo_w = logo_h * (img_logo.width / img_logo.height)
            c.drawImage(logotipo_path, curr_x, logo_y, width=logotipo_w, height=logo_h, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # --- Rodapé direito ---
    c.setFillColorRGB(0, 0, 0)
    c.setFont(_font_regular(), 16)
    c.drawRightString(cx + CARD_W - 0.5 * cm, cy + 0.8 * cm, rodape)


def _draw_text_centered_wrapped(
    c: rl_canvas.Canvas,
    text: str,
    center_x: float,
    y: float,
    max_width: float,
    font_size: float,
    font_name: str,
    line_height: float,
):
    """Desenha texto centralizado com suporte a quebras manuais (\\n) e wrap automático."""
    if not text:
        return

    c.setFont(font_name, font_size)

    lines = []
    if "\n" in text:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
    else:
        words = text.split()
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if c.stringWidth(test, font_name, font_size) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

    total_h = (len(lines) - 1) * line_height
    start_y = y + total_h / 2

    for i, line in enumerate(lines):
        c.drawCentredString(center_x, start_y - i * line_height, line)


def gerar_pdf(dados: DadosCerimonia, caminho_saida: str) -> None:
    """Gera o PDF: A4 Retrato, 2 cards por página."""
    _garantir_fontes()

    logo_path = resource_path(os.path.join("assets", "logo.png"))
    logotipo_path = resource_path(os.path.join("assets", "logotipo.png"))
    isologo_cut_path = resource_path(os.path.join("assets", "isologo_cut.png"))
    if not os.path.exists(isologo_cut_path):
        isologo_cut_path = resource_path(os.path.join("assets", "isologo_black.png"))

    c = rl_canvas.Canvas(caminho_saida, pagesize=A4)
    c.setTitle(f"Cards Formatura — {dados.texto_evento}")
    c.setAuthor("Anthony Perotti")
    c.setCreator("Gerador de Cards PROGRAD/UFSM — por Anthony Perotti")
    c.setSubject("Desenvolvido para PROGRAD UFSM por Anthony Perotti")

    total = dados.total_cards()
    if total == 0:
        c.setFont(_font_regular(), 20)
        c.drawCentredString(PAGE_W / 2, PAGE_H / 2, "Nenhum participante cadastrado.")
        c.save()
        return

    # Dois cards por página: índices 0,1 → pág 1; 2,3 → pág 2; etc.
    for i in range(0, total, 2):
        # Card superior
        card1 = dados.get_card(i)
        _desenhar_card(c, card1, logo_path, logotipo_path, isologo_cut_path, CARD_X, CARD_CY_TOP)

        # Card inferior (se existir)
        if i + 1 < total:
            card2 = dados.get_card(i + 1)
            _desenhar_card(c, card2, logo_path, logotipo_path, isologo_cut_path, CARD_X, CARD_CY_BOT)

        c.showPage()

    c.save()


# Alias para compatibilidade
gerar_pdf_cards = gerar_pdf
