CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT
);
CREATE TABLE IF NOT EXISTS journeys (
    user INTEGER,
    station_from TEXT,
    station_to TEXT,
    time_in INTEGER,
    time_out INTEGER,
    cost INTEGER,
    FOREIGN KEY (user) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS payments (
    user INTEGER,
    amount INTEGER,
    time INTEGER,
    FOREIGN KEY (user) REFERENCES users(id)
);