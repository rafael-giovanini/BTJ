"""
Módulo: ui_historico_entradas.py

Responsabilidade:
    Exibir histórico industrial de entradas de insumos
    com filtros e totalizadores.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QDateEdit, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QDate
from core.database import conectar


class HistoricoEntradasView(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #0f172a; color: white;")

        layout = QVBoxLayout()

        # ---------------- FILTROS ----------------
        filtro_layout = QHBoxLayout()

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())

        self.combo_fornecedor = QComboBox()
        self.btn_filtrar = QPushButton("Filtrar")

        filtro_layout.addWidget(QLabel("Data Inicial"))
        filtro_layout.addWidget(self.data_inicio)
        filtro_layout.addWidget(QLabel("Data Final"))
        filtro_layout.addWidget(self.data_fim)
        filtro_layout.addWidget(QLabel("Fornecedor"))
        filtro_layout.addWidget(self.combo_fornecedor)
        filtro_layout.addWidget(self.btn_filtrar)

        # ---------------- TABELA ----------------
        self.tabela = QTableWidget()

        # ---------------- TOTALIZADORES ----------------
        self.lbl_total_qtd = QLabel("Total Quantidade: 0")
        self.lbl_total_valor = QLabel("Total Valor: R$ 0.00")

        layout.addLayout(filtro_layout)
        layout.addWidget(self.tabela)
        layout.addWidget(self.lbl_total_qtd)
        layout.addWidget(self.lbl_total_valor)

        self.setLayout(layout)

        # Conexões
        self.btn_filtrar.clicked.connect(self.carregar_dados)

        self.carregar_fornecedores()
        self.carregar_dados()

    # -------------------------------------------------
    # Carregar fornecedores no filtro
    # -------------------------------------------------
    def carregar_fornecedores(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("SELECT id, nome FROM fornecedores ORDER BY nome")
        fornecedores = cur.fetchall()

        conn.close()

        self.combo_fornecedor.clear()
        self.combo_fornecedor.addItem("Todos", None)

        for fid, nome in fornecedores:
            self.combo_fornecedor.addItem(nome, fid)

    # -------------------------------------------------
    # Carregar dados filtrados
    # -------------------------------------------------
    def carregar_dados(self):

        conn = conectar()
        cur = conn.cursor()

        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")
        fornecedor_id = self.combo_fornecedor.currentData()

        query = """
            SELECT
                e.data_entrada,
                e.numero_nf,
                i.nome,
                f.nome,
                e.quantidade,
                e.valor_unitario,
                e.valor_total
            FROM entrada_insumos e
            JOIN insumos i ON e.insumo_id = i.id
            JOIN fornecedores f ON e.fornecedor_id = f.id
            WHERE date(e.data_entrada) BETWEEN ? AND ?
        """

        params = [data_inicio, data_fim]

        if fornecedor_id:
            query += " AND f.id = ?"
            params.append(fornecedor_id)

        query += " ORDER BY e.data_entrada DESC"

        cur.execute(query, params)
        dados = cur.fetchall()

        conn.close()

        # Preencher tabela
        colunas = [
            "Data", "NF", "Insumo",
            "Fornecedor", "Qtd",
            "Vlr Unit", "Total"
        ]

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        total_qtd = 0
        total_valor = 0

        for r, linha in enumerate(dados):
            for c, valor in enumerate(linha):
                self.tabela.setItem(
                    r, c, QTableWidgetItem(str(valor))
                )

            total_qtd += float(linha[4])
            total_valor += float(linha[6])

        self.lbl_total_qtd.setText(f"Total Quantidade: {total_qtd:.2f}")
        self.lbl_total_valor.setText(f"Total Valor: R$ {total_valor:.2f}")

    # -------------------------------------------------
    # Método padrão de atualização
    # -------------------------------------------------
    def atualizar(self):
        self.carregar_fornecedores()
        self.carregar_dados()