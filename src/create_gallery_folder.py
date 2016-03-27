#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import tagging
import database
import output
import os


class CreateGalleryFolder(wx.Dialog):

    """Extending Dialog"""

    def __init__(self, *args, **kw):
        super(CreateGalleryFolder, self).__init__(*args, **kw)

        self.SetSize((550, 600))
        self.SetTitle("Create gallery folder")
        self.InitUI()

    def InitUI(self):
        """Initialize User Interface"""

        panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
        empty_panel = wx.Panel(self)
        self.tags = []
        for tag in tagging.get_all_tags():
            self.tags.append(tag.replace("_", " "))

        # Set sizers

        main_sz = wx.BoxSizer(wx.VERTICAL)
        main_sz.Add(panel, 1, flag=wx.EXPAND)
        self.SetSizer(main_sz)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sz_location = wx.BoxSizer(wx.HORIZONTAL)
        sz_name = wx.BoxSizer(wx.HORIZONTAL)
        sz_options = wx.BoxSizer(wx.HORIZONTAL)
        sz_symlinks = wx.BoxSizer(wx.VERTICAL)
        sz_automatic = wx.BoxSizer(wx.HORIZONTAL)
        sz_tags = wx.BoxSizer(wx.VERTICAL)
        sz_tags_body = wx.BoxSizer(wx.HORIZONTAL)
        sz_sel_btn = wx.BoxSizer(wx.VERTICAL)
        sz_close_btn = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(sz_location, 0, flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(sz_name, 0, flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(sz_options, 0, flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(sz_tags, 1, flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(sz_close_btn, 0, flag=wx.ALL | wx.EXPAND, border=5)

        sz_options.Add(sz_symlinks, 1, flag=wx.ALL, border=5)
        sz_options.Add(sz_automatic, 1, flag=wx.ALL, border=5)

        # Define elements and add them to sizers
        # Labels

        txt_directory = wx.StaticText(panel, size=(80, -1), label="Location:")
        sz_location.Add(txt_directory, 0, flag=wx.ALL, border=5)

        txt_name = wx.StaticText(panel, size=(80, -1), label="Name:")
        sz_name.Add(txt_name, 0, flag=wx.ALL, border=5)

        txt_tags = wx.StaticText(panel, label="Tags: ")
        sz_tags.Add(txt_tags, 0, flag=wx.ALL, border=5)

        txt_symlinks = wx.StaticText(panel, label="Symlink method:")
        sz_symlinks.Add(txt_symlinks, 0)

        # Text controls

        self.tc_directory = wx.TextCtrl(panel)
        sz_location.Add(self.tc_directory, 1,
                        flag=wx.ALL | wx.EXPAND, border=5)

        self.tc_name = wx.TextCtrl(panel)
        sz_name.Add(self.tc_name, 1, flag=wx.ALL | wx.EXPAND, border=5)

        # Radio buttons

        self.rb_softlinks = wx.RadioButton(panel, -1, "Softlinks")
        sz_symlinks.Add(self.rb_softlinks, 0, flag=wx.TOP | wx.LEFT, border=5)

        self.rb_hardlinks = wx.RadioButton(panel, -1, "Hardlinks")
        sz_symlinks.Add(self.rb_hardlinks, 0, flag=wx.LEFT, border=5)

        # Checkbox

        self.cb_automatic = wx.CheckBox(
            panel, label="Automatically add new tags", name="auto")
        sz_automatic.Add(self.cb_automatic, 0)

        # Buttons

        btn_browse = wx.Button(panel, label="Browse...")
        btn_browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
        sz_location.Add(btn_browse, 0, flag=wx.ALL, border=5)

        btn_select_all = wx.Button(panel, label="Select all")
        btn_select_all.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        sz_sel_btn.Add(btn_select_all, 0, flag=wx.ALL, border=5)

        btn_deselect_all = wx.Button(panel, label="Deselect all")
        btn_deselect_all.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        sz_sel_btn.Add(btn_deselect_all, 0, flag=wx.ALL, border=5)

        btn_ok = wx.Button(panel, label="Ok")
        btn_ok.Bind(wx.EVT_BUTTON, self.OnOk)
        sz_close_btn.Add(empty_panel, 1, flag=wx.ALL | wx.EXPAND, border=5)
        sz_close_btn.Add(btn_ok, 0, flag=wx.ALL, border=5)

        btn_cancel = wx.Button(panel, label="Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)
        sz_close_btn.Add(btn_cancel, 0, flag=wx.ALL, border=5)

        # Tags
        # Check list box
        self.lb = wx.CheckListBox(
            panel,
            wx.ID_ANY,
            (0, 0),
            wx.DefaultSize,
            self.tags
        )
        sz_tags_body.Add(self.lb, 1, flag=wx.ALL | wx.EXPAND, border=5)
        sz_tags_body.Add(sz_sel_btn, 0, flag=wx.ALL, border=5)
        sz_tags.Add(sz_tags_body, 1, flag=wx.ALL | wx.EXPAND, border=5)

        panel.SetSizerAndFit(sizer)
        self.Layout()

    def OnSelectAll(self, e):
        for cb in range(self.lb.GetCount()):
            self.lb.Check(cb)

    def OnDeselectAll(self, e):
        for cb in self.lb.GetChecked():
            self.lb.Check(cb, False)

    def OnBrowse(self, e):
        dlg_select_dir = wx.DirDialog(
            self,
            ("Choose a location in which the "
             "output folders will be generated"),
            os.path.expanduser("~"))

        if dlg_select_dir.ShowModal() == wx.ID_CANCEL:
            print "Selection aborted."
        else:
            self.tc_directory.SetValue(dlg_select_dir.GetPath())

    def OnOk(self, e):
        self.SaveSettings()
        self.EndModal(0)

    def OnClose(self, e):
        self.EndModal(0)

    def SaveSettings(self):

        # Register folders
        # Get gallery connection
        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        location = self.tc_directory.GetValue()
        name = self.tc_name.GetValue()
        if self.cb_automatic.GetValue():
            add_new_tag = 1
        else:
            add_new_tag = 0

        if self.rb_softlinks.GetValue():
            use_softlink = 1
        else:
            use_softlink = 0

        if not os.path.isdir(location):
            wx.MessageBox("Location does not exist!", "Error")
            return

        if name == "":
            wx.MessageBox("Must define a name.", "Error")
            return

        if os.path.isdir(os.path.join(location, name)):
            wx.MessageBox(
                ("Target folder already exists, "
                 "remove it first."),
                "Error",
            )
            return

        checked_tags = self.lb.GetCheckedStrings()
        tags = []
        for tag in checked_tags:
            tags.append(tagging.tag_name_to_id(tag.replace(" ", "_")))

        cursor.execute(
            (
                "INSERT INTO gallery_folder "
                "(name, location, add_new_tag, use_softlink) "
                "VALUES (:name, :location, :add_new_tag, :use_softlink)"
            ),
            {
                "name": name,
                "location": location,
                "add_new_tag": add_new_tag,
                "use_softlink": use_softlink
            }
        )
        gallery_conn.commit()

        cursor.execute(
            (
                "SELECT pk_id FROM gallery_folder "
                "WHERE name = :name "
                "AND location = :location "
            ),
            {
                "name": name,
                "location": location,
            }
        )
        folder_id = cursor.fetchone()[0]

        output.create_gallery(folder_id)
        for tag in tags:
            output.change_gallery(folder_id, tag, True)
