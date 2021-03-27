ALTER TABLE friend_requests
    ADD UNIQUE only_one_request (from_user, to_user);
