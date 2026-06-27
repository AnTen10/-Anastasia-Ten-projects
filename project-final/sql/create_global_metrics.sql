CREATE TABLE VT26021862C020__DWH.global_metrics (
    date_update DATE,
    currency_from INT,
    amount_total NUMERIC(18,2),
    cnt_transactions INT,
    avg_transactions_per_account NUMERIC(18,2),
    cnt_accounts_make_transactions INT
)
ORDER BY date_update, currency_from
SEGMENTED BY HASH(date_update, currency_from) ALL NODES;