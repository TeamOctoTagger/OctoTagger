#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Interface for getting, creating, deleting and switching the gallery database, as well as getting the system database.
'''

import sqlite3
import os
import shutil

sys_db_file = './system.db'


def get_sys_db():
    return sqlite3.connect(sys_db_file)


def get_gallery(gallery_id, property):
    # Variable for storing the current gallery's properties.
    gallery_location = ''
    gallery_name = ''

    # Get gallery's data.
    sys_db = get_sys_db()
    cursor = sys_db.cursor()
    query_gallery_location = "SELECT location, name FROM gallery WHERE pk_id = %d" % (gallery_id)

    cursor.execute(query_gallery_location)
    result = cursor.fetchall()
    for gallery in result:
        gallery_location = os.path.normpath(gallery[0])
        gallery_name = gallery[1]

    # Close connection
    sys_db.commit()

    # Return property
    if(property == "id"):
        return gallery_id
    elif(property == "name"):
        return gallery_name
    elif(property == "location"):
        return gallery_location
    elif(property == "directory"):
        return os.path.join(gallery_location, gallery_name)
    elif(property == "file"):
        return os.path.normpath(os.path.join(gallery_location, gallery_name, (gallery_name + '.db')))
    elif(property == "connection"):
        return sqlite3.connect(os.path.normpath(os.path.join(gallery_location, gallery_name, (gallery_name + '.db'))))
    else:
        return False


def get_current_gallery(property):

    gallery_id = -1

    # Select the current gallery from the system database.
    sys_db = get_sys_db()
    cursor = sys_db.cursor()
    query_current_gallery = "SELECT current_db FROM settings"
    cursor.execute(query_current_gallery)
    result = cursor.fetchall()
    for setting in result:
        gallery_id = setting[0]

    # Close connection
    sys_db.commit()

    return get_gallery(gallery_id, property)


def create_gallery(name, location):
    # Sanitize
    location = os.path.normpath(location)

    # Create folders and database file
    try:
        folder_gallery = os.path.normpath(location + "/" + name)
        folder_files = os.path.normpath(folder_gallery + "/files")
        folder_thumbnails = os.path.normpath(folder_gallery + "/thumbnails")

        file_default_gallery = os.path.normpath("./db/default.db")
        file_new_gallery = os.path.join(folder_gallery, "%s.db" % (name))

        os.mkdir(folder_gallery)
        os.mkdir(folder_files)
        os.mkdir(folder_thumbnails)

        shutil.copy(file_default_gallery, file_new_gallery)

        # Get sys connection
        sys_db = get_sys_db()
        cursor = sys_db.cursor()
    except:
        return -1

    # Insert new gallery into sys connection
    query_insert_gallery = "INSERT INTO gallery(name, location) VALUES (\'%s\', \'%s\')" % (
        name, location)
    cursor.execute(query_insert_gallery)
    sys_db.commit()

    # Return new gallery's ID
    query_id = "SELECT pk_id FROM gallery WHERE name = \'%s\' AND location=\'%s\'" % (
        name, location)
    cursor.execute(query_id)
    result = cursor.fetchall()
    for gallery in result:
        return gallery[0]


def switch_gallery(id):
    # Get sys connection
    sys_db = get_sys_db()
    cursor = sys_db.cursor()

    # Check if id exists
    query_id = "SELECT pk_id FROM gallery WHERE pk_id = %d" % (id)
    cursor.execute(query_id)
    if cursor.fetchall():
        query_update = "UPDATE settings SET current_db = %d" % (id)
        cursor.execute(query_update)
        sys_db.commit()
        return True
    else:
        return False


def reset_gallery(id):
    gallery_conn = get_gallery(id, "connection")
    cursor = gallery_conn.cursor()

    query_file_has_tag = "DELETE FROM file_has_tag"
    query_tag = "DELETE FROM tag"
    query_folder = "DELETE FROM folder"

    cursor.execute(query_file_has_tag)
    cursor.execute(query_tag)
    cursor.execute(query_folder)

    gallery_conn.commit()


def delete_gallery(id):

    # Get gallery location
    directory = get_gallery(id, "directory")

    # Delete directory
    shutil.rmtree(directory)

    # Get sys connection
    sys_conn = get_sys_db()
    cursor = sys_conn.cursor()

    # Remove gallery from system db
    query_remove_gallery = "DELETE FROM gallery WHERE pk_id = %d" % id
    cursor.execute(query_remove_gallery)
    sys_conn.commit()
