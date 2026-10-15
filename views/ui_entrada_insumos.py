"""
Módulo: ui_entrada_insumos.py

Responsabilidade:
    Exibir histórico de entradas de itens.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from core.database import conectar


class EntradaInsumosView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)

        self.setLayout(layout)
        self.carregar()

    def atualizar(self):
        self.carregar()

    def carregar(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                e.data_entrada,
                e.numero_nf,
                i.codigo,
                i.descricao,
                f.nome,
                e.quantidade,
                e.valor_unitario,
                e.valor_total
            FROM entrada_itens e
            JOIN itens i ON e.item_id = i.id
            JOIN fornecedores f ON e.fornecedor_id = f.id
            ORDER BY e.data_entrada DESC
        """)

        dados = cur.fetchall()
        conn.close()

        colunas = [
            "Data", "NF", "Código",
            "Descrição", "Fornecedor",
            "Quantidade", "Vlr Unit", "Vlr Total"
        ]

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        for r, linha in enumerate(dados):
            for c, valor in enumerate(linha):
                self.tabela.setItem(r, c, QTableWidgetItem(str(valor)))

        self.tabela.resizeColumnsToContents()