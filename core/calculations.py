"""
Módulo: calculations.py

Camada:
    core

Responsabilidade:
    Executar cálculo industrial de custo por derivação
    e gerenciar atualização de custo médio dos itens.

Modelo Industrial Atual:
    - Tudo está na tabela 'itens'
    - Peixe vivo identificado por origem_erp = 'PXV'
    - MP = unidade em kg
    - EMB = qualquer outra unidade
    - Custo MP base = preco_peixe_vivo / rendimento
"""

from core.database import conectar


# =========================================================
# 🔹 BUSCAS ESTRUTURAIS
# =========================================================

def obter_custo_peixe_vivo(conn) -> float:
    """
    Retorna custo_unitario do item
    com origem_erp = 'PXV'.
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT custo_unitario
        FROM itens
        WHERE origem_erp = 'PXV'
        AND ativo = 1
        LIMIT 1
    """)

    row = cur.fetchone()

    if not row:
        raise ValueError("Peixe vivo (PXV) não cadastrado na tabela itens.")

    return row[0]


def obter_rendimento_derivacao(conn, derivacao_id: int) -> float:
    """
    Retorna rendimento industrial da derivação.
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT percentual
        FROM rendimento
        WHERE derivacao_id = ?
    """, (derivacao_id,))

    row = cur.fetchone()

    if not row:
        raise ValueError("Rendimento não cadastrado para esta derivação.")

    return row[0]


def obter_peso_base(conn, derivacao_id: int) -> float:
    """
    Retorna peso_base da derivação.
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT peso_base
        FROM derivacoes
        WHERE id = ?
    """, (derivacao_id,))

    row = cur.fetchone()

    if not row:
        raise ValueError("Derivação não encontrada.")

    return row[0]


def obter_receita(conn, derivacao_id: int):
    """
    Retorna todos os itens da receita da derivação.
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.quantidade,
            r.unidade,
            r.tipo_item,
            i.custo_unitario
        FROM receita_derivacao r
        JOIN itens i ON r.item_id = i.id
        WHERE r.derivacao_id = ?
    """, (derivacao_id,))

    return cur.fetchall()


# =========================================================
# 🔹 CÁLCULO INDUSTRIAL DE DERIVAÇÃO
# =========================================================

def calcular_custo_derivacao(derivacao_id: int, kg_produzido: float) -> dict:
    """
    Calcula custo industrial da derivação.
    """

    conn = conectar()

    # -------------------------------------------------
    # 1️⃣ Buscar dados estruturais
    # -------------------------------------------------
    peso_base = obter_peso_base(conn, derivacao_id)
    rendimento = obter_rendimento_derivacao(conn, derivacao_id)
    preco_peixe_vivo = obter_custo_peixe_vivo(conn)

    if peso_base == 0:
        conn.close()
        raise ValueError("Peso base da derivação está zerado.")

    # -------------------------------------------------
    # 2️⃣ Regra Industrial
    # -------------------------------------------------
    custo_mp_base = preco_peixe_vivo / rendimento

    # -------------------------------------------------
    # 3️⃣ Fator de escala
    # -------------------------------------------------
    fator = kg_produzido / peso_base

    receita = obter_receita(conn, derivacao_id)

    custo_total = 0
    custo_mp = 0
    custo_emb = 0

    # -------------------------------------------------
    # 4️⃣ Processar itens da receita
    # -------------------------------------------------
    for quantidade, unidade, tipo_item, custo_unitario in receita:

        quantidade_real = quantidade * fator

        if tipo_item == "MP":
            custo_item = quantidade_real * custo_mp_base
            custo_mp += custo_item
        else:
            custo_item = quantidade_real * custo_unitario
            custo_emb += custo_item

        custo_total += custo_item

    conn.close()

    return {
        "custo_total": round(custo_total, 2),
        "custo_mp": round(custo_mp, 2),
        "custo_emb": round(custo_emb, 2),
        "custo_por_kg": round(custo_total / kg_produzido, 4),
        "fator": fator,
        "rendimento": rendimento,
        "preco_peixe_vivo": preco_peixe_vivo
    }


# =========================================================
# 🔹 ATUALIZAÇÃO DE CUSTO MÉDIO (NOVO MODELO)
# =========================================================

def atualizar_custo_medio_item(item_id: int):
    """
    Atualiza custo_unitario do item
    com base no custo médio ponderado das entradas.
    """

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT SUM(valor_total), SUM(quantidade)
        FROM entrada_itens
        WHERE item_id = ?
    """, (item_id,))

    resultado = cur.fetchone()

    if resultado:
        total_valor, total_qtd = resultado

        if total_qtd and total_qtd > 0:
            custo_medio = total_valor / total_qtd

            cur.execute("""
                UPDATE itens
                SET custo_unitario = ?
                WHERE id = ?
            """, (custo_medio, item_id))

    conn.commit()
    conn.close()