#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
#import edit_output_folder
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

        # A StatusBar in the bottom of the window
        self.CreateStatusBar()

        # Setting up the menus.
        self.filemenu = wx.Menu()
        toolmenu = wx.Menu()
        viewmenu = wx.Menu()
        helpmenu = wx.Menu()
        menu_open_database = self.get_gallery_menu()

        # FILEMENU
        fileNewDatabase = self.filemenu.Append(
            1,
            "&New database",
            " Create a new database"
        )
        self.filemenu.AppendMenu(wx.ID_ANY,
                                 "&Open gallery", menu_open_database)

        self.filemenu.AppendSeparator()
        fileImportFiles = self.filemenu.Append(
            3,
            "&Import Files",
            "Import files and folders into the program"
        )
        item_create_bulk_output_folders = self.filemenu.Append(
            wx.ID_ANY,
            "&Create output folders",
            "Automatically create an output folder for each tag"
        )
        item_create_output_folder = self.filemenu.Append(
            wx.ID_ANY,
            "&Create advanced output folder",
            "Dialog for editing a specific output folder"
        )
        self.filemenu.AppendSeparator()
        item_settings = self.filemenu.Append(
            wx.ID_ANY,
            "&Settings",
            "OctoTagger settings."
        )
        fileExit = self.filemenu.Append(
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
        menuBar.Append(self.filemenu, "&File")
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

        for gallery in menu_open_database.GetMenuItems():
            self.Bind(wx.EVT_MENU, self.on_switch_gallery, gallery)

        leftUpperPan = wx.Panel(self)
        leftUpperPan1 = wx.Panel(self)
        leftUpperPan2 = wx.Panel(self)
        leftUpperPan3 = wx.Panel(self)
        usertext = wx.TextCtrl(leftUpperPan, -1, "", size=(250, -1))
        self.mainPan = itemview.ItemView(self)
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
        mainBox.Add(self.mainPan, 3, wx.EXPAND)

        # Check current gallery

        current_gallery = database.get_current_gallery("id")
        for gallery in menu_open_database.GetMenuItems():
            if gallery.GetId() - 100 == current_gallery:
                gallery.Check()

        self.SetSizer(mainBox)
        self.Layout()
        self.Show(True)

        self.start_overview()

    # define events

    def start_overview(self):
        # Set items to all current database items
        # Get gallery connection

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = "SELECT pk_id FROM file"
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def get_gallery_menu(self):
        menu = wx.Menu()

        # Create list of galleries
        gallery_list = []

        # Get system connection

        sys_conn = database.get_sys_db()
        cursor = sys_conn.cursor()

        # Select galleries
        query_galleries = "SELECT pk_id, name FROM gallery"
        cursor.execute(query_galleries)
        result = cursor.fetchall()
        for gallery in result:
            gallery_list.append(gallery)

        # Open Database menu
        for gallery in gallery_list:
            item = wx.MenuItem(
                id=100 + gallery[0],
                text=gallery[1],
                help="Switch to database: " + gallery[1],
                kind=wx.ITEM_RADIO
            )
            menu.AppendItem(item)

        return menu

    def update_gallery_menu(self):
        self.filemenu.DeleteItem(
            self.filemenu.FindItemByPosition(1))
        self.filemenu.InsertMenu(1, wx.ID_ANY, "Open gallery",
                                 self.get_gallery_menu(), "")

    def on_switch_gallery(self, e):
        gallery_id = e.GetId() - 100
        database.switch_gallery(gallery_id)
        self.start_overview()

    def on_new_database(self, e):
        dlg = new_database.NewDatabase(self)
        dlg.ShowModal()
        self.update_gallery_menu()

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

        self.update_gallery_menu()

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
frame = MainWindow(None, "OctoTagger")
app.MainLoop()
