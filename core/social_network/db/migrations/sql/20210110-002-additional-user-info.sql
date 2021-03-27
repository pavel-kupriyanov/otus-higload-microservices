ALTER TABLE users
    ADD COLUMN age    int NOT NULL,
    ADD COLUMN city   varchar(255),
    ADD COLUMN gender varchar(255);

CREATE TABLE hobbies
(
    id   int          NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

CREATE TABLE users_hobbies_mtm
(
    id       int NOT NULL AUTO_INCREMENT,
    user_id  int NOT NULL,
    hobby_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (hobby_id) REFERENCES hobbies (id) ON DELETE CASCADE,
    UNIQUE one_mtm (user_id, hobby_id)
);

