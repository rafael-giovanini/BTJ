"""
Módulo: ui_itens.py

Camada:
    views

Responsabilidade:
    Exibir e editar todos os itens do sistema BTJ
    (modelo unificado industrial).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox,
    QComboBox, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt

from core.database import conectar


class ItensView(QWidget):

    def __init__(self):
        super().__init__()

        layout_principal = QVBoxLayout()

        # 🔹 Filtro
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Categoria:"))

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(
            ["TODOS", "PRODUTO", "INSUMO", "MATERIAL", "IMOBILIZADO"]
        )
        self.combo_categoria.currentIndexChanged.connect(self.carregar)

        filtro_layout.addWidget(self.combo_categoria)
        filtro_layout.addStretch()
        layout_principal.addLayout(filtro_layout)

        # 🔹 Tabela
        self.tabela = QTableWidget()
        layout_principal.addWidget(self.tabela)

        # 🔹 Botão salvar
        btn_salvar = QPushButton("Salvar alterações")
        btn_salvar.clicked.connect(self.salvar)
        layout_principal.addWidget(btn_salvar)

        self.setLayout(layout_principal)
        self.carregar()

    # -------------------------------------------------
    # 🔄 Atualizar
    # -------------------------------------------------
    def atualizar(self):
        self.carregar()

    # -------------------------------------------------
    # 🔷 Carregar dados
    # -------------------------------------------------
    def carregar(self):

        categoria = self.combo_categoria.currentText()

        conn = conectar()
        cur = conn.cursor()

        sql = """
            SELECT
                id,
                codigo,
                descricao,
                familia,
                unidade_base,
                subtipo,
                descricao_tipo,
                custo_unitario,
                ativo
            FROM itens
        """

        if categoria != "TODOS":
            sql += " WHERE categoria = ? ORDER BY codigo"
            cur.execute(sql, (categoria,))
        else:
            sql += " ORDER BY codigo"
            cur.execute(sql)

        dados = cur.fetchall()
        conn.close()

        # 🔥 NÃO mostramos ID visualmente
        colunas = [
            "Código",
            "Descrição",
            "Família",
            "Unidade Base",
            "Tipo",
            "Origem",
            "Custo Unit.",
            "Ativo"
        ]

        self.tabela.clear()
        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        for r, linha in enumerate(dados):

            item_id = linha[0]  # ID interno

            # Mapeamento ignorando ID
            dados_visuais = linha[1:]

            for c, valor in enumerate(dados_visuais):

                # 🔹 Custo formatado como moeda
                if c == 6:
                    valor = 0 if valor is None else float(valor)
                    item = QTableWidgetItem(f"{valor:,.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                # 🔹 Ativo como checkbox
                elif c == 7:
                    checkbox = QCheckBox()
                    checkbox.setChecked(bool(valor))

                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.addWidget(checkbox)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.setContentsMargins(0, 0, 0, 0)

                    self.tabela.setCellWidget(r, c, container)
                    continue

                else:
                    item = QTableWidgetItem("" if valor is None else str(valor))

                    # 🔹 Campos não editáveis
                    if c in (0, 4, 5):  # Código, Tipo, Origem
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self.tabela.setItem(r, c, item)

            # Guardar ID oculto
            self.tabela.setVerticalHeaderItem(r, QTableWidgetItem(str(item_id)))

        self.tabela.resizeColumnsToContents()

    # -------------------------------------------------
    # 💾 Salvar alterações
    # -------------------------------------------------
    def salvar(self):

        conn = conectar()
        cur = conn.cursor()

        for row in range(self.tabela.rowCount()):

            item_id = self.tabela.verticalHeaderItem(row).text()

            descricao = self.tabela.item(row, 1).text()
            custo_texto = self.tabela.item(row, 6).text().replace(",", "")
            container = self.tabela.cellWidget(row, 7)
            checkbox = container.layout().itemAt(0).widget()
            ativo = 1 if checkbox.isChecked() else 0

            try:
                custo = float(custo_texto) if custo_texto else 0.0
            except:
                QMessageBox.warning(self, "Erro", "Custo inválido.")
                conn.close()
                return

            cur.execute("""
                UPDATE itens
                SET descricao = ?, custo_unitario = ?, ativo = ?
                WHERE id = ?
            """, (descricao, custo, ativo, item_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sucesso", "Alterações salvas.")
        self.carregar()