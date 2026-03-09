"""Ponto de entrada do pipeline ETL.

Ordem executada:
1. Extract: busca dados brutos de produtos na API.
2. Transform: limpa produtos e simula vendas.
3. Load: grava dimensões e fatos no banco analítico.
"""
from sqlalchemy import text

from config.database import get_engine
from extract import extract_products
from load import (
    load_dim_date,
    load_dim_product,
    load_fact_sales,
    load_staging,
    reset_warehouse_tables,
)
from transform import transform_products, simulate_sales


def check_database_connection():
    """Valida conexão com o banco antes de iniciar o pipeline."""
    # Cria engine e testa uma consulta simples.
    # Se o banco estiver fora do ar, a execução para aqui com erro claro.
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def main():
    # 0) PRE-CHECK: garante que o banco esta acessivel antes do ETL.
    check_database_connection()

    # 1) EXTRAÇÃO: coleta dados sem tratamento.
    raw = extract_products()

    # 2) TRANSFORMAÇÃO: organiza colunas e remove ruídos.
    products_df = transform_products(raw)

    # 3) Geração de fatos sintéticos de vendas.
    sales_df = simulate_sales(products_df)

    # Carrega cópia "raw tratada" na staging para auditoria/rastreabilidade.
    load_staging(products_df)

    # Limpa a camada analitica para que o rerun nao duplique dados.
    reset_warehouse_tables()

    # 4) Carga em dimensões e fatos no banco.
    load_dim_product(products_df)
    load_dim_date(sales_df)
    load_fact_sales(sales_df)

if __name__ == "__main__":
    # Permite executar o pipeline diretamente via `python main.py`.
    main()
