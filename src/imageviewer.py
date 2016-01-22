import wx, os
#from PIL import Image
#from PIL.ExifTags import TAGS


# TODO: Arrows/NextPrevButtons in TopBar
# TODO: Handle Case: Box Height > Box Width

class TestFrame(wx.Frame):
    def __init__(self, parent, files):
        wx.Frame.__init__(self, parent)

        self.files = files
        print self.files

        self.SetTitle("Tagging View")
        self.SetSize((100, 100))
        self.jpgs = GetJpgList("./Images")
        self.CurrentJpg = 0
        self.newLoad = True
        self.factor = 0.0
        self.loadCounter = 0

        self.MaxImageSize = 1000

        #topPan = wx.Panel(self)
        topLeftPan = wx.Panel(self)
        topRightPan = wx.Panel(self)

        self.imgPan = wx.Panel(self)

        topLeftPan.SetBackgroundColour("#aaaaaa")
        topRightPan.SetBackgroundColour("#aaaaaa")

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topInnerBox = wx.BoxSizer(wx.VERTICAL)
        topInnerLeftBox = wx.BoxSizer(wx.VERTICAL)
        topInnerRightBox = wx.BoxSizer(wx.VERTICAL)
        mainBox = wx.BoxSizer(wx.VERTICAL)

        self.text = wx.StaticText(
            self,
            label=self.jpgs[self.CurrentJpg],
            style=(
                wx.ALIGN_CENTRE_HORIZONTAL |
                wx.ST_ELLIPSIZE_END |
                wx.ST_NO_AUTORESIZE
            )
        )
        '''
        img = wx.Image("arrow_left.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(40,40)
        imageCtrl2 = wx.StaticBitmap(topLeftPan, wx.ID_ANY,
                                         wx.BitmapFromImage(img))


        imageCtrl2.SetBitmap(wx.BitmapFromImage(img))

        imageCtrl2.Bind(wx.EVT_LEFT_DOWN, self.DisplayNext)

        imageCtrl2.SetBackgroundColour("#aaaaaa")

        topLeftPan.Refresh()

        img = wx.Image("arrow_right.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(40,40)
        imageCtrl3 = wx.StaticBitmap(topRightPan, wx.ID_ANY,
                                         wx.BitmapFromImage(img))
        imageCtrl3.SetBitmap(wx.BitmapFromImage(img))

        imageCtrl3.Bind(wx.EVT_LEFT_DOWN, self.DisplayNext)

        imageCtrl3.SetBackgroundColour("#aaaaaa")

        topRightPan.Refresh()

        '''



        self.Image = wx.StaticBitmap(self.imgPan, bitmap=wx.EmptyBitmap(1500, 1500))

        self.imgPan.Bind(wx.EVT_SIZE, self.ReSize)

        self.DisplayNext()

        self.box = wx.BoxSizer(wx.VERTICAL)

        self.button = wx.Button(self, -1, "Previous Image")
        self.button.Bind(wx.EVT_BUTTON, self.DisplayPrev)

        self.button2 = wx.Button(self, -1, "Next Image")
        self.button2.Bind(wx.EVT_BUTTON, self.DisplayNext)



        topInnerBox.Add((1,1),1)
        topInnerBox.Add(self.text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        topInnerBox.Add((1,1),1)

        topInnerLeftBox.Add((1,1),1)
        topInnerLeftBox.Add(self.button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        topInnerLeftBox.Add((1,1),1)

        topInnerRightBox.Add((1,1),1)
        topInnerRightBox.Add(self.button2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        topInnerRightBox.Add((1,1),1)


        topBox.Add(topInnerLeftBox, 1, wx.EXPAND)
        topBox.Add(topInnerBox, 0, wx.EXPAND)
        topBox.Add(topInnerRightBox, 1, wx.EXPAND)


        self.box.Add((1,1),1)
        self.box.Add(self.imgPan, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        self.box.Add((1,1),1)

        mainBox.Add(topBox, 1, wx.EXPAND)
        mainBox.Add(self.box, 12, wx.EXPAND)

        self.SetSizerAndFit(mainBox)
        
        wx.EVT_CLOSE(self, self.OnCloseWindow)

    def DisplayNext(self, event=None):

        print self.jpgs
        print self.imgPan.GetSize()
        #print self.box.GetSize() FUNKTIONIERT NICHT! Muss gefixt werden

        self.CurrentJpg += 1
        if self.CurrentJpg > len(self.jpgs) -1:
            self.CurrentJpg = 0
        Img = wx.Image(self.jpgs[self.CurrentJpg], wx.BITMAP_TYPE_JPEG)

        print self.CurrentJpg, "Picture"

        self.text.SetLabel(os.path.basename(self.jpgs[self.CurrentJpg]))

        '''
        W = Img.GetWidth()/2
        H = Img.GetHeight()/2
        if W > H:
            NewW = W
            NewH = W * H / W
        else:
            NewH = H
            NewW = H * W / H
        '''

        Img = Img.Scale(800,500)

        self.Image.SetBitmap(wx.BitmapFromImage(Img))

        self.newLoad = True
        self.Fit()
        self.Layout()
        self.Refresh()

        print self.CurrentJpg

    def ReSize(self, event=None):

        #print self.box.GetSize()
        print self.loadCounter % 10
        width, height = self.box.GetSize()

        if self.newLoad:
            self.Img = wx.Image(self.jpgs[self.CurrentJpg], wx.BITMAP_TYPE_JPEG)
            self.newLoad = False
            self.factor = float(self.Img.GetWidth())/float(self.Img.GetHeight())
            print "Start Load"

        if self.loadCounter % 10 == 0:
            self.Img = self.Img = wx.Image(self.jpgs[self.CurrentJpg], wx.BITMAP_TYPE_JPEG)
            print "loader"
            print self.factor, "factor"

        if width>height:
            if height>width*float(self.Img.GetHeight())/float(self.Img.GetWidth()):
                self.Img = self.Img.Scale(width,width*float(self.Img.GetHeight())/float(self.Img.GetWidth()))
            else:
                self.Img = self.Img.Scale(height*self.factor,height)
        else:
            if width>height*float(self.Img.GetWidth())/float(self.Img.GetHeight()):
                self.Img = self.Img.Scale(height*float(self.Img.GetWidth())/float(self.Img.GetHeight()),height)
            else:
                self.Img = self.Img.Scale(width, width/self.factor)


        self.Image.SetBitmap(wx.BitmapFromImage(self.Img))

        self.loadCounter = self.loadCounter + 2
        #self.Fit()
        #self.Layout()

        self.Refresh()

    def DisplayPrev(self, event=None):
        self.CurrentJpg -= 1
        if self.CurrentJpg < 0:
            self.CurrentJpg = len(self.jpgs) -1

        Img = wx.Image(self.jpgs[self.CurrentJpg], wx.BITMAP_TYPE_JPEG)

        print self.CurrentJpg, "Picture"

        self.text.SetLabel(os.path.basename(self.jpgs[self.CurrentJpg]))

        W = Img.GetWidth()
        H = Img.GetHeight()
        if W > H:
            NewW = self.MaxImageSize
            NewH = self.MaxImageSize * H / W
        else:
            NewH = self.MaxImageSize
            NewW = self.MaxImageSize * W / H
        Img = Img.Scale(800,500)

        self.Image.SetBitmap(wx.BitmapFromImage(Img))
        self.newLoad = True

        self.Fit()
        self.Layout()
        self.Refresh()

        print self.CurrentJpg

    def OnCloseWindow(self, event):
        self.Destroy()
'''
    def get_exif(fn):
        ret = {}
        i = Image.open(fn)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret
'''
def GetJpgList(dir):
    jpgs = [f for f in os.listdir(dir) if f[-4:] == ".jpg"]
    return [os.path.join(dir, f) for f in jpgs]

class App(wx.App):
    def OnInit(self):

        frame = TestFrame(None, files=[1, 2, 3])
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = App(0)
    app.MainLoop()