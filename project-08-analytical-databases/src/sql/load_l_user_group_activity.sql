INSERT
	INTO
	VT26021862C020__DWH.l_user_group_activity
(hk_l_user_group_activity,
	hk_user_id,
	hk_group_id,
	load_dt,
	load_src)

SELECT
	DISTINCT
       hash(hu.hk_user_id, hg.hk_group_id) AS hk_l_user_group_activity,
	hu.hk_user_id,
	hg.hk_group_id,
	now() AS load_dt,
	's3' AS load_src
FROM
	VT26021862C020__STAGING.group_log AS gl
LEFT JOIN VT26021862C020__DWH.h_users AS hu
       ON
	gl.user_id = hu.user_id
LEFT JOIN VT26021862C020__DWH.h_groups AS hg
       ON
	gl.group_id = hg.group_id
WHERE
	hu.hk_user_id IS NOT NULL
	AND hg.hk_group_id IS NOT NULL
	AND hash(hu.hk_user_id, hg.hk_group_id) NOT IN
      (
	SELECT
		hk_l_user_group_activity
	FROM
		VT26021862C020__DWH.l_user_group_activity);