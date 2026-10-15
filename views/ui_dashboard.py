"""
Módulo: ui_dashboard.py

Camada:
    views

Responsabilidade:
    Exibir indicadores industriais e financeiros do SICAP
    (modelo unificado com tabela 'itens').

Indicadores:
    - Custo Peixe Vivo
    - Total de Itens Comprados (C)
    - Total de Produtos Produzidos (P)
    - Variação mensal de compras
    - Gráfico de compras mensais
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.database import conectar


# -------------------------------------------------
# 🔷 Card KPI Profissional (versão com ObjectName)
# -------------------------------------------------
class KpiCard(QFrame):

    def __init__(self, titulo):
        super().__init__()

        # 🔹 Identificador do Card
        self.setObjectName("kpiCard")

        layout = QVBoxLayout()

        # 🔹 Título
        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("kpiTitulo")

        # 🔹 Valor
        self.lbl_valor = QLabel("0")
        self.lbl_valor.setObjectName("kpiValor")

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_valor)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)

    def atualizar(self, texto):
        self.lbl_valor.setText(texto)

# -------------------------------------------------
# 🔷 Dashboard Principal
# -------------------------------------------------
class DashboardView(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # -------------------------------------------------
        # 🔷 Linha de KPIs
        # -------------------------------------------------
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_peixe = KpiCard("Custo Peixe Vivo")
        self.card_insumos = KpiCard("Itens Comprados (C)")
        self.card_produtos = KpiCard("Produtos Produzidos (P)")
        self.card_variacao = KpiCard("Variação Mensal Compras")

        kpi_layout.addWidget(self.card_peixe)
        kpi_layout.addWidget(self.card_insumos)
        kpi_layout.addWidget(self.card_produtos)
        kpi_layout.addWidget(self.card_variacao)

        # -------------------------------------------------
        # 🔷 Gráfico
        # -------------------------------------------------
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        main_layout.addLayout(kpi_layout)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

        self.atualizar()

    # -------------------------------------------------
    # 🔄 Atualização geral
    # -------------------------------------------------
    def atualizar(self):
        self.atualizar_kpis()
        self.atualizar_grafico()

    # -------------------------------------------------
    # 🔷 Buscar dados mensais
    # -------------------------------------------------
    def buscar_dados(self):

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                strftime('%Y-%m', data_entrada) AS mes,
                SUM(valor_total)
            FROM entrada_itens
            GROUP BY mes
            ORDER BY mes
        """)

        dados = cur.fetchall()
        conn.close()

        return dados

    # -------------------------------------------------
    # 🔷 Atualizar KPIs
    # -------------------------------------------------
    def atualizar_kpis(self):

        conn = conectar()
        cur = conn.cursor()

        # 🔹 Custo Peixe Vivo (subtipo PXV)
        cur.execute("""
            SELECT custo_unitario
            FROM itens
            WHERE subtipo = 'PXV'
            AND ativo = 1
            LIMIT 1
        """)
        peixe = cur.fetchone()
        peixe = peixe[0] if peixe else 0

        # 🔹 Total Itens Comprados (C)
        cur.execute("""
            SELECT COUNT(*)
            FROM itens
            WHERE tipo_item = 'C'
            AND ativo = 1
        """)
        total_insumos = cur.fetchone()[0]

        # 🔹 Total Produtos Produzidos (P)
        cur.execute("""
            SELECT COUNT(*)
            FROM itens
            WHERE tipo_item = 'P'
            AND ativo = 1
        """)
        total_produtos = cur.fetchone()[0]

        # 🔹 Variação mensal
        dados = self.buscar_dados()

        variacao = 0
        if len(dados) >= 2:
            atual = dados[-1][1] or 0
            anterior = dados[-2][1] or 0
            if anterior > 0:
                variacao = ((atual - anterior) / anterior) * 100

        conn.close()

        # Atualiza cards
        self.card_peixe.atualizar(f"R$ {peixe:,.2f}")
        self.card_insumos.atualizar(str(total_insumos))
        self.card_produtos.atualizar(str(total_produtos))
        self.card_variacao.atualizar(f"{variacao:,.2f}%")

    # -------------------------------------------------
    # 📊 Atualizar gráfico
    # -------------------------------------------------
    def atualizar_grafico(self):

        dados = self.buscar_dados()

        meses = [d[0] for d in dados]
        valores = [d[1] or 0 for d in dados]

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # 🎨 Fundo branco
        ax.set_facecolor("white")
        self.figure.patch.set_facecolor("white")

        # 🔷 Linha principal
        ax.plot(
            meses,
            valores,
            linewidth=3,
            color="#0E5E8C",
            marker="o",
            markersize=6
        )

        # 🔷 Área preenchida suave
        ax.fill_between(
            meses,
            valores,
            color="#1CA7EC",
            alpha=0.15
        )

        # 🔷 Grid leve
        ax.grid(
            True,
            linestyle="--",
            linewidth=0.5,
            alpha=0.3
        )

        # 🔷 Remover bordas superiores e direita
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # 🔷 Ajustes de texto
        ax.set_title("Compras Mensais", fontsize=14, fontweight="bold")
        ax.set_ylabel("Valor Total (R$)", fontsize=10)
        ax.set_xlabel("Mês", fontsize=10)

        ax.tick_params(axis="x", rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()