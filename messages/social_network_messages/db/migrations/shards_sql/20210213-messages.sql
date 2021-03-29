CREATE TABLE messages
(
    id        varchar(36)  NOT NULL,
    chat_key  varchar(255) NOT NULL,
    author_id int          NOT NULL,
    text      TEXT         NOT NULL,
    created   timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX chat (chat_key, created)
)
