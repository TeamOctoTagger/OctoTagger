#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx


class BulkCreateOutputFolders(wx.Dialog):
    """Extending Dialog"""
    def __init__(self, *args, **kw):
        super(BulkCreateOutputFolders, self).__init__(*args, **kw)

        self.SetSize((450, 500))
        self.SetTitle("Bulk create output folders")
        self.InitUI()

    def InitUI(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)
        sz_sel_btn = wx.BoxSizer(wx.VERTICAL)
        self.tags = [
            "gif", "iceland 2012", "meme", "human", "iceland 2012",
            "meme", "human", "iceland 2012", "meme", "human", "iceland 2012",
            "meme", "human", "iceland 2012", "meme", "human"
        ]

        # Define elements and add them to sizer
        # Labels

        txt_directory = wx.StaticText(panel, label="Directory: ")
        sizer.Add(
            txt_directory,
            pos=(0, 0),
            flag=wx.LEFT | wx.TOP,
            border=10
        )

        txt_tags = wx.StaticText(panel, label="Tags:")
        sizer.Add(
            txt_tags,
            pos=(1, 0),
            flag=wx.LEFT | wx.TOP,
            border=10
        )

        # Text controls

        tc_directory = wx.TextCtrl(panel)
        sizer.Add(
            tc_directory,
            pos=(0, 1),
            span=(1, 2),
            flag=wx.RIGHT | wx.TOP | wx.EXPAND,
            border=5
        )

        # Buttons

        btn_browse = wx.Button(panel, label="Browse...")
        sizer.Add(
            btn_browse,
            pos=(0, 3),
            flag=wx.TOP | wx.RIGHT,
            border=5
        )

        btn_select_all = wx.Button(panel, label="Select all")
        btn_select_all.Bind(wx.EVT_BUTTON, self.OnSelectAll)
        sz_sel_btn.Add(
            btn_select_all,
            0,
            wx.TOP | wx.BOTTOM | wx.EXPAND,
            5
        )

        btn_deselect_all = wx.Button(panel, label="Deselect all")
        btn_deselect_all.Bind(wx.EVT_BUTTON, self.OnDeselectAll)
        sz_sel_btn.Add(
            btn_deselect_all,
            0,
            wx.TOP | wx.BOTTOM | wx.EXPAND,
            5
        )

        sizer.Add(
            sz_sel_btn,
            pos=(2, 2),
            flag=wx.TOP,
            border=0
        )

        btn_ok = wx.Button(panel, label="Ok")
        sizer.Add(
            btn_ok,
            pos=(4, 2),
            flag=wx.RIGHT | wx.BOTTOM,
            border=5
        )

        btn_cancel = wx.Button(panel, label="Cancel")
        sizer.Add(
            btn_cancel,
            pos=(4, 3),
            flag=wx.RIGHT | wx.BOTTOM,
            border=5
        )
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)

        # Tags
        # Check list box
        lb = wx.CheckListBox(
            panel,
            wx.ID_ANY,
            (0, 0),
            wx.DefaultSize,
            self.tags
        )
        self.lb = lb
        sizer.Add(
            lb,
            pos=(2, 0),
            span=(1, 2),
            flag=wx.GROW | wx.ALL,
            border=10
        )

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(2)
        sizer.AddGrowableRow(3)
        panel.SetSizer(sizer)

    def OnSelectAll(self, e):
        for cb in range(self.lb.GetCount()):
            self.lb.Check(cb)

    def OnDeselectAll(self, e):
        for cb in self.lb.GetChecked():
            self.lb.Check(cb, False)

    def OnClose(self, e):
        self.Destroy()
