from core.database import conectar


def calcular_margem(derivacao_id: int):

    conn = conectar()
    cur = conn.cursor()

    # Custo médio produção
    cur.execute("""
        SELECT SUM(custo_total), SUM(kg_produzido)
        FROM producao
        WHERE derivacao_id = ?
    """, (derivacao_id,))

    total_custo, total_kg = cur.fetchone()

    if not total_kg:
        conn.close()
        return 0

    custo_medio = total_custo / total_kg

    # Preço médio venda
    cur.execute("""
        SELECT SUM(preco_venda_kg * kg_vendido), SUM(kg_vendido)
        FROM vendas
        WHERE derivacao_id = ?
    """, (derivacao_id,))

    total_venda, total_kg_vendido = cur.fetchone()

    conn.close()

    if not total_kg_vendido:
        return 0

    preco_medio = total_venda / total_kg_vendido

    margem = preco_medio - custo_medio

    return margem