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
    "name": "Icon Tools",
    "author": "koil > subauthor Marvin",
    "version": (1, 5, 0),
    "blender": (2, 68, 1),
    "location": "Editors > View 3D > Properties (N) or Tools (T)> Tools.",
    "description": "Icon Tools. set switch = 'TOOLS' to replace Tool Shelf.",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/Icon_Tools",
    "tracker_url": "https://projects.blender.org/tracker/index.php?func=detail&aid=34584",
    "category": "3D View"
}


""" ---------------------------------------------------------------- """
""" header """

import bpy
from bpy.types import Header, Menu, Panel, Operator
from math import sin, cos
import bmesh
from bpy_extras import object_utils
from bpy.props import PointerProperty, EnumProperty, FloatProperty, BoolProperty
from mathutils import Vector
from mathutils.geometry import intersect_point_line, intersect_line_plane



global switch
switch = 'UI'

bpy.types.Scene.b_label = bpy.props.BoolProperty(default=0)	# labels			d
bpy.types.Scene.b_add_set = bpy.props.BoolProperty(default=0)	# add_set			d
bpy.types.Scene.tool = bpy.props.StringProperty(default='UI')	# tool				d
bpy.types.Scene.sst = bpy.props.FloatProperty(default=0.25)	# spin screw turns		d
bpy.types.Scene.sss = bpy.props.FloatProperty(default=9.0)	# spin screw steps		d
bpy.types.Scene.sm = bpy.props.BoolProperty(default=1)		# sm # descope			d #XX00#
bpy.types.Scene.se = bpy.props.BoolProperty(default=1)		# se # descope			d #XX00#

global descope
descope = 1

""" ---------------------------------------------------------------- """




class OT_mod_add_with_targets(Operator):
    bl_idname = "object.mod_add_with_targets"
    bl_label = "mod_add_with_targets"
    mb_type = bpy.props.StringProperty(default='BOOLEAN')

    """ ------------------------------------------------ """
    """ mod_bool_add_with_targets """
    
    def execute(self, context):

        """ ------------------------------------------------ """
        """ count active_object.modifiers """
    
        mm_count=0
        for i in bpy.context.active_object.modifiers:
            mm_count+=1

        """ ------------------------------------------------ """

        """ ------------------------------------------------ """
        """ if select_object!=active_object                  """
        """     add mod to active_object                     """
        """     add select_object                            """

        xxx=bpy.context.active_object

        for obs in bpy.context.selected_objects:
        
            if self.mb_type=='SUBSURF':
                bpy.context.scene.objects.active=obs
                bpy.ops.object.modifier_add(type=self.mb_type)
                mm_count+=1
                

            if self.mb_type=='ARMATURE':
                if obs.name!=bpy.context.active_object.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=obs             # targets armatures
                    mm_count+=1

            if self.mb_type=='BOOLEAN':
                if obs.name!=bpy.context.active_object.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=obs             # target objects
                    bpy.context.active_object.modifiers[mm_name].operation="INTERSECT"
                    mm_count+=1

            if self.mb_type=='MESH_DEFORM':
                if obs.name!=bpy.context.active_object.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=obs             # target objects
                    mm_count+=1

        bpy.context.scene.objects.active=xxx

        """ ------------------------------------------------ """

        return{'FINISHED'}

    """ ------------------------------------------------ """

bpy.utils.register_class(OT_mod_add_with_targets)

""" ---------------------------------------------------------------- """


""" ---------------------------------------------------------------- """
""" object.moda_add_with_targets(mb_type='BOOLEAN') """

class OT_moda_add_with_targets(Operator):
    bl_idname = "object.moda_add_with_targets"
    bl_label = "moda_add_with_targets"
    mb_type = bpy.props.StringProperty(default='BOOLEAN')

    """ ------------------------------------------------ """
    """ mod_bool_add_with_targets """
    
    def execute(self, context):

        """ ------------------------------------------------ """

        if self.mb_type=='ARMATURE':

            xxx=bpy.context.active_object

            for obs in bpy.context.selected_objects:

                bpy.context.scene.objects.active=obs

                mm_count=0
                for i in bpy.context.active_object.modifiers:
                    mm_count+=1

                if obs.name!=xxx.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=xxx
                    mm_count+=1

            bpy.context.scene.objects.active=xxx

        """ ------------------------------------------------ """

        return{'FINISHED'}

    """ ------------------------------------------------ """

bpy.utils.register_class(OT_moda_add_with_targets)

""" ---------------------------------------------------------------- """


""" ---------------------------------------------------------------- """
""" object.mod_add_with_targets(mb_type='BOOLEAN') """

