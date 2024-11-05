
CREATE TABLE potions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    red INT DEFAULT 0,
    green INT DEFAULT 0,
    blue INT DEFAULT 0,
    dark INT DEFAULT 0,
    inventory INT DEFAULT 0,
    price INT NOT NULL,
    description TEXT
);


CREATE TABLE ledger (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL,
    change INT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    description TEXT,
    transaction_id INT
);


CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    customer_id INT,
    status VARCHAR(20) DEFAULT 'open' -- e.g., open, completed, canceled
);


CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INT REFERENCES carts(id) ON DELETE CASCADE,
    potion_id INT REFERENCES potions(id),
    quantity INT DEFAULT 1,
    price INT NOT NULL
);

