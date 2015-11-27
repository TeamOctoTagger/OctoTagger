#!/usr/bin/env python

import wx
import edit_output_folder
import bulk_create_output_folders
import settings
import about
import itemview


class TaggingView(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(900, 550))
        # self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar()  # A StatusBar in the bottom of the window

        leftPan = wx.Panel(self)
        leftUpPan = wx.Panel(self)
        leftBotPan = wx.Panel(self)

        leftMidLeftPan = wx.Panel(self)
        leftMidMidPan = wx.Panel(self)
        leftMidRightPan = wx.Panel(self)

        midLeftPan = wx.Panel(self)
        midTopPan = wx.Panel(self)
        midPan = wx.Panel(self)
        midBotPan = wx.Panel(self)
        midRightPan = wx.Panel(self)

        rightPan = wx.Panel(self)
        rightUpPan = wx.Panel(self)
        rightBotPan = wx.Panel(self)

        rightMidLeftPan = wx.Panel(self)
        rightMidMidPan = wx.Panel(self)
        rightMidRightPan = wx.Panel(self)

        topPan = wx.Panel(self)
        topPanLeft = wx.Panel(self)
        topPanTop = wx.Panel(self)
        topPanBot = wx.Panel(self)
        topPanRight = wx.Panel(self)
        '''
        botPan1 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan2 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan3 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan4 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan5 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        '''

        leftPan.SetBackgroundColour("#3498db")
        leftUpPan.SetBackgroundColour("#3498db")
        leftBotPan.SetBackgroundColour("#3498db")

        leftMidLeftPan.SetBackgroundColour("#3498db")
        leftMidMidPan.SetBackgroundColour("#3498db")
        leftMidRightPan.SetBackgroundColour("#3498db")

        midPan.SetBackgroundColour("#3498db")
        midLeftPan.SetBackgroundColour("#3498db")
        midRightPan.SetBackgroundColour("#3498db")
        midTopPan.SetBackgroundColour("#3498db")
        midBotPan.SetBackgroundColour("#3498db")

        rightPan.SetBackgroundColour("#3498db")
        rightUpPan.SetBackgroundColour("#3498db")
        rightBotPan.SetBackgroundColour("#3498db")

        rightMidLeftPan.SetBackgroundColour("#3498db")
        rightMidMidPan.SetBackgroundColour("#3498db")
        rightMidRightPan.SetBackgroundColour("#3498db")

        topPan.SetBackgroundColour("#2ecc71")
        topPanLeft.SetBackgroundColour("#2ecc71")
        topPanTop.SetBackgroundColour("#2ecc71")
        topPanBot.SetBackgroundColour("#2ecc71")
        topPanRight.SetBackgroundColour("#2ecc71")
        '''
        botPan1.SetBackgroundColour("#e74c3c")
        botPan2.SetBackgroundColour("#e74c3c")
        botPan3.SetBackgroundColour("#e74c3c")
        botPan4.SetBackgroundColour("#e74c3c")
        botPan5.SetBackgroundColour("#e74c3c")
        '''

        PhotoMaxSize = 900

        url = "landschaft.png"
        img = wx.Image(url, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = PhotoMaxSize
            NewH = PhotoMaxSize * H / W
        else:
            NewH = PhotoMaxSize
            NewW = PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)
        imageCtrl = wx.StaticBitmap(midPan, wx.ID_ANY,
                                         wx.BitmapFromImage(img))

        imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        midPan.Refresh()

        img = wx.Image("arrow_left.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(40,40)
        imageCtrl2 = wx.StaticBitmap(topPanLeft, wx.ID_ANY,
                                         wx.BitmapFromImage(img))

        imageCtrl2.SetBitmap(wx.BitmapFromImage(img))
        topPanLeft.Refresh()

        img = wx.Image("arrow_right.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(40,40)
        imageCtrl3 = wx.StaticBitmap(topPanRight, wx.ID_ANY,
                                         wx.BitmapFromImage(img))

        imageCtrl3.SetBitmap(wx.BitmapFromImage(img))
        topPanRight.Refresh()

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topUnderBox = wx.BoxSizer(wx.VERTICAL)

        midBox = wx.BoxSizer(wx.HORIZONTAL)
        midInnerBox = wx.BoxSizer(wx.VERTICAL)

        #botBox = wx.BoxSizer(wx.HORIZONTAL)
        #botUnderBox = wx.BoxSizer(wx.HORIZONTAL)

        leftBox = wx.BoxSizer(wx.VERTICAL)
        leftInnerBox = wx.BoxSizer(wx.HORIZONTAL)

        rightBox = wx.BoxSizer(wx.VERTICAL)
        rightInnerBox = wx.BoxSizer(wx.HORIZONTAL)

        mainBox = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(topPan, id=wx.ID_ANY, label="Dateiname")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        text.SetFont(font)

        #topUnderBox.Add(topPanTop, 0.5, wx.EXPAND)
        topUnderBox.Add(topPan, 1, wx.EXPAND)
        #topUnderBox.Add(topPanBot, 1, wx.EXPAND)

        topBox.Add(topPanLeft, 10, wx.EXPAND)
        topBox.Add(topUnderBox, 2000, wx.EXPAND|wx.ALIGN_CENTER)
        topBox.Add(topPanRight, 10, wx.EXPAND)

        leftInnerBox.Add(leftMidLeftPan, 100, wx.EXPAND)
        leftInnerBox.Add(leftMidMidPan, 100, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        leftInnerBox.Add(leftMidRightPan, 1, wx.EXPAND)

        rightInnerBox.Add(rightMidLeftPan, 30, wx.EXPAND)
        rightInnerBox.Add(rightMidMidPan,100, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        rightInnerBox.Add(rightMidRightPan, 100, wx.EXPAND)

        leftBox.Add(leftUpPan, 4, wx.EXPAND)
        leftBox.Add(leftInnerBox, 4, wx.EXPAND)
        leftBox.Add(leftBotPan, 4, wx.EXPAND)

        rightBox.Add(rightUpPan, 4, wx.EXPAND)
        rightBox.Add(rightInnerBox, 4, wx.EXPAND)
        rightBox.Add(rightBotPan, 4, wx.EXPAND)

        midInnerBox.Add(midTopPan, 5, wx.EXPAND)
        midInnerBox.Add(midPan, 100, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        midInnerBox.Add(midBotPan, 5, wx.EXPAND)

        #midBox.Add(leftBox, 50, wx.EXPAND)
        midBox.Add(midLeftPan, 10, wx.EXPAND)
        midBox.Add(midInnerBox, 10, wx.EXPAND)
        midBox.Add(midRightPan, 10, wx.EXPAND)
        #midBox.Add(rightBox, 50, wx.EXPAND)

        '''
        botUnderBox.Add(botPan1, 1, wx.EXPAND)
        botUnderBox.Add(botPan2, 1, wx.EXPAND)
        botUnderBox.Add(botPan3, 1, wx.EXPAND)
        botUnderBox.Add(botPan4, 1, wx.EXPAND)
        botUnderBox.Add(botPan5, 1, wx.EXPAND)

        botBox.Add(botUnderBox, 10, wx.EXPAND)
        '''
        mainBox.Add(topBox, 2, wx.EXPAND)
        mainBox.Add(midBox, 12, wx.EXPAND)
        #mainBox.Add(botBox, 4, wx.EXPAND)



        self.SetSizer(mainBox)
        self.Layout()
        self.Show(True)


app = wx.App(False)
frame = TaggingView(None, "Tagging View")
app.MainLoop()