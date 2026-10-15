import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox
)

DB = "btj.db"


class TelaReceitaManual(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cadastro manual de receita")
        self.resize(420, 300)

        layout = QVBoxLayout()

        # -------- derivação --------
        layout.addWidget(QLabel("Derivação"))
        self.combo_der = QComboBox()
        layout.addWidget(self.combo_der)

        # -------- insumo --------
        layout.addWidget(QLabel("Insumo"))
        self.combo_ins = QComboBox()
        layout.addWidget(self.combo_ins)

        # -------- quantidade --------
        layout.addWidget(QLabel("Quantidade"))
        self.edit_qtd = QLineEdit()
        layout.addWidget(self.edit_qtd)

        # -------- unidade --------
        layout.addWidget(QLabel("Unidade"))
        self.edit_un = QLineEdit()
        layout.addWidget(self.edit_un)

        # -------- tipo --------
        layout.addWidget(QLabel("Tipo"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["MP", "EMB"])
        layout.addWidget(self.combo_tipo)

        # -------- botão --------
        btn = QPushButton("Salvar item na receita")
        btn.clicked.connect(self.salvar)
        layout.addWidget(btn)

        self.setLayout(layout)

        self.carregar()

    # ------------------------------

    def carregar(self):
        conn = sqlite3.connect(DB)

        # derivações
        ders = conn.execute("""
            select descricao from derivacoes_produto
            order by descricao
        """).fetchall()

        for (d,) in ders:
            self.combo_der.addItem(d)

        # insumos
        ins = conn.execute("""
            select codigo, nome from insumos
            order by nome
        """).fetchall()

        for cod, nome in ins:
            self.combo_ins.addItem(f"{nome} ({cod})", (cod, nome))

        conn.close()

    # ------------------------------

    def salvar(self):

        der = self.combo_der.currentText()
        cod, nome = self.combo_ins.currentData()

        try:
            qtd = float(self.edit_qtd.text().replace(",", "."))
        except:
            QMessageBox.warning(self, "Erro", "Quantidade inválida")
            return

        un = self.edit_un.text().strip()
        tipo = self.combo_tipo.currentText()

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
            insert into receita_derivacao
            (derivacao_nome, insumo_codigo, insumo_nome,
             quantidade, unidade, tipo_item)
            values (?, ?, ?, ?, ?, ?)
        """, (der, cod, nome, qtd, un, tipo))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Item inserido na receita")
