#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The purpose of this frame is to create the dialogs.
It is only needed for development and testing reasons.
'''

import wx
import edit_output_folder

class TestMainFrame(wx.Frame):
	"""Extending Frame"""
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (800, 600))

		self.CreateStatusBar() # Status Bar

		# Menu
		dialog_menu = wx.Menu()

		menu_edit_output_folder = dialog_menu.Append(wx.NewId(), "Edit Output Folder", "Dialog for editing a specific output folder.")

		# Create the menubar
		menubar = wx.MenuBar()
		menubar.Append(dialog_menu, "&Dialogs") # filemenu to menubar
		self.SetMenuBar(menubar) # menubar to frame

		# Set Events
		self.Bind(wx.EVT_MENU, self.OnEditOutputFolder, menu_edit_output_folder)

		self.Show(True)

	def OnEditOutputFolder(self, e):
		dlg = edit_output_folder.EditOutputFolder(self)
		if dlg.ShowModal() == 5101:
        		dlg.Destroy()

def main():
	app = wx.App()
	frame = TestMainFrame(None, 'Test Main Frame')
	app.MainLoop()

if __name__ == '__main__':
	main()
