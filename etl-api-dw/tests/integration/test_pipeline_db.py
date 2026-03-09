"""Testes de integracao do pipeline contra o banco real.

Esses testes exercitam a camada de carga com o Postgres configurado no projeto.
Eles sao uteis para estudar a diferenca entre:
- teste unitario: valida regra isolada;
- teste de integracao: valida colaboracao entre codigo, schema e banco.
"""

from datetime import date
from pathlib import Path
import sys
import unittest

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from config.database import get_engine
from load import (
    ensure_warehouse_schema,
    load_dim_date,
    load_dim_product,
    load_fact_sales,
    load_staging,
    reset_warehouse_tables,
)
from transform import simulate_sales, transform_products


class PipelineDatabaseIntegrationTestCase(unittest.TestCase):
    """Valida o pipeline no banco configurado pelo projeto."""

    @classmethod
    def setUpClass(cls):
        cls.engine = get_engine()

    def setUp(self):
        raw_data = [
            {"id": 1, "title": "Notebook", "price": 1000.0, "category": "tech"},
            {"id": 2, "title": "Mouse", "price": 50.0, "category": "tech"},
        ]
        self.products_df = transform_products(raw_data)
        self.sales_df = simulate_sales(
            self.products_df,
            n=10,
            seed=7,
            reference_date=date(2026, 3, 9),
        )

        ensure_warehouse_schema()
        load_staging(self.products_df)
        reset_warehouse_tables()

    def test_pipeline_loads_expected_shapes_into_database(self):
        load_dim_product(self.products_df)
        load_dim_date(self.sales_df)
        load_fact_sales(self.sales_df)

        with self.engine.connect() as conn:
            staging_count = conn.execute(text("SELECT COUNT(*) FROM stg_products")).scalar()
            dim_product_count = conn.execute(text("SELECT COUNT(*) FROM dim_product")).scalar()
            dim_date_count = conn.execute(text("SELECT COUNT(*) FROM dim_date")).scalar()
            fact_sales_count = conn.execute(text("SELECT COUNT(*) FROM fact_sales")).scalar()

        self.assertEqual(staging_count, 2)
        self.assertEqual(dim_product_count, 2)
        self.assertGreaterEqual(dim_date_count, 1)
        self.assertEqual(fact_sales_count, 10)

    def test_fact_sales_uses_sale_id_as_primary_business_key(self):
        load_dim_product(self.products_df)
        load_dim_date(self.sales_df)
        load_fact_sales(self.sales_df)

        with self.engine.connect() as conn:
            duplicated_sale_ids = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM (
                        SELECT sale_id
                        FROM fact_sales
                        GROUP BY sale_id
                        HAVING COUNT(*) > 1
                    ) duplicated
                    """
                )
            ).scalar()

        self.assertEqual(duplicated_sale_ids, 0)


if __name__ == "__main__":
    unittest.main()
