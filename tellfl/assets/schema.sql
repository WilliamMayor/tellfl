DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS journeys;
DROP TABLE IF EXISTS payments;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    UNIQUE(username) ON CONFLICT FAIL
);
CREATE TABLE journeys (
    user INTEGER,
    station_from TEXT,
    station_to TEXT,
    time_in INTEGER,
    time_out INTEGER,
    cost INTEGER,
    UNIQUE(user, time_in) ON CONFLICT IGNORE,
    FOREIGN KEY (user) REFERENCES users(id)
);
CREATE TABLE payments (
    user INTEGER,
    amount INTEGER,
    time INTEGER,
    UNIQUE(user, time) ON CONFLICT IGNORE,
    FOREIGN KEY (user) REFERENCES users(id)
);