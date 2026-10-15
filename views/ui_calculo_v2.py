import sys
import sqlite3

# Componentes de interface do PyQt6
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QComboBox, QLineEdit,
    QPushButton, QTextEdit, QMessageBox
)

# Motor de cálculo de custo
from btj.calc_v2 import calcular_custo_por_kg

# Caminho do banco SQLite
DB = "btj.db"


class TelaCalculo(QWidget):
    def __init__(self):
        super().__init__()

        # ----- Configuração básica da janela -----
        self.setWindowTitle("BTJ — Cálculo de Custo")
        self.resize(720, 560)

        layout = QVBoxLayout()

        # ----- Campo: seleção da derivação -----
        layout.addWidget(QLabel("Derivação"))
        self.combo = QComboBox()
        layout.addWidget(self.combo)

        # ----- Campo: kg produzido/vendido -----
        layout.addWidget(QLabel("Kg produzido / vendido"))
        self.edit_kg = QLineEdit()
        self.edit_kg.setPlaceholderText("ex: 500 ou 500,0")
        layout.addWidget(self.edit_kg)

        # ----- Botão executar cálculo -----
        btn = QPushButton("Calcular custo")
        btn.clicked.connect(self.calcular)
        layout.addWidget(btn)

        # ----- Área de saída do relatório -----
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        layout.addWidget(self.out)

        self.setLayout(layout)

        # Carrega derivações disponíveis no banco
        self.carregar_derivacoes()

    # ------------------------------------------------
    # Busca derivações existentes na BOM e popula o combo
    def carregar_derivacoes(self):
        self.combo.clear()

        conn = sqlite3.connect(DB)

        dados = conn.execute("""
            SELECT DISTINCT derivacao_nome
            FROM receita_derivacao
            ORDER BY derivacao_nome
        """).fetchall()

        conn.close()

        for (nome,) in dados:
            self.combo.addItem(nome)

    # ------------------------------------------------
    # Converte número digitado aceitando vírgula decimal
    def _parse_float(self, txt):
        txt = txt.strip().replace(",", ".")
        return float(txt)

    # ------------------------------------------------
    # Executa cálculo de custo
    def calcular(self):

        # --- valida se existem derivações carregadas ---
        if self.combo.count() == 0:
            QMessageBox.warning(self, "Aviso", "Nenhuma derivação carregada.")
            return

        # --- valida campo kg preenchido ---
        if not self.edit_kg.text().strip():
            QMessageBox.warning(self, "Aviso", "Informe os kg.")
            return

        # --- converte texto para número ---
        try:
            kg = self._parse_float(self.edit_kg.text())
        except ValueError:
            QMessageBox.critical(self, "Erro", "Kg inválido.")
            return

        # ✅ VALIDAÇÃO PEDIDA — impedir zero ou negativo
        if kg <= 0:
            QMessageBox.warning(self, "Aviso", "Kg deve ser maior que zero.")
            return

        derivacao = self.combo.currentText()

        # --- chama motor de cálculo ---
        try:
            fator, itens, total = calcular_custo_por_kg(derivacao, kg)
        except Exception as e:
            QMessageBox.critical(self, "Erro de cálculo", str(e))
            return

        # --- acumuladores de totais ---
        total_mp = 0
        total_emb = 0

        linhas = []
        linhas.append(f"Derivação: {derivacao}")
        linhas.append(f"Kg base cálculo: {kg:.3f}")
        linhas.append(f"Fator escala: {fator:.4f}")
        linhas.append("-" * 55)

        # --- lista detalhada de consumo e custo ---
        for it in itens:

            linha = (
                f"{it['tipo']:3} | "
                f"{it['nome'][:28]:28} | "
                f"{it['consumo']:8.3f} {it['unidade']:>4} | "
                f"R$ {it['custo']:8.2f}"
            )

            linhas.append(linha)

            # separa total MP x EMB
            if it["tipo"] == "MP":
                total_mp += it["custo"]
            else:
                total_emb += it["custo"]

        # --- totais finais ---
        linhas.append("-" * 55)
        linhas.append(f"TOTAL MP  : R$ {total_mp:.2f}")
        linhas.append(f"TOTAL EMB : R$ {total_emb:.2f}")
        linhas.append(f"TOTAL GERAL: R$ {total:.2f}")

        # --- imprime no painel ---
        self.out.setText("\n".join(linhas))


# ----------------------------------------------------
# Boot da aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TelaCalculo()
    w.show()
    app.exec()
