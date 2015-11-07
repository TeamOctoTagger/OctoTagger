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

    def SetItems(self, items):
        self.sizer.Clear()
        for item in items:
            itemCtrl = Item(self, item['name'])
            self.sizer.Add(
                itemCtrl,
                flag=wx.ALL,
                border=5
            )


class Item(wx.Panel):
    def __init__(self, parent, name):
        super(Item, self).__init__(parent)
        self.SetBackgroundColour(parent.GetBackgroundColour())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

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
