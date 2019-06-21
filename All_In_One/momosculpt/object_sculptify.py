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

from .sculpty import map_size, sculpt_type, map_pixels
from . import config
from math import ceil, log


class ObjectSculptify(bpy.types.Operator):
    '''Sculptify Object'''
    bl_idname = "object.sculptify"
    bl_label = "Sculptify Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type in ['MESH', 'SURFACE', 'CURVE'])

    def execute(self, context):
        obj = context.active_object

        # Toggle Edit mode
        is_editmode = (obj.mode == 'EDIT')
        if is_editmode:
            bpy.ops.object.mode_set(mode='OBJECT')

        conv = False
        if obj.type != 'MESH':
            bpy.ops.object.convert(target='MESH', keep_original=False)
            conv = True

        uvs = obj.data.uv_textures
        if 'UVTex' in uvs:
            uvtex = True
            uvs.active = uvs['UVTex']
            tex = uvs.active.data[0].image
            bpy.ops.mesh.uv_texture_remove()
        else:
            tex = None
            uvtex = False
        if 'sculptie' not in uvs:
            uvs.new(name='sculptie')
        uvs.active = uvs['sculptie']
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        if conv:
            bpy.ops.mesh.normals_make_consistent(inside=False)
        obj.data.faces.active = obj.data.faces[0].index
        bpy.ops.uv.reset()
        bpy.ops.object.mode_set(mode='OBJECT')
        if obj.data.faces[0].normal[2] < 0 and not conv:
            f = uvs['sculptie'].data[0]
            for i in range(1, len(f.uv_raw), 2):
                f.uv_raw[i - 1], f.uv_raw[i] = f.uv_raw[i], f.uv_raw[i - 1]
                if obj.data.faces[0].normal[0] < 0:
                    f.uv_raw[i - 1] = 1.0 - f.uv_raw[i - 1]
                if obj.data.faces[0].normal[1] < 0:
                    f.uv_raw[i] = 1.0 - f.uv_raw[i]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.follow_active_quads(mode='EVEN')
        bpy.ops.uv.to_bounds()
        uc = 0
        vc = 0
        bpy.ops.object.mode_set(mode='OBJECT')
        for f in uvs.active.data:
            if len(f.uv) < 4:
                self.report({'ERROR'},
                    "Sculptify: Mesh has triangle faces.")
                return {'CANCELLED'}
            for u, v in f.uv:
                if v < 0.002:
                    uc += 1
                if u < 0.002:
                    vc += 1
        uc = int(uc / 2)
        vc = int(vc / 2)
        lod = 3
        while uc < 4 or vc < 4:
            uc *= 2
            vc *= 2
        levels = 0
        for m in obj.modifiers:
            if m.type == 'SUBSURF':
                levels += max(m.levels, m.render_levels)
            elif m.type == 'MULTIRES':
                levels += max(m.levels, m.render_levels, m.sculpt_levels)
        s, t, w, h, cs, ct = map_size(uc, vc, levels)
        if not config.minimise_map:
            while w * h <= 1024:
                levels += 1
                lod -= 1
                s, t, w, h, cs, ct = map_size(uc, vc, levels)
            lod = max(lod, 1)
        if uvs.active.data[0].image is None:
            img = bpy.data.images.new(name=obj.name,
                width=w,
                height=h,
                alpha=True)
            for f in uvs.active.data:
                f.image = img
                f.use_image = True
        else:
            img = uvs.active.data[0].image
            img.source = 'GENERATED'
            img.generated_width = w
            img.generated_height = h
        ss, ts = map_pixels(w, h, [lod])
        ss[-1] = w
        ts[-1] = h
        wt = len(ss) - 1
        ht = len(ts) - 1
        for f in uvs.active.data:
            for i in range(len(f.uv_raw)):
                if i % 2:
                    idx = int(f.uv_raw[i] * ht)
                    f.uv_raw[i] = ts[idx] / h
                else:
                    idx = int(f.uv_raw[i] * wt)
                    f.uv_raw[i] = ss[idx] / w
        if uvtex:
            uvs.new(name='UVTex')
            uvs.active = uvs['UVTex']
            for f in uvs.active.data:
                f.image = tex
                if tex is not None:
                    f.use_image = True
        if is_editmode:
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            obj.data.update_tag()
        obj.prim.type = 'PRIM_TYPE_SCULPT'
        obj.prim.sculpt_type = 'PRIM_SCULPT_TYPE_%s' % sculpt_type(obj)
        return {'FINISHED'}
