WITH user_group_log AS (
SELECT
	hg.hk_group_id,
	COUNT(DISTINCT luga.hk_user_id) AS cnt_added_users
FROM
	VT26021862C020__DWH.s_auth_history AS sah
JOIN VT26021862C020__DWH.l_user_group_activity AS luga
        ON
	sah.hk_l_user_group_activity = luga.hk_l_user_group_activity
JOIN VT26021862C020__DWH.h_groups AS hg
        ON
	luga.hk_group_id = hg.hk_group_id
WHERE
	sah.event = 'add'
	AND hg.hk_group_id IN (
	SELECT
		hk_group_id
	FROM
		VT26021862C020__DWH.h_groups
	ORDER BY
		registration_dt
	LIMIT 10
      )
GROUP BY
	hg.hk_group_id
), 
user_group_messages AS (
SELECT
	lgd.hk_group_id,
	COUNT(DISTINCT lum.hk_user_id) AS cnt_users_in_group_with_messages
FROM
	VT26021862C020__DWH.l_groups_dialogs AS lgd
JOIN VT26021862C020__DWH.l_user_message AS lum
        ON
	lgd.hk_message_id = lum.hk_message_id
WHERE
	lgd.hk_group_id IN (
	SELECT
		hk_group_id
	FROM
		VT26021862C020__DWH.h_groups
	ORDER BY
		registration_dt
	LIMIT 10
      )
GROUP BY
	lgd.hk_group_id
)
SELECT
	ugl.hk_group_id,
	ugl.cnt_added_users,
	COALESCE(ugm.cnt_users_in_group_with_messages, 0) AS cnt_users_in_group_with_messages,
	COALESCE(ugm.cnt_users_in_group_with_messages, 0)::decimal / ugl.cnt_added_users AS group_conversion
FROM
	user_group_log AS ugl
LEFT JOIN user_group_messages AS ugm
    ON
	ugl.hk_group_id = ugm.hk_group_id
ORDER BY
	group_conversion DESC;