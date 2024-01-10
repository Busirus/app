CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT false
);

CREATE TABLE post (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    image_path VARCHAR(128),
    ip_address VARCHAR(15),
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES user(id)
);

CREATE TABLE reply (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    post_id INTEGER REFERENCES post(id),
    user_id INTEGER REFERENCES user(id)
);

INSERT INTO user (username, password_hash, is_admin)
VALUES ('busirus', 'your_hashed_password_here', true);
