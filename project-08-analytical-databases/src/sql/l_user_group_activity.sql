DROP TABLE IF EXISTS VT26021862C020__DWH.l_user_group_activity;

CREATE TABLE VT26021862C020__DWH.l_user_group_activity
(
    hk_l_user_group_activity bigint PRIMARY KEY,
    hk_user_id bigint NOT NULL 
        CONSTRAINT fk_l_user_group_activity_user 
        REFERENCES VT26021862C020__DWH.h_users (hk_user_id),
    hk_group_id bigint NOT NULL 
        CONSTRAINT fk_l_user_group_activity_group 
        REFERENCES VT26021862C020__DWH.h_groups (hk_group_id),
    load_dt datetime,
    load_src varchar(20)
)
ORDER BY
load_dt
SEGMENTED BY hk_user_id ALL nodes
PARTITION BY load_dt::date
GROUP BY
calendar_hierarchy_day(load_dt::date, 3, 2);