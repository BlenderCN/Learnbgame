#############################################
# SCENE/OBJECT UTILITIES & QUICK FUNCTIONS
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
import os
import numpy
from bpy.props import *
from . constants import *
from . scene_props import *
from . import_nodes import *
import ntpath

# METHODS
#############################################

#----------------------------------------------------------------------------------
#- Fills a selection of pedestrian objects with the given props
#----------------------------------------------------------------------------------
#def fill_pedestrians(selection, ped_data):
#    print("omg")


# OPERATORS
#############################################
#----------------------------------------------------------------------------------
class THUGUtilShowFirstPoint(bpy.types.Operator):
    bl_idname = "io.import_thug_util_showfirstpt"
    bl_label = "Show 1st Pt"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Selects the first point on the path you're currently working with."

    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'CURVE' and context.active_object.mode == 'EDIT')
        
    def execute(self, context):
        ob = context.active_object
        if len(ob.data.splines) > 0:
            if len(ob.data.splines[0].points) > 0:
                bpy.ops.curve.select_all(action='DESELECT')
                ob.data.splines[0].points[0].select = True
        return {'FINISHED'}

    
        
#----------------------------------------------------------------------------------
class THUGUtilFillPedestrians(bpy.types.Operator):
    bl_idname = "io.import_thug_util_fillpedestrians"
    bl_label = "Set Pedestrians"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Fills a selection (or all) pedestrian objects with default settings for THUG1/2/PRO."
    game_mode = EnumProperty(items=(
        ("THUG1", "THUG1", ""),
        ("THUG2", "THUG2/PRO", ""),
        ), name="Target Game", default="THUG1")

    def execute(self, context):
        peds = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.thug_empty_props.empty_type == 'Pedestrian' ]
        for ped in peds:
            ped.thug_ped_props.ped_type = 'Ped_From_Profile'
            ped.thug_ped_props.ped_source = 'Profile'
            ped.thug_ped_props.ped_profile = 'random_male_profile'
            ped.thug_ped_props.ped_skeleton = 'THPS5_human'
            ped.thug_ped_props.ped_animset = 'animload_THPS5_human'
            if self.game_mode == 'THUG2':
                ped.thug_ped_props.ped_skeleton = 'THPS6_human'
                ped.thug_ped_props.ped_animset = 'animload_THPS6_human'
            ped.thug_ped_props.ped_extra_anims = ''
            ped.thug_ped_props.ped_suspend = 0
            ped.thug_ped_props.ped_model = ''
            ped.thug_ped_props.ped_nologic = False
            
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        peds = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.thug_empty_props.empty_type == 'Pedestrian' ]
        return len(peds) > 0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=350)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Node Array Import")
        row = col.row()
        row.prop(self, "game_mode")
        
#----------------------------------------------------------------------------------
class THUGUtilFillVehicles(bpy.types.Operator):
    bl_idname = "io.import_thug_util_fillvehicles"
    bl_label = "Set Vehicles"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Fills a selection (or all) vehicle objects with default settings for THUG1/2/PRO."
    game_mode = EnumProperty(items=(
        ("THUG1", "THUG1/Underground+", ""),
        ("THUG2", "THUG2/PRO", ""),
        ), name="Target Game", default="THUG1")

    def execute(self, context):
        vehs = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.thug_empty_props.empty_type == 'Vehicle' ]
        for veh in vehs:
            veh.thug_veh_props.veh_type = 'Generic'
            veh.thug_veh_props.veh_model = 'veh\\Veh_DCShoeTruck\\Veh_DCShoeTruck.mdl'
            veh.thug_veh_props.veh_skeleton = 'car'
            veh.thug_veh_props.veh_suspend = 108000
            veh.thug_veh_props.veh_norail = False
            veh.thug_veh_props.veh_noskitch = False
            veh.thug_veh_props.veh_usemodellights = False
            veh.thug_veh_props.veh_allowreplacetex = False
            
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        vehs = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.thug_empty_props.empty_type == 'Vehicle' ]
        return len(vehs) > 0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=350)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Node Array Import")
        row = col.row()
        row.prop(self, "game_mode")
        
