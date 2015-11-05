import wx


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
            self.sizer.Add(itemCtrl)


class Item(wx.Panel):
    def __init__(self, parent, name):
        super(Item, self).__init__(parent)
        self.text = wx.StaticText(
            self,
            label=name,
            style=wx.ALIGN_CENTRE_HORIZONTAL
        )

if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None)
    itemview = ItemView(frame)
    itemview.SetItems([
        {'name': 'abc1'},
        {'name': 'abc2'},
        {'name': 'abc3'},
        {'name': 'abc4'},
        {'name': 'abc5'},
        {'name': 'abc6'}
    ])
    frame.Show(True)
    app.MainLoop()

