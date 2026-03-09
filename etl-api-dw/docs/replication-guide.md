# Guia Completo de Replicacao do Projeto

## Objetivo deste guia
Este guia mostra, em ordem, como recriar o projeto do zero e entender o raciocinio por tras de cada etapa.

Ele foi escrito para estudo. A ideia nao e apenas copiar comandos, mas entender:
- por que cada arquivo existe;
- por que a ordem importa;
- como cada camada conversa com a seguinte.

## Visao Geral do que voce vai construir
Ao final do processo voce tera:
- um projeto Python com pipeline ETL
- um banco PostgreSQL rodando em Docker
- um Airflow local orquestrando a DAG
- testes unitarios e de integracao
- um modelo analitico com staging, dimensao e fato

## Ordem Recomendada de Construcao
1. criar a estrutura do projeto
2. criar e ativar o ambiente virtual
3. instalar dependencias Python
4. configurar o arquivo `.env`
5. criar a camada de extração
6. criar a camada de transformação
7. criar a camada de carga
8. criar o entrypoint local do ETL
9. modelar tabelas SQL
10. subir o PostgreSQL com Docker
11. validar execucao local do pipeline
12. adicionar Airflow
13. criar a DAG
14. validar execucao no Airflow
15. criar testes unitarios
16. criar testes de integracao
17. documentar arquitetura e fluxo

## 1. Criar a estrutura de pastas
Na raiz do workspace:

```powershell
mkdir etl-api-dw
cd .\etl-api-dw
mkdir src, sql, docker, airflow, tests
mkdir src\config, src\utils, airflow\dags, tests\unit, tests\integration
```

Estrutura esperada:

```text
etl-api-dw/
  airflow/
    dags/
  docker/
  sql/
  src/
    config/
    utils/
  tests/
    unit/
    integration/
```

## 2. Criar o ambiente virtual
Comando:

```powershell
python -m venv venv
```

### Ativar no PowerShell
Se voce estiver dentro de `etl-api-dw`:

```powershell
.\venv\Scripts\Activate.ps1
```

Se der erro de politica de execucao:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 3. Instalar dependencias Python
Crie `requirements.txt` com:

```text
requests==2.32.3
pandas==2.2.3
SQLAlchemy==2.0.36
psycopg2-binary==2.9.10
python-dotenv==1.0.1
```

Instale:

```powershell
pip install -r requirements.txt
```

## 4. Configurar o `.env`
Crie o arquivo `.env` na raiz de `etl-api-dw`.

Exemplo deste projeto:

```env
DATABASE_URL=postgresql+psycopg2://postgres:123456@localhost:5433/sales_dw
```

Raciocinio:
- `localhost:5433` aponta para a porta exposta do container
- dentro do container do Airflow, o host nao sera `localhost`, e sim `postgres`

## 5. Criar o logger
Arquivo: `src/utils/logger.py`

Papel:
- padronizar logs do projeto
- facilitar debug do ETL

Conceito:
- logs sao fundamentais em pipelines porque voce raramente depura step by step em producao

## 6. Criar a configuracao de banco
Arquivo: `src/config/database.py`

Responsabilidades:
- carregar `.env`
- ler `DATABASE_URL`
- criar `engine` do SQLAlchemy

Conceito:
- a camada de configuracao centraliza dependencia externa
- assim voce nao espalha string de conexao pelo codigo

## 7. Criar a camada Extract
Arquivo: `src/extract.py`

Responsabilidades:
- chamar a API
- validar status HTTP
- retornar JSON

Fluxo:
1. define a URL da fonte
2. faz `GET`
3. usa `raise_for_status()`
4. retorna `response.json()`

## 8. Criar a camada Transform
Arquivo: `src/transform.py`

Responsabilidades:
- transformar dados brutos em formato analitico
- gerar vendas sinteticas
- criar `sale_id` deterministico

Conceitos importantes:
- `transform_products()`: reduz colunas e remove duplicidades
- `simulate_sales()`: gera dataset sintético para estudo
- `generate_sale_id()`: chave de negocio estavel da venda

Por que usar `seed`:
- permite reproduzir o mesmo resultado em testes e reruns

## 9. Criar a camada Load
Arquivo: `src/load.py`

