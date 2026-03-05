"""Camada de transformação de dados (Transform) do pipeline ETL.

Contém:
- Normalização de campos de produtos vindos da extração.
- Simulação de vendas para geração de dados analíticos.
"""

from datetime import datetime, timedelta
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


def simulate_sales(product_df, n=200):
    """Gera um conjunto sintético de vendas baseado no catálogo de produtos.

    Args:
        product_df (pandas.DataFrame): Catálogo já transformado.
        n (int, optional): Quantidade de vendas a simular. Padrão: 200.

    Returns:
        pandas.DataFrame: Tabela de vendas simuladas contendo
            ``product_id``, ``quantity``, ``unit_price`` e ``sale_date``.
    """
    # Vamos acumular cada venda como um dicionário e converter para DataFrame no final.
    sales = []

    # Cada iteração representa UMA venda.
    for _ in range(n):
        # Sorteia um produto aleatório para representar uma venda individual.
        product = product_df.sample(1).iloc[0]

        # Define quantidade vendida entre 1 e 5 unidades.
        quantity = random.randint(1, 5)

        # Distribui vendas nos últimos 30 dias para simular histórico recente.
        sale_date = datetime.today() - timedelta(days=random.randint(0, 30))

        # Estrutura final de cada venda (grão do dado): 1 linha = 1 transação.
        sales.append(
            {
                "product_id": product["id"],
                "quantity": quantity,
                "unit_price": product["price"],
                "sale_date": sale_date.date(),
            }
        )

    # Converte lista de transações para formato tabular (pronto para load/análise).
    return pd.DataFrame(sales)
