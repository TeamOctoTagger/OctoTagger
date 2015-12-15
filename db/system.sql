CREATE TABLE gallery (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT
);

CREATE TABLE settings (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    use_softlink BOOLEAN,
    current_db INTEGER REFERENCES gallery(pk_id)
);

INSERT INTO gallery(name, location) VALUES ('default', '.');
INSERT INTO settings(use_softlink, current_db) VALUES (1, 1);

