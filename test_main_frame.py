#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The purpose of this frame is to create the dialogs.
It is only needed for development and testing reasons.
'''

import wx
import edit_output_folder
import about

class TestMainFrame(wx.Frame):
	"""Extending Frame"""
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (800, 600))

		self.CreateStatusBar() # Status Bar

		# Menu
		dialog_menu = wx.Menu()

		item_edit_output_folder = dialog_menu.Append(wx.NewId(), "Edit Output Folder", "Dialog for editing a specific output folder.")
		item_about = dialog_menu.Append(wx.NewId(), "&About", "About OctoTagger")

		# Create the menubar
		menubar = wx.MenuBar()
		menubar.Append(dialog_menu, "&Dialogs") # filemenu to menubar
		self.SetMenuBar(menubar) # menubar to frame

		# Set Events
		self.Bind(wx.EVT_MENU, self.OnEditOutputFolder, item_edit_output_folder)
		self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

		self.Show(True)

	def OnEditOutputFolder(self, e):
		dlg = edit_output_folder.EditOutputFolder(self)
		if dlg.ShowModal() == 5101:
        		dlg.Destroy()

	def OnAbout(self, e):
		wx.AboutBox(about.getInfo())

def main():
	app = wx.App()
	frame = TestMainFrame(None, 'Test Main Frame')
	app.MainLoop()

if __name__ == '__main__':
	main()
