import database
import create_folders
import expression
import os
import shutil
import tagging


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
        query_file = (
                "SELECT pk_id "
                "FROM file "
                "WHERE %s AND pk_id = %d"
                % (expression.parse(folder[2]), item)
        )
        c.execute(query_file)
        matches = c.fetchone()
        if matches is None and os.path.exists(link):
            os.remove(link)
        elif matches is not None and not os.path.exists(link):
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
            "WHERE ft.pk_fk_file_id=:file "
            "GROUP BY g.pk_id"
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

    # Get tag name
    tags = tagging.get_tag_names(item)
    for folder in folders:
        for tag in tags:
            path = os.path.join(folder[0], folder[1], tag, filename[0])
            os.remove(path)


def move(id, advanced, target):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    if advanced:
        query_select = "SELECT location, name FROM folder WHERE pk_id = ?"
    else:
        query_select = (
            "SELECT location, name FROM gallery_folder WHERE pk_id = ?"
        )
    c.execute(query_select, (id,))
    folder = c.fetchone()
    if folder is None:
        raise ValueError("No output folder with this id", id)
    (source, name) = folder

    # verify
    if source == target:
        print "Source and target are the same"
        return
    if os.path.exists(os.path.join(target, name)):
        print "Target path already exists"
        return
        # TODO: handle this better

    # move
    shutil.move(
        os.path.join(source, name),
        os.path.join(target, name),
    )

    # update db
    if advanced:
        query_update = "UPDATE folder SET location = ? WHERE pk_id = ?"
    else:
        query_update = "UPDATE gallery_folder SET location = ? WHERE pk_id = ?"
    c.execute(query_update, (target, id))
    connection.commit()


def rename(id, advanced, new):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    if advanced:
        query = "SELECT location, name FROM folder WHERE pk_id = ?"
    else:
        query = "SELECT location, name FROM gallery_folder WHERE pk_id = ?"
    c.execute(query, (id,))
    folder = c.fetchone()
    if folder is None:
        raise ValueError("No output folder with this id", id)
    (location, old) = folder

    # verify
    if old == new:
        print "New name must be different"
        return
    if os.path.exists(os.path.join(location, new)):
        print "New name already exists"
        return
        # TODO: Handle this better

    # move
    shutil.move(
        os.path.join(location, old),
        os.path.join(location, new),
    )

    # update db
    if advanced:
        query = "UPDATE folder SET name = ? WHERE pk_id = ?"
    else:
        query = "UPDATE gallery_folder SET name = ? WHERE pk_id = ?"
    c.execute(query, (new, id))
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
            "WHERE pk_fk_gallery_folder_id=? AND pk_id=?"
        ),
        (id, tag),
    )
    tag_name = c.fetchone()
    if tag_name is not None and add:
        raise ValueError("Tag already added")
    elif tag_name is None and not add:
        raise ValueError("Tag already removed")

    if add:
        # Get tag name
        c.execute("SELECT name FROM tag WHERE pk_id = ?", (tag,))
        result = c.fetchone()
        tag_name = result[0]

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

        # Get tag name
        c.execute("SELECT name FROM tag WHERE pk_id = ?", (tag,))
        result = c.fetchone()
        tag_name = result[0]

        shutil.rmtree(os.path.join(folder[0], folder[1], tag_name))

        # update db
        c.execute(
            (
                "DELETE FROM gallery_folder_has_tag "
                "WHERE pk_fk_gallery_folder_id=? AND "
                "pk_fk_tag_id=?"
            ),
            (id, tag),
        )
        connection.commit()


