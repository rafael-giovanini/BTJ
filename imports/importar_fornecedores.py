"""
Módulo: importar_fornecedores.py

Responsabilidade:
    Importar fornecedores a partir de planilha Excel.

Planilha mínima esperada:
    - Nome
"""

import pandas as pd
from datetime import datetime
from core.database import conectar


def importar_fornecedores(caminho_arquivo: str) -> dict:

    df = pd.read_excel(caminho_arquivo)

    if "Nome" not in df.columns:
        raise ValueError("A planilha deve conter a coluna 'Nome'.")

    conn = conectar()
    cur = conn.cursor()

    inseridos = 0
    duplicados = 0

    for _, row in df.iterrows():

        nome = str(row["Nome"]).strip()

        if not nome:
            continue

        cur.execute(
            "SELECT id FROM fornecedores WHERE nome = ?",
            (nome,)
        )

        if cur.fetchone():
            duplicados += 1
            continue

        cur.execute("""
            INSERT INTO fornecedores (nome, ativo)
            VALUES (?, 1)
        """, (nome,))

        inseridos += 1

    # Salvar histórico
    cur.execute("""
        INSERT INTO historico_importacoes
        (tipo_importacao, arquivo, data_execucao,
         registros_importados, itens_criados, duplicados)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "FORNECEDORES",
        caminho_arquivo,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        inseridos,
        0,
        duplicados
    ))

    conn.commit()
    conn.close()

    return {
        "importados": inseridos,
        "duplicados": duplicados
    }