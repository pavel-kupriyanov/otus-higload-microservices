CREATE TABLE news
(
    id        varchar(36)  NOT NULL,
    author_id int          NOT NULL,
    type      varchar(255) NOT NULL,
    payload   JSON,
    created   timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX author_id(author_id),
    INDEX created(created)
);
