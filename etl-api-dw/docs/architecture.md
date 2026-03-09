# Arquitetura Tecnica

## Visao Geral
Este projeto implementa um pipeline ETL didatico usando:
- Python para logica de negocio e manipulacao de dados
- PostgreSQL como banco analitico
- Docker para empacotar infraestrutura
- Apache Airflow para orquestracao

O objetivo da arquitetura e mostrar um fluxo que seja simples o suficiente para estudo e, ao mesmo tempo, proximo do que se faz em projetos reais.

## Stack Utilizada
- Linguagem: Python 3.11
- Manipulacao de dados: `pandas`
- Acesso ao banco: `SQLAlchemy` + `psycopg2`
- Configuracao: `python-dotenv`
- Banco analitico: PostgreSQL 15
- Orquestracao: Apache Airflow 2.10
- Infraestrutura local: Docker Compose
- Testes: `unittest`

## Camadas do Projeto
### 1. Extract
Arquivo: `src/extract.py`

Responsabilidade:
- chamar a API de origem;
- validar o retorno HTTP;
- entregar dados brutos em estrutura Python.

Raciocinio:
- a extração nao deve conhecer regra analitica;
- ela apenas coleta e entrega materia-prima para as proximas etapas.

### 2. Transform
Arquivo: `src/transform.py`

Responsabilidade:
- padronizar o catalogo de produtos;
- gerar um conjunto sintetico de vendas para estudo;
- criar `sale_id` deterministico.

Raciocinio:
- `transform_products()` reduz o dataset para o schema minimo necessario;
- `simulate_sales()` cria eventos de venda reproduziveis;
- `generate_sale_id()` transforma uma venda em uma chave estavel de negocio.

Por que `sale_id` deterministico importa:
- permite rerun sem perder rastreabilidade;
- ajuda a auditar a origem de cada linha da fato;
- aproxima o projeto de tecnicas de idempotencia usadas em producao.

### 3. Load
Arquivo: `src/load.py`

Responsabilidade:
- garantir que o schema do DW exista;
- transformar DataFrames no formato final de dimensao e fato;
- gravar staging, dimensoes e fatos.

Componentes importantes:
- `ensure_warehouse_schema()`: cria ou corrige tabelas
- `reset_warehouse_tables()`: limpa a camada analitica para rerun consistente
- `_prepare_dim_product_df()`: modela a dimensao de produto
- `_prepare_dim_date_df()`: modela a dimensao de data
- `_prepare_fact_sales_df()`: monta a fato final

### 4. Orquestracao Local
Arquivo: `src/main.py`

Responsabilidade:
- encadear o pipeline fora do Airflow;
- servir como caminho simples para executar e validar o ETL.

Ordem:
1. valida conexao com banco
2. extrai produtos
3. transforma produtos
4. simula vendas
5. carrega staging
6. limpa DW
7. carrega `dim_product`
8. carrega `dim_date`
9. carrega `fact_sales`

### 5. Orquestracao com Airflow
Arquivo: `airflow/dags/etl_api_dw_dag.py`

Responsabilidade:
- representar o pipeline como tarefas observaveis;
- permitir monitoramento, retries e rerun controlado.

Organizacao com `TaskGroup`:
- `prepare`
- `extract_transform`
- `load`

Isso melhora a leitura da DAG e ensina a separar etapas por dominio logico.

## Modelagem Analitica
### stg_products
Camada de staging.

Objetivo:
- guardar um snapshot do catalogo tratado da ultima execucao;
- facilitar auditoria da fonte antes da modelagem dimensional.

### dim_product
Tabela de dimensao.

Objetivo:
- armazenar atributos descritivos do produto;
- separar contexto do evento de venda.

Chave:
- `product_id`

### dim_date
Tabela de dimensao de tempo.

Objetivo:
- permitir agregacoes por dia, mes e ano;
- evitar derivacao repetida de partes da data em consultas.

Chave:
- `date`

### fact_sales
Tabela fato.

Objetivo:
- armazenar o evento analitico central do projeto: a venda.

Colunas principais:
- `sale_id`
- `product_id`
- `date`
- `quantity`
- `total_amount`

## Idempotencia
Este projeto foi ajustado para reruns previsiveis.

Como funciona:
- `stg_products` representa snapshot da ultima extração
- `reset_warehouse_tables()` limpa a camada analitica
- `simulate_sales()` usa `seed`
- `sale_id` e deterministico

Consequencia:
- rerodar o pipeline nao infla `fact_sales`
- a contagem final permanece consistente

## Testes
### Testes Unitarios
Diretorio: `tests/unit`

Validam:
- transformacao de produtos
- reproducibilidade da simulacao
- `sale_id`
- preparacao de `dim_product`, `dim_date` e `fact_sales`

### Testes de Integracao
Diretorio: `tests/integration`

Validam:
- criacao do schema no banco real
- carga do pipeline nas tabelas reais
- unicidade pratica de `sale_id`

## Infraestrutura
### Docker Compose
Arquivo: `docker/docker-compose.yaml`

Servicos:
- `postgres`
- `airflow`

Motivos da configuracao:
- `postgres_data`: persiste dados do banco entre recriacoes
- `airflow_home`: persiste estado do Airflow
- `healthcheck` no Postgres: evita subir o Airflow antes do banco estar pronto

### Dockerfile do Airflow
Arquivo: `docker/Dockerfile.airflow`

Ponto importante:
- o Airflow precisa respeitar seu arquivo oficial de constraints;
- por isso o container instala dependencias usando `--constraint`.

Sem isso, conflitos de versao com `SQLAlchemy` e `pandas` quebram o Airflow.
