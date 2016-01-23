import os
import shutil
import database
import tagging


def file(ids, path, move=False):
    gallery = database.get_current_gallery("directory")
    connection = database.get_current_gallery("connection")
    c = connection.cursor()
    c.execute("SELECT uuid, file_name FROM file WHERE pk_id IN (?)", ids)
    files = c.fetchall()

    for file in files:
        intern = os.path.join(gallery, "files", file[0])
        extern = os.path.join(path, file[1])
        shutil.copy(intern, extern)
        if move:
            tagging.remove_file(file)
            os.remove(intern)


def output(id, advanced, tag=None, convert=False, path=None):
    connection = database.get_current_gallery("connection")
    c = connection.cursor()

    # get folder information
    if advanced:
        c.execute("SELECT location, name FROM folder WHERE pk_id=?", (id,))
        folder = c.fetchone()
        if folder is None:
            raise ValueError("No advanced output folder with this id", id)
    else:
        if convert:
            raise ValueError("Gallery output folders cannot be converted")
        if tag is None:
            raise ValueError("Gallery folder exports require a tag")

        c.execute("SELECT name FROM tag WHERE pk_id=?", (tag,))
        tag_name = c.fetchone()
        if tag_name is None:
            raise ValueError("Invalid tag id", tag)
        tag_name = tag_name[0]

        c.execute(
            "SELECT location, name FROM gallery_folder WHERE pk_id=?",
            (id,)
        )
        folder = c.fetchone()
        if folder is None:
            raise ValueError("No advanced output folder with this id", id)

    # set copy source and destination
    source = os.path.join(folder[0], folder[1])
    if not advanced:
        source = os.path.join(source, tag_name)

    if convert:
        dest = source
    elif not advanced:
        dest = os.path.join(path, tag_name)
    else:
        dest = os.path.join(path, folder[1])
    os.makedirs(dest)

    # copy files
    files = os.listdir(source)
    for file in files:
        shutil.copy(os.path.join(source, file), dest)

    if convert:
        # delete folder from db
        if advanced:
            query = "DELETE FROM folder WHERE pk_id=?"
        else:
            query = "DELETE FROM gallery_folder WHERE pk_id=?"

        c.execute(query, id)
        connection.commit()


output(1, False, tag=2, path="/home/clemens/Desktop/export")
