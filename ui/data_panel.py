"""
Painel de entrada de dados — 3 abas com tabelas editáveis e importação CSV.
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QFileDialog, QAbstractItemView,
    QHeaderView, QMessageBox, QSizePolicy, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from core.card_data import (
    DadosCerimonia, Formando, MembroMesa, Homenageado,
    parse_arquivo_formandos, parse_arquivo_mesa, parse_arquivo_homenageados,
    parse_csv_formandos, parse_csv_mesa, parse_csv_homenageados,
    export_csv_formandos, export_csv_mesa, export_csv_homenageados,
)


class NoElideDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.textElideMode = Qt.ElideNone

        painter.save()
        widget = opt.widget
        style = widget.style() if widget else QApplication.style()

        # Desenha fundo e selecao
        style.drawPrimitive(QStyle.PE_PanelItemViewRow, opt, painter, widget)
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, widget)

        # Desenha texto completo sem insolar reticencias
        text = index.data(Qt.DisplayRole)
        if text:
            rect = opt.rect.adjusted(6, 0, -6, 0)
            if opt.state & QStyle.State_Selected:
                color = opt.palette.highlightedText().color()
            else:
                color = opt.palette.text().color()
            painter.setPen(color)
            painter.setFont(opt.font)
            painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter | Qt.TextSingleLine, str(text))

        painter.restore()


_STYLE_BTN_ACTION = (
    "QPushButton {"
    "  background-color: #1b365d; color: white; border: none;"
    "  border-radius: 5px; padding: 5px 10px; font-size: 12px;"
    "}"
    "QPushButton:hover { background-color: #2b4c7e; }"
    "QPushButton:pressed { background-color: #122540; }"
)

_STYLE_BTN_DANGER = (
    "QPushButton {"
    "  background-color: #c0392b; color: white; border: none;"
    "  border-radius: 5px; padding: 5px 10px; font-size: 12px;"
    "}"
    "QPushButton:hover { background-color: #e74c3c; }"
    "QPushButton:pressed { background-color: #96281b; }"
)

_STYLE_BTN_SECONDARY = (
    "QPushButton {"
    "  background-color: #5d6d7e; color: white; border: none;"
    "  border-radius: 5px; padding: 5px 10px; font-size: 12px;"
    "}"
    "QPushButton:hover { background-color: #717d8c; }"
)


def _make_table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setTextElideMode(Qt.ElideNone)
    t.setItemDelegate(NoElideDelegate(t))
    for i in range(len(headers)):
        t.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
    t.horizontalHeader().setStretchLastSection(True)
    t.verticalHeader().setVisible(True)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setAlternatingRowColors(True)
    t.setStyleSheet(
        "QTableWidget { border: 1px solid #cccccc; gridline-color: #e0e0e0; font-size: 13px; }"
        "QHeaderView::section { background-color: #1b365d; color: white; padding: 6px; font-size: 13px; font-weight: bold; }"
        "QTableWidget::item:selected { background-color: #d0e8f8; color: black; }"
    )
    t.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
    return t


class AbaFormandos(QWidget):
    dados_alterados = pyqtSignal()

    def __init__(self, dados: DadosCerimonia, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._bloqueado = False
        self._setup_ui()
        self._carregar_dados()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        desc = QLabel("Cada linha = um formando. <b>Nome</b> e <b>Curso</b> aparecerão no card.")
        desc.setStyleSheet("font-size: 12px; color: #555555; padding: 4px 0;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._table = _make_table(["Nome", "Curso"])
        self._table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._table, 1)

        btns = QHBoxLayout()
        btns.setSpacing(6)

        b_add = QPushButton("➕  Adicionar")
        b_add.setToolTip("Adicionar novo formando")
        b_add.setStyleSheet(_STYLE_BTN_ACTION)
        b_add.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        b_add.clicked.connect(self._adicionar_linha)
        btns.addWidget(b_add)

        b_del = QPushButton("🗑  Remover")
        b_del.setToolTip("Remover formando selecionado")
        b_del.setStyleSheet(_STYLE_BTN_DANGER)
        b_del.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        b_del.clicked.connect(self._remover_linha)
        btns.addWidget(b_del)

        btns.addStretch()

        b_imp = QPushButton("📂  Importar Planilha")
        b_imp.setToolTip("Importar lista de formandos via Excel (.xlsx) ou CSV")
        b_imp.setStyleSheet(_STYLE_BTN_SECONDARY)
        b_imp.clicked.connect(self._importar_csv)
        btns.addWidget(b_imp)

        b_exp = QPushButton("💾  Exportar Tabela")
        b_exp.setToolTip("Exportar lista de formandos para arquivo CSV")
        b_exp.setStyleSheet(_STYLE_BTN_SECONDARY)
        b_exp.clicked.connect(self._exportar_csv)
        btns.addWidget(b_exp)

        layout.addLayout(btns)

    def _carregar_dados(self):
        self._bloqueado = True
        self._table.setRowCount(0)
        for f in self._dados.formandos:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(f.nome))
            self._table.setItem(row, 1, QTableWidgetItem(f.curso))
        self._bloqueado = False

    def _adicionar_linha(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(""))
        self._table.setItem(row, 1, QTableWidgetItem(""))
        self._table.scrollToBottom()
        self._table.setCurrentCell(row, 0)
        self._table.editItem(self._table.item(row, 0))
        self._sincronizar()

    def _remover_linha(self):
        rows = sorted(set(i.row() for i in self._table.selectedItems()), reverse=True)
        for r in rows:
            self._table.removeRow(r)
        self._sincronizar()

    def _on_item_changed(self, _):
        if not self._bloqueado:
            self._sincronizar()

    def _sincronizar(self):
        result = []
        for row in range(self._table.rowCount()):
            nome = (self._table.item(row, 0) or QTableWidgetItem()).text().strip()
            curso = (self._table.item(row, 1) or QTableWidgetItem()).text().strip()
            result.append(Formando(nome=nome, curso=curso))
        self._dados.formandos = result
        self.dados_alterados.emit()

    def _importar_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar Planilha de Formandos", "", "Planilhas Excel e CSV (*.xlsx *.xls *.csv);;Todos os arquivos (*)"
        )
        if not path:
            return
        try:
            self._dados.formandos = parse_arquivo_formandos(path)
            self._carregar_dados()
            self.dados_alterados.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao importar", str(e))

    def _exportar_csv(self):
        self._sincronizar()
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV de Formandos", "formandos.csv", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(export_csv_formandos(self._dados.formandos))
        except Exception as e:
            QMessageBox.critical(self, "Erro ao exportar", str(e))

    def atualizar_dados(self):
        self._carregar_dados()


class AbaMesa(QWidget):
    dados_alterados = pyqtSignal()

    def __init__(self, dados: DadosCerimonia, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._bloqueado = False
        self._setup_ui()
        self._carregar_dados()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        desc = QLabel("Membros da <b>Mesa de Honra</b>. <b>Nome</b> e <b>Cargo</b> aparecerão no card (ex: Reitor, Pró-Reitor).")
        desc.setStyleSheet("font-size: 12px; color: #555555; padding: 4px 0;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._table = _make_table(["Nome", "Cargo"])
        self._table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._table, 1)

        btns = QHBoxLayout()
        btns.setSpacing(6)

        b_add = QPushButton("➕  Adicionar")
        b_add.setToolTip("Adicionar novo membro da mesa")
        b_add.setStyleSheet(_STYLE_BTN_ACTION)
        b_add.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        b_add.clicked.connect(self._adicionar_linha)
        btns.addWidget(b_add)

        b_del = QPushButton("🗑  Remover")
        b_del.setToolTip("Remover membro selecionado")
        b_del.setStyleSheet(_STYLE_BTN_DANGER)
        b_del.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        b_del.clicked.connect(self._remover_linha)
        btns.addWidget(b_del)

        btns.addStretch()

        b_imp = QPushButton("📂  Importar Planilha")
        b_imp.setToolTip("Importar membros da mesa via Excel (.xlsx) ou CSV")
        b_imp.setStyleSheet(_STYLE_BTN_SECONDARY)
        b_imp.clicked.connect(self._importar_csv)
        btns.addWidget(b_imp)

        b_exp = QPushButton("💾  Exportar Tabela")
        b_exp.setToolTip("Exportar lista da mesa para arquivo CSV")
        b_exp.setStyleSheet(_STYLE_BTN_SECONDARY)
        b_exp.clicked.connect(self._exportar_csv)
        btns.addWidget(b_exp)

        layout.addLayout(btns)

    def _carregar_dados(self):
        self._bloqueado = True
        self._table.setRowCount(0)
        for m in self._dados.mesa:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(m.nome))
            self._table.setItem(row, 1, QTableWidgetItem(m.cargo))
        self._bloqueado = False

    def _adicionar_linha(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(""))
        self._table.setItem(row, 1, QTableWidgetItem(""))
        self._table.scrollToBottom()
        self._table.setCurrentCell(row, 0)
        self._table.editItem(self._table.item(row, 0))
        self._sincronizar()

    def _remover_linha(self):
        rows = sorted(set(i.row() for i in self._table.selectedItems()), reverse=True)
        for r in rows:
            self._table.removeRow(r)
        self._sincronizar()

    def _on_item_changed(self, _):
        if not self._bloqueado:
            self._sincronizar()

    def _sincronizar(self):
        result = []
        for row in range(self._table.rowCount()):
            nome = (self._table.item(row, 0) or QTableWidgetItem()).text().strip()
            cargo = (self._table.item(row, 1) or QTableWidgetItem()).text().strip()
            result.append(MembroMesa(nome=nome, cargo=cargo))
        self._dados.mesa = result
        self.dados_alterados.emit()

    def _importar_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar Planilha da Mesa", "", "Planilhas Excel e CSV (*.xlsx *.xls *.csv);;Todos os arquivos (*)"
        )
        if not path:
            return
        try:
            self._dados.mesa = parse_arquivo_mesa(path)
            self._carregar_dados()
            self.dados_alterados.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao importar", str(e))

    def _exportar_csv(self):
        self._sincronizar()
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV da Mesa", "mesa.csv", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(export_csv_mesa(self._dados.mesa))
        except Exception as e:
            QMessageBox.critical(self, "Erro ao exportar", str(e))

    def atualizar_dados(self):
        self._carregar_dados()


class AbaHomenageados(QWidget):
    dados_alterados = pyqtSignal()

    def __init__(self, dados: DadosCerimonia, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._bloqueado = False
        self._setup_ui()
        self._carregar_dados()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        desc = QLabel("<b>Homenageados</b> da cerimônia. <b>Nome</b> e <b>Título</b> aparecerão no card (ex: Homenageada da Turma de Medicina, Patrono).")
        desc.setStyleSheet("font-size: 12px; color: #555555; padding: 4px 0;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._table = _make_table(["Nome", "Título"])
        self._table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._table, 1)

        btns = QHBoxLayout()
        btns.setSpacing(6)

        b_add = QPushButton("➕  Adicionar")
        b_add.setToolTip("Adicionar novo homenageado")
        b_add.setStyleSheet(_STYLE_BTN_ACTION)
        b_add.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        b_add.clicked.connect(self._adicionar_linha)
        btns.addWidget(b_add)

        b_del = QPushButton("🗑  Remover")
        b_del.setToolTip("Remover homenageado selecionado")
        b_del.setStyleSheet(_STYLE_BTN_DANGER)
        b_del.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        b_del.clicked.connect(self._remover_linha)
        btns.addWidget(b_del)

        btns.addStretch()

        b_imp = QPushButton("📂  Importar Planilha")
        b_imp.setToolTip("Importar homenageados via Excel (.xlsx) ou CSV")
        b_imp.setStyleSheet(_STYLE_BTN_SECONDARY)
        b_imp.clicked.connect(self._importar_csv)
        btns.addWidget(b_imp)

        b_exp = QPushButton("💾  Exportar Tabela")
        b_exp.setToolTip("Exportar lista de homenageados para arquivo CSV")
        b_exp.setStyleSheet(_STYLE_BTN_SECONDARY)
        b_exp.clicked.connect(self._exportar_csv)
        btns.addWidget(b_exp)

        layout.addLayout(btns)

    def _carregar_dados(self):
        self._bloqueado = True
        self._table.setRowCount(0)
        for h in self._dados.homenageados:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(h.nome))
            self._table.setItem(row, 1, QTableWidgetItem(h.titulo))
        self._bloqueado = False

    def _adicionar_linha(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(""))
        self._table.setItem(row, 1, QTableWidgetItem(""))
        self._table.scrollToBottom()
        self._table.setCurrentCell(row, 0)
        self._table.editItem(self._table.item(row, 0))
        self._sincronizar()

    def _remover_linha(self):
        rows = sorted(set(i.row() for i in self._table.selectedItems()), reverse=True)
        for r in rows:
            self._table.removeRow(r)
        self._sincronizar()

    def _on_item_changed(self, _):
        if not self._bloqueado:
            self._sincronizar()

    def _sincronizar(self):
        result = []
        for row in range(self._table.rowCount()):
            nome = (self._table.item(row, 0) or QTableWidgetItem()).text().strip()
            titulo = (self._table.item(row, 1) or QTableWidgetItem()).text().strip()
            result.append(Homenageado(nome=nome, titulo=titulo))
        self._dados.homenageados = result
        self.dados_alterados.emit()

    def _importar_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar Planilha de Homenageados", "", "Planilhas Excel e CSV (*.xlsx *.xls *.csv);;Todos os arquivos (*)"
        )
        if not path:
            return
        try:
            self._dados.homenageados = parse_arquivo_homenageados(path)
            self._carregar_dados()
            self.dados_alterados.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao importar", str(e))

    def _exportar_csv(self):
        self._sincronizar()
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV de Homenageados", "homenageados.csv", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(export_csv_homenageados(self._dados.homenageados))
        except Exception as e:
            QMessageBox.critical(self, "Erro ao exportar", str(e))

    def atualizar_dados(self):
        self._carregar_dados()


class DataPanelWidget(QWidget):
    """Painel esquerdo: campo de evento + 3 abas de dados."""
    dados_alterados = pyqtSignal()

    def __init__(self, dados: DadosCerimonia, parent=None):
        super().__init__(parent)
        self._dados = dados
        self._setup_ui()

    def _setup_ui(self):
        from PyQt5.QtWidgets import QGroupBox, QLineEdit, QComboBox, QFormLayout
        from PyQt5.QtGui import QIntValidator

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Grupo: Informações do Evento ---
        grupo_evento = QGroupBox("📋  Informações do Evento")
        grupo_evento.setStyleSheet(
            "QGroupBox { font-size: 13px; font-weight: bold; color: #1b365d; "
            "border: 1px solid #b0c8e0; border-radius: 6px; margin-top: 8px; padding-top: 6px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }"
        )
        form = QFormLayout(grupo_evento)
        form.setSpacing(8)
        form.setContentsMargins(10, 12, 10, 10)

        # Campo: texto fixo (não editável pelo usuário)
        lbl_fixo = QLabel("Colações de Grau UFSM")
        lbl_fixo.setStyleSheet("font-size: 13px; color: #333333;")
        form.addRow("Texto base:", lbl_fixo)

        # Campos: Ano e Semestre
        h_ano_sem = QHBoxLayout()
        h_ano_sem.setSpacing(8)

        self._edit_ano = QLineEdit(self._dados.ano)
        self._edit_ano.setPlaceholderText("Ex: 2025")
        self._edit_ano.setMaximumWidth(80)
        self._edit_ano.setMaxLength(4)
        self._edit_ano.setValidator(QIntValidator(0, 9999))
        self._edit_ano.setStyleSheet(self._input_style())
        self._edit_ano.textChanged.connect(self._on_evento_changed)
        h_ano_sem.addWidget(self._edit_ano)

        h_ano_sem.addWidget(QLabel("/"))

        self._combo_sem = QComboBox()
        self._combo_sem.addItems(["1", "2"])
        self._combo_sem.setCurrentText(self._dados.semestre)
        self._combo_sem.setMaximumWidth(55)
        self._combo_sem.setStyleSheet(
            "QComboBox { font-size: 13px; padding: 4px; border: 1px solid #aaaaaa; border-radius: 4px; }"
        )
        self._combo_sem.currentTextChanged.connect(self._on_evento_changed)
        h_ano_sem.addWidget(self._combo_sem)
        h_ano_sem.addStretch()

        self._lbl_preview_evento = QLabel()
        self._lbl_preview_evento.setStyleSheet("font-size: 12px; color: #777777; font-style: italic;")
        h_ano_sem.addWidget(self._lbl_preview_evento)

        form.addRow("Ano / Semestre:", h_ano_sem)
        layout.addWidget(grupo_evento)

        self._atualizar_preview_evento()

        # --- Abas ---
        self._tabs = QTabWidget()
        self._tabs.setElideMode(Qt.ElideNone)          # nunca cortar texto das abas
        self._tabs.setUsesScrollButtons(False)          # sem seta de scroll — expande
        self._tabs.tabBar().setElideMode(Qt.ElideNone)
        self._tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #cccccc; border-radius: 4px; }"
            "QTabBar::tab { padding: 8px 20px; font-size: 13px; font-weight: bold; min-width: 140px; min-height: 24px; margin-right: 4px; }"
            "QTabBar::tab:selected { background: #1b365d; color: white; border-radius: 4px 4px 0 0; }"
            "QTabBar::tab:!selected { background: #e8e8e8; color: #555555; }"
        )

        self._aba_formandos = AbaFormandos(self._dados)
        self._aba_formandos.dados_alterados.connect(self._relay_change)
        self._tabs.addTab(self._aba_formandos, "🎓  Formandos")

        self._aba_mesa = AbaMesa(self._dados)
        self._aba_mesa.dados_alterados.connect(self._relay_change)
        self._tabs.addTab(self._aba_mesa, "🏛  Mesa de Honra")

        self._aba_homenageados = AbaHomenageados(self._dados)
        self._aba_homenageados.dados_alterados.connect(self._relay_change)
        self._tabs.addTab(self._aba_homenageados, "⭐  Homenageados")

        layout.addWidget(self._tabs, 1)

    def _input_style(self):
        return (
            "QLineEdit { font-size: 13px; padding: 4px 8px; border: 1px solid #aaaaaa;"
            "border-radius: 4px; }"
            "QLineEdit:focus { border: 1px solid #1b365d; }"
        )

    def _on_evento_changed(self):
        self._dados.ano = self._edit_ano.text().strip()
        self._dados.semestre = self._combo_sem.currentText()
        self._atualizar_preview_evento()
        self.dados_alterados.emit()

    def _atualizar_preview_evento(self):
        self._lbl_preview_evento.setText(f"→  {self._dados.texto_evento}")

    def _relay_change(self):
        self.dados_alterados.emit()
