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

def import_files(files, db):
    dest_dir = os.path.normpath(db + "/files")
    for file in files:
        file = os.path.normpath(file)
        if os.path.isfile(file) and os.path.isdir(dest_dir):    # Defensive programming
            print "Importing " + file
            original_name = os.path.basename(file) # for the database
            new_name = str(uuid.uuid4())

            while os.path.exists(os.path.join(dest_dir, new_name)):
                new_name = str(uuid.uuid4())

            dest = os.path.join(dest_dir, new_name)
            shutil.copy(file, dest)
        else:
            dlg_error = wx.MessageBox('An error has occured while importing.', 'Error',
                						wx.OK | wx.ICON_EXCLAMATION)
