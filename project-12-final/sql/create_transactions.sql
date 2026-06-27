CREATE TABLE VT26021862C020__STAGING.transactions (
    operation_id VARCHAR(50),
    account_number_from INT,
    account_number_to INT,
    currency_code INT,
    country VARCHAR(50),
    status VARCHAR(20),
    transaction_type VARCHAR(50),
    amount INT,
    transaction_dt TIMESTAMP
)
ORDER BY transaction_dt, operation_id
SEGMENTED BY HASH(operation_id) ALL NODES;