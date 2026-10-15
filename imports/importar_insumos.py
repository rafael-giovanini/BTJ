"""
Módulo: importar_insumos.py

Responsabilidade:
    Importar insumos para o modelo relacional definitivo.

Contrato:
    importar_insumos(caminho_arquivo: str) -> int
"""

import pandas as pd
from core.database import conectar


def importar_insumos(caminho_arquivo: str) -> int:

    # 🔒 FORÇA código como string (evita float)
    df = pd.read_excel(
        caminho_arquivo,
        dtype={"CÓDIGOS": str}
    )

    colunas_necessarias = [
        "CÓDIGOS",
        "INSUMOS NAS ESTRUTURAS",
        "unidade de estoque",
        "vlr unit pela unidade de estoque"
    ]

    df = df[colunas_necessarias]

    # Normalização
    df["CÓDIGOS"] = df["CÓDIGOS"].str.strip()

    df = df.dropna(subset=["CÓDIGOS"])
    df = df[df["vlr unit pela unidade de estoque"].notna()]

    conn = conectar()
    cur = conn.cursor()

    inseridos = 0

    for _, row in df.iterrows():

        codigo = row["CÓDIGOS"]
        nome = str(row["INSUMOS NAS ESTRUTURAS"]).strip()
        unidade = str(row["unidade de estoque"]).strip()
        custo = float(row["vlr unit pela unidade de estoque"])

        if not codigo:
            continue

        cur.execute(
            "SELECT id FROM insumos WHERE codigo = ?",
            (codigo,)
        )

        existente = cur.fetchone()

        if existente:
            cur.execute("""
                UPDATE insumos
                SET nome = ?, unidade_base = ?, custo_unitario = ?, ativo = 1
                WHERE codigo = ?
            """, (nome, unidade, custo, codigo))
        else:
            cur.execute("""
                INSERT INTO insumos
                (codigo, nome, unidade_base, custo_unitario, ativo)
                VALUES (?, ?, ?, ?, 1)
            """, (codigo, nome, unidade, custo))

        inseridos += 1

    conn.commit()
    conn.close()

    return inseridos