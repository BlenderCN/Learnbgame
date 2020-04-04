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
    "name": "Add Chain Mail",
    "author": "Andy Davies (metalliandy)",
    "version": (0,2,5),
    "blender": (2, 5, 8),
    "api": 37702,
    "location": "View3D > Add > Mesh > Chain Mail",
    "description": "Adds a Chain Mail mesh with two paths for size control",
    "warning": "",
    "wiki_url": ""\
        "",
    "tracker_url": "",
    "category": "Learnbgame",
}
      
"""
About this script:-
This script enables the creation of a Chain Mail mesh with two paths that directly control the overall size of the mail across two axis.

Usage:-
Activate the script via the "Add-Ons" tab under the user preferences.
The Chain Mail can then be accessed via Add Mesh> Chain Mail

Related Links:-
http://blenderartists.org/forum/showthread.php?t=205582
http://www.metalliandy.com

Thanks to:-
Dealga McArdle (zeffii) - http://www.digitalaphasia.com

Version history:-
v0.2.5 - Ammended script for compatibility with recent API changes.
v0.2.4 - Ammended script and changed bl_info for compatibility with recent API changes.
v0.2.3 - Ammended script for compatibility with recent API changes.
v0.2.2 - Ammended script meta information for compatibility with recent API changes.
v0.2.1 - Fixed a bug where the script caused an error if run on any layer other than 0.
v0.2 - Code refactor and tweaks to the final resulting mesh.
v0.1 - Initial revision.

"""

import bpy

def Add_ChainMail():

    ##   some helper functions.
    def AddArrayModifierTo(torus_instance):
        #sets it up and applies it
        bpy.ops.object.modifier_add(type='ARRAY')
        array = torus_instance.modifiers['Array']    #magic happened here.
        array.fit_type = ('FIXED_COUNT')
        array.use_relative_offset = False
        array.use_constant_offset = True
        array.constant_offset_displace = (0.0, 2.22, 0.0)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Array")
        
    # setup a torus and add: takes name and rotation value, returns an instance
    def CreateTorus(name, this_rotation):
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25, major_segments=8, minor_segments=4, abso_major_rad=1, abso_minor_rad=0.5, location=(0, 0, 0), rotation=(0, -0, 0))
        temp_torus = bpy.context.object
        temp_torus.name = "Chain Mail"
        bpy.ops.transform.resize(value=(0.45, 0.45, 0.45), constraint_orientation='GLOBAL')
        bpy.ops.transform.rotate(value=(this_rotation,), axis=(-0, 1, -3.42285e-8), constraint_orientation='GLOBAL', mirror=False)
        return temp_torus

    # you can also write 
    # AddArrayModifierTo(CreateTorus("Chain Mail",-0.349066,))
    # once that makes sense, you should do so.
    
    torus1 = CreateTorus("Chain Mail", -0.349066)
    AddArrayModifierTo(torus1)
    torus2 = CreateTorus("Chain Mail_2", 0.349066)
    AddArrayModifierTo(torus2)

    #Translates object .5 in X and Y
    bpy.ops.transform.translate(value=(0, 0.5, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')
    bpy.ops.transform.translate(value=(0.5, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')

    #Selects all objects, and joins, gives name and sets to smooth
    bpy.ops.object.select_all(action='TOGGLE')
    bpy.ops.object.select_all(action='TOGGLE')
    bpy.ops.object.join()
    torus2.name = "Chain Mail"
    bpy.ops.object.shade_smooth()


    #Sets origin to 3d Cursor
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    #Applys location, rotation and scale data
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    #Adds  Path to scene, set name and add variable path
    bpy.ops.curve.primitive_nurbs_path_add( view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0),)
    pathacross = bpy.context.object
    pathacross.name = "Deformation Path Across" 

    #Change to Editmode
    bpy.ops.object.editmode_toggle()

    #Translate Deformation Pathacross
    bpy.ops.transform.translate(value=(2, 0, 0), constraint_axis=(True, False, False), 
    constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', 
    proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, 
    snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), 
    release_confirm=False)

    #Change to Objectmode
    bpy.ops.object.editmode_toggle()

    #Adds  Path to scene
    bpy.ops.curve.primitive_nurbs_path_add( view_align=False, enter_editmode=False, location=(0, 2, 0), rotation=(0, 0, 0),)
    pathup = bpy.context.object
    pathup.name = "Deformation Path UP" 

    #Change to Editmode
    bpy.ops.object.editmode_toggle()

    #Translate Deformation Pathup
    bpy.ops.transform.rotate(value=(-1.5708,), axis=(-0, -0, -1), constraint_axis=(False, False, False))

    #Change to Objectmode
    bpy.ops.object.editmode_toggle()

    #Select Chain Mail
    sce = bpy.context.scene
    sce.objects.active = torus2
    
    #this is your modifier stack.
    #Adds Array Modifier to Chain Mail, and sets it up 
    bpy.ops.object.modifier_add(type='ARRAY')
    array = torus2.modifiers['Array']
    array.use_relative_offset = False
    array.use_constant_offset = True
    array.fit_type = ('FIT_CURVE')
    array.curve = pathacross
    array.use_object_offset = True
    array.constant_offset_displace = (1.0, 0.0, 0.0)

    #Adds Array Modifier to Chain Mail, and sets it up
    bpy.ops.object.modifier_add(type='ARRAY')
    array = torus2.modifiers['Array.001']
    array.use_relative_offset = False
    array.use_constant_offset = True
    array.fit_type = ('FIT_CURVE')
    array.curve = pathup
    array.use_object_offset = True
    array.constant_offset_displace = (0.0, 2.0, 0.0)

    #Adds Subsurf Modifier
    bpy.ops.object.modifier_add(type='SUBSURF')

    #Selects Subsurf Modifier for editing
    subsurf = torus2.modifiers['Subsurf']

    #Changes Subsurf levels
    subsurf.levels = 1 
    subsurf.show_only_control_edges = True
    subsurf.use_subsurf_uv = False

#makes ChainMail an operator
class AddChainMail(bpy.types.Operator):
    bl_idname = "mesh.chainmail_add"
    bl_label = "Add Chain Mail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Add_ChainMail()
        return {'FINISHED'}


# Register the operator
def menu_func(self, context):
    self.layout.operator(AddChainMail.bl_idname, text="Chain Mail", icon='PLUGIN')

#register and unregister add and remove menu items from mesh menu
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()

