#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The purpose of this frame is to create the dialogs.
It is only needed for development and testing reasons.
'''

import wx
import edit_output_folder
import bulk_create_output_folders
import about

class TestMainFrame(wx.Frame):
	"""Extending Frame"""
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (800, 600))

		self.CreateStatusBar() # Status Bar

		# Menu
		dialog_menu = wx.Menu()

		item_edit_output_folder = dialog_menu.Append(wx.ID_ANY, "&Edit Output Folder", "Dialog for editing a specific output folder")
		item_create_bulk_output_folders = dialog_menu.Append(wx.ID_ANY, "&Bulk create output folders", "Automatically create an output folder for each tag")
		item_about = dialog_menu.Append(wx.ID_ANY, "&About", "About OctoTagger")

		# Create the menubar
		menubar = wx.MenuBar()
		menubar.Append(dialog_menu, "&Dialogs") # filemenu to menubar
		self.SetMenuBar(menubar) # menubar to frame

		# Set Events
		self.Bind(wx.EVT_MENU, self.OnEditOutputFolder, item_edit_output_folder)
		self.Bind(wx.EVT_MENU, self.OnBulkCreate, item_create_bulk_output_folders)
		self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

		self.Centre()
		self.Show(True)

	def OnEditOutputFolder(self, e):
		dlg = edit_output_folder.EditOutputFolder(self)
		dlg.ShowModal()
		dlg.Destroy()

	def OnBulkCreate(self, e):
		dlg = bulk_create_output_folders.BulkCreateOutputFolders(self)
		dlg.ShowModal()
		dlg.Destroy()

	def OnAbout(self, e):
		wx.AboutBox(about.getInfo())

def main():
	app = wx.App()
	frame = TestMainFrame(None, 'Test Main Frame')
	app.MainLoop()

if __name__ == '__main__':
	main()
