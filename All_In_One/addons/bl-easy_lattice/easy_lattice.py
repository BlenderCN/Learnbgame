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


import bpy
import mathutils
import math


MODIFIER_NAME = "easy_lattice_tmp"
LATTICE_OBJECT_NAME = "EasyLatticeTemp"
VERTEX_GROUP_NAME = "easy_lattice_vg"


def lattice_delete(obj):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if LATTICE_OBJECT_NAME in ob.name:
            ob.select = True
    bpy.ops.object.delete(use_global=False)

    # select the original object back
    obj.select = True


def create_lattice(obj, size, pos, props):
    # Create lattice and object
    lat = bpy.data.lattices.new(LATTICE_OBJECT_NAME)
    ob = bpy.data.objects.new(LATTICE_OBJECT_NAME, lat)

    # the position comes from the bbox
    ob.location = pos

    # the size  from bbox
    ob.scale = size

    # the rotation comes from the combined obj world matrix which was
    # converted to euler pairs.
    loc, rot, scl = obj.matrix_world.decompose()
    ob.rotation_euler = rot.to_euler()

    ob.show_x_ray = True
    # Link object to scene
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    scn.update()

    # Set lattice attributes
    lat_u, lat_v, lat_w, lat_interpolation = props

    lat.interpolation_type_u = lat_interpolation
    lat.interpolation_type_v = lat_interpolation
    lat.interpolation_type_w = lat_interpolation

    lat.use_outside = False

    lat.points_u = lat_u
    lat.points_v = lat_v
    lat.points_w = lat_w

    return ob


def find_bbox(obj, selected_verts):
    # Build world matrix with translation and scale but leave out the rotation.
    loc, rot, scl = obj.matrix_world.decompose()
    mat_trans = mathutils.Matrix.Translation(loc)

    mat_scale = mathutils.Matrix.Scale(scl[0], 4, (1, 0, 0))
    mat_scale *= mathutils.Matrix.Scale(scl[1], 4, (0, 1, 0))
    mat_scale *= mathutils.Matrix.Scale(scl[2], 4, (0, 0, 1))

    mat_no_rot = mat_trans * mat_scale

    mat_world = obj.matrix_world

    min_x, min_y, min_z = selected_verts[0].co
    max_x, max_y, max_z = selected_verts[0].co

    for c in range(len(selected_verts)):
        co = selected_verts[c].co

        if co.x < min_x:
            min_x = co.x
        if co.y < min_y:
            min_y = co.y
        if co.z < min_z:
            min_z = co.z

        if co.x > max_x:
            max_x = co.x
        if co.y > max_y:
            max_y = co.y
        if co.z > max_z:
            max_z = co.z

    min_point = mathutils.Vector((min_x, min_y, min_z))
    max_point = mathutils.Vector((max_x, max_y, max_z))

    middle = ((min_point + max_point) / 2)

    min_point = mat_no_rot * min_point  # Calculate only based on loc/scale
    max_point = mat_no_rot * max_point  # Calculate only based on loc/scale
    # the middle has to be calculated based on the real world matrix
    middle = mat_world * middle

    size = max_point - min_point
    size = mathutils.Vector((abs(size.x), abs(size.y), abs(size.z)))

    return min_point, max_point, size, middle


def delete_group(obj):
    # Delete vertex group we were using on last lattice
    for grp in obj.vertex_groups:
        if VERTEX_GROUP_NAME in grp.name:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=obj.name, extend=False)
            bpy.ops.object.vertex_group_set_active(group=grp.name)
            bpy.ops.object.vertex_group_remove()
            break