class OT_mod_add_with_targets(Operator):
    bl_idname = "object.mod_add_with_targets"
    bl_label = "mod_add_with_targets"
    mb_type = bpy.props.StringProperty(default='BOOLEAN')

    """ ------------------------------------------------ """
    """ mod_bool_add_with_targets """
    
    def execute(self, context):

        """ ------------------------------------------------ """
        """ count active_object.modifiers """
    
        mm_count=0
        for i in bpy.context.active_object.modifiers:
            mm_count+=1

        """ ------------------------------------------------ """

        """ ------------------------------------------------ """
        """ if select_object!=active_object                  """
        """     add mod to active_object                     """
        """     add select_object                            """

        xxx=bpy.context.active_object

        for obs in bpy.context.selected_objects:
        
            if self.mb_type=='SUBSURF':
                bpy.context.scene.objects.active=obs
                bpy.ops.object.modifier_add(type=self.mb_type)
                mm_count+=1
                

            if self.mb_type=='ARMATURE':
                if obs.name!=bpy.context.active_object.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=obs             # targets armatures
                    mm_count+=1

            if self.mb_type=='BOOLEAN':
                if obs.name!=bpy.context.active_object.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=obs             # target objects
                    bpy.context.active_object.modifiers[mm_name].operation="INTERSECT"
                    mm_count+=1

            if self.mb_type=='MESH_DEFORM':
                if obs.name!=bpy.context.active_object.name:
                    bpy.ops.object.modifier_add(type=self.mb_type)
                    mm_name=bpy.context.active_object.modifiers[mm_count].name
                    bpy.context.active_object.modifiers[mm_name].object=obs             # target objects
                    mm_count+=1

        bpy.context.scene.objects.active=xxx

        """ ------------------------------------------------ """

        return{'FINISHED'}

    """ ------------------------------------------------ """

bpy.utils.register_class(OT_mod_add_with_targets)

""" ---------------------------------------------------------------- """


""" ------------------------------------------------ """
""" draw_main """

def draw_add_set(context, layout):
        
        if descope:

            col = layout.column(align=True)

            # button group_1

        col = layout.column(align=True)
        col.label(text="Navigation to:")
        
                
        row = col.row(align=True)
        row.operator("view3d.viewnumpad", text="Front").type='FRONT'
        row.operator("view3d.viewnumpad", text="Back").type='BACK'
        row = col.row(align=True)
        row.operator("view3d.viewnumpad", text="Left").type='LEFT'
        row.operator("view3d.viewnumpad", text="Right").type='RIGHT'
        row = col.row(align=True)
        row.operator("view3d.viewnumpad", text="Top").type='TOP'
        row.operator("view3d.viewnumpad", text="Bottom").type='BOTTOM'
        
       
        row = col.row(align=True)
        row.operator("view3d.view_all", text="All").center=True 
        row.operator("view3d.viewnumpad", text="Camera", icon='CAMERA_DATA').type='CAMERA'
        
        row = col.row(align=True)
        row.operator("view3d.localview", text="Global/Local")
        row.operator("view3d.view_persportho", text="Persp/Ortho") 
        
        
        
        col = layout.column(align=True)
        col.label(text="Zoom to:")
        
        row = col.row(align=True)
        row.operator("view3d.view_selected", text="Selected") 
        row.operator("view3d.zoom_border", text="Border")
       
        