Responsabilidades:
- garantir schema do DW
- montar DataFrames finais
- carregar staging, dimensoes e fato

Funcoes principais:
- `ensure_warehouse_schema()`
- `reset_warehouse_tables()`
- `load_staging()`
- `load_dim_product()`
- `load_dim_date()`
- `load_fact_sales()`

Raciocinio:
- a camada de carga precisa conhecer a modelagem do banco
- por isso ela prepara DataFrames no formato final antes de persistir

## 10. Criar o entrypoint local
Arquivo: `src/main.py`

Responsabilidades:
- orquestrar o pipeline fora do Airflow
- servir como caminho simples de execucao

Ordem correta:
1. validar banco
2. extrair
3. transformar
4. simular vendas
5. carregar staging
6. resetar DW
7. carregar `dim_product`
8. carregar `dim_date`
9. carregar `fact_sales`

## 11. Criar os scripts SQL
Arquivos:
- `sql/staging_tables.sql`
- `sql/dw_tables.sql`

Papel:
- documentar a modelagem do banco
- representar o contrato analitico do projeto

Conceito:
- mesmo usando `to_sql`, manter o SQL explicito ajuda no estudo de modelagem

## 12. Configurar Docker Compose
Arquivo: `docker/docker-compose.yaml`

Servicos principais:
- `postgres`
- `airflow`

Conceitos do YAML:
- `services`: lista de containers
- `environment`: variaveis de ambiente
- `ports`: mapeamento host -> container
- `volumes`: persistencia de dados
- `depends_on`: ordem de dependencia
- `healthcheck`: verifica se o servico esta pronto

Exemplo importante:

```yaml
ports:
  - "5433:5432"
```

Leitura:
- host `5433`
- container `5432`

## 13. Subir apenas o banco primeiro
Comando:

```powershell
docker-compose -f docker/docker-compose.yaml up -d postgres
```

Conferir status:

```powershell
docker-compose -f docker/docker-compose.yaml ps
```

## 14. Rodar o pipeline localmente
Comando:

```powershell
python src/main.py
```

O que isso valida:
- conexao com banco
- acesso a API
- transformacao
- carga no DW

## 15. Consultar o banco
Exemplos SQL:

```sql
SELECT COUNT(*) FROM stg_products;
SELECT COUNT(*) FROM dim_product;
SELECT COUNT(*) FROM dim_date;
SELECT COUNT(*) FROM fact_sales;
```

Verificar schema da fato:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'fact_sales'
ORDER BY ordinal_position;
```

## 16. Adicionar Airflow
Arquivos:
- `docker/Dockerfile.airflow`
- `docker/requirements-airflow.txt`
- `airflow/dags/etl_api_dw_dag.py`

### Dockerfile.airflow
Papel:
- criar imagem customizada do Airflow com dependencias do projeto

Ponto critico:
- usar constraints oficiais do Airflow para evitar conflitos de versao

### requirements-airflow.txt
Papel:
- instalar apenas dependencias necessarias para a DAG acessar o projeto

Regra:
- nao forcar versoes incompatíveis com as constraints do Airflow

## 17. Subir o projeto completo com Airflow
Comando:

```powershell
docker-compose -f docker/docker-compose.yaml up --build
```

Acesso:
- Airflow UI em `http://localhost:8080`

## 18. Encontrar credenciais do Airflow
Se estiver usando `standalone`, confira os logs:

```powershell
docker logs airflow
```

Procure o usuario e senha inicial gerados automaticamente.

## 19. Entender a DAG
Arquivo: `airflow/dags/etl_api_dw_dag.py`

Organizacao:
- `TaskGroup prepare`
- `TaskGroup extract_transform`
- `TaskGroup load`

Tarefas:
- validar banco
- extrair produtos
- transformar produtos e vendas
- carregar staging
- resetar DW
- carregar dimensoes
- carregar fato

Conceito:
- a DAG nao substitui o ETL
- ela orquestra o ETL

## 20. Rodar a DAG
### Pela UI
1. abrir o Airflow
2. localizar `etl_api_dw`
3. despausar a DAG
4. clicar em trigger

### Pelo CLI
```powershell
docker exec airflow airflow dags unpause etl_api_dw
docker exec airflow airflow dags trigger etl_api_dw
```

