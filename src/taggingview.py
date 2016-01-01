#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import os
import database
from PIL import Image
import time

# TODO: Exit Tagging View, Tagging functionality, Context pane


class TaggingView(wx.Panel):

    def __init__(self, parent, files):
        wx.Panel.__init__(self, parent)

        self.files = files
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

        self.SetSizerAndFit(mainBox)

        print self.GetSize()
        
        self.Layout()
        self.Refresh()
        self.Bind(wx.EVT_SIZE, self.ReSize)

        self.ReSize()


    def DisplayNext(self, event=None):

        index = self.files.index(self.current_file)
        if index == len(self.files) - 1:
            self.current_file = self.files[0]
        else:
            self.current_file = self.files[index + 1]

        result = self.GetImage(self.current_file)
        image = result[0]
        image_name = result[1]

        self.text.SetLabel(os.path.basename(image_name))

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

    def ReSize(self, event=None):

        # TODO: When window is resized quickly, doesn't resize image correctly.

        size = self.imgPan.GetSize()
        print size

        image = Image.open(self.GetImage(self.current_file)[2])

        image.thumbnail(size, Image.ANTIALIAS)
        new_image = self.ConvertPILToWX(image)

        try:
            self.Image.SetBitmap(wx.BitmapFromImage(new_image))
        except:
            print "No luck"

        self.Layout()
        self.Refresh()

    def DisplayPrev(self, event=None):

        index = self.files.index(self.current_file)
        if index == 0:
            self.current_file = len(self.files)
        else:
            self.current_file = self.files[index - 1]

        result = self.GetImage(self.current_file)
        image = result[0]
        image_name = result[1]

        print self.current_file, "Picture"

        self.text.SetLabel(os.path.basename(image_name))

        image = image.Scale(800, 500)

        self.Image.SetBitmap(wx.BitmapFromImage(image))

        self.newLoad = True
        self.ReSize()
        self.Layout()
        self.Refresh()

    def ConvertPILToWX(self, pil, alpha=True):

        if alpha:
            image = apply(wx.EmptyImage, pil.size)
            image.SetData(pil.convert("RGB").tostring())
            image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
        else:
            image = wx.EmptyImage(pil.size[0], pil.size[1])
            new_image = pil.convert('RGB')
            data = new_image.tostring()
            image.SetData(data)

        return image 

    def GetItems(self):
        return self.files

    def OnExit(self, event):
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