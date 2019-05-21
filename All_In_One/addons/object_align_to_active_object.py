# coding: utf-8

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

bl_info = {
    'name': 'Align to Active Object',
    'author': 'chromoly',
    'version': (0, 3),
    'blender': (2, 5, 6),
    'api': 34765,
    'location': 'View3D Header > Object Menu > Transform',
    'description': '',
    'category': 'Object'}


#import math
#from functools import reduce
import itertools

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Matrix, Vector, Quaternion
#from va.object import sorted_parent_and_child, object_children

BP = BoolProperty


def sorted_parent_and_child(obs, ob_children={}):
    '''親から順に返すジェネレータ。'''
    if not ob_children:
        ob_parent = {ob: None for ob in obs}
        for ob in obs:
            if ob.parent in ob_parent:
                ob_parent[ob] = ob.parent
            else:
                # [parent] ob1 - ob9_not_obs - ob2 [child]
                tmp = ob.parent
                while tmp:
                    if tmp in ob_parent:
                        ob_parent[ob] = tmp
                        break
                    tmp = tmp.parent

        ob_children = {ob: [] for ob in obs}
        for ob, parent in ob_parent.items():
            if parent:
                ob_children[parent].append(ob)
        obs = [ob for ob, parent in ob_parent.items() if not parent]

    for ob in obs:
        yield ob

        for o in sorted_parent_and_child(ob_children[ob], ob_children):
            yield o


def object_children(ob, insert_none=False, root=True):
    '''
    全ての子を順に返すジェネレータ。
    insert_none: if not object.children, return None
    '''
    if not root:
        yield ob
    for child in ob.children:
        for o in object_children(child, insert_none, False):
            yield o
    if not ob.children and insert_none:
        yield None