def change_link_type(id, advanced, type):
    """Changes the link type of an output folder. Softlinks if type is True and
    hardlinks if type is False, like the use_softlink field"""
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get output folder information
    if advanced:
        query = (
            "SELECT location, name, use_softlink, expression "
            "FROM folder WHERE "
            "pk_id = ?"
        )
    else:
        query = (
            "SELECT location, name, use_softlink "
            "FROM gallery_folder "
            "WHERE pk_id = ?"
        )
    c.execute(query, (id,))
    output = c.fetchone()
    if output is None:
        raise ValueError("Invalid folder id", id)
    if output[2] == type:
        # nothing to do
        return

    gallery = database.get_current_gallery("directory")

    if advanced:
        # remake folders
        folder = os.path.join(output[0], output[1])
        shutil.rmtree(folder)
        os.mkdir(folder)

        # relink files
        expression = output[3]
        c.execute(
            (
                "SELECT uuid, file_name "
                "FROM file "
                "WHERE ?"
            ),
            (expression,),
        )
        files = c.fetchall()
        if files is None:
            # no files, nothing to do
            return
        for file in files:
            source = os.path.join(gallery, "files", file[0])
            target = os.path.join(folder, file[1])
            create_folders.symlink(source, target, type)

        # update db
        c.execute(
            (
                "UPDATE folder "
                "SET use_softlink = ? "
                "WHERE pk_id = ?"
            ),
            (type, id),
        )
        connection.commit()
    else:
        # get tags
        c.execute(
            (
                "SELECT pk_id, name "
                "FROM gallery_folder_has_tag "
                "JOIN tag ON pk_fk_tag_id = pk_id "
                "WHERE pk_fk_gallery_folder_id = ?"
            ),
            (id,),
        )
        tags = c.fetchall()
        if tags is None:
            # no folders, nothing to do
            return
        for tag in tags:
            # remake folder
            folder = os.path.join(output[0], output[1], tag[1])
            shutil.rmtree(folder)
            os.mkdir(folder)

            # relink files
            c.execute(
                (
                    "SELECT uuid, file_name "
                    "FROM file f "
                    "JOIN file_has_tag ft ON f.pk_id = ft.pk_fk_file_id "
                    "JOIN tag t ON ft.pk_fk_tag_id = t.pk_id "
                    "WHERE t.pk_id = ?"
                ),
                (tag[0],),
            )
            files = c.fetchall()
            if files is None:
                # no files, nothing to do
                continue
            for file in files:
                source = os.path.join(gallery, "files", file[0])
                target = os.path.join(folder, file[1])
                create_folders.symlink(source, target, type)

            # update dn
            c.execute(
                (
                    "UPDATE gallery_folder "
                    "SET use_softlink = ? "
                    "WHERE pk_id = ?"
                ),
                (type, id),
            )
            connection.commit()


def change_expression(id, new_expression):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder
    c.execute(
        (
            "SELECT location, name, use_softlink "
            "FROM folder "
            "WHERE pk_id = ?"
        ),
        (id,)
    )
    output = c.fetchone()
    if output is None:
        raise ValueError("Invalid folder id", id)

    # parse expression
    where = expression.parse(new_expression)

    # remake folder
    folder = os.path.join(output[0], output[1])
    shutil.rmtree(folder)
    os.mkdir(folder)

    # relink files
    c.execute(
        (
            "SELECT uuid, file_name "
            "FROM file "
            "WHERE {}"
        ).format(where)
    )
    files = c.fetchall()
    if files is not None:
        gallery = database.get_current_gallery("directory")
        for file in files:
            source = os.path.join(gallery, "files", file[0])
            target = os.path.join(folder, file[1])
            create_folders.symlink(source, target, output[2])

    # update db
    c.execute(
        (
            "UPDATE folder "
            "SET expression = ? "
            "WHERE pk_id = ?"
        ),
        (new_expression, id),
    )
    connection.commit()


