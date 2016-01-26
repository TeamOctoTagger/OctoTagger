import database
import create_folders
import expression
import os
import shutil


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
            link_path = os.path.join(path, g_file[1])
            if os.path.lexists(link_path):
                os.remove(link_path)

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


def move(id, advanced, target):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    c.execute("SELECT location, name FROM ? WHERE pk_id=?", (
        (advanced and "folder" or "gallery_folder"),
        id,
    ))
    folder = c.fetchone()
    if folder is None:
        raise ValueError("No output folder with this id", id)
    (source, name) = folder

    # verify
    if source == target:
        raise ValueError("Source and target are the same")
    if os.path.exists(os.path.join(target, name)):
        raise IOError("Target path already exists")

    # move
    shutil.move(
        os.path.join(source, name),
        os.path.join(target, name),
    )

    # update db
    c.execute(
        (
            "UPDATE ? "
            "SET location=? "
            "WHERE pk_id=?"
        ),
        (
            (advanced and "folder" or "gallery_folder"),
            target,
            id,
        )
    )
    connection.commit()


def rename(id, advanced, new):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    c.execute("SELECT location, name FROM ? WHERE pk_id=?", (
        (advanced and "folder" or "gallery_folder"),
        id,
    ))
    folder = c.fetchone()
    if folder is None:
        raise ValueError("No output folder with this id", id)
    (location, old) = folder

    # verify
    if old == new:
        raise ValueError("New name must be different")
    if os.path.exists(os.path.join(location, new)):
        raise ValueError("New name already exists")

    # move
    shutil.move(
        os.path.join(location, old),
        os.path.join(location, new),
    )

    # update db
    c.execute(
        (
            "UPDATE ? "
            "SET name=? "
            "WHERE pk_id=?"
        ),
        (
            (advanced and "folder" or "gallery_folder"),
            new,
            id,
        )
    )
    connection.commit()


def change_gallery(id, tag, add):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    c.execute(
        (
            "SELECT location, name, use_softlink "
            "FROM gallery_folder WHERE pk_id=?"
        ),
        (id,),
    )
    folder = c.fetchone()
    if folder is None:
        raise ValueError("No gallery folder with this id", id)

    # check tag
    c.execute(
        (
            "SELECT name FROM gallery_folder_has_tag "
            "JOIN tag ON pk_fk_tag_id = pk_id "
            "WHERE pk_fk_gallery_id=? AND pk_id=?"
        ),
        (id, tag),
    )
    tag_name = c.fetchone()
    if tag_name is not None and add:
        raise ValueError("Tag already added")
    elif tag_name is None and not add:
        raise ValueError("Tag already removed")
    else:
        tag_name = tag_name[0]

    if add:
        # get files
        os.mkdir(os.path.join(folder[0], folder[1], tag_name))
        c.execute(
            (
                "SELECT uuid, file_name "
                "FROM file "
                "JOIN file_has_tag ON pk_id = pk_fk_file_id "
                "WHERE pk_fk_tag_id=?"
            ),
            (tag,),
        )
        files = c.fetchall()
        gallery = database.get_current_gallery("directory")

        # link files
        if files is not None:
            for file in files:
                source = os.path.join(gallery, "files", file[0])
                target = os.path.join(folder[0], folder[1], tag_name, file[1])
                create_folders.symlink(source, target, folder[2])

        # update db
        c.execute(
            (
                "INSERT INTO gallery_folder_has_tag "
                "VALUES (?, ?)"
            ),
            (id, tag),
        )
        connection.commit()
    else:
        # delete files
        shutil.rmtree(os.path.join(folder[0], folder[1], tag_name))

        # update db
        c.execute(
            (
                "DELETE FROM gallery_folder "
                "WHERE pk_fk_gallery_id=? AND "
                "pk_fk_tag_id=?"
            ),
            (id, tag),
        )
        connection.commit()


def change_link_type(id, advanced, type):
    raise NotImplementedError()


def change_expression(id, expression):
    # TODO get folder
    # TODO delete old files
    # TODO link new files
    raise NotImplementedError()
