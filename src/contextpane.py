#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx


class ContextPane(wx.ScrolledWindow):

    def __init__(self, parent, size, octotagger):
        wx.ScrolledWindow.__init__(self, parent, size=size, style=wx.VSCROLL)

        # 0 = No selection
        # 1 = Single selection
        # 2 = Multiple selection
        self.selection = 0
        self.mode = "overview"
        self.octotagger = octotagger

        self.SetScrollRate(10, 10)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.InitUI()

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = {}

        select_all = wx.Button(
            self,
            label="Select All"
        )
        self.Bind(wx.EVT_BUTTON, self.SelectAll, select_all)
        buttons["select_all"] = select_all
        self.sizer.Add(select_all, 0, flag=wx.EXPAND)

        deselect_all = wx.Button(
            self,
            label="Deselect All"
        )
        self.Bind(wx.EVT_BUTTON, self.DeselectAll, deselect_all)
        buttons["deselect_all"] = deselect_all
        self.sizer.Add(deselect_all, 0, flag=wx.EXPAND)

        exit_tagging_view = wx.Button(
            self,
            label="Exit tagging view"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.on_resume_overview_mode,
            exit_tagging_view,
        )
        buttons["exit_tagging_view"] = exit_tagging_view
        self.sizer.Add(exit_tagging_view, 0, flag=wx.EXPAND)

        create_folder = wx.Button(
            self,
            label="Create folder"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.OnCreateOutputFolder,
            create_folder
        )
        buttons["create_folder"] = create_folder
        self.sizer.Add(create_folder, 0, flag=wx.EXPAND)

        return_overview = wx.Button(
            self,
            label="Return to overview"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.start_overview,
            return_overview
        )
        buttons["return_overview"] = return_overview
        self.sizer.Add(return_overview, 0, flag=wx.EXPAND)

        create_folder_from_expr = wx.Button(
            self,
            label="Create folder from current expression"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.CreateFolderFromExpression,
            create_folder_from_expr,
        )
        buttons["create_folder_from_expr"] = create_folder_from_expr
        self.sizer.Add(create_folder_from_expr, 0, flag=wx.EXPAND)

        item_edit = wx.Button(
            self,
            label="Edit folder"
        )
        self.Bind(wx.EVT_BUTTON, self.octotagger.EditFolder, item_edit)
        buttons["item_edit"] = item_edit
        self.sizer.Add(item_edit, 0, flag=wx.EXPAND)

        abort_import = wx.Button(
            self,
            label="Abort import"
        )
        self.Bind(wx.EVT_BUTTON, self.octotagger.start_overview, abort_import)
        buttons["abort_import"] = abort_import
        self.sizer.Add(abort_import, 0, flag=wx.EXPAND)

        import_all = wx.Button(
            self,
            label="Import all files"
        )
        self.Bind(wx.EVT_BUTTON, self.octotagger.ImportAll, import_all)
        buttons["import_all"] = import_all
        self.sizer.Add(import_all, 0, flag=wx.EXPAND)

        import_tagged = wx.Button(
            self,
            label="Import tagged files"
        )
        self.Bind(wx.EVT_BUTTON, self.octotagger.ImportTagged, import_tagged)
        buttons["import_tagged"] = import_tagged
        self.sizer.Add(import_tagged, 0, flag=wx.EXPAND)

        item_remove_import = wx.Button(
            self,
            label="Remove from import"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.RemoveItem,
            item_remove_import,
        )
        buttons["item_remove_import"] = item_remove_import
        self.sizer.Add(item_remove_import, 0, flag=wx.EXPAND)

        item_open = wx.Button(
            self,
            label="Open"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.OpenItem,
            item_open,
        )
        buttons["item_open"] = item_open
        self.sizer.Add(item_open, 0, flag=wx.EXPAND)

        item_remove = wx.Button(
            self,
            label="Remove"
        )
        self.Bind(wx.EVT_BUTTON, self.octotagger.RemoveItem, item_remove)
        buttons["item_remove"] = item_remove
        self.sizer.Add(item_remove, 0, flag=wx.EXPAND)

        item_restore = wx.Button(
            self,
            label="Restore"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.RestoreSelected,
            item_restore,
        )
        buttons["item_restore"] = item_restore
        self.sizer.Add(item_restore, 0, flag=wx.EXPAND)

        item_export = wx.Button(
            self,
            label="Export"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.ExportSelected,
            item_export,
        )
        buttons["item_export"] = item_export
        self.sizer.Add(item_export, 0, flag=wx.EXPAND)

        item_rename = wx.Button(
            self,
            label="Rename"
        )
        self.Bind(
            wx.EVT_BUTTON,
            self.octotagger.RenameItem,
            item_rename,
        )
        buttons["item_rename"] = item_rename
        self.sizer.Add(item_rename, 0, flag=wx.EXPAND)

        self.buttons = buttons
        self.SetMode()
        self.SetSizer(self.sizer)
        self.Layout()

    def Insert(self, name):
        self.buttons[name].Show(True)

    def Remove(self, name):
        self.buttons[name].Show(False)

    def SetMode(self, mode=None, selection=0):

        if mode is None:
            mode = self.mode
        else:
            self.mode = mode

        for button in self.GetChildren():
            button.Show(False)

        if mode == "overview":
            self.Insert("select_all")
            self.Insert("deselect_all")
            self.Insert("create_folder")

            if selection == 1:
                self.Insert("item_rename")
                self.Insert("item_open")

            if selection >= 1:
                self.Insert("item_remove")
                self.Insert("item_restore")
                self.Insert("item_export")

            if selection > 1:
                self.Remove("item_rename")

        elif mode == "tagging":
            self.Insert("exit_tagging_view")
            self.Insert("item_open")
            self.Insert("item_rename")
            self.Insert("item_remove")
            self.Insert("item_restore")
            self.Insert("item_export")

        elif mode == "folder":
            self.Insert("select_all")
            self.Insert("deselect_all")
            self.Insert("create_folder")
            self.Insert("return_overview")

            if selection == 1:
                self.Insert("item_open")
                self.Insert("item_edit")

            if selection >= 1:
                self.Insert("item_remove")

        elif mode == "import":
            self.Insert("select_all")
            self.Insert("deselect_all")
            self.Insert("abort_import")
            self.Insert("import_all")
            self.Insert("import_tagged")

            if selection > 0:
                self.Insert("item_remove_import")

        self.Layout()

    def SelectAll(self, event):
        self.octotagger.mainPan.SetSelectedAll(True)
        self.octotagger.on_selection_change()
        self.octotagger.mainPan.SetFocus()

    def DeselectAll(self, event):
        self.octotagger.mainPan.SetSelectedAll(False)
        self.octotagger.on_selection_change()
        self.octotagger.mainPan.SetFocus()

    def EnableAll(self, enable):
        for child in self.GetChildren():
            child.Enable(enable)

    def OnResize(self, event):
        self.Refresh()
        self.Layout()
