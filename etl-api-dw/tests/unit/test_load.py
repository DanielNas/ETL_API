"""Testes unitarios da camada de carga.

O foco aqui e validar os DataFrames intermediarios antes da persistencia:
- formato da dimensao de produtos;
- derivacao da dimensao de datas;
- formato final da fato de vendas.
"""

from datetime import date
from pathlib import Path
import sys
import unittest

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from load import _prepare_dim_date_df, _prepare_dim_product_df, _prepare_fact_sales_df


class LoadPreparationTestCase(unittest.TestCase):
    """Valida helpers que preparam dados para carga."""

    def test_prepare_dim_product_df_renames_and_selects_columns(self):
        product_df = pd.DataFrame(
            [
                {"id": 1, "title": "Notebook", "price": 1000.0, "category": "tech"},
            ]
        )

        result = _prepare_dim_product_df(product_df)

        self.assertEqual(list(result.columns), ["product_id", "product_name", "category"])
        self.assertEqual(result.iloc[0]["product_name"], "Notebook")

    def test_prepare_dim_date_df_builds_calendar_attributes(self):
        sales_df = pd.DataFrame(
            [
                {"sale_date": date(2026, 3, 9)},
                {"sale_date": date(2026, 3, 9)},
                {"sale_date": date(2026, 3, 8)},
            ]
        )

        result = _prepare_dim_date_df(sales_df)

        self.assertEqual(list(result.columns), ["date", "year", "month", "day"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["date"], date(2026, 3, 8))

    def test_prepare_fact_sales_df_computes_total_amount_and_keeps_sale_id(self):
        sales_df = pd.DataFrame(
            [
                {
                    "sale_id": "abc123",
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 10.0,
                    "sale_date": date(2026, 3, 9),
                }
            ]
        )

        result = _prepare_fact_sales_df(sales_df)

        self.assertEqual(
            list(result.columns),
            ["sale_id", "product_id", "date", "quantity", "total_amount"],
        )
        self.assertEqual(result.iloc[0]["total_amount"], 20.0)
        self.assertEqual(result.iloc[0]["sale_id"], "abc123")


if __name__ == "__main__":
    unittest.main()