def easy_lattice(lattice_properties):
    current_object = bpy.context.object

    if current_object.type == "MESH":
        # set global property for the currently active latticed object
        bpy.types.Scene.active_lattice_object = bpy.props.StringProperty(
            name="current_lattice_object", default="")
        bpy.types.Scene.active_lattice_object = current_object.name

        if current_object.mode == "EDIT":
            bpy.ops.object.editmode_toggle()

        # Apply current lattice modifier
        for mod in current_object.modifiers:
            if mod.name == MODIFIER_NAME:
                if mod.object == bpy.data.objects[LATTICE_OBJECT_NAME]:
                    bpy.ops.object.modifier_apply(
                        apply_as='DATA', modifier=mod.name)

        # Delete vertex group we were using on last lattice
        delete_group(current_object)

        # Create new vertex group
        vertex_grp = current_object.vertex_groups.new(VERTEX_GROUP_NAME)

        # And add selected vertices to it
        selected_verts = []
        for vert in current_object.data.vertices:
            if vert.select:
                selected_verts.append(vert)
                vertex_grp.add([vert.index], 1.0, "REPLACE")

        # Get size and position for lattice based on selected vertices bounding
        # box
        _, _, size, pos = find_bbox(current_object, selected_verts)

        # Delete lattice for current object
        lattice_delete(current_object)

        # Create new lattice object and lattice modifier and link them together
        lat = create_lattice(current_object, size, pos, lattice_properties)
        modif = current_object.modifiers.new(MODIFIER_NAME, "LATTICE")
        modif.object = lat
        modif.vertex_group = VERTEX_GROUP_NAME

        # Select newly created lattice
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=lat.name, extend=False)
        bpy.context.scene.objects.active = lat

        bpy.context.scene.update()
        # And go into edit mode for quick editing
        bpy.ops.object.mode_set(mode='EDIT')

    # If we easy_lattice on lattice, apply modifiers and delete it.
    if current_object.type == "LATTICE":
        if bpy.types.Scene.active_lattice_object:
            name = bpy.types.Scene.active_lattice_object

            if current_object.mode == "EDIT":
                bpy.ops.object.editmode_toggle()

            for ob in bpy.context.scene.objects:
                if ob.name == name:  # found the object with the lattice mod
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.ops.object.select_pattern(
                        pattern=ob.name, extend=False)
                    bpy.context.scene.objects.active = ob

                    for mod in ob.modifiers:
                        if mod.name == MODIFIER_NAME:
                            if mod.object == bpy.data.objects[
                                    LATTICE_OBJECT_NAME]:
                                bpy.ops.object.modifier_apply(
                                    apply_as='DATA', modifier=mod.name)
                                delete_group(mod.object)
                    lattice_delete(current_object)
    return


class EasyLattice(bpy.types.Operator):
    """
    Easy Lattice.
    If selected object is a mesh lattice will be created based on its selected 
    vertices. 
    To apply lattice either run this operator again with lattice selected,
    or create new one on a object
    """
    bl_idname = "object.easy_lattice"
    bl_label = "Easy Lattice"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    lat_u = bpy.props.IntProperty(name="Lattice u", default=3)
    lat_v = bpy.props.IntProperty(name="Lattice v", default=3)
    lat_w = bpy.props.IntProperty(name="Lattice w", default=3)

    lat_interpolation_types = (
        ('KEY_LINEAR',
         'Linear',
         'Use linear interpolation on effected vertices.'),
        ('KEY_CARDINAL',
         'Cardinal',
         'Use cardinal interpolation on effected vertices.'),
        ('KEY_CATMULL_ROM',
         'Catmull-Rom',
         'Use Catmull-Rom interpolation on effected vertices.'),
        ('KEY_BSPLINE',
         'BSpline',
         'Use BSpline interpolation on effected vertices.'))

    lat_interpolation = bpy.props.EnumProperty(
        name="Lattice interpolation",
        items=lat_interpolation_types,
        default='KEY_LINEAR')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        lat_u = self.lat_u
        lat_v = self.lat_v
        lat_w = self.lat_w

        easy_lattice(
            lattice_properties=(
                lat_u,
                lat_v,
                lat_w,
                self.lat_interpolation))
        return {'FINISHED'}

    def invoke(self, context, event):
        # Don't show dialog if we have lattice selected.
        # We'll just apply modifiers and delete it.
        if context.object.type == 'LATTICE':
            return self.execute(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
