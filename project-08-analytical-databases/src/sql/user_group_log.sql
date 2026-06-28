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
)
SELECT
	hk_group_id,
	cnt_added_users
FROM
	user_group_log
ORDER BY
	cnt_added_users DESC
LIMIT 10;