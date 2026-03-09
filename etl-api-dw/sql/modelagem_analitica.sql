SELECT * FROM dim_product

SELECT * FROM fact_sales


SELECT id,title,price,category FROM stg_products;

SELECT SUM(quantity) as total_itens,
    SUM(total_amount) as total_valor
FROM fact_sales
--GROUP BY "date"

-- Validção de atualização
SELECT MAX(c) FROM fact_sales