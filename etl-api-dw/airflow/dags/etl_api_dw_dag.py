"""DAG do Airflow para orquestrar o pipeline ETL do projeto."""

from pathlib import Path
import sys

import pandas as pd
from airflow.decorators import dag, task
from airflow.utils.task_group import TaskGroup
from pendulum import datetime, duration


# Garante que os modulos do projeto possam ser importados pela DAG.
PROJECT_SRC = Path("/opt/airflow/project/src")
if str(PROJECT_SRC) not in sys.path:
    sys.path.append(str(PROJECT_SRC))

from extract import extract_products
from load import (
    load_dim_date,
    load_dim_product,
    load_fact_sales,
    load_staging,
    reset_warehouse_tables,
)
from main import check_database_connection
from transform import simulate_sales, transform_products


def log_task_failure(context):
    """Callback simples para estudo de observabilidade em falhas."""
    task_instance = context["task_instance"]
    print(
        "Task falhou:",
        {
            "dag_id": task_instance.dag_id,
            "task_id": task_instance.task_id,
            "run_id": task_instance.run_id,
        },
    )


@dag(
    dag_id="etl_api_dw",
    start_date=datetime(2024, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=duration(minutes=15),
    tags=["etl", "dw", "study"],
    default_args={
        "owner": "airflow",
        "retries": 2,
        "retry_delay": duration(minutes=1),
        "execution_timeout": duration(minutes=5),
        "depends_on_past": False,
        "on_failure_callback": log_task_failure,
    },
)
def etl_api_dw():
    """Define a orquestracao do ETL em tarefas independentes.

    A DAG foi organizada em TaskGroups para refletir a logica do pipeline:
    - preparacao do ambiente;
    - extracao e transformacao;
    - carga no Data Warehouse.
    """

    @task
    def validate_database():
        """Falha cedo se o banco nao estiver acessivel."""
        check_database_connection()

    @task
    def extract_task():
        """Extrai os produtos e retorna estrutura serializavel via XCom."""
        return extract_products()

    @task
    def transform_task(raw_data):
        """Transforma produtos e gera vendas sinteticas em formato serializavel."""
        products_df = transform_products(raw_data)
        sales_df = simulate_sales(products_df)

        return {
            "products": products_df.to_dict(orient="records"),
            "sales": sales_df.to_dict(orient="records"),
        }

    @task
    def load_staging_task(payload):
        """Carrega a camada staging."""
        products_df = pd.DataFrame(payload["products"])
        load_staging(products_df)

    @task
    def reset_warehouse_task():
        """Limpa as tabelas analiticas antes da recarga."""
        reset_warehouse_tables()

    @task
    def load_dim_product_task(payload):
        """Carrega a dimensao de produtos."""
        products_df = pd.DataFrame(payload["products"])
        load_dim_product(products_df)

    @task
    def load_dim_date_task(payload):
        """Carrega a dimensao de datas."""
        sales_df = pd.DataFrame(payload["sales"])
        load_dim_date(sales_df)

    @task
    def load_fact_sales_task(payload):
        """Carrega a fato de vendas."""
        sales_df = pd.DataFrame(payload["sales"])
        load_fact_sales(sales_df)

    with TaskGroup(group_id="prepare", tooltip="Validacoes iniciais do ambiente") as prepare_group:
        database_ready = validate_database()

    with TaskGroup(group_id="extract_transform", tooltip="Coleta e modelagem dos dados") as extract_transform_group:
        raw_data = extract_task()
        transformed_payload = transform_task(raw_data)
        raw_data >> transformed_payload

    with TaskGroup(group_id="load", tooltip="Carga das camadas do Data Warehouse") as load_group:
        staging_loaded = load_staging_task(transformed_payload)
        warehouse_reset = reset_warehouse_task()
        dim_loaded = load_dim_product_task(transformed_payload)
        dim_date_loaded = load_dim_date_task(transformed_payload)
        fact_loaded = load_fact_sales_task(transformed_payload)

        transformed_payload >> staging_loaded
        transformed_payload >> warehouse_reset
        warehouse_reset >> dim_loaded
        warehouse_reset >> dim_date_loaded
        dim_loaded >> fact_loaded
        dim_date_loaded >> fact_loaded

    prepare_group >> extract_transform_group >> load_group


etl_api_dw()
