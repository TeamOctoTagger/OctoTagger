from __future__ import division

import thumbnail
import database
import os
import wx
import wx.lib.newevent
import threading


THUMBNAIL_SIZE = (128, 128)

SelectionChangeEvent, EVT_SELECTION_CHANGE = wx.lib.newevent.NewCommandEvent()
DoubleClickItemEvent, EVT_ITEM_DOUBLE_CLICK = wx.lib.newevent.NewCommandEvent()
RightClickItemEvent, EVT_ITEM_RIGHT_CLICK = wx.lib.newevent.NewCommandEvent()
ThumbnailLoadEvent, EVT_THUMBNAIL_LOAD = wx.lib.newevent.NewEvent()


class ItemView(wx.ScrolledWindow):

    def __init__(self, parent):
        super(ItemView, self).__init__(
            parent,
            style=wx.VSCROLL,
        )
        # Bright vs Dark theme
        # self.SetBackgroundColour("#c1c8c5")
        self.SetBackgroundColour("#444444")

        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.WrapSizer(wx.HORIZONTAL)

        self.mainsizer.Add(
            self.sizer,
            0,
            wx.EXPAND | wx.LEFT | wx.TOP,
            border=10)

        self.SetSizer(self.mainsizer)

        # scrollbars

        # TODO include text and border
        self.SetScrollRate(THUMBNAIL_SIZE[0] / 2, THUMBNAIL_SIZE[1] / 2)

        self.Bind(wx.EVT_SIZE, self.OnSize)

        # selections

        self.items = []
        self.breadcrumbs = []
        self.last_clicked = None

        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnContextBackground)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)

    def get_current_root(self):
        root = self.items
        for breadcrumb in self.breadcrumbs:
            root = root[breadcrumb]
        return root

    def update_items(self):
        self.sizer.Clear(True)

        root = self.get_current_root()
        if len(self.breadcrumbs) > 0:
            self.sizer.Add(
                Item(self, root['path'], "..", root['image']),
                flag=wx.ALL,
                border=10,
                userData=-1,
            )
        if type(root) is dict:
            root = root['path']

        for item in root:
            index = len(self.sizer.GetChildren())
            self.sizer.Add(
                Item(self, **item),
                flag=wx.ALL,
                border=5,
                userData=index,
            )
        self.Layout()
        self.AdjustScrollbars()

    def OnSize(self, event):
        # prevent horizontal overflow
        size = self.GetSize()
        vsize = self.GetVirtualSize()
        self.SetVirtualSize((size[0], vsize[1]))

        event.Skip()

    def OnMouseUp(self, event):
        target = event.GetEventObject()
        if target is self:
            # clicked outside of any item
            self.SetSelectedAll(False)
            wx.PostEvent(self, SelectionChangeEvent(self.GetId()))
            return

        if not target.GetClientRect().Contains(event.GetPosition()):
            # click dragged outside of target
            return

        while not isinstance(target, Item):
            # clicked on a child of the item
            target = target.GetParent()

        index = self.sizer.GetItem(target).GetUserData()

        if not (event.ControlDown() or event.ShiftDown()):
            # clear selection
            items = self.sizer.GetChildren()
            for item in items:
                item.GetWindow().SetSelected(False)

        if event.ShiftDown() and self.last_clicked is not None:
            items = self.sizer.GetChildren()
            direction = 1 if self.last_clicked < index else -1

            for i in range(self.last_clicked, index + direction, direction):
                items[i].GetWindow().SetSelected(
                    items[self.last_clicked].GetWindow().IsSelected()
                )
        else:
            target.ToggleSelected()

        self.last_clicked = index

        wx.PostEvent(self, SelectionChangeEvent(self.GetId()))

    def OnRightMouseUp(self, target, modifiers):
        # So that rightclicking an item selects it,
        # without removing a multiselection

        index = self.sizer.GetItem(target).GetUserData()

        selected = self.GetSelectedItems()
        path = target.GetPath()

        if modifiers:
            return

        elif path in selected:
            return

        # clear selection
        items = self.sizer.GetChildren()
        for item in items:
            item.GetWindow().SetSelected(False)

        target.ToggleSelected()

        self.last_clicked = index

        wx.PostEvent(self, SelectionChangeEvent(self.GetId()))

    def OnContextBackground(self, event):
        new_event = RightClickItemEvent(self.GetId(), item=None)
        wx.PostEvent(self, new_event)

    def OnMouseDouble(self, event):
        target = event.GetEventObject()

        if target is self:
            # clicked outside of any item
            return

        if not target.GetClientRect().Contains(event.GetPosition()):
            # click dragged outside of target
            return

        while not isinstance(target, Item):
            # clicked on a child of the item
            target = target.GetParent()

        index = self.sizer.GetItem(target).GetUserData()
        if index == -1:
            self.breadcrumbs.pop()
        else:
            self.breadcrumbs.append(index)

        self.last_clicked = None
        self.update_items()

    def SetItems(self, items):
        '''
        Sets which items are to be displayed. Pass ids from database as int or
        paths from filesystem as str.
        '''
        connection = database.get_current_gallery('connection').cursor()

        ids = map(str, filter(lambda x: type(x) == int, items))
        paths = filter(lambda x: type(x) == str, items)
        files = filter(os.path.isfile, paths)
        folders = filter(os.path.isdir, paths)
        gf = filter(
            lambda x: os.path.isdir("|".join(x.split("|")[0:-1])),
            paths,
        )

        connection.execute(
            "SELECT pk_id FROM file WHERE pk_id IN ({}) ORDER BY file_name"
            .format(','.join(ids))
        )
        ids = map(lambda x: x[0], connection.fetchall())

        files.sort(key=os.path.basename)
        folders.sort(key=os.path.basename)
        gf.sort(key=os.path.basename)

        items = gf
        items.extend(folders)
        items.extend(files)
        items.extend(ids)

        def parse_items(items):
            result = []
            for item in items:
                if type(item) is int:  # item is db id
                    connection.execute(
                        (
                            'SELECT file_name '
                            'FROM file '
                            'WHERE file.pk_id=:id '
                        ),
                        {
                            'id': item,
                        }
                    )
                    row = connection.fetchone()
                    if row is None:
                        raise ValueError('Item not found in database', item)

                    result.append({
                        'name': row[0],
                        'path': item,
                    })
                elif type(item) is str:  # item is fs path
                    splitted_item = item.split("|")
                    if splitted_item.pop() == "GALLERYFOLDER":
                        is_gf = True
                        item = "|".join(splitted_item)
                    else:
                        is_gf = False

                    name = os.path.basename(item)
                    if os.path.isdir(item):
                        result.append({
                            'name': name,
                            'path': item,
                            'thumb': thumbnail.GENERIC['folder'],
                            'is_gf': is_gf,
                        })
                    elif os.path.isfile(item):
                        result.append({
                            'name': name,
                            'path': item,
                        })
                    else:
                        print ('Encountered unsupported path', item)

                else:
                    raise TypeError('Encountered unsupported item', item)
            return result

        self.items = parse_items(items)
        self.update_items()

    def GetSelectedItems(self):
        result = []
        items = self.sizer.GetChildren()

        for item in items:
            if item.GetWindow().IsSelected():
                result.append(item.GetWindow().GetPath())

        return result

    def SetSelectedItems(self, selected):
        items = self.sizer.GetChildren()

        for item in items:
            if item.GetWindow().GetPath in selected:
                item.GetWindow().SetSelected(True)

    def GetItems(self):
        result = []
        items = self.sizer.GetChildren()

        for item in items:
            result.append(item.GetWindow().GetPath())

        return result

    def GetItemFromPath(self, path):
        try:
            path = int(path)
        except:
            pass

        items = self.GetChildren()
        for item in items:
            if item != self.GetParent().topbar:
                if item.GetPath() == path:
                    return item

    def IsSelectedAll(self):
        items = self.sizer.GetChildren()
        for item in items:
            if not item.GetWindow().IsSelected():
                return False

        return True

    def SetSelectedAll(self, selected=True):
        items = self.sizer.GetChildren()
        for item in items:
            item.GetWindow().SetSelected(selected)

    def RemoveItem(self, paths):
        # FIXME: Update item view correctly
        for path in paths:
            item = self.GetItemFromPath(path)
            print path, item
            self.sizer.Remove(item)
            item.Destroy()

        self.last_clicked = None
        self.Layout()

        for item in self.items:
            if item["path"] in paths:
                self.items.remove(item)


