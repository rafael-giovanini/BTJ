"""
Responsabilidade:
    Gerar relatório mensal de custo médio.
"""

from core.database import conectar


def custo_medio_mensal(insumo_id: int, ano: int, mes: int):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT SUM(valor_total), SUM(quantidade)
        FROM entrada_insumos
        WHERE insumo_id = ?
        AND strftime('%Y', data_entrada) = ?
        AND strftime('%m', data_entrada) = ?
    """, (insumo_id, str(ano), f"{mes:02d}"))

    total_valor, total_qtd = cur.fetchone()

    conn.close()

    if total_qtd and total_qtd > 0:
        return total_valor / total_qtd

    return 0