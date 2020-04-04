#3d_cursor_menu.py (c) 2011 Jonathan Smith (JayDez)
#
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
    "name": "Context Sensitive Menu",
    "author": "zeffii, ideasman42, meta-androcto, batFINGER, Demohero",
    "version": (2,0),
    "blender": (2, 6, 1),
    "location": "View3D, Object, Edit Mesh, Edit Curve, Armature, Edit Armature, Pose >  Shift RMB",
    "description": "Context Sensitive Menu for Blender users",
    "category": "Learnbgame",
}

import bpy

# Object Specials                     
                    
class ConSenOb(bpy.types.Menu):
    bl_label = "Object Specials"
    bl_idname = "VIEW3D_MT_object_specials"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'objectmode':
                
                layout.separator()
                
    @classmethod
    def poll(cls, context):
        # add more special types
        return context.object

    def draw(self, context):
        layout = self.layout

        obj = context.object
        if obj.type == 'CAMERA':
            layout.operator_context = 'INVOKE_REGION_WIN'

            if obj.data.type == 'PERSP':
                props = layout.operator("wm.context_modal_mouse", text="Camera Lens Angle")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.lens"
                props.input_scale = 0.1
            else:
                props = layout.operator("wm.context_modal_mouse", text="Camera Lens Scale")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.ortho_scale"
                props.input_scale = 0.01

            if not obj.data.dof_object:
                #layout.label(text="Test Has DOF obj");
                props = layout.operator("wm.context_modal_mouse", text="DOF Distance")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.dof_distance"
                props.input_scale = 0.02

        if obj.type in {'CURVE', 'FONT'}:
            layout.operator_context = 'INVOKE_REGION_WIN'

            props = layout.operator("wm.context_modal_mouse", text="Extrude Size")
            props.data_path_iter = "selected_editable_objects"
            props.data_path_item = "data.extrude"
            props.input_scale = 0.01

            props = layout.operator("wm.context_modal_mouse", text="Width Size")
            props.data_path_iter = "selected_editable_objects"
            props.data_path_item = "data.offset"
            props.input_scale = 0.01

        if obj.type == 'EMPTY':
            layout.operator_context = 'INVOKE_REGION_WIN'

            props = layout.operator("wm.context_modal_mouse", text="Empty Draw Size")
            props.data_path_iter = "selected_editable_objects"
            props.data_path_item = "empty_draw_size"
            props.input_scale = 0.01

        if obj.type == 'LAMP':
            layout.operator_context = 'INVOKE_REGION_WIN'

            props = layout.operator("wm.context_modal_mouse", text="Energy")
            props.data_path_iter = "selected_editable_objects"
            props.data_path_item = "data.energy"

            if obj.data.type in {'SPOT', 'AREA', 'POINT'}:
                props = layout.operator("wm.context_modal_mouse", text="Falloff Distance")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.distance"
                props.input_scale = 0.1

            if obj.data.type == 'SPOT':
                layout.separator()
                props = layout.operator("wm.context_modal_mouse", text="Spot Size")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.spot_size"
                props.input_scale = 0.01

                props = layout.operator("wm.context_modal_mouse", text="Spot Blend")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.spot_blend"
                props.input_scale = -0.01

                props = layout.operator("wm.context_modal_mouse", text="Clip Start")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.shadow_buffer_clip_start"
                props.input_scale = 0.05

                props = layout.operator("wm.context_modal_mouse", text="Clip End")
                props.data_path_iter = "selected_editable_objects"
                props.data_path_item = "data.shadow_buffer_clip_end"
                props.input_scale = 0.05

        layout.separator()

        props = layout.operator("object.isolate_type_render")
        props = layout.operator("object.hide_render_clear_all")


# Mesh Tools 

