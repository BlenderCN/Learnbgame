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
from bpy.props import FloatProperty, BoolProperty
from .sculpty import is_active, bake, bounding_box
from mathutils import Vector
from math import floor


class ObjectBakeSculpt(bpy.types.Operator):
    bl_idname = "object.sculpty_bake"
    bl_label = "Bake Sculpt Maps"
    bl_options = {'REGISTER'}

    red_scale = FloatProperty(name="Red X",
        description="Red Bake Range Scale",
        default=100.0, soft_min=0.0, soft_max=100.0,
        precision=4, step=39.2156863)
    green_scale = FloatProperty(name="Green Y",
        description="Green Bake Range Scale",
        default=100.0, soft_min=0.0, soft_max=100.0,
        precision=4, step=39.2156863)
    blue_scale = FloatProperty(name="Blue Z",
        description="Blue Bake Range Scale",
        default=100.0, soft_min=0.0, soft_max=100.0,
        precision=4, step=39.2156863)
    reset_origin = BoolProperty(name="Reset Origin",
        description="Sets object origins to geometry centers",
        default=True)
    aligned = BoolProperty(name="Aligned",
        description="Ensures exact alignment of multiple sculpties")
    optimise = BoolProperty(name="Optimise",
        description="Optimises colour ranges at a cost to alignment",
        default=True)
    use_objects = BoolProperty(name="Include objects in range size",
        description="Include object sizes in range calculations")
    no_dialog = BoolProperty(name="Bypass dialog",
        description="Bypass dialog and immediately bake with these settings")
    update_name = BoolProperty(name="Rename Maps",
        description="Rename sculpt maps to match object names",
        default=False)
    sculpties = []
    objects = []

    def draw_objs(self, layout):
        if self.objects != []:
            split = layout.split(0.33)
            split.label("Objects:", 'OBJECT_DATAMODE')
            col = split.column()
            for obj in self.objects:
                if 'sculptie' in obj.data.uv_textures:
                    col.label(obj.name + ' (no sculpt map)', 'ERROR')
                else:
                    col.label(obj.name)
                if self.sculpties != []:
                    col.prop(self, 'use_objects')
                layout.separator()

    def draw(self, context):
        layout = self.layout
        if self.sculpties == []:
            layout.label('No sculpty objects selected', 'ERROR')
            self.draw_objs(layout)
        else:
            split = layout.split(0.33)
            split.label("Colour Range", 'COLOR')
            col = split.column()
            col.prop(self, 'red_scale')
            col.prop(self, 'green_scale')
            col.prop(self, 'blue_scale')
            self.draw_objs(layout)
            split = layout.split(0.33)
            split.label("Sculpties:", 'MESH_MONKEY')
            col = split.column()
            for obj in self.sculpties:
                txt = "%s"
                if self.reset_origin:
                    for m in obj.modifiers:
                        if m.type == 'MIRROR':
                            txt = "%s has mirror, can't reset origin"
                col.label(txt % obj.name)
            if len(self.sculpties) > 1:
                r = col.row()
                r.prop(self, 'aligned')
                r.prop(self, 'optimise')
            r = col.row()
            r.prop(self, 'reset_origin')
            r.prop(self, 'update_name')

    def execute(self, context):
        if self.sculpties == []:
            return {'CANCELLED'}
        sculpt_bb = {}
        gmin = None
        gmax = None
        edit_mode = context.mode == 'EDIT_MESH'
        if edit_mode:
            bpy.ops.object.editmode_toggle()
        if self.reset_origin:
            for obj in self.sculpties + self.objects:
                if 'MIRROR' not in [m.type for m in obj.modifiers]:
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',
                        center='MEDIAN')
        for obj in self.sculpties:
            mesh = obj.to_mesh(context.scene, True, 'RENDER')
            vmin, vmax = bounding_box(mesh)
            if not self.reset_origin:
                vmax.x = max(abs(vmin.x), abs(vmax.x))
                vmin.x = -vmax.x
                vmax.y = max(abs(vmin.y), abs(vmax.y))
                vmin.y = -vmax.y
                vmax.z = max(abs(vmin.z), abs(vmax.z))
                vmin.z = -vmax.z
            if self.aligned:
                if gmin is None:
                    gmin = Vector((vmin.x, vmin.y, vmin.z))
                    gmax = Vector((vmax.x, vmax.y, vmax.z))
                else:
                    gmin.x = min(gmin.x, vmin.x)
                    gmin.y = min(gmin.y, vmin.y)
                    gmin.z = min(gmin.z, vmin.z)
                    gmax.x = max(gmax.x, vmax.x)
                    gmax.y = max(gmax.y, vmax.y)
                    gmax.z = max(gmax.z, vmax.z)
            sculpt_bb[obj.name] = (vmin, vmax)
        if self.use_objects:
            for obj in self.objects:
                mesh = obj.to_mesh(context.scene, True, 'RENDER')
                vmin, vmax = bounding_box(mesh)
                if gmin is None:
                    gmin = Vector((vmin.x, vmin.y, vmin.z))
                    gmax = Vector((vmax.x, vmax.y, vmax.z))
                else:
                    gmin.x = min(gmin.x, vmin.x)
                    gmin.y = min(gmin.y, vmin.y)
                    gmin.z = min(gmin.z, vmin.z)
                    gmax.x = max(gmax.x, vmax.x)
                    gmax.y = max(gmax.y, vmax.y)
                    gmax.z = max(gmax.z, vmax.z)
            if not self.reset_origin:
                gmax.x = max(abs(gmin.x), abs(gmax.x))
                gmin.x = -gmax.x
                gmax.y = max(abs(gmin.y), abs(gmax.y))
                gmin.y = -gmax.y
                gmax.z = max(abs(gmin.z), abs(gmax.z))
                gmin.z = -gmax.z
        for obj_name in sculpt_bb:
            smin, smax = sculpt_bb[obj_name]
            if gmin is not None:
                if self.aligned:
                    vmin = Vector((gmin.x, gmin.y, gmin.z))
                    vmax = Vector((gmax.x, gmax.y, gmax.z))
                else:
                    vmin.x = min(gmin.x, smin.x)
                    vmin.y = min(gmin.y, smin.y)
                    vmin.z = min(gmin.z, smin.z)
                    vmax.x = max(gmax.x, smax.x)
                    vmax.y = max(gmax.y, smax.y)
                    vmax.z = max(gmax.z, smax.z)
                if self.optimise:
                    # try to improve bake range. Make sure that
                    # any increases don't go beyond the original mesh
                    f = floor((vmax.x - vmin.x) / (smax.x - smin.x))
                    if f > 1.0:
                        size = (vmax.x - vmin.x) * 0.5
                        center = vmin.x + size
                        vmin.x = center - size / f
                        vmax.x = center + size / f
                    f = floor((vmax.y - vmin.y) / (smax.y - smin.y))
                    if f > 1.0:
                        size = (vmax.y - vmin.y) * 0.5
                        center = vmin.y + size
                        vmin.y = center - size / f
                        vmax.y = center + size / f
                    f = floor((vmax.z - vmin.z) / (smax.z - smin.z))
                    if f > 1.0:
                        size = (vmax.z - vmin.z) * 0.5
                        center = vmin.z + size
                        vmin.z = center - size / f
                        vmax.z = center + size / f
            else:
                vmin = smin
                vmax = smax
            if self.red_scale != 100.0:
                red_range = vmax.x - vmin.x
                if self.red_scale == 0.0:
                    red_adjust = red_range / 2.0
                else:
                    new_range = red_range * 100.0 / self.red_scale
                    red_adjust = (new_range - red_range) / 2.0
                vmin.x -= red_adjust
                vmax.x += red_adjust
            if self.green_scale != 100.0:
                green_range = vmax.y - vmin.y
                if self.green_scale == 0.0:
                    green_adjust = green_range / 2.0
                else:
                    new_range = green_range * 100.0 / self.green_scale
                    green_adjust = (new_range - green_range) / 2.0
                vmin.y -= green_adjust
                vmax.y += green_adjust
            if self.blue_scale != 100.0:
                blue_range = vmax.z - vmin.z
                if self.blue_scale == 0.0:
                    blue_adjust = blue_range / 2.0
                else:
                    new_range = blue_range * 100.0 / self.blue_scale
                    blue_adjust = (new_range - blue_range) / 2.0
                vmin.z -= blue_adjust
                vmax.z += blue_adjust
            bake(bpy.data.objects[obj_name], context.scene,
                vmin, vmax, self.update_name)
        for a in context.window.screen.areas:
            for s in a.spaces:
                if s.type == 'IMAGE_EDITOR':
                    # force refresh for missing images set to generated
                    if s.image is not None:
                        t = bpy.data.images[s.image.name]
                        s.image = t
            if a.type == 'IMAGE_EDITOR':
                a.tag_redraw()
        if edit_mode:
            bpy.ops.object.editmode_toggle()
        if not self.no_dialog:
            context.scene['sculpty_bake'] = {
                'r': self.red_scale,
                'g': self.green_scale,
                'b': self.blue_scale,
                'ro': self.reset_origin,
                'uo': self.use_objects,
                'a': self.aligned,
                'o': self.optimise}
        return {'FINISHED'}

    def invoke(self, context, event):
        self.sculpties = []
        self.objects = []
        if 'sculpty_bake' in context.scene and not self.no_dialog:
            settings = context.scene['sculpty_bake']
            self.red_scale = settings['r']
            self.green_scale = settings['g']
            self.blue_scale = settings['b']
            self.reset_origin = settings['ro']
            self.use_objects = settings['uo']
            self.aligned = settings['a']
            self.optimise = settings['o']
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()
            if is_active(context.active_object):
                self.sculpties.append(context.active_object)
            else:
                self.objects.append(context.active_object)
            bpy.ops.object.editmode_toggle()
        else:
            for obj in context.scene.objects:
                if obj.select:
                    if obj.type == 'MESH':
                        if is_active(obj):
                            self.sculpties.append(obj)
                        else:
                            self.objects.append(obj)
        if self.no_dialog:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self)
