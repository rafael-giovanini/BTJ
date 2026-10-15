"""
Módulo: ui_derivacoes.py

Camada:
    views

Responsabilidade:
    Gerenciar derivações vinculadas a itens do tipo PRODUZIDO (P).

Modelo Atual:
    - Tabela principal: itens
    - Produtos são identificados por tipo_item = 'P'
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from core.database import conectar


class DerivacoesView(QWidget):

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
    # 🔄 Atualização padrão (MainWindow usa)
    # -------------------------------------------------
    def atualizar(self):
        self.carregar()

    # -------------------------------------------------
    # 📦 Carregar derivações
    # -------------------------------------------------
    def carregar(self):

        conn = conectar()
        cur = conn.cursor()

        # 🔥 Correção: usar tipo_item = 'P'
        cur.execute("""
            SELECT
                d.id,
                i.codigo,
                i.descricao,
                d.codigo_emb,
                d.peso_base,
                d.ativo
            FROM derivacoes d
            JOIN itens i ON d.item_id = i.id
            WHERE i.tipo_item = 'P'
            ORDER BY i.codigo
        """)

        dados = cur.fetchall()
        conn.close()

        colunas = [
            "ID",
            "Produto Código",
            "Descrição",
            "Código EMB",
            "Peso Base",
            "Ativo"
        ]

        self.tabela.setRowCount(len(dados))
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)

        for r, linha in enumerate(dados):
            for c, valor in enumerate(linha):

                item = QTableWidgetItem("" if valor is None else str(valor))

                # Não editáveis:
                # ID, Código Produto, Descrição, Código EMB
                if c in (0, 1, 2, 3):
                    item.setFlags(
                        item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )

                self.tabela.setItem(r, c, item)

        self.tabela.resizeColumnsToContents()

    # -------------------------------------------------
    # 💾 Salvar alterações
    # -------------------------------------------------
    def salvar(self):

        conn = conectar()
        cur = conn.cursor()

        for row in range(self.tabela.rowCount()):

            deriv_id_item = self.tabela.item(row, 0)
            peso_base_item = self.tabela.item(row, 4)
            ativo_item = self.tabela.item(row, 5)

            if not deriv_id_item:
                continue

            deriv_id = deriv_id_item.text()

            try:
                peso_base = float(peso_base_item.text()) if peso_base_item else 0
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Erro",
                    f"Linha {row+1}: Peso base inválido."
                )
                conn.close()
                return

            try:
                ativo = int(ativo_item.text()) if ativo_item else 0
                if ativo not in (0, 1):
                    raise ValueError
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Erro",
                    f"Linha {row+1}: Ativo deve ser 0 ou 1."
                )
                conn.close()
                return

            cur.execute("""
                UPDATE derivacoes
                SET peso_base = ?, ativo = ?
                WHERE id = ?
            """, (peso_base, ativo, deriv_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sucesso", "Alterações salvas.")
        self.carregar()