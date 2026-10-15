from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QMessageBox,
    QTextEdit, QProgressBar
)

from imports.importar_entrada_itens import importar_entrada_itens
from imports.importar_produtos import importar_produtos
from imports.importar_fornecedores import importar_fornecedores


class ImportacoesView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.btn_produtos = QPushButton("Importar Produtos")
        self.btn_produtos.clicked.connect(self.importar_produtos)
        layout.addWidget(self.btn_produtos)

        self.btn_entradas = QPushButton("Importar Entradas")
        self.btn_entradas.clicked.connect(self.importar_entradas)
        layout.addWidget(self.btn_entradas)

        self.btn_fornecedores = QPushButton("Importar Fornecedores")
        self.btn_fornecedores.clicked.connect(self.importar_fornecedores)
        layout.addWidget(self.btn_fornecedores)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        layout.addStretch()
        self.setLayout(layout)

    # -------------------------------------------------
    # 🔹 Importar Produtos
    # -------------------------------------------------
    def importar_produtos(self):

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar planilha de Produtos",
            "",
            "Arquivos Excel (*.xlsx *.xls)"
        )

        if not arquivo:
            return

        self.progress.setValue(30)
        total = importar_produtos(arquivo)
        self.progress.setValue(100)

        self.log.append(f"✔ Produtos importados: {total}")

        QMessageBox.information(
            self,
            "Importação concluída",
            f"{total} produtos importados."
        )

        self.progress.setValue(0)

    # -------------------------------------------------
    # 🔹 Importar Entradas
    # -------------------------------------------------
    def importar_entradas(self):

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar planilha de Entradas",
            "",
            "Arquivos Excel (*.xlsx *.xls)"
        )

        if not arquivo:
            return

        self.progress.setValue(20)

        resultado = importar_entrada_itens(arquivo)

        self.progress.setValue(100)

        self.log.append("✔ Importação de Entradas Finalizada")
        self.log.append(f"   Importados: {resultado['importados']}")
        self.log.append(f"   Itens Criados: {resultado['itens_criados']}")
        self.log.append(f"   Duplicados: {resultado['duplicados']}")
        self.log.append("---------------------------------------------------")

        QMessageBox.information(
            self,
            "Importação concluída",
            "Entradas importadas com sucesso."
        )

        self.progress.setValue(0)

    # -------------------------------------------------
    # 🔹 Importar Fornecedores
    # -------------------------------------------------
    def importar_fornecedores(self):

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar planilha de Fornecedores",
            "",
            "Arquivos Excel (*.xlsx *.xls)"
        )

        if not arquivo:
            return

        resultado = importar_fornecedores(arquivo)

        self.log.append("✔ Importação de Fornecedores Finalizada")
        self.log.append(f"   Importados: {resultado['importados']}")
        self.log.append(f"   Duplicados: {resultado['duplicados']}")
        self.log.append("---------------------------------------------------")

        QMessageBox.information(
            self,
            "Importação concluída",
            "Fornecedores importados com sucesso."
        )

        self.progress.setValue(0)