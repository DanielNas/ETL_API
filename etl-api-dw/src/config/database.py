import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carrega .env da raiz do projeto (etl-api-dw), independente de onde o script for executado.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

def get_engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL nao definido. "
        )

    engine = create_engine(database_url)

    return engine
