"""
Módulo: splash_screen.py
Splash Screen animado do SICAP
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QGraphicsOpacityEffect


class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(700, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #0A2A43;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # ---------------------------
        # 🔷 Logo SVG
        # ---------------------------
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "sicap_logo_white.svg")

        self.logo = QSvgWidget(logo_path)
        self.logo.setFixedSize(400, 150)

        # Efeito de opacidade (fade)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.logo.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # ---------------------------
        # 🔷 Texto Status
        # ---------------------------
        self.status = QLabel("Inicializando sistema...")
        self.status.setFont(QFont("Segoe UI", 12))
        self.status.setStyleSheet("color: white;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------------------
        # 🔷 Barra de progresso
        # ---------------------------
        self.progress = QProgressBar()
        self.progress.setFixedWidth(400)
        self.progress.setValue(0)

        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1C3B57;
                border-radius: 8px;
                height: 16px;
                color: white;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #1CA7EC;
                border-radius: 8px;
            }
        """)

        layout.addWidget(self.logo)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        # ---------------------------
        # 🔷 Animação Fade-in
        # ---------------------------
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(1200)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()

    # ----------------------------------
    # Atualizar progresso externamente
    # ----------------------------------
    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.status.setText(message)