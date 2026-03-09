-- ==========================================================
-- Modelo estrela simplificado para o projeto ETL
-- dim_product: descreve os produtos
-- dim_date: descreve o calendario
-- fact_sales: registra as vendas (medidas + chaves)
-- ==========================================================

-- Dimensao de produtos (atributos descritivos)
CREATE TABLE dim_product (
    -- Chave natural do produto vinda da fonte.
    product_id INT PRIMARY KEY,
    -- Nome amigavel para análise.
    product_name TEXT,
    -- Segmentação/categoria do produto.
    category TEXT
);

-- Dimensao de datas para analises por ano/mes/dia
CREATE TABLE dim_date (
    -- Chave da dimensão de tempo.
    date DATE PRIMARY KEY,
    -- Partes da data para facilitar agregações.
    year INT,
    month INT,
    day INT
);

-- Tabela fato: cada linha representa uma venda
CREATE TABLE fact_sales (
    -- Chave deterministica da venda, derivada do proprio evento.
    -- Como e baseada no conteudo da linha, ajuda em auditoria e reprocessamento.
    sale_id TEXT PRIMARY KEY,
    -- Relacionamento com produto.
    product_id INT REFERENCES dim_product(product_id),
    -- Relacionamento com dimensão de data.
    date DATE REFERENCES dim_date(date),
    -- Medidas da venda.
    quantity INT,
    total_amount NUMERIC
);
