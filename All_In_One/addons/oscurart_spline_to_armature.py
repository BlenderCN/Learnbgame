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
    "name": "Spline To Armature",
    "author": "Oscurart",
    "version": (0,1),
    "blender": (2, 6, 3),
    "api": 49000,
    "location": "Add > Armature > Spline To Armature",
    "description": "Make a Armature from a spline.",
    "warning": "",
    "wiki_url": "oscurart.blogspot.com",
    "tracker_url": "",
    "category": "Learnbgame",
}



import bpy

def OscSplineToArmature (context) :

    sp = bpy.context.object
    amt = bpy.data.armatures.new("Armature")
    obj = bpy.data.objects.new("Object", amt)
    bpy.context.scene.objects.link(obj)
    
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    
    for POINT in sp.data.splines[0].points[:]:
        bone = amt.edit_bones.new("bone")
        bone.tail = (POINT.co[0]+sp.location.x, POINT.co[1]+sp.location.y, POINT.co[2]+1+sp.location.z)
        bone.head = (POINT.co[0]+sp.location.x, POINT.co[1]+sp.location.y, POINT.co[2]+sp.location.z)
        
    bpy.ops.object.mode_set(mode="OBJECT")   
    bpy.context.scene.objects.active = sp    
    bpy.ops.object.mode_set(mode="EDIT")


    for BONEINC,POINT in enumerate(sp.data.splines[0].points):
        md = sp.modifiers.new("Hook", "HOOK")
        md.object = obj    
        md.subtarget = amt.bones[BONEINC].name        
        bpy.ops.curve.select_all(action='DESELECT')
        sp.data.splines[0].points[BONEINC].select = 1
        POINT.select = 1
        print(md.name)
        bpy.ops.object.hook_assign(modifier=md.name)
        bpy.ops.object.hook_reset(modifier=md.name)


    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')


class oscClSplineToArmature (bpy.types.Operator):

    bl_idname = "armature.spline_to_armature"
    bl_label = "Spline To Armature"
    bl_description = "Create a Thread"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.active_object.type == "CURVE" )  
    
    def execute(self, context):
        OscSplineToArmature(self)
        return {'FINISHED'}



# Registration

def add_oscsplinetoarmature_list(self, context):
    self.layout.operator(
        "armature.spline_to_armature",
        text="Spline To Armature",
        icon="PLUGIN")

def register():
    bpy.types.INFO_MT_armature_add.append(add_oscsplinetoarmature_list)
    bpy.utils.register_class(oscClSplineToArmature)


def unregister():
    bpy.types.INFO_MT_mesh_add.remove(add_oscsplinetoarmature_list)
    bpy.utils.unregister_class(oscClSplineToArmature)


if __name__ == '__main__':
    register()    