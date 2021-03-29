CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT,
    email varchar (255) NOT NULL,
    password varchar (255) NOT NULL,
    first_name varchar(255) NOT NULL,
    last_name varchar(255),
    PRIMARY KEY (id)
);
