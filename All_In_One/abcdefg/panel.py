import bpy
import os
from odcutils import get_settings
from healing_abutment import tooth_to_FDI as FDI
from healing_abutment import tooth_to_text as PAL
           
class VIEW3D_PT_ODCCustomUCLAWax(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type="TOOLS"
    bl_category = "Profile Generator"
    bl_label = "Anatomic Profile Generator"
    bl_context = ""
    
    def draw(self, context):
        sce = bpy.context.scene
        layout = self.layout
        
        addon_prefs = get_settings()
        
        row = layout.row()
        row.label(text = "Preferences")
        
        row = layout.row()
        col = row.column()
        col.prop(addon_prefs, "heal_workflow")
        col.prop(addon_prefs, "heal_profile")
        col.prop(addon_prefs, "profile_scale")
        col.prop(addon_prefs, "heal_print_type", text = "Print Type")
        col.prop(addon_prefs, "heal_number_sys", text = "Number System")
   
        row = layout.row()
        row.prop(addon_prefs, "heal_show_prefs", text = "Show Settings")     
        
        if addon_prefs.heal_show_prefs:
            row = layout.row()
            col = row.column()
            col.prop(addon_prefs, "heal_passive_offset", text = "Passive Gap")
            col.prop(addon_prefs, "heal_block_border_x", text = "Border Horizontal")
            col.prop(addon_prefs, "heal_block_border_y", text = "Border Vertical")
            col.prop(addon_prefs, "heal_inter_space_x", text = "Spacing Horizontal")
            col.prop(addon_prefs, "heal_inter_space_y", text = "Spacing Vertical")
            col.prop(addon_prefs, "heal_middle_space_x", text = "Spacing Middle")
            col.prop(addon_prefs, "heal_bevel_width", text = "Bevel Width")
            col.prop(addon_prefs, "mould_wall_thickness", text = "Wall Thickness")
            col.prop(addon_prefs, "default_text_size", text = "Label Font Size")
        
            #col.prop(addon_prefs, "heal_abutment_depth", text = "Abutment Depth")
            #col.prop(addon_prefs, "heal_show_prefs", text = "Show Settings")
            #col.prop(addon_prefs, "heal_show_prefs", text = "Show Settings")
            
            #operator save settings
            
            row = layout.row()
            row.operator("wm.save_userpref",text = "Save Settings")
        
        
        row = layout.row()
        row.label("Select Teeth (" + addon_prefs.heal_number_sys + " system)")
        row = layout.row()
        row.label("(expand Menu to see tooth numbers")
        row = layout.row()
        row.prop(addon_prefs, "heal_tooth_preset")
        box = layout.box()
        split = box.column_flow(8)
        
        if addon_prefs.heal_number_sys == 'UNIVERSAL':
            for i in range(0,7):
                c = split.column()
                
                if i == 0:
                    c.row().label('R') #spacer
                else:
                    c.row().label('')
                c.row().prop(addon_prefs, "heal_teeth", index = i+1,  text = str(i+2), toggle= True)
                c.row().prop(addon_prefs, "heal_teeth", index = 30 - i,  text = str(31 -i), toggle= True)
                
                if i == 0:
                    c.row().label('L') #spacer
                else:
                    c.row().label('')
                c.row().prop(addon_prefs, "heal_teeth", index = i + 8,  text = str(i+9), toggle= True)
                c.row().prop(addon_prefs, "heal_teeth", index = 23 - i,  text = str(24 -i), toggle= True)
        
        elif addon_prefs.heal_number_sys == 'F.D.I.':
            
            for i in range(0,7):
                c = split.column()
                
                if i == 0:
                    c.row().label('R') #spacer
                else:
                    c.row().label('')
                c.row().prop(addon_prefs, "heal_teeth", index = i+1,  text = FDI[i+2], toggle= True)
                c.row().prop(addon_prefs, "heal_teeth", index = 30 - i,  text = FDI[31 -i], toggle= True)
                
                if i == 0:
                    c.row().label('L') #spacer
                else:
                    c.row().label('')
                c.row().prop(addon_prefs, "heal_teeth", index = i + 8,  text = FDI[i+9], toggle= True)
                c.row().prop(addon_prefs, "heal_teeth", index = 23 - i,  text = FDI[24 -i], toggle= True)

        elif addon_prefs.heal_number_sys == 'PALMER':
            
            for i in range(0,7):
                c = split.column()
                
                if i == 0:
                    c.row().label('R') #spacer
                else:
                    c.row().label('')
                c.row().prop(addon_prefs, "heal_teeth", index = i+1,  text = PAL[i+2], toggle= True)
                c.row().prop(addon_prefs, "heal_teeth", index = 30 - i,  text = PAL[31 -i], toggle= True)
                
                if i == 0:
                    c.row().label('L') #spacer
                else:
                    c.row().label('')
                c.row().prop(addon_prefs, "heal_teeth", index = i + 8,  text = PAL[i+9], toggle= True)
                c.row().prop(addon_prefs, "heal_teeth", index = 23 - i,  text = PAL[24 -i], toggle= True)
        
        if addon_prefs.heal_workflow == 'WIZARD':
            box = layout.box()
            row = box.row()
            row.label('Basic Steps')
            row = box.row()
            
            row = box.row()
            row.prop(addon_prefs, "heal_abutment_file")
            
            row = box.row()
            col = row.column(align=True)
            col.operator("opendental.heal_import_abutment", text = "Import Abutment")
            
            row = box.row()
            col = row.column(align = True)
            col.operator("opendental.heal_abutment_generator", text = "Create Abutment From Measurements")
            
            row = box.row()
            row.prop(addon_prefs, "heal_abutment_depth", text = "Depth to Collar")
            row = box.row()
            col = row.column()
            col.prop(addon_prefs, "heal_block_label")
            col.operator("opendental.heal_auto_generate")
            col.operator("apg.export_block", text = "Export Model")
            
            box = layout.box()
            row = box.row()
            row.label('Boolean Fixes')
            row = box.row()
            col = row.column()
            col.operator("opendental.heal_boolean_change_solver", text = "Change Solver")
            col.operator("opendental.heal_boolean_nudge", text = "Nudge Booleans")
            col.operator("opendental.heal_boolean_nudge_block",text = "Fix Booleans in Bottom")
        
        
            box = layout.box()
            row = box.row()
            row.label('Issues/Bugs and Help')
            row = box.row()
            col = row.column()
            col.operator("wm.console_toggle",text = "Open Console")
            col.operator("wm.url_open",text = "Report Issue").url = "https://bitbucket.org/impdental/waxing_designer/issues"
        
            return
        
        row = layout.row()
        row.label('Abutment Fns')
        row = layout.row()
        row.prop(addon_prefs, "heal_abutment_file")
        
        row = layout.row()
        col = row.column(align=True)
        
        col.operator("opendental.heal_import_abutment", text = "Import Abutment")    
        row = layout.row()
        
        row.label('Abutment Cleanup Ops')
        row = layout.row()  
        col = row.column()
        col.operator("opendental.heal_mark_abutment_shoulder", text = "Mark Abutment Shoulder")
        col.operator("opendental.heal_mark_abutment_timing", text = "Mark Abutment Timing")
        col.prop(addon_prefs, "heal_advanced_abutment")
        if addon_prefs.heal_advanced_abutment:
            col.operator("opendental.heal_abutment_generator", text = "Create Abutment From Measurements")
            col.operator("opendental.heal_remove_internal", text = "Remove Internal Geom")
            col.operator("opendental.ucla_remove_timing", text = "Remove Timing Geom")
            col.operator("opendental.heal_cut_at_cursor", text = "Cut at Cursor")
            col.operator("opendental.heal_extend_flat", text = "Extend From Cursor")
            col.operator("apg.export_abutment", text = "Export Abutment")
            
        row = layout.row()
        row.label('Generate Profiles and Shapes')
        row = layout.row()
        col = row.column()
        col.prop(addon_prefs, "heal_abutment_depth", text = "Depth CEJ to Platform")  
        #col.operator("opendental.heal_generate_profiles", text = "Generate Profiles")
        
        cejs = [ob.name for ob in context.scene.objects if ":CEJ" in  ob.name]
        if len(cejs) == 0:
            col.operator("opendental.heal_database_profiles", text = "Database Profiles (Mesh)")
            col.operator("opendental.heal_database_curve_profiles", text = "Database Profiles (Curve)")
        
        
        row = layout.row()
        col = row.column()
        col.prop(addon_prefs, "heal_show_ob")
        
        if addon_prefs.heal_mirror_transform == True:
            col.operator("opendental.heal_stop_mirror")
        else:
            col.operator("opendental.heal_mirror_transform")
        if addon_prefs.heal_show_ob and context.object != None:
            if ":CEJ" in context.object.name:
                col.prop(context.object, "dimensions")
                col.prop(context.object, "location")
        
        col.operator("opendental.heal_mesh_convert", text = "Connect CEJ to Base")
        
        
        
        row = layout.row()
        row.label('Edit Profile Shapes')
        row = layout.row()
        col = row.column()
        
        col.prop(addon_prefs, 'heal_show_edit')
        
        if context.object != None and addon_prefs.heal_show_edit:
            
            vis_obs = [ob for ob in context.scene.objects if not ob.hide]
        
            local = len(vis_obs) <= 1
            
            if ":Profile" in context.object.name and "Final" not in context.object.name:
                col.label(context.object.name)
                if local == False:
                    col.operator("opendental.heal_isolate_view", text = "Isolate View")
                elif local and context.mode != 'SCULPT':
                    col.operator("opendental.heal_global_view", text = "Global View")
        
                    if context.object.mode == 'OBJECT':
                        col.operator("object.mode_set", text = 'Go Sculpt').mode = 'SCULPT'
                        col.operator("opendental.heal_reprofile", text = 'Cone Profile').preset = 'CONE'
                        col.operator("opendental.heal_reprofile", text = 'Hour Glass Profile').preset = 'HOURGLASS'
                        col.operator("opendental.heal_reprofile", text = 'Convex Profile').preset = 'BOWL'
                        col.operator("opendental.heal_reprofile", text = 'Deep Convex Profile').preset = 'DEEP_BOWL'
                        
                elif context.object.mode == 'SCULPT':
                    col.operator("object.mode_set", text = 'Finish Sculpt').mode = 'OBJECT'
        
        is_local = False
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces[0]
                if space.local_view: #check if using local view
                    is_local = True
                    break
        if is_local:
            row = layout.row()
            row.label('Need Global View to continue!')
            return
        
        row = layout.row()
        row.label('Generate Box')
        row = layout.row()
        col = row.column()
        col.prop(addon_prefs, "heal_print_type")
        col.operator("opendental.heal_generate_box", text = "Generate Box")
        
        row = layout.row()
        row.label('Labels and Custom Text')
        row = layout.row()
        col = row.column()
        col.operator("opendental.heal_generate_text", text = "Generate Labels")
        
        row = layout.row()
        row.prop(addon_prefs, "heal_custom_text")
        row = layout.row()
        row.operator("opendental.heal_custom_text", text = "Add Text at 3D Cursor")
        
        row = layout.row()
        row.label("Prepare CAD Model")
        row = layout.row()
        col = row.column()
        col.operator("opendental.heal_emboss_text", text = "Emboss All Text")
        col.operator("opendental.heal_create_final_template", text = "Boolean Profiles")
        
        
        col.operator("opendental.heal_boolean_nudge", text = "Fix Boolean")
        col.operator("opendental.heal_boolean_nudge_block",text = "Fix Booleans in Bottom")
        
        row = layout.row()
        row.label("Export CAD Model")
        
        row = layout.row()
        if len(context.selected_objects) == 0:
            row.label('Select the object!')
        elif len(context.selected_objects) > 1:
            row.label('Select only 1 object!')   
        elif context.object != None:
            row.label(context.object.name)

        row = layout.row()
        col = row.column()
        col.operator("apg.export_block", text = "Export Block")
        
        box = layout.box()
        row = box.row()
        row.label('Issues/Bugs and Help')
        row = box.row()
        col = row.column()
        col.operator("wm.console_toggle",text = "Open Console")
        col.operator("wm.url_open",text = "Report Issue").url = "https://bitbucket.org/impdental/waxing_designer/issues"
        
        
def register():
    #bpy.utils.register_class(SCENE_UL_odc_teeth)
    #bpy.utils.register_class(SCENE_UL_odc_implants)
    #bpy.utils.register_class(SCENE_UL_odc_bridges)
    #bpy.utils.register_class(SCENE_UL_odc_splints)
    #bpy.utils.register_class(VIEW3D_PT_ODCSettings)
    #bpy.utils.register_class(VIEW3D_PT_ODCTeeth)
    #bpy.utils.register_class(VIEW3D_PT_ODCImplants)
    #bpy.utils.register_class(VIEW3D_PT_ODCBridges)
    #bpy.utils.register_class(VIEW3D_PT_ODCSplints)
    #bpy.utils.register_class(VIEW3D_PT_ODCOrtho)
    #bpy.utils.register_class(VIEW3D_PT_ODCDentures)
    #bpy.utils.register_class(VIEW3D_PT_ODCModels)
    bpy.utils.register_class(VIEW3D_PT_ODCCustomUCLAWax)
    #bpy.utils.register_module(__name__)
    
def unregister():
    #bpy.utils.unregister_class(SCENE_UL_odc_teeth)
    #bpy.utils.unregister_class(SCENE_UL_odc_implants)
    #bpy.utils.unregister_class(SCENE_UL_odc_bridges)
    #bpy.utils.unregister_class(SCENE_UL_odc_splints)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCTeeth)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCImplants)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCBridges)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCSettings)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCBridges)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCSplints)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCOrtho)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCDentures)
    #bpy.utils.unregister_class(VIEW3D_PT_ODCModels)
    bpy.utils.unregister_class(VIEW3D_PT_ODCCustomUCLAWax)
if __name__ == "__main__":
    register()