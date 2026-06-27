-- Открываю транзакцию
BEGIN;

-- Явно блокирую таблицу для любых изменений
LOCK TABLE cafe.managers IN ACCESS EXCLUSIVE MODE;

-- Добавляю новое поле для массива с телефонами (и новые и старые)
ALTER TABLE cafe.managers ADD COLUMN phone_numbers text[];

-- CTE для нового номера телефона по алфавиту
WITH numbered AS (
    SELECT
        manager_uuid,
        ROW_NUMBER() OVER (ORDER BY name) + 99 AS order_number -- порядковый номер начиная с 100
    FROM cafe.managers
)
-- Обновляю массив phone_numbers с новым и старым телефонами
UPDATE cafe.managers m
SET phone_numbers = ARRAY[
    CONCAT('8-800-2500-', n.order_number), -- новый телефон
    m.phone                                -- старый телефон
]
FROM numbered n
WHERE m.manager_uuid = n.manager_uuid;

-- Удаляю старое поле phone
ALTER TABLE cafe.managers DROP COLUMN phone;

-- Завершаю транзакцию
COMMIT;