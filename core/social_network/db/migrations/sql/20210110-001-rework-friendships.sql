DROP TABLE friendships;
CREATE TABLE friendships
(
    id        int NOT NULL AUTO_INCREMENT,
    user_id   int NOT NULL,
    friend_id int NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE friendship_unique (user_id, friend_id)
)
