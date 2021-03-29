CREATE TABLE friendships
(
    id       int NOT NULL AUTO_INCREMENT,
    user_id1 int NOT NULL,
    user_id2 int NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id1) REFERENCES users (id),
    FOREIGN KEY (user_id2) REFERENCES users (id)
);

CREATE TABLE friend_requests
(
    id        int          NOT NULL AUTO_INCREMENT,
    from_user int          NOT NULL,
    to_user   int          NOT NULL,
    status    varchar(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (from_user) REFERENCES users (id),
    FOREIGN KEY (to_user) REFERENCES users (id)
)
