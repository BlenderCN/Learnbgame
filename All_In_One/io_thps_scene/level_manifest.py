#############################################
# LEVEL MANIFEST FILE HANDLER
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
import os
import numpy
from bpy.props import *


# METHODS
#############################################

#----------------------------------------------------------------------------------
#- Writes the level manifest JSON file
#----------------------------------------------------------------------------------
def export_level_manifest_json(filename, directory, operator, level_info):
    with open(os.path.join(directory, "../" + filename + ".level.json"), "w") as outp:
        outp.write("{\n")
        outp.write("\t\"level_name\": \"{}\",\n".format(level_info.level_name))
        outp.write("\t\"scene_name\": \"{}\",\n".format(level_info.scene_name))
        outp.write("\t\"sky_scene_name\": \"{}\",\n".format(level_info.scene_name + "_Sky"))
        outp.write("\t\"creator_name\": \"{}\",\n".format((level_info.creator_name if level_info.creator_name else "Unknown")))

        outp.write("\t\"level_qb\": \"levels\\\\{}\\\\{}.qb\",\n".format(level_info.scene_name, level_info.scene_name))
        outp.write("\t\"level_scripts_qb\": \"levels\\\\{}\\\\{}_scripts.qb\",\n".format(level_info.scene_name, level_info.scene_name))
        outp.write("\t\"level_sfx_qb\": \"levels\\\\{}\\\\{}_sfx.qb\",\n".format(level_info.scene_name, level_info.scene_name))
        outp.write("\t\"level_thugpro_qb\": \"levels\\\\{}\\\\{}_thugpro.qb\",\n".format(level_info.scene_name, level_info.scene_name))

        if not level_info.level_flag_noprx:
            outp.write("\t\"level_pre\": \"{}_scripts.pre\",\n".format(level_info.scene_name))
            outp.write("\t\"level_scnpre\": \"{}scn.pre\",\n".format(level_info.scene_name))
            outp.write("\t\"level_colpre\": \"{}col.pre\",\n".format(level_info.scene_name))
            
        # Export level light color & angles
        lighta = level_info.level_ambient_rgba
        lightc0 = level_info.level_light0_rgba
        lightc1 = level_info.level_light1_rgba
        lighta0 = level_info.level_light0_headpitch
        lighta1 = level_info.level_light1_headpitch
        outp.write("\t\"ambient_rgba\": [{}, {}, {}, {}],\n".format(int(lighta[0]*255), int(lighta[1]*255), int(lighta[2]*255), int(lighta[3]*255)))
        outp.write("\t\"light0_rgba\": [{}, {}, {}, {}],\n".format(int(lightc0[0]*255), int(lightc0[1]*255), int(lightc0[2]*255), int(lightc0[3]*255)))
        outp.write("\t\"light1_rgba\": [{}, {}, {}, {}],\n".format(int(lightc1[0]*255), int(lightc1[1]*255), int(lightc1[2]*255), int(lightc1[3]*255)))
        outp.write("\t\"light0_position\": [{}, {}],\n".format(lighta0[0], lighta0[1]))
        outp.write("\t\"light1_position\": [{}, {}],\n".format(lighta1[0], lighta1[1]))
        
        outp.write("\t\"FLAG_OFFLINE\": {},\n".format(("true" if level_info.level_flag_offline else "false")))
        outp.write("\t\"FLAG_INDOOR\": {},\n".format(("true" if level_info.level_flag_indoor else "false")))
        outp.write("\t\"FLAG_NOSUN\": {},\n".format(("true" if level_info.level_flag_nosun else "false")))
        outp.write("\t\"FLAG_DEFAULT_SKY\": {},\n".format(("true" if level_info.level_flag_defaultsky else "false")))
        outp.write("\t\"FLAG_ENABLE_WALLRIDE_HACK\": {},\n".format(("true" if level_info.level_flag_wallridehack else "false")))
        outp.write("\t\"FLAG_DISABLE_BACKFACE_HACK\": {},\n".format(("true" if level_info.level_flag_nobackfacehack else "false")))
        outp.write("\t\"FLAG_MODELS_IN_SCRIPT_PRX\": {},\n".format(("true" if level_info.level_flag_modelsinprx else "false")))
        outp.write("\t\"FLAG_DISABLE_GOALEDITOR\": {},\n".format(("true" if level_info.level_flag_nogoaleditor else "false")))
        outp.write("\t\"FLAG_DISABLE_GOALATTACK\": {},\n".format(("true" if level_info.level_flag_nogoalattack else "false")))
        outp.write("\t\"FLAG_NO_PRX\": {},\n".format(("true" if level_info.level_flag_noprx else "false")))
        outp.write("\t\"FLAG_IS_BIG_LEVEL\": {},\n".format(("true" if level_info.level_flag_biglevel else "false")))

        outp.write("}\n")


