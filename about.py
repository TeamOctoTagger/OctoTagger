#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
OctoTagger's About dialog.
'''

import wx

def getInfo():
    description = "OctoTagger is a simple yet powerful software for organizing your files."
    licence = "GPLv3"

    info = wx.AboutDialogInfo()

    info.SetIcon(wx.Icon('logo.png', wx.BITMAP_TYPE_PNG))
    info.SetName('OctoTagger')
    info.SetVersion('0.1')
    info.SetDescription(description)
    info.SetCopyright('(C) 2015 Team OctoTagger')
    info.SetWebSite('http://www.octotagger.co')
    info.SetLicence(licence)
    info.AddDeveloper('Erik Ritschl')
    info.AddDeveloper('Clemens Stadlbauer')
    info.AddDeveloper('Christoph Führer')
    info.AddDocWriter('Julian Lorenz')
    info.AddArtist('Julian Lorenz')
    info.AddTranslator('Julian Lorenz')
    return info
