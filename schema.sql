CREATE ROLE IF NOT EXISTS skye WITH LOGIN PASSWORD 'your_password';
CREATE DATABASE IF NOT EXISTS skye OWNER skye;
CREATE EXTENSION IS NOT EXISTS pg_tgrm;

CREATE TABLE IF NOT EXISTS prefix(
    prefix TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    channel_id BIGINT
);

CREATE TABLE IF NOT EXISTS autorole (
    guild BIGINT,
    role BIGINT
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name TEXT content TEXT,
    owner_id BIGINT,
    uses INTEGER DEFAULT 0,
    location_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() AT TIME ZONE 'utc'
);

CREATE TABLE IF NOT EXISTS Enabled(
    command TEXT,
    guild_id BIGINT
)