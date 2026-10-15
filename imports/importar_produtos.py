"""
Módulo: importar_produtos.py

Responsabilidade:
    Importar produtos a partir da planilha ERP oficial.

Colunas utilizadas:
    Produto
    Descrição
    Família
    UM
    Tipo
    Origem
    Descr. (Origem)
    Descr. (Tipo)

Modelo Industrial:
    - Tipo define natureza contábil
    - Origem define subclassificação
"""

import pandas as pd
from datetime import datetime
from core.database import conectar


def importar_produtos(caminho_arquivo: str) -> int:

    df = pd.read_excel(caminho_arquivo)

    colunas_necessarias = [
        "Produto",
        "Descrição",
        "Família",
        "UM",
        "Tipo",
        "Origem",
        "Descr. (Origem)",
        "Descr. (Tipo)"
    ]

    # Validação estrutural
    for col in colunas_necessarias:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória não encontrada: {col}")

    df = df[colunas_necessarias]
    df = df.dropna(subset=["Produto"])

    conn = conectar()
    cur = conn.cursor()

    inseridos = 0
    duplicados = 0

    for _, row in df.iterrows():

        codigo = str(row["Produto"]).strip()
        descricao = str(row["Descrição"]).strip()
        familia = str(row["Família"]).strip() if pd.notna(row["Família"]) else None
        unidade = str(row["UM"]).strip() if pd.notna(row["UM"]) else "UN"
        tipo = str(row["Tipo"]).strip().upper()
        subtipo = str(row["Origem"]).strip().upper()
        desc_origem = str(row["Descr. (Origem)"]).strip()
        desc_tipo = str(row["Descr. (Tipo)"]).strip()

        if not codigo:
            continue

        if tipo not in ("P", "C", "D"):
            continue

        cur.execute(
            "SELECT id FROM itens WHERE codigo = ?",
            (codigo,)
        )

        if cur.fetchone():
            duplicados += 1
            continue

        cur.execute("""
            INSERT INTO itens
            (codigo, descricao, familia,
             unidade_base, tipo_item,
             subtipo, descricao_subtipo,
             descricao_tipo, custo_unitario, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
        """, (
            codigo,
            descricao,
            familia,
            unidade,
            tipo,
            subtipo,
            desc_origem,
            desc_tipo
        ))

        inseridos += 1

    # Histórico
    cur.execute("""
        INSERT INTO historico_importacoes
        (tipo_importacao, arquivo, data_execucao,
         registros_importados, itens_criados, duplicados)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "PRODUTOS",
        caminho_arquivo,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        inseridos,
        0,
        duplicados
    ))

    conn.commit()
    conn.close()

    return inseridos