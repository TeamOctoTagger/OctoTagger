from __future__ import division
import wx

THUMBNAIL_MAX_SIZE = 128


class ItemView(wx.Panel):
    def __init__(self, parent):
        super(ItemView, self).__init__(parent)
        self.SetBackgroundColour(wx.LIGHT_GREY)

        self.sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)

    def OnMouseUp(self, event):
        target = event.GetEventObject()
        if target is self:
            # clicked outside of any item
            print(self.GetSelectedItems())
            return
        elif not isinstance(target, wx.Panel):
            # clicked on a child of the item
            target = target.GetParent()
        target.ToggleSelected()

    def SetItems(self, items):
        self.sizer.Clear()
        for item in items:
            itemCtrl = Item(self, item['name'])
            self.sizer.Add(
                itemCtrl,
                flag=wx.ALL,
                border=5,
                userData=item['name']  # FIXME use ID
            )

    def GetSelectedItems(self):
        selected_items = []
        for i in range(self.sizer.GetItemCount()):
            item = self.sizer.GetItem(i)
            window = item.GetWindow()
            if window.IsSelected():
                selected_items.append(item.GetUserData())
        return selected_items


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
        event.ResumePropagation(3)
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
