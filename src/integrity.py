import database
import os
import sqlite3


def check(event = None):
    """checks the integrity of the current gallery"""
    gallery_folder = database.get_current_gallery("directory")
    gallery_conn = database.get_current_gallery("connection")
    gallery_conn.row_factory = sqlite3.Row
    c = gallery_conn.cursor()
    result = {
        "files": {
            "untracked": [],
            "missing": [],
        },
        "folder": {
            "directories": [],
            "untracked": [],
            "changed": [],
        },
    }

    # check for loose files

    files_fs = set(os.listdir(os.path.join(gallery_folder, "files")))

    c.execute("SELECT uuid FROM file")
    files_db = set(map(lambda x: x[0], c.fetchall()))

    for untracked_file in (files_fs - files_db):
        result["files"]["untracked"].append(untracked_file)

    for missing_file in (files_db - files_fs):
        c.execute("SELECT pk_id FROM file WHERE uuid=:uuid", {
            "uuid": missing_file,
        })
        result["files"]["missing"].append(c.fetchone()[0])

    # check for old output folders

    c.execute("SELECT name, location, use_softlink FROM folder")
    for folder in c.fetchall():
        folder_path = os.path.join(folder["location"], folder["name"])
        files = set(os.listdir(folder_path))

        # TODO check expression

        result["folder"]["directories"].extend([
            f for f in files if
            os.path.isdir(os.path.join(folder_path, f))
        ])

        if folder["use_softlink"] == True:
            untracked_files = [
                f for f in files if
                os.path.isfile(os.path.join(folder_path, f)) and not
                os.path.islink(os.path.join(folder_path, f))
            ]
            for untracked_file in untracked_files:
                c.execute("SELECT pk_id FROM file WHERE file_name=:name", {
                    "name": untracked_file,
                })
                internal_file = c.fetchone()
                if internal_file is None:
                    result["folder"]["untracked"].append(untracked_file)
                else:
                    # TODO check if file matches expression
                    result["folder"]["changed"].append(internal_file[0])

    c.close()
    return result


def apply(diffs):
    pass


print(check())