class ConSenEd(bpy.types.Menu):
    bl_label = "Mesh Tools"
    bl_idname = "OBJECT_MT_context_sensitive_menu"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_MESH':

                layout.separator()
                
                current_mesh_mode = context.tool_settings.mesh_select_mode[:]

               
                # if vertex mode on
 
                if current_mesh_mode[0]: 
                    
                    
                    layout.operator_context = 'INVOKE_REGION_WIN'
                    
                    layout.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude Region")
                    layout.operator("mesh.extrude_vertices_move", text="Extrude Only Vertices")
                    layout.operator("transform.resize", text="Scale")
                    
                    layout.separator()
                    
                    layout.operator("mesh.loopcut_slide")
                    
                    layout.separator()
                   
                    layout.operator("mesh.merge")
                    layout.operator("mesh.rip_move")
                    layout.operator("mesh.split")
                    layout.operator("mesh.merge")
                    layout.operator("mesh.separate")
                    
                    layout.separator()
                    
                    layout.operator("mesh.remove_doubles")
                    
                    layout.separator()
                    
                    layout.operator("mesh.vertices_smooth")
                    layout.operator("mesh.vertices_sort")
                    layout.operator("mesh.vertices_randomize")
                    layout.operator("mesh.select_vertex_path")
                    layout.operator("mesh.blend_from_shape")
                    layout.operator("object.vertex_group_blend")
                    layout.operator("mesh.shape_propagate_to_all")
                    
                    layout.separator()
                    
                    layout.menu("VIEW3D_MT_vertex_group")
                    layout.menu("VIEW3D_MT_hook", text="Hooks")
					
                  
                # if edge mode on
                
                if current_mesh_mode[1]:
                    
                    layout.operator_context = 'INVOKE_REGION_WIN'
                    
                    layout.operator("view3d.edit_mesh_extrude_move_normal", text= "Extrude Region")
                    layout.operator("mesh.extrude_edges_move", text= "Extrude Edges Only")
                    layout.operator("transform.resize", text="Scale")
                     
                    layout.separator()
                    
                    layout.operator("mesh.loopcut_slide")
                    
                    layout.separator()
                    
                    layout.operator("mesh.edge_face_add")
                    layout.operator("mesh.subdivide")
                    
                    layout.separator()
                    
                    layout.operator("mesh.merge")
                    layout.operator("mesh.remove_doubles")
                    
                    layout.separator()
                    
                    layout.operator("mesh.mark_seam")
                    layout.operator("mesh.mark_seam", text="Clear Seam").clear = True
                    
                    layout.separator()
                    
                    layout.menu("VIEW3D_MT_uv_map", icon='MOD_UVPROJECT')
                    
                    layout.separator()
                    
                    layout.operator("mesh.mark_sharp")
                    layout.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
                    
                    layout.separator()
                    
                    layout.operator("mesh.edge_rotate", text="Rotate Edge CW")
                    layout.operator("mesh.edge_rotate", text="Rotate Edge CCW").direction = 'CCW'
                    
                    layout.separator()
                    
                    layout.operator("transform.edge_slide")
                    layout.operator("transform.edge_crease")
                    layout.operator("mesh.loop_multi_select", text="Edge Loop")
                    layout.operator("mesh.loop_multi_select", text="Edge Ring").ring = True
                    
                    layout.separator()
                    
                    layout.operator("mesh.loop_to_region")
                    layout.operator("mesh.region_to_loop")

                # if face mode on
                
                if current_mesh_mode[2]:
                    
                    layout.operator_context = 'INVOKE_REGION_WIN'
                    
                    layout.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude Region")
                    layout.operator("mesh.extrude_faces_move", text="Extrude Individual")
                    layout.operator("mesh.subdivide")
                    
                    layout.operator("transform.resize", text="Scale")
                    
                    layout.separator()
  
                    layout.operator("mesh.flip_normals")
                    layout.operator("mesh.edge_face_add")
                    layout.operator("mesh.fill")
                    layout.operator("mesh.beautify_fill")
                    layout.operator("mesh.solidify")
                    layout.operator("mesh.sort_faces")
            
                    layout.separator()
            
                    layout.operator("mesh.merge")
                    layout.operator("mesh.remove_doubles")
                    
                    layout.separator()
            
                    layout.operator("mesh.fgon_make")
                    layout.operator("mesh.fgon_clear")
            
                    layout.separator()
            
                    layout.operator("mesh.quads_convert_to_tris")
                    layout.operator("mesh.tris_convert_to_quads")
                    layout.operator("mesh.edge_flip")
            
                    layout.separator()
            
                    layout.operator(    "mesh.faces_shade_smooth")
                    layout.operator("mesh.faces_shade_flat")
            
                    layout.separator()
            
                    layout.operator("mesh.edge_rotate", text="Rotate Edge CW").direction = 'CW'
            
                    layout.separator()
                   
                    layout.operator_menu_enum("mesh.uvs_rotate", "direction")
                    layout.operator_menu_enum("mesh.uvs_mirror", "axis")
                    layout.operator_menu_enum("mesh.colors_rotate", "direction")
                    layout.operator_menu_enum("mesh.colors_mirror", "axis")
                    
                    layout.separator()
                    
    

