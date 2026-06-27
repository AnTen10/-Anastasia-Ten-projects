SELECT
    r.name AS restaurant_name,
    (count(rm.manager_uuid) - 1) AS manager_changes
FROM cafe.restaurant_manager_work_dates rm
JOIN cafe.restaurants r ON rm.restaurant_uuid = r.restaurant_uuid
GROUP BY r.name
ORDER BY manager_changes DESC
LIMIT 3;