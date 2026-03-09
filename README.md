# ETL API DW

Projeto de estudo em Engenharia de Dados com foco em pipeline ETL (Extract, Transform, Load) aplicado a dados de produtos e vendas.

## Visão Geral
O projeto demonstra, de forma prática, como:
- extrair dados de uma fonte externa;
- transformar e padronizar esses dados para análise;
- carregar o resultado em um modelo analítico com tabelas de staging, dimensão e fato.

## Objetivo
Consolidar fundamentos de ETL e modelagem analítica, praticando:
1. integração com fonte de dados;
2. limpeza e estruturação tabular;
3. persistência em banco relacional para análises.

## Arquitetura do Pipeline
1. **Extract**: coleta dados brutos.
2. **Transform**: seleciona campos relevantes, remove inconsistências e gera dados analíticos de apoio.
3. **Load**: grava os dados nas camadas do Data Warehouse.
4. **Orquestração**: o Airflow coordena a execução das etapas e organiza o pipeline em tarefas independentes.

## Modelagem de Dados
O projeto utiliza uma estrutura simplificada de DW:
- **Staging**: armazenamento inicial dos dados coletados.
- **Dimensão de Produto**: atributos descritivos de produto.
- **Fato de Vendas**: eventos transacionais com métricas de negócio.
- **Dimensão de Data** (estrutura prevista): apoio a análises temporais.

## Organização do Código
```text
etl-api-dw/
  docker/      # infraestrutura do banco para desenvolvimento
  sql/         # scripts de modelagem
  src/         # código-fonte do pipeline ETL
    config/    # configuração de conexão
    utils/     # utilitários (ex.: logging)
```

## Tecnologias
- Python
- Pandas
- SQLAlchemy
- PostgreSQL
- Docker
- Apache Airflow

## Resultado Esperado
Ao final da execução do pipeline, os dados extraídos e transformados ficam disponíveis em estruturas analíticas, permitindo consultas e criação de indicadores.

## Orquestracao com Airflow
O projeto tambem pode ser executado com Airflow para representar um fluxo de dados mais proximo de ambientes reais de engenharia de dados.

Na DAG do projeto, o pipeline foi dividido em tarefas independentes:
- validacao de conexao com o banco;
- extracao dos dados;
- transformacao dos dados;
- carga da staging;
- carga da dimensao de produtos;
- carga da fato de vendas.

Essa separacao ajuda no estudo de:
- dependencias entre tarefas;
- monitoramento de execucao;
- reprocessamento de partes especificas do pipeline;
- observabilidade da rotina ETL.

## Documentacao Tecnica
Documentacao detalhada para estudo e replicacao:
- `etl-api-dw/docs/architecture.md`
- `etl-api-dw/docs/replication-guide.md`

## Evolução do Projeto
Próximas melhorias previstas:
- automatizar carga da dimensão de datas;
- ampliar validações de qualidade de dados;
- adicionar testes automatizados para cada etapa do ETL;
- evoluir versionamento de schema e deploy.
