BEGIN;

SELECT restaurant_uuid
FROM cafe.restaurants
WHERE type = 'coffee_shop'
  AND menu ? 'Кофе'
  AND menu -> 'Кофе' ? 'Капучино'
FOR UPDATE;

UPDATE cafe.restaurants
SET menu = jsonb_set(
    menu,
    '{Кофе,Капучино}',
    ((menu -> 'Кофе' ->> 'Капучино')::numeric * 1.2)::text::jsonb
)
WHERE type = 'coffee_shop'
  AND menu ? 'Кофе'
  AND menu -> 'Кофе' ? 'Капучино';

COMMIT;