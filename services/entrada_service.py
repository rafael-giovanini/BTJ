"""
Módulo: entrada_service.py

Camada:
    services

Responsabilidade:
    Registrar entradas de itens com:
        - Atualização de estoque
        - Cálculo automático de custo médio ponderado
        - Persistência na tabela entrada_itens

Regra de negócio:
    O custo médio é recalculado a cada entrada:
        novo_custo =
        ((estoque_atual × custo_atual) + (quantidade × valor_unitario))
        /
        (estoque_atual + quantidade)

Tipos de item (P, C, D):
    Todos controlam estoque e custo médio.
"""

from core.database import conectar


def registrar_entrada(
    item_id: int,
    quantidade: float,
    valor_unitario: float,
    numero_nf: str = None
) -> None:

    if quantidade <= 0:
        raise ValueError("Quantidade deve ser maior que zero.")

    if valor_unitario < 0:
        raise ValueError("Valor unitário não pode ser negativo.")

    conn = conectar()
    cur = conn.cursor()

    valor_total = quantidade * valor_unitario

    # Buscar dados atuais do item
    cur.execute("""
        SELECT estoque_atual, custo_unitario
        FROM itens
        WHERE id = ?
    """, (item_id,))

    resultado = cur.fetchone()

    if not resultado:
        conn.close()
        raise ValueError("Item não encontrado.")

    estoque_atual, custo_atual = resultado

    estoque_atual = estoque_atual or 0
    custo_atual = custo_atual or 0

    novo_estoque = estoque_atual + quantidade

    # Cálculo do custo médio ponderado
    if novo_estoque == 0:
        novo_custo = 0
    else:
        novo_custo = (
            (estoque_atual * custo_atual) +
            (quantidade * valor_unitario)
        ) / novo_estoque

    # Registrar movimentação
    cur.execute("""
        INSERT INTO entrada_itens
        (item_id, data_entrada, numero_nf, quantidade, valor_unitario, valor_total)
        VALUES (?, DATE('now'), ?, ?, ?, ?)
    """, (
        item_id,
        numero_nf,
        quantidade,
        valor_unitario,
        valor_total
    ))

    # Atualizar estoque e custo médio
    cur.execute("""
        UPDATE itens
        SET estoque_atual = ?,
            custo_unitario = ?
        WHERE id = ?
    """, (
        novo_estoque,
        novo_custo,
        item_id
    ))

    conn.commit()
    conn.close()