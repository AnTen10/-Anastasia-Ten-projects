DROP TABLE IF EXISTS VT26021862C020__STAGING.group_log CASCADE;

CREATE TABLE VT26021862C020__STAGING.group_log
(
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    user_id_from INT,
    event VARCHAR(20),
    event_dt TIMESTAMP
)
ORDER BY
group_id,
user_id
SEGMENTED BY HASH(group_id) ALL NODES
PARTITION BY event_dt::date
GROUP BY
calendar_hierarchy_day(event_dt::date, 3, 2);