"""
Módulo: importar_receitas

Responsabilidade:
Importar estrutura de produtos, derivações e receitas
a partir da planilha de Valoração de Custo Médio.

Regra de funcionamento:
- Detecta produtos comerciais (PAC)
- Detecta produtos diretos (ex: 10 KG)
- Detecta derivações EMB
- Detecta itens da receita (MP ou EMB)
- Define peso_base automaticamente
- Insere registros respeitando integridade relacional

Retorno:
Quantidade de itens inseridos na tabela receita_derivacao
"""

import pandas as pd
import re
from core.database import conectar


def importar_receitas(caminho_arquivo: str) -> int:
    """
    Executa importação da planilha informada.

    Parâmetros:
        caminho_arquivo (str): Caminho completo do arquivo Excel.

    Retorna:
        int: Total de registros inseridos em receita_derivacao.
    """

    # -------------------------------------------------
    # Leitura da planilha sem cabeçalho
    # -------------------------------------------------
    df = pd.read_excel(caminho_arquivo, header=None)

    # -------------------------------------------------
    # Conexão com banco via camada core
    # -------------------------------------------------
    conn = conectar()
    cur = conn.cursor()

    # Controle de contexto da importação
    produto_id = None          # Produto atual identificado
    derivacao_id = None        # Derivação atual identificada
    esperando_peso = False     # Flag para definir peso_base
    inseridos = 0              # Contador de itens inseridos

    # -------------------------------------------------
    # Expressões regulares de identificação estrutural
    # -------------------------------------------------
    regex_pac = re.compile(r"^PAC\d+")                  # Produto comercial
    regex_emb = re.compile(r"^EMB\d+")                  # Derivação
    regex_codigo = re.compile(r"^\d+\.\d+|^FLR\d+")     # Código de insumo
    regex_produto_direto = re.compile(r".*\d+\s*KG", re.IGNORECASE)

    # =================================================
    # Loop principal linha a linha
    # =================================================
    for _, row in df.iterrows():

        # Extração segura das colunas
        c0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        c2 = str(row[2]).strip() if len(row) > 2 and pd.notna(row[2]) else ""
        c3 = row[3] if len(row) > 3 else None

        # -------------------------------------------------
        # 1️⃣ Identificação de Produto Comercial (PAC)
        # -------------------------------------------------
        if regex_pac.match(c0):

            # Insere produto se ainda não existir
            cur.execute("""
                INSERT OR IGNORE INTO produtos (codigo, descricao)
                VALUES (?, ?)
            """, (c0, c0))

            # Recupera ID do produto
            cur.execute("SELECT id FROM produtos WHERE codigo = ?", (c0,))
            resultado = cur.fetchone()
            if not resultado:
                continue

            produto_id = resultado[0]
            derivacao_id = None
            continue

        # -------------------------------------------------
        # 2️⃣ Produto direto (ex: FILE 10 KG)
        # -------------------------------------------------
        if (
            regex_produto_direto.match(c0)
            and not regex_pac.match(c0)
            and not regex_emb.match(c0)
            and not regex_codigo.match(c0)
        ):

            # Criação do produto
            cur.execute("""
                INSERT OR IGNORE INTO produtos (codigo, descricao)
                VALUES (?, ?)
            """, (c0, c0))

            cur.execute("SELECT id FROM produtos WHERE codigo = ?", (c0,))
            resultado = cur.fetchone()
            if not resultado:
                continue

            produto_id = resultado[0]

            # Extração automática do peso_base a partir do nome
            peso_match = re.search(r"(\d+)\s*KG", c0, re.IGNORECASE)
            peso_base = float(peso_match.group(1)) if peso_match else 0

            # Verifica se já existe derivação
            cur.execute("""
                SELECT id FROM derivacoes
                WHERE produto_id = ? AND codigo_emb = ?
            """, (produto_id, c0))

            existente = cur.fetchone()

            if existente:
                derivacao_id = existente[0]
            else:
                # Cria derivação automaticamente
                cur.execute("""
                    INSERT INTO derivacoes (produto_id, codigo_emb, peso_base)
                    VALUES (?, ?, ?)
                """, (produto_id, c0, peso_base))

                derivacao_id = cur.lastrowid

            esperando_peso = False
            continue

        # -------------------------------------------------
        # 3️⃣ Derivação EMB
        # -------------------------------------------------
        if regex_emb.match(c0) and produto_id:

            cur.execute("""
                SELECT id FROM derivacoes
                WHERE produto_id = ? AND codigo_emb = ?
            """, (produto_id, c0))

            existente = cur.fetchone()

            if existente:
                derivacao_id = existente[0]
            else:
                cur.execute("""
                    INSERT INTO derivacoes (produto_id, codigo_emb, peso_base)
                    VALUES (?, ?, 0)
                """, (produto_id, c0))

                derivacao_id = cur.lastrowid

            esperando_peso = True
            continue

        # -------------------------------------------------
        # 4️⃣ Itens da Receita (MP ou EMB)
        # -------------------------------------------------
        if regex_codigo.match(c0) and derivacao_id:

            # Conversão segura de quantidade
            try:
                qtd = float(str(c3).replace(",", "."))
            except:
                continue

            unidade = c2.lower()

            # Primeira matéria-prima define peso_base
            if esperando_peso and unidade == "kg":
                cur.execute("""
                    UPDATE derivacoes
                    SET peso_base = ?
                    WHERE id = ?
                """, (qtd, derivacao_id))
                esperando_peso = False

            # Classificação do item
            tipo = "MP" if unidade == "kg" else "EMB"

            # Busca insumo
            cur.execute("SELECT id FROM insumos WHERE codigo = ?", (c0,))
            insumo = cur.fetchone()

            if not insumo:
                continue

            insumo_id = insumo[0]

            # Inserção do item na receita
            try:
                cur.execute("""
                    INSERT INTO receita_derivacao
                    (derivacao_id, insumo_id, quantidade, unidade, tipo_item)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    derivacao_id,
                    insumo_id,
                    qtd,
                    unidade,
                    tipo
                ))

                inseridos += 1

            except:
                pass

    # -------------------------------------------------
    # Finalização transacional
    # -------------------------------------------------
    conn.commit()
    conn.close()

    return inseridos