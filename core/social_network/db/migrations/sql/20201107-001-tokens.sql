CREATE TABLE access_tokens (
    id int NOT NULL AUTO_INCREMENT,
    value varchar (255) NOT NULL UNIQUE,
    user_id int NOT NULL,
    expired_at timestamp NOT NULL ,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
