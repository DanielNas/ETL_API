-- ==========================================================
-- Modelo estrela simplificado para o projeto ETL
-- dim_product: descreve os produtos
-- dim_date: descreve o calendario
-- fact_sales: registra as vendas (medidas + chaves)
-- ==========================================================

-- Dimensao de produtos (atributos descritivos)
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name TEXT,
    category TEXT
);

-- Dimensao de datas para analises por ano/mes/dia
CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT
);

-- Tabela fato: cada linha representa uma venda
CREATE TABLE fact_sales (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES dim_product(product_id),
    date DATE REFERENCES dim_date(date),
    quantity INT,
    total_amount NUMERIC
);
