import sys
import sqlite3

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QComboBox, QLineEdit,
    QPushButton, QTextEdit, QMessageBox
)

DB = "btj.db"


class TelaCalculo(QWidget):
    """
    Tela de cálculo baseada na nova estrutura:

    Produto (PAC) → Derivação (EMB) → Receita

    Permite:
    - Selecionar produto
    - Selecionar embalagem
    - Visualizar peso_base
    - Informar kg produzido
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BTJ — Cálculo de Custo v3")
        self.resize(750, 550)

        layout = QVBoxLayout()

        # ---------------- PRODUTO ----------------
        layout.addWidget(QLabel("Produto (PAC)"))
        self.combo_produto = QComboBox()
        self.combo_produto.currentIndexChanged.connect(self.carregar_derivacoes)
        layout.addWidget(self.combo_produto)

        # ---------------- DERIVAÇÃO ----------------
        layout.addWidget(QLabel("Embalagem (EMB)"))
        self.combo_derivacao = QComboBox()
        self.combo_derivacao.currentIndexChanged.connect(self.mostrar_peso_base)
        layout.addWidget(self.combo_derivacao)

        # ---------------- PESO BASE ----------------
        self.lbl_peso = QLabel("Peso base: -")
        layout.addWidget(self.lbl_peso)

        # ---------------- KG DIGITADO ----------------
        layout.addWidget(QLabel("Kg produzido / vendido"))
        self.edit_kg = QLineEdit()
        self.edit_kg.setPlaceholderText("Ex: 500 ou 500,0")
        layout.addWidget(self.edit_kg)

        # ---------------- BOTÃO CALCULAR ----------------
        btn = QPushButton("Calcular custo")
        btn.clicked.connect(self.calcular)
        layout.addWidget(btn)

        # ---------------- SAÍDA ----------------
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        layout.addWidget(self.out)

        self.setLayout(layout)

        self.carregar_produtos()

    # -------------------------------------------------
    # Carrega lista de produtos (PAC)
    # -------------------------------------------------
    def carregar_produtos(self):

        self.combo_produto.clear()

        conn = sqlite3.connect(DB)
        dados = conn.execute("""
            SELECT id, codigo
            FROM produtos
            ORDER BY codigo
        """).fetchall()
        conn.close()

        for id_, codigo in dados:
            self.combo_produto.addItem(codigo, id_)

    # -------------------------------------------------
    # Carrega derivações do produto selecionado
    # -------------------------------------------------
    def carregar_derivacoes(self):

        self.combo_derivacao.clear()
        self.lbl_peso.setText("Peso base: -")

        produto_id = self.combo_produto.currentData()

        if not produto_id:
            return

        conn = sqlite3.connect(DB)
        dados = conn.execute("""
            SELECT id, codigo_emb
            FROM derivacoes
            WHERE produto_id = ?
        """, (produto_id,)).fetchall()
        conn.close()

        for id_, codigo_emb in dados:
            self.combo_derivacao.addItem(codigo_emb, id_)

    # -------------------------------------------------
    # Mostra peso_base da derivação selecionada
    # -------------------------------------------------
    def mostrar_peso_base(self):

        derivacao_id = self.combo_derivacao.currentData()

        if not derivacao_id:
            return

        conn = sqlite3.connect(DB)
        result = conn.execute("""
            SELECT peso_base
            FROM derivacoes
            WHERE id = ?
        """, (derivacao_id,)).fetchone()
        conn.close()

        if result:
            self.lbl_peso.setText(f"Peso base: {result[0]} kg")

    # -------------------------------------------------
    # Placeholder para cálculo (motor será ligado depois)
    # -------------------------------------------------
    def calcular(self):

        if not self.edit_kg.text().strip():
            QMessageBox.warning(self, "Aviso", "Informe os kg.")
            return

        try:
            kg = float(self.edit_kg.text().replace(",", "."))
        except:
            QMessageBox.warning(self, "Erro", "Kg inválido.")
            return

        if kg <= 0:
            QMessageBox.warning(self, "Erro", "Kg deve ser maior que zero.")
            return

        produto = self.combo_produto.currentText()
        derivacao = self.combo_derivacao.currentText()

        self.out.setText(
            f"Produto: {produto}\n"
            f"Derivação: {derivacao}\n"
            f"Kg informado: {kg}\n\n"
            "Motor de cálculo será integrado na próxima etapa."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TelaCalculo()
    w.show()
    app.exec()
