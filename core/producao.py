from core.database import conectar
from core.calculations import calcular_custo_derivacao


def registrar_producao(derivacao_id: int, kg_produzido: float, data: str):

    resultado = calcular_custo_derivacao(derivacao_id, kg_produzido)

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO producao
        (derivacao_id, data_producao, kg_produzido, custo_total)
        VALUES (?, ?, ?, ?)
    """, (
        derivacao_id,
        data,
        kg_produzido,
        resultado["custo_total"]
    ))

    conn.commit()
    conn.close()

    return resultado