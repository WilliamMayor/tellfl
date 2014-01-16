DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS journeys;
DROP TABLE IF EXISTS payments;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    UNIQUE(username) ON CONFLICT FAIL,
    UNIQUE(email) ON CONFLICT FAIL
);
CREATE TABLE journeys (
    user INTEGER,
    station_in TEXT,
    station_out TEXT,
    time_in INTEGER,
    time_out INTEGER,
    cost INTEGER,
    FOREIGN KEY (user) REFERENCES users(id)
);
CREATE TABLE payments (
    user INTEGER,
    amount INTEGER,
    time INTEGER,
    FOREIGN KEY (user) REFERENCES users(id)
);