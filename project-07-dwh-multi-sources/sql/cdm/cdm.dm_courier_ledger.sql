CREATE TABLE cdm.dm_courier_ledger (
	id serial4 NOT NULL,
	courier_id text NOT NULL,
	courier_name text NOT NULL,
	settlement_year int4 NOT NULL,
	settlement_month int4 NOT NULL,
	orders_count int4 NOT NULL,
	orders_total_sum numeric(14, 2) NOT NULL,
	rate_avg numeric(3, 2) NULL,
	order_processing_fee numeric(14, 2) NOT NULL,
	courier_order_sum numeric(14, 2) NOT NULL,
	courier_tips_sum numeric(14, 2) NOT NULL,
	courier_reward_sum numeric(14, 2) NOT NULL,
	CONSTRAINT dm_courier_ledger_courier_id_settlement_year_settlement_mon_key UNIQUE (courier_id, settlement_year, settlement_month),
	CONSTRAINT dm_courier_ledger_pkey PRIMARY KEY (id)
);