# Curve Tools 

class ConSenCur(bpy.types.Menu):
    bl_label = "Curve Tools"
    bl_idname = "VIEW3D_MT_edit_curve_specials"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_CURVE':
                
                layout.separator()
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator("curve.extrude")
        
        layout.separator()
        
        layout.operator("transform.transform", text="Tilt").mode = 'TILT'
        layout.operator("curve.tilt_clear")
        
        layout.operator("transform.transform", text="Shrink/Fatten").mode = 'CURVE_SHRINKFATTEN'
        
        layout.separator()
            
        layout.operator("curve.subdivide", text="Subdivide")
        layout.operator("curve.separate")
        
        layout.operator("curve.switch_direction", text="Switch Direction")
        layout.operator("curve.spline_weight_set")
        layout.operator("curve.radius_set")
        layout.operator("curve.smooth")
        layout.operator("curve.smooth_radius")
        
        layout.separator()
        
        layout.operator("curve.duplicate")
        layout.operator("curve.delete")
        layout.operator("curve.cyclic_toggle")
        layout.operator("curve.switch_direction")
        layout.operator("curve.spline_type_set")
            
        layout.separator()
        
        layout.operator_menu_enum("curve.handle_type_set", "type")
        
        layout.menu("VIEW3D_MT_hook", text="Hooks")
  

# Metaball Tools   
          
class ConSenMet(bpy.types.Menu):
    bl_label = "Metaball Tools"
    bl_idname = "VIEW3D_MT_metaball"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_METABALL':
                
                layout.separator()
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
            
        layout.operator("transform.translate")
        layout.operator("transform.rotate")
        layout.operator("transform.resize", text= "Scale")  


# Text Tools         
        
class ConSenTex(bpy.types.Menu):
    bl_label = "Text Tools"
    bl_idname = "VIEW3D_MT_text"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_TEXT':
                
                layout.separator()
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
            
        layout.operator("font.text_copy")
        layout.operator("font.text_cut")
        layout.operator("font.text_paste")
        
        layout.separator()
        
        layout.operator("font.case_set", text = "Set Case To Upper").case ='UPPER'
        layout.operator("font.case_set", text = "Set Case To Lower").case ='LOWER'
        
        layout.separator()
        
        layout.operator("font.style_toggle", text = "Style Bold")
        layout.operator("font.style_toggle", text = "Style Italic").style ='ITALIC'
        layout.operator("font.style_toggle", text = "Style Underline").style ='UNDERLINE'
        
  
# Armature Tools   
        
