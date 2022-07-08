INSERT INTO osu_user (osu_username, user_id) VALUES(12, 12)
ON CONFLICT(osu_username) DO 
UPDATE SET osu_username = excluded.osu_username