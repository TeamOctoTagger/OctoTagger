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
import sqlite3
import database

def import_files(files, db):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()
    dest_dir = os.path.join(database.get_current_gallery("directory"), "files")

    for file in files:
        file = os.path.normpath(file)
        # Defensive programming
        if os.path.isfile(file) and os.path.isdir(dest_dir):
            print "Importing " + file
            original_name = os.path.basename(file)  # for the database
            new_name = str(uuid.uuid4())

            while os.path.exists(os.path.join(dest_dir, new_name)):
                new_name = str(uuid.uuid4())

            dest = os.path.join(dest_dir, new_name)
            shutil.copy(file, dest)

            query_insert_file = "INSERT INTO file (file_name, uuid) VALUES (\'%s\', \'%s\')"%(original_name, new_name)
            cursor.execute(query_insert_file)

        else:
            dlg_error = wx.MessageBox(
                'An error has occured while importing.',
                'Error',
                wx.OK | wx.ICON_EXCLAMATION
            ).ShowModal()

    gallery.commit()
