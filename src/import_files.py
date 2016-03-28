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

    # Progress Window
    current_file = 1
    message = "Importing file " + str(current_file) + " of " + str(len(files))
    dlg_progress = wx.ProgressDialog(
        "Importing",
        message,
        maximum=len(files)
    )

    if type(files) is list:

        for file in files:
            file = os.path.normpath(file)

            # Update progress info
            dlg_progress.Update(
                current_file,
                "Importing file " + str(current_file) + " of " + str(len(files)) + "."
            )
            current_file += 1

            # Defensive programming
            if os.path.isfile(file) and os.path.isdir(dest_dir):

                original_name = os.path.basename(file)  # for the database
                new_name = (
                    str(uuid.uuid4()) + "." + original_name.split(".")[-1]
                )

                while os.path.exists(os.path.join(dest_dir, new_name)):
                    new_name = (
                        str(uuid.uuid4()) + "." + original_name.split(".")[-1]
                    )
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
            print file
            # Update progress info
            dlg_progress.Update(
                current_file,
                "Importing file " + str(current_file) + 
                " of " + str(len(files)) + "."
            )
            current_file += 1

            file = os.path.normpath(file)

            # Defensive programming
            if not os.path.isfile(file):
                continue

            if not os.path.isdir(dest_dir):
                print "Not a dir:", file, dest_dir

            if os.path.isfile(file) and os.path.isdir(dest_dir):
                original_name = os.path.basename(file)
                new_name = (
                    str(uuid.uuid4()) + "." + original_name.split(".")[-1]
                )

                while os.path.exists(os.path.join(dest_dir, new_name)):
                    new_name = (
                        str(uuid.uuid4()) + "." + original_name.split(".")[-1]
                    )

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

    dlg_progress.Destroy()

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


def rename_file(id, new_name):

    # Update database
    gallery_conn = database.get_current_gallery("connection")
    cursor = gallery_conn.cursor()
    cursor.execute("SELECT uuid FROM file WHERE pk_id = %d" % (id))
    old_uuid = cursor.fetchone()[0]
    new_uuid = ".".join([old_uuid.split(".")[0], new_name.split(".")[-1]])

    cursor.execute((
        "UPDATE file SET uuid = \'%s\'"
        "WHERE pk_id = %d"
        ) % (new_uuid, id)
    )
    gallery_conn.commit()

    # Rename file
    file_path = os.path.join(
        database.get_current_gallery("directory"), "files")
    old_file = os.path.join(file_path, old_uuid)
    new_file = os.path.join(file_path, new_uuid)
    shutil.move(old_file, new_file)
