CREATE TABLE gallery (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT
);

CREATE TABLE settings (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    default_gallery_path TEXT,
    default_folder_path TEXT,
    use_softlink BOOLEAN,
    import_copy BOOLEAN,
    use_dark_theme BOOLEAN,
    current_db INTEGER REFERENCES gallery(pk_id)
);

INSERT INTO gallery(name, location) VALUES ('default', '.');
INSERT INTO settings(default_gallery_path, default_folder_path, use_softlink, import_copy, use_dark_theme, current_db) VALUES ('.', '', 1, 1, 1, 1);