#----------------------------------------------------------------------------------
class THUGUtilAutoWall(bpy.types.Operator):
    bl_idname = "io.import_thug_util_autowall"
    bl_label = "Auto-Wall"
    bl_description = "Detects walls in your scene and marks them wallrideable."
    pass_options = EnumProperty(items=(
        ("ClearInvalid", "Clear Invalid", "Unsets the wallride flag on faces that are not considered walls."),
        ("MarkValid", "Mark Valid", "Sets the wallride flag on faces considered walls."),
        ), name="Options", default={"MarkValid"}, options={'ENUM_FLAG'})
    tolerance = FloatProperty(name="Tolerance", min=0.001, max=0.99, default=0.15, description="How much slope is allowed when detecting walls")

    def execute(self, context):
        objects = [o for o in bpy.data.objects if o.type == 'MESH' and o.thug_export_collision == True ]
        for ob in objects:
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            cfl = bm.faces.layers.int.get("collision_flags")
            
            if not cfl:
                cfl = bm.faces.layers.int.new("collision_flags")
            
            for f in bm.faces:
                flags = f[cfl]
                if f.normal[2] > -self.tolerance and f.normal[2] < self.tolerance:
                    if "MarkValid" in self.pass_options \
                    and not (flags & FACE_FLAGS['mFD_VERT']) and not (flags & FACE_FLAGS['mFD_NON_COLLIDABLE']):
                        flags |= FACE_FLAGS['mFD_WALL_RIDABLE']
                else:
                    if "ClearInvalid" in self.pass_options:
                        flags &= ~FACE_FLAGS['mFD_WALL_RIDABLE']
                f[cfl] = flags
            bm.to_mesh(ob.data)
            bm.free()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        objects = [o for o in bpy.data.objects if o.type == 'MESH' and o.thug_export_collision == True ]
        return len(objects) > 0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=350)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Auto-Wall Utility")
        row = col.row()
        row.prop_menu_enum(self, "pass_options", icon='SETTINGS')
        row.prop(self, "tolerance", icon='SETTINGS')


#----------------------------------------------------------------------------------
class THUGUtilBatchTerrain(bpy.types.Operator):
    bl_idname = "io.import_thug_util_batchterrain"
    bl_label = "Set Terrain"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Sets the terrain type on all faces/points for all selected objects/rail paths."
    terrain_type = EnumProperty(
        name="Terrain Type",
        items=[(t, t, t) for t in ["Auto"] + TERRAIN_TYPES], 
        description="Terrain type to set.")

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        curves = [o for o in context.selected_objects if o.type == 'CURVE' and o.thug_path_type != ""]
        for ob in meshes:
            bpy.context.scene.objects.active = ob
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bm = bmesh.from_edit_mesh(ob.data)
            ttl = bm.faces.layers.int.get("terrain_type")
            if not ttl:
                ttl = bm.faces.layers.int.new("terrain_type")
            for face in bm.faces:
                #if not face.select:
                #    continue
                if self.terrain_type == "Auto":
                    face[ttl] = AUTORAIL_AUTO
                else:
                    face[ttl] = TERRAIN_TYPES.index(self.terrain_type)
            bmesh.update_edit_mesh(context.edit_object.data)
            bpy.ops.object.editmode_toggle()
            ob.select = False
        
        for ob in curves:
            ob.thug_rail_terrain_type = self.terrain_type
            # Set the terrain on any points with terrain defined
            for spline in ob.data.splines:
                points = spline.points
                point_count = len(points)
                p_num = -1
                for point in points:
                    p_num += 1
                    if len(ob.data.thug_pathnode_triggers) > p_num and ob.data.thug_pathnode_triggers[p_num].terrain != "Auto" and ob.data.thug_pathnode_triggers[p_num].terrain != "None":
                        ob.data.thug_pathnode_triggers[p_num].terrain = self.terrain_type
            
            
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        curves = [o for o in context.selected_objects if o.type == 'CURVE' and o.thug_path_type != ""]
        return len(meshes) > 0 or len(curves) > 0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=250)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        #col.label(text="Node Array Import")
        row = col.row()
        row.prop(self, "terrain_type")

