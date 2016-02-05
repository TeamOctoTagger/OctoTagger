#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import database
import os


class Settings(wx.Dialog):
    """Extending Dialog"""

    def __init__(self, *args, **kw):
        super(Settings, self).__init__(*args, **kw)

        self.SetSize((400, 400))
        self.SetTitle("Settings")
        self.InitUI()

    def InitUI(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sz_controls = wx.BoxSizer(wx.VERTICAL)

        # Default gallery path
        sz_gallery = wx.BoxSizer(wx.HORIZONTAL)
        txt_gallery = wx.StaticText(
            panel,
            label="Default gallery location:"
        )
        self.tc_gallery = wx.TextCtrl(panel)
        btn_gallery = wx.Button(panel, label="Browse...")
        self.Bind(wx.EVT_BUTTON, self.OnBrowseGallery, btn_gallery)
        sz_controls.Add(txt_gallery, 1, flag=wx.TOP | wx.LEFT, border=5)
        sz_gallery.Add(self.tc_gallery, 1, flag=wx.ALL, border=5)
        sz_gallery.Add(btn_gallery, 0, flag=wx.ALL, border=5)
        sz_controls.Add(sz_gallery, 0, flag=wx.EXPAND)

        # Default output folder path
        sz_folder = wx.BoxSizer(wx.HORIZONTAL)
        txt_folder = wx.StaticText(
            panel,
            label="Default folder location:"
        )
        self.tc_folder = wx.TextCtrl(panel)
        btn_folder = wx.Button(panel, label="Browse...")
        self.Bind(wx.EVT_BUTTON, self.OnBrowseFolder, btn_folder)
        sz_controls.Add(txt_folder, 1, flag=wx.TOP | wx.LEFT, border=5)
        sz_folder.Add(self.tc_folder, 1, flag=wx.ALL, border=5)
        sz_folder.Add(btn_folder, 0, flag=wx.ALL, border=5)
        sz_controls.Add(sz_folder, 0, flag=wx.EXPAND)

        # Symlink method
        sz_link = wx.BoxSizer(wx.HORIZONTAL)
        txt_link = wx.StaticText(
            panel,
            label="Default linking method:"
        )
        self.cb_link = wx.ComboBox(
            panel,
            value="Softlinks",
            choices=["Softlinks", "Hardlinks"],
            style=wx.CB_READONLY
        )
        sz_controls.Add(txt_link, 1, flag=wx.TOP | wx.LEFT, border=5)
        sz_link.Add(self.cb_link, 1, flag=wx.ALL, border=5)
        sz_controls.Add(sz_link, 0, flag=wx.EXPAND)

        # Import method
        sz_import = wx.BoxSizer(wx.HORIZONTAL)
        txt_import = wx.StaticText(
            panel,
            label="Import method:"
        )
        self.cb_import = wx.ComboBox(
            panel,
            value="Copy files",
            choices=["Copy files", "Move files"],
            style=wx.CB_READONLY
        )
        sz_controls.Add(txt_import, 1, flag=wx.TOP | wx.LEFT, border=5)
        sz_import.Add(self.cb_import, 1, flag=wx.ALL, border=5)
        sz_controls.Add(sz_import, 0, flag=wx.EXPAND)

        # Color theme
        sz_theme = wx.BoxSizer(wx.HORIZONTAL)
        txt_theme = wx.StaticText(
            panel,
            label="Color theme:",
        )
        self.cb_theme = wx.ComboBox(
            panel,
            value="Dark",
            choices=["Dark", "Bright"],
            style=wx.CB_READONLY,
        )
        sz_controls.Add(txt_theme, 1, flag=wx.TOP | wx.LEFT, border=5)
        sz_theme.Add(self.cb_theme, 1, flag=wx.ALL, border=5)
        sz_controls.Add(sz_theme, 0, flag=wx.EXPAND)

        # Sizer stuff
        sizer.Add(sz_controls, 1, flag=wx.EXPAND | wx.ALL, border=5)
        pn_empty1 = wx.Panel(panel)
        sizer.Add(pn_empty1, 1, flag=wx.EXPAND)

        # Buttons
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)
        pn_empty2 = wx.Panel(panel)
        btn_sz.Add(pn_empty2, 1, flag=wx.EXPAND)
        btn_ok = wx.Button(panel, label="Ok")
        btn_sz.Add(btn_ok, 0, flag=wx.ALL, border=5)
        btn_ok.Bind(wx.EVT_BUTTON, self.OnOk)
        btn_cancel = wx.Button(panel, label="Cancel")
        btn_sz.Add(btn_cancel, 0, flag=wx.ALL, border=5)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnExit)
        sizer.Add(btn_sz, 0, flag=wx.ALL | wx.EXPAND, border=5)

        panel.SetSizer(sizer)
        self.SetFocus()
        self.InitData()

    def InitData(self):
        # Get setting from database
        sys_db = database.get_sys_db()
        cursor = sys_db.cursor()
        cursor.execute(
            ("SELECT default_gallery_path, default_folder_path, "
             "use_softlink, import_copy, use_dark_theme "
             "FROM settings")
        )
        settings = cursor.fetchone()

        if settings[0] != "":
            default_gallery_path = os.path.abspath(settings[0])
        else:
            default_gallery_path = ""

        if settings[1] != "":
            default_folder_path = os.path.abspath(settings[1])
        else:
            default_folder_path = ""

        use_softlink = (settings[2] == 1)
        import_copy = (settings[3] == 1)
        use_dark_theme = (settings[4] == 1)
        self.use_dark_theme = use_dark_theme

        self.tc_gallery.SetValue(default_gallery_path)
        self.tc_folder.SetValue(default_folder_path)

        if use_softlink:
            self.cb_link.SetValue("Softlinks")
        else:
            self.cb_link.SetValue("Hardlinks")

        if import_copy:
            self.cb_import.SetValue("Copy files")
        else:
            self.cb_import.SetValue("Move files")

        if use_dark_theme:
            self.cb_theme.SetValue("Dark")
        else:
            self.cb_theme.SetValue("Bright")

        sys_db.commit()

    def OnBrowseGallery(self, event):
        path = os.path.normpath(self.tc_gallery.GetValue())
        dlg_select_dir = wx.DirDialog(
            self,
            "Choose the default location for new gallerries.",
            path,
        )

        if not dlg_select_dir.ShowModal() == wx.ID_CANCEL:
            self.tc_gallery.SetValue(dlg_select_dir.GetPath())

    def OnBrowseFolder(self, event):
        path = os.path.normpath(self.tc_folder.GetValue())
        dlg_select_dir = wx.DirDialog(
            self,
            "Choose the default location for output folders.",
            path,
        )

        if not dlg_select_dir.ShowModal() == wx.ID_CANCEL:
            self.tc_folder.SetValue(dlg_select_dir.GetPath())

    def OnExit(self, e):
        self.Destroy()

    def OnOk(self, e):
        # Get input
        default_gallery_path = self.tc_gallery.GetValue()
        default_folder_path = self.tc_folder.GetValue()

        if self.cb_link.GetValue() == "Softlinks":
            use_softlink = 1
        else:
            use_softlink = 0

        if self.cb_import.GetValue() == "Copy files":
            import_copy = 1
        else:
            import_copy = 0

        if self.cb_theme.GetValue() == "Dark":
            use_dark_theme = 1
        else:
            use_dark_theme = 0

        # Validate input
        if default_gallery_path != "":
            path = os.path.normpath(default_gallery_path)
            if not os.path.isdir(path):
                wx.MessageBox(
                    ("The given default gallery path does not exist. "
                     "Please create it first, change the location or "
                     "leave the field blank."),
                    "Error",
                )
                return
            else:
                default_gallery_path = path

        if default_folder_path != "":
            path = os.path.normpath(default_folder_path)
            if not os.path.isdir(path):
                wx.MessageBox(
                    ("The given default folder path does not exist. "
                     "Please create it first, change the location or "
                     "leave the field blank."),
                    "Error",
                )
                return
            else:
                default_folder_path = path

        if use_dark_theme != self.use_dark_theme:
            wx.MessageBox(
                ("For the theme change to take effect, please restart "
                 "the application."),
                "Notification",
            )

        # Write to database
        sys_db = database.get_sys_db()
        cursor = sys_db.cursor()
        cursor.execute(
            ("UPDATE settings SET "
             "default_gallery_path = ?, "
             "default_folder_path = ?, "
             "use_softlink = ?, "
             "import_copy = ?, "
             "use_dark_theme = ?"),
            (default_gallery_path,
             default_folder_path,
             use_softlink,
             import_copy,
             use_dark_theme)
        )
        sys_db.commit()
        self.Destroy()

