from __future__ import division

import thumbnail
import database
import os
import wx
import wx.lib.newevent


THUMBNAIL_SIZE = (128, 128)

SelectionChangeEvent, EVT_SELECTION_CHANGE = wx.lib.newevent.NewCommandEvent()
DoubleClickItemEvent, EVT_ITEM_DOUBLE_CLICK = wx.lib.newevent.NewCommandEvent()
RightClickItemEvent, EVT_ITEM_RIGHT_CLICK = wx.lib.newevent.NewCommandEvent()

# TODO: Load thumbnails in background


class ItemView(wx.ScrolledWindow):

    def __init__(self, parent):
        super(ItemView, self).__init__(
            parent,
            style=wx.VSCROLL,
        )
        self.SetBackgroundColour("#c1c8c5")

        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.WrapSizer(wx.HORIZONTAL)

        self.mainsizer.Add(self.sizer, 0, wx.EXPAND)
        self.SetSizer(self.mainsizer)

        # scrollbars

        # TODO include text and border
        self.SetScrollRate(THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])

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
                border=5,
                userData=-1,
            )
        if type(root) is dict:
            root = root['path']

        for item in root:
            index = len(self.sizer.GetChildren())
            if 'is_gf' in item:
                new_item = Item(self,
                                item['path'],
                                item['name'],
                                item['image'],
                                item['is_gf'])
            else:
                new_item = Item(
                    self,
                    item['path'],
                    item['name'],
                    item['image'],
                )
            self.sizer.Add(
                new_item,
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

        connection.execute(
            "SELECT pk_id FROM file WHERE pk_id IN ({}) ORDER BY file_name"
            .format(','.join(ids))
        )
        ids = map(lambda x: x[0], connection.fetchall())

        paths.sort(key=os.path.basename)

        items = paths
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
                        'image': thumbnail.get_thumbnail(item),
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
                            'image': thumbnail.GENERIC['folder'],
                            'is_gf': is_gf,
                        })
                    elif os.path.isfile(item):
                        print "file"
                        result.append({
                            'name': name,
                            'path': item,
                            'image': thumbnail.get_thumbnail(item),
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


class Item(wx.Panel):

    def __init__(self, parent, path, name, image, is_gf=False):
        super(Item, self).__init__(parent)

        self.path = path
        self.is_gf = is_gf
        self.selected = False

        self.UpdateBackground()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # controls

        image = wx.Image(image)
        image.Resize(THUMBNAIL_SIZE, (
            (THUMBNAIL_SIZE[0] - image.GetWidth()) / 2,
            (THUMBNAIL_SIZE[1] - image.GetHeight()) / 2,
        ))
        self.bitmap = wx.StaticBitmap(
            self,
            bitmap=image.ConvertToBitmap()
        )

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
                wx.ST_ELLIPSIZE_END |
                wx.ST_NO_AUTORESIZE
            )
        )
        self.sizer.Add(
            self.text,
            flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER,
            border=5
        )

        self.Layout()

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

    def GetPath(self):
        return self.path

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
