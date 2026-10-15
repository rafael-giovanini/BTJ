"""
Responsabilidade:
    Calcular saldo atual de insumos.
"""

from core.database import conectar


def calcular_saldo_insumo(insumo_id: int) -> float:
    """
    Saldo = entradas - consumo nas receitas
    """

    conn = conectar()
    cur = conn.cursor()

    # Total entrada
    cur.execute("""
        SELECT SUM(quantidade)
        FROM entrada_insumos
        WHERE insumo_id = ?
    """, (insumo_id,))

    entrada = cur.fetchone()[0] or 0

    # Total consumo estimado (base receita)
    cur.execute("""
        SELECT SUM(r.quantidade)
        FROM receita_derivacao r
        WHERE r.insumo_id = ?
    """, (insumo_id,))

    consumo = cur.fetchone()[0] or 0

    conn.close()

    return entrada - consumo