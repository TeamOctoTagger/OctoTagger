#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import stat
from sys import platform


def exec_setup():
    os.system("python db/setup.py")


def write_desktop_file():
    path = os.path.abspath(os.getcwd())

    desktop_file_content = (
        ("[Desktop Entry]\n"
         "Encoding=UTF-8\n"
         "Version=1.0\n"
         "Type=Application\n"
         "Name=OctoTagger\n"
         "Icon=%s\n"
         "Path=%s\n"
         "Exec=python src/octotagger.py\n"
         "StartupNotify=false\n"
         "StartupWMClass=Octotagger.py\n"
         "OnlyShowIn=Unity") %
        (os.path.join(path, "icons/logo.png"),
         path)
    )

    desktop_file_path = os.path.expanduser(
        "~/.local/share/applications/octotagger.desktop"
    )

    desktop_file = open(
        desktop_file_path,
        "w"
    )

    desktop_file.write(desktop_file_content)
    os.chmod(desktop_file_path, os.stat(
        desktop_file_path).st_mode | stat.S_IEXEC)


def create_shortcut_file():
    run_script_path = os.path.join(os.getcwd(), "OctoTagger.command")
    run_script = open(
        run_script_path,
        "w"
    )
    # TODO: Hide terminal window
    run_script_content = (
        '#!/bin/sh\n'
        'cd %s\n'
        'python ./src/octotagger.py' %
        (os.getcwd())
    )
    run_script.write(run_script_content)
    os.chmod(run_script_path, os.stat(
             run_script_path).st_mode | stat.S_IEXEC)

    shortcut_file = os.path.expanduser("~/Desktop/OctoTagger.command")
    os.symlink(run_script_path, shortcut_file)

if platform == "darwin":
    exec_setup()
    create_shortcut_file()
elif platform.startswith("linux"):
    exec_setup()
    write_desktop_file()
