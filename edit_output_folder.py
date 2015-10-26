#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx

class EditOutputFolder(wx.Dialog):
#    """Extending Dialog"""
    def __init__(self, *args, **kw):
        super(EditOutputFolder, self).__init__(*args, **kw)

        self.SetSize((450, 350))
        self.SetTitle("Edit Output Folder")
        self.InitUI()

    def InitUI(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # Define elements and add them to sizer
        # Labels
        txt_name = wx.StaticText(panel, label="Name: ")
        sizer.Add(txt_name, pos=(0,0), flag=wx.LEFT|wx.TOP, border=5)

        txt_expression = wx.StaticText(panel, label="Expression: ")
        sizer.Add(txt_expression, pos=(1,0), flag=wx.LEFT|wx.TOP, border=5)

        txt_directory = wx.StaticText(panel, label="Directory: ")
        sizer.Add(txt_directory, pos=(2,0), flag=wx.LEFT|wx.TOP, border=5)

        # Text controls
        tc_name = wx.TextCtrl(panel)
        sizer.Add(tc_name, pos=(0, 1), span=(1, 3), flag=wx.RIGHT|wx.TOP|wx.EXPAND, border=5)

        tc_expression = wx.TextCtrl(panel)
        sizer.Add(tc_expression, pos=(1, 1), span=(1, 3), flag=wx.RIGHT|wx.TOP|wx.EXPAND, border=5)

        tc_directory = wx.TextCtrl(panel)
        sizer.Add(tc_directory, pos=(2, 1), span=(1, 3), flag=wx.RIGHT|wx.TOP|wx.EXPAND, border=5)

        # Buttons
        btn_browse = wx.Button(panel, label="Browse...")
        sizer.Add(btn_browse, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5)

        btn_ok = wx.Button(panel, label="Ok")
        sizer.Add(btn_ok, pos=(5, 3), flag=wx.RIGHT|wx.BOTTOM, border=5)

        btn_cancel = wx.Button(panel, label="Cancel")
        sizer.Add(btn_cancel, pos=(5, 4), flag=wx.RIGHT|wx.BOTTOM, border=5)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)

        # Advanced options
        sbox_advanced_title = wx.StaticBox(panel, -1, "Advanced options")
        sbox_advanced = wx.StaticBoxSizer(sbox_advanced_title, wx.VERTICAL)

        txt_symlink = wx.StaticText(panel, label="Type of symbolic link used:")
        sbox_advanced.Add(txt_symlink, flag=wx.LEFT|wx.TOP|wx.BOTTOM, border=5)

        rb_softlinks = wx.RadioButton(panel, -1, "Softlinks", style = wx.RB_GROUP)
        sbox_advanced.Add(rb_softlinks, flag=wx.LEFT|wx.BOTTOM, border=5)

        rb_hardlinks = wx.RadioButton(panel, -1, "Hardlinks")
        sbox_advanced.Add(rb_hardlinks, flag=wx.LEFT|wx.BOTTOM, border=5)

        sizer.Add(sbox_advanced, pos=(3,0), span=(0, 5), flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, border=10)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(4)
        panel.SetSizer(sizer)

    def OnClose(self, e):
        self.Destroy()
