import bpy
import random
import time
from math import pi

# mangle_tools.py (c) 2011 Phil Cote (cotejrp1)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    'name': 'Mangle Tools',
    'author': 'Phil Cote, cotejrp1, (http://www.blenderaddons.com)',
    'version': (0, 1),
    "blender": (2, 6, 0),
    "api": 41098,
    'location': 'VIEW 3D -> TOOLS',
    'description': 'Set of tools to mangle curves, meshes, and shape keys',
    'warning': '',
    "category": "Learnbgame",
}


def move_coordinate(context, co, is_curve=False):
    xyz_const = context.scene.constraint_vector
    random.seed(time.time())
    multiplier = 1

    # For curves, we base the multiplier on the circumference formula.
    # This helps make curve changes more noticable.
    if is_curve:
        multiplier = 2 * pi
    random_mag = context.scene.random_magnitude
    if xyz_const[0]:
        co.x += .01 * random.randrange(-random_mag, random_mag) * multiplier
    if xyz_const[1]:
        co.y += .01 * random.randrange(-random_mag, random_mag) * multiplier
    if xyz_const[2]:
        co.z += .01 * random.randrange(-random_mag, random_mag) * multiplier


class MeshManglerOperator(bpy.types.Operator):
    '''push vertices on the selected object around in random directions to
    create a crumpled look'''
    bl_idname = "ba.mesh_mangler"
    bl_label = "Mangle Mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type == 'MESH'

    def execute(self, context):
        random.seed(time.time())

        mesh = context.active_object.data

        if mesh.shape_keys is not None:
            self.report({"INFO"}, "Cannot mangle mesh: Shape keys present")
            return {'CANCELLED'}

        for vert in mesh.vertices:
            move_coordinate(context, vert.co)

        return {'FINISHED'}


class AnimanglerOperator(bpy.types.Operator):
    '''makes a shape key and pushes the verts around on it
    to set up for random pulsating animation'''
    bl_idname = "ba.ani_mangler"
    bl_label = "Mangle Shape Key"

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type in ['MESH', 'CURVE']

    def execute(self, context):
        scn = context.scene
        mangleName = scn.mangle_name
        ob = context.object
        shapeKey = ob.shape_key_add(name=mangleName)
        verts = shapeKey.data

        for vert in verts:
            move_coordinate(context, vert.co, is_curve=ob.type == 'CURVE')

        return {'FINISHED'}


class CurveManglerOp(bpy.types.Operator):
    '''Mangles a curve to the degree the user specifies'''
    bl_idname = "ba.curve_mangler"
    bl_label = "Mangle Curve"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type == "CURVE"

    def execute(self, context):

        ob = context.active_object
        if ob.data.shape_keys is not None:
            self.report({"INFO"}, "Cannot mangle curve.  Shape keys present")
            return {'CANCELLED'}
        splines = context.object.data.splines

        for spline in splines:
            if spline.type == 'BEZIER':
                points = spline.bezier_points
            elif spline.type in ('POLY', 'NURBS'):
                points = spline.points

            for point in points:
                move_coordinate(context, point.co, is_curve=True)

        return {'FINISHED'}


class MangleToolsPanel(bpy.types.Panel):
    bl_label = "Mangle Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        col = layout.column()
        col.prop(scn, "constraint_vector")
        col.prop(scn, "random_magnitude")

        col.operator("ba.curve_mangler")
        col.operator("ba.mesh_mangler")
        col.separator()
        col.prop(scn, "mangle_name")
        col.operator("ba.ani_mangler")


IntProperty = bpy.props.IntProperty
StringProperty = bpy.props.StringProperty
BoolVectorProperty = bpy.props.BoolVectorProperty


def register():
    bpy.utils.register_class(AnimanglerOperator)
    bpy.utils.register_class(MeshManglerOperator)
    bpy.utils.register_class(CurveManglerOp)
    bpy.utils.register_class(MangleToolsPanel)
    scnType = bpy.types.Scene

    scnType.constraint_vector = BoolVectorProperty(name="Mangle Constraint",
                                                   default=(True, True, True),
                                                   subtype='XYZ',
                                                   description="Constrains Mangle Direction")

    scnType.random_magnitude = IntProperty(name="Mangle Severity",
                                           default=10, min=1, max=30,
                                           description="Severity of mangling")

    scnType.mangle_name = StringProperty(name="Shape Key Name",
                                         default="mangle",
                                         description="Name given for mangled shape keys")


def unregister():
    bpy.utils.unregister_class(AnimanglerOperator)
    bpy.utils.unregister_class(MeshManglerOperator)
    bpy.utils.unregister_class(MangleToolsPanel)
    bpy.utils.unregister_class(CurveManglerOp)


if __name__ == "__main__":
    register()
