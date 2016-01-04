#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os
import database
from PIL import Image
# TODO: Move rightclick event somewhere other than taggingview
import itemview

# TODO: Context pane
# TODO: Switch from PIL to Pillow
# TODO: Generic icons for generic files
# OPTIONAL: Animated gif support, open file with application

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

        topBox = wx.BoxSizer(wx.HORIZONTAL)

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

        index = self.files.index(self.current_file)
        if index == len(self.files) - 1:
            self.current_file = self.files[0]
        else:
            self.current_file = self.files[index + 1]

        result = self.GetImage(self.current_file)
        image_name = result[1]

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.UpdateLabel()
        self.ReSize()
        self.Layout()
        self.Refresh()

    def DisplayPrev(self, event=None):

        index = self.files.index(self.current_file)
        print index
        if index == 0:
            self.current_file = self.files[len(self.files) - 1]
        else:
            self.current_file = self.files[index - 1]

        result = self.GetImage(self.current_file)
        image_name = result[1]

        wx.PostEvent(self, ItemChangeEvent(self.GetId()))

        self.UpdateLabel()
        self.ReSize()
        self.Layout()
        self.Refresh()

    def GetImage(self, file):

        cursor = database.get_current_gallery("connection").cursor()
        query = "SELECT uuid, file_name FROM file WHERE pk_id = %s" % (file)
        cursor.execute(query)
        result = cursor.fetchone()
        path = os.path.join(
            database.get_current_gallery("directory"),
            "files/",
            result[0])

        return [wx.Image(path), result[1], path]

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

        size = self.imgPan.GetSize()

        image = Image.open(self.GetImage(self.current_file)[2])

        image.thumbnail(size, Image.ANTIALIAS)
        new_image = self.ConvertPILToWX(image)

        try:
            self.Image.SetBitmap(wx.BitmapFromImage(new_image))
        except:
            print "No luck"

        self.Layout()
        self.Refresh()

    def ConvertPILToWX(self, pil, alpha=True):

        if alpha:
            image = apply(wx.EmptyImage, pil.size)
            image.SetData(pil.convert("RGB").tobytes())
            image.SetAlphaData(pil.convert("RGBA").tobytes()[3::4])
        else:
            image = wx.EmptyImage(pil.size[0], pil.size[1])
            new_image = pil.convert('RGB')
            data = new_image.tobytes()
            image.SetData(data)

        return image 

    def GetItems(self):
        return self.files

    def GetCurrentItem(self):
        return self.current_file

    def OnMouseRight(self, event):
        wx.PostEvent(self, itemview.RightClickItemEvent(self.GetId()))

    def OnExit(self, event=None):
        wx.PostEvent(self, TaggingViewExitEvent(self.GetId()))



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

'''

# print self.box.GetSize()

'''

'''
        factor = float(image.GetWidth()) / float(image.GetHeight())

        if width > height:
            if height > width * float(image.GetHeight()) / float(image.GetWidth()):
                new_width = width
                new_height = width * float(image.GetHeight()) / float(image.GetWidth())
            else:
                new_width = height * factor
                new_height = height
        else:
            if width > height * float(image.GetWidth()) / float(image.GetHeight()):
                new_width = height * float(image.GetWidth()) / float(image.GetHeight())
                new_height = height
            else:
                new_width = width
                new_height = width / factor
        try:
            pil_im = self.ConvertWXToPIL(image)
            pil_im = pil_im.resize((new_width, new_height), Image.ANTIALIAS)
            image = self.ConvertPILToWX(pil_im)
            
            print "Yay!"
        except Exception as e:
            print e

'''