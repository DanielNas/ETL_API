"""Camada de carga de dados (Load) do pipeline ETL.

Este modulo grava os dados transformados no banco analitico:
- Dimensao de produtos (dim_product)
- Fato de vendas (fact_sales)
"""

from config.database import get_engine
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

def load_staging(df):
    engine = get_engine()

    df.to_sql(
        "stg_products",
        engine,
        if_exists="append",
        index=False
    )

def load_dim_product(df):
    """Carrega a dimensao de produtos no Data Warehouse."""
    engine = get_engine()

    # Renomeia campos para o padrao dimensional e seleciona apenas o necessario.
    df.rename(
        columns={
            "id": "product_id",
            "title": "product_name",
        }
    )[["product_id", "product_name", "category"]].to_sql(
        "dim_product", engine, if_exists="replace", index=False
    )

def load_fact_sales(df):
    """Carrega os eventos de venda na tabela fato."""
    engine = get_engine()

    # Medida principal da fato: valor total da venda.
    df["total_amount"] = df["quantity"] * df["unit_price"]

    # Log de carga
    logger.info("Carregando dados no banco")

    # Ajusta schema para a tabela fato e acumula novos registros.
    df.rename(columns={"sale_date": "date"})[
        ["product_id", "date", "quantity", "total_amount"]
    ].to_sql("fact_sales", engine, if_exists="append", index=False)
