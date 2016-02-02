#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os
import database
from PIL import Image
import itemview
import thumbnail
import threading

# TODO: Behaviour when all files get deleted
# OPTIONAL: Animated gif support,
# OPTIONAL: open file with application, preload next files

TaggingViewExitEvent, EVT_EXIT_TAGGING_VIEW = wx.lib.newevent.NewCommandEvent()
ItemChangeEvent, EVT_ITEM_CHANGE = wx.lib.newevent.NewCommandEvent()


class TaggingView(wx.Panel):

    def __init__(self, parent, files, start_file=None):
        wx.Panel.__init__(self, parent)

        self.files = files
        if start_file and start_file in self.files:
            self.current_file = self.files.index(start_file)
        else:
            self.current_file = 0

        self.image_buffer = [None] * 3
        self.image_thread = [threading.Thread()] * 3
        self.file_buffer = [None] * len(self.files)
        self.current_buffer = 0
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
        self.text.SetForegroundColour("#FFFFFF")

        self.Image = wx.StaticBitmap(self.imgPan)

        # self.SetBackgroundColour("#c1c8c5")
        # self.imgPan.SetBackgroundColour("#c1c8c5")
        self.SetBackgroundColour("#444444")
        self.imgPan.SetBackgroundColour("#444444")

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

    def load_images(self):
        for i in [-1, 0, 1]:
            buffer = (self.current_buffer + i) % 3
            file = (self.current_file + i) % len(self.files)

            if self.image_buffer[buffer] is not None:
                # image loaded
                continue

            if self.image_thread[buffer].is_alive():
                # image loading
                continue

            # begin loading image
            self.image_thread[buffer] = threading.Thread(
                target=self._load_image,
                args=(buffer, file),
            )
            self.image_thread[buffer].start()

    def _load_image(self, buffer, file):
        self.image_buffer[buffer] = Image.open(
            self.get_file(file)[1]
        ).convert()

    def get_image(self, position):
        """Position can be 0 for current, 1 for next or -1 for previous
        image"""
        if position < -1 or position > 1:
            raise ValueError("Position must be in [-1;1]", position)

        buffer = (self.current_buffer + position) % 3
        self.image_thread[buffer].join()  # wait for image to be loaded
        return self.image_buffer[buffer].copy()

    def get_file(self, index):
        if self.file_buffer[index] is not None:
            return self.file_buffer[index]

        connection = database.get_current_gallery("connection")
        c = connection.cursor()
        c.execute(
            "SELECT uuid, file_name FROM file WHERE pk_id = ?",
            (self.files[index],),
        )

        result = c.fetchone()
        path = os.path.join(
            database.get_current_gallery("directory"),
            "files",
            result[0],
        )

        thumb_path = thumbnail.get_thumbnail(self.files[index], path_only=True)
        if thumb_path is not None:
            path = thumb_path

        self.file_buffer[index] = (result[1], path)
        return self.file_buffer[index]

    def DisplayNext(self, event=None):

        # move pointers forward
        self.current_buffer = (self.current_buffer + 1) % 3
        self.current_file = (self.current_file + 1) % len(self.files)

        # invalidate next image
        next = (self.current_buffer + 1) % 3
        self.image_thread[next].join()  # prevent race
        self.image_buffer[next] = None  # clear image

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.load_images()
        self.UpdateLabel()
        self.ReSize()

    def DisplayPrev(self, event=None):
        # move pointer backward
        self.current_buffer = (self.current_buffer - 1) % 3
        self.current_file = (self.current_file - 1) % len(self.files)

        # invalidate previous image
        prev = (self.current_buffer - 1) % 3
        self.image_thread[prev].join()  # prevent race
        self.image_buffer[prev] = None  # clear image

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.load_images()
        self.UpdateLabel()
        self.ReSize()

    def UpdateLabel(self):
        label = (
            "%s  (%d/%d)" % (
                os.path.basename(self.get_file(self.current_file)[0]),
                self.current_file + 1,
                len(self.files),
            )
        )
        self.text.SetLabel(label)

    def ReSize(self, event=None):

        # TODO: When window is resized quickly, doesn't resize image correctly.
        # Maybe use Double Buffering?
        # http://wiki.wxpython.org/DoubleBufferedDrawing

        self.load_images()
        self.Layout()
        self.Refresh()
        size = self.imgPan.GetSize()

        image = self.get_image(0)
        image.thumbnail(size, Image.BILINEAR)
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
        return self.files[self.current_file]

    def GetName(self):
        return self.get_file(self.current_file)[0]

    def RemoveItem(self, item):
        self.DisplayNext()
        self.files.remove(item)

    def OnMouseRight(self, event):
        wx.PostEvent(self, itemview.RightClickItemEvent(self.GetId()))

    def OnExit(self, event=None):
        wx.PostEvent(self, TaggingViewExitEvent(self.GetId()))
