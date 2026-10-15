"""
Módulo: ui_receitas.py

Camada:
    views

Responsabilidade:
    Gerenciar estrutura (BOM) das derivações.

Modelo Atual:
    - Derivação pertence a item tipo P
    - Receita usa itens tipo C
    - Classificação MP / EMB baseada na unidade
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit,
    QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt

from core.database import conectar


class ReceitasView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # ---------------- Derivação ----------------
        layout.addWidget(QLabel("Derivação"))

        self.combo_derivacao = QComboBox()
        layout.addWidget(self.combo_derivacao)

        # ---------------- Inserção de item ----------------
        linha = QHBoxLayout()

        self.combo_item = QComboBox()
        self.edit_qtd = QLineEdit()
        self.edit_qtd.setPlaceholderText("Quantidade")

        self.edit_unidade = QLineEdit()
        self.edit_unidade.setPlaceholderText("Unidade (kg, un, pct...)")

        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self.adicionar)

        linha.addWidget(self.combo_item)
        linha.addWidget(self.edit_qtd)
        linha.addWidget(self.edit_unidade)
        linha.addWidget(btn_add)

        layout.addLayout(linha)

        # ---------------- Tabela ----------------
        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)

        btn_salvar = QPushButton("Salvar Receita")
        btn_salvar.clicked.connect(self.salvar)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)

        self.carregar_combos()
        self.carregar_receita()

        self.combo_derivacao.currentIndexChanged.connect(self.carregar_receita)

    # -------------------------------------------------
    # 🔄 Atualização padrão
    # -------------------------------------------------
    def atualizar(self):
        self.carregar_combos()
        self.carregar_receita()

    # -------------------------------------------------
    # 📦 Carregar Combos
    # -------------------------------------------------
    def carregar_combos(self):

        conn = conectar()
        cur = conn.cursor()

        # 🔹 Derivações → somente itens tipo P
        cur.execute("""
            SELECT d.id, i.codigo
            FROM derivacoes d
            JOIN itens i ON d.item_id = i.id
            WHERE i.tipo_item = 'P'
            ORDER BY i.codigo
        """)
        derivacoes = cur.fetchall()

        self.combo_derivacao.clear()
        for did, codigo in derivacoes:
            self.combo_derivacao.addItem(codigo, did)

        # 🔹 Itens para receita → somente tipo C (Comprado)
        cur.execute("""
            SELECT id, descricao
            FROM itens
            WHERE tipo_item = 'C'
            AND ativo = 1
            ORDER BY descricao
        """)
        itens = cur.fetchall()

        self.combo_item.clear()
        for iid, nome in itens:
            self.combo_item.addItem(nome, iid)

        conn.close()

    # -------------------------------------------------
    # ➕ Adicionar item temporário
    # -------------------------------------------------
    def adicionar(self):

        row = self.tabela.rowCount()
        self.tabela.insertRow(row)

        self.tabela.setItem(
            row, 0,
            QTableWidgetItem(self.combo_item.currentText())
        )

        self.tabela.setItem(
            row, 1,
            QTableWidgetItem(self.edit_qtd.text())
        )

        self.tabela.setItem(
            row, 2,
            QTableWidgetItem(self.edit_unidade.text())
        )

    # -------------------------------------------------
    # 📥 Carregar Receita
    # -------------------------------------------------
    def carregar_receita(self):

        deriv_id = self.combo_derivacao.currentData()

        if not deriv_id:
            return

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT i.descricao, r.quantidade, r.unidade
            FROM receita_derivacao r
            JOIN itens i ON i.id = r.item_id
            WHERE r.derivacao_id = ?
        """, (deriv_id,))

        dados = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(
            ["Item", "Quantidade", "Unidade"]
        )

        for r, (nome, qtd, unidade) in enumerate(dados):
            self.tabela.setItem(r, 0, QTableWidgetItem(nome))
            self.tabela.setItem(r, 1, QTableWidgetItem(str(qtd)))
            self.tabela.setItem(r, 2, QTableWidgetItem(unidade))

    # -------------------------------------------------
    # 💾 Salvar Receita
    # -------------------------------------------------
    def salvar(self):

        deriv_id = self.combo_derivacao.currentData()

        conn = conectar()
        cur = conn.cursor()

        # Remover receita antiga
        cur.execute("""
            DELETE FROM receita_derivacao
            WHERE derivacao_id = ?
        """, (deriv_id,))

        for row in range(self.tabela.rowCount()):

            nome = self.tabela.item(row, 0).text()
            qtd = self.tabela.item(row, 1).text()
            unidade = self.tabela.item(row, 2).text().lower()

            try:
                qtd = float(qtd)
            except:
                QMessageBox.warning(
                    self,
                    "Erro",
                    f"Linha {row+1}: Quantidade inválida."
                )
                conn.close()
                return

            # Buscar item_id
            cur.execute(
                "SELECT id FROM itens WHERE descricao = ?",
                (nome,)
            )
            item = cur.fetchone()

            if not item:
                continue

            item_id = item[0]

            # Regra industrial MP vs EMB
            tipo_item_receita = "MP" if unidade == "kg" else "EMB"

            cur.execute("""
                INSERT INTO receita_derivacao
                (derivacao_id, item_id, quantidade, unidade, tipo_item)
                VALUES (?, ?, ?, ?, ?)
            """, (deriv_id, item_id, qtd, unidade, tipo_item_receita))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Sucesso",
            "Receita salva com sucesso."
        )

        self.carregar_receita()