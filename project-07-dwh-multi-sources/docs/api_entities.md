1. Витрина cdm.dm_courier_ledger:
Витрина предназначена для расчёта вознаграждения курьеров за отчётный период (месяц).

Состав витрины cdm.dm_courier_ledger:
id — идентификатор записи
courier_id — ID курьера
courier_name — Ф. И. О. курьера
settlement_year — год отчёта
settlement_month — месяц отчёта (1–12)
orders_count — количество заказов за месяц
orders_total_sum — общая стоимость заказов
rate_avg — средний рейтинг курьера
order_processing_fee — сумма удержания (orders_total_sum * 0.25)
courier_order_sum — сумма оплаты курьеру за заказы (зависит от рейтинга)
courier_tips_sum — сумма чаевых
courier_reward_sum — итоговая сумма к выплате
courier_reward_sum Вычисляется как courier_order_sum + courier_tips_sum * 0.95 (5% — комиссия за обработку платежа).

Правила расчёта процента выплаты курьеру в зависимости от рейтинга, где r — это средний рейтинг курьера в расчётном месяце:
r < 4 — 5% от заказа, но не менее 100 р.;
4 <= r < 4.5 — 7% от заказа, но не менее 150 р.;
4.5 <= r < 4.9 — 8% от заказа, но не менее 175 р.;
4.9 <= r — 10% от заказа, но не менее 200 р.

Источники данных для витрины:

id — surrogate key (генерируется)
courier_id — dds.dm_couriers.courier_id  
courier_name — dds.dm_couriers.courier_name  
settlement_year — вычисляется из delivery_ts (dds.fct_deliveries.delivery_ts)  
settlement_month — вычисляется из delivery_ts  
orders_count — количество уникальных order_id в dds.fct_deliveries  
orders_total_sum — сумма заказов из:
dds.dm_orders + dds.fct_product_sales  
rate_avg — средний рейтинг из dds.fct_deliveries.rate  
order_processing_fee — вычисляемое поле  
courier_order_sum — вычисляемое поле  
courier_tips_sum — сумма чаевых из dds.fct_deliveries.tip_sum  
courier_reward_sum — вычисляемое поле

2. Список таблиц в слое DDS, необходимые для построения витрины

Для формирования витрины используются следующие таблицы:
Уже существуют в хранилище:
dds.dm_orders — содержит информацию о заказах и их сумме
dds.dm_timestamps — содержит дату/время (для выделения года и месяца)

Нужно создать:
dds.dm_couriers — справочник курьеров
dds.fct_deliveries — факт доставок

Связи между таблицами:
dds.fct_deliveries.order_id → dds.dm_orders.id  
dds.fct_deliveries.courier_id → dds.dm_couriers.courier_id  
dds.fct_deliveries.delivery_ts → dds.dm_timestamps.ts


3. Какие данные необходимо загрузить из API:

Метод GET /restaurants используется для получения списка ресторанов,
которые необходимы для дальнейшей загрузки доставок.
Полученные рестораны используются для получения списка доставок
по каждому ресторану.

Необходимые поля:

_id → restaurant_id  
name → restaurant_name

Метод GET /couriers для таблицы dds.dm_couriers.

Необходимые поля:
_id → courier_id
name → courier_name

Метод GET /deliveries для таблицы dds.fct_deliveries.

Необходимые поля:
delivery_id — идентификатор доставки
order_id — идентификатор заказа (для связи с dds.dm_orders)
courier_id — идентификатор курьера
delivery_ts — дата и время доставки
rate — рейтинг доставки
tip_sum — сумма чаевых

таблицы в stg:
stg.api_restaurants
stg.api_couriers
stg.api_deliveries