# PANELS
#############################################
#----------------------------------------------------------------------------------
class THUGSceneSettings(bpy.types.Panel):
    bl_label = "TH Level Settings"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        if not context.scene: return
        scene = context.scene
        self.layout.row().prop(scene.thug_level_props, "level_name")
        self.layout.row().prop(scene.thug_level_props, "scene_name")
        self.layout.row().prop(scene.thug_level_props, "creator_name")
        #self.layout.row().prop(scene.thug_level_props, "level_skybox")
        
        #self.layout.row().prop(scene.thug_level_props.export_props, "use_quick_export")
        # QUICK EXPORT SETTINGS
        if True: #scene.thug_level_props.export_props.use_quick_export:
            box = self.layout.box().column()
            box.row().prop(scene.thug_level_props.export_props, "target_game")
            box.row().prop(scene.thug_level_props.export_props, "directory")
            box.row().prop(scene.thug_level_props.export_props, "scene_type", expand=True)
            if scene.thug_level_props.export_props.scene_type == 'Model':
                box.row().prop(scene.thug_level_props.export_props, "model_type", toggle=True, icon='MOD_EDGESPLIT')
            box.separator()
            
            box.row().prop(scene.thug_level_props.export_props, "generate_sky", toggle=True, icon='MAT_SPHERE_SKY')
            if scene.thug_level_props.export_props.generate_sky:
                box.row().prop(scene.thug_level_props.export_props, "skybox_name")
                
            box.row().prop(scene.thug_level_props.export_props, "always_export_normals", toggle=True, icon='SNAP_NORMAL')
            box.row().prop(scene.thug_level_props.export_props, "speed_hack", toggle=True, icon='FF')
            box.row().prop(scene.thug_level_props.export_props, "autosplit_everything", toggle=True, icon='MOD_EDGESPLIT')
            if scene.thug_level_props.export_props.autosplit_everything:
                box2 = box.box().column(True)
                box2.row().prop(scene.thug_level_props.export_props, "autosplit_faces_per_subobject")
                box2.row().prop(scene.thug_level_props.export_props, "autosplit_max_radius")
                
            box.row().prop(scene.thug_level_props.export_props, "pack_pre", toggle=True, icon='PACKAGE')
            box.row().prop(scene.thug_level_props.export_props, "is_park_editor", toggle=True, icon='PACKAGE')
            box.row().prop(scene.thug_level_props.export_props, "generate_tex_file", toggle=True, icon='TEXTURE_DATA')
            box.row().prop(scene.thug_level_props.export_props, "generate_scn_file", toggle=True, icon='SCENE_DATA')
            box.row().prop(scene.thug_level_props.export_props, "generate_col_file", toggle=True, icon='OBJECT_DATA')
            box.row().prop(scene.thug_level_props.export_props, "generate_scripts_files", toggle=True, icon='FILE_SCRIPT')
            box.row().prop(scene.thug_level_props.export_props, "export_scale")
            box2 = box.box().column(True)
            box2.row().prop(scene.thug_level_props.export_props, "mipmap_offset")
            #box2.row().prop(scene.thug_level_props.export_props, "only_offset_lightmap")
        
        #self.layout.row().prop(scene.thug_level_props, "default_terrain")
        #self.layout.row().prop(scene.thug_level_props, "default_terrain_rail")
        
        self.layout.row().label(text="Level Lighting", icon='LAMP_DATA')
        if scene.thug_level_props.export_props.target_game == 'THUG1':
            # Underground+ TOD/lighting settings here
            self.layout.prop(scene.thug_level_props, "tod_scale")
            self.layout.prop(scene.thug_level_props, "tod_slot")
            
            if scene.thug_level_props.tod_slot != '':
                tod_props = scene.thug_level_props.tod_day
                if scene.thug_level_props.tod_slot == 'EVENING':
                    tod_props = scene.thug_level_props.tod_evening
                elif scene.thug_level_props.tod_slot == 'NIGHT':
                    tod_props = scene.thug_level_props.tod_night
                elif scene.thug_level_props.tod_slot == 'MORNING':
                    tod_props = scene.thug_level_props.tod_morning
                    
            #self.layout.label(text="TOD - " + scene.thug_level_props.tod_slot)
            box = self.layout.box().column()
            box.row().label(text="Ambient Down/Up Color")
            tmp_row = box.row().split()
            col = tmp_row.column()
            col.prop(tod_props, "ambient_down_rgb", text='')
            col = tmp_row.column()
            col.prop(tod_props, "ambient_up_rgb", text='')
            tmp_row = box.row().split()
            col = tmp_row.column()
            col.prop(tod_props, "sun_rgb")
            col = tmp_row.column()
            col.prop(tod_props, "sun_headpitch")
            tmp_row = box.row().split()
            col = tmp_row.column()
            col.prop(tod_props, "light1_rgb")
            col = tmp_row.column()
            col.prop(tod_props, "light1_headpitch")
            box.row().label(text="Fog Distance/Color")
            tmp_row = box.row().split()
            col = tmp_row.column()
            col.prop(tod_props, "fog_startend", text='')
            col = tmp_row.column()
            col.prop(tod_props, "fog_bottomtop", text='')
            box.row().prop(tod_props, "fog_rgba", text='')
            
        else:
            # Legacy lighting settings!
            box = self.layout.box().column(True)
            box.row().prop(scene.thug_level_props, "level_ambient_rgba")
            
            tmp_row = box.row().split()
            col = tmp_row.column()
            col.prop(scene.thug_level_props, "level_light0_rgba")
            col = tmp_row.column()
            col.prop(scene.thug_level_props, "level_light0_headpitch")
            
            tmp_row = box.row().split()
            col = tmp_row.column()
            col.prop(scene.thug_level_props, "level_light1_rgba")
            col = tmp_row.column()
            col.prop(scene.thug_level_props, "level_light1_headpitch")
        
        self.layout.row().label(text="Level Flags", icon='INFO')
        box = self.layout.box().column(True)
        box.row().prop(scene.thug_level_props, "level_flag_offline")
        box.row().prop(scene.thug_level_props, "level_flag_biglevel")
        box.row().prop(scene.thug_level_props, "level_flag_noprx")
        box.row().prop(scene.thug_level_props, "level_flag_indoor")
        box.row().prop(scene.thug_level_props, "level_flag_nosun")
        box.row().prop(scene.thug_level_props, "level_flag_defaultsky")
        box.row().prop(scene.thug_level_props, "level_flag_wallridehack")
        box.row().prop(scene.thug_level_props, "level_flag_nobackfacehack")
        box.row().prop(scene.thug_level_props, "level_flag_modelsinprx")
        box.row().prop(scene.thug_level_props, "level_flag_nogoaleditor")
        box.row().prop(scene.thug_level_props, "level_flag_nogoalattack")