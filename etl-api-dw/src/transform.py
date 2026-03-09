"""Camada de transformação de dados (Transform) do pipeline ETL.

Contém:
- Normalização de campos de produtos vindos da extração.
- Simulação de vendas para geração de dados analíticos.
"""

from datetime import date, datetime, timedelta
import hashlib
import random

import pandas as pd


def transform_products(raw_data):
    """Normaliza o dataset de produtos para um schema mínimo e consistente.

    Args:
        raw_data (list[dict]): Lista de produtos em formato bruto (JSON).

    Returns:
        pandas.DataFrame: Tabela com colunas essenciais sem duplicidades.
    """
    # Entrada esperada: lista de dicionários (JSON da etapa extract).
    # Saída desta linha: tabela em memória para filtrar/limpar com pandas.
    df = pd.DataFrame(raw_data)

    # Mantém apenas as colunas necessárias para análise e modelagem de vendas.
    df = df[["id", "title", "price", "category"]]

    # Remove registros repetidos para evitar contagem duplicada em métricas.
    # Regra prática: ETL deve produzir base "confiável" antes de gerar análises.
    df = df.drop_duplicates()

    return df


def generate_sale_id(product_id, quantity, unit_price, sale_date, sequence):
    """Gera uma chave deterministica para a venda simulada.

    A ideia e simples:
    - montar uma representacao canonica da venda;
    - aplicar hash para obter um identificador pequeno e estavel;
    - usar esse valor como chave de negocio da fato.
    """
    raw_key = f"{product_id}|{quantity}|{unit_price:.2f}|{sale_date.isoformat()}|{sequence}"
    return hashlib.sha1(raw_key.encode("utf-8")).hexdigest()[:16]


def simulate_sales(product_df, n=200, seed=42, reference_date=None):
    """Gera um conjunto sintético de vendas baseado no catálogo de produtos.

    Args:
        product_df (pandas.DataFrame): Catálogo já transformado.
        n (int, optional): Quantidade de vendas a simular. Padrão: 200.
        seed (int, optional): Semente do gerador aleatorio para reproducao.
        reference_date (date | datetime | None, optional): Data base da simulacao.

    Returns:
        pandas.DataFrame: Tabela de vendas simuladas contendo
            ``sale_id``, ``product_id``, ``quantity``, ``unit_price`` e ``sale_date``.
    """
    # Seed fixa ajuda no estudo: a mesma entrada gera a mesma simulacao.
    rng = random.Random(seed)
    base_date = reference_date or date.today()
    if isinstance(base_date, datetime):
        base_date = base_date.date()

    # Vamos acumular cada venda como um dicionário e converter para DataFrame no final.
    sales = []

    # Cada iteração representa UMA venda.
    for sequence in range(n):
        # Sorteia um produto aleatório para representar uma venda individual.
        product = product_df.sample(1, random_state=rng.randint(0, 10_000_000)).iloc[0]

        # Define quantidade vendida entre 1 e 5 unidades.
        quantity = rng.randint(1, 5)

        # Distribui vendas nos ultimos 30 dias a partir de uma data base controlada.
        sale_date = base_date - timedelta(days=rng.randint(0, 30))
        sale_id = generate_sale_id(
            product_id=product["id"],
            quantity=quantity,
            unit_price=product["price"],
            sale_date=sale_date,
            sequence=sequence,
        )

        # Estrutura final de cada venda (grão do dado): 1 linha = 1 transação.
        sales.append(
            {
                "sale_id": sale_id,
                "product_id": product["id"],
                "quantity": quantity,
                "unit_price": product["price"],
                "sale_date": sale_date,
            }
        )

    # Converte lista de transações para formato tabular (pronto para load/análise).
    return pd.DataFrame(sales)
