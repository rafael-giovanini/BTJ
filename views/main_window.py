"""
Módulo: main_window.py

Camada:
    views

Responsabilidade:
    Tela principal (hub) do sistema BTJ.

Modelo:
    Arquitetura unificada com tabela 'itens'.
"""
from core.config import APP_NAME, APP_VERSION
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton,
    QStackedWidget, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

import os
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QFont

# -------------------------------------------------
# 🔹 Import das telas
# -------------------------------------------------
from views.ui_dashboard import DashboardView
from views.ui_itens import ItensView
from views.ui_derivacoes import DerivacoesView
from views.ui_receitas import ReceitasView
from views.ui_entrada_insumos import EntradaInsumosView
from views.ui_importacoes import ImportacoesView
from views.ui_historico_importacoes import HistoricoImportacoesView


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BTJ - Sistema Industrial Completo")
        self.setMinimumSize(1300, 750)

        self.init_ui()
        self.showMaximized()

    # -------------------------------------------------
    # 🔹 Montagem da interface
    # -------------------------------------------------
    def init_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_principal = QHBoxLayout()
        central_widget.setLayout(layout_principal)

        # -------------------------------------------------
        # 🟦 MENU LATERAL
        # -------------------------------------------------
        menu_layout = QVBoxLayout()

        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_itens = QPushButton("Itens")
        self.btn_derivacoes = QPushButton("Derivações")
        self.btn_receitas = QPushButton("Receitas")
        self.btn_entradas = QPushButton("Entradas")
        self.btn_importar = QPushButton("Importar")
        self.btn_historico = QPushButton("Histórico")
        self.btn_sair = QPushButton("Sair")

        botoes = [
            self.btn_dashboard,
            self.btn_itens,
            self.btn_derivacoes,
            self.btn_receitas,
            self.btn_entradas,
            self.btn_importar,
            self.btn_historico,
            self.btn_sair
        ]

        for btn in botoes:
            btn.setMinimumHeight(45)
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()

        # -------------------------------------------------
        # 🟦 RODAPÉ CORPORATIVO
        # -------------------------------------------------
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "sicap_logo_icon.svg")

        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(2)

        # 🔹 Logo
        self.logo = QSvgWidget(logo_path)
        self.logo.setFixedSize(300, 300)

        # Opacidade correta (Qt way)
        self.logo_opacity = QGraphicsOpacityEffect()
        self.logo_opacity.setOpacity(0.6)
        self.logo.setGraphicsEffect(self.logo_opacity)

        # Animação hover
        self.logo_anim = QPropertyAnimation(self.logo_opacity, b"opacity")
        self.logo_anim.setDuration(200)
        self.logo_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.logo.enterEvent = self._logo_hover_enter
        self.logo.leaveEvent = self._logo_hover_leave

        # 🔹 Nome do sistema (via config)
        lbl_nome = QLabel(APP_NAME)
        lbl_nome.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 🔹 Versão automática
        lbl_versao = QLabel(f"v{APP_VERSION}")
        lbl_versao.setFont(QFont("Segoe UI", 8))
        lbl_versao.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 🔹 Ano automático
        ano_atual = datetime.now().year
        lbl_copy = QLabel(f"© {ano_atual}")
        lbl_copy.setFont(QFont("Segoe UI", 7))
        lbl_copy.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(lbl_nome)
        footer_layout.addWidget(lbl_versao)
        footer_layout.addWidget(lbl_copy)

        menu_layout.addLayout(footer_layout)

        # -------------------------------------------------
        # 🟦 STACK CENTRAL
        # -------------------------------------------------
        self.stack = QStackedWidget()

        # Instanciar telas
        self.tela_dashboard = DashboardView()
        self.tela_itens = ItensView()
        self.tela_derivacoes = DerivacoesView()
        self.tela_receitas = ReceitasView()
        self.tela_entradas = EntradaInsumosView()
        self.tela_importacoes = ImportacoesView()
        self.tela_historico = HistoricoImportacoesView()

        # Adicionar ao stack
        self.stack.addWidget(self.tela_dashboard)
        self.stack.addWidget(self.tela_itens)
        self.stack.addWidget(self.tela_derivacoes)
        self.stack.addWidget(self.tela_receitas)
        self.stack.addWidget(self.tela_entradas)
        self.stack.addWidget(self.tela_importacoes)
        self.stack.addWidget(self.tela_historico)

        # Layout final
        layout_principal.addLayout(menu_layout, 1)
        layout_principal.addWidget(self.stack, 4)

        # Tela inicial
        self.stack.setCurrentWidget(self.tela_dashboard)

        # Conectar botões
        self._conectar_botoes()

    # -------------------------------------------------
    # 🔹 Conexão dos botões
    # -------------------------------------------------
    def _conectar_botoes(self):

        mapa = {
            self.btn_dashboard: self.tela_dashboard,
            self.btn_itens: self.tela_itens,
            self.btn_derivacoes: self.tela_derivacoes,
            self.btn_receitas: self.tela_receitas,
            self.btn_entradas: self.tela_entradas,
            self.btn_historico: self.tela_historico,
            self.btn_importar: self.tela_importacoes
        }

        for botao, tela in mapa.items():
            botao.clicked.connect(
                lambda _, t=tela: self._trocar_tela(t)
            )

        self.btn_sair.clicked.connect(self.close)

    # -------------------------------------------------
    # 🔄 Troca de tela com atualização automática
    # -------------------------------------------------
    def _trocar_tela(self, tela):

        # Atualiza automaticamente se existir método atualizar()
        if hasattr(tela, "atualizar"):
            tela.atualizar()

        self.stack.setCurrentWidget(tela)
    
    # -------------------------------------------------
    # ✨ Hover animation do logo
    # -------------------------------------------------
    def _logo_hover_enter(self, event):
        self.logo_anim.stop()
        self.logo_anim.setStartValue(self.logo_opacity.opacity())
        self.logo_anim.setEndValue(1.0)
        self.logo_anim.start()

    def _logo_hover_leave(self, event):
        self.logo_anim.stop()
        self.logo_anim.setStartValue(self.logo_opacity.opacity())
        self.logo_anim.setEndValue(0.6)
        self.logo_anim.start()