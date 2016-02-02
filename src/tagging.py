#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Functionality for assigning tags to imported files.
'''

import os
import database
import output

# Methods for assigning tags to files


def create_tag(tag_name, is_numeric=False):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    # Try to find existing tag
    query_get_tags = "SELECT pk_id FROM tag WHERE name = \'%s\'" % (tag_name)
    cursor.execute(query_get_tags)
    tag = cursor.fetchone()
    if tag:
        return tag[0]

    else:
        # Tag needs to be created
        query_insert_tag = "INSERT INTO tag(name, is_numeric) VALUES (\'%s\', %d)" % (
            tag_name, is_numeric)
        cursor.execute(query_insert_tag)
        gallery.commit()

    # Get ID of the tag
    query_get_tags = "SELECT pk_id FROM tag WHERE name = \'%s\'" % (tag_name)
    cursor.execute(query_get_tags)
    tag_id = cursor.fetchone()

    cursor.execute("SELECT pk_id, add_new_tag FROM gallery_folder")
    gallery_folders = cursor.fetchall()
    for gallery_folder in gallery_folders:
        print gallery_folder
        if gallery_folder[1] == 1:
            cursor.execute(
                "INSERT INTO gallery_folder_has_tag "
                "VALUES(%d, %d)"
                % (gallery_folder[0], tag_id[0])
            )
    gallery.commit()

    return tag_id[0]


def delete_tag(id):
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    cursor.execute(
        "DELETE FROM gallery_folder_has_tag WHERE pk_fk_tag_id = ?",
        (id,),
    )
    cursor.execute(
        "DELETE FROM file_has_tag WHERE pk_fk_tag_id = ?",
        (id,),
    )
    cursor.execute("DELETE FROM tag WHERE pk_id = ?", (id,))

    gallery.commit()


def tag_file(file_id, tag_name, amount=-1):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    # Get tag or create it
    if amount > -1:
        tag_id = create_tag(tag_name, True)
    elif amount == -1:
        tag_id = create_tag(tag_name)

    query_link = (
        "INSERT INTO file_has_tag(pk_fk_file_id, pk_fk_tag_id, amount) "
        "VALUES (%d, %d, %d)" %
        (file_id, tag_id, amount)
    )
    cursor.execute(query_link)

    # Write changes
    gallery.commit()
    output.change(file_id, tag_id, True)


def untag_file(file_id, tag_name):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    # Get tag
    query_get_tags = "SELECT pk_id FROM tag WHERE name = \'%s\'" % (tag_name)
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()

    for tag in tags:
        tag_id = tag[0]
        query_untag = (
            "DELETE FROM file_has_tag WHERE pk_fk_file_id = %d "
            "AND pk_fk_tag_id = %d" % (file_id, tag_id))
        cursor.execute(query_untag)

    # Write changes
    gallery.commit()
    output.change(file_id, tag_id, False)


def tag_files(file_ids, tag_name, amount=-1):
    for file_id in file_ids:
        tag_file(file_id, tag_name, amount)


def remove_file(file_id):
    gallery = database.get_current_gallery("connection")
    c = gallery.cursor()

    c.execute(
        (
            "SELECT pk_id FROM tag "
            "JOIN file_has_tag ON pk_id=pk_fk_tag_id "
            "WHERE pk_fk_file_id=:file"
        ),
        {
            "file": file_id
        }
    )
    tags = c.fetchall()
    for tag in tags:
        output.change(file_id, tag[0], False)

    c.execute("DELETE FROM file WHERE pk_id=%s" % str(file_id))
    c.execute("DELETE FROM file_has_tag WHERE pk_fk_file_id=%s" % str(file_id))
    gallery.commit()


# Methods for analyzing assigned tags


def file_has_tag_id(file_id, tag_id):
    tags = get_tags(file_id)
    if tag_id in tags:
        return True
    else:
        return False


def file_has_tag(file_id, tag_name):
    tag_id = tag_name_to_id(tag_name)
    return file_has_tag_id(file_id, tag_id)


def get_tags(file_id):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    tags = []
    query_get_tags = "SELECT pk_fk_tag_id FROM file_has_tag WHERE pk_fk_file_id = %d" % (
        file_id)
    cursor.execute(query_get_tags)
    result = cursor.fetchall()
    for tag in result:
        tags.append(tag[0])

    gallery.commit()
    return tags


def get_tag_names(file_id):
    tag_ids = get_tags(file_id)
    tags = []
    for tag_id in tag_ids:
        tags.append(tag_id_to_name(tag_id))

    return tags


def tag_id_to_name(tag_id):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    query_get_tags = "SELECT name FROM tag WHERE pk_id = %d" % (tag_id)
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    gallery.commit()
    if tags:
        for tag in tags:
            return tag[0]
    else:
        return "?"
        # raise ValueError("Tag does not exist", tag_id)


def tag_name_to_id(tag_name):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    query_get_tags = "SELECT pk_id FROM tag WHERE name = \'%s\'" % (tag_name)
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    gallery.commit()
    if tags:
        for tag in tags:
            return tag[0]
    else:
        return "?"
        # raise ValueError("Tag does not exist", tag_name)


def advanced_path_to_id(path):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    location, name = os.path.split(path)

    query_get_folders = (
        "SELECT pk_id FROM folder "
        "WHERE location = \'%s\' AND name = \'%s\'" % (location, name))
    cursor.execute(query_get_folders)
    folder = cursor.fetchone()
    if folder:
        return folder[0]
    else:
        return False


def gallery_path_to_id(path):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    location, name = os.path.split(path)

    query_get_folders = (
        "SELECT pk_id FROM gallery_folder "
        "WHERE location = \'%s\' AND name = \'%s\'" % (location, name))
    cursor.execute(query_get_folders)
    folder = cursor.fetchone()
    if folder:
        return folder[0]
    else:
        return False


def get_all_tag_ids():
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    tag_ids = []
    query_get_tags = "SELECT pk_id FROM tag"
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    for tag in tags:
        tag_ids.append(tag[0])

    gallery.commit()
    return tag_ids


def get_all_tags():
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    tag_names = []
    query_get_tags = "SELECT name FROM tag"
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    for tag in tags:
        tag_names.append(tag[0])

    gallery.commit()
    return tag_names