#----------------------------------------------------------------------------------
class THUGUtilBatchObjectProps(bpy.types.Operator):
    bl_idname = "io.import_thug_util_batchobjprops"
    bl_label = "Object Properties"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Applies a selection of properties on all selected objects."
    
    # Basic object properties
    thug_created_at_start = EnumProperty(name="Created At Start", items=[
        ("NULL", " --- ", "This property will not be modified."),
        ("True", "Yes", ""),
        ("False", "No", "")
    ], default="NULL")
    thug_network_option = EnumProperty(name="Network Options", items=[
            ("NULL", " --- ", "This property will not be modified."),
            ("Default", "Default", "Appears in network games."),
            ("AbsentInNetGames", "Offline Only", "Only appears in single-player."),
            ("NetEnabled", "Online (Broadcast)", "Appears in network games, events/scripts appear on all clients.")],
        default="NULL")
    thug_export_collision = EnumProperty(name="Export to Collisions", items=[
        ("NULL", " --- ", "This property will not be modified."),
        ("True", "Yes", ""),
        ("False", "No", "")
    ], default="NULL")
    thug_export_scene = EnumProperty(name="Export to Scene", items=[
        ("NULL", " --- ", "This property will not be modified."),
        ("True", "Yes", ""),
        ("False", "No", "")
    ], default="NULL")
    thug_lightgroup = EnumProperty(name="Light Group", items=[
            ("NULL", " --- ", "This property will not be modified."),
            ("None", "None", ""),
            ("Outdoor", "Outdoor", ""),
            ("NoLevelLights", "NoLevelLights", ""),
            ("Indoor", "Indoor", "")],
        default="NULL")
    thug_is_trickobject = EnumProperty(name="Is a TrickObject", items=[
        ("NULL", " --- ", "This property will not be modified."),
        ("True", "Yes", ""),
        ("False", "No", "")
    ], default="NULL")
    thug_cluster_name = StringProperty(name="TrickObject Cluster")
        
    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH' or o.type == 'CURVE']
        for ob in meshes:
            if self.thug_created_at_start != "NULL":
                print("Updating thug_created_at_start for object {}...".format(ob.name))
                ob.thug_created_at_start = (self.thug_created_at_start == "True")
            if self.thug_network_option != "NULL":
                print("Updating thug_network_option for object {}...".format(ob.name))
                ob.thug_network_option = self.thug_network_option
                
            # Mesh-only properties start here!
            if ob.type == 'MESH':
                if self.thug_export_collision != "NULL":
                    print("Updating thug_export_collision for object {}...".format(ob.name))
                    ob.thug_export_collision = (self.thug_export_collision == "True")
                if self.thug_export_scene != "NULL":
                    print("Updating thug_export_scene for object {}...".format(ob.name))
                    ob.thug_export_scene = (self.thug_export_scene == "True")
                if self.thug_lightgroup != "NULL":
                    print("Updating thug_lightgroup for object {}...".format(ob.name))
                    ob.thug_lightgroup = self.thug_lightgroup
            # Mesh-only properties end here!
            
            if self.thug_is_trickobject != "NULL":
                print("Updating thug_is_trickobject for object {}...".format(ob.name))
                ob.thug_is_trickobject = (self.thug_is_trickobject == "True")
                if self.thug_is_trickobject == "True":
                    print("Updating thug_cluster_name for object {}...".format(ob.name))
                    ob.thug_cluster_name = self.thug_cluster_name
                    
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH' or o.type == 'CURVE']
        return len(meshes) > 0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=800, height=350)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="                                        ")
        col.row().prop(self, "thug_created_at_start")
        col.row().prop(self, "thug_network_option")
        col.row().prop(self, "thug_export_collision")
        col.row().prop(self, "thug_export_scene")
        col.row().prop(self, "thug_lightgroup")
        col.row().prop(self, "thug_is_trickobject")
        col.row().prop(self, "thug_cluster_name")

