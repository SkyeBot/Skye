CREATE TABLE IF NOT EXISTS avatars(
    user_id BIGINT NOT NULL,
    time_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    avatar BYTEA NOT NULL

)

CREATE TABLE IF NOT EXISTS warn(
    warns BIGINT,
    member_id BIGINT,
    guild_id BIGINT
)