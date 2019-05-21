# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 - 2017 Pixar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# ##### END MIT LICENSE BLOCK #####

import os
import bpy
import bpy.utils.previews
from .. import util

asset_previews = bpy.utils.previews.new()

def get_presets_for_lib(lib):
    items = list(lib.presets)
    for sub_group in lib.sub_groups:
        items.extend(get_presets_for_lib(sub_group))
    return items

def load_previews(lib):
    global asset_previews
    enum_items = []

    lib_dir = presets_library = util.get_addon_prefs().presets_library.path

    items = get_presets_for_lib(lib)
    items = sorted(items, key=lambda item: item.label)

    for i, asset in enumerate(items):
        path = asset.path
        
        if path not in asset_previews:
            thumb_path = os.path.join(asset.path, 'asset_100.png')
            
            thumb = asset_previews.load(path, thumb_path, 'IMAGE', force_reload=True)
        else:
            thumb = asset_previews[path]
        enum_items.append((asset.path, asset.label, '', thumb.icon_id, i))

    return enum_items if enum_items else [('', '', '')]