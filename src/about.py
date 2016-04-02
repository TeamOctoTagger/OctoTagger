#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
OctoTagger's About dialog.
'''

import wx


def getInfo():
    description = (u"OctoTagger is a simple yet powerful software for "
                   u"organizing your files.")

    info = wx.AboutDialogInfo()

    info.SetName(u'OctoTagger')
    info.SetVersion(u'1.0')
    info.SetDescription(description)
    info.SetCopyright(u'(C) 2016 Team OctoTagger')
    info.AddDeveloper(u'Erik Ritschl')
    info.AddDeveloper(u'Clemens Stadlbauer')
    info.AddDeveloper(u'Christoph Führer')
    info.AddDocWriter(u'Julian Lorenz')
    info.AddArtist(u'Julian Lorenz')

    # Not supported natively by Windows and OS X
    info.SetWebSite(u'https://octotagger.co')
    info.SetIcon(wx.Icon('icons/logo.png', wx.BITMAP_TYPE_PNG))

    licence = open("LICENSE").read()
    info.SetLicence(licence)

    return info
