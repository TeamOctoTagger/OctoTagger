import sqlite3
import os
import shutil

SQL_PATH = os.path.dirname(__file__)
DEFAULT_GALLERY_PATH = os.path.expanduser("~/OctoTagger")


def update_system():
    conn = sqlite3.connect("system.db")
    query_path = os.path.join(SQL_PATH, "system.sql")
    with open(query_path, "r") as f:
        query = f.read()

    conn.executescript(query)
    conn.commit()
    conn.close()


def update_gallery():
    os.makedirs("default/files")
    os.makedirs("default/thumbnails/temp")
    if not os.path.isdir(DEFAULT_GALLERY_PATH + "/default"):
        os.makedirs(DEFAULT_GALLERY_PATH + "/default")

    conn = sqlite3.connect("default/default.db")
    query_path = os.path.join(SQL_PATH, "gallery.sql")
    with open(query_path, "r") as f:
        query = f.read()

    conn.executescript(query)
    conn.commit()
    conn.close()

    # Copy db file to db folder
    source = os.path.normpath("default/default.db")
    dest = os.path.join(SQL_PATH, "default.db")
    shutil.copy(source, dest)

    # Insert default gallery output folder
    gallery_db = sqlite3.connect("default/default.db")
    gallery_db.execute(
        (
            "INSERT INTO gallery_folder "
            "(name, location, add_new_tag, use_softlink) "
            "VALUES (:name, :location, :add_new_tag, :use_softlink)"
        ),
        {
            "name": "default",
            "location": DEFAULT_GALLERY_PATH,
            "add_new_tag": True,
            "use_softlink": True
        }
    )
    gallery_db.commit()


if __name__ == '__main__':
    if os.path.isfile("system.db"):
        print("system.db already exists!")
        print("If you want to generate a new one delete it")
    else:
        update_system()

    if os.path.isdir("default"):
        print("default/ gallery already exists!")
        print("If you want to generate a new one delete it")
    else:
        update_gallery()
