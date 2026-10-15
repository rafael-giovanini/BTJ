import sys
import sqlite3

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHBoxLayout,
    QLineEdit
)

DB = "btj.db"


class TelaEditorReceita(QWidget):
    """
    Editor completo da estrutura (BOM).

    Permite:
    - Visualizar itens
    - Editar inline
    - Excluir
    - Adicionar novo item
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Editor Completo de Receita (BOM)")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        # ---------------- DERIVAÇÃO ----------------
        layout.addWidget(QLabel("Derivação"))

        self.combo_der = QComboBox()
        self.combo_der.currentTextChanged.connect(self.carregar_receita)
        layout.addWidget(self.combo_der)

        # ---------------- ÁREA DE INSERÇÃO ----------------
        layout.addWidget(QLabel("Adicionar novo item"))

        insert_layout = QHBoxLayout()

        self.combo_ins = QComboBox()
        insert_layout.addWidget(self.combo_ins)

        self.edit_qtd = QLineEdit()
        self.edit_qtd.setPlaceholderText("Qtd")
        insert_layout.addWidget(self.edit_qtd)

        # Combo de unidades padronizadas
        self.combo_un = QComboBox()
        self.combo_un.addItems([
            "kg",
            "un",
            "m",
            "g",
            "cx",
            "pct"
        ])
        insert_layout.addWidget(self.combo_un)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["MP", "EMB"])
        insert_layout.addWidget(self.combo_tipo)

        self.btn_add = QPushButton("Adicionar")
        self.btn_add.clicked.connect(self.adicionar_item)
        insert_layout.addWidget(self.btn_add)

        layout.addLayout(insert_layout)

        # ---------------- TABELA ----------------
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Insumo", "Qtd", "Unidade", "Tipo", "ID"
        ])
        self.tabela.setColumnHidden(5, True)
        layout.addWidget(self.tabela)

        # ---------------- BOTÕES ----------------
        btn_layout = QHBoxLayout()

        self.btn_salvar = QPushButton("Salvar alterações")
        self.btn_salvar.clicked.connect(self.salvar_alteracoes)
        btn_layout.addWidget(self.btn_salvar)

        self.btn_excluir = QPushButton("Excluir item")
        self.btn_excluir.clicked.connect(self.excluir_item)
        btn_layout.addWidget(self.btn_excluir)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.carregar_derivacoes()
        self.carregar_insumos()

    # -------------------------------------------------
    # Carrega derivações disponíveis
    # -------------------------------------------------
    def carregar_derivacoes(self):
        self.combo_der.clear()

        conn = sqlite3.connect(DB)
        dados = conn.execute("""
            SELECT DISTINCT derivacao_nome
            FROM receita_derivacao
            ORDER BY derivacao_nome
        """).fetchall()
        conn.close()

        for (nome,) in dados:
            self.combo_der.addItem(nome)

    # -------------------------------------------------
    # Carrega lista de insumos para combo
    # -------------------------------------------------
    def carregar_insumos(self):
        conn = sqlite3.connect(DB)
        dados = conn.execute("""
            SELECT codigo, nome
            FROM insumos
            ORDER BY nome
        """).fetchall()
        conn.close()

        for cod, nome in dados:
            self.combo_ins.addItem(f"{nome} ({cod})", (cod, nome))

    # -------------------------------------------------
    # Carrega receita da derivação
    # -------------------------------------------------
    def carregar_receita(self):
        derivacao = self.combo_der.currentText()

        conn = sqlite3.connect(DB)
        dados = conn.execute("""
            SELECT id, insumo_codigo, insumo_nome,
                   quantidade, unidade, tipo_item
            FROM receita_derivacao
            WHERE derivacao_nome = ?
        """, (derivacao,)).fetchall()
        conn.close()

        self.tabela.setRowCount(len(dados))

        for row, (id_, cod, nome, qtd, un, tipo) in enumerate(dados):

            self.tabela.setItem(row, 0, QTableWidgetItem(str(cod)))
            self.tabela.setItem(row, 1, QTableWidgetItem(nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(str(qtd)))
            self.tabela.setItem(row, 3, QTableWidgetItem(un))
            self.tabela.setItem(row, 4, QTableWidgetItem(tipo))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(id_)))

    # -------------------------------------------------
    # Adiciona novo item na receita
    # -------------------------------------------------
    def adicionar_item(self):

        derivacao = self.combo_der.currentText()
        cod, nome = self.combo_ins.currentData()

        try:
            qtd = float(self.edit_qtd.text().replace(",", "."))
        except:
            QMessageBox.warning(self, "Erro", "Quantidade inválida")
            return

        un = self.combo_un.currentText()
        tipo = self.combo_tipo.currentText()

        conn = sqlite3.connect(DB)
        conn.execute("""
            INSERT INTO receita_derivacao
            (derivacao_nome, insumo_codigo, insumo_nome,
             quantidade, unidade, tipo_item)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (derivacao, cod, nome, qtd, un, tipo))
        conn.commit()
        conn.close()

        self.edit_qtd.clear()

        self.carregar_receita()
        QMessageBox.information(self, "OK", "Item adicionado.")

    # -------------------------------------------------
    # Salva alterações feitas na tabela
    # -------------------------------------------------
    def salvar_alteracoes(self):

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        for row in range(self.tabela.rowCount()):
            id_item = self.tabela.item(row, 5).text()
            qtd = float(self.tabela.item(row, 2).text().replace(",", "."))
            un = self.tabela.item(row, 3).text()
            tipo = self.tabela.item(row, 4).text()

            cur.execute("""
                UPDATE receita_derivacao
                SET quantidade = ?, unidade = ?, tipo_item = ?
                WHERE id = ?
            """, (qtd, un, tipo, id_item))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Alterações salvas.")

    # -------------------------------------------------
    # Exclui item selecionado
    # -------------------------------------------------
    def excluir_item(self):

        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um item.")
            return

        id_item = self.tabela.item(linha, 5).text()

        conn = sqlite3.connect(DB)
        conn.execute("""
            DELETE FROM receita_derivacao
            WHERE id = ?
        """, (id_item,))
        conn.commit()
        conn.close()

        self.carregar_receita()
        QMessageBox.information(self, "OK", "Item excluído.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TelaEditorReceita()
    w.show()
    app.exec()
