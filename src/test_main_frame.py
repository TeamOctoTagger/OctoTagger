#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The purpose of this frame is to create the dialogs.
It is only needed for development and testing reasons.
'''

import wx
import import_files
import create_output_folder
import edit_output_folder
import bulk_create_output_folders
import settings
import about


class TestMainFrame(wx.Frame):

    """Extending Frame"""

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 600))

        self.CreateStatusBar()  # Status Bar

        # Important variables
        self.current_db = "./default"

        # Menu
        dialog_menu = wx.Menu()

        item_import = dialog_menu.Append(
            wx.ID_ANY, "&Import files",
            "Import one or more files into the current database.")
        item_create_output_folder = dialog_menu.Append(
            wx.ID_ANY, "&Create Output Folder",
            "Dialog for creating a specific output folder")
        item_edit_output_folder = dialog_menu.Append(
            wx.ID_ANY, "&Edit Output Folder",
            "Dialog for editing a specific output folder")
        item_create_bulk_output_folders = dialog_menu.Append(
            wx.ID_ANY, "&Bulk create output folders",
            "Automatically create an output folder for each tag")
        item_clear_data = dialog_menu.Append(
            wx.ID_ANY, "&Clear all data",
            "Removes all databases and clears all private data.")
        item_settings = dialog_menu.Append(
            wx.ID_ANY, "&Settings",
            "OctoTagger settings.")
        item_about = dialog_menu.Append(
            wx.ID_ANY, "&About",
            "About OctoTagger")

        # Create the menubar
        menubar = wx.MenuBar()
        menubar.Append(dialog_menu, "&Dialogs")  # filemenu to menubar
        self.SetMenuBar(menubar)  # menubar to frame

        # Set Events
        self.Bind(wx.EVT_MENU, self.OnImport, item_import)
        self.Bind(
            wx.EVT_MENU, self.OnCreateOutputFolder, item_create_output_folder)
        self.Bind(
            wx.EVT_MENU, self.OnEditOutputFolder, item_edit_output_folder)
        self.Bind(wx.EVT_MENU, self.OnBulkCreate,
                  item_create_bulk_output_folders)
        self.Bind(wx.EVT_MENU, self.OnClearData, item_clear_data)
        self.Bind(wx.EVT_MENU, self.OnSettings, item_settings)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

        # self.Centre()
        self.Show(True)

    def OnImport(self, e):
        dlg_import = wx.FileDialog(self, "Import files", "", "",
                                   "All files (*.*)|*.*",
                                   wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            print "Import aborted."
        else:
            import_files.import_files(dlg_import.GetPaths(), self.current_db)

    def OnCreateOutputFolder(self, e):
        dlg = create_output_folder.CreateOutputFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnEditOutputFolder(self, e):
        dlg = edit_output_folder.EditOutputFolder(self, 1)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBulkCreate(self, e):
        dlg = bulk_create_output_folders.BulkCreateOutputFolders(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnClearData(self, e):
        dlg_clear = wx.MessageBox(
            'Are you sure you want to clear all data? '
            'This will remove all your databases.',
            'Information',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
        # If the user continues, ask if he wants to export his files.
        if dlg_clear == 2:
            dlg_export = wx.MessageBox(
                'Do you want to export your saved files? '
                'Click "Yes" if you want to keep your files, '
                'and "No" if you want to delete them. \n\n'
                'WARNING: You will not be able to retrieve your '
                'files again if you click "No"!', 'Export saved files?',
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
            if dlg_export == 2:
                print "Export files now"
            else:
                print "Delete files now"

        else:
            print "Aborted clearing of files"

    def OnSettings(self, e):
        dlg = settings.Settings(self)
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
