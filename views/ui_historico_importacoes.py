"""
Módulo: ui_historico_importacoes.py

Responsabilidade:
    Exibir histórico completo das importações realizadas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem
)
from core.database import conectar


class HistoricoImportacoesView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)

        self.setLayout(layout)

        self.carregar()

    # -------------------------------------------------
    # 🔄 Atualização padrão
    # -------------------------------------------------
    def atualizar(self):
        self.carregar()

    # -------------------------------------------------
    # Carregar histórico
    # -------------------------------------------------
    def carregar(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                tipo_importacao,
                arquivo,
                data_execucao,
                registros_importados,
                itens_criados,
                duplicados
            FROM historico_importacoes
            ORDER BY data_execucao DESC
        """)

        dados = cur.fetchall()
        conn.close()

        colunas = [
            "Tipo",
            "Arquivo",
            "Data Execução",
            "Importados",
            "Itens Criados",
            "Duplicados"
        ]

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        for r, linha in enumerate(dados):
            for c, valor in enumerate(linha):
                self.tabela.setItem(r, c, QTableWidgetItem(str(valor)))

        self.tabela.resizeColumnsToContents()