# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#   the Free Software Foundation Inc.
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

import bpy
import json
from urllib.request import urlopen

def get_raw_url_from_gist_id(gist_id):
    
    gist_id = str(gist_id)
    url = 'https://api.github.com/gists/' + gist_id
    
    found_json = urlopen(url).readall().decode()

    wfile = json.JSONDecoder()
    wjson = wfile.decode(found_json)

    # 'files' may contain several - this will mess up gist name.
    files_flag = 'files'
    file_names = list(wjson[files_flag].keys())
    file_name = file_names[0]
    return wjson[files_flag][file_name]['raw_url']


def get_file(gist_id):
    url = get_raw_url_from_gist_id(gist_id)
    conn = urlopen(url).readall().decode()
    return conn


class GistDownloadButton(bpy.types.Operator):
    """Defines a button"""
    bl_idname = "scene.download_gist"
    bl_label = "Download given gist from id only"
 
    def execute(self, context):
        # could name this filename instead of gist_id for new .blend text.
        gist_id = context.scene.gist_id_property
        bpy.data.texts.new(gist_id)
        bpy.data.texts[gist_id].write(get_file(gist_id))
        return{'FINISHED'}


class GistDownloadPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Download Gist"
    bl_idname = "OBJECT_PT_somefunction"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        scn = bpy.context.scene

        # display stringbox and download button
        self.layout.prop(scn, "gist_id_property")
        self.layout.operator("scene.download_gist", text='Download to .blend')









