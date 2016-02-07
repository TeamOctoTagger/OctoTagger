#!/usr/bin/python
# -*- coding: utf-8 -*-

import database
import expression
import os

if os.name == "nt":
    import winlink

# TODO: Delete existing files first!


def create_folders():

    # Get gallery connection
    gallery_conn = database.get_current_gallery("connection")
    cursor = gallery_conn.cursor()

    # Get output folders
    query_folders = ("SELECT name, location, "
                     "expression, use_softlink FROM folder")
    cursor.execute(query_folders)
    folders = cursor.fetchall()

    for folder in folders:
        name = folder[0]
        location = folder[1]
        folder_expression = folder[2]
        dest = os.path.join(location, name)

        if folder[3] == 1:
            use_softlink = True
        else:
            use_softlink = False

        if not os.path.exists(dest):
            os.makedirs(dest)

        # Get files
        query_files = ("SELECT file_name, uuid FROM file WHERE %s" %
                       (expression.parse(folder_expression)))

        cursor.execute(query_files)
        files = cursor.fetchall()
        for file in files:
            name = file[0]
            uuid = file[1]

            destination = os.path.join(dest, name)

            if not os.path.exists(destination):

                source = os.path.join(
                    os.path.join(database.get_current_gallery("directory"),
                                 "files"), uuid)

                symlink(source, destination, use_softlink)


def symlink(src, dest, use_softlink):
    src = os.path.normpath(os.path.abspath(src))
    dest = os.path.normpath(os.path.abspath(dest))

    print "SRC", src
    print "DST", dest
    print "EXST?", os.path.exists(src)
    print "DSTEXST?", os.path.exists(dest)

    if not os.path.exists(dest):
        try:
            os.remove(dest)
        except:
            pass

        if os.name == "nt":
            use_hardlink = not use_softlink
            winlink.symlink(src, dest, use_hardlink)
        else:
            if use_softlink:
                os.symlink(src, dest)
            else:
                os.link(src, dest)