class OBJECT_OT_align_to_active_object(bpy.types.Operator):
    '''Selected objects align to active object.'''
    bl_idname = 'object.align_to_active_object'
    bl_label = 'Align to Active Object'
    bl_description = 'Selected objects align to active object'
    bl_options = {'REGISTER', 'UNDO'}

    location = BP(name='Location', default=False)
    rotation = BP(name='Rotation', default=False)
    keep_location = BP(name='Keep Location',
                       description='When rotate, keep location',
                       default=True)
    keep_deselected_location = BP(name='Keep Desel Location',
                       description='When rotate or translate, keep deselected objects location',
                       default=True)
    keep_deselected_rotation = BP(name='Keep Desel Rotation',
                       description='When rotate, keep deselected objects rotations',
                       default=True)
    force_calc = BP(default=False, options={'HIDDEN'})
    empty_options = BP(name='Empty Options', default=False)
    color_wire = BP(name='Color Wire', default=False)

    @classmethod
    def poll(cls, context):
        actob = context.active_object
        return actob and actob.select and len(context.selected_objects) >= 2

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'location', toggle=True)
        col.prop(self, 'rotation', toggle=True)
        col.prop(self, 'keep_location')
        col.prop(self, 'keep_deselected_location')
        col.prop(self, 'keep_deselected_rotation')
        col.separator()
        col.prop(self, 'empty_options', toggle=True)
        col.prop(self, 'color_wire', toggle=True)

    def calc(self, context):
        actob = context.active_object
        selobs = [ob for ob in context.selected_objects if ob != actob]
        if (actob and not actob.select) or not(actob and selobs):
            return None
        selobs.append(actob)

        # Shift + D -> Rigt mouse で複製した直後のバグ?対策。
        # Shift + D -> Enter だと問題無し。
        for ob, loc in zip(context.selected_objects, self.locs):
            ob.matrix_world[3][:3] = loc

        sorted_objects = list(sorted_parent_and_child(selobs))
        objects_set = set(sorted_objects)

        root_obs = []
        for ob in sorted_objects:
            tmp = ob
            while tmp:
                tmp = tmp.parent
                if not tmp:
                    root_obs.append(ob)
                    break
                elif tmp in objects_set:
                    break
        #need_scene_update = set()  # context.scene.update()
        need_transform = set()  # deselected objects
        apply_objects = root_obs[:]  # apply transform
        for ob in root_obs:
            for tmp in object_children(ob):
                if tmp and tmp not in objects_set:
                    need_transform.add(tmp)
                    '''if tmp.parent in objects_set:
                        need_scene_update.add(tmp.parent)
                    '''
                apply_objects.append(tmp)

        sorted_apply_objects = list(sorted_parent_and_child(apply_objects))
        ob_loc = {ob.name: ob.matrix_world[3][:3] for ob in apply_objects}
        deselob_rmat = {}
        for ob in need_transform:
            mat3 = ob.matrix_world.to_3x3()
            rmat = mat3.to_euler().to_matrix()
            deselob_rmat[ob.name] = rmat

        #self.selobs = selobs
        self.objects_set = {ob.name for ob in objects_set}
        #self.need_scene_update = {ob.name for ob in need_scene_update}
        self.sorted_apply_objects = [ob.name for ob in sorted_apply_objects]
        self.ob_loc = ob_loc
        self.deselob_rmat = deselob_rmat

    def execute(self, context):
        if self.force_calc:
            self.force_calc = False
            self.locs = [Vector(ob.matrix_world[3][:3]) for ob in
                         context.selected_objects]
            self.calc(context)
            context.area.tag_redraw()
        scn = context.scene
        actob = context.active_object
        selobs = [ob for ob in context.selected_objects if ob != actob]
        if (actob and not actob.select) or not(actob and selobs):
            return {'FINISHED'}
        #selobs.append(actob)

        obs = scn.objects
        objects_set = {obs[name] for name in self.objects_set}
        #need_scene_update = {obs[name] for name in self.need_scene_update}
        sorted_apply_objects = [obs[name] for name in \
                                self.sorted_apply_objects]
        ob_loc = {obs[name]: val for name, val in self.ob_loc.items()}
        deselob_rmat = {obs[name]: val for name, val in \
                        self.deselob_rmat.items()}

        actobloc = actob.matrix_world[3][:3]
        if self.rotation:
            # e.g. m1 * m2 = m3; m1 = m3 * m2.inverted(); m2 = m1.inverted() * m3
            orient_bak = context.space_data.transform_orientation
            context.space_data.transform_orientation = 'LOCAL'
            bpy.ops.transform.create_orientation(use=True)
            orient_rot = context.space_data.current_orientation.matrix.copy()
            for ob in objects_set:
                ob.select = False
            for ob in sorted_apply_objects:
                ob.select = True
                if ob in objects_set:
                    context.space_data.current_orientation.matrix = orient_rot
                    bpy.ops.transform.transform('INVOKE_REGION_WIN',
                                                value=(0.0, 0.0, 0.0, 0.0),
                                                mode='ALIGN')
                    if self.keep_location:
                        ob.matrix_world[3][:3] = ob_loc[ob]
                    pass
                else:
                    if self.keep_deselected_rotation:
                        rmat = deselob_rmat[ob]
                        context.space_data.current_orientation.matrix = rmat
                        bpy.ops.transform.transform('INVOKE_REGION_WIN',
                                                    value=(0.0, 0.0, 0.0, 0.0),
                                                    mode='ALIGN')
                    if self.keep_deselected_location:
                        ob.matrix_world[3][:3] = ob_loc[ob]
                ob.select = False
            for ob in objects_set:
                ob.select = True
            bpy.ops.transform.delete_orientation()
            context.space_data.transform_orientation = orient_bak
        if self.location:
            for ob in sorted_apply_objects:
                if ob in objects_set:
                    '''if ob in need_scene_update:
                        context.scene.update()
                    '''
                    ob.matrix_world[3][:3] = actobloc
                elif self.keep_deselected_location:
                    ob.matrix_world[3][:3] = ob_loc[ob]
        if self.empty_options:
            if actob.type == 'EMPTY':
                for ob in (ob for ob in objects_set if ob.type == 'EMPTY'):
                    ob.empty_draw_type = actob.empty_draw_type
                    ob.empty_draw_size = actob.empty_draw_size
        if self.color_wire:
            for ob in objects_set:
                if hasattr(ob, 'color_wire'):
                    ob.color_wire = actob.color_wire
                    ob.wire_color[:] = actob.wire_color[:]
        return {'FINISHED'}

    def invoke(self, context, event):
        self.locs = [Vector(ob.matrix_world[3][:3]) for ob in
                     context.selected_objects]
        self.calc(context)
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_MT_align_to_active_object(bpy.types.Menu):
    bl_label = 'Align to Active Object'

    @classmethod
    def poll(cls, context):
        return context.active_object

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        idname = 'object.align_to_active_object'
        layout.operator(idname, text='Location').location = True
        layout.operator(idname, text='Rotation').rotation = True
        layout.operator(idname, text='Empty Options').empty_options = True
        layout.operator(idname, text='Color Wire').color_wire = True


def menu_func_copy(self, context):
    self.layout.menu('OBJECT_MT_align_to_active_object',
                     text='World Coordinate')


def menu_func_transform(self, context):
    op = self.layout.operator('object.align_to_active_object',
                              text='Align to Active Object')
    op.force_calc = True  # if can't call invoke.
    #op.location = True
    op.rotation = True


# Register
def register():
    bpy.utils.register_module(__name__)

    try:
        bpy.types.VIEW3D_MT_copypopup.append(menu_func_copy)
    except:
        pass
    bpy.types.VIEW3D_MT_transform.append(menu_func_transform)


def unregister():
    bpy.utils.unregister_module(__name__)

    try:
        bpy.types.VIEW3D_MT_copypopup.remove(menu_func_copy)
    except:
        pass
    bpy.types.VIEW3D_MT_transform.remove(menu_func_transform)


if __name__ == '__main__':
    register()