# button group_2---Transform / Snap / Add---------------

        col = layout.column(align=True)
        col.label(text="Transform / Snap / Add:")
        
        row = col.row(align=True)
        row.operator("view3d.snap_cursor_to_center",text="Center")
        row.operator("view3d.snap_cursor_to_active",icon='FORCE_BOID',text="")          
        row.operator("view3d.snap_cursor_to_selected",icon='FORCE_FORCE',text="")
        row.operator("view3d.snap_selected_to_cursor",icon='FORCE_LENNARDJONES',text="")
        row.operator("view3d.snap_cursor_to_grid",icon='HELP',text="")
        row.operator("view3d.snap_selected_to_grid",icon='BBOX',text="")
        
        row = col.row(align=True)
        row.operator("object.origin_set", text="Origin")
        row.operator("mesh.primitive_plane_add",icon='MESH_PLANE',text="")
        row.operator("mesh.primitive_cube_add",icon='MESH_CUBE',text="")
        row.operator("mesh.primitive_circle_add",icon='MESH_CIRCLE',text="")
        row.operator("mesh.primitive_uv_sphere_add",icon='MESH_UVSPHERE',text="")
        row.operator("mesh.primitive_ico_sphere_add",icon='MESH_ICOSPHERE',text="")
        
        row = col.row(align=True)
        row.operator("transform.translate",text="Move")
        row.operator("mesh.primitive_grid_add",icon='MESH_GRID',text="")
        row.operator("mesh.primitive_monkey_add",icon='MESH_MONKEY',text="")
        row.operator("mesh.primitive_cylinder_add",icon='MESH_CYLINDER',text="")
        row.operator("mesh.primitive_torus_add",icon='MESH_TORUS',text="")
        row.operator("mesh.primitive_cone_add",icon='MESH_CONE',text="")
        
        row = col.row(align=True)
        row.operator("transform.rotate")
        row.operator("curve.primitive_bezier_curve_add",icon='CURVE_BEZCURVE',text="")
        row.operator("curve.primitive_bezier_circle_add",icon='CURVE_BEZCIRCLE',text="")
        row.operator("curve.primitive_nurbs_curve_add",icon='CURVE_NCURVE',text="")
        row.operator("curve.primitive_nurbs_circle_add",icon='CURVE_NCIRCLE',text="")
        row.operator("curve.primitive_nurbs_path_add",icon='CURVE_PATH',text="")
           
        row = col.row(align=True)
        row.operator("transform.resize", text="Scale")
        row.operator("surface.primitive_nurbs_surface_circle_add",icon='SURFACE_NCIRCLE',text="")
        row.operator("surface.primitive_nurbs_surface_surface_add",icon='SURFACE_NSURFACE',text="")
        row.operator("surface.primitive_nurbs_surface_cylinder_add",icon='SURFACE_NCYLINDER',text="")
        row.operator("surface.primitive_nurbs_surface_sphere_add",icon='SURFACE_NSPHERE',text="")
        row.operator("surface.primitive_nurbs_surface_torus_add",icon='SURFACE_NTORUS',text="")  
            
        row = col.row(align=True)
        row.operator("object.transform_apply", text="Apply")
        row.operator("object.armature_add",text="",icon="BONE_DATA")
        row.operator("object.add",text="",icon="OUTLINER_OB_LATTICE").type="LATTICE"
        row.operator("object.empty_add",icon='OUTLINER_OB_EMPTY',text="")
        row.operator("object.camera_add",icon='OUTLINER_OB_CAMERA',text="")
        row.operator("object.lamp_add",icon='OUTLINER_OB_LAMP',text="")
        
        
        row = col.row(align=True)
        row.operator("object.duplicate_move", text="Copy")
        row.operator("mesh.duplicate_move", text="Copy")
        row.operator("view3d.ruler", text="Ruler")
        
        
        
        
        col = layout.column(align=True)
        col.label(text="Select with / by:")
        
        row = col.row(align=True)
        row.operator("view3d.select_border", text="Box")
        row.operator("view3d.select_circle", text="Circle")
        row.operator("object.select_by_type", text="Type")
        #row.operator("object.select_all", text="All")
        #row.operator("mesh.select_all", text="All")
        
        col = layout.column(align=True)

        
        
        
        

""" ------------------------------------------------ """


""" ------------------------------------------------ """
""" draw_extra """
 

