"""
Arquivo principal do sistema SICAP.
Responsável por iniciar a aplicação,
carregar estilo global, exibir splash
e garantir estrutura do banco.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.database import criar_tabelas
from views.main_window import MainWindow
from views.splash_screen import SplashScreen


def carregar_estilo(app):
    """
    Carrega o stylesheet global (QSS).
    Usa caminho absoluto para evitar erro em execução externa.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base_dir, "assets", "style.qss")

    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"⚠ style.qss não encontrado em: {caminho}")


def iniciar_sistema(app, splash):
    """
    Executa etapas de inicialização sem travar a UI.
    """

    # Etapa 1
    splash.update_progress(30, "Conectando ao banco de dados...")
    criar_tabelas()

    # Etapa 2
    splash.update_progress(60, "Carregando módulos industriais...")

    # Etapa 3
    splash.update_progress(90, "Inicializando interface...")

    # Finalização
    splash.update_progress(100, "Finalizando...")

    # Abrir janela principal após pequeno delay
    QTimer.singleShot(400, lambda: abrir_main(app, splash))


def abrir_main(app, splash):
    window = MainWindow()
    window.show()
    splash.close()


def main():

    app = QApplication(sys.argv)

    carregar_estilo(app)

    splash = SplashScreen()
    splash.show()

    # Executa inicialização após exibir splash
    QTimer.singleShot(300, lambda: iniciar_sistema(app, splash))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()