# arm_curve.py (c) 2011 Phil Cote (cotejrp1)
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
    'name': 'Armature Curve',
    'author': 'Phil Cote, cotejrp1, (http://www.blenderaddons.com)',
    'version': (0,1),
    "blender": (2, 6, 0),
    "api": 41098,
    'location': '',
    'description': 'Generates a curve character based on an existing armature',
    'warning': '', # used for warning icon and text in addons panel
    'category': 'Add Curve'}

import bpy
from pdb import set_trace

def add_spline(bone_chain, crv):
    
    bone_data = []
    for bone in bone_chain:
        loc = bone.head_local
        bone_data.extend((loc.x, loc.y, loc.z))
        if bpy.context.scene.curve_type == 'POLY':
            bone_data.extend( (0,) )

    loc = bone_chain[-1].tail_local
    bone_data.extend((loc.x, loc.y, loc.z))
    if bpy.context.scene.curve_type == 'POLY':
        bone_data.extend( (0,) )

    # construct the spline itself.
    crv_type = bpy.context.scene.curve_type
    spline = crv.splines.new(type=crv_type)
    num_points = len(bone_chain)
    
    if crv_type == 'BEZIER':
        points = spline.bezier_points
    else:
        points = spline.points
    
    points.add(num_points)
    points.foreach_set("co", bone_data)
    
    for point in points:
        if hasattr( point, "handle_left_type"):
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
            

def get_bone_chain(arm):
    bone_chain = []

    for bone in arm.bones:
        bone_chain.append( bone )
        if len( bone.children ) != 1:
            yield bone_chain
            bone_chain = []
            

def make_arm_curve(arm_ob):
    crv = bpy.data.curves.new("crv", type="CURVE")
    crv_ob = bpy.data.objects.new("crv_ob", crv)
    
    for bone_chain in get_bone_chain(arm_ob.data):
        add_spline(bone_chain, crv)
    
    return crv_ob
    

class CurveArmatureOp(bpy.types.Operator):
    '''Make a curve that binds itself to the selected armature.'''
    bl_idname = "curve.armature_curve"
    bl_label = "Curve Armature"

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if ob == None:
            return False
        if ob.type != 'ARMATURE':
            return False 
        return True


    def execute(self, context):
        scn = bpy.context.scene
        arm_ob = bpy.context.active_object
        crv_ob = make_arm_curve(arm_ob)
        scn.objects.link(crv_ob)
        crv_ob.parent = arm_ob
        crv_ob.parent_type="ARMATURE"
        return {'FINISHED'}


class CurveArmaturePanel(bpy.types.Panel):
    bl_label = "Curve Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    
    def draw(self, context):
        scn = context.scene
        layout = self.layout
        col = layout.column
        col().operator("curve.armature_curve")
        col().prop(scn, "curve_type")


def register():
    scntype = bpy.types.Scene
    enumprop=bpy.props.EnumProperty
    choices=[ ('BEZIER', 'BEZIER', 'BEZIER'), ('POLY', 'POLY', 'POLY'), ]
    
    scntype.curve_type=enumprop("curve type", items=choices)
    bpy.utils.register_class(CurveArmatureOp)
    bpy.utils.register_class(CurveArmaturePanel)


def unregister():
    bpy.utils.unregister_class(CurveArmatureOp)
    bpy.utils.unregister_class(CurveArmaturePanel)


if __name__ == "__main__":
    register()