Consultar status:

```powershell
docker exec airflow airflow dags list
docker exec airflow airflow tasks states-for-dag-run etl_api_dw <dag_run_id>
```

## 21. Criar testes unitarios
Diretorio: `tests/unit`

Objetivo:
- validar logica pura sem depender do banco

O que testar:
- colunas e deduplicacao de produtos
- reproducibilidade de `simulate_sales`
- `sale_id`
- preparacao de DataFrames para dimensao e fato

Rodar:

```powershell
python -m unittest discover -s tests\unit -v
```

## 22. Criar testes de integracao
Diretorio: `tests/integration`

Objetivo:
- validar colaboracao entre ETL e banco real

O que testar:
- schema criado corretamente
- tabelas populadas
- `sale_id` sem duplicidade

Rodar:

```powershell
python -m unittest discover -s tests\integration -v
```

Precondicao:
- banco Docker precisa estar ativo

## 23. Ordem de validacao recomendada
Sempre valide nesta ordem:
1. `py_compile`
2. testes unitarios
3. execucao local do ETL
4. testes de integracao
5. execucao da DAG no Airflow

Comandos:

```powershell
python -m py_compile src\transform.py src\load.py src\main.py airflow\dags\etl_api_dw_dag.py
python -m unittest discover -s tests\unit -v
python src/main.py
python -m unittest discover -s tests\integration -v
docker exec airflow airflow dags trigger etl_api_dw
```

## 24. Troubleshooting
### `empty compose file`
Causa:
- rodar `docker-compose up` fora da pasta esperada ou sem `-f`

Correcao:

```powershell
docker-compose -f docker/docker-compose.yaml up -d
```

### `Expected string or URL object, got None`
Causa:
- `DATABASE_URL` nao carregado

Correcao:
- criar `.env`
- garantir que `database.py` carrega a raiz correta

### `OperationalError`
Causa comum:
- banco nao esta ativo
- porta errada
- conflito com Postgres local

Correcao:
- conferir `docker-compose ps`
- conferir `DATABASE_URL`
- usar a porta publicada correta do host

### Airflow quebra ao subir
Causa comum:
- conflito de dependencias com constraints do Airflow

Correcao:
- usar `Dockerfile.airflow` com `--constraint`
- nao fixar versoes incompatíveis de `SQLAlchemy` ou `pandas`

## 25. Comandos mais importantes
### Ambiente Python
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Docker
```powershell
docker-compose -f docker/docker-compose.yaml up -d postgres
docker-compose -f docker/docker-compose.yaml up --build
docker-compose -f docker/docker-compose.yaml ps
docker-compose -f docker/docker-compose.yaml down
```

### ETL local
```powershell
python src/main.py
```

### Testes
```powershell
python -m unittest discover -s tests\unit -v
python -m unittest discover -s tests\integration -v
```

### Airflow CLI
```powershell
docker exec airflow airflow dags list
docker exec airflow airflow dags unpause etl_api_dw
docker exec airflow airflow dags trigger etl_api_dw
docker exec airflow airflow tasks states-for-dag-run etl_api_dw <dag_run_id>
docker logs airflow
```

## 26. O que estudar em cada arquivo
- `src/extract.py`: integracao com API e validacao HTTP
- `src/transform.py`: logica de negocio e reproducibilidade
- `src/load.py`: modelagem analitica e persistencia
- `src/main.py`: orquestracao local
- `airflow/dags/etl_api_dw_dag.py`: orquestracao operacional
- `docker/docker-compose.yaml`: infraestrutura local
- `docker/Dockerfile.airflow`: imagem customizada do Airflow
- `tests/unit`: regra pura
- `tests/integration`: colaboracao com banco real

## 27. Como replicar este projeto em outro tema
Se voce quiser reaproveitar a mesma arquitetura para outro dataset:
1. troque a fonte no `extract.py`
2. redefina o schema analitico
3. ajuste `transform.py`
4. atualize os helpers do `load.py`
5. adapte a DAG
6. reescreva os testes de unidade e integracao

Essa e a parte mais importante para aprender:
- o formato do pipeline permanece
- o que muda e a regra de negocio e a modelagem
