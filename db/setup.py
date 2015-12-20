import sqlite3
import os
import shutil

SQL_PATH = os.path.dirname(__file__)


def update_system():
    conn = sqlite3.connect("system.db")
    query_path = os.path.join(SQL_PATH, "system.sql")
    with open(query_path, "r") as f:
        query = f.read()

    conn.executescript(query)
    conn.commit()
    conn.close()


def update_gallery():
    os.mkdir("default")
    os.mkdir("default/files")
    os.mkdir("default/thumbnails")

    conn = sqlite3.connect("default/default.db")
    query_path = os.path.join(SQL_PATH, "gallery.sql")
    with open(query_path, "r") as f:
        query = f.read()

    conn.executescript(query)
    conn.commit()
    conn.close()

    # Copy db file to db folder
    source = os.path.normpath("default/default.db")
    dest = os.path.normpath("db/default.db")

    shutil.copy(source, dest)


if __name__ == '__main__':
    if os.path.isfile("system.db"):
        print("system.db already exists!")
        print("If you want to generate a new one delete it")
    else:
        update_system()

    if os.path.isfile("default/default.db"):
        print("default/ gallery already exists!")
        print("If you want to generate a new one delete it")
    else:
        update_gallery()
