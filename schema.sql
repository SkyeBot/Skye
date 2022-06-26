CREATE TABLE tags_new (
    id SERIAL UNIQUE,
    name TEXT NOT NULL CHECK (char_length(name) <= 32),
    PRIMARY KEY (name),
    content TEXT NOT NULL CHECK (char_length(content) <= 2000),
    owner BIGINT NOT NULL,
    uses INT DEFAULT 0,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);
CREATE TABLE tag_lookup (
    name TEXT PRIMARY KEY CHECK (char_length(name) <= 32),
    tagId INT NOT NULL REFERENCES tags_new(id),
    isAlias BOOLEAN NOT NULL
);

CREATE FUNCTION isTagOwner(tagID_ INTEGER, requester BIGINT)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    AS
    $$
    BEGIN
        IF ((
            SELECT 1
                FROM tags_new
                WHERE
                    owner = requester AND id = tagID_
            ) IS NULL
        )
        THEN RETURN FALSE;
        END IF;
        RETURN TRUE;
    END
    $$;

CREATE FUNCTION findTag(givenName TEXT, guild_id BIGINT)
    RETURNS TEXT[] -- [name, content]
    LANGUAGE plpgsql
    AS
    $$

    DECLARE
        tagID_ INT;
        tagName TEXT;
        tagContent TEXT;
        tagGuild_id BIGINT;
        tagAlias BOOLEAN
    BEGIN
        SELECT tagId, isAlias
            INTO tagID_, tagAlias
            FROM tag_lookup
            WHERE name = givenName AND guild_id = guildID;

        IF tagID_ IS NULL
            THEN RETURN NULL;
        END IF;

       IF tagAlias IS TRUE
            THEN SELECT 

        UPDATE tags_new
            SET uses = uses + 1
            WHERE id = tagID_
            RETURNING name, content
                INTO tagName, tagContent;

        RETURN ARRAY[tagName, tagContent];
    END



CREATE FUNCTION createTag (tag_name TEXT, tag_content TEXT, tag_owner BIGINT, tag_guild_id BIGINT)
    RETURNS INT
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        tagID_ INT;
    BEGIN
        INSERT INTO
            tags_new (name, content, owner, guildId)
            VALUES (tag_name, tag_content, tag_owner, tag_guild_id)
            RETURNING id INTO tagID_;
        INSERT INTO
            tag_lookup (name, tagId, isAlias, guildId)
            VALUES (tag_name, tagID_, FALSE, tag_guild_id);
        RETURN tagID_;
    END
    $$;

CREATE FUNCTION createAlias (originalTag TEXT, aliasName TEXT)
    RETURNS TEXT
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        tagID_ INT;
        tagName TEXT;
    BEGIN
        SELECT
            tagId, name
            INTO tagID_, tagName
            FROM tag_lookup
            WHERE name = originalTag;

        IF (tagID_ IS NULL)
            THEN RETURN 'Tag does not exist';
        END IF;

        INSERT INTO
            tag_lookup (name, tagId, isAlias)
            VALUES (aliasName, tagID_, TRUE);

        RETURN concat('Created alias ', aliasName, ' that points to ', tagName);
    END
    $$;

CREATE FUNCTION deleteTag (tagName TEXT, requester BIGINT)
    RETURNS TEXT
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        tagID_ INT;
        isAlias_ BOOLEAN;
    BEGIN
        SELECT
            tagId, isAlias
            INTO tagID_, isAlias_
            FROM tag_lookup
            WHERE name = tagName;

        IF (tagID_ IS NULL)
        THEN RETURN 'This tag does not exist';
        END IF;

        IF (isTagOwner(tagID_, requester) IS FALSE)
        THEN RETURN 'You do not own this tag';
        END IF;

        IF (isAlias_ IS FALSE)
            THEN
                DELETE FROM tag_lookup WHERE tagId = tagID_;
                DELETE FROM tags_new WHERE id = tagID_;
                RETURN 'Tag deleted';
        END IF;
        IF (isAlias_ IS TRUE)
            THEN
                DELETE FROM tag_lookup WHERE name = tagName;
                RETURN 'Tag alias deleted';
        END IF;
    END
    $$;


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