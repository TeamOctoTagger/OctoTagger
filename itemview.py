from __future__ import division
import wx

THUMBNAIL_MAX_SIZE = 128


class ItemView(wx.Panel):
    def __init__(self, parent):
        super(ItemView, self).__init__(parent)
        self.SetBackgroundColour("#e74c3c")

        self.sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        # selections

        self.selection = []
        self.breadcrumbs = []
        self.lastClicked = None
        # TODO tree structure of selections

        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDouble)

    def OnMouseUp(self, event):
        target = event.GetEventObject()
        if target is self:
            # clicked outside of any item
            return

        if not target.GetClientRect().Contains(event.GetPosition()):
            # click dragged outside of target
            # cancel click
            return

        while not isinstance(target, wx.Panel):
            # clicked on a child of the item
            target = target.GetParent()

        if event.ControlDown() and event.ShiftDown():
            # add new range selection
            pass
        elif event.ControlDown():
            # add new single selection
            pass
        elif event.ShiftDown():
            # set new range selection
            pass
        else:
            # set new single selection
            # TODO cache children, also for folder structure
            # self.lastClicked = self.sizer.GetChildren().index(target)
            target.ToggleSelected()

    def OnMouseDouble(self, event):
        # TODO open folder or open tagging view
        pass

    def SetItems(self, items):
        # TODO support db items AND fs items
        for item in items:
            if type(item) is str:  # item is db uuid
                pass
            elif type(item) is dict:  # item is fs reference
                # item['name'] == filename
                # item['path'] == location in fs
                if type(item['path']) is list:  # this is a folder
                    pass
                elif type(item['path']) is str:  # this is a file
                    pass
                else:
                    raise TypeError(
                        'Encountered unsupported path',
                        item['path']
                    )
            else:
                raise TypeError('Encountered unsupported item', item)

            # TODO remove old code
            itemCtrl = Item(self, item)
            self.sizer.Add(
                itemCtrl,
                flag=wx.ALL,
                border=5,
            )

    def GetSelectedItems(self):
        selected_items = []
        for i in range(self.sizer.GetItemCount()):
            item = self.sizer.GetItem(i)
            window = item.GetWindow()
            if window.IsSelected():
                selected_items.append(item.GetUserData())
        return selected_items

    def UpdateSelection(self):
        self.sizer.Clear()


class Item(wx.Panel):
    def __init__(self, parent, name):
        super(Item, self).__init__(parent)

        self.selected = False

        self.SetBackgroundColour(parent.GetBackgroundColour())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        # controls

        image = wx.Image('default/files/' + name)

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

    def PropagateEvent(self, event):
        event.ResumePropagation(1)
        event.Skip()

    def UpdateBackground(self):
        if self.selected:
            color = wx.BLUE
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
