"""Camada de extração de dados (Extract) do pipeline ETL.

Este módulo centraliza a leitura de produtos de uma API externa e retorna
os dados brutos em formato JSON para as etapas seguintes.
"""

import requests
from utils.logger import get_logger

# Logger do módulo: registra o que aconteceu durante a extração.
logger = get_logger(__name__)

def extract_products():
    """Busca produtos da Fake Store API e retorna a lista em JSON.

    Fluxo:
    1. Define o endpoint de origem.
    2. Executa a requisição HTTP GET.
    3. Valida erros HTTP com ``raise_for_status``.
    4. Retorna o payload convertido para estruturas nativas (list/dict).

    Returns:
        list[dict]: Dados brutos de produtos retornados pela API.
    """
    # Fonte única de dados desta etapa (Extract).
    url = "https://fakestoreapi.com/products"

    logger.info("Extraindo dados da API")

    # Requisição simples para coletar o dataset de produtos.
    response = requests.get(url)

    # Garante falha explícita para status 4xx/5xx, evitando dados inválidos no ETL.
    response.raise_for_status()

    # A API devolve uma lista de dicionários:
    # [{"id": ..., "title": ..., "price": ..., "category": ...}, ...]
    # Esse formato já é ideal para virar DataFrame na etapa de transformação.
    return response.json()
