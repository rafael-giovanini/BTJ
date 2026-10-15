"""
Módulo: ui_insumos.py
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox,
    QCheckBox
)
from PyQt6.QtCore import Qt

from core.database import conectar


class InsumosView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)

        btn_salvar = QPushButton("Salvar alterações")
        btn_salvar.clicked.connect(self.salvar)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

        self.carregar()

    def atualizar(self):
        self.carregar()

    def carregar(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, codigo, nome, unidade_base, custo_unitario, ativo
            FROM insumos
            ORDER BY codigo
        """)

        dados = cur.fetchall()
        conn.close()

        colunas = [
            "ID",
            "Código",
            "Nome",
            "Unidade Base",
            "Custo Unitário",
            "Ativo"
        ]

        self.tabela.clear()
        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        for r, linha in enumerate(dados):
            for c, valor in enumerate(linha):

                # Checkbox para ativo
                if c == 5:
                    checkbox = QCheckBox()
                    checkbox.setChecked(bool(valor))
                    checkbox.setStyleSheet("margin-left:50%; margin-right:50%;")
                    self.tabela.setCellWidget(r, c, checkbox)
                    continue

                item = QTableWidgetItem("" if valor is None else str(valor))

                if c in (0, 1, 3):
                    item.setFlags(
                        item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )

                self.tabela.setItem(r, c, item)

        self.tabela.resizeColumnsToContents()

    def salvar(self):

        conn = conectar()
        cur = conn.cursor()

        for row in range(self.tabela.rowCount()):

            id_item = self.tabela.item(row, 0)
            nome_item = self.tabela.item(row, 2)
            custo_item = self.tabela.item(row, 4)
            checkbox = self.tabela.cellWidget(row, 5)

            if not id_item:
                continue

            insumo_id = id_item.text()
            nome = nome_item.text() if nome_item else ""

            try:
                custo = float(custo_item.text()) if custo_item else 0.0
            except ValueError:
                QMessageBox.warning(self, "Erro", "Custo inválido.")
                conn.close()
                return

            ativo = 1 if checkbox.isChecked() else 0

            cur.execute("""
                UPDATE insumos
                SET nome = ?, custo_unitario = ?, ativo = ?
                WHERE id = ?
            """, (nome, custo, ativo, insumo_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sucesso", "Alterações salvas.")
        self.carregar()