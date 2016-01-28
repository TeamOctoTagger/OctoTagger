#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os
import database
from PIL import Image
import itemview
import thumbnail

# TODO: Behaviour when all files get deleted
# OPTIONAL: Animated gif support,
# OPTIONAL: open file with application, preload next files

TaggingViewExitEvent, EVT_EXIT_TAGGING_VIEW = wx.lib.newevent.NewCommandEvent()
ItemChangeEvent, EVT_ITEM_CHANGE = wx.lib.newevent.NewCommandEvent()


class TaggingView(wx.Panel):

    def __init__(self, parent, files, start_file=None):
        wx.Panel.__init__(self, parent)

        self.files = files
        if start_file and start_file in files:
            self.current_file = start_file
        else:
            self.current_file = files[0]
        self.first = True

        self.init_ui()

    def init_ui(self):
        self.imgPan = wx.Panel(self)

        self.text = wx.StaticText(
            self,
            label="file",
            style=(
                wx.ALIGN_CENTRE_HORIZONTAL |
                wx.ST_ELLIPSIZE_END |
                wx.ST_NO_AUTORESIZE |
                wx.SIMPLE_BORDER
            )
        )

        self.Image = wx.StaticBitmap(self.imgPan)

        self.SetBackgroundColour("#c1c8c5")
        self.imgPan.SetBackgroundColour("#c1c8c5")

        topBox = wx.BoxSizer(wx.HORIZONTAL)

        btn_prev = wx.Button(self, -1, "<")
        btn_prev.Bind(wx.EVT_BUTTON, self.DisplayPrev)

        btn_next = wx.Button(self, -1, ">")
        btn_next.Bind(wx.EVT_BUTTON, self.DisplayNext)

        btn_exit = wx.Button(self, -1, "X")
        btn_exit.Bind(wx.EVT_BUTTON, self.OnExit)

        topBox.Add(btn_prev, 0, wx.EXPAND)
        topBox.Add(self.text, 1, wx.EXPAND)
        topBox.Add(btn_next, 0, wx.EXPAND)
        topBox.Add(btn_exit, 0, wx.EXPAND)

        imgPan_sz = wx.BoxSizer(wx.VERTICAL)
        imgPan_sz.Add(
            self.Image,
            1,
            wx.ALIGN_CENTER | wx.ALL | wx.ADJUST_MINSIZE
        )
        self.imgPan.SetSizer(imgPan_sz)

        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(topBox, 0, wx.EXPAND)
        mainBox.Add(self.imgPan, 1, wx.ALL | wx.EXPAND)

        self.UpdateLabel()

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.SetSizerAndFit(mainBox)

        self.Layout()
        self.Refresh()
        self.Bind(wx.EVT_SIZE, self.ReSize)
        self.imgPan.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)
        self.Image.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)

    def DisplayNext(self, event=None):
        # FIXME: first key-down not recognized for next and prev

        index = self.files.index(self.current_file)
        if index == len(self.files) - 1:
            self.current_file = self.files[0]
        else:
            self.current_file = self.files[index + 1]

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.UpdateLabel()
        self.ReSize()

    def DisplayPrev(self, event=None):

        index = self.files.index(self.current_file)
        if index == 0:
            self.current_file = self.files[len(self.files) - 1]
        else:
            self.current_file = self.files[index - 1]

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.UpdateLabel()
        self.ReSize()

    def GetImage(self, file):

        cursor = database.get_current_gallery("connection").cursor()
        query = "SELECT uuid, file_name FROM file WHERE pk_id = %s" % (file)
        cursor.execute(query)
        result = cursor.fetchone()
        path = os.path.join(
            database.get_current_gallery("directory"),
            "files",
            result[0])

        thumb_path = thumbnail.get_thumbnail(file, path_only=True)
        if thumb_path is None:
            image = wx.Image(path)
        else:
            image = wx.Image(thumb_path)
            path = thumb_path
        return [image, result[1], path]

    def UpdateLabel(self):
        label = (
            "%s  (%d/%d)" % (
                os.path.basename(self.GetImage(self.current_file)[1]),
                self.files.index(self.current_file) + 1,
                len(self.files),
            )
        )
        self.text.SetLabel(label)

    def ReSize(self, event=None):

        # TODO: When window is resized quickly, doesn't resize image correctly.
        # Maybe use Double Buffering?
        # http://wiki.wxpython.org/DoubleBufferedDrawing

        size = self.imgPan.GetSize()

        image = Image.open(self.GetImage(self.current_file)[2]).convert()

        image.thumbnail(size, Image.ANTIALIAS)
        new_image = self.ConvertPILToWX(image)

        try:
            self.Image.SetBitmap(wx.BitmapFromImage(new_image))
        except:
            print "No luck"

        self.Layout()

    def ConvertPILToWX(self, myPilImage, copyAlpha=True):

        hasAlpha = myPilImage.mode[-1] == 'A'
        if copyAlpha and hasAlpha:  # Make sure there is an alpha layer copy.

            myWxImage = wx.EmptyImage(*myPilImage.size)
            myPilImageCopyRGBA = myPilImage.copy()
            myPilImageCopyRGB = myPilImageCopyRGBA.convert(
                'RGB')    # RGBA --> RGB
            myPilImageRgbData = myPilImageCopyRGB.tobytes()
            myWxImage.SetData(myPilImageRgbData)
            # Create layer and insert alpha values.
            myWxImage.SetAlphaData(myPilImageCopyRGBA.tobytes()[3::4])

        else:    # The resulting image will not have alpha.

            myWxImage = wx.EmptyImage(*myPilImage.size)
            myPilImageCopy = myPilImage.copy()
            # Discard any alpha from the PIL image.
            myPilImageCopyRGB = myPilImageCopy.convert('RGB')
            myPilImageRgbData = myPilImageCopyRGB.tobytes()
            myWxImage.SetData(myPilImageRgbData)

        return myWxImage

    def GetItems(self):
        return self.files

    def GetCurrentItem(self):
        return self.current_file

    def GetName(self):
        return self.GetImage(self.current_file)[1]

    def RemoveItem(self, item):
        self.DisplayNext()
        self.files.remove(item)

    def OnMouseRight(self, event):
        wx.PostEvent(self, itemview.RightClickItemEvent(self.GetId()))

    def OnExit(self, event=None):
        wx.PostEvent(self, TaggingViewExitEvent(self.GetId()))
