-- Camada de staging:
-- recebe os dados quase "como vieram" da fonte, com pouca transformação.
CREATE TABLE IF NOT EXISTS stg_products (
    -- ID original do produto na fonte.
    id INT,
    -- Nome original do produto.
    title TEXT,
    -- Preço capturado no momento da extração.
    price NUMERIC,
    -- Categoria informada pela fonte.
    category TEXT,
    -- Carimbo de quando o registro entrou na staging.
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