'''
class Settings(wx.Dialog):
    """Extending Dialog"""
    def __init__(self, *args, **kw):
        super(Settings, self).__init__(*args, **kw)

        self.SetSize((400, 300))
        self.SetTitle("Settings")
        self.init_ui()

    def init_ui(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # Define elements and add them to sizer
        # Labels
        txt_symlink = wx.StaticText(panel, label="Default linking method: ")
        sizer.Add(txt_symlink, pos=(0, 0), flag=wx.LEFT | wx.TOP, border=10)
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons
        btn_clear = wx.Button(panel, label="Clear all data")
        sizer.Add(btn_clear, pos=(2, 0), flag=wx.ALL, border=10)

        btn_integrity = wx.Button(panel, label="Perform integrity check")
        sizer.Add(btn_integrity, pos=(3, 0), flag=wx.ALL, border=10)

        btn_ok = wx.Button(panel, label="Ok")
        btn_sz.Add(btn_ok, flag=wx.ALL, border=5)
#        sizer.Add(btn_ok, pos=(5, 2), flag=wx.RIGHT | wx.BOTTOM, border=5)
        btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)

        btn_cancel = wx.Button(panel, label="Cancel")
        btn_sz.Add(btn_cancel, flag=wx.ALL, border=5)
#        sizer.Add(btn_cancel, pos=(5, 3), flag=wx.RIGHT | wx.BOTTOM, border=5)
        btn_cancel.Bind(wx.EVT_BUTTON, self.on_close)

        sizer.Add(btn_sz, pos=(5, 1), flag=wx.ALL, border=5)

        # Radio buttons
        self.rb_softlinks = wx.RadioButton(
            panel,
            -1,
            "Softlinks",
            style=wx.RB_GROUP
        )
        sizer.Add(self.rb_softlinks, pos=(0, 1), flag=wx.ALL, border=5)

        self.rb_hardlinks = wx.RadioButton(
            panel,
            -1,
            "Hardlinks"
        )
        sizer.Add(self.rb_hardlinks, pos=(1, 1), flag=wx.ALL, border=5)

        sizer.AddGrowableRow(4)
        panel.SetSizer(sizer)
        self.init_settings()

    def init_settings(self):
        # Variable for storing setting
        use_softlinks = 1

        # Get setting from database
        sys_db = database.get_sys_db()
        cursor = sys_db.cursor()
        query_set_softlink = "SELECT use_softlink FROM settings"
        cursor.execute(query_set_softlink)
        result = cursor.fetchall()
        for setting in result:
            use_softlinks = setting[0]

        # Write setting to UI
        if use_softlinks == 1:
            self.rb_softlinks.SetValue(True)
            self.rb_hardlinks.SetValue(False)
        else:
            self.rb_softlinks.SetValue(False)
            self.rb_hardlinks.SetValue(True)

        sys_db.commit()

    def on_close(self, e):
        self.Destroy()

    def on_ok(self, e):
        # Get setting
        if self.rb_softlinks.GetValue():
            use = 1
        else:
            use = 0

        # Write to database
        sys_db = database.get_sys_db()
        cursor = sys_db.cursor()
        query_set_softlink = "UPDATE settings SET use_softlink = %d" % use
        cursor.execute(query_set_softlink)
        sys_db.commit()
        self.Destroy()
'''
