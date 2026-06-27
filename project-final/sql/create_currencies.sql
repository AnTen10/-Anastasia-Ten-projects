CREATE TABLE VT26021862C020__STAGING.currencies (
    date_update TIMESTAMP,
    currency_code INT,
    currency_code_with INT,
    currency_with_div NUMERIC(10,5)
)
ORDER BY date_update, currency_code
SEGMENTED BY HASH(currency_code) ALL NODES;