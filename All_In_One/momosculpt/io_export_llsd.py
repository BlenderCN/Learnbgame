# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import os
from .sculpty import ImageBuffer
from .llbase import llsd


def child_objs(object):
    objs = [object]
    for obj in object.children:
        objs.extend(child_objs(obj))
    return objs

class ExportLLSD(bpy.types.Operator):
    bl_idname = "export.llsd"
    bl_label = "LLSD Primitives (.xml, .tga)"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(name='Directory',
        subtype='DIR_PATH')

    version = bpy.props.EnumProperty(name='Version',
        items=(
            ('3', '3', 'MoMoSculpt compatible viewers'),
            ('2', '2', 'Phoenix viewer'),
            ('1', '1', 'Imprudence viewer')),
            description='LLSD version to use for XML files',
            default='1')

    format = bpy.props.EnumProperty(name='Image Type',
        items=(
        ('TARGA', 'tga', 'Targa'),
        ('PNG', 'png', 'Portable network graphic'),
        ('JPEG2000', 'jp2', 'Jpeg 2000')),
        description='Image format to save',
        default='TARGA')

    alpha = bpy.props.EnumProperty(name='Alpha',
        items=(
            ('NONE', 'None', 'No alpha channel'),
            ('CLEAR', 'Clear', '100% transparent'),
            ('SOLID', 'Solid', '100% opaque'),
            ('PREVIEW', 'Preview', '3D preview')),
        description='Alpha channel type',
        default='NONE')

    filename = ''
    dirname = ''

    def image_ext(self):
        if self.format == 'PNG':
            e = 'png'
        elif self.format == 'JPEG2000':
            e = 'jp2'
        else:
            e = 'tga'
        return e

    def save_map(self, image):
        fn = bpy.path.clean_name(image.name)
        image.file_format = self.format
        fn = os.path.join(self.dirname, fn) + '.' + self.image_ext()
        image.filepath_raw = fn
        if self.alpha == 'NONE':
            img = bpy.data.images.new("Temp",
                image.size[0],
                image.size[1],
                alpha=False)
            img.pixels = list(image.pixels)
            img.filepath_raw = fn
            img.file_format = self.format
            img.save()
            bpy.data.images.remove(img)
            return
        elif self.alpha in ['CLEAR', 'SOLID']:
            src = ImageBuffer(image, clear=False)
            if self.alpha == 'SOLID':
                v = 1.0
            else:
                v = 0.0
            src.clear_alpha(v)
            src.update()
        image.save()

    def prim_to_py(self, object):
        if 'prim' not in object:
            return None
        obj = {}
        obj['position'] = [f for f in object.location]
        obj['rotation'] = [f for f in object.rotation_quaternion]
        if object.prim.type == 'PRIM_TYPE_SCULPT':
            img = object.data.uv_textures['sculptie'].data[0].image
            if img is None:
                return None
            else:
                self.save_map(img)
            if 'vmin' in img:
                vmin = img['vmin']
                vmax = img['vmax']
                vscale = img['vscale']
                sx = vmax[0] - vmin[0]
                sy = vmax[1] - vmin[1]
                sz = vmax[2] - vmin[2]
                rx = object.scale[0] / vscale[0]
                ry = object.scale[1] / vscale[1]
                rz = object.scale[2] / vscale[2]
                scale = [
                    sx * vscale[0] * rx,
                    sy * vscale[1] * ry,
                    sz * vscale[2] * rz]
                obj['scale'] = [f for f in scale]
            else:
                obj['scale'] = [f for f in object.scale]
            obj['sculpt'] = {}
            fn = bpy.path.clean_name(img.name) + '.' + self.image_ext()
            obj['sculpt']['texture'] = fn
            buffer = ImageBuffer(img, clear=False)
            map_type = buffer.map_type()
            t = ['NONE', 'SPHERE', 'TORUS', 'PLANE', 'CYLINDER'].index(map_type)
            obj['sculpt']['type'] = t
        else:
            obj['scale'] = [f for f in object.scale]
        for uv in object.data.uv_textures:
            if uv.name[:5] == 'UVTex':
                img = uv.data[0].image
                if img is not None:
                    fn = bpy.path.clean_name(img.name)
                    img.file_format = self.format
                    fn = os.path.join(self.dirname, fn) + '.' + self.image_ext()
                    img.filepath_raw = fn
                    img.save()
        return obj

    def execute(self, context):
        fn = os.path.basename(self.filepath)
        if fn == '':
            fn = os.path.basename(bpy.data.filepath)
            if fn == '':
                fn = 'primitives'
            else:
                fn = os.path.splitext(fn)[0]
        fn = bpy.path.clean_name(fn)
        if fn[-4:] != '.xml':
            fn = fn + '.xml'
        self.dirname = os.path.dirname(self.filepath)
        self.filename = fn
        if not os.path.exists(self.dirname):
            self.report({'ERROR'},
                    "Directory does not exist.")
            return {'CANCELLED'}
        prims = {}
        pyll = {}
        # version 1
        pyll['data'] = []
        objects = [o for o in context.selected_objects]
        for obj in context.selected_objects:
            for child in child_objs(obj)[1:]:
                if child in objects:
                    objects.remove(child)
        for obj in objects:
            body = {}
            prims = {}
            p = self.prim_to_py(obj)
            if p is not None:
                body['root_position'] = p['position']
                body['root_rotation'] = p['rotation']
                prims[obj.name] = p
                for child in child_objs(obj)[1:]:
                    c = self.prim_to_py(child)
                    if c is not None:
                        c['parent'] = obj.name
                        prims[child.name] = c
                body['group_body'] = prims
            pyll['data'].append(body)
        f = open(os.path.join(self.dirname, self.filename), 'w')
        f.write(llsd.format_pretty_xml(pyll))
        f.close()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
