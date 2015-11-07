#!/usr/bin/env python

import wx
import edit_output_folder
import bulk_create_output_folders
import settings
import about
import itemview


class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280, 720))
        # self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar()  # A StatusBar in the bottom of the window

        # Setting up the menus.
        filemenu = wx.Menu()
        toolmenu = wx.Menu()
        viewmenu = wx.Menu()
        helpmenu = wx.Menu()

        # FILEMENU
        fileNewDatabase = filemenu.Append(
            1,
            "&New Database",
            " Create a new database"
        )
        fileOpenDatabase = filemenu.Append(
            2,
            "&Open Database",
            " Open an existing database"
        )
        filemenu.AppendSeparator()
        fileImportFiles = filemenu.Append(
            3,
            "&Import Files",
            "Import files and folders into the program"
        )
        item_create_bulk_output_folders = filemenu.Append(
            wx.ID_ANY,
            "&Create output folders",
            "Automatically create an output folder for each tag"
        )
        item_edit_output_folder = filemenu.Append(
            wx.ID_ANY,
            "&Create advanced output folder",
            "Dialog for editing a specific output folder"
        )
        filemenu.AppendSeparator()
        item_settings = filemenu.Append(
            wx.ID_ANY,
            "&Settings",
            "OctoTagger settings."
        )
        fileExit = filemenu.Append(
            wx.ID_EXIT, "&Exit", " Terminate the program")

        # TOOLMENU
        toolStartTaggingMode = toolmenu.Append(
            7,
            "&Start tagging mode",
            "Enter the tagging mode"
        )
        toolmenu.AppendSeparator()
        toolIntegrityCheck = toolmenu.Append(
            8,
            "&Integrity check",
            "Execute an Integrity check"
        )
        toolmenu.AppendSeparator()
        toolResetCurrentDatabase = toolmenu.Append(
            9,
            "&Reset current database",
            "Reset the current database"
        )
        item_clear_data = toolmenu.Append(
            wx.ID_ANY,
            "&Clear all data",
            "Removes all databases and clears all private data."
        )
        toolExportDatabase = toolmenu.Append(
            10,
            "&Export database",
            " Exports the current database"
        )
        toolmenu.AppendSeparator()
        toolRestoreAllFiles = toolmenu.Append(
            11,
            "&Restore all files",
            " Restores all Files"
        )

        # VIEWMENU
        viewShowAllFiles = viewmenu.Append(
            12,
            "&Show all files",
            " Shows every file"
        )
        viewShowTaggedFiles = viewmenu.Append(
            13,
            "&Show tagged files",
            " Shows the tagged files only"
        )
        viewShowUntaggedFiles = viewmenu.Append(
            14,
            "&Show untagged files",
            " Shows the untagged files only"
        )
        viewmenu.AppendSeparator()
        viewShowOutputFolders = viewmenu.Append(
            15,
            "&Show output folders",
            " Shows the output folders"
        )

        # HELPMENU
        helpManual = helpmenu.Append(
            6, "&User Manual", " How to use this program")
        item_about = helpmenu.Append(wx.ID_ANY, "&About", "About OctoTagger")

        # Creating the menubar
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu, "&File")
        # Adding the "toolmenu" to the MenuBar
        menuBar.Append(toolmenu, "&Tools")
        # Adding the "viewmenu" to the MenuBar
        menuBar.Append(viewmenu, "&View")
        # Adding the "helpmenu" to the MenuBar
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events
        self.Bind(wx.EVT_MENU, self.OnManual, helpManual)
        self.Bind(wx.EVT_MENU, self.OnExit, fileExit)
        self.Bind(wx.EVT_MENU, self.OnEditOutputFolder,
                  item_edit_output_folder)
        self.Bind(wx.EVT_MENU, self.OnBulkCreate,
                  item_create_bulk_output_folders)
        self.Bind(wx.EVT_MENU, self.OnClearData, item_clear_data)
        self.Bind(wx.EVT_MENU, self.OnSettings, item_settings)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

        panel1 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        usertext = wx.TextCtrl(panel1, -1, "", size=(200, -1))
        panel2 = itemview.ItemView(self)
        panel3 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        panel1.SetBackgroundColour("#3498db")
        panel3.SetBackgroundColour("#2ecc71")
        box = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.VERTICAL)

        box2.Add(panel1, 7, wx.EXPAND)
        box2.Add(panel3, 10, wx.EXPAND)

        box.Add(box2, 1, wx.EXPAND)
        box.Add(panel2, 3, wx.EXPAND)

        panel2.SetItems([
            {"name": "hello.jpg"},
            {"name": "todo.txt"},
            {"name": "bye.png"}
        ])

        self.SetSizer(box)
        self.Layout()
        self.Show(True)

    # define events

    def OnManual(self, e):
        dlg = wx.MessageDialog(
            self,
            "Octotagger is the best program and doesn't need any explanation!",
            "User Manual",
            wx.OK
        )
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)

    def OnEditOutputFolder(self, e):
        dlg = edit_output_folder.EditOutputFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBulkCreate(self, e):
        dlg = bulk_create_output_folders.BulkCreateOutputFolders(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnClearData(self, e):
        dlg_clear = wx.MessageBox(
            (
                'Are you sure you want to clear all data? '
                'This will remove all your databases.'
            ),
            'Information',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
        )
        # If the user continues, ask if he wants to export his files.
        if dlg_clear == 2:
            dlg_export = wx.MessageBox(
                (
                    'Do you want to export your saved files? '
                    'Click "Yes" if you want to keep your files, '
                    'and "No" if you want to delete them. '
                    '\n\nWARNING: You will not be able to retrieve '
                    'your files again if you click "No"!'
                ),
                'Export saved files?',
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
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

app = wx.App(False)
frame = MainWindow(None, "Octotagger")
app.MainLoop()

'''

import wx

class MyFrame(wx.Frame):
   def __init__(self, parent, ID, title):
       wx.Frame.__init__(self, parent, ID, title, size=(300, 250))

       panel1 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)
       panel2 = wx.Panel(self,-1, style=wx.SUNKEN_BORDER)

       panel1.SetBackgroundColour("BLUE")
       panel2.SetBackgroundColour("RED")

       box = wx.BoxSizer(wx.HORIZONTAL)
       box.Add(panel1, 2, wx.EXPAND)
       box.Add(panel2, 1, wx.EXPAND)

       self.SetAutoLayout(True)
       self.SetSizer(box)
       self.Layout()


app = wx.PySimpleApp()
frame = MyFrame(None, -1, "Sizer Test")
frame.Show()
app.MainLoop()
'''
