"""Ponto de entrada do pipeline ETL.

Ordem executada:
1. Extract: busca dados brutos de produtos na API.
2. Transform: limpa produtos e simula vendas.
3. Load: grava dimensões e fatos no banco analítico.
"""

from sqlalchemy import text

from config.database import get_engine
from extract import extract_products
from load import load_staging, load_dim_product, load_fact_sales
from transform import transform_products, simulate_sales

def check_database_connection():
    """Valida conexão com o banco antes de iniciar o pipeline."""
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

    load_staging(products_df)

    # 4) Carga em dimensões e fatos no banco.
    load_dim_product(products_df)
    load_fact_sales(sales_df)

if __name__ == "__main__":
    # Permite executar o pipeline diretamente via `python main.py`.
    main()
