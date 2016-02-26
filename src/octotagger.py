#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from autocomplete import AutocompleteTextCtrl
import about
import autocomplete
import contextpane
import create_folders
import create_gallery_folder
import create_output_folder
import database
import edit_gallery_folder
import edit_output_folder
import export
import expression
import import_files
import integrity
import itemview
import new_database
import output
import os
import re
import settings
import shutil
import subprocess
import suggestion
import sys
import tagging
import taglist
import taggingview
import wx

# TODO: Make everything more efficient, prevent unresponsive moments


class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280, 720))

        # Create_folders.create_folders()
        # Fix working directory
        if os.path.basename(os.getcwd()) == "src":
            os.chdir("..")

        # Modes: overview, tagging, import, folder
        self.mode = "overview"

        # Map of temporary files and tags, for import mode
        self.temp_file_tags = {}

        # Application theme
        cursor = database.get_sys_db().cursor()
        cursor.execute("SELECT use_dark_theme FROM settings")
        if cursor.fetchone()[0] == 1:
            self.dark_theme = True
        else:
            self.dark_theme = False

        # A StatusBar in the bottom of the window
        self.CreateStatusBar()

        # Setting icon
        self.SetIcon(wx.Icon("icons/logo.ico", wx.BITMAP_TYPE_ICO))

        # Disable warnings
        wx.Log.SetLogLevel(0)

        # Setting up the menus.
        self.filemenu = wx.Menu()
        toolmenu = wx.Menu()
        viewmenu = wx.Menu()
        helpmenu = wx.Menu()
        menu_open_database = self.get_gallery_menu()

        # File
        fileNewDatabase = self.filemenu.Append(
            wx.ID_ANY,
            "&New gallery",
            " Create a new gallery",
        )
        self.filemenu.AppendMenu(wx.ID_ANY,
                                 "&Open gallery",
                                 menu_open_database,
                                 )

        self.filemenu.AppendSeparator()
        self.fileImportFiles = self.filemenu.Append(
            wx.ID_ANY,
            "&Start file import process...",
            "Start the import process of files and folders"
        )
        self.fileDirectImportFiles = self.filemenu.Append(
            wx.ID_ANY,
            "&Direct file import",
            "Import files directly, without going through the process"
        )
        item_create_gallery_folder = self.filemenu.Append(
            wx.ID_ANY,
            "&Create gallery folder",
            "Create another gallery folder"
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

        # Tools
        self.toolStartTaggingMode = toolmenu.Append(
            wx.ID_ANY,
            "&Start tagging mode",
            "Enter the tagging mode"
        )
        toolRefreshThumbnails = toolmenu.Append(
            wx.ID_ANY,
            "&Refresh thumbnails",
            "Regenerate all existing thumbnail. Could take a while."
        )
        toolIntegrityCheck = toolmenu.Append(
            wx.ID_ANY,
            "&Perfrom integrity check",
            "Checks links and folder for consistency."
        )
        toolmenu.AppendSeparator()
        toolResetCurrentDatabase = toolmenu.Append(
            wx.ID_ANY,
            "&Reset current database",
            "Reset the current database"
        )
        self.toolDeleteDatabase = toolmenu.Append(
            wx.ID_ANY,
            "&Delete current database",
            "Completely removes the current database."
        )
        toolmenu.AppendSeparator()
        toolRestoreAllFiles = toolmenu.Append(
            wx.ID_ANY,
            "&Restore all files",
            " Restores all Files"
        )

        # View
        viewShowAllFiles = viewmenu.Append(
            wx.ID_ANY,
            "&Show all files",
            " Shows every file"
        )
        viewShowTaggedFiles = viewmenu.Append(
            wx.ID_ANY,
            "&Show tagged files",
            " Shows the tagged files only"
        )
        viewShowUntaggedFiles = viewmenu.Append(
            wx.ID_ANY,
            "&Show untagged files",
            " Shows the untagged files only"
        )
        viewmenu.AppendSeparator()
        viewShowOutputFolders = viewmenu.Append(
            wx.ID_ANY,
            "&Show output folders",
            " Shows the output folders"
        )

        # Help
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
        self.Bind(
            wx.EVT_MENU, self.on_start_folder_mode, viewShowOutputFolders)
        self.Bind(wx.EVT_MENU, self.start_overview, viewShowAllFiles)
        self.Bind(wx.EVT_MENU, self.on_show_tagged, viewShowTaggedFiles)
        self.Bind(wx.EVT_MENU, self.on_show_untagged, viewShowUntaggedFiles)
        self.Bind(wx.EVT_MENU, self.on_new_database, fileNewDatabase)
        self.Bind(wx.EVT_MENU, self.on_reset, toolResetCurrentDatabase)
        self.Bind(wx.EVT_MENU, self.OnRestoreAllFiles, toolRestoreAllFiles)
        self.Bind(wx.EVT_MENU, self.OnDeleteDatabase, self.toolDeleteDatabase)
        self.Bind(wx.EVT_MENU, self.OnRefreshThumbnails, toolRefreshThumbnails)
        self.Bind(wx.EVT_MENU, self.OnIntegrityCheck, toolIntegrityCheck)
        self.Bind(wx.EVT_MENU, self.on_start_import, self.fileImportFiles)
        self.Bind(
            wx.EVT_MENU,
            self.on_direct_import,
            self.fileDirectImportFiles,
        )
        self.Bind(wx.EVT_MENU, self.OnManual, helpManual)
        self.Bind(wx.EVT_MENU, self.OnExit, fileExit)

        self.Bind(
            wx.EVT_MENU,
            self.OnCreateGalleryFolder,
            item_create_gallery_folder,
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnCreateOutputFolder,
            item_create_output_folder,
        )

        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)

        self.Bind(wx.EVT_MENU, self.OnSettings, item_settings)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

        self.Bind(
            wx.EVT_MENU,
            self.start_tagging_mode,
            self.toolStartTaggingMode,
        )

        self.Bind(
            itemview.EVT_SELECTION_CHANGE,
            self.on_selection_change,
        )

        # Tag and Context Pane

        self.mainPan = itemview.ItemView(self)
        self.Bind(itemview.EVT_ITEM_DOUBLE_CLICK, self.on_double_click_item)
        self.Bind(itemview.EVT_ITEM_RIGHT_CLICK, self.on_right_click_item)

        # Save scroll position in order to prevent a reset
        self.scrolled = self.mainPan.GetViewStart()

        self.main_box = wx.BoxSizer(wx.HORIZONTAL)
        left_panel = wx.Panel(self, size=(300, -1), name="left_panel")
        left_panel_sz = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(left_panel_sz)

        tag_panel = wx.Panel(left_panel, name="tag_panel")
        tag_panel_sz = wx.BoxSizer(wx.VERTICAL)
        tag_panel.SetSizer(tag_panel_sz)

        query_field_panel = wx.Panel(
            tag_panel,
            size=(-1, 50),
            name="query_field_panel",
        )
        query_field_panel_sz = wx.BoxSizer(wx.HORIZONTAL)
        query_field_panel.SetSizer(query_field_panel_sz)

        tag_list_panel = wx.Panel(tag_panel)
        tag_list_panel_sz = wx.BoxSizer(wx.VERTICAL)
        tag_list_panel.SetSizer(tag_list_panel_sz)

        tag_panel_sz.Add(query_field_panel, 0, wx.EXPAND | wx.ALIGN_CENTER)
        tag_panel_sz.Add(tag_list_panel, 1, wx.EXPAND)

        template = "%s<b><u>%s</b></u>%s"

        def list_completer(a_list):
            def completer(query1):
                formatted, unformatted = list(), list()
                if query1:
                    unformatted = [item for item in a_list if query1 in item]
                    for item in unformatted:
                        s = item.find(query1)
                        formatted.append(
                            template % (item[:s], query1, item[s + len(query1):])
                        )

                print ("formatted: ", formatted)
                print ("unformatted: ", unformatted)
                return formatted, unformatted
            return completer

        self.tags = suggestion.get_suggestions(self.GetSelectedItems())

        self.query_field = autocomplete.AutocompleteTextCtrl(
            query_field_panel,
            completer=list_completer(self.tags),
            octotagger=self
        )

        self.current_query = ""
        self.checked_tags = []

        self.Bind(
            wx.EVT_TEXT,
            self.on_query_text,
            self.query_field,
        )

        self.Bind(
            wx.EVT_TEXT_ENTER,
            self.on_query_text_enter,
            self.query_field,
        )

        query_field_panel_sz.Add(
            self.query_field,
            1,
            wx.LEFT | wx.RIGHT | wx.UP,
            20)

        self.AddTopbar()

        self.cpane = contextpane.ContextPane(
            left_panel, size=(-1, 200), octotagger=self)

        left_panel_sz.Add(tag_panel, 1, wx.EXPAND)
        left_panel_sz.Add(
            self.cpane,
            0,
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
            border=15,
        )

        self.main_box.Add(left_panel, 0, wx.EXPAND)
        self.main_box.Add(self.mainPan, 1, wx.EXPAND)

        # Tag Pane

        self.lb_pan = tag_list_panel
        self.lb_sz = tag_list_panel_sz
        self.update_tag_list()

        # Key bindings
        # TODO: Are the manual IDs really a good idea?
        f2_id = 5050
        ctrl_a_id = 5051
        delete_id = 5052
        escape_id = 5053
        left_id = 5054
        right_id = 5055
        self.Bind(wx.EVT_MENU, self.RenameItem, id=f2_id)
        self.Bind(wx.EVT_MENU, self.OnCtrlA, id=ctrl_a_id)
        self.Bind(wx.EVT_MENU, self.RemoveItem, id=delete_id)
        self.Bind(wx.EVT_MENU, self.OnEscape, id=escape_id)
        self.Bind(wx.EVT_MENU, self.OnLeft, id=left_id)
        self.Bind(wx.EVT_MENU, self.OnRight, id=right_id)

        self.accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_F2, f2_id),
            (wx.ACCEL_NORMAL, wx.WXK_F1, helpManual.GetId()),
            (wx.ACCEL_CTRL, ord('A'), ctrl_a_id),
            (wx.ACCEL_NORMAL, wx.WXK_DELETE, delete_id),
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, escape_id),
            (wx.ACCEL_NORMAL, wx.WXK_LEFT, left_id),
            (wx.ACCEL_NORMAL, wx.WXK_RIGHT, right_id),
            (wx.ACCEL_NORMAL, wx.WXK_F5, toolRefreshThumbnails.GetId()),
        ])
        self.SetAcceleratorTable(self.accel_tbl)

        self.SetSizer(self.main_box)
        self.Layout()
        self.Show(True)

        self.start_overview()

    def AddTopbar(self):
        # Add Topbar
        topbar_sz = wx.BoxSizer(wx.HORIZONTAL)
        self.topbar = wx.Panel(self.mainPan)
        self.topbar.SetSizer(topbar_sz)

        self.current_directory = wx.StaticText(
            self.topbar,
            label="",
            style=(
                wx.ALIGN_CENTRE_HORIZONTAL |
                wx.ALIGN_CENTRE_VERTICAL |
                wx.ST_ELLIPSIZE_MIDDLE |
                wx.ST_NO_AUTORESIZE
            )
        )
        if self.dark_theme:
            self.topbar.SetBackgroundColour("#333333")
            self.current_directory.SetForegroundColour("#FFFFFF")

        self.btn_up = wx.Button(self.topbar, -1, "^")
        self.btn_up.Bind(wx.EVT_BUTTON, self.ChangeFolderUp)
        self.btn_up.Disable()

        topbar_sz.Add(self.btn_up, 0, wx.EXPAND)
        topbar_sz.Add(self.current_directory, 1, wx.ALIGN_CENTER | wx.ALIGN_CENTRE_VERTICAL)

        self.mainPan.mainsizer.Insert(0, self.topbar, 0, wx.EXPAND)
        self.topbar.Show(False)

    def on_start_import(self, e):
        dlg_import = wx.DirDialog(
            self,
            "Select the folder containing the "
            "files you want to import",
            style=wx.DD_DIR_MUST_EXIST | wx.DD_DEFAULT_STYLE,
            defaultPath=os.path.expanduser("~")
        )

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            return

        if self.mode == "tagging":
            self.mode = "import"
            self.on_resume_overview_mode()
        else:
            self.mode = "import"

        # Set Title
        self.SetTitle(
            "OctoTagger - Import mode (Changes are not saved automatically)"
        )

        # Set Items
        self.import_path = dlg_import.GetPath()
        self.InitImportFiles(self.import_path)

        items = self.GetFolderItems(self.import_path, True)
        self.mainPan.SetItems(items)
        self.topbar.Show(True)
        

        self.cpane.SetMode("import")
        self.update_tag_list()
        self.lb.EnableAll(False)
        self.query_field.Enable(False)
        self.mainPan.SetAcceleratorTable(self.accel_tbl)

        self.SetFocus()
        self.mainPan.Layout()
        self.mainPan.Refresh()
        self.current_directory.SetLabelText(self.import_path)

    def InitImportFiles(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                self.temp_file_tags[file_path] = []

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                self.temp_file_tags[dir_path] = []

    def GetFolderItems(self, path, isRoot=False):
        items = []
        folders = []
        files = []

        for item in os.listdir(path):

            item = os.path.join(path, item)

            if item not in self.temp_file_tags:
                print item, " is removed from import."
            elif os.path.isfile(item):
                files.append(item)
            elif os.path.isdir(item):
                folders.append(item)

        for folder in folders:
            # if not isRoot:
            #    item = os.path.join(path, folder)
            items.append(folder)

        for file in files:
            # if not isRoot:
            #    item = os.path.join(path, file)
            items.append(file)

        return items

    def CancelImportWarning(self):
        dlg_cancel = wx.MessageBox(
            'Do you really want to exit the import process? '
            'All your progress will be lost. '
            'The tags you have already assigned will not be saved, '
            'and nothing will be imported.\n',
            'In order to save your progress, please import beforehand. '
            'Click "Ok" to continue, and "Cancel" to return.'
            'Warning',
            wx.CANCEL | wx.OK | wx.CANCEL_DEFAULT | wx.ICON_WARNING
        )

        return dlg_cancel == wx.OK

    def on_direct_import(self, e):
        if self.mode == "import":
            if not self.CancelImportWarning():
                return

        dlg_import = wx.FileDialog(
            self,
            message="Import files",
            wildcard="All files (*.*)|*.*",
            style=wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST,
            defaultDir=os.path.expanduser("~")
        )

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            print "Import aborted."
        else:
            import_files.import_files(dlg_import.GetPaths())
            self.start_overview(False)

    def on_start_folder_mode(self, e=None):
        if self.mode == "import":
            if not self.CancelImportWarning():
                return

        elif self.mode == "tagging":
            # TODO: Find better solution than this
            self.on_resume_overview_mode()

        self.toolStartTaggingMode.Enable(enable=False)

        self.mode = "folder"

        # Set items to all current database items
        # Get gallery connection

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_gallery_folders = (
            "SELECT pk_id, location, name FROM gallery_folder"
        )
        query_special_folders = "SELECT pk_id, location, name FROM folder"

        cursor.execute(query_gallery_folders)
        gallery_folder_result = cursor.fetchall()

        cursor.execute(query_special_folders)
        special_folder_result = cursor.fetchall()

        folders = []

        for folder in gallery_folder_result:
            path = os.path.join(folder[1], folder[2])
            folders.append(path.encode('utf-8') + "|GALLERYFOLDER")

        for folder in special_folder_result:
            path = os.path.join(folder[1], folder[2])
            folders.append(unicode(path.encode('utf-8'), "utf-8"))

        self.update_gallery_menu()
        self.lb.EnableAll(False)
        self.cpane.SetMode("folder")

        # Set items
        self.mainPan.SetItems(folders)
        self.Refresh()
        self.Layout()
        self.mainPan.SetFocus()

    def on_show_tagged(self, e):
        if self.mode == "tagging":
            self.on_resume_overview_mode()
        else:
            self.mode = "overview"

        # Set items to all untagged files
        # Get gallery connection

        self.lb.EnableAll(True)
        self.toolStartTaggingMode.Enable(enable=True)

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = ("SELECT pk_id FROM file "
                       "WHERE pk_id IN "
                       "(select pk_fk_file_id FROM file_has_tag)")
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def on_show_untagged(self, e):
        if self.mode == "tagging":
            self.on_resume_overview_mode()
        else:
            self.mode = "overview"

        # Set items to all untagged files
        # Get gallery connection

        self.lb.EnableAll(True)
        self.toolStartTaggingMode.Enable(enable=True)

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = ("SELECT pk_id FROM file "
                       "WHERE pk_id NOT IN "
                       "(select pk_fk_file_id FROM file_has_tag)")
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def start_tagging_mode(self, e=None, start_file=None):
        if self.mode == "tagging":
            return
        else:
            self.mode = "tagging"

        # Disable unavailable menu items
        self.fileImportFiles.Enable(enable=False)
        self.fileDirectImportFiles.Enable(enable=False)

        self.items = self.mainPan.GetItems()
        self.selected_items = self.mainPan.GetSelectedItems()
        self.scrolled = self.mainPan.GetViewStart()

        self.main_box.Remove(self.mainPan)
        self.mainPan.Destroy()

        if start_file:
            self.mainPan = taggingview.TaggingView(
                self, self.items, start_file)
        elif self.selected_items:
            start_file = self.selected_items[0]
            self.mainPan = taggingview.TaggingView(
                self, self.items, start_file)
        else:
            self.mainPan = taggingview.TaggingView(self, self.items)

        self.Bind(
            taggingview.EVT_EXIT_TAGGING_VIEW,
            self.on_resume_overview_mode,
        )
        self.Bind(
            taggingview.EVT_ITEM_CHANGE,
            self.on_selection_change,
        )

        self.main_box.Add(self.mainPan, 1, wx.EXPAND)

        self.cpane.SetMode("tagging")

        self.Layout()
        self.Refresh()
        self.mainPan.ReSize()
        self.mainPan.SetFocus()

    def on_resume_overview_mode(self, event=None):

        self.fileImportFiles.Enable(enable=True)
        self.fileDirectImportFiles.Enable(enable=True)

        self.main_box.Remove(self.mainPan)
        self.mainPan.Destroy()
        self.mainPan = itemview.ItemView(self)
        self.Bind(itemview.EVT_ITEM_DOUBLE_CLICK, self.on_double_click_item)
        self.Bind(itemview.EVT_ITEM_RIGHT_CLICK, self.on_right_click_item)
        self.main_box.Add(self.mainPan, 1, wx.EXPAND)
        self.AddTopbar()
        self.update_tag_list()
        self.mode = "overview"

        self.start_overview()

    def on_query_text(self, e):

        if self.mode == "overview":
            if self.mainPan.GetSelectedItems():
                return

            else:
                query_input = e.GetEventObject().GetValue()
                self.lb.SetCheckedStrings(query_input.split(" "), only=True)
                self.current_query = query_input

                if query_input == "":
                    self.start_overview()
                    self.query_field.SetFocus()
                    self.cpane.Remove("create_folder_from_expr")

                else:
                    try:
                        parsed_query = expression.parse(query_input)
                    except:
                        return

                    self.cpane.Insert("create_folder_from_expr")

                    # Get file list
                    cursor = (
                        database.get_current_gallery("connection").cursor()
                    )
                    cursor.execute(
                        "SELECT pk_id FROM file WHERE %s" %
                        parsed_query
                    )
                    result = cursor.fetchall()

                    items = []
                    for item in result:
                        items.append(item[0])

                    if len(items) == 0:
                        # TODO: Show warning instead of nothing?
                        pass

                    # Display files
                    self.mainPan.SetItems(items)
                    self.Layout()

    def on_query_text_select(self, e):
        items = self.GetSelectedItems()
        tag = e.GetEventObject().GetValue()

        if not (items and tag):
            return

        for item in items:
            tagging.tag_file(item, tag)

        self.update_tag_list()
        self.select_tags()
        e.GetEventObject().Clear()

    def on_query_text_enter(self, e):
        self.tags = suggestion.get_suggestions(self.GetSelectedItems())
        #print ("selftags: ", self.tags)
        self.query_field.completer = self.list_completer(self.tags)
        items = self.GetSelectedItems()
        tag = e.GetEventObject().GetValue()

        if not (items and tag):
            return

        if (not re.match('^' + expression.REG_TAG_NAME + '$', tag) or
                tag == "False"):
            wx.MessageBox(
                ("Invalid input! Tag names can only contain letters, "
                 "numbers and underscores (which will be displayed "
                 "as a sapce). They must start with a letter.\n"
                 "For further information, consult the user manual."),
                "Error",
                wx.OK,
            )
            return

        for item in items:
            if self.mode == "import":

                # Create tag if necessary
                tag_id = tagging.create_tag(tag)

                # Append id
                if tag_id not in self.temp_file_tags[item]:
                    self.temp_file_tags[item].append(tag_id)

            else:
                tagging.tag_file(item, tag)

        self.update_tag_list()
        self.select_tags()
        e.GetEventObject().Clear()

    def list_completer(self, a_list):
        template = "%s<b><u>%s</b></u>%s"
        def completer(query2):
            formatted, unformatted = list(), list()
            if query2:
                unformatted = [item for item in a_list if query2 in item]
                for item in unformatted:
                    s = item.find(query2)
                    formatted.append(
                        template % (item[:s], query2, item[s + len(query2):])
                    )

            print ("formatted_2: ", formatted)
            print ("unformatted_2: ", unformatted)
            return formatted, unformatted
        return completer

    def start_overview(self, e=None, warn_import=True):
        # Set items to all current database items
        # Get gallery connection

        if self.mode == "import":
            if warn_import:
                if not self.CancelImportWarning():
                    return
            self.topbar.Show(False)
        elif self.mode == "tagging":
            self.on_resume_overview_mode()

        self.lb.EnableAll(True)
        self.toolStartTaggingMode.Enable(enable=True)
        self.mode = "overview"

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = "SELECT pk_id FROM file"
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()
        self.cpane.SetMode("overview")

        # Re-enable windows
        self.lb.EnableAll(True)
        self.query_field.Enable(True)
        self.SetTitle("OctoTagger")

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()
        self.mainPan.SetFocus()
        self.mainPan.Scroll(self.scrolled)
        print self.scrolled

    def on_selection_change(self, event=None):
        selection = len(self.GetSelectedItems())

        self.select_tags()
        if selection == 0:
            if self.mode == "import":
                self.query_field.SetValue("")
                self.query_field.Enable(False)
                self.lb.SetCheckedAll(False)
                self.lb.EnableAll(False)
            else:
                if self.current_query:
                    self.query_field.SetValue(self.current_query)
                    self.lb.SetCheckedStrings(self.checked_tags, only=True)
        elif selection > 0:
            self.query_field.SetValue("")
            if self.mode == "import":
                self.query_field.Enable(True)
                self.lb.EnableAll(True)

        if selection > 2:
            selection = 2
        self.cpane.SetMode(selection=selection)

        self.Refresh()
        self.Layout()

    def select_tags(self):

        if self.mode == "folder":
            return
        else:
            items = self.GetSelectedItems()

        self.SetCursorWaiting(True)

        if self.mode == "import":
            item_tags = {}
            for item in items:

                if item not in self.temp_file_tags:
                    self.temp_file_tags[item] = []
                    item_tags[item] = []

                else:
                    tag_ids = self.temp_file_tags[item]
                    tag_names = []
                    for tag_id in tag_ids:
                        tag_names.append(tagging.tag_id_to_name(tag_id))

                    item_tags[item] = tag_names
        elif self.mode in ["overview", "tagging"]:
            item_tags = {}
            for item in items:
                tag_ids = tagging.get_tags(item)
                tag_names = []
                for tag_id in tag_ids:
                    tag_names.append(tagging.tag_id_to_name(tag_id))

                item_tags[item] = tag_names
        else:
            return

        self.lb.CheckAll(wx.CHK_UNCHECKED)

        checked = []
        undetermined = []

        for item in items:
            tags = item_tags[item]

            if not (checked or undetermined):
                for tag in tags:
                    checked.append(tag)

            else:
                scrapbook = []
                for tag in checked:
                    scrapbook.append(tag)

                for checked_tag in scrapbook:
                    if checked_tag not in tags:
                        checked.remove(checked_tag)
                        undetermined.append(checked_tag)

                for tag in tags:
                    if tag not in checked:
                        undetermined.append(tag)

        self.lb.SetCheckedStrings(checked)
        self.lb.SetUndeterminedStrings(undetermined)
        self.SetCursorWaiting(False)

    def GetSelectedItems(self, path=None):
        if self.mode == "import":
            items = []
            if path:
                items.append(path)
                folder_items = []
                children = os.listdir(path)
                for child in children:
                    item = os.path.join(path, child)
                    folder_items.append(item)
            else:
                folder_items = self.mainPan.GetSelectedItems()

            for item in folder_items:
                if os.path.isdir(item):
                    # print "Folder: ", item
                    items = items + self.GetSelectedItems(item)
                else:
                    items.append(os.path.join(item))

            return items

        elif self.mode in ["overview", "folder"]:
            return self.mainPan.GetSelectedItems()

        elif self.mode == "tagging":
            return [self.mainPan.GetCurrentItem()]

    def ChangeFolder(self, path):
        self.SetCursorWaiting(True)
        self.Freeze()

        self.topbar.Show()
        self.current_directory.SetLabelText(path)
        if path == self.import_path:
            self.btn_up.Disable()
        else:
            self.btn_up.Enable()

        items = self.GetFolderItems(path)
        self.mainPan.SetItems(items)
        self.on_selection_change()
        self.Layout()
        self.Thaw()
        self.SetCursorWaiting(False)

    def ChangeFolderUp(self, event=None):
        directory_txt = self.current_directory.GetLabelText()
        directory = os.path.normpath(directory_txt)
        if directory == self.import_path:
            return
        else:
            new_dir = os.path.dirname(directory)
            self.ChangeFolder(new_dir)

    def SetCursorWaiting(self, waiting=True):
        if waiting:
            cursor = wx.StockCursor(wx.CURSOR_WAIT)
        else:
            cursor = wx.StockCursor(wx.CURSOR_ARROW)
        self.SetCursor(cursor)

    def on_tag_selected(self, e):
        if self.mode in ["overview", "import"]:
            self.SetCursorWaiting(True)

            items = self.GetSelectedItems()
            tags = self.lb.GetStrings()
            checked_tags = self.lb.GetCheckedStrings()
            undetermined_tags = self.lb.GetUndeterminedStrings()

            if items:
                # Files are selected -> tag them
                for item in items:
                    if self.mode == "overview":
                        item_tags = tagging.get_tag_names(item)
                        for tag in tags:
                            if(tag not in item_tags and tag in checked_tags):
                                tagging.tag_file(item, tag)

                            elif(tag in item_tags and
                                 tag not in checked_tags and
                                    tag not in undetermined_tags):
                                tagging.untag_file(item, tag)
                    elif self.mode == "import":
                        # Convert ID's to names
                        item_tag_ids = self.temp_file_tags[item]
                        item_tags = []
                        for item_tag_id in item_tag_ids:
                            item_tags.append(
                                tagging.tag_id_to_name(item_tag_id)
                            )

                        for tag in tags:
                            # Convert tag name to ID
                            tag_id = tagging.tag_name_to_id(tag)

                            # If tag should be added
                            if(tag not in item_tags and tag in checked_tags):

                                self.temp_file_tags[item].append(tag_id)

                            # If tag should be removed
                            elif(tag in item_tags and
                                 tag not in checked_tags and
                                    tag not in undetermined_tags):

                                self.temp_file_tags[item].remove(tag_id)

            else:
                # No files are selected -> filter them
                self.checked_tags = checked_tags
                self.query_field.SetValue(" ".join(checked_tags))

            self.SetCursorWaiting(False)

        elif self.mode == "tagging":
            item = self.mainPan.GetCurrentItem()
            tags = self.lb.GetStrings()
            checked_tags = self.lb.GetCheckedStrings()

            item_tags = tagging.get_tag_names(item)
            for tag in tags:
                if(tag not in item_tags and tag in checked_tags):
                    tagging.tag_file(item, tag)

                elif(tag in item_tags and tag not in checked_tags):
                    tagging.untag_file(item, tag)

    def update_tag_list(self, event=None):

        # Remove previous list

        self.lb_pan.DestroyChildren()

        tags = tagging.get_all_tags()

        self.lb = taglist.TagList(
            self.lb_pan,
            id=wx.ID_ANY,
            pos=(0, 0),
            size=(-1, -1),
            tags=tags,
        )

        self.lb_sz.Add(
            self.lb,
            1,
            wx.EXPAND | wx.ALL,
            20,
        )
        if event:
            self.lb.SetCheckedStrings(event.checked)
        self.Bind(taglist.EVT_TAGLIST_CHECK, self.on_tag_selected, self.lb)
        self.Bind(taglist.EVT_TAGLIST_UPDATE, self.update_tag_list, self.lb)
        self.Layout()
        self.Refresh()

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

        self.amount_galleries = len(gallery_list)
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

        menu_open_database = self.filemenu.FindItemByPosition(1)

        self.filemenu.DeleteItem(menu_open_database)
        menu_open_database = self.filemenu.InsertMenu(
            1,
            wx.ID_ANY,
            "Open gallery",
            self.get_gallery_menu(),
            "")

        # Check current gallery

        current_gallery = database.get_current_gallery("id")
        for gallery in menu_open_database.GetSubMenu().GetMenuItems():
            self.Bind(wx.EVT_MENU, self.on_switch_gallery, gallery)
            if gallery.GetId() - 100 == current_gallery:
                gallery.Check()

        if (self.amount_galleries == 1):
            self.toolDeleteDatabase.Enable(False)
        else:
            self.toolDeleteDatabase.Enable(True)

    def on_switch_gallery(self, e):
        gallery_id = e.GetId() - 100
        if not os.path.isfile(database.get_gallery(gallery_id, "file")):
            dlg = wx.MessageBox(
                ("Gallery not found. "
                 "Do you wish to remove it?"),
                "Error",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
                )
            if dlg == wx.YES:
                database.delete_gallery(gallery_id)

            self.update_gallery_menu()
        else:
            database.switch_gallery(gallery_id)
            self.start_overview()
            self.update_tag_list()

    def on_new_database(self, e):
        dlg = new_database.NewDatabase(self)
        dlg.ShowModal()
        self.start_overview()
        self.update_gallery_menu()
        self.update_tag_list()

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
        if dlg_export == 4:
            database.reset_gallery(database.get_current_gallery("id"))
            self.update_tag_list()

        elif dlg_export == 16:
            print "Canceled."

    def OnDeleteDatabase(self, e):
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
        if dlg_clear == wx.YES:
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
            if dlg_export == wx.YES:
                self.OnRestoreAllFiles()

            database.delete_gallery(database.get_current_gallery("id"))
            if self.mode == "tagging":
                self.on_resume_overview_mode()
            else:
                self.start_overview()

            self.update_gallery_menu()

    def OnManual(self, e):
        path = os.path.join("doc", "documentation.pdf")
        self.OpenItem(file=path)

    def OnExit(self, e):
        if self.mode == "import":
            if self.CancelImportWarning():
                self.Close(True)
        else:
            self.Close(True)

    def OnCreateGalleryFolder(self, event=None):
        dlg = create_gallery_folder.CreateGalleryFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

        if self.mode == "folder":
            self.on_start_folder_mode()

    def OnCreateOutputFolder(self, event=None):
        dlg = create_output_folder.CreateOutputFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

        if self.mode == "folder":
            self.on_start_folder_mode()

    def OnSettings(self, e):
        dlg = settings.Settings(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, e):
        wx.AboutBox(about.getInfo())

    def OnActivate(self, event):
        if self.mode != "tagging":
            if event.GetActive():
                self.mainPan.Scroll(self.scrolled)
            else:
                self.scrolled = self.mainPan.GetViewStart()

    def OnRefreshThumbnails(self, event=None):
        items = self.GetSelectedItems()
        if len(items) == 0 or self.mode != "overview":
            gallery_dir = database.get_current_gallery("directory")
            thumbnails = os.path.join(gallery_dir, "thumbnails")
            temp = os.path.join(thumbnails, "temp")

            shutil.rmtree(thumbnails)
            os.makedirs(temp)

            if self.mode == "overview":
                for child in self.mainPan.GetChildren():
                    if isinstance(child, itemview.Item):
                        child.LoadThumbnail()

        elif len(items) > 0 and self.mode == "overview":
            for item in items:
                cursor = database.get_current_gallery("connection").cursor()
                cursor.execute(
                    "SELECT uuid FROM file WHERE pk_id = ?",
                    (item,)
                )
                uuid = cursor.fetchone()[0]

                directory = database.get_current_gallery("directory")
                thumbnail = os.path.join(directory, "thumbnails", uuid)
                os.remove(thumbnail)
                self.mainPan.GetItemFromPath(item).LoadThumbnail()

    # Key events

    def OnEscape(self, event):
        if self.mode == "tagging":
            self.mainPan.OnExit()

    def OnRight(self, event):
        if self.mode == "tagging":
            self.mainPan.DisplayNext()
            self.select_tags()

    def OnLeft(self, event):
        if self.mode == "tagging":
            self.mainPan.DisplayPrev()
            self.select_tags()

    def OnCtrlA(self, event):
        if self.mode not in ["overview", "import", "folder"]:
            return

        if not self.mainPan.IsSelectedAll():
            self.mainPan.SetSelectedAll(True)
        else:
            self.mainPan.SetSelectedAll(False)

        self.select_tags()
        event.Skip()
        self.Layout()
        self.Refresh()

    def OnIntegrityCheck(self, event):
        result = integrity.check()
        text = ""

        if result['untracked']:
            text += (
                "The following files have been found in our database "
                "folder, but they have no entry in our database. "
                "Please move them somewhere else.\n\n"
            )
            for untracked in result['untracked']:
                text += untracked + "\n"
            text += "\n"

        if result['missing']:
            text += (
                "The following files are missing in our database folder. "
                "Please move them back.\n\n"
            )
            for missing in result['missing']:
                text += "{} ({})\n".format(*missing)
            text += "\n"

        if result['occupied']:
            text += (
                "The following output folders could not be created "
                "as the name is already taken. Please rename the files "
                "and run the check again.\n"
            )
            for occupied in result['occupied']:
                text += occupied + "\n"
            text + "\n"

        if text:
            dlg = wx.MessageDialog(
                self,
                text,
                "Integrity Check",
                wx.OK | wx.ICON_WARNING,
            )
        else:
            dlg = wx.MessageDialog(
                self,
                "Integrity checked",
                "Integrity Check",
                wx.OK | wx.ICON_INFORMATION,
            )

        dlg.ShowModal()
        dlg.Destroy()

    def on_double_click_item(self, e):

        if self.mode == "overview":
            item = e.item
            self.start_tagging_mode(item)

        elif self.mode == "import":
            item = e.item
            if os.path.isdir(item):
                self.ChangeFolder(item)
            else:
                print "Not a folder"

        elif self.mode == "folder":
            self.EditFolder()

    def on_right_click_item(self, e):

        menu = wx.Menu()

        if self.mode == "folder":

            if e.item:
                self.mainPan.OnRightMouseUp(e.item, e.modifiers)

            items = self.GetSelectedItems()

            if len(items) == 0:
                item_add = menu.Append(
                    wx.ID_ANY,
                    "Add folder",
                    "Create a new folder."
                )
                self.Bind(wx.EVT_MENU, self.OnCreateOutputFolder, item_add)

            elif len(items) == 1:
                if e.item.IsGalleryFolder():
                    kind = "gallery"
                else:
                    kind = "custom"

                item_edit = menu.Append(
                    wx.ID_ANY,
                    "Edit",
                    ("Edit this " + kind + " folder.")
                )
                self.Bind(wx.EVT_MENU, self.EditFolder, item_edit)
                item_open = menu.Append(
                    wx.ID_ANY,
                    "Open",
                    "Open file in with its default application."
                )
                self.Bind(wx.EVT_MENU, self.OpenItem, item_open)
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove",
                    ("Remove this " + kind + " folder from the "
                     "database (files remain untouched).")
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

            elif len(items) > 1:

                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove",
                    ("Remove the selected folders from the "
                     "database (files remain untouched).")
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

        elif self.mode == "overview":

            if e.item:
                # Clicked an item

                self.mainPan.OnRightMouseUp(e.item, e.modifiers)
                items = self.mainPan.GetSelectedItems()

                if len(items) == 1:
                    item_open = menu.Append(
                        wx.ID_ANY,
                        "Open",
                        "Open file in with its default application."
                    )
                    self.Bind(wx.EVT_MENU, self.OpenItem, item_open)
                    item_rename = menu.Append(
                        wx.ID_ANY,
                        "Rename",
                        "Rename this files."
                    )
                    self.Bind(wx.EVT_MENU, self.RenameItem, item_rename)
                item_refresh = menu.Append(
                    wx.ID_ANY,
                    "Refresh thumbnail",
                    "Regenerate the thumbnail of the selected files."
                )
                self.Bind(wx.EVT_MENU, self.OnRefreshThumbnails, item_refresh)
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Delete",
                    "Delete the selected files (this can not be undone)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)
                item_restore = menu.Append(
                    wx.ID_ANY,
                    "Restore",
                    ("Remove the selected files from the database and "
                     "move them to the desired location.")
                )
                self.Bind(wx.EVT_MENU, self.RestoreSelected, item_restore)
            else:
                query = self.query_field.GetValue()
                if query != "":
                    item_create_folder = menu.Append(
                        wx.ID_ANY,
                        "Create folder from current expression",
                        ("Create a special output folder from the "
                         "current expression.")
                    )
                    self.Bind(
                        wx.EVT_MENU,
                        self.CreateFolderFromExpression,
                        item_create_folder,
                    )

        elif self.mode == "tagging":

            item_open = menu.Append(
                wx.ID_ANY,
                "Open",
                "Open file in with its default application."
            )
            self.Bind(wx.EVT_MENU, self.OpenItem, item_open)
            item_rename = menu.Append(
                wx.ID_ANY,
                "Rename",
                "Rename this file."
            )
            self.Bind(wx.EVT_MENU, self.RenameItem, item_rename)
            item_remove = menu.Append(
                wx.ID_ANY,
                "Delete",
                "Delete this file (this can not be undone)."
            )
            self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)
            item_restore = menu.Append(
                wx.ID_ANY,
                "Restore",
                ("Remove this file from the database "
                 "and move it to the desired location.")
            )
            self.Bind(wx.EVT_MENU, self.RestoreSelected, item_restore)

        elif self.mode == "import":

            if e.item:
                self.mainPan.OnRightMouseUp(e.item, e.modifiers)

            items = self.mainPan.GetSelectedItems()

            if len(items) == 0:
                item_abort = menu.Append(
                    wx.ID_ANY,
                    "Abort import",
                    "Abort the import, all files remain where they are."
                )
                self.Bind(wx.EVT_MENU, self.start_overview, item_abort)
                item_import_all = menu.Append(
                    wx.ID_ANY,
                    "Import all",
                    "Import all files."
                )
                self.Bind(wx.EVT_MENU, self.ImportAll, item_import_all)
                item_import_tagged = menu.Append(
                    wx.ID_ANY,
                    "Import tagged",
                    "Import all files that have at least one tag assigned."
                )
                self.Bind(wx.EVT_MENU, self.ImportTagged, item_import_tagged)
            elif len(items) == 1:
                item_open = menu.Append(
                    wx.ID_ANY,
                    "Open",
                    "Open file in with its default application."
                )
                self.Bind(wx.EVT_MENU, self.OpenItem, item_open)

            if len(items) >= 1:
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove from import",
                    "Remove the selected items from the import "
                    "(they remain where they are)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

        if menu.GetMenuItemCount() > 0:
            self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))

    def CreateFolderFromExpression(self, event):
        query = self.query_field.GetValue()

        dlg = create_output_folder.CreateOutputFolder(self, expr=query)
        dlg.ShowModal()
        dlg.Destroy()

    def ImportAll(self, event):
        self.cpane.EnableAll(False)
        import_files.import_files(self.temp_file_tags)
        self.query_field.SetValue("")
        self.lb.SetCheckedAll(False)
        self.start_overview(warn_import=False)
        self.cpane.EnableAll(True)

    def ImportTagged(self, event):
        self.cpane.EnableAll(False)
        tagged_files = {}
        for item, tags in self.temp_file_tags.iteritems():
            if len(tags) > 0:
                tagged_files[item] = tags

        import_files.import_files(tagged_files)
        self.query_field.SetValue("")
        self.lb.SetCheckedAll(False)
        self.start_overview(warn_import=False)
        self.cpane.EnableAll(True)

    def EditFolder(self, event=None):
        if not self.mode == "folder":
            return

        items = self.mainPan.GetSelectedItems()
        if len(items) != 1:
            print "Can not edit more than one folder at once."
            return

        is_gf = self.mainPan.GetItemFromPath(items[0]).IsGalleryFolder()
        if is_gf:
            folder = tagging.gallery_path_to_id(items[0])
            dlg = edit_gallery_folder.EditGalleryFolder(self, folder)
        else:
            folder = tagging.advanced_path_to_id(items[0])
            dlg = edit_output_folder.EditOutputFolder(self, folder)

        dlg.ShowModal()

        self.on_start_folder_mode()

    def OpenItem(self, event=None, file=None):
        if file:
            path = file
        else:
            items = self.GetSelectedItems()
            print items
            if len(items) != 1:
                if self.mode == "import":
                    paths = self.mainPan.GetSelectedItems()
                    if len(paths) == 1 and os.path.isdir(paths[0]):
                        item = paths[0]
                    else:
                        return
                else:
                    return
            else:
                item = items[0]
                print items

            if self.mode in ["overview", "tagging"]:

                cursor = database.get_current_gallery("connection").cursor()
                cursor.execute(
                    ("SELECT uuid, file_name FROM file WHERE pk_id = ?"),
                    (item,)
                )
                result = cursor.fetchone()
                uuid = result[0]
                file_name = result[1]

                files_path = os.path.join(
                    database.get_current_gallery("directory"),
                    "files",
                )

                path = os.path.join(files_path, uuid)

            elif self.mode in ["folder", "import"]:
                path = item
            else:
                return

        if sys.platform.startswith('darwin'):
            subprocess.call(('open', path))
        elif os.name == 'nt':
            if file or self.mode in ["import", "folder"]:
                os.startfile(path)
            else:
                link_path = os.path.join(files_path, "temp_links", file_name)
                create_folders.symlink(path, link_path, True)
                os.startfile(link_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', path))

    def RenameItem(self, event=None):
        if self.mode == "tagging":
            old_name = self.mainPan.GetName()
        elif self.mode == "overview":
            items = self.GetSelectedItems()
            if len(items) == 1:
                item = items[0]
            else:
                return
            for child in self.mainPan.GetChildren():
                if child is not self.topbar and child.GetPath() == item:
                    old_name = child.GetText()
        else:
            return

        if not old_name:
            return

        dlg = wx.TextEntryDialog(
            self,
            "Enter a new name:",
            defaultValue=old_name,
        )
        dlg.ShowModal()
        new_name = dlg.GetValue()

        # TODO: Find out the constant name
        if dlg.GetReturnCode() == 5101:
            return

        if new_name == old_name:
            return

        dlg.Destroy()

        # Check if name already exists
        cursor = database.get_current_gallery("connection").cursor()
        cursor.execute(
            "SELECT file_name FROM file WHERE file_name = ?",
            (new_name,)
        )
        result = cursor.fetchone()
        if result:
            wx.MessageBox(
                ("There already are files with the same name. "
                 "It is recommended to give each file a unique name, "
                 "in order to prevent inconsistencies and unexpected "
                 "behaviour."),
                "Warning"
            )

        # Rename the file
        output.rename_file(self.GetSelectedItems()[0], new_name)

        if self.mode == "overview" and old_name != new_name:
            self.start_overview()

    def RestoreFiles(self, files, event=None):

        # Ask for target directory
        dlg_import = wx.DirDialog(
            self,
            "Select the location where you want to move "
            "files to.",
            style=wx.DD_DEFAULT_STYLE)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            # Restoration aborted
            return "ABORT"

        target_dir = dlg_import.GetPath()

        # Restore the files
        export.file(files, target_dir, move=True)

        self.select_tags()

        if self.mode == "overview":
            self.start_overview()

        dlg_complete = wx.MessageDialog(
            self,
            "Restoration complete.",
            "Message",
            wx.OK
        )
        dlg_complete.ShowModal()
        dlg_complete.Destroy()

    def OnRestoreAllFiles(self, event=None):

        # Get all file IDs
        gallery_conn = database.get_current_gallery("connection")
        c = gallery_conn.cursor()

        query_ids = "SELECT pk_id FROM file"
        c.execute(query_ids)
        result = c.fetchall()

        ids = []
        for id in result:
            ids.append(id[0])

        # Restore
        self.RestoreFiles(ids)

    def RestoreSelected(self, event=None):

        item = self.GetSelectedItems()
        self.RestoreFiles(item)

        if self.mode == "tagging":
            self.mainPan.RemoveItem(item[0])

    def RemoveItem(self, event=None):
        if self.mode == "folder":
            items = self.mainPan.GetSelectedItems()
            advanced_ids = []
            gallery_ids = []
            for item in items:
                obj = self.mainPan.GetItemFromPath(item)
                if obj.IsGalleryFolder():
                    gallery_ids.append(str(tagging.gallery_path_to_id(item)))
                else:
                    advanced_ids.append(str(tagging.advanced_path_to_id(item)))

            # Delete folders

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            for gallery_id in gallery_ids:
                output.delete_gallery(gallery_id)

            for advanced_id in advanced_ids:
                output.delete_folder(advanced_id)

            self.on_start_folder_mode()

        elif self.mode == "overview":

            items = self.mainPan.GetSelectedItems()
            ids = []

            amount = len(items)

            # Confirm action with user.
            if amount == 1:
                file_text = "this file"
                file_text_2 = (
                    "If you only want to remove this file from OctoTagger, "
                    "but keep it on your computer, use the 'Restore' "
                    "option instead."
                )
            elif amount > 1:
                file_text = "these " + str(amount) + " files"
                file_text_2 = (
                    "If you only want to remove these files from OctoTagger, "
                    "but keep them on your computer, use the 'Restore' "
                    "option instead."
                )
            elif amount == 0:
                return

            dlg = wx.MessageBox(
                ("You are about to permanently delete " +
                 file_text + " from your computer. "
                 "Are you sure you want to continue?\n\n" +
                 file_text_2),
                style=wx.ICON_EXCLAMATION | wx.YES_NO | wx.NO_DEFAULT
            )

            if dlg == wx.NO:
                return

            # Delete files
            self.mainPan.RemoveItem(items)

            for item in items:
                ids.append(str(item))

            for item in items:
                output.remove(item)

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_files = (
                "DELETE FROM file WHERE pk_id IN (%s)"
                % ", ".join(ids)
            )
            query_tags = (
                "DELETE FROM file_has_tag WHERE pk_fk_file_id IN (%s)"
                % ", ".join(ids)
            )
            cursor.execute(query_files)
            cursor.execute(query_tags)
            gallery.commit()

            self.select_tags()

        elif self.mode == "tagging":

            item = self.mainPan.GetCurrentItem()

            # Confirm with user

            dlg = wx.MessageBox(
                ("You are about to permanently delete this file " +
                 "from your computer. "
                 "Are you sure you want to continue?\n\n" +
                 "If you only want to remove this file from OctoTagger, "
                 "but keep it on your computer, use the 'Restore' "
                 "option instead."),
                style=wx.ICON_EXCLAMATION | wx.YES_NO | wx.NO_DEFAULT
            )
            if dlg == wx.NO:
                return

            # Delete files

            self.mainPan.RemoveItem(item)
            output.remove(item)

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_files = (
                "DELETE FROM file WHERE pk_id = %d"
                % item
            )
            query_tags = (
                "DELETE FROM file_has_tag WHERE pk_fk_file_id = %d"
                % item
            )
            cursor.execute(query_files)
            cursor.execute(query_tags)
            gallery.commit()

        elif self.mode == "import":

            # Get items to be removed
            sel_items = self.mainPan.GetSelectedItems()
            for item in sel_items:

                # Delete all children if a folder is removed
                if os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                del self.temp_file_tags[file_path]
                            except:
                                print "Item already removed"

                # Remove the item itself
                try:
                    del self.temp_file_tags[item]
                except:
                    print "Error removing item"

            # Update the import view
            self.mainPan.RemoveItem(sel_items)
            self.select_tags()
            self.Layout()

app = wx.App(False)
frame = MainWindow(None, "OctoTagger")
# import wx.lib.inspection
# wx.lib.inspection.InspectionTool().Show()
app.MainLoop()