class ConSenArm(bpy.types.Menu):
    bl_label = "Armature Tools"
    bl_idname = "VIEW3D_MT_armature_specials"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_ARMATURE':
                
                layout.separator()
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        
        layout.operator("armature.extrude_move")
        layout.operator("armature.extrude_forked")
        layout.operator("armature.merge")
        layout.operator("armature.fill")
        layout.operator("armature.delete")
        layout.operator("armature.separate")

        
        layout.separator()
        
        layout.operator("armature.subdivide", text="Subdivide")
        layout.operator("armature.duplicate_move")
        
        layout.separator()
        
        layout.operator("armature.parent_set", text="Make Parent")
        layout.operator("armature.parent_clear", text="Clear Parent")
        
        layout.separator()
        
        layout.operator("armature.switch_direction", text="Switch Direction")

        layout.separator()

        layout.operator_context = 'EXEC_REGION_WIN'
        layout.operator("armature.autoside_names", text="AutoName Left/Right").type = 'XAXIS'
        layout.operator("armature.autoside_names", text="AutoName Front/Back").type = 'YAXIS'
        layout.operator("armature.autoside_names", text="AutoName Top/Bottom").type = 'ZAXIS'
        layout.operator("armature.flip_names", text="Flip Names")
        
        layout.separator()
        
        layout.menu("VIEW3D_MT_bone_options_enable",
            text="Enable Bone Options")
        layout.menu("VIEW3D_MT_bone_options_toggle",
            text="Toggle Bone Options")
        layout.menu("VIEW3D_MT_bone_options_disable",
            text="Disable Bone Options")  
            
            
# Pose Tools           
        
class ConSenPos(bpy.types.Menu):
    bl_label = "Pose Tools"
    bl_idname = "POS_ED_pose_tools"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'POSE':
                
                layout.separator()
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
		
        layout.operator("pose.push")
        layout.operator("pose.relax")
        layout.operator("pose.breakdown")
    
        layout.separator()
    
        layout.operator("pose.copy")
        layout.operator("pose.paste")
        layout.operator("pose.paste", text="Paste X-Flipped Pose").flipped = True
        
        layout.operator("poselib.pose_add")
        
        layout.menu("VIEW3D_MT_pose_apply")
        layout.separator()
        
        layout.operator_menu_enum("object.parent_set", "type", text="Set Parent")
        layout.operator_menu_enum("object.parent_clear", "type", text="Clear Parent")
        
        layout.separator()
        
        layout.menu("VIEW3D_MT_pose_motion")
        layout.menu("VIEW3D_MT_pose_group")
        layout.separator()

        layout.menu("VIEW3D_MT_pose_ik")
        layout.separator()

        layout.menu("VIEW3D_MT_pose_constraints")
        layout.separator()

        layout.operator("pose.quaternions_flip")
        layout.separator()

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("pose.armature_layers",
            text="Change Armature Layers...")
        layout.operator("pose.bone_layers", text="Change Bone Layers...")
        layout.separator()

        layout.menu("VIEW3D_MT_bone_options_enable",
            text="Enable Bone Options")
        layout.menu("VIEW3D_MT_bone_options_toggle",
            text="Toggle Bone Options")
        layout.menu("VIEW3D_MT_bone_options_disable",
            text="Disable Bone Options")             


# Lattice Tools         
        
class ConSenLat(bpy.types.Menu):
    bl_label = "Lattice Tools"
    bl_idname = "VIEW3D_MT_hook"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'EDIT_LATTICE':
                
                layout.separator()
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
            
        layout.operator("object.hook_add_newob")
        layout.operator("object.hook_add_selob")
        
        layout.separator()
        
        layout.operator("lattice.make_regular")
 

# Weight Paint Tools        
        
