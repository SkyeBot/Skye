CREATE TABLE IF NOT EXISTS levelling_config (
    guild_id BIGINT PRIMARY KEY
        REFERENCES guilds(guild_id)
            ON DELETE CASCADE,
    announce_channel BIGINT,
    xp_modifier FLOAT NOT NULL DEFAULT 1.0,
    blacklisted_roles BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    blacklisted_channels BIGINT[] NOT NULL DEFAULT ARRAY[]::BIGINT[],
    card_background BYTEA,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    levelup_messages TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[]
);



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