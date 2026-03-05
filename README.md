# ETL API DW

Pipeline ETL em Python para estudo de engenharia de dados, com:
- `Extract` de produtos da Fake Store API
- `Transform` para normalização e simulação de vendas
- `Load` em PostgreSQL (Docker)

## Objetivo
Praticar lógica ETL ponta a ponta:
1. Ler dados de API externa
2. Tratar e modelar em DataFrame
3. Persistir em camadas staging/dimensão/fato

## Arquitetura
- Fonte: `https://fakestoreapi.com/products`
- Banco: PostgreSQL 15 via Docker Compose
- Linguagem: Python 3.11
- Bibliotecas principais: `pandas`, `SQLAlchemy`, `psycopg2`, `python-dotenv`

Fluxo:
1. `extract_products()` coleta JSON da API
2. `transform_products()` seleciona colunas e remove duplicados
3. `simulate_sales()` gera vendas sintéticas
4. `load_staging()`, `load_dim_product()`, `load_fact_sales()` gravam no banco

## Estrutura do Projeto
```text
etl-api-dw/
  docker/
    docker-compose.yaml
  sql/
    staging_tables.sql
    dw_tables.sql
  src/
    main.py
    extract.py
    transform.py
    load.py
    config/
      database.py
    utils/
      logger.py
  .env
  requirements.txt
```

## Pré-requisitos
- Python 3.11+
- Docker Desktop
- PowerShell (Windows)

## Configuração do Ambiente
No diretório `etl-api-dw`:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie/ajuste o arquivo `.env` com:

```env
DATABASE_URL=postgresql+psycopg2://postgres:123456@localhost:5433/sales_dw
```

## Subindo o Banco (Docker)
Na pasta `etl-api-dw`:

```powershell
docker-compose -f docker/docker-compose.yaml up -d
```

Verificar status:

```powershell
docker-compose -f docker/docker-compose.yaml ps
```

## Executando o Pipeline
Na pasta `etl-api-dw`, com `venv` ativo:

```powershell
python src/main.py
```

Logs esperados:
- `Extraindo dados da API`
- `Carregando dados no banco`

## Como Validar os Dados no PostgreSQL
Conecte no banco com:
- Host: `localhost`
- Port: `5433`
- Database: `sales_dw`
- User: `postgres`
- Password: `123456`

Consultas de validação:

```sql
SELECT COUNT(*) FROM stg_products;
SELECT COUNT(*) FROM dim_product;
SELECT COUNT(*) FROM fact_sales;
```

## Scripts SQL
Os arquivos em `sql/` servem para modelagem/estudo:
- `staging_tables.sql`: estrutura de staging
- `dw_tables.sql`: estrutura dimensional (dimensões e fato)

Observação:
- O pipeline atual usa `pandas.to_sql`, que pode criar tabelas automaticamente.
- Se você optar por criar tabelas manualmente via SQL, garanta compatibilidade de schema e constraints.

## Troubleshooting
### 1) `empty compose file`
Causa: comando rodado na pasta errada sem `-f`.

Correção:
```powershell
docker-compose -f docker/docker-compose.yaml up -d
```

### 2) `Expected string or URL object, got None`
Causa: `DATABASE_URL` ausente no `.env`.

Correção:
- Criar `.env` na raiz de `etl-api-dw`
- Definir `DATABASE_URL` corretamente

### 3) `OperationalError` no PostgreSQL
Causa comum: conflito de porta com PostgreSQL local na `5432`.

Correção adotada no projeto:
- Docker exposto em `5433:5432`
- App conecta em `localhost:5433`

### 4) Erro de logging com `levename`
Causa: typo no formatter.

Correto:
```python
format="%(asctime)s | %(levelname)s | %(message)s"
```

## Comandos Úteis
Parar ambiente:
```powershell
docker-compose -f docker/docker-compose.yaml down
```

Recriar containers:
```powershell
docker-compose -f docker/docker-compose.yaml down
docker-compose -f docker/docker-compose.yaml up -d
```

## Próximos Passos (estudo)
- Popular `dim_date` automaticamente no ETL
- Adicionar testes unitários para `transform.py`
- Versionar schema com migrações (`alembic`)
- Adicionar volume Docker para persistência de dados entre recriações