#----------------------------------------------------------------------------------
class THUGUtilBatchImport(bpy.types.Operator):
    bl_idname = "io.import_thug_util_batchimport"
    bl_label = "Import Level/Model"
    bl_description = "Imports mesh/collision/textures in one process."
    
    # Basic object properties
    game_mode = EnumProperty(name="Game Engine", items=[
        ("NULL", " --- ", ""),
        ("THPS4", "THPS4", "Note: THPS4 collision importing not yet supported."),
        ("THUG1", "THUG1", ""),
        ("THUG2", "THUG2", "THUG2/THUG PRO."),
    ], default="NULL")
    
    scn_file_path = StringProperty(name="Scene/skin file", default="", description="Path to the .scn/.skin/.mdl file.", subtype="FILE_PATH")
    col_file_path = StringProperty(name="Collision file", default="", description="Path to the .col file.", subtype="FILE_PATH")
    tex_file_path = StringProperty(name="Texture file", default="", description="Path to the .tex file.", subtype="FILE_PATH")
    ske_file_path = StringProperty(name="Skeleton file", default="", description="Path to the .ske file.", subtype="FILE_PATH")
    
    def execute(self, context):
        # IMPORT TEX FILE
        if self.tex_file_path:
            head, tail = ntpath.split(self.tex_file_path)
            if head and tail:
                print("Running tex import on: {}{}".format(head, tail))
                bpy.ops.io.thug2_tex("EXEC_DEFAULT", filename=tail, directory=head)
            else:
                raise Exception("Unable to parse TEX file path.")
        # END IMPORT TEX FILE
        
        # IMPORT SCN FILE
        if self.scn_file_path:
            head, tail = os.path.split(self.scn_file_path)
            if head and tail:
                if self.game_mode == "THPS4":
                    print("Running THPS4 scn import on: {}{}".format(head, tail))
                    bpy.ops.io.th4_xbx_scn_to_scene("EXEC_DEFAULT", filename=tail, directory=head, load_tex=False, import_custom_normals=True)
                elif self.game_mode == "THUG1":
                    print("Running THUG1 scn import on: {}{}".format(head, tail))
                    bpy.ops.io.thug1_xbx_scn_to_scene("EXEC_DEFAULT", filename=tail, directory=head, load_tex=False, import_custom_normals=True)
                elif self.game_mode == "THUG2":
                    print("Running THUG2 scn import on: {}{}".format(head, tail))
                    bpy.ops.io.thug2_xbx_scn_to_scene("EXEC_DEFAULT", filename=tail, directory=head, load_tex=False, import_custom_normals=True)
            else:
                raise Exception("Unable to parse SCN file path.")
        # END IMPORT SCN FILE
        
        # IMPORT COL FILE
        if self.col_file_path:
            head, tail = ntpath.split(self.col_file_path)
            if head and tail:
                print("Running col import on: {}{}".format(head, tail))
                bpy.ops.io.thug_xbx_col_to_scene("EXEC_DEFAULT", filename=tail, directory=head)
            else:
                raise Exception("Unable to parse COL file path.")
        # END IMPORT SCN FILE
        
        # IMPORT SKE FILE
        if self.ske_file_path:
            head, tail = ntpath.split(self.ske_file_path)
            if head and tail:
                print("Running ske import on: {}{}".format(head, tail))
                bpy.ops.io.import_thug_skeleton("EXEC_DEFAULT", filename=tail, directory=head, set_rotation=False)
            else:
                raise Exception("Unable to parse SKE file path.")
        # END IMPORT SKE FILE
                
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=800, height=350)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="                                        ")
        col.row().prop(self, "game_mode")
        col.row().prop(self, "scn_file_path")
        col.row().prop(self, "col_file_path")
        col.row().prop(self, "tex_file_path")
        col.row().prop(self, "ske_file_path")


# PANELS
#############################################
#----------------------------------------------------------------------------------
class THUGObjectUtils(bpy.types.Panel):
    bl_label = "TH Object Utilities"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"
    bl_category = "THUG Tools"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        if not context.scene: return
        scene = context.scene
        row = self.layout.row()
        row.column().operator(THUGUtilFillPedestrians.bl_idname, THUGUtilFillPedestrians.bl_label, icon="TEXT")
        row.column().operator(THUGUtilFillVehicles.bl_idname, THUGUtilFillVehicles.bl_label, icon="TEXT")
        row = self.layout.row()
        row.column().operator(THUGUtilBatchTerrain.bl_idname, THUGUtilBatchTerrain.bl_label, icon="TEXT")
        row.column().operator(THUGUtilBatchObjectProps.bl_idname, THUGUtilBatchObjectProps.bl_label, icon="TEXT")
        if context.edit_object and context.edit_object.type == 'CURVE':
            self.layout.row().operator(THUGUtilShowFirstPoint.bl_idname, THUGUtilShowFirstPoint.bl_label, icon="TEXT")
            
        self.layout.row().operator(THUGUtilBatchImport.bl_idname, text=THUGUtilBatchImport.bl_label, icon='PLUGIN')
        self.layout.row().operator(THUGImportNodeArray.bl_idname, text=THUGImportNodeArray.bl_label, icon='PLUGIN')
        self.layout.row().operator(THUGImportTriggerScripts.bl_idname, text=THUGImportTriggerScripts.bl_label, icon='PLUGIN')
        self.layout.row().operator(THUGRenameObjects.bl_idname, text=THUGRenameObjects.bl_label, icon='FILE_TEXT')
        self.layout.row().operator(THUGMergeObjects.bl_idname, text=THUGMergeObjects.bl_label, icon='FILE_TEXT')
        self.layout.row().operator(THUGUtilAutoWall.bl_idname, text=THUGUtilAutoWall.bl_label, icon='MESH_PLANE')