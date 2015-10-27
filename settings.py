#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The dialog in which the user can perfrom various actions and set default values.
'''

import wx

class Settings(wx.Dialog):
#    """Extending Dialog"""
    def __init__(self, *args, **kw):
        super(Settings, self).__init__(*args, **kw)

        self.SetSize((400, 300))
        self.SetTitle("Settings")
        self.InitUI()

    def InitUI(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # Define elements and add them to sizer
        # Labels
        txt_symlink = wx.StaticText(panel, label="Default linking method: ")
        sizer.Add(txt_symlink, pos=(0,0), flag=wx.LEFT|wx.TOP, border=10)
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons
        btn_clear = wx.Button(panel, label="Clear all data")
        sizer.Add(btn_clear, pos=(2, 0), flag=wx.ALL, border=10)

        btn_integrity = wx.Button(panel, label="Perform integrity check")
        sizer.Add(btn_integrity, pos=(3, 0), flag=wx.ALL, border=10)

        btn_ok = wx.Button(panel, label="Ok")
        btn_sz.Add(btn_ok, flag=wx.ALL, border=5)
#        sizer.Add(btn_ok, pos=(5, 2), flag=wx.RIGHT|wx.BOTTOM, border=5)

        btn_cancel = wx.Button(panel, label="Cancel")
        btn_sz.Add(btn_cancel, flag=wx.ALL, border=5)
#        sizer.Add(btn_cancel, pos=(5, 3), flag=wx.RIGHT|wx.BOTTOM, border=5)
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnClose)

        sizer.Add(btn_sz, pos=(5, 1), flag=wx.ALL, border=5)

        # Radio buttons
        rb_softlinks = wx.RadioButton(panel, -1, "Softlinks", style = wx.RB_GROUP)
        sizer.Add(rb_softlinks, pos=(0, 1), flag=wx.ALL, border=5)

        rb_hardlinks = wx.RadioButton(panel, -1, "Hardlinks")
        sizer.Add(rb_hardlinks, pos=(1, 1), flag=wx.ALL, border=5)

        sizer.AddGrowableRow(4)
        panel.SetSizer(sizer)

    def OnClose(self, e):
        self.Destroy()
