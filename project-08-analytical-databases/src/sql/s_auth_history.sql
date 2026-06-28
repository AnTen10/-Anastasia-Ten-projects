DROP TABLE IF EXISTS VT26021862C020__DWH.s_auth_history;

CREATE TABLE VT26021862C020__DWH.s_auth_history
(
    hk_l_user_group_activity bigint NOT NULL,
    user_id_from int,
    event varchar(20),
    event_dt timestamp,
    load_dt datetime,
    load_src varchar(20)
)
ORDER BY
event_dt
segmented BY hk_l_user_group_activity ALL nodes
PARTITION BY event_dt::date
GROUP BY
calendar_hierarchy_day(event_dt::date, 3, 2);