def draw_extra(context, layout):

    """ -------------------------------- """
    """ active_object """
   

    if context.active_object:

        # global column
        # this is the gap before modifiers
        # when no modifier, makes a bigger gap
        
        col = layout.column(align=True)
        
        

        active_object = context.active_object

        """ -------------------------------- """
        """ OBJECT """

        if context.mode=="OBJECT":

            xx=0
            for i in context.selected_objects:
                xx+=1

            if context.active_object.type=='MESH':

                if xx==1:
                    
                    col.label(text="Modifier:") 
                    
                    
                    row = col.row(align=True)
                    row.operator("object.modifier_add",icon='MOD_ARRAY',text=" Array").type="ARRAY"
                    row.operator("object.modifier_add",icon='MOD_SUBSURF',text=" Subsurf").type="SUBSURF"      
                    
                    row = col.row(align=True)
                    row.operator("object.modifier_add",icon='MOD_BOOLEAN',text=" Boolean").type="BOOLEAN"
                    row.operator("object.modifier_add",icon='MOD_LATTICE',text=" Lattice").type="LATTICE"
                    
                    row = col.row(align=True)
                    row.operator("object.modifier_add",icon='MOD_SIMPLEDEFORM',text=" Simple D").type="SIMPLE_DEFORM" 
                    row.operator("object.modifier_add",icon='MOD_MESHDEFORM',text=" Mesh D").type="MESH_DEFORM"
                    
                    row = col.row(align=True)
                    row.operator("object.modifier_add",icon='MOD_SOLIDIFY',text=" Solidify").type="SOLIDIFY"
                    row.operator("object.modifier_add",icon='MOD_ARMATURE',text=" Armature").type="ARMATURE"
                    
                
                elif xx>1:
                    
                    
                    row = col.row(align=True)
                    row.operator("object.mod_add_with_targets",icon='MOD_ARRAY',text=" Array").mb_type="ARRAY"
                    row.operator("object.mod_add_with_targets",icon='MOD_SUBSURF',text=" Subsurf").mb_type="SUBSURF"
                                                          
                    row = col.row(align=True)
                    row.operator("object.mod_add_with_targets",icon='MOD_BOOLEAN',text=" Boolean").mb_type="BOOLEAN"
                    row.operator("object.mod_add_with_targets",icon='MOD_LATTICE',text=" Lattice").mb_type="LATTICE"
                    
                    row = col.row(align=True)
                    row.operator("object.mod_add_with_targets",icon='MOD_SIMPLEDEFORM',text=" Simple D").mb_type="SIMPLE_DEFORM"
                    row.operator("object.mod_add_with_targets",icon='MOD_MESHDEFORM',text=" Mesh D").mb_type="MESH_DEFORM"
                    
                    row = col.row(align=True)
                    row.operator("object.mod_add_with_targets",icon='MOD_SOLIDIFY',text=" Solidify").mb_type="SOLIDFIY"
                    row.operator("object.mod_add_with_targets",icon='MOD_ARMATURE',text=" Armature").mb_type="ARMATURE"
                    

            if context.active_object.type=='ARMATURE':

                if xx>1:
                    row = col.row(align=True)
                    row.operator("object.moda_add_with_targets",icon='MOD_ARMATURE',text=" Armature").mb_type="ARMATURE"

        """ -------------------------------- """
        """ OBJECT POSE """

        if context.mode=="OBJECT" or context.mode=="POSE":
            
            """ Keyframes """
            if context.active_object and context.active_object.type in {'MESH', 'CURVE', 'SURFACE', 'ARMATURE'}:

                col = layout.column(align=True)
                row = col.row(align=True)
                row.label(text="Keyframes (I)  Delete (Alt+I)")
                row = col.row(align=True)
                row.operator("anim.keyframe_insert_menu", icon='ZOOMIN', text="")
                row.operator("anim.keyframe_delete_v3d", icon='ZOOMOUT', text="")
                row.prop_search(context.scene.keying_sets_all, "active", context.scene, "keying_sets_all", text="")
                row.operator("anim.keyframe_insert", text="", icon='KEY_HLT')
                row.operator("anim.keyframe_delete", text="", icon='KEY_DEHLT')

        """ -------------------------------- """

    view = context.space_data

    col = layout.column(align=True)
    split = layout.split()
        
    
    row = col.row(align=True)  
    row.operator("ed.undo", text="Undo")
    row.operator("ed.redo", text="Redo")
    row.operator("ed.undo_history", text="History")

    
    
    
    
    """ Grease """
    col = split.column(align=True)
    row = col.row(align=True)
    row.prop(context.tool_settings, "use_grease_pencil_sessions",text="")
    row.label(text="Session")
    row = col.row(align=True)
    row.operator("gpencil.draw", text="",icon="GREASEPENCIL").mode = 'DRAW'
    row.operator("gpencil.draw", text="",icon="OUTLINER_OB_CURVE").mode = 'DRAW_STRAIGHT'
    row.operator("gpencil.draw", text="",icon="OUTLINER_OB_MESH").mode = 'DRAW_POLY'
    row.operator("gpencil.draw", text="",icon="PANEL_CLOSE").mode = 'ERASER'
        
    """ Misc """
    row = col.row(align=True)
    row.prop(view, "use_occlude_geometry", text="")
    row.prop(view, "show_textured_solid",text="",icon="TEXTURE")
    row.prop(view, "show_background_images", text="",icon="IMAGE_DATA")
    if context.active_object:
        row.prop(context.active_object, "show_x_ray", text="",icon="RADIO")
    else:
        row.operator("object.lamp_add", text="",icon="OUTLINER_OB_LAMP")
        
    """ Misc """
    row = col.row(align=True)
    row.prop(context.scene.tool_settings, "use_uv_select_sync", text="")
    row.prop(view, "show_manipulator",text="")
    row.operator("mesh.primitive_cube_add",text="",icon="MESH_CUBE")
    row.operator("object.armature_add",text="",icon="BONE_DATA")
        
    """ Motion """
    col = split.column(align=True)
    row = col.row(align=True)
    #row.prop(context.scene, "hide",text="")
    row.label(text=" ")
    row = col.row(align=True)
    row.operator("object.paths_calculate", text="",icon="ANIM_DATA")
    row.operator("object.paths_clear", text="",icon="PANEL_CLOSE")
    row.operator("screen.repeat_last",text="",icon="RECOVER_LAST")
    row.operator("screen.repeat_history", text="",icon="TIME")
        
    row = col.row(align=True)
    row.operator("render.render", text="", icon='RENDER_STILL')
    row.operator("render.render", text="", icon='RENDER_ANIMATION').animation = True
    row.operator("render.opengl", text="", icon='RENDER_STILL')
    row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True

    row = col.row(align=True)
    row.operator("wm.save_mainfile",text="",icon="FILE_TICK")
    row.operator("wm.save_as_mainfile",text="",icon="SAVE_AS")
    row.operator("wm.console_toggle",text="",icon="CONSOLE")
    row.operator("render.play_rendered_anim", text="", icon='PLAY')

