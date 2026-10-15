import pandas as pd
import sqlite3
import re

ARQ = "documentos/Valoração Custo Médio 2.xlsx"

df = pd.read_excel(ARQ, header=None)

conn = sqlite3.connect("btj.db")
cur = conn.cursor()

regex_codigo = re.compile(r"^\d+\.\d+")
regex_peso = re.compile(r"(\d+)\s*KG", re.IGNORECASE)

derivacao_atual_id = None
derivacao_atual_nome = None

for _, row in df.iterrows():

    c0 = str(row[0]).strip() if pd.notna(row[0]) else ""
    c1 = str(row[1]).strip() if pd.notna(row[1]) else ""
    c2 = str(row[2]).strip() if pd.notna(row[2]) else ""
    c3 = row[3] if len(row) > 3 else None

    # -------------------------------------------------
    # Detecta início de nova derivação
    # -------------------------------------------------
    if c0 and not regex_codigo.match(c0):

        derivacao_atual_nome = c0

        # Extrai peso base automaticamente do nome
        peso_match = regex_peso.search(c0)
        peso_base = float(peso_match.group(1)) if peso_match else 0

        # Insere derivação
        cur.execute("""
            INSERT INTO derivacoes_produto
            (codigo_derivacao, descricao, peso_base, tipo)
            VALUES (?, ?, ?, ?)
        """, (None, c0, peso_base, None))

        derivacao_atual_id = cur.lastrowid
        continue

    # -------------------------------------------------
    # Detecta item da receita
    # -------------------------------------------------
    if regex_codigo.match(c0) and derivacao_atual_id:

        codigo = c0

        # Converter quantidade
        qtd_txt = str(c3).replace(",", ".")
        try:
            qtd = float(qtd_txt)
        except:
            continue

        unidade = c2
        tipo = "MP" if unidade.lower() == "kg" else "EMB"

        # Buscar insumo_id
        cur.execute("""
            SELECT id FROM insumos
            WHERE codigo = ?
        """, (codigo,))
        ins = cur.fetchone()

        if not ins:
            continue

        insumo_id = ins[0]

        # Inserir item na receita
        cur.execute("""
            INSERT INTO receita_derivacao
            (derivacao_id, insumo_id, quantidade, unidade, tipo_item)
            VALUES (?, ?, ?, ?, ?)
        """, (derivacao_atual_id, insumo_id, qtd, unidade, tipo))

conn.commit()
conn.close()

print("Importação concluída.")
