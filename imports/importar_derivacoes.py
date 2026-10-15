"""
Módulo: importar_derivacoes.py

Responsabilidade:
    Importar derivações (EMB) para o modelo relacional definitivo.

Contrato:
    importar_derivacoes(caminho_arquivo: str) -> int
"""

import pandas as pd
from core.database import conectar


def importar_derivacoes(caminho_arquivo: str) -> int:

    df = pd.read_excel(caminho_arquivo, header=None)

    conn = conectar()
    cur = conn.cursor()

    total_importado = 0

    for _, row in df.iterrows():

        codigo_emb = str(row[0]).strip()
        descricao = str(row[2]).strip()

        if not codigo_emb or codigo_emb.lower() == "nan":
            continue

        # Aqui você precisa decidir como relacionar com produto.
        # Exemplo simplificado:
        # Se não houver produto_id ainda, criar derivação sem vínculo.

        cur.execute("""
            INSERT INTO derivacoes (produto_id, codigo_emb, peso_base, ativo)
            VALUES (?, ?, ?, 1)
        """, (None, codigo_emb, 0))

        total_importado += 1

    conn.commit()
    conn.close()

    return total_importado