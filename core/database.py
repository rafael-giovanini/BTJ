"""
Módulo: database.py

Camada:
    core

Responsabilidade:
    Gerenciar conexão e estrutura do banco BTJ
    (Modelo Industrial Unificado).

Modelo Conceitual:

    🔹 Tabela principal: ITENS
        - Centraliza produtos, insumos e despesas
        - Classificação por tipo e subtipo

    🔹 Entrada de Itens
        - Controla histórico de compras
        - Base para cálculo de custo médio

    🔹 Derivações
        - Produtos produzidos a partir de item base

    🔹 Receita (BOM)
        - Estrutura industrial da derivação

    🔹 Histórico
        - Rastreabilidade de importações

Observação:
    O banco é criado automaticamente na pasta /database.
"""

import sqlite3
import os


# -------------------------------------------------
# 📁 Caminho absoluto do banco (padrão do projeto)
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "btj.db")


# -------------------------------------------------
# 🔹 Conexão
# -------------------------------------------------

def conectar():
    """
    Retorna conexão SQLite utilizando
    caminho absoluto do projeto.
    """
    return sqlite3.connect(DB_PATH)


# -------------------------------------------------
# 🔹 Criação das tabelas
# -------------------------------------------------

def criar_tabelas():
    """
    Cria todas as tabelas estruturais
    do modelo industrial unificado.
    """

    conn = conectar()
    cur = conn.cursor()

    # =================================================
    # 🟦 TABELA PRINCIPAL — ITENS
    # =================================================
    # Centraliza:
    #   P = Produzido
    #   C = Comprado
    #   D = Despesa
    #
    # Subtipo:
    #   PAC, MP, EMB, SERV, etc.
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Código ERP
        codigo TEXT UNIQUE NOT NULL,

        -- Descrição principal
        descricao TEXT NOT NULL,

        -- Família contábil ERP
        familia TEXT,

        -- Unidade base
        unidade_base TEXT,

        -- Tipo principal:
        -- P = Produzido
        -- C = Comprado
        -- D = Despesa
        tipo_item TEXT NOT NULL,

        -- Subtipo técnico (PAC, MP, EMB...)
        subtipo TEXT,

        -- Descrição textual do subtipo
        descricao_subtipo TEXT,

        -- Descrição textual do tipo
        descricao_tipo TEXT,

        -- Custo médio unitário
        custo_unitario REAL DEFAULT 0,

        -- Controle lógico
        ativo INTEGER DEFAULT 1
    )
    """)

    # =================================================
    # 🟦 FORNECEDORES
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        ativo INTEGER DEFAULT 1
    )
    """)

    # =================================================
    # 🟦 ENTRADA DE ITENS (Compras)
    # =================================================
    # Base para cálculo de custo médio ponderado
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS entrada_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        fornecedor_id INTEGER,
        data_entrada TEXT,
        numero_nf TEXT,
        quantidade REAL,
        valor_unitario REAL,
        valor_total REAL,
        FOREIGN KEY(item_id) REFERENCES itens(id),
        FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
    )
    """)

    # =================================================
    # 🟦 DERIVAÇÕES (Industrial)
    # =================================================
    # Apenas para itens tipo P
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS derivacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        codigo_emb TEXT,
        peso_base REAL,
        ativo INTEGER DEFAULT 1,
        FOREIGN KEY(item_id) REFERENCES itens(id)
    )
    """)

    # =================================================
    # 🟦 RECEITA INDUSTRIAL (BOM)
    # =================================================
    # Estrutura técnica da produção
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS receita_derivacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        derivacao_id INTEGER,
        item_id INTEGER,
        quantidade REAL,
        unidade TEXT,
        tipo_item TEXT,
        FOREIGN KEY(derivacao_id) REFERENCES derivacoes(id),
        FOREIGN KEY(item_id) REFERENCES itens(id)
    )
    """)

    # =================================================
    # 🟦 AUDITORIA
    # =================================================
    # Rastreabilidade de alterações
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabela TEXT,
        registro_id INTEGER,
        campo TEXT,
        valor_antigo TEXT,
        valor_novo TEXT,
        data_alteracao TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =================================================
    # 📑 HISTÓRICO DE IMPORTAÇÕES
    # =================================================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS historico_importacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_importacao TEXT,
        arquivo TEXT,
        data_execucao TEXT,
        registros_importados INTEGER,
        itens_criados INTEGER,
        duplicados INTEGER
    )
    """)

    conn.commit()
    conn.close()