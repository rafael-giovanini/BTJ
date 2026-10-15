"""
Módulo: importar_entrada_itens.py

Responsabilidade:
    Importador industrial definitivo de entradas fiscais.

Modelo:
    - Usa tabela 'itens'
    - Usa tabela 'entrada_itens'
    - Cria item automaticamente se não existir
    - Cria fornecedor automaticamente
    - Bloqueia duplicidade (item + NF)
    - Atualiza custo médio automaticamente
"""

import pandas as pd
from core.database import conectar
from core.calculations import atualizar_custo_medio_item


def importar_entrada_itens(caminho_arquivo: str) -> dict:

    df = pd.read_excel(caminho_arquivo)

    colunas_utilizadas = [
        "Cli/For",
        "Nº Inicial NF",
        "Produto",
        "Qtd.",
        "Preço Uni.",
        "Vlr. Mercadoria",
        "Data Geração"
    ]

    df = df[colunas_utilizadas]
    df = df.dropna(subset=["Produto", "Qtd.", "Preço Uni."])

    conn = conectar()
    cur = conn.cursor()

    total_importado = 0
    itens_criados = 0
    duplicados = 0

    for _, row in df.iterrows():

        fornecedor_nome = str(row["Cli/For"]).strip()
        numero_nf = str(row["Nº Inicial NF"]).strip()
        codigo = str(row["Produto"]).strip().replace(".0", "")

        quantidade = float(row["Qtd."])
        valor_unitario = float(row["Preço Uni."])
        valor_total = float(row["Vlr. Mercadoria"])
        data = str(row["Data Geração"])

        if not codigo:
            continue

        # -------------------------------------------------
        # 1️⃣ Criar ou localizar ITEM
        # -------------------------------------------------
        cur.execute(
            "SELECT id FROM itens WHERE codigo = ?",
            (codigo,)
        )
        item = cur.fetchone()

        if item:
            item_id = item[0]
        else:
            cur.execute("""
                INSERT INTO itens
                (codigo,
                descricao,
                familia,
                unidade_base,
                tipo_item,
                subtipo,
                descricao_subtipo,
                descricao_tipo,
                custo_unitario,
                ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                codigo,
                f"ITEM {codigo}",
                "GERAL",                 # familia padrão
                "KG",                    # unidade_base padrão
                "INSUMO",                # tipo_item
                "ENTRADA",               # subtipo
                "IMPORTACAO NF",         # descricao_subtipo
                "INSUMO",                # descricao_tipo
                valor_unitario,
                1
            ))
            item_id = cur.lastrowid
            itens_criados += 1

        # -------------------------------------------------
        # 2️⃣ Criar ou localizar fornecedor
        # -------------------------------------------------
        cur.execute(
            "SELECT id FROM fornecedores WHERE nome = ?",
            (fornecedor_nome,)
        )
        fornecedor = cur.fetchone()

        if fornecedor:
            fornecedor_id = fornecedor[0]
        else:
            cur.execute("""
                INSERT INTO fornecedores (nome, ativo)
                VALUES (?, 1)
            """, (fornecedor_nome,))
            fornecedor_id = cur.lastrowid

        # -------------------------------------------------
        # 3️⃣ Bloqueio de duplicidade
        # -------------------------------------------------
        cur.execute("""
            SELECT id
            FROM entrada_itens
            WHERE item_id = ?
            AND numero_nf = ?
        """, (item_id, numero_nf))

        if cur.fetchone():
            duplicados += 1
            continue

        # -------------------------------------------------
        # 4️⃣ Inserir entrada
        # -------------------------------------------------
        cur.execute("""
            INSERT INTO entrada_itens
            (item_id, fornecedor_id, data_entrada,
             numero_nf, quantidade, valor_unitario, valor_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            fornecedor_id,
            data,
            numero_nf,
            quantidade,
            valor_unitario,
            valor_total
        ))

        total_importado += 1

        # -------------------------------------------------
        # 5️⃣ Atualizar custo médio
        # -------------------------------------------------
        atualizar_custo_medio_item(item_id)

        from datetime import datetime

        cur.execute("""
        INSERT INTO historico_importacoes
        (tipo_importacao, arquivo, data_execucao,
        registros_importados, itens_criados, duplicados)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "ENTRADA_ITENS",
            caminho_arquivo,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_importado,
            itens_criados,
            duplicados
        ))

    conn.commit()
    conn.close()

    return {
        "importados": total_importado,
        "itens_criados": itens_criados,
        "duplicados": duplicados
    }