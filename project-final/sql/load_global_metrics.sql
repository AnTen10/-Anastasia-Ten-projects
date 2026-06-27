INSERT INTO VT26021862C020__DWH.global_metrics
SELECT
    DATE(t.transaction_dt) AS date_update,
    t.currency_code AS currency_from,

    SUM(t.amount * c.currency_with_div) AS amount_total,
    COUNT(*) AS cnt_transactions,

    COUNT(*)::FLOAT / COUNT(DISTINCT t.account_number_from) AS avg_transactions_per_account,

    COUNT(DISTINCT t.account_number_from) AS cnt_accounts_make_transactions

FROM VT26021862C020__STAGING.transactions t
JOIN VT26021862C020__STAGING.currencies c
    ON t.currency_code = c.currency_code
   AND DATE(t.transaction_dt) = DATE(c.date_update)

WHERE DATE(t.transaction_dt) = '{{ ds }}'
  AND t.status = 'done'
  AND t.account_number_from > 0

GROUP BY
    DATE(t.transaction_dt),
    t.currency_code;