DROP TABLE if exists urls CASCADE;

CREATE TABLE urls(
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at DATE
);