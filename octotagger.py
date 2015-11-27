#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import edit_output_folder
import create_output_folder
import bulk_create_output_folders
import settings
import about
import itemview
import database
import new_database
import import_files


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
        menu_open_database = wx.Menu()

        # Create list of galleries
        gallery_list = []

        # Get system connection

        sys_conn = database.get_sys_db()
        cursor = sys_conn.cursor()

        # Select galleries
        query_galleries = "SELECT pk_id, name FROM gallery"
        cursor.execute(query_galleries)
        galleries = cursor.fetchall()
        for gallery in galleries:
            gallery_list.append(gallery)

        print gallery_list

        # Open Database menu
        for gallery in gallery_list:
            menu_open_database.Append(
                100 + gallery[0],
                gallery[1],
                "Switch to database: " + gallery[1]
            )

        # TODO
        # Make switching functional
        # Make list updateable

        # FILEMENU
        fileNewDatabase = filemenu.Append(
            1,
            "&New database",
            " Create a new database"
        )
        filemenu.AppendMenu(wx.ID_ANY, "&Open database", menu_open_database)

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
        item_create_output_folder = filemenu.Append(
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
        tool_delete_database = toolmenu.Append(
            wx.ID_ANY,
            "&Delete current database",
            "Completely removes the current database."
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
        self.Bind(wx.EVT_MENU, self.on_new_database, fileNewDatabase)
        self.Bind(wx.EVT_MENU, self.on_reset, toolResetCurrentDatabase)
        self.Bind(wx.EVT_MENU, self.on_delete, tool_delete_database)
        self.Bind(wx.EVT_MENU, self.on_import, fileImportFiles)
        self.Bind(wx.EVT_MENU, self.OnManual, helpManual)
        self.Bind(wx.EVT_MENU, self.OnExit, fileExit)
        self.Bind(wx.EVT_MENU, self.OnCreateOutputFolder,
                  item_create_output_folder)
        self.Bind(wx.EVT_MENU, self.OnBulkCreate,
                  item_create_bulk_output_folders)
        self.Bind(wx.EVT_MENU, self.OnSettings, item_settings)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

        leftUpperPan = wx.Panel(self)
        leftUpperPan1 = wx.Panel(self)
        leftUpperPan2 = wx.Panel(self)
        leftUpperPan3 = wx.Panel(self)
        usertext = wx.TextCtrl(leftUpperPan, -1, "", size=(250, -1))
        mainPan = itemview.ItemView(self)
        leftLowerPan = wx.Panel(self)
        leftUpperPan.SetBackgroundColour("#3498db")
        leftUpperPan1.SetBackgroundColour("#3498db")
        leftUpperPan2.SetBackgroundColour("#3498db")
        leftUpperPan3.SetBackgroundColour("#3498db")
        leftLowerPan.SetBackgroundColour("#2ecc71")
        mainBox = wx.BoxSizer(wx.HORIZONTAL)
        leftBox = wx.BoxSizer(wx.VERTICAL)
        leftInnerBox = wx.BoxSizer(wx.HORIZONTAL)
        leftInnerBox2 = wx.BoxSizer(wx.VERTICAL)

        leftInnerBox2.Add(leftUpperPan3, 1, flag=wx.EXPAND | wx.ALIGN_CENTER)
        leftInnerBox2.Add(leftUpperPan, 8, flag=wx.EXPAND | wx.ALIGN_CENTER)

        leftInnerBox.Add(leftUpperPan1, 2, flag=wx.EXPAND | wx.ALIGN_CENTER)
        leftInnerBox.Add(leftInnerBox2, flag=wx.EXPAND | wx.ALIGN_CENTER)
        leftInnerBox.Add(leftUpperPan2, 2, flag=wx.EXPAND | wx.ALIGN_CENTER)

        leftBox.Add(
            leftInnerBox, proportion=7, flag=wx.EXPAND | wx.ALIGN_CENTER)
        leftBox.Add(
            leftLowerPan, proportion=10, flag=wx.EXPAND | wx.ALIGN_CENTER)

        mainBox.Add(leftBox, 1, wx.EXPAND)
        mainBox.Add(mainPan, 3, wx.EXPAND)

        self.SetSizer(mainBox)
        self.Layout()
        self.Show(True)

    # define events

    def on_new_database(self, e):
        dlg = new_database.NewDatabase(self)
        dlg.ShowModal()

    def on_reset(self, e):
        dlg_export = wx.MessageBox(
            (
                'This will remove all tags and output folders '
                'from the database \"%s\". Your files will remain. '
                'Do you want to continue?'
                % (database.get_current_gallery("name"))
            ),
            'Warning',
            wx.CANCEL | wx.OK | wx.CANCEL_DEFAULT | wx.ICON_WARNING
        )
        print dlg_export
        if dlg_export == 4:
            database.reset_gallery(database.get_current_gallery("id"))

        elif dlg_export == 16:
            print "Canceled."

    def on_delete(self, e):
        dlg_clear = wx.MessageBox(
            (
                'Are you sure you want to remove the database \"%s\"? '
                'This will remove all data associated with the database.'
                % (database.get_current_gallery("name"))
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
                    'your files again if you select "No"!'
                ),
                'Export saved files?',
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
            if dlg_export == 2:
                print "Export files now"
                # TODO: Export files!

            # Delete everything now!
            database.delete_gallery(database.get_current_gallery("id"))

        else:
            print "Aborted clearing of files"

    def on_import(self, e):
        dlg_import = wx.FileDialog(self, "Import files", "", "",
                                   "All files (*.*)|*.*",
                                   wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            print "Import aborted."
        else:
            import_files.import_files(dlg_import.GetPaths())

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

    def OnCreateOutputFolder(self, e):
        dlg = create_output_folder.CreateOutputFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBulkCreate(self, e):
        dlg = bulk_create_output_folders.BulkCreateOutputFolders(self)
        dlg.ShowModal()
        dlg.Destroy()

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



        mainPan.SetItems([
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
            "92996172-60c0-47e1-b447-d0bbeb9eab97",
        ])


'''

# TODO: Solve issue with displayed items (see above)
