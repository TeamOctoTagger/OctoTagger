#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import database


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
