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
import base64
import os

from urllib.request import urlopen
from urllib.parse import urlencode
from xml.dom import minidom

def upload_image(path_to_image):

    url = 'http://api.imgur.com/2/upload.xml'
    apikey = '-----------your api key-------------'
    identifiers = 'imgur_page|original|delete_page|large_thumbnail'.split('|')

    if apikey.startswith('-----'):
        print('fill in the API key, visit http://api.imgur.com get one')
        return
    
    def xml_reader(xml_to_read):
        doc_ob = minidom.parseString(xml_to_read)
        for identifier in identifiers:
            co = doc_ob.getElementsByTagName(identifier)
            content = co[0].lastChild.toxml().strip()
            print(content + ' ('+identifier+')')

    def encoded_image():
        source = open(path_to_image, 'rb')
        return base64.b64encode(source.read())

    def pack_data():
        parameters = { 'key': apikey, 'image': encoded_image()}
        return urlencode(parameters).encode('utf-8')

    data = pack_data()
    print('encoded, sending...')
    xml_to_parse = urlopen(url, data)

    print('received response from server')
    xml_reader(xml_to_parse.readall().decode())



class ImageUploadButton(bpy.types.Operator):
    bl_idname = "scene.upload_imgur"
    bl_label = "Upload image slot to imgur"
 
    def execute(self, context):
        print(dir(context.edit_image))
        c_img = context.edit_image
        file_name = c_img.name        
        file_format = c_img.file_format

        path_pre_file = '/tmp'
        img = bpy.data.images[file_name]
        path_to_image = os.path.join(path_pre_file, 'imgur_upload.png')

        if len(img.pixels) == 0:
            img.save_render(path_to_image)
        else:
            img.filepath_raw = path_to_image
            img.save()

        try:
            upload_image(path_to_image)
        except:
            print('failed')

        return{'FINISHED'}  


class ImageUploadPanel(bpy.types.Panel):
    bl_label = "Upload Imgur"
    bl_idname = "OBJECT_PT_imgurfunction"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        scn = bpy.context.scene
        self.layout.operator("scene.upload_imgur", text='Upload from .blend')