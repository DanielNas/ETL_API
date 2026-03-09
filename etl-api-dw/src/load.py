"""Camada de carga de dados (Load) do pipeline ETL.

Este modulo grava os dados transformados no banco analitico:
- Dimensao de produtos (dim_product)
- Dimensao de datas (dim_date)
- Fato de vendas (fact_sales)

A ideia principal desta camada e:
1. garantir que o schema exista;
2. transformar DataFrames em estruturas de DW;
3. manter reruns previsiveis e idempotentes.
"""

import pandas as pd
from sqlalchemy import inspect, text

from config.database import get_engine
from utils.logger import get_logger

# Logger do módulo: útil para acompanhar em qual etapa da carga o ETL está.
logger = get_logger(__name__)


def _table_exists(connection, table_name):
    """Verifica se a tabela existe antes de operar nela."""
    return inspect(connection).has_table(table_name)


def _table_has_column(connection, table_name, column_name):
    """Confere se uma coluna existe na tabela atual."""
    columns = inspect(connection).get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def _table_has_primary_key(connection, table_name, expected_columns):
    """Confere se a tabela possui a chave primaria esperada."""
    pk_constraint = inspect(connection).get_pk_constraint(table_name)
    constrained_columns = pk_constraint.get("constrained_columns") or []
    return constrained_columns == expected_columns


def _prepare_dim_product_df(df):
    """Converte o catalogo para o formato da dimensao de produtos."""
    return df.rename(
        columns={
            "id": "product_id",
            "title": "product_name",
        }
    )[["product_id", "product_name", "category"]].copy()


def _prepare_dim_date_df(df):
    """Deriva a dimensao de datas a partir das datas presentes nas vendas."""
    date_df = pd.DataFrame({"date": pd.to_datetime(df["sale_date"]).dt.date})
    date_df = date_df.drop_duplicates().sort_values("date")

    # Separa a data em atributos analiticos para filtros e agregacoes.
    date_df["year"] = pd.to_datetime(date_df["date"]).dt.year
    date_df["month"] = pd.to_datetime(date_df["date"]).dt.month
    date_df["day"] = pd.to_datetime(date_df["date"]).dt.day
    return date_df


def _prepare_fact_sales_df(df):
    """Converte vendas simuladas para o schema final da tabela fato."""
    fact_df = df.copy()

    # A fato guarda medidas finais, nao preco unitario intermediario.
    fact_df["total_amount"] = fact_df["quantity"] * fact_df["unit_price"]
    fact_df = fact_df.rename(columns={"sale_date": "date"})
    return fact_df[
        ["sale_id", "product_id", "date", "quantity", "total_amount"]
    ].copy()


def ensure_warehouse_schema():
    """Cria ou ajusta o schema minimo necessario para o DW.

    Como o projeto e didatico e evoluiu durante o estudo, esta funcao tambem
    corrige o caso em que `fact_sales` ainda existe no formato antigo sem
    `sale_id`.
    """
    engine = get_engine()

    with engine.begin() as conn:
        # Se tabelas antigas foram criadas por `to_sql`, elas podem existir sem PK.
        # Nesse caso, derrubamos o schema analitico e recriamos no formato correto.
        if _table_exists(conn, "fact_sales") and not _table_has_column(conn, "fact_sales", "sale_id"):
            conn.execute(text("DROP TABLE fact_sales"))
        if _table_exists(conn, "dim_date") and not _table_has_primary_key(conn, "dim_date", ["date"]):
            if _table_exists(conn, "fact_sales"):
                conn.execute(text("DROP TABLE fact_sales"))
            conn.execute(text("DROP TABLE dim_date"))
        if _table_exists(conn, "dim_product") and not _table_has_primary_key(conn, "dim_product", ["product_id"]):
            if _table_exists(conn, "fact_sales"):
                conn.execute(text("DROP TABLE fact_sales"))
            conn.execute(text("DROP TABLE dim_product"))

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS stg_products (
                    id INT,
                    title TEXT,
                    price NUMERIC,
                    category TEXT,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS dim_product (
                    product_id INT PRIMARY KEY,
                    product_name TEXT,
                    category TEXT
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS dim_date (
                    date DATE PRIMARY KEY,
                    year INT,
                    month INT,
                    day INT
                )
                """
            )
        )

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS fact_sales (
                    sale_id TEXT PRIMARY KEY,
                    product_id INT REFERENCES dim_product(product_id),
                    date DATE REFERENCES dim_date(date),
                    quantity INT,
                    total_amount NUMERIC
                )
                """
            )
        )


def reset_warehouse_tables():
    """Limpa as tabelas do DW para permitir reruns idempotentes."""
    engine = get_engine()
    ensure_warehouse_schema()

    # Fato primeiro, depois dimensoes, para respeitar dependencias logicas.
    with engine.begin() as conn:
        for table_name in ["fact_sales", "dim_date", "dim_product"]:
            conn.execute(text(f"DELETE FROM {table_name}"))


def load_staging(df):
    """Carrega produtos tratados na camada staging."""
    engine = get_engine()
    ensure_warehouse_schema()

    # Staging vira um snapshot da ultima extração, sem acumular duplicatas.
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM stg_products"))

    df.to_sql("stg_products", engine, if_exists="append", index=False)


def load_dim_product(df):
    """Carrega a dimensao de produtos no Data Warehouse."""
    engine = get_engine()
    ensure_warehouse_schema()
    dim_product_df = _prepare_dim_product_df(df)
    dim_product_df.to_sql("dim_product", engine, if_exists="append", index=False)


def load_dim_date(df):
    """Carrega a dimensao de datas a partir das datas presentes nas vendas."""
    engine = get_engine()
    ensure_warehouse_schema()
    dim_date_df = _prepare_dim_date_df(df)
    dim_date_df.to_sql("dim_date", engine, if_exists="append", index=False)


def load_fact_sales(df):
    """Carrega os eventos de venda na tabela fato."""
    engine = get_engine()
    ensure_warehouse_schema()
    fact_sales_df = _prepare_fact_sales_df(df)

    # Log de carga
    logger.info("Carregando dados no banco")
    fact_sales_df.to_sql("fact_sales", engine, if_exists="append", index=False)
