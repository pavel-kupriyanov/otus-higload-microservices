DROP TABLE friendships;
CREATE TABLE friendships
(
    id       int NOT NULL AUTO_INCREMENT,
    user_id1 int NOT NULL,
    user_id2 int NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id1) REFERENCES users (id),
    FOREIGN KEY (user_id2) REFERENCES users (id)
);