""" ------------------------------------------------ """


""" ------------------------------------------------ """
""" Object Mode """

class VIEW3D_PT_tools_objectmode(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = switch
    #bl_region_type = context.scene.tool	# check if exist, set
    bl_context = "objectmode"
    bl_label = "Object Tools"
    #bl_options = {'HIDE_HEADER'}		# check if top default

    @classmethod
    def poll(cls, context):
        return ((context.mode == 'OBJECT'))

    def draw(self, context):
        
        layout = self.layout

        if context.active_object:
            if context.scene.b_add_set:
                draw_add_set(context, layout)
        else:
            draw_add_set(context, layout)

        """ -------------------------------- """
        """ Object """

        col = layout.column(align=True)		# global column, keep aligned

        if context.active_object and context.active_object.type in {'MESH', 'CURVE', 'SURFACE', "ARMATURE", "EMPTY", "LATTICE","LAMP","CAMERA", "SPEAKER"}:
            
            
        
            
            row = col.row(align=True)
            row.operator("object.move_to_layer", text="Move to Layer")
            
                                
        col = layout.column(align=True)
        col.label(text="Group:")
            
        row = col.row(align=True)
        row.operator("group.create", text="Group")
        row.operator("group.objects_add_active", text="-> to Active")
            
        row = col.row(align=True)
        row.operator("group.objects_remove", text="Remove")
        row.operator("group.objects_remove_active", text="-> from Active")
        
        
        
        col = layout.column(align=True)
        col.label(text="Hidden:")
                   
        row = col.row(align=True)
        row.operator("object.hide_view_set", text="Select").unselected=False
        row.operator("object.hide_view_set", text="UnSelect").unselected=True
        row.operator("object.hide_view_clear", text="Show All")
                 
       
       
        if context.active_object:
        
            
            col = layout.column(align=True)
            col.label(text="Links:")
          
            
            row = col.row(align=True)
            row.operator("object.join",text="Join")
            row.operator("object.constraint_add_with_targets",text="Constraint")
            
            row = col.row(align=True)
            row.operator("object.track_set",text="Track")
            row.operator("object.parent_set",text="Parent")
            
            
            
            
        
         
            
            

        """ -------------------------------- """

        draw_extra(context, layout)

""" ------------------------------------------------ """


""" ------------------------------------------------ """
""" Edit Mode Mesh """

class VIEW3D_PT_tools_meshedit(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = switch
    bl_context = "mesh_edit"
    bl_label = "Mesh Tools"

    @classmethod
    def poll(cls, context):
        return ((context.mode == 'EDIT_MESH'))

    def draw(self, context):
        
        layout = self.layout

        if context.active_object:
            if context.scene.b_add_set:
                draw_add_set(context, layout)

        """ -------------------------------- """
        """ Mesh """

       #---------------------Selection----------------------
        
               
        col = layout.column(align=True)
        col.label(text="Selection:")
        
        row = col.row(align=True)
        row.operator("mesh.loop_multi_select",text="Loop").ring=False
        row.operator("mesh.loop_multi_select",text="Ring").ring=True
        row.operator("mesh.select_all",text="All")
        
        
        row = col.row(align=True)
        row.operator("mesh.e2e_evnfe", text="Loop+")
        row.operator("mesh.e2e_efnve", text="Ring+")
        row.operator("mesh.select_linked",text="Linked")
        
        
           
             
       
       
       
       #-------------Subdivde-----------------------        
        

        col = layout.column(align=True)
        col.label(text="Subdivide:")
        
        
        row = col.row(align=True)
        row.operator("mesh.subdivide")
        row.operator("mesh.unsubdivide")
        
        row = col.row(align=True)
        row.operator("mesh.quads_convert_to_tris",text="Quad to Tri")
        row.operator("mesh.tris_convert_to_quads",text="Tri to Quad")
        
#---------------------Cutting----------------------
        
               
        col = layout.column(align=True)
        col.label(text="Loop / Cut / Vertex Connect:")        
        
        
        row = col.row(align=True)
        row.operator("object_ot.fastloop",text="Fast")
        row.operator("mesh.loopcut_slide",text="Loop")
        row.operator("mesh.vert_connect",text="Connect")
        
        
        row = col.row(align=True)
        props = row.operator("mesh.knife_tool", text="Knife")
        props.use_occlude_geometry = True
        
        props.only_selected = False
        props = row.operator("mesh.knife_tool", text="-> Select")
        
        props.use_occlude_geometry = False
        props.only_selected = True
        row.operator("mesh.knife_project", text="-> Project") 
        
        row = col.row(align=True)
        row.operator("mesh.bisect",text="Bisect Plane")
        row.operator("mesh.vert_connect_nonplanar",text="Nonplanar")
        
        
        

        
        
#-------------Split-----------------------        
        
        
        col = layout.column(align=True)
        col.label(text="Separate:")
        
        row = col.row(align=True)
        row.operator("mesh.split")
        row.operator("mesh.wireframe", text="Wire")
        row.operator("mesh.separate")  
        
#-------------Remove-----------------------          
        
        col = layout.column(align=True)
        col.label(text="Remove:")
        
        row = col.row(align=True)  
        row.menu("VIEW3D_MT_edit_mesh_delete")
        row.operator("mesh.remove_doubles", text="Doubles")
        

        """ -------------------------------- """

        draw_extra(context, layout)

""" ------------------------------------------------ """


""" ------------------------------------------------ """
""" Edit Mode Armature """

class VIEW3D_PT_tools_armatureedit(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = switch
    bl_context = "armature_edit"
    bl_label = "Armature Tools"

    @classmethod
    def poll(cls, context):
        return ((context.mode == 'EDIT_ARMATURE'))

    def draw(self, context):

        layout = self.layout

        if context.active_object:
            if context.scene.b_add_set:
                draw_add_set(context, layout)

        """ -------------------------------- """
        """ Armature """

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("armature.bone_primitive_add", text="Add")
        row = col.row(align=True)
        row.operator("armature.merge")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("armature.subdivide",text="Subdivide").number_cuts=1
        row.operator("armature.subdivide",text="Subdivide 2").number_cuts=2
        row = col.row(align=True)
        row.operator("armature.select_hierarchy",text="Select Parent").direction="PARENT"
        row.operator("armature.select_hierarchy",text="Select Child").direction="CHILD"
        row = col.row(align=True)
        row.operator("armature.fill",text="Fill Between")
        row.operator("armature.switch_direction")
        row = col.row(align=True)
        row.operator("armature.parent_set")
        row.operator("armature.parent_clear")
        #row = col.row(align=True)
        #row.operator("armature.calculate_roll")
        #row.operator("armature.switch_direction")

        """ -------------------------------- """

        draw_extra(context, layout)

""" ------------------------------------------------ """


""" ------------------------------------------------ """
""" Pose Mode Armature """

class VIEW3D_PT_tools_posemode(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = switch
    bl_context = "posemode"
    bl_label = "Pose Tools"

    @classmethod
    def poll(cls, context):
        return ((context.mode == 'POSE'))

    def draw(self, context):
        
        layout = self.layout

        if context.active_object:
            if context.scene.b_add_set:
                draw_add_set(context, layout)

        """ -------------------------------- """
        """ Pose """

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("poselib.pose_add", text="Add To Library")

        row = col.row(align=True)
        row.operator("pose.copy")
        row.operator("pose.paste")
        row = col.row(align=True)
        row.operator("pose.loc_clear",text="Clear Loc")
        row.operator("pose.rot_clear",text="Clear Rot")
        row = col.row(align=True)
        row.operator("pose.scale_clear",text="Clear Scale")
        row.operator("pose.transforms_clear",text="Clear All")

        """ -------------------------------- """
        
        draw_extra(context, layout)
        
""" ------------------------------------------------ """


""" ---------------------------------------------------------------- """
""" OBJECT_OT_primitive_custom_add """

class OBJECT_OT_primitive_custom_tri_add(Operator):
    bl_idname = "mesh.primitive_custom_tri_add"
    bl_label = "Add Triangle"

    def execute(self, context):

        A = 6.283185307179586476925286766559 / 3

        verts = [(sin(A*1), 0.0, cos(A*1)),
                 (sin(A*2), 0.0, cos(A*2)),
                 (sin(A*3), 0.0, cos(A*3)),
                 ]

        faces = [(0, 1, 2)]

        mesh = bpy.data.meshes.new("Cube")

        bm = bmesh.new()

        for v_co in verts:
            bm.verts.new(v_co)

        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])

        bm.to_mesh(mesh)
        mesh.update()

        object_utils.object_data_add(context, mesh)

        return{'FINISHED'}

bpy.utils.register_class(OBJECT_OT_primitive_custom_tri_add)

""" ---------------------------------------------------------------- """


""" ------------------------------------------------ """
""" Add """

bpy.types.Scene.add_p_c_vertices = bpy.props.IntProperty(default=32,soft_min=3, soft_max=250)
bpy.types.Scene.add_p_c_radius = bpy.props.FloatProperty(default=1,soft_min=-50.0, soft_max=50.0)

bpy.types.Scene.add_p_uvs_segments = bpy.props.IntProperty(default=32,soft_min=3, soft_max=250)
bpy.types.Scene.add_p_uvs_rings = bpy.props.IntProperty(default=16,soft_min=3, soft_max=250)

class VIEW3D_PT_Add(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = ''
    bl_label = "Add Objects"

    def draw(self, context):
        
        layout = self.layout

        # Circle
        col = layout.column(align=True)
        row = col.row(align=True)
        p=row.operator("mesh.primitive_circle_add")
        row = col.row(align=True)
        row.prop(context.scene,"add_p_c_vertices",text="vertices")
        row = col.row(align=True)
        p.vertices=context.scene.add_p_c_vertices
        
        # UV Sphere
        col = layout.column(align=True)
        row = col.row(align=True)
        p=row.operator("mesh.primitive_uv_sphere_add")
        row = col.row(align=True)
        row.prop(context.scene,"add_p_uvs_segments",text="segments")
        row = col.row(align=True)
        row.prop(context.scene,"add_p_uvs_rings",text="rings")
        row = col.row(align=True)
        p.segments=context.scene.add_p_uvs_segments
        p.ring_count=context.scene.add_p_uvs_rings
        
        # Triangle
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.primitive_custom_tri_add")



        """

        # ---------------------------------------------------------------- #
        # rule: make col + row when you want to draw

        check = 0

        # ---------------------------------------------------------------- #

        # ---------------------------------------------------------------- #

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label("--------------------------------")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.primitive_custom_add",text="test")

        if check==1:
            row = col.row(align=True)
            row.operator("mesh.primitive_custom_add",text="test")

        row = col.row(align=True)
        row.operator("mesh.primitive_custom_add",text="test")

        # ---------------------------------------------------------------- #

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label("--------------------------------")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.primitive_custom_add",text="test")

        if check==1:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("mesh.primitive_custom_add",text="test")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.primitive_custom_add",text="test")
        

        # ---------------------------------------------------------------- #

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label("--------------------------------")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.primitive_custom_add",text="test")

        if check==1:
            row.operator("mesh.primitive_custom_add",text="test")

        row.operator("mesh.primitive_custom_add",text="test")

        # ---------------------------------------------------------------- #


        """

""" ------------------------------------------------ """


""" ---------------------------------------------------------------- """
""" UI_OT_dere_add """

class UI_OT_dere_add(Operator):
    bl_idname = "ui.dere_add"
    bl_label = "De Register Add"

    def execute(self, context):

        bpy.utils.unregister_class(VIEW3D_PT_Add)

        return{'FINISHED'}


bpy.utils.register_class(UI_OT_dere_add)

""" ---------------------------------------------------------------- """


""" ---------------------------------------------------------------- """
""" UI_OT_regi_add """

class UI_OT_regi_add(Operator):
    bl_idname = "ui.regi_add"
    bl_label = "Register Add"

    def execute(self, context):

        bpy.utils.register_class(VIEW3D_PT_Add)

        return{'FINISHED'}


bpy.utils.register_class(UI_OT_regi_add)

""" ---------------------------------------------------------------- """


""" ---------------------------------------------------------------- """
""" Icon Tools """

class SCENE_PT_Icon_Tools(Panel):
    bl_label = "Icon Tools"
    bl_idname = "SCENE_PT_Icon_Tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    #bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        """ column split """
        split = layout.split()
        

        """ column one """
        col = split.column(align=False)
        row = col.row(align=False)
        row.prop(context.scene, "b_label",text="Labels",toggle=True)

        row = col.row(align=False)
        row.prop(context.scene, "b_add_set",text="Add Set",toggle=True)

        row = col.row(align=False)
        row.operator("ui.regi_add")

        row = col.row(align=False)
        row.operator("ui.dere_add")


        """ column two """

        """
        col = split.column(align=False)
        col.context_pointer_set("bpy.data.screens['Scripting']", context.space_data)
        row = col.row(align=False)
        row.context_pointer_set("bpy.data.screens['Scripting']", context.space_data)

        col = split.column(align=False)
        col.context_pointer_set("Scripting", context.space_data)
        row = col.row(align=False)
        row.context_pointer_set("Scripting", context.space_data)

        col = split.column(align=False)
        col.context_pointer_set("SpaceTextEditor", context.space_data)
        row = col.row(align=False)
        row.context_pointer_set("SpaceTextEditor", context.space_data)

        p=row.operator("text.reload")
        row = col.row(align=False)
        row.operator("text.run_script")
        """

        """ -------------------------------- """
        """ Labels """

        if context.scene.b_label==1:

            if context.mode=='OBJECT':

                col = layout.column(align=True)
                row = col.row(align=True)
                row.label("Object")

                row = col.row(align=True)
                row.label("Select All: A")
                row.label("Locate: G")

                row = col.row(align=True)
                row.label("Rotate: R")
                row.label("Scale: S")

                row = col.row(align=True)
                row.label("Mode: TAB")
                row.label("Snap Menu: Shift + S")

                row = col.row(align=True)
                row.label("Box Select: B")
                row.label("Circle Select: C")

                row = col.row(align=True)
                row.label("Add: Shift + A")
                row.label("Delete: X")

                row = col.row(align=True)
                row.label("Duplcate: Shift + D")
                row.label("Join: Ctrl + J")

                row = col.row(align=True)
                row.label("Pan: Shift + LMB")
                row.label("View: NUMPAD 5")

            if context.mode=='EDIT_MESH':

                col = layout.column(align=True)
                row = col.row(align=True)
                row.label("Mesh")

                row = col.row(align=True)
                row.label("Select All: A")
                row.label("Locate: G")

                row = col.row(align=True)
                row.label("Rotate: R")
                row.label("Scale: S")

                row = col.row(align=True)
                row.label("Mode: TAB")
                row.label("Snap Menu: Shift + S")

                row = col.row(align=True)
                row.label("Box Select: B")
                row.label("Circle Select: C")

                row = col.row(align=True)
                row.label("Add: Shift + A")
                row.label("Delete: X")

                row = col.row(align=True)
                row.label("Duplcate: Shift + D")
                row.label("Merge: Alt + M")

                row = col.row(align=True)
                row.label("Extrude: E")
                row.label("Knife: K")

                row = col.row(align=True)
                row.label("Edge Loop: Alt + RMB")
                row.label("Edge Ring: Ctrl + Alt + RMB")

                row = col.row(align=True)
                row.label("Pan: Shift + LMB")
                row.label("View: NUMPAD 5")

        """ -------------------------------- """

class PT_xxxx(Panel):
    bl_label = "Test"
    bl_idname = "xxxxxx"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.context_pointer_set("SpaceTextEditor", context.space_data)
        row = col.row(align=False)
        row.context_pointer_set("SpaceTextEditor", context.space_data)

        p=row.operator("text.reload")
        row = col.row(align=False)
        row.operator("text.run_script")
        row = col.row(align=False)
        row.label(str(context.space_data))
        

""" ---------------------------------------------------------------- """


""" ------------------------------------------------ """
""" Register """

def register():
    bpy.utils.register_class(VIEW3D_PT_tools_objectmode)
    bpy.utils.register_class(VIEW3D_PT_tools_meshedit)
    bpy.utils.register_class(VIEW3D_PT_tools_armatureedit)
    bpy.utils.register_class(VIEW3D_PT_tools_posemode)
    bpy.utils.register_class(SCENE_PT_Icon_Tools)
    
    #bpy.utils.register_class(PT_xxxx)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_tools_objectmode)
    bpy.utils.unregister_class(VIEW3D_PT_tools_meshedit)
    bpy.utils.unregister_class(VIEW3D_PT_tools_armatureedit)
    bpy.utils.unregister_class(VIEW3D_PT_tools_posemode)
    bpy.utils.unregister_class(SCENE_PT_Icon_Tools)
   
    #bpy.utils.unregister_class(PT_xxxx)

if __name__ == "__main__":
    register()

""" ------------------------------------------------ """





# ------------------Fast Loop > Author: Andy Davies (metalliandy)-------------------------------------------------------


class OBJECT_OT_FastLoop(bpy.types.Operator):
    bl_idname = "object_ot.fastloop"
    bl_label = "FastLoop"
    
    active = bpy.props.BoolProperty(name="active", default=False)
    
    @classmethod
    def poll(cls, context):
        return bpy.ops.mesh.loopcut_slide.poll()
    
    def modal(self, context, event):
        if event.type == 'ESC':
            context.area.header_text_set()
            return {'CANCELLED'}
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.active = False
        
        if not self.active:
            self.active = True
            bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')
            context.area.header_text_set("Press ESC twice to stop FastLoop")
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    
    ## registring
def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()

