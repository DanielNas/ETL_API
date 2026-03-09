"""Testes unitarios da camada de transformacao.

Os testes focam em regras de negocio puras:
- selecao e deduplicacao de produtos;
- reproducibilidade da simulacao;
- geracao de sale_id deterministico.
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

from transform import generate_sale_id, simulate_sales, transform_products


class TransformProductsTestCase(unittest.TestCase):
    """Valida a normalizacao do catalogo bruto."""

    def test_transform_products_selects_expected_columns_and_drops_duplicates(self):
        raw_data = [
            {"id": 1, "title": "Notebook", "price": 1000.0, "category": "tech", "extra": "x"},
            {"id": 1, "title": "Notebook", "price": 1000.0, "category": "tech", "extra": "y"},
            {"id": 2, "title": "Mouse", "price": 50.0, "category": "tech", "extra": "z"},
        ]

        result = transform_products(raw_data)

        self.assertEqual(list(result.columns), ["id", "title", "price", "category"])
        self.assertEqual(len(result), 2)


class SimulateSalesTestCase(unittest.TestCase):
    """Valida a simulacao sintetica de vendas."""

    def setUp(self):
        self.product_df = pd.DataFrame(
            [
                {"id": 1, "title": "Notebook", "price": 1000.0, "category": "tech"},
                {"id": 2, "title": "Mouse", "price": 50.0, "category": "tech"},
            ]
        )

    def test_generate_sale_id_is_deterministic(self):
        sale_id_one = generate_sale_id(1, 2, 1000.0, date(2026, 3, 9), 0)
        sale_id_two = generate_sale_id(1, 2, 1000.0, date(2026, 3, 9), 0)
        sale_id_three = generate_sale_id(1, 2, 1000.0, date(2026, 3, 9), 1)

        self.assertEqual(sale_id_one, sale_id_two)
        self.assertNotEqual(sale_id_one, sale_id_three)

    def test_simulate_sales_is_reproducible_with_same_seed_and_reference_date(self):
        first_run = simulate_sales(
            self.product_df,
            n=5,
            seed=123,
            reference_date=date(2026, 3, 9),
        )
        second_run = simulate_sales(
            self.product_df,
            n=5,
            seed=123,
            reference_date=date(2026, 3, 9),
        )

        pd.testing.assert_frame_equal(first_run, second_run)
        self.assertEqual(len(first_run["sale_id"].unique()), len(first_run))


if __name__ == "__main__":
    unittest.main()
