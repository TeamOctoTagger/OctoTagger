#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
from os.path import expanduser
import os
import database

class NewDatabase(wx.Dialog):

    """Extending Dialog"""

    def __init__(self, *args, **kw):
        super(NewDatabase, self).__init__(*args, **kw)

        self.SetSize((450, 200))
        self.SetTitle("New Database")
        self.init_ui()

    def init_ui(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # Define elements and add them to sizer
        # Labels
        txt_name = wx.StaticText(panel, label="Name: ")
        sizer.Add(
            txt_name,
            pos=(0, 0),
            flag=wx.LEFT | wx.TOP,
            border=5
        )

        txt_directory = wx.StaticText(panel, label="Location: ")
        sizer.Add(
            txt_directory,
            pos=(1, 0),
            flag=wx.LEFT | wx.TOP,
            border=5
        )

        # Text controls
        self.tc_name = wx.TextCtrl(panel)
        sizer.Add(
            self.tc_name,
            pos=(0, 1),
            span=(1, 3),
            flag=wx.RIGHT | wx.TOP | wx.EXPAND,
            border=5
        )

        self.tc_directory = wx.TextCtrl(panel)
        sizer.Add(
            self.tc_directory,
            pos=(1, 1),
            span=(1, 3),
            flag=wx.RIGHT | wx.TOP | wx.EXPAND,
            border=5
        )

        # Buttons
        btn_browse = wx.Button(panel, label="Browse...")
        btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
        sizer.Add(
            btn_browse,
            pos=(1, 4),
            flag=wx.TOP | wx.RIGHT,
            border=5
        )

        btn_ok = wx.Button(panel, label="Ok")
        btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        sizer.Add(
            btn_ok,
            pos=(3, 3),
            flag=wx.RIGHT | wx.BOTTOM,
            border=5
        )

        btn_cancel = wx.Button(panel, label="Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, self.on_close)
        sizer.Add(
            btn_cancel,
            pos=(3, 4),
            flag=wx.RIGHT | wx.BOTTOM,
            border=5
        )

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(2)
        panel.SetSizer(sizer)

    def on_browse(self, e):
        dlg_browse = wx.DirDialog(self,
                                  "Choose a location in which the "
                                  "database and files will be stored",
                                  expanduser("~"))

        if dlg_browse.ShowModal() == wx.ID_CANCEL:
            print "Selection aborted."
        else:
            self.tc_directory.SetValue(dlg_browse.GetPath())

    def on_ok(self, e):
        name = self.tc_name.GetValue()
        location = self.tc_directory.GetValue()
        dir = os.path.normpath(location)

        # TODO: Better sanitization
        if(name == ""):
            wx.MessageBox(
                'Please enter a name!',
                'Error',
                wx.OK | wx.ICON_EXCLAMATION)

            return

        if(location == ""):
            wx.MessageBox(
                'Please enter a location!',
                'Error',
                wx.OK | wx.ICON_EXCLAMATION)

            return

        if(not os.path.exists(dir) or not os.path.isdir(dir)):
            wx.MessageBox(
                'Invalid location!',
                'Error',
                wx.OK | wx.ICON_EXCLAMATION)

            return

        # Create Gallery
        gallery_id = database.create_gallery(name, dir)
        database.switch_gallery(gallery_id)

        self.Destroy()

    def on_close(self, e):
        self.Destroy()
