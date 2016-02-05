#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Functionality for moving specified files to the current databases file folder,
give them a unique name in the process.
'''

import os
import shutil
import uuid
import wx
import database
import tagging


def import_files(files):

    # Get gallery connection
    gallery_conn = database.get_current_gallery("connection")
    cursor = gallery_conn.cursor()
    dest_dir = os.path.join(database.get_current_gallery("directory"), "files")

    # Retrieve import setting
    sys_cursor = database.get_sys_db().cursor()
    sys_cursor.execute(
        "SELECT import_copy FROM settings"
    )
    import_copy = (sys_cursor.fetchone()[0] == 1)

    # Keep track of files with the same name
    same_name_files = []

    if type(files) is list:

        for file in files:
            file = os.path.normpath(file)
            # Defensive programming
            if os.path.isfile(file) and os.path.isdir(dest_dir):
                # print "Importing " + file
                original_name = os.path.basename(file)  # for the database
                new_name = str(uuid.uuid4())

                while os.path.exists(os.path.join(dest_dir, new_name)):
                    new_name = str(uuid.uuid4())

                dest = os.path.join(dest_dir, new_name)
                if import_copy:
                    shutil.copy(file, dest)
                else:
                    shutil.move(file, dest)

                # Check if name already exists
                cursor.execute(
                    "SELECT file_name FROM file WHERE file_name = ?",
                    (original_name,)
                )
                name = cursor.fetchone()
                if name:
                    same_name_files.append(name[0])

                # Save to database
                cursor.execute(
                    ("INSERT INTO file (file_name, uuid) "
                     "VALUES (\'%s\', \'%s\')") %
                    (original_name, new_name)
                )
                gallery_conn.commit()

            else:
                wx.MessageBox(
                    'An error has occured while importing.',
                    'Error',
                    wx.OK | wx.ICON_EXCLAMATION
                )

    elif type(files) is dict:
        for file, tags in files.iteritems():

            file = os.path.normpath(file)

            # Defensive programming
            if not os.path.isfile(file):
                continue

            if not os.path.isdir(dest_dir):
                print "Not a dir:", file, dest_dir

            if os.path.isfile(file) and os.path.isdir(dest_dir):
                original_name = os.path.basename(file)
                new_name = str(uuid.uuid4())

                while os.path.exists(os.path.join(dest_dir, new_name)):
                    new_name = str(uuid.uuid4())

                dest = os.path.join(dest_dir, new_name)
                if import_copy:
                    shutil.copy(file, dest)
                else:
                    shutil.move(file, dest)

                # Check if name already exists
                cursor.execute(
                    "SELECT file_name FROM file WHERE file_name = ?",
                    (original_name,)
                )
                name = cursor.fetchone()
                if name:
                    same_name_files.append(name[0])

                # Save to database
                query_insert_file = (
                    ("INSERT INTO file (file_name, uuid) "
                     "VALUES (\'%s\', \'%s\')")
                    % (original_name, new_name)
                )

                cursor.execute(query_insert_file)
                gallery_conn.commit()

                # Get ID
                query_file_id = (
                    "SELECT pk_id FROM file WHERE uuid = \'%s\'"
                    % (new_name)
                )
                cursor.execute(query_file_id)
                file_id = cursor.fetchone()[0]

                # Connect with tags
                tag_names = []
                for tag in tags:
                    tag_names.append(tagging.tag_id_to_name(tag))

                for tag_name in tag_names:
                    tagging.tag_file(file_id, tag_name)

            else:
                wx.MessageBox(
                    'An error has occured while importing.',
                    'Error',
                    wx.OK | wx.ICON_EXCLAMATION
                )

    # Warn user about same name files
    if len(same_name_files) == 0:
        return

    else:
        wx.MessageBox(
            ("Some of your imported files share the "
             "same name with each other, or with files "
             "that are already imported. \n\n"
             "This can lead to some unexpected behaviour "
             "or inconsistencies. "
             "It is recommended to give each file a unique name. "
             "You can rename a file in OctoTagger "
             "by selecting it and pressing 'F2'.\n\n"
             "Below is the list of file names the occur multiple times:\n\n" +
             "\n".join(same_name_files)),
            "Warning"
        )
