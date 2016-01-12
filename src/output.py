import database
import create_folders
import expression
import os


def change(item, tag, create):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    c.execute(
        (
            "SELECT uuid, file_name "
            "FROM file "
            "WHERE pk_id=:id"
        ),
        {
            "id": item
        }
    )
    # TODO better var name
    g_file = c.fetchone()
    if g_file is None:
        raise ValueError("No file with this id", item)
    target = os.path.join(
        database.get_current_gallery("directory"),
        "files",
        g_file[0]
    )

    # gallery output folders

    c.execute(
        "SELECT pk_id, location, name, use_softlink "
        "FROM gallery_folder"
    )
    folders = c.fetchall()

    for folder in folders:
        c.execute(
            (
                "SELECT name "
                "FROM gallery_folder_has_tag "
                "JOIN tag ON pk_fk_tag_id=pk_id "
                "WHERE pk_fk_gallery_folder_id=:folder AND pk_id=:tag"
            ),
            {
                "folder": folder[0],
                "tag": tag
            }
        )
        tag_name = c.fetchone()
        if tag_name is None:
            # gallery output does not use this tag
            continue
        else:
            tag_name = tag_name[0]

        path = os.path.join(folder[1], folder[2], tag_name)
        if not os.path.isdir(path):
            os.makedirs(path)

        if create:
            # create
            create_folders.symlink(
                target,
                os.path.join(path, g_file[1]),
                folder[3]
            )
        else:
            # delete
            os.remove(os.path.join(path, g_file[1]))

    # advanced output folders

    c.execute(
        "SELECT location, name, expression, use_softlink "
        "FROM folder"
    )
    folders = c.fetchall()
    for folder in folders:
        path = os.path.join(folder[0], folder[1])
        link = os.path.join(path, g_file[1])
        c.execute(
            (
                "SELECT pk_id "
                "FROM file "
                "WHERE :expression AND pk_id=:id"
            ),
            {
                "expression": expression.parse(folder[2]),
                "id": item
            }
        )
        matches = c.fetchone()
        if matches is None and os.path.islink(link):
            os.remove(link)
        elif matches is not None and not os.path.islink(link):
            if not os.path.isdir(path):
                os.makedirs(path)
            create_folders.symlink(target, link, folder[3])


def remove(item):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    c.execute(
        "SELECT file_name FROM file WHERE pk_id=:file",
        {
            "file": item
        }
    )
    filename = c.fetchone()
    if filename is None:
        raise ValueError("No file with this id", item)

    c.execute(
        (
            "SELECT location, name FROM gallery_folder AS g "
            "LEFT JOIN gallery_folder_has_tag AS gt "
            "ON g.pk_id = gt.pk_fk_gallery_folder_id "
            "LEFT JOIN file_has_tag AS ft "
            "ON gt.pk_fk_tag_id = ft.pk_fk_tag_id "
            "WHERE ft.pk_fk_file_id=:file"
        ),
        {
            "file": item
        }
    )
    folders = c.fetchall()

    for folder in c.execute("SELECT location, name, expression FROM folder"):
        c.execute(
            (
                "SELECT pk_id FROM file "
                "WHERE :expression AND pk_id=:file"
            ),
            {
                "expression": expression.parse(folder[2]),
                "file": item
            }
        )
        if c.fetchone() is None:
            continue

        folders.append(folder[0:2])

    for folder in folders:
        path = os.path.join(folder[0], folder[1], filename)
        os.remove(path)
