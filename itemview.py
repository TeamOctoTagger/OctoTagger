from __future__ import division
import os
import wx
import database

THUMBNAIL_MAX_SIZE = 128


class ItemView(wx.Panel):
    def __init__(self, parent):
        super(ItemView, self).__init__(parent)
        self.SetBackgroundColour("#c1c8c5")

        self.sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        # selections

        self.items = []
        self.breadcrumbs = []
        self.last_clicked = None

        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)

    def get_current_root(self):
        root = self.items
        for breadcrumb in self.breadcrumbs:
            root = root[breadcrumb]
        return root

    def update_items(self):
        self.sizer.Clear()
        root = self.get_current_root()
        for item in root:
            index = len(self.sizer.GetChildren())
            self.sizer.Add(
                Item(self, item['name'], item['path']),
                flag=wx.ALL,
                border=5,
                userData=index,
            )

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

            for i in range(self.last_clicked, index+direction, direction):
                items[i].GetWindow().SetSelected(
                    items[self.last_clicked].GetWindow().IsSelected()
                )
        else:
            target.ToggleSelected()

        self.last_clicked = index

    def OnMouseDouble(self, event):
        # TODO open folder or open tagging view
        self.last_clicked = None
        self.update_items()
        pass

    def SetItems(self, items):
        '''
        Sets which items are to be displayed. Pass ids from database as int or
        paths from filesystem as str.
        '''

        connection = database.get_current_gallery('connection').cursor()

        def parse_items(items):
            result = []
            for item in items:
                if type(item) is int:  # item is db id
                    connection.execute(
                        (
                            'SELECT file_name, location '
                            'FROM file '
                            'LEFT JOIN thumbnail '
                            'ON fk_thumbnail_id=thumbnail.pk_id '
                            'WHERE file.pk_id=:id '
                        ),
                        {
                            'id': item,
                        }
                    )
                    row = connection.fetchone()
                    if row is None:
                        raise ValueError('Item not found in database', item)
                    print(row)
                    result.append({
                        'name': row[0],
                        'path': row[1],  # TODO absolute thumbnail location
                    })
                elif type(item) is str:  # item is fs path
                    # TODO check if file or folder
                    name = os.path.basename(item)
                    if os.path.isdir(item):
                        result.append({
                            'name': name,
                            'path': parse_items(item),
                        })
                    elif os.path.isfile(item):
                        result.append({
                            'name': name,
                            'path': item,
                        })
                    else:
                        raise TypeError('Encountered unsupported path', item)
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

    def SetSelectedAll(self, selected=True):
        items = self.sizer.GetChildren()
        for item in items:
            item.GetWindow().SetSelected(selected)


class Item(wx.Panel):
    def __init__(self, parent, name, path):
        super(Item, self).__init__(parent)

        self.path = path
        self.selected = False
        self.is_folder = type(path) is list

        self.UpdateBackground()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        # controls

        if self.is_folder:
            image = wx.Image(path)  # FIXME path to image of folder
        else:
            image = wx.Image(path)

        # center image
        # FIXME center image on Windows
        size = image.GetSize()
        if size.GetWidth() > size.GetHeight():
            factor = THUMBNAIL_MAX_SIZE / size.GetWidth()
            pos = (0, (THUMBNAIL_MAX_SIZE - image.GetHeight()*factor)/2)
        else:
            factor = THUMBNAIL_MAX_SIZE / size.GetHeight()
            pos = ((THUMBNAIL_MAX_SIZE - image.GetWidth()*factor)/2, 0)
        size.Scale(factor, factor)
        image.Rescale(size.GetWidth(), size.GetHeight())
        image.Resize((THUMBNAIL_MAX_SIZE, THUMBNAIL_MAX_SIZE), pos)

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

        # events

        self.Bind(wx.EVT_LEFT_UP, self.PropagateEvent)
        self.bitmap.Bind(wx.EVT_LEFT_UP, self.PropagateEvent)
        self.text.Bind(wx.EVT_LEFT_UP, self.PropagateEvent)

    def GetPath(self):
        return self.path

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
