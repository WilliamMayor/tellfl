DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS journeys;
DROP TABLE IF EXISTS payments;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT
);
CREATE TABLE journeys (
    user INTEGER,
    station_from TEXT,
    station_to TEXT,
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