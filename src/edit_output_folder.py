#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import database
import os
from os.path import expanduser
import expression
import tagging
import output


class EditOutputFolder(wx.Dialog):

    """Extending Dialog"""

    def __init__(self, *args, **kw):
        super(EditOutputFolder, self).__init__(*args, **kw)

        self.folder_id = args[-1]

        self.SetSize((450, 350))
        self.SetTitle("Edit Output Folder")
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

        txt_expression = wx.StaticText(panel, label="Expression: ")
        sizer.Add(
            txt_expression,
            pos=(1, 0),
            flag=wx.LEFT | wx.TOP,
            border=5
        )

        txt_directory = wx.StaticText(panel, label="Location: ")
        sizer.Add(
            txt_directory,
            pos=(2, 0),
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

        self.tc_expression = wx.TextCtrl(panel)
        sizer.Add(
            self.tc_expression,
            pos=(1, 1),
            span=(1, 3),
            flag=wx.RIGHT | wx.TOP | wx.EXPAND,
            border=5
        )

        self.tc_directory = wx.TextCtrl(panel)
        sizer.Add(
            self.tc_directory,
            pos=(2, 1),
            span=(1, 3),
            flag=wx.RIGHT | wx.TOP | wx.EXPAND,
            border=5
        )

        # Buttons
        btn_browse = wx.Button(panel, label="Browse...")
        btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
        sizer.Add(
            btn_browse,
            pos=(2, 4),
            flag=wx.TOP | wx.RIGHT,
            border=5
        )

        btn_ok = wx.Button(panel, label="Ok")
        btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        sizer.Add(
            btn_ok,
            pos=(5, 3),
            flag=wx.RIGHT | wx.BOTTOM,
            border=5
        )

        btn_cancel = wx.Button(panel, label="Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, self.on_close)
        sizer.Add(
            btn_cancel,
            pos=(5, 4),
            flag=wx.RIGHT | wx.BOTTOM,
            border=5
        )

        # Advanced options
        sbox_advanced_title = wx.StaticBox(panel, -1, "Advanced options")
        sbox_advanced = wx.StaticBoxSizer(sbox_advanced_title, wx.VERTICAL)

        txt_symlink = wx.StaticText(panel, label="Type of symbolic link used:")
        sbox_advanced.Add(
            txt_symlink,
            flag=wx.LEFT | wx.TOP | wx.BOTTOM,
            border=5
        )

        self.rb_softlinks = wx.RadioButton(panel, -1, "Softlinks",
                                           style=wx.RB_GROUP)
        sbox_advanced.Add(
            self.rb_softlinks,
            flag=wx.LEFT | wx.BOTTOM,
            border=5
        )

        self.rb_hardlinks = wx.RadioButton(panel, -1, "Hardlinks")
        sbox_advanced.Add(
            self.rb_hardlinks,
            flag=wx.LEFT | wx.BOTTOM,
            border=5
        )

        sizer.Add(
            sbox_advanced,
            pos=(3, 0),
            span=(0, 5),
            flag=wx.LEFT | wx.TOP | wx.RIGHT | wx.EXPAND,
            border=10
        )

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(4)
        panel.SetSizer(sizer)

        self.init_data()

    def init_data(self):

        # Define variables
        name = expr = location = ""
        softlink = True

        # Get connection
        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        # Get data
        query_folder = (
            "SELECT name, expression, location, use_softlink "
            "FROM folder WHERE pk_id = %d" % (self.folder_id)
        )
        cursor.execute(query_folder)
        result = cursor.fetchall()
        for properties in result:
            name = properties[0]
            expr = expression.convert_tag_id(
                properties[1],
                tagging.tag_id_to_name
            )
            location = os.path.normpath(properties[2])
            if properties[3] == 1:
                softlink = True
            else:
                softlink = False

        # Set data in UI
        self.tc_name.SetValue(name)
        self.tc_expression.SetValue(expr)
        self.tc_directory.SetValue(location)

        if softlink:
            self.rb_softlinks.SetValue(True)
            self.rb_hardlinks.SetValue(False)
        else:
            self.rb_softlinks.SetValue(False)
            self.rb_hardlinks.SetValue(True)

    def on_browse(self, e):
        dlg_browse = wx.DirDialog(self,
                                  "Choose a location in which the "
                                  "output folders will be generated",
                                  expanduser("~"))

        if dlg_browse.ShowModal() == wx.ID_CANCEL:
            print "Selection aborted."
        else:
            self.tc_directory.SetValue(dlg_browse.GetPath())

    def on_ok(self, e):

        # Check for valid input

        location = self.tc_directory.GetValue()
        dir = os.path.normpath(location)
        name = self.tc_name.GetValue()
        expr = expression.convert_tag_name(
            self.tc_expression.GetValue(),
            tagging.tag_name_to_id
        )

        if self.rb_softlinks.GetValue():
            softlink = True
        else:
            softlink = False
        output.change_link_type(self.folder_id, True, softlink)

        if(name == ""):
            wx.MessageBox(
                'Please enter a name!',
                'Error',
                wx.OK | wx.ICON_EXCLAMATION)

            return

        if(expr == ""):
            wx.MessageBox(
                'Please enter an expression!',
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

        # TODO: Implement relevent output functions
        output.move(self.folder_id, True, dir)
        output.rename(self.folder_id, True, name)
        output.change_expression(self.folder_id, expr)

        # Exit
        self.Destroy()

    def on_close(self, e):
        self.Destroy()
