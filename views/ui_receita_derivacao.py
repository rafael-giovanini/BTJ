import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)

DB = "btj.db"


class TelaReceitaDerivacao(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BTJ — Receita por Derivação")
        self.resize(900, 520)

        layout = QVBoxLayout()

        # seleção derivação
        layout.addWidget(QLabel("Derivação"))
        self.combo_der = QComboBox()
        layout.addWidget(self.combo_der)

        # linha adicionar insumo
        linha = QHBoxLayout()

        self.combo_insumo = QComboBox()
        self.edit_qtd = QLineEdit()
        self.edit_qtd.setPlaceholderText("Quantidade")

        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self.adicionar)

        linha.addWidget(self.combo_insumo)
        linha.addWidget(self.edit_qtd)
        linha.addWidget(btn_add)

        layout.addLayout(linha)

        # tabela
        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)

        btn_salvar = QPushButton("Salvar Receita")
        btn_salvar.clicked.connect(self.salvar)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

        self.carregar_combos()
        self.carregar_receita()

        self.combo_der.currentIndexChanged.connect(self.carregar_receita)

    def conectar(self):
        return sqlite3.connect(DB)

    def carregar_combos(self):
        conn = self.conectar()
        cur = conn.cursor()

        # derivações
        cur.execute("""
            SELECT id, descricao_derivada
            FROM derivacoes_produto
            ORDER BY descricao_derivada
        """)
        self.derivacoes = cur.fetchall()

        self.combo_der.clear()
        for did, nome in self.derivacoes:
            self.combo_der.addItem(nome, did)

        # insumos
        cur.execute("SELECT id, nome FROM insumos ORDER BY nome")
        self.insumos = cur.fetchall()

        self.combo_insumo.clear()
        for iid, nome in self.insumos:
            self.combo_insumo.addItem(nome, iid)

        conn.close()

    def adicionar(self):
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)

        self.tabela.setItem(row, 0,
            QTableWidgetItem(self.combo_insumo.currentText()))
        self.tabela.setItem(row, 1,
            QTableWidgetItem(self.edit_qtd.text()))

    def carregar_receita(self):
        did = self.combo_der.currentData()

        conn = self.conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT i.nome, r.quantidade
            FROM receita_derivacao r
            JOIN insumos i ON i.id = r.insumo_id
            WHERE r.derivacao_id = ?
        """, (did,))

        dados = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(2)
        self.tabela.setHorizontalHeaderLabels(["Insumo", "Quantidade"])

        for r, (nome, qtd) in enumerate(dados):
            self.tabela.setItem(r, 0, QTableWidgetItem(nome))
            self.tabela.setItem(r, 1, QTableWidgetItem(str(qtd)))

    def salvar(self):
        did = self.combo_der.currentData()

        conn = self.conectar()
        cur = conn.cursor()

        cur.execute("DELETE FROM receita_derivacao WHERE derivacao_id = ?", (did,))

        for row in range(self.tabela.rowCount()):
            nome = self.tabela.item(row, 0).text()
            qtd = self.tabela.item(row, 1).text()

            iid = next(i for i, n in self.insumos if n == nome)

            cur.execute("""
                INSERT INTO receita_derivacao
                (derivacao_id, insumo_id, quantidade)
                VALUES (?, ?, ?)
            """, (did, iid, qtd))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Receita salva")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TelaReceitaDerivacao()
    w.show()
    app.exec()