class ConSenWeight(bpy.types.Menu):
    bl_label = "Weight Tools"
    bl_idname = "Weight_Paint"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'PAINT_WEIGHT':
                
                layout.separator()       
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.operator("paint.weight_set")
        
        layout.separator() 
		
        layout.operator("object.vertex_group_normalize_all", text="Normalize All")
        layout.operator("object.vertex_group_normalize", text="Normalize")
        layout.operator("object.vertex_group_mirror", text="Mirror")
        layout.operator("object.vertex_group_invert", text="Invert")
        layout.operator("object.vertex_group_clean", text="Clean")
        layout.operator("object.vertex_group_levels", text="Levels")
        layout.operator("object.vertex_group_fix", text="Fix Deforms")
        
        layout.separator()
        
        layout.operator("paint.weight_from_bones", text="Assing From Bone Envelopes").type='ENVELOPES'
        layout.operator("paint.weight_from_bones", text="Assing Automatic From Bones")
        

# Texture Paint Tools

class ConSenTP(bpy.types.Menu):
    bl_label = "Not Avaliable in Texture Paint Mode"
    bl_idname = "TextureP_Menu"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'PAINT_TEXTURE':
                
                layout.separator() 
                
    def draw(self, context):
        layout = self.layout
        
        
# Vertex Paint Tools

class ConSenVP(bpy.types.Menu):
    bl_label = "Vertex Paint Tools"
    bl_idname = "VertexP_Menu"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'PAINT_VERTEX':
                
                layout.separator()       
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.operator("paint.vertex_color_dirt")    
        layout.operator("paint.vertex_color_set")          
        

# Sculpt Tools       
            
class ConSenSculpt(bpy.types.Menu):
    bl_label = "Sculpt Tools"
    bl_idname = "Sculpt_Menu"

    def draw(self, context):
        layout = self.layout
        if context.space_data.type == 'VIEW_3D':
            if context.mode == 'SCULPT':
                
                layout.separator()       
                
    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.operator("brush.reset")
        

    # Define Keymaps (Shift R)    

    km = bpy.context.window_manager.keyconfigs.active.keymaps['Curve']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VIEW3D_MT_edit_curve_specials" 
    
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Object Mode']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VIEW3D_MT_object_specials"   
   
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "OBJECT_MT_context_sensitive_menu" 
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Armature']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VIEW3D_MT_armature_specials" 
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Lattice']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VIEW3D_MT_hook"    
        
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Pose']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "POS_ED_pose_tools"       
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Metaball']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VIEW3D_MT_metaball"   
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Font']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VIEW3D_MT_text"   
               
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Weight Paint']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "Weight_Paint"   
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Sculpt']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "Sculpt_Menu"  
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Vertex Paint']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "VertexP_Menu"  
    
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Image Paint']
    kmi = km.keymap_items.new('wm.call_menu', 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi.properties.name = "TextureP_Menu"  
    
    
# Register and Unregister

def register():
    bpy.utils.register_class(ConSenOb)
    bpy.utils.register_class(ConSenEd)
    bpy.utils.register_class(ConSenCur)
    bpy.utils.register_class(ConSenMet)
    bpy.utils.register_class(ConSenTex)
    bpy.utils.register_class(ConSenArm)
    bpy.utils.register_class(ConSenPos)
    bpy.utils.register_class(ConSenLat)
    bpy.utils.register_class(ConSenWeight)
    bpy.utils.register_class(ConSenTP)
    bpy.utils.register_class(ConSenVP)
    bpy.utils.register_class(ConSenSculpt)
    

def unregister():
    bpy.utils.unregister_class(ConSenOb)
    bpy.utils.unregister_class(ConSenEd)
    bpy.utils.unregister_class(ConSenCur)
    bpy.utils.unregister_class(ConSenMet)
    bpy.utils.unregister_class(ConSenTex)
    bpy.utils.unregister_class(ConSenArm)
    bpy.utils.unregister_class(ConSenPos)
    bpy.utils.unregister_class(ConSenLat)
    bpy.utils.unregister_class(ConSenWeight)
    bpy.utils.unregister_class(ConSenTP)
    bpy.utils.unregister_class(ConSenVP)
    bpy.utils.unregister_class(ConSenSculpt)


if __name__ == "__main__":
    register()
