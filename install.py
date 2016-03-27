#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import stat
from sys import platform
import shutil

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

def create_app_file():
    run_script_path = os.path.join(os.getcwd(), "run.sh")
    run_script = open(
        run_script_path,
        "w"
    )
    run_script_content = (
        '#!/bin/sh\n'
        'export PYTHONPATH="/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages"\n'
        'cd %s\n'
        'python ./src/octotagger.py' %
        (os.getcwd())
    )
    run_script.write(run_script_content)
    os.chmod(run_script_path, os.stat(
             run_script_path).st_mode | stat.S_IEXEC)

    app_file = "~/Desktop/OctoTagger.app"
    command = ("osacompile -e 'do shell script \"%s\"' -x -o %s" % (run_script_path, app_file))
    os.system(command)

    src = "./icons/logo.icns"
    dest = os.path.join(app_file, "Contents/Resources/applet.icns")
    os.system("cp -f %s %s" % (src, dest))

if platform == "darwin":
    exec_setup()
    create_app_file()
elif platform.startswith("linux"):
    exec_setup()
    write_desktop_file()

