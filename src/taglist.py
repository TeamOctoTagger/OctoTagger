#!/usr/bin/python
# -*- coding: utf-8 --

import wx

TagListCheckEvent, EVT_TAGLIST_CHECK = wx.lib.newevent.NewCommandEvent()

# TODO: Find workaround for appearance of undetermined state in some GTK themes


class TagList(wx.ScrolledWindow):

    def __init__(self, parent, id, pos, size, tags):
        super(TagList, self).__init__(
            parent,
            style=wx.VSCROLL | wx.SIMPLE_BORDER,
            id=id,
            pos=pos,
            size=size,
        )

        self.SetBackgroundColour("#FFFFFF")
        self.tags = tags
        self.checked = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.SetScrollRate(10, 10)

        self.init_ui()

    def init_ui(self):
        for tag in self.tags:
            self.Insert(tag)

    def Insert(self, tag):
        checkbox = wx.CheckBox(
            self,
            label=tag,
            style=wx.CHK_3STATE,
        )
        self.sizer.Add(checkbox, 0, flag=wx.ALL, border=2)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def OnCheck(self, e):
        cb = e.GetEventObject()
        self.checked.append(cb.GetLabelText())
        wx.PostEvent(self, TagListCheckEvent(self.GetId()))

    def GetChecked(self):
        checked_cb = []

        for cb in self.GetItems():
            if cb.Get3StateValue() == wx.CHK_CHECKED:
                checked_cb.append(cb)
        return checked_cb

    def GetUndetermined(self):
        checked_cb = []

        for cb in self.GetItems():
            if cb.Get3StateValue() == wx.CHK_UNDETERMINED:
                checked_cb.append(cb)
        return checked_cb

    def GetCheckedStrings(self):
        checked_strings = []

        for cb in self.GetChecked():
            checked_strings.append(cb.GetLabelText())

        return checked_strings

    def GetItems(self):
        return self.GetChildren()

    def GetStrings(self):
        items = self.GetItems()
        item_strings = []

        for item in items:
            item_strings.append(item.GetLabelText())

        return item_strings

    def SetCheckedStrings(self, strings):
        items = self.GetItems()

        for item in items:
            if item.GetLabelText() in strings:
                item.Set3StateValue(wx.CHK_CHECKED)

    def GetUndeterminedStrings(self):
        undetermined_strings = []

        for cb in self.GetUndetermined():
            undetermined_strings.append(cb.GetLabelText())

        return undetermined_strings

    def SetUndeterminedStrings(self, strings):
        items = self.GetItems()

        for item in items:
            if item.GetLabelText() in strings:
                item.Set3StateValue(wx.CHK_UNDETERMINED)

    def Check(self, checkbox, state):
        checkbox.Set3StateValue(state)

    def CheckAll(self, state):
        for cb in self.GetItems():
            cb.Set3StateValue(state)
