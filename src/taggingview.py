#!/usr/bin/python
# -*- coding: utf-8 -*-
import wx
import os
import database
from PIL import Image
import itemview
import thumbnail
import threading

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

        self.InitUI()

    def InitUI(self):

        self.imgPan = wx.Panel(self)

        tag_topbar = wx.Panel(self)
        tag_topbar_sz = wx.BoxSizer(wx.HORIZONTAL)
        tag_topbar.SetSizer(tag_topbar_sz)

        self.text = wx.StaticText(
            tag_topbar,
            label="file",
            style=(
                wx.ALIGN_CENTRE_HORIZONTAL |
                wx.ALIGN_CENTRE_VERTICAL |
                wx.ST_ELLIPSIZE_MIDDLE |
                wx.ST_NO_AUTORESIZE
            )
        )

        if self.GetParent().dark_theme:
            tag_topbar.SetBackgroundColour("#333333")
            self.text.SetForegroundColour("#FFFFFF")
            self.SetBackgroundColour("#444444")
            self.imgPan.SetBackgroundColour("#444444")
        else:
            self.SetBackgroundColour("#c1c8c5")
            self.imgPan.SetBackgroundColour("#c1c8c5")

        btn_prev = wx.Button(tag_topbar, -1, "<")
        btn_prev.Bind(wx.EVT_BUTTON, self.DisplayPrev)

        btn_next = wx.Button(tag_topbar, -1, ">")
        btn_next.Bind(wx.EVT_BUTTON, self.DisplayNext)

        # btn_exit = wx.Button(tag_topbar, -1, "X")
        # btn_exit.Bind(wx.EVT_BUTTON, self.OnExit)

        tag_topbar_sz.Add(btn_prev, 0, wx.EXPAND)
        tag_topbar_sz.Add(self.text, 1, wx.CENTER | wx.ALIGN_CENTRE_VERTICAL)
        tag_topbar_sz.Add(btn_next, 0, wx.EXPAND)
        # tag_topbar_sz.Add(btn_exit, 0, wx.EXPAND)

        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(tag_topbar, 0, wx.EXPAND)
        mainBox.Add(self.imgPan, 1, wx.ALL | wx.EXPAND)

        self.UpdateLabel()

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.SetSizerAndFit(mainBox)

        self._imageBuffer = wx.EmptyBitmap(*self.imgPan.GetSize())

        self.Bind(wx.EVT_SIZE, self.ReSize)
        self.imgPan.Bind(wx.EVT_PAINT, self.RePaint)
        self.imgPan.Bind(wx.EVT_RIGHT_UP, self.OnMouseRight)

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
        self.Layout()
        self.load_images()
        size = self.imgPan.GetSize()

        image = self.get_image(0)
        image.thumbnail(size, Image.BILINEAR)  # make image fit imgPan
        image = self.convert_pil_to_wx(image, True)
        bitmap = wx.BitmapFromImage(image)
        self._imageBuffer = wx.EmptyBitmap(*size)

        dc = wx.MemoryDC()
        dc.SelectObject(self._imageBuffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.DrawBitmap(
            bitmap,
            (size[0] - bitmap.GetWidth()) / 2,
            (size[1] - bitmap.GetHeight()) / 2,
        )

        del dc
        self.Refresh()

    def RePaint(self, event):
        dc = wx.PaintDC(self.imgPan)
        dc.DrawBitmap(self._imageBuffer, 0, 0)

    def convert_pil_to_wx(self, image_pil, copy_alpha=True):
        image_wx = wx.EmptyImage(*image_pil.size)
        image_wx.SetData(image_pil.convert('RGB').tobytes())

        has_alpha = image_pil.mode[-1] == 'A'
        if has_alpha and copy_alpha:
            image_wx.SetAlphaData(image_pil.split()[-1].tobytes())

        return image_wx

    def GetItems(self):
        return self.files

    def GetCurrentItem(self):
        return self.files[self.current_file]

    def GetName(self):
        return self.get_file(self.current_file)[0]

    def RemoveItem(self, item):
        index = self.files.index(item)
        self.files.remove(item)
        self.file_buffer.pop(index)

        # invalidate current image
        self.image_thread[self.current_buffer].join()  # prevent race
        self.image_buffer[self.current_buffer] = None

        if len(self.files) == 0:
            # no more images
            self.OnExit()
        elif self.current_file == len(self.files):
            # was last image
            self.DisplayPrev()
        else:
            # invalidate next image
            next = (self.current_buffer + 1) % 3
            self.image_thread[next].join()  # prevent race
            self.image_buffer[next] = None  # clear image

            wx.PostEvent(self, ItemChangeEvent(self.GetId()))
            self.load_images()
            self.UpdateLabel()
            self.ReSize()

    def OnMouseRight(self, event):
        wx.PostEvent(self, itemview.RightClickItemEvent(self.GetId()))

    def OnExit(self, event=None):
        wx.PostEvent(self, TaggingViewExitEvent(self.GetId()))
