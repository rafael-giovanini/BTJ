"""
Módulo: importar_entrada_planilha.py

Responsabilidade:
    Importar planilha de entradas de itens.

Fluxo:
    - Localiza item pelo código
    - Registra entrada via service (cálculo de custo médio)
    - Atualiza estoque automaticamente

Requisitos da planilha:
    - CÓDIGOS
    - quantidade
    - vlr unit pela unidade de estoque
    - numero_nf (opcional)

Observação:
    Não altera cadastro.
    Apenas gera movimentação.
"""

import pandas as pd
from core.database import conectar
from services.entrada_service import registrar_entrada


def importar_entrada(caminho_arquivo: str) -> int:

    df = pd.read_excel(
        caminho_arquivo,
        dtype={"CÓDIGOS": str}
    )

    df["CÓDIGOS"] = df["CÓDIGOS"].str.strip()

    df = df.dropna(subset=["CÓDIGOS"])

    conn = conectar()
    cur = conn.cursor()

    processados = 0

    for _, row in df.iterrows():

        codigo = row["CÓDIGOS"]
        quantidade = float(row["quantidade"])
        valor_unitario = float(row["vlr unit pela unidade de estoque"])
        numero_nf = str(row.get("numero_nf", "")).strip()

        # Buscar item
        cur.execute(
            "SELECT id FROM itens WHERE codigo = ?",
            (codigo,)
        )

        item = cur.fetchone()

        if not item:
            continue

        item_id = item[0]

        registrar_entrada(
            item_id=item_id,
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            numero_nf=numero_nf
        )

        processados += 1

    conn.close()

    return processados