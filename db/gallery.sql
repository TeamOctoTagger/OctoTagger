CREATE TABLE tag (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text UNIQUE ON CONFLICT ABORT,
    is_numeric BOOLEAN
);

-- TODO rename in accordance to gallery_folder
CREATE TABLE folder (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT,
    expression TEXT,
    use_softlink BOOLEAN
);

CREATE TABLE gallery_folder (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT,
    add_new_tag BOOLEAN,
    use_softlink BOOLEAN
);

CREATE TABLE gallery_folder_has_tag (
    pk_fk_gallery_folder_id INTEGER REFERENCES gallery_folder(pk_id),
    pk_fk_tag_id INTEGER REFERENCES tag(pk_id)
);

CREATE TABLE file (
    pk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE ON CONFLICT ABORT,
    file_name TEXT
);

CREATE TABLE file_has_tag (
    pk_fk_file_id INTEGER REFERENCES file(pk_id),
    pk_fk_tag_id INTEGER REFERENCES tags(pk_id),
    amount INTEGER
);

