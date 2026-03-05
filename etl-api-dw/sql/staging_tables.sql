CREATE TABLE IF NOT EXISTS stg_products (
    id INT,
    title TEXT,
    price NUMERIC,
    category TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);