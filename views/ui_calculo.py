"""
Módulo: ui_calculo.py

Camada:
    views

Responsabilidade:
    Tela de cálculo industrial de custo por derivação.

Fluxo:
    1. Usuário seleciona derivação
    2. Informa kg produzido
    3. Sistema executa cálculo industrial
    4. Resultado é exibido formatado
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

from core.database import conectar
from core.calculations import calcular_custo_derivacao


class CalculoView(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cálculo Industrial - BTJ")

        self.layout = QVBoxLayout()

        # -------------------------------------------------
        # Seleção de derivação
        # -------------------------------------------------
        self.label_derivacao = QLabel("Derivação:")
        self.combo_derivacao = QComboBox()

        self.carregar_derivacoes()

        # -------------------------------------------------
        # Kg produzido
        # -------------------------------------------------
        self.label_kg = QLabel("Kg produzido:")
        self.input_kg = QLineEdit()
        self.input_kg.setPlaceholderText("Ex: 500")

        # -------------------------------------------------
        # Botão calcular
        # -------------------------------------------------
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.clicked.connect(self.executar_calculo)

        # -------------------------------------------------
        # Área de resultado
        # -------------------------------------------------
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)

        # -------------------------------------------------
        # Montagem layout
        # -------------------------------------------------
        self.layout.addWidget(self.label_derivacao)
        self.layout.addWidget(self.combo_derivacao)

        self.layout.addWidget(self.label_kg)
        self.layout.addWidget(self.input_kg)

        self.layout.addWidget(self.btn_calcular)
        self.layout.addWidget(self.resultado)

        self.setLayout(self.layout)

    # -------------------------------------------------
    # Carrega derivacoes no ComboBox
    # -------------------------------------------------
    def carregar_derivacoes(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, codigo_emb
            FROM derivacoes
            WHERE ativo = 1
            ORDER BY codigo_emb
        """)

        derivacoes = cur.fetchall()
        conn.close()

        for derivacao_id, codigo in derivacoes:
            self.combo_derivacao.addItem(codigo, derivacao_id)

    # -------------------------------------------------
    # Executa cálculo
    # -------------------------------------------------
    def executar_calculo(self):

        try:
            derivacao_id = self.combo_derivacao.currentData()
            kg_produzido = float(self.input_kg.text())

            if kg_produzido <= 0:
                raise ValueError("Kg produzido deve ser maior que zero.")

            resultado = calcular_custo_derivacao(
                derivacao_id,
                kg_produzido
            )

            self.mostrar_resultado(resultado)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro no cálculo",
                str(e)
            )

    # -------------------------------------------------
    # Formata resultado na tela
    # -------------------------------------------------
    def mostrar_resultado(self, dados: dict):

        texto = f"""
======= RESULTADO =======

Preço Peixe Vivo: R$ {dados['preco_peixe_vivo']:.2f}
Rendimento: {dados['rendimento'] * 100:.2f} %

Fator de escala: {dados['fator']:.2f}

Custo MP: R$ {dados['custo_mp']:.2f}
Custo EMB: R$ {dados['custo_emb']:.2f}

--------------------------
CUSTO TOTAL: R$ {dados['custo_total']:.2f}
CUSTO POR KG: R$ {dados['custo_por_kg']:.4f}
"""

        self.resultado.setText(texto)