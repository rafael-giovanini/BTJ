"""
Módulo: ui_produtos.py

Camada:
    views

Responsabilidade:
    Exibir e permitir edição básica dos produtos.

Regra:
    - Código não pode ser alterado.
    - Descrição pode ser editada.
    - Produto pode ser ativado/desativado.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from core.database import conectar


class ProdutosView(QWidget):

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

    # -------------------------------------------------
    # Carrega produtos do banco
    # -------------------------------------------------
    def carregar(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, codigo, descricao, unidade_base, tipo, familia, ativo
            FROM produtos
            ORDER BY codigo
        """)

        dados = cur.fetchall()
        conn.close()

        colunas = ["ID", "Código", "Descrição", "Unidade Base", "Tipo", "Família", "Ativo"]

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        for r, linha in enumerate(dados):
            for c, valor in enumerate(linha):

                item = QTableWidgetItem(str(valor))

                # ID e Código não editáveis
                if c in (0, 1):
                    item.setFlags(
                        item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )

                self.tabela.setItem(r, c, item)

        self.tabela.resizeColumnsToContents()

    # -------------------------------------------------
    # Salva alterações
    # -------------------------------------------------
    def salvar(self):

        conn = conectar()
        cur = conn.cursor()

        for row in range(self.tabela.rowCount()):

            id_prod = self.tabela.item(row, 0).text()
            descricao = self.tabela.item(row, 2).text()
            ativo = self.tabela.item(row, 3).text()

            cur.execute("""
                UPDATE produtos
                SET descricao = ?, ativo = ?
                WHERE id = ?
            """, (descricao, ativo, id_prod))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Sucesso",
            "Alterações salvas com sucesso."
        )