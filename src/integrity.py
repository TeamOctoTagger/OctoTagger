import create_folders
import database
import os


def check(event=None):
    connection = database.get_sys_db()
    c = connection.cursor()
    for gallery in c.execute("SELECT pk_id FROM gallery"):
        _check_gallery(gallery)


def _check_gallery(id):
    """checks the integrity of a gallery"""
    connection = database.get_gallery(id, "connection")
    c = connection.cursor()

    gallery = os.path.join(database.get_gallery(id, "directory"), "files")

    result = {
        "untracked": [],
        "missing": [],
    }

    # check database

    files_fs = set(os.listdir(gallery))
    files_db = {x[0] for x in c.execute("SELECT uuid FROM file")}

    for untracked_file in (files_fs - files_db):
        result["untracked"].append(untracked_file)

    for missing_file in (files_db - files_fs):
        c.execute("SELECT pk_id FROM file WHERE uuid=:uuid", {
            "uuid": missing_file,
        })
        result["missing"].append(c.fetchone()[0])

    # check advanced output folders

    c.execute("SELECT location, name, use_softlink, expression FROM folder")
    for folder in c.fetchall():
        path = os.path.join(folder[0], folder[1])
        files_fs = set(os.listdir(path))

        # create missing links
        c.execute(
            (
                "SELECT uuid, file_name "
                "FROM file "
                "WHERE {}"
            ).format(folder[3])
        )
        files = [f for f in c.fetchall() if f not in files_fs]
        for file in files:
            create_folders.symlink(
                os.path.join(gallery, file[0]),
                os.path.join(path, file[1]),
                folder[2],
            )

    # check gallery output folders

    c.execute(
        "SELECT location, name, use_softlink, pk_id "
        "FROM gallery_folder"
    )
    for folder in c.fetchall():
        c.execute(
            (
                "SELECT t.name, t.pk_id "
                "FROM gallery_folder g "
                "JOIN gallery_folder_has_tag gt "
                "ON g.pk_id = gt.pk_fk_gallery_folder_id "
                "JOIN tag t ON gt.pk_fk_tag_id = t.pk_id "
                "WHERE g.pk_id = ?"
            ),
            (
                folder[3],
            ),
        )
        for tag in c.fetchall():
            path = os.path.join(folder[0], folder[1], tag[0])
            files_fs = set(os.listdir(path))

            # create missing links
            c.execute(
                (
                    "SELECT uuid, file_name "
                    "FROM file f "
                    "JOIN file_has_tag ft ON t.pk_id = ft.pk_fk_file_id "
                    "JOIN tag t ON ft.pk_fk_tag_id = t.pk_id "
                    "WHERE t.pk_id = ?"
                ),
                (
                    tag[1],
                ),
            )
            files = [f for f in c.fetchall() if f not in files_fs]
            for file in files:
                create_folders.symlink(
                    os.path.join(gallery, file[0]),
                    os.path.join(path, file[1]),
                    folder[2],
                )

    return result