def rename_tag(id, new_name):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # check if new names is taken
    c.execute("SELECT pk_id FROM tag WHERE name = ?", (new_name,))
    test = c.fetchone()
    if test is not None:
        raise ValueError("New tag name is already in use")

    # get old name
    c.execute("SELECT name FROM tag WHERE pk_id = ?", (id,))
    old_name = c.fetchone()
    if old_name is None:
        raise ValueError("Unknown tag id", id)
    old_name = old_name[0]

    # get all gallery folders with this tag
    c.execute(
        (
            "SELECT location, name "
            "FROM gallery_folder "
            "JOIN gallery_folder_has_tag "
            "WHERE pk_fk_tag_id = ?"
        ),
        (id,),
    )
    outputs = c.fetchall()

    # rename folders
    if outputs is not None:
        for output in outputs:
            folder = os.path.join(output[0], output[1])
            shutil.move(
                os.path.join(folder, old_name),
                os.path.join(folder, new_name),
            )

    # update db
    c.execute(
        "UPDATE tag SET name = ? WHERE pk_id = ?",
        (new_name, id),
    )
    connection.commit()


def delete_tag(id):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get tag information
    c.execute("SELECT name FROM tag WHERE pk_id = ?", (id,))
    name = c.fetchone()
    if name is None:
        raise ValueError("Invalid tag id", id)
    name = name[0]

    # get galleries
    c.execute(
        (
            "SELECT pk_id "
            "FROM gallery_folder "
            "JOIN gallery_folder_has_tag ON pk_id = pk_fk_gallery_folder_id "
            "WHERE pk_fk_tag_id = ?"
        ),
        (id,),
    )
    galleries = c.fetchall()

    # untag galleries
    if galleries is not None:
        for gallery in galleries:
            change_gallery(gallery[0], id, False)

    # get files
    c.execute(
        (
            "SELECT pk_id "
            "FROM file "
            "JOIN file_has_tag ON pk_id = pk_fk_file_id "
            "WHERE pk_fk_tag_id = ?"
        ),
        (id,),
    )
    files = c.fetchall()

    # untag files
    if files is not None:
        for file in files:
            change(file[0], id, False)


def rename_file(id, new_name):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get file information
    c.execute("SELECT file_name FROM file WHERE pk_id = ?", (id,))
    old_name = c.fetchone()
    if old_name is None:
        raise ValueError("Invalid file id", id)
    old_name = old_name[0]

    # get folders
    outputs = []

    # get gallery folders
    c.execute("SELECT location, name, pk_id FROM gallery_folder")
    folders = c.fetchall()
    if folders is not None:
        for folder in folders:
            # get all matching tags
            c.execute(
                (
                    "SELECT name "
                    "FROM tag "
                    "JOIN gallery_folder_has_tag g ON g.pk_fk_tag_id = pk_id "
                    "JOIN file_has_tag t ON t.pk_fk_tag_id = pk_id "
                    "WHERE g.pk_fk_gallery_folder_id = ? "
                    "AND t.pk_fk_file_id = ?"
                ),
                (
                    folder[2],
                    id,
                ),
            )
            tags = c.fetchall()
            if tags is not None:
                for tag in tags:
                    outputs.append(os.path.join(folder[0], folder[1], tag[0]))

    # get advanced folders
    c.execute("SELECT pk_id, expression FROM folder")
    folders = c.fetchall()
    if folders is not None:
        for folder in folders:
            # test expression
            where = expression.parse(folder[1])
            c.execute(
                "SELECT pk_id FROM file WHERE pk_id = ? AND {}".format(where),
                (id,),
            )
            test = c.fetchone()
            if test is None:
                continue

            # expression matches file
            c.execute(
                "SELECT location, name FROM folder WHERE pk_id = ?",
                (folder[0],),
            )
            folder = c.fetchone()
            outputs.append(os.path.join(folder[0], folder[1]))

    # rename links
    for output in outputs:
        source = os.path.join(output, old_name)
        target = os.path.join(output, new_name)
        print(source, target)
        os.rename(source, target)

    # update db
    c.execute(
        "UPDATE file SET file_name = ? WHERE pk_id = ?",
        (new_name, id),
    )
    connection.commit()


def create_gallery(id):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    c.execute(
        "SELECT location, name FROM gallery_folder WHERE pk_id = ?",
        (id,),
    )
    folder = c.fetchone()
    if folder is None:
        raise ValueError("Invalid gallery folder id", id)

    shutil.makedirs(os.path.join(folder[0], folder[1]))

# TODO: remove links when files are restored (?)
