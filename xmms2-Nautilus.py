#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright 2011 Eli. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY ELI ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ELI OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from urllib import quote_plus, unquote_plus

import nautilus

import xmmsclient

def fileToXmmsUri(file):
    return unquote_plus(file.get_uri())

class Xmms2Nautilus(nautilus.InfoProvider, nautilus.MenuProvider):
    def __init__(self):
        self.xmms = xmmsclient.XMMSSync("xmms2-Nautilus")
        try:
            self.xmms.connect(os.getenv("XMMS_PATH"))
        except IOError:
            self.xmms = None

    def update_file_info(self, file):
        if self.xmms == None:
            return
        
        if file.is_directory():
            return
        
        uri = fileToXmmsUri(file)
        if self.xmms.medialib_get_id(uri) > 0:
            file.add_emblem("xmms2")
    
    def menuAdd(self, menu, files):
        for file in files:
            uri = fileToXmmsUri(file)
            self.xmms.medialib_add_entry(uri)
            file.invalidate_extension_info()
            
    def menuRemove(self, menu, files):
        for file in files:
            self.xmms.medialib_remove_entry(file.xmmsId)
            file.invalidate_extension_info()
            
    def menuRehash(self, menu, files):
        for file in files:
            self.xmms.medialib_rehash(file.xmmsId)
            file.invalidate_extension_info()
    
    def get_file_items(self, window, files):
        if self.xmms == None:
            return
        
        for file in files:
            if file.is_directory():
                return
        
        for file in files:
            file.xmmsId = self.xmms.medialib_get_id(fileToXmmsUri(file))
            
        allFilesHaveIds = True
        noFilesHaveIds = True
            
        for file in files:
            if allFilesHaveIds and file.xmmsId == 0:
                allFilesHaveIds = False
            if noFilesHaveIds and file.xmmsId > 0:
                noFilesHaveIds = False
            
        
        topItem = nautilus.MenuItem('Xmms2Nautilus::xmms2', 'xmms2', '', 'xmms2')

        menu = nautilus.Menu()
        topItem.set_submenu(menu)
        
        if noFilesHaveIds:
            menuItem = nautilus.MenuItem('Xmms2Nautilus::add', 'add', 'Add selected files from medialib', 'edit-add')
            menuItem.connect('activate', self.menuAdd, files)
            menu.append_item(menuItem)  
        
        if allFilesHaveIds:
            menuItem = nautilus.MenuItem('Xmms2Nautilus::remove', 'remove', 'Remove selected files from medialib', 'edit-delete')
            menuItem.connect('activate', self.menuRemove, files)
            menu.append_item(menuItem)
            
            menuItem = nautilus.MenuItem('Xmms2Nautilus::rehash', 'rehash', 'Reload metadata from selected files', 'reload')
            menuItem.connect('activate', self.menuRehash, files)
            menu.append_item(menuItem)

        return topItem,
