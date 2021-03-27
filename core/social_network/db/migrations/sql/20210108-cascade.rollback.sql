ALTER TABLE access_tokens
    DROP FOREIGN KEY access_tokens_ibfk_1;
ALTER TABLE access_tokens
    ADD CONSTRAINT access_tokens_ibfk_1
        FOREIGN KEY (user_id)
            REFERENCES users (id);

ALTER TABLE friend_requests
    DROP FOREIGN KEY friend_requests_ibfk_1;
ALTER TABLE friend_requests
    DROP FOREIGN KEY friend_requests_ibfk_2;
ALTER TABLE friend_requests
    ADD CONSTRAINT friend_requests_ibfk_1
        FOREIGN KEY (from_user)
            REFERENCES users (id);
ALTER TABLE friend_requests
    ADD CONSTRAINT friend_requests_ibfk_2
        FOREIGN KEY (to_user)
            REFERENCES users (id);


ALTER TABLE friendships
    DROP FOREIGN KEY friendships_ibfk_1;
ALTER TABLE friendships
    DROP FOREIGN KEY friendships_ibfk_2;
ALTER TABLE friendships
    ADD CONSTRAINT friendships_ibfk_1
        FOREIGN KEY (user_id1)
            REFERENCES users (id);
ALTER TABLE friendships
    ADD CONSTRAINT friendships_ibfk_2
        FOREIGN KEY (user_id2)
            REFERENCES users (id);
