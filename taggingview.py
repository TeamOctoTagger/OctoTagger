#!/usr/bin/env python

import wx
import edit_output_folder
import bulk_create_output_folders
import settings
import about
import itemview


class TaggingView(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280, 900))
        # self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar()  # A StatusBar in the bottom of the window

        leftPan = wx.Panel(self, style=wx.SUNKEN_BORDER)
        leftUpPan = wx.Panel(self, style=wx.SUNKEN_BORDER)
        leftBotPan = wx.Panel(self, style=wx.SUNKEN_BORDER)

        midLeftPan = wx.Panel(self)
        midPan = wx.Panel(self)
        midRightPan = wx.Panel(self)

        rightPan = wx.Panel(self, style=wx.SUNKEN_BORDER)
        rightUpPan = wx.Panel(self, style=wx.SUNKEN_BORDER)
        rightBotPan = wx.Panel(self, style=wx.SUNKEN_BORDER)

        topPan = wx.Panel(self)
        topPanLeft = wx.Panel(self)
        topPanTop = wx.Panel(self)
        topPanBot = wx.Panel(self)
        topPanRight = wx.Panel(self)

        botPan1 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan2 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan3 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan4 = wx.Panel(self, style=wx.SUNKEN_BORDER)
        botPan5 = wx.Panel(self, style=wx.SUNKEN_BORDER)


        leftPan.SetBackgroundColour("#3498db")
        leftUpPan.SetBackgroundColour("#3498db")
        leftBotPan.SetBackgroundColour("#3498db")

        midPan.SetBackgroundColour("#3498db")
        midLeftPan.SetBackgroundColour("#3498db")
        midRightPan.SetBackgroundColour("#3498db")


        rightPan.SetBackgroundColour("#3498db")
        rightUpPan.SetBackgroundColour("#3498db")
        rightBotPan.SetBackgroundColour("#3498db")

        topPan.SetBackgroundColour("#2ecc71")
        topPanLeft.SetBackgroundColour("#2ecc71")
        topPanTop.SetBackgroundColour("#2ecc71")
        topPanBot.SetBackgroundColour("#2ecc71")
        topPanRight.SetBackgroundColour("#2ecc71")

        botPan1.SetBackgroundColour("#e74c3c")
        botPan2.SetBackgroundColour("#e74c3c")
        botPan3.SetBackgroundColour("#e74c3c")
        botPan4.SetBackgroundColour("#e74c3c")
        botPan5.SetBackgroundColour("#e74c3c")

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

        img = wx.Image("arrow_left", wx.BITMAP_TYPE_ANY)
        img = img.Scale(200,150)

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topUnderBox = wx.BoxSizer(wx.VERTICAL)

        midBox = wx.BoxSizer(wx.HORIZONTAL)
        midInnerBox = wx.BoxSizer(wx.HORIZONTAL)

        botBox = wx.BoxSizer(wx.HORIZONTAL)
        botUnderBox = wx.BoxSizer(wx.HORIZONTAL)

        leftBox = wx.BoxSizer(wx.VERTICAL)

        rightBox = wx.BoxSizer(wx.VERTICAL)

        mainBox = wx.BoxSizer(wx.VERTICAL)



        text = wx.StaticText(topPan, id=wx.ID_ANY, label="Dateiname")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        text.SetFont(font)

        topUnderBox.Add(topPanTop, 1, wx.EXPAND)
        topUnderBox.Add(topPan, 1, wx.EXPAND)
        topUnderBox.Add(topPanBot, 1, wx.EXPAND)

        topBox.Add(topPanLeft, 10, wx.EXPAND)
        topBox.Add(topUnderBox, 2, wx.EXPAND)
        topBox.Add(topPanRight, 10, wx.EXPAND)

        leftBox.Add(leftUpPan, 4, wx.EXPAND)
        leftBox.Add(leftPan, 4, wx.EXPAND)
        leftBox.Add(leftBotPan, 4, wx.EXPAND)

        rightBox.Add(rightUpPan, 4, wx.EXPAND)
        rightBox.Add(rightPan, 4, wx.EXPAND)
        rightBox.Add(rightBotPan, 4, wx.EXPAND)

        midBox.Add(leftBox, 50, wx.EXPAND)
        midBox.Add(midLeftPan, 10, wx.EXPAND)
        midBox.Add(midPan, 1, wx.EXPAND)
        midBox.Add(midRightPan, 10, wx.EXPAND)
        midBox.Add(rightBox, 50, wx.EXPAND)

        botUnderBox.Add(botPan1, 1, wx.EXPAND)
        botUnderBox.Add(botPan2, 1, wx.EXPAND)
        botUnderBox.Add(botPan3, 1, wx.EXPAND)
        botUnderBox.Add(botPan4, 1, wx.EXPAND)
        botUnderBox.Add(botPan5, 1, wx.EXPAND)

        botBox.Add(botUnderBox, 10, wx.EXPAND)

        mainBox.Add(topBox, 2, wx.EXPAND)
        mainBox.Add(midBox, 12, wx.EXPAND)
        mainBox.Add(botBox, 4, wx.EXPAND)



        self.SetSizer(mainBox)
        self.Layout()
        self.Show(True)


app = wx.App(False)
frame = TaggingView(None, "Tagging View")
app.MainLoop()