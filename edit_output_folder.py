#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx

class EditOutputFolder(wx.Frame):
    """Extending Frame"""
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title = "Edit Output Folder", size = (600, 400))

        self.InitUI()
        self.Show(True)

    def InitUI(self):
        """Initialize User Interface"""

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # Define elements and add them to sizer
        # Labels
        txt_name = wx.StaticText(panel, label="Name: ")
        sizer.Add(txt_name, pos=(0,0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=10)

#        txt_expression = wx.StaticText(panel, label="Expression: ")
#        txt_directory = wx.StaticText(panel, label="Directory: ")

        # Text controls
        tc_name = wx.TextCtrl(panel)
        sizer.Add(tc_name, pos=(0, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND)
#        tc_expression = wx.TextCtrl(panel)
#        tc_directory = wx.TextCtrl(panel)

        # Define buttons
#        btn_browse = wx.Button(panel, label="Browse...")
#        btn_ok = wx.Button(panel, label="Ok")
#        btn_cancel = wx.Button(panel, label="Cancel")

        # Add elements to sizer
#        sizer.Add(txt_name, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=5)
#        sizer.Add(tc_name, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)

#        sizer.Add(btn_ok, pos=(3, 3))
#        sizer.Add(btn_cancel, pos=(3, 4), flag=wx.RIGHT|wx.BOTTOM, border=5)
        sizer.AddGrowableCol(1)
        panel.SetSizer(sizer)

# Run the window, for testing purposes. Needs to be removed eventually.

app = wx.App(False)
frame = EditOutputFolder(None)
app.MainLoop()
