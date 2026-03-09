import logging


def get_logger(name):
    """Retorna um logger padronizado para todo o projeto."""

    # Configuração global do formato de log para facilitar debug do pipeline.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # `name` normalmente recebe __name__, identificando qual módulo logou a mensagem.
    return logging.getLogger(name)
