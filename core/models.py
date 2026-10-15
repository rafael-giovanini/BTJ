def caixas_equivalentes(kg_vendidos, kg_por_caixa):
    return kg_vendidos / kg_por_caixa


def custo_materia_prima(custo_kg_peixe, rendimento):
    # custo real do kg de filé
    return custo_kg_peixe / rendimento


def consumo_insumo(caixas, qtd_por_caixa):
    return caixas * qtd_por_caixa
