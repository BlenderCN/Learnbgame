import bpy
import os

addon_name = os.path.basename(os.path.dirname(__file__))

class SmartConfig_AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = addon_name
    
    exception_list = bpy.props.StringProperty(name='Custom Addons to exclude', default='', description='Addon Modules to exclude separated with a comma')
    errors_report = bpy.props.BoolProperty(name='Create Error Report on export', default=True, description='Create a text file with problematic addons in case of error on the export')
    use_trunk_exception = bpy.props.BoolProperty(name='Exclude Trunk Addons', default=True, description='Exclude automatically Addons in Blender 2.79 Trunk')
    show_excluded_addons = bpy.props.BoolProperty(name='Show Addons to exclude in export', default=False)
    trunk_exception = bpy.props.StringProperty(
            name='Trunk Addons Exception', 
            default=('io_scene_3ds,io_scene_fbx,io_anim_bvh,io_mesh_ply,io_scene_obj,io_scene_x3d,io_mesh_stl,'
            'io_mesh_uv_layout,io_curve_svg,cycles,mesh_looptools,blender_id,io_export_after_effects,'
            'add_curve_extra_objects,add_curve_ivygen,add_curve_sapling,add_mesh_extra_objects,'
            'io_sequencer_edl,io_import_gimp_image_to_scene,io_import_images_as_planes,io_anim_nuke_chan,'
            'object_fracture_cell,object_fracture,node_wrangler,animation_animall,'
            'object_cloud_gen,development_icon_get,ui_layer_manager,space_view3d_pie_menus,'
            'space_view3d_stored_views,archipack,measureit,mesh_f2,rigify,space_view3d_copy_attributes,'
            'space_view3d_3d_navigation,space_view3d_display_tools,space_view3d_spacebar_menu,'
            'space_view3d_math_vis,space_view3d_modifier_tools,space_view3d_brush_menus,btrace,curve_simplify,'
            'archimesh,ant_landscape,add_mesh_BoltFactory,bone_selection_sets,animation_add_corrective_shape_key,'
            'mocap,camera_dolly_crane_rigs,development_edit_operator,development_api_navigator,camera_turnaround,'
            'development_iskeyfree,development_ui_classes,game_engine_publishing,game_engine_save_as_runtime,'
            'io_coat3D,io_anim_acclaim,io_mesh_pdb,io_export_unreal_psk_psa,io_export_pc2,io_export_paper_model,'
            'io_anim_camera,io_export_dxf,io_scene_x,io_anim_c3d,io_blend_utils,io_convert_image_to_mesh_img,'
            'io_import_dxf,io_shape_mdd,io_scene_ms3d,io_import_scene_unreal_psa_psk,io_import_scene_lwo,'
            'io_mesh_raw,io_online_sketchfab,io_scene_vrml2,lighting_dynamic_sky,materials_library_vx,'
            'object_print3d_utils,materials_utils,mesh_auto_mirror,mesh_bsurfaces,mesh_custom_normals_tools,'
            'mesh_extra_tools,space_clip_editor_refine_solution,space_clip_editor_autotracker,mesh_tiny_cad,'
            'mesh_tissue,mesh_snap_utilities_line,mesh_relax,mesh_inset,mesh_carver,object_boolean_tools,'
            'add_advanced_objects_menu,add_advanced_objects_panels,object_fracture_crack,object_edit_linked,'
            'object_grease_scatter,oscurart_tools,object_skinify,paint_palette,render_copy_settings,'
            'render_clay,render_auto_tile_size,object_animrenderbake,pie_menus_official,render_freestyle_svg,'
            'light_field_tools,render_povray,netrender,sequencer_kinoraw_tools,system_demo_mode,ui_translate,'
            'system_property_chart,system_blend_info,uv_bake_texture_to_vcols,uv_magic_uv,uv_texture_atlas'),
            )
            
    
    def draw(self, context):
        layout = self.layout
        row=layout.row()
        row.prop(self, "errors_report")
        row.prop(self, "use_trunk_exception")
        row.operator('smartconfig.print_addons', icon='INFO')
        row=layout.row()
        row.prop(self, "exception_list")
        box=layout.box()
        row=box.row(align=True)
        if self.show_excluded_addons==False:
            row.prop(self, 'show_excluded_addons', text='', emboss=False, icon='TRIA_RIGHT')
            row.label('Show excluded Addons')
        else:
            row.prop(self, 'show_excluded_addons', text='', emboss=False, icon='TRIA_DOWN')
            row.label('Show excluded Addons')
            if self.use_trunk_exception==True:
                split=box.split()
                col=split.column(align=True)
                col2=split.column(align=True)
                col.label('TRUNK EXCEPTIONS')
                if self.exception_list!="":
                    col2.label('CUSTOM EXCEPTIONS')
                for a in self.trunk_exception.split(","):
                    col.label(a)
            else:
                col2=box.column(align=True)
            for a in self.exception_list.split(","):
                col2.label(a)
                


# get addon preferences
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get(addon_name)
    return getattr(addon, "preferences", None)