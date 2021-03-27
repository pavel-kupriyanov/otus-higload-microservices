CREATE TABLE database_info
(
    id       int          NOT NULL AUTO_INCREMENT,
    host     varchar(255) NOT NULL,
    port     int          NOT NULL,
    user     varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    name     varchar(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE shards_info
(
    id          int          NOT NULL AUTO_INCREMENT,
    db_info     int          NOT NULL,
    shard_table varchar(255) NOT NULL,
    shard_key   int          NOT NULL,
    state       varchar(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (db_info) REFERENCES database_info (id),
    UNIQUE unique_key_per_table (shard_table, shard_key)
)
