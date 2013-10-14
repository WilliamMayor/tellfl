CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT
);
CREATE TABLE IF NOT EXISTS history (
    user INT,
    station_from TEXT,
    station_to TEXT,
    time_in INT,
    time_out INT,
    cost INT,
    FOREIGN KEY (user) REFERENCES users(id)
);