class _ThumbnailThread(threading.Thread):
    def __init__(self, notify_window, path, thumb):
        super(_ThumbnailThread, self).__init__()
        self._notify_window = notify_window
        self._path = path
        self._thumb = thumb

    def run(self):
        if self._thumb is None:
            self._thumb = thumbnail.get_thumbnail(self._path)
        image = wx.Image(self._thumb)
        image.Resize(THUMBNAIL_SIZE, (
            (THUMBNAIL_SIZE[0] - image.GetWidth()) / 2,
            (THUMBNAIL_SIZE[1] - image.GetHeight()) / 2,
        ))
        wx.PostEvent(self._notify_window, ThumbnailLoadEvent(data=image))


class Item(wx.Panel):

    def __init__(self, parent, path, name, thumb=None, is_gf=False):
        super(Item, self).__init__(parent)

        self.path = path
        self.is_gf = is_gf
        self.selected = False

        self.UpdateBackground()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # controls

        # image = wx.Image(image)
        image = wx.Image(thumbnail.DEFAULT_ICON)
        image.Resize(THUMBNAIL_SIZE, (
            (THUMBNAIL_SIZE[0] - image.GetWidth()) / 2,
            (THUMBNAIL_SIZE[1] - image.GetHeight()) / 2,
        ))
        self.bitmap = wx.StaticBitmap(
            self,
            bitmap=image.ConvertToBitmap()
        )

        self.Bind(EVT_THUMBNAIL_LOAD, self.OnThumbnailLoad)
        self.thumb_thread = _ThumbnailThread(self, path, thumb)
        self.thumb_thread.start()

        self.sizer.Add(
            self.bitmap,
            flag=wx.ALL,
            border=2
        )

        self.text = wx.StaticText(
            self,
            label=name,
            style=(
                wx.ALIGN_CENTRE_HORIZONTAL |
                wx.ST_NO_AUTORESIZE |
                wx.ST_ELLIPSIZE_END
            )
        )
        self.text.SetMaxSize((THUMBNAIL_SIZE[0], -1))

        # For dark theme
        self.text.SetForegroundColour("#FFFFFF")

        self.sizer.Add(
            self.text,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER,
            border=5
        )

        self.Layout()

        # ToolTip
        tooltip = wx.ToolTip(name)
        tooltip.SetDelay(1000)
        self.SetToolTip(tooltip)

        # events

        self.Bind(wx.EVT_LEFT_UP, self.PropagateEvent)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)

        self.bitmap.Bind(wx.EVT_LEFT_UP, self.PropagateEvent)
        self.bitmap.Bind(wx.EVT_RIGHT_UP, self.PropagateEvent)
        self.bitmap.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)
        self.bitmap.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)

        self.text.Bind(wx.EVT_LEFT_UP, self.PropagateEvent)
        self.text.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)
        self.text.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)

    def OnThumbnailLoad(self, event):
        self.bitmap.SetBitmap(event.data.ConvertToBitmap())
        self.thumb_thread = None

    def GetPath(self):
        return self.path

    def GetText(self):
        return self.text.GetLabelText()

    def IsGalleryFolder(self):
        return self.is_gf

    def PropagateEvent(self, event):
        event.ResumePropagation(1)
        event.Skip()

    def UpdateBackground(self):
        if self.selected:
            color = "#3bb1d8"
        else:
            color = self.GetParent().GetBackgroundColour()
        self.SetBackgroundColour(color)

    def IsSelected(self):
        return self.selected

    def SetSelected(self, selected):
        self.selected = selected
        self.UpdateBackground()

    def ToggleSelected(self):
        self.selected = not self.selected
        self.UpdateBackground()

    def OnMouseDouble(self, event):
        new_event = DoubleClickItemEvent(self.GetId(), item=self.path)
        wx.PostEvent(self, new_event)

    def OnMouseRight(self, event):
        modifiers = event.ControlDown() or event.ShiftDown()
        new_event = RightClickItemEvent(
            self.GetId(),
            item=self,
            modifiers=modifiers
        )
        wx.PostEvent(self, new_event)
