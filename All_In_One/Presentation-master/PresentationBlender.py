
bl_info = {
    "name": "Presentation Maker",
    "description": "Blender projects can be generated with json files of a specific format.",
    "author": "aporter",
    "version": (0,0,1,0),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    "location": "View3D"
}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
# if "bpy" in locals():
#     import imp
#     imp.reload(CompositeWriter)
#     print("Reloaded multifiles")
# else:
from CompositeWriter import CompositeWriter
from BlenderToJson import BlenderToJson
print("Imported multifiles")

import math
import mathutils
import bpy
import os.path
import json
import bpy.types
import numbers
import inspect
import bmesh
import shutil, errno
from types import *
from Constants import COMPOSITOR_NODE_COMPOSITE, SHADER_NODE_BACKGROUND, SHADER_WORLD_NODE_OUTPUT, SHADER_NODE_DIFFUSE, SHADER_NODE_MIX, SHADER_NODE_VALUE, SHADER_EMISSION, SHADER_OUTPUT_MATERIAL, SHADER_MIX_RGB, _keypoint_settings, KEYPOINT_SETTINGS, RENDERSETTINGS, IMAGE_SETTINGS, CYCLESRENDERSETTINGS, CONVERT_INDEX, DEFAULT_ENVIRONMENT
debugmode = True
def debugPrint(val=None):
    if debugmode and val:
        print(val)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class PresentationBlenderGUI(bpy.types.Panel):
    """Presentation GUI"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    # bl_category = "Movie"
    bl_label = "Generate Presentation"
 
    def draw(self, context):
        TheCol = self.layout.column(align=True)
        TheCol.prop(context.scene, "presentation_settings")
        TheCol.operator("object.presentation_blender_maker", text="Update")
        TheCol.operator("object.presentation_blender_mat_comp_reader", text="Read Mat/Comp")
        TheCol.separator()
        TheCol.separator()
        TheCol.prop(context.scene, "use_output_folder")
        TheCol.prop(context.scene, "presentation_scene_output_folder")
        TheCol.separator()
        TheCol.prop(context.scene, "isbillboardcomposite")
        #TheCol.operator("object.presentation_compositor_to_billboard", text="Billboard Composite")
        TheCol.operator("object.presentation_blender_from_scene", text="Scene")
        TheCol.operator("object.presentation_compositor", text="Composite")
        TheCol.operator("object.write_config", text="Config")
        TheCol.prop(context.scene, "presentation_name")
        TheCol.operator("object.write_environment", text="Environment")
        TheCol.operator("object.write_worlds", text="Worlds")
        TheCol.operator("object.write_groups", text="Groups")
        TheCol.operator("object.write_materials", text="Materials")
        TheCol.operator("object.copy_textures", text="Copy Textures")
        TheCol.separator()
        TheCol.separator()
        TheCol.prop(context.scene, "matcompositefile")
        TheCol.operator("object.presentation_blender_material_composite_reader", text="Setup Comp/Mat/World")
        
class PresentationBlenderFromScene(bpy.types.Operator):
    """Presentation Blender From Scene """
    bl_idname = "object.presentation_blender_from_scene"
    bl_label = "Presentation Blender from scenes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        self.context = context
        cursor = scene.cursor_location
        debugPrint("Read blender from scene")
        try:
            debugPrint("start")
            blenderToJson = BlenderToJson()
            res = blenderToJson.readScene(self.context.scene)
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                with open(os.path.join(scene.presentation_scene_output_folder, "scene.json"), 'w') as outfile:
                    json.dump(res, outfile)
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
        except Exception as e:
            debugPrint("didnt work out")
            debugPrint(e)
        return {'FINISHED'}

class WriteConfig(bpy.types.Operator):
    """Write configuration"""
    bl_idname = "object.write_config"
    bl_label = "Write config"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        
        try:
            debugPrint("start")
            res = { 
                "scene": "scene.json",  
                "environment": "environment.json",
                "composite": "composite.json", 
                "composite.groups":"groups.json", 
                "composite.materials": "materials.json",
                "composite.worlds":"worlds.json", 
                "billboardComposite": "billboard-composite.json",
                "billboardComposite.groups": "billboard-groups.json",
                "billboardComposite.materials": "billboard-materials.json",
                "billboardComposite.worlds": "billboard-worlds.json" 
                }
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                with open(os.path.join(scene.presentation_scene_output_folder, "config.json"), 'w') as outfile:
                    json.dump(res, outfile)
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")

        return {'FINISHED'}

class CopyTextureDirectory(bpy.types.Operator):
    """Copy Textures to directory"""
    bl_idname = "object.copy_textures"
    bl_label = "Copy textures"
    bl_options = {'REGISTER', 'UNDO'}

    def copyanything(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc: # python >2.5
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: raise

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        
        try:
            debugPrint("start")
            if scene.use_output_folder and scene.presentation_scene_output_folder != None and scene.presentation_name != None:
                dst = os.path.join(scene.presentation_scene_output_folder , scene.presentation_name, "textures")
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                self.copyanything(os.path.join(bpy.path.abspath("//"), "textures"), dst)
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")

        return {'FINISHED'}

class WriteWorlds(bpy.types.Operator):
    """Write Worlds"""
    bl_idname = "object.write_worlds"
    bl_label = "Write Worlds"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = context.active_object
        self.context = context
        
        try:
            debugPrint("start")
            compositeWriter = CompositeWriter()
            compositeWriter.forceRelative = True #context.scene.presentation_name != None
            compositeWriter.relativePath = False #context.scene.presentation_name
            compositeWriter.replaceWith = "//textures/"
            compositeWriter.replaceText = "//textures\\"
            worlds = compositeWriter.readWorlds(bpy.data.worlds)
            res = { "worlds": worlds }
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                filename = "worlds.json"
                if scene.isbillboardcomposite:
                    filename = "billboard-worlds.json"
                with open(os.path.join(scene.presentation_scene_output_folder, filename), 'w') as outfile:
                    json.dump(res, outfile)
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")
        return {'FINISHED'}

class WriteGroups(bpy.types.Operator):
    """Write Groups"""
    bl_idname = "object.write_groups"
    bl_label = "Write Groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        
        try:
            debugPrint("start")
            compositeWriter = CompositeWriter()
            compositeWriter.forceRelative = True #context.scene.presentation_name != None
            compositeWriter.relativePath = False #context.scene.presentation_name
            compositeWriter.replaceWith = "//textures/"
            compositeWriter.replaceText = "//textures\\"
            groups = compositeWriter.readGroups(bpy.data.node_groups)
            res = { "groups": groups }
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                filename = "groups.json"
                if scene.isbillboardcomposite:
                    filename = "billboard-groups.json"
                with open(os.path.join(scene.presentation_scene_output_folder, filename), 'w') as outfile:
                    json.dump(res, outfile)
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")
        return {'FINISHED'}

class WriteMaterials(bpy.types.Operator):
    """Write Materials"""
    bl_idname = "object.write_materials"
    bl_label = "Write Materials"
    bl_options = {'REGISTER','UNDO'}
    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = context.active_object
        self.context = context
        
        try:
            debugPrint("start write materials")
            compositeWriter = CompositeWriter()
            compositeWriter.forceRelative = True #context.scene.presentation_name != None
            compositeWriter.relativePath = False #context.scene.presentation_name
            compositeWriter.replaceWith = "//textures/"
            compositeWriter.replaceText = "//textures\\"
            matLib = {}
            materials = compositeWriter.readMats(bpy.data.materials)
            groups = compositeWriter.readGroups(bpy.data.node_groups, 'SHADER')
            res = { "materials" : materials, "library": groups }
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                filename = "materials.json"
                if scene.isbillboardcomposite:
                    filename = "billboard-materials.json"
                with open(os.path.join(scene.presentation_scene_output_folder, filename), 'w') as outfile:
                    json.dump(res, outfile)
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")
        return {'FINISHED'}

class WriteEnvironment(bpy.types.Operator):
    """Write Environment"""
    bl_idname = "object.write_environment"
    bl_label = "Write config"
    bl_options = {'REGISTER', 'UNDO'}
    def getCamera(self, scene):
        for obj in scene.objects:
            if obj.type == "CAMERA":
                return obj
        return None
    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        
        try:
            debugPrint("start")
            res = DEFAULT_ENVIRONMENT
            res["name"] = scene.presentation_name
            res["id"] = scene.presentation_name
            res["folder"] = scene.presentation_name
            res["resourceType"] = scene.presentation_name
            camera = self.getCamera(scene)
            if camera != None:
                res["camera"] = camera.name
            res["composite_parameters"]["start_frame"] = scene.frame_start
            res["composite_parameters"]["end_frame"] = scene.frame_end
            res["composite_parameters"]["frame_count"] = scene.frame_end - scene.frame_start + 1
            res["world"] = scene.world.name
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                filename = "environment.json"
                if scene.isbillboardcomposite:
                    filename = "billboard-environment.json"
                with open(os.path.join(scene.presentation_scene_output_folder, filename), 'w') as outfile:
                    json.dump(res, outfile)
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")

        return {'FINISHED'}
class CompositorToScene(bpy.types.Operator):
    """Compositor to Scene composite settings"""
    bl_idname = "object.presentation_compositor"
    bl_label = "Composite Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = context.active_object
        self.context = context
        
        try:
            debugPrint("start")
            compositeWriter = CompositeWriter()
            compositeWriter.forceRelative = True #context.scene.presentation_name != None
            compositeWriter.relativePath = False #context.scene.presentation_name
            compositeWriter.replaceWith = "//"+context.scene.presentation_name+"/"
            compositeWriter.replaceText = "//textures\\"
            compositeWriter.replaceAnd = "//"+context.scene.presentation_name+"\\"
            comp = compositeWriter.readMats([self.context.scene])
            groups = compositeWriter.readGroups(bpy.data.node_groups, 'COMPOSITING')
            res = { "composite" : comp, "library": groups }
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            if scene.use_output_folder and scene.presentation_scene_output_folder != None:
                filename = "composite.json"
                if scene.isbillboardcomposite:
                    filename = "billboard-composite.json"
                with open(os.path.join(scene.presentation_scene_output_folder, filename), 'w') as outfile:
                    json.dump(res, outfile)
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")

        return {'FINISHED'}


class PresentationBlenderMatCompReader(bpy.types.Operator):
    """Presentation Blender Material Composition"""
    bl_idname = "object.presentation_blender_mat_comp_reader"
    bl_label = "Presentation Material Reader"
    bl_options = {'REGISTER', 'UNDO'}
    
    # total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = context.active_object
        self.context = context
        # settings = context.scene.presentation_settings
        # debugPrint(context.scene.presentation_settings)
        #
        try:
            debugPrint("start")
            compositeWriter = CompositeWriter()
            materials = compositeWriter.readMats(bpy.data.materials)
            groups = compositeWriter.readGroups(bpy.data.node_groups)
            worlds = compositeWriter.readWorlds(bpy.data.worlds)
            comp = compositeWriter.readComp(self.context.scene)
            scenes = compositeWriter.readComps(bpy.data.scenes)
            res = { "materials" : materials, "composite": comp, "groups": groups, "worlds": worlds, "scenes": scenes }
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
            debugPrint("complete")
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")

        return {'FINISHED'}     

class PresentationBlenderMaterialCompositeReader(bpy.types.Operator):
    """Presentation Blender Material Composition"""
    bl_idname = "object.presentation_blender_material_composite_reader"
    bl_label = "Setup composite material and world"
    bl_options = {'REGISTER', 'UNDO'}
    
    # total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        compositeWriter = CompositeWriter()
        #
        try:
            settings = context.scene.matcompositefile
            f = open(settings, 'r')
            filecontents = f.read()
            obj = json.loads(filecontents)
            debugPrint("loaded config json")
            presentation_material_animation_points = []
            compositeWriter.setup(obj, context, presentation_material_animation_points)
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)              
        return {'FINISHED'}
        
class PresentationBlenderAnimation(bpy.types.Operator):
    """Presentation Blender Animation"""
    bl_idname = "object.presentation_blender_maker"
    bl_label = "Presentation Maker"
    bl_options = {'REGISTER', 'UNDO'}
    
    presentation_armatures = []
    presentation_objects = []
    presentation_target_bones = []
    presentation_material_animation_points = []

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        self.context = context
        settings = context.scene.presentation_settings
        self.relativeDirePath = self.fixPath(os.path.dirname(settings))
        # debugPrint(context.scene.presentation_settings)
        try:
            self.clearObjects()
        except Exception as e:
            debugPrint(e)
        try:
            f = open(settings, 'r')
            filecontents = f.read()
            
            obj = json.loads(filecontents)
            debugPrint("loaded config json")
            self.processAnimation(obj)
            bpy.ops.file.pack_all()
            bpy.ops.file.unpack_all(method='USE_LOCAL')
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")

        return {'FINISHED'}
    def processAnimation(self, config):
        debugPrint("processing animation")
        #debugPrint("{}".format(config))
        self.settings = self.loadSettings(config)
        debugPrint("set settings")
        self.scenes = self.loadSceneConfig(config)
        debugPrint("set scenes config")
        self.createScenes(self.scenes)
        debugPrint("created scenes")
        for scene in self.scenes:
            debugPrint("switching scenes")
            self.switchToScene(scene["name"])
            debugPrint("processing setings")
            self.processSettings(scene)
            self.processCompositeParts(scene)
            self.setupWorld(scene)
            self.processWorld(scene)
            self.prolightingProcess(scene)
            debugPrint("start proskies processing")
            self.proskiesProcess(scene)
            self.armatures = self.loadArmaturesConfig(scene)
            newobjects = self.createObjectsUsed(scene)
            self.createStage(scene)
            self.attachGroups(scene)
            for i in range(len(newobjects)):
                newobjects[i]["scene"] = self.scene
                self.presentation_objects.append(newobjects[i])
            self.parentCreatedObjects(scene)
            
            debugPrint("configur armatures")
            self.configureArmature(scene)
            self.processArmatures(scene)
            self.processKeyFrames(scene)
            self.processArmatureFrames(scene)
            self.processMaterialKeyFrames(scene)
        compositeWriter = CompositeWriter()
        count = 0
        for scene in self.scenes:
            self.switchToScene(scene["name"])
            # compositeWriter.setupComposite(scene, self.context, self.presentation_material_animation_points)
            self.setupComposite(scene, count)
            count = count + 1
        
    def parseValue(self, value):
        if isinstance(value, bool) or isinstance(value, float) or isinstance(value, int) or isinstance(value, str):
            try:
                return float(value)
            except:
                try:
                    return int(value)
                except:
                    return value
        return value

    def proskiesProcess(self, scene):
        debugPrint("Pro skies processing")
        if "proskies" in scene:
            if scene["proskies"] == False:
                return
            elif hasattr(bpy.context.scene.world,"pl_skies_settings"):
                debugPrint("Found : Pro skies processing")
                proskies_config = scene["proskies"]
                if "skies" in proskies_config:
                    skies_config = proskies_config["skies"]
                    if "use_pl_skies" in skies_config and skies_config["use_pl_skies"]:
                        debugPrint("Using pl_skies")
                        setattr(bpy.context.scene.world.pl_skies_settings, 'use_pl_skies', True)
                        if "evn_previews" in skies_config:
                            try:
                                setattr(bpy.context.scene.world, "env_previews", skies_config["evn_previews"])
                                debugPrint("set environment preview")
                            except:
                                pass
                        for key in skies_config:
                            val = self.parseValue(skies_config[key])
                            if hasattr(bpy.context.scene.world.pl_skies_settings, key):
                                setattr(bpy.context.scene.world.pl_skies_settings, key , val)   
    def prolightingProcess(self, scene):
        debugPrint("prolighting process")
        if "prolighting" in scene:
            firefixes = False
            if scene["prolighting"] == False:
                return
            else:
                debugPrint("setup pro lighting ")
                prolighting_config = scene["prolighting"]
                if "light" in prolighting_config:
                    light_config = prolighting_config["light"]
                    debugPrint(light_config)
                    light_key_list = ["use_pl_studio_lights"]
                    if "use_pl_studio_lights" in light_config  and light_config["use_pl_studio_lights"]:
                        firefixes = True
                        for key in light_config:
                            light_key_list.append(key)
                        for key in light_key_list:
                            debugPrint(key)
                            val = self.parseValue(light_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                if "background" in prolighting_config:
                    background_config = prolighting_config["background"]
                    debugPrint(background_config)
                    background_key_list = ["use_pl_studio_background"]
                    if "use_pl_studio_background" in background_config and background_config["use_pl_studio_background"]:
                        firefixes = True
                        for key in background_config:
                            background_key_list.append(key)
                        for key in background_key_list:
                            debugPrint(key)
                            val = self.parseValue(background_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                if "reflections" in prolighting_config:
                    reflections_config = prolighting_config["reflections"]
                    debugPrint(reflections_config)
                    reflections_key_list = ["use_pl_studio_reflections"]
                    if "use_pl_studio_reflections" in reflections_config and reflections_config["use_pl_studio_reflections"]:
                        firefixes = True
                        for key in reflections_config:
                            reflections_key_list.append(key)
                        for key in reflections_key_list:
                            debugPrint(key)
                            val = self.parseValue(reflections_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                if "floor" in prolighting_config :
                    floor_config = prolighting_config["floor"]
                    #debugPrint(floor_config)
                    floor_key_list = ["use_pl_studio_floors"]
                    if "use_pl_studio_floors" in floor_config and floor_config["use_pl_studio_floors"]:
                        firefixes = True
                        for key in floor_config:
                            floor_key_list.append(key)
                        for key in floor_key_list:
                            debugPrint(key)
                            val = self.parseValue(floor_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                         
                        bpy.ops.scene.pl_studio_floor_apply()
                if firefixes :
                    bpy.ops.scene.pl_studio_fix_warnings(warning_type='background_color')
                    bpy.ops.scene.pl_studio_make_real()


    def createScenes(self, scenes):
        running = True
        while len(bpy.data.scenes) > 1:
            running = False
            debugPrint("deleting scene")
            res = bpy.ops.scene.delete()
            debugPrint("deleted scene")
            if res.pop() != "CANCELLED":
                running = True
        lastscene = bpy.data.scenes[0]
        for scene in scenes:
            debugPrint("scene ----- ")
            bpy.ops.scene.new(type='NEW')
            debugPrint("new scene made ")
            cloneScene = bpy.context.scene
            debugPrint("setting scene name")
            cloneScene.name = scene["name"]
        if len([f for f in bpy.data.scenes if f.name == lastscene.name]) > 0:
            debugPrint("switching to scene")
            self.switchToScene(lastscene.name)
            debugPrint("deleting scene")
            bpy.ops.scene.delete()

    def switchToScene(self, name):
        # 
        try:
            bpy.data.screens['Default'].scene = bpy.data.scenes[name]
            bpy.context.screen.scene = bpy.data.scenes[name]
            self.scene = bpy.context.screen.scene
        except:
            bpy.context.scene.name = name
            self.scene = bpy.context.scene
    def setupWorld(self, scene):
        debugPrint("--- setup world ---")
        if "world-config" in scene:
            world = scene["world-config"]
            bpy.data.worlds.new(world["name"])
            newworld = bpy.data.worlds[world["name"]]
            debugPrint("newworld")
            debugPrint(world["name"])
            debugPrint(newworld)
            newworld.use_nodes = True
            
            for node in newworld.node_tree.nodes:
                debugPrint("Remove node")
                newworld.node_tree.nodes.remove(node)
            debugPrint("nodes removed ---")
            self.buildMaterial(world["config"], newworld)
    def setupComposite(self, scene, index):
        debugPrint("--- setup compositor ---- ")
        if "scene-composite" in scene:
            composite = scene["scene-composite"]
            bscene = bpy.data.scenes[index]
            bscene.use_nodes = True
            for node in bscene.node_tree.nodes:
                debugPrint("remove composite tree node")
                bscene.node_tree.nodes.remove(node)
            debugPrint("composite tree nodes removed")
            self.buildMaterial(composite["config"], bscene)

    def processWorld(self, scene):
        debugPrint("process world")
        if "world" in scene:
            debugPrint("set the world ")
            worldName = scene["world"]
            if self.hasWorldsByName(worldName):
                world = self.getWorldByName(worldName)
                self.context.scene.world = world
    def isCycles(self):
        renderEngine = self.context.scene.render.engine
        return renderEngine == "CYCLES"
    def isEevee(self):
        renderEngine = self.context.scene.render.engine
        return renderEngine == "EEVEE"
    def processSettings(self, scene):
        debugPrint("Process settings")
        if "RenderEngine" in scene:
            self.context.scene.render.engine = scene["RenderEngine"]
        elif "RenderEngine" in self.settings:
            debugPrint("set render engine")
            self.context.scene.render.engine = self.settings["RenderEngine"]
        

        if "Device" in self.settings:
            debugPrint("device in settings")
            if self.isCycles():
                self.context.scene.cycles.device = self.settings["Device"]
        if "resolution_x" in self.settings:
            bpy.context.scene.render.resolution_x = float(self.settings["resolution_x"])
        else:
            bpy.context.scene.render.resolution_x = 1280
        
        if "resolution_y" in self.settings:
            bpy.context.scene.render.resolution_y = float(self.settings["resolution_y"])
        else:
            bpy.context.scene.render.resolution_y = 720
        if "filepath" in self.settings and self.settings["filepath"]:
            bpy.context.scene.render.filepath = os.path.relpath(self.settings["filepath"])
            
        bpy.context.scene.render.tile_y = 64
        if "tile_y" in self.settings:
            bpy.context.scene.render.tile_y = self.settings["tile_y"]

        bpy.context.scene.render.tile_x = 64
        if "tile_x" in self.settings:
            bpy.context.scene.render.tile_x = self.settings["tile_x"]
        
        if "fps" in self.settings:
            debugPrint("fps in settings")
            bpy.context.scene.render.fps = float(self.settings["fps"])
            bpy.context.scene.render.fps_base = 1

        if "file_format" in self.settings:
            bpy.context.scene.render.image_settings.file_format = self.settings["file_format"]

        bpy.context.scene.render.resolution_percentage = 100
        if "samples" in self.settings:
            debugPrint("samples in settings")
            if self.isCycles():
                bpy.context.scene.cycles.samples = float(self.settings["samples"])
            elif self.isEevee():
                bpy.context.scene.eevee.taa_render_samples = float(self.settings["samples"])

        else :
            default_samples  = 200
            if self.isCycles():
                bpy.context.scene.cycles.samples = default_samples
            elif self.isEevee():
                bpy.context.scene.eevee.taa_render_samples = default_samples
        if self.isCycles():
            bpy.context.scene.cycles.preview_samples = 0

        for _setting in RENDERSETTINGS:
            if _setting in self.settings and hasattr(bpy.context.scene.render, _setting):
                setattr(bpy.context.scene.render, _setting, self.settings[_setting])
        for _setting in IMAGE_SETTINGS:
            if _setting in self.settings and hasattr(bpy.context.scene.render.image_settings, _setting):
                setattr(bpy.context.scene.render.image_settings, _setting, self.settings[_setting])
        for _setting in CYCLESRENDERSETTINGS:
            if self.isCycles():
                if _setting in self.settings and hasattr(bpy.context.scene.cycles, _setting):
                    setattr(bpy.context.scene.cycles, _setting, self.settings[_setting])
        
        if "FrameEnd" in self.settings:
            debugPrint("frameend in settings")
            bpy.context.scene.frame_end = self.settings["FrameEnd"]
        
        if "FrameStart" in self.settings:
            debugPrint("framestart in settings")
            bpy.context.scene.frame_start = self.settings["FrameStart"]
        if "Objects" in self.settings:
            debugPrint("objects in settings")
            objectssettings = self.settings["Objects"]
            
            if "File" in objectssettings:
                obj_location = self.fixPath(os.path.join(self.relativeDirePath, objectssettings["File"])) 
                with bpy.data.libraries.load(obj_location) as (data_from, data_to):
                    data_to.groups = [name for name in data_from.groups if not self.hasGroupByName(name)]
            
            if "Files" in objectssettings:
                for i in range(len(objectssettings["Files"])):
                    objlocation = self.fixPath(os.path.join(self.relativeDirePath, objectssettings["Files"][i]))
                    debugPrint(objlocation)
                    with bpy.data.libraries.load(objlocation) as (data_from, data_to):
                        data_to.groups = [name for name in data_from.groups if not self.hasGroupByName(name)]
        if "MaterialGroups" in self.settings and self.settings["MaterialGroups"] != None:
            groupMaterials = self.settings["MaterialGroups"]
            self.setupGroupMaterials(groupMaterials)
        if "CompositeGroups" in self.settings and self.settings["CompositeGroups"] != None:
            groupComposites = self.settings["CompositeGroups"]
            self.setupGroupComposites(groupComposites)

        if "Materials" in self.settings:
            debugPrint("setup materials")
            matsettings = self.settings["Materials"]
            
            if "File" in matsettings:
                mat_location = matsettings["File"] 
                for i in range(len(matsettings["Names"])):
                    matname = matsettings["Names"][i]
                    opath = self.fixPath(os.path.join(self.relativeDirePath,  mat_location))
                    debugPrint(opath)
                    with bpy.data.libraries.load(opath) as (data_from, data_to):
                        data_to.materials = [name for name in data_from.materials if not self.hasMaterialByName(name)]
                        data_to.worlds = [name for name in data_from.worlds if not self.hasWorldsByName(name)]
            
            if "Materials" in matsettings:
                custom_materials = matsettings["Materials"]
                debugPrint("creating custom materials")
                compositeWriter = CompositeWriter()
                for custom_mat in custom_materials:
                    debugPrint("create material")
                    if "name" in custom_mat:
                        compositeWriter.defineMaterial(custom_mat, self.presentation_material_animation_points)
                        # self.defineMaterial(custom_mat)
                    elif "file" in custom_mat:
                        f = open(custom_mat["file"], 'r')
                        filecontents = f.read()
                        composite_settings = json.loads(filecontents)
                        
                            
    def processCompositeParts(self, scene):
        if "composite" in scene:
            compositeWriter = CompositeWriter()
            composite_settings = scene["composite"]
            if "groups" in composite_settings:
                debugPrint("define groups")
                compositeWriter.setupGroups(composite_settings["groups"], self.context, self.presentation_material_animation_points)
            if "materials" in composite_settings:
                if "materials" in composite_settings["materials"]:
                    debugPrint("material, setting one more level down, hopefully to a list/array")
                    composite_settings["materials"] = composite_settings["materials"]["materials"]
                for material in composite_settings["materials"]:
                    compositeWriter.defineMaterial(material, self.presentation_material_animation_points)
                    # self.defineMaterial(material)
            if "worlds" in composite_settings:
                debugPrint("define worlds")
                if "worlds" in composite_settings["worlds"]:
                    debugPrint("world, setting one more level down, hopefully to a list/array")
                    composite_settings["worlds"] = composite_settings["worlds"]["worlds"]
                for world in composite_settings["worlds"]:
                    compositeWriter.setupWorld(world, self.context, self.presentation_material_animation_points)

    def hasGroupByName(self, name):
        debugPrint("has group by name")
        for i in range(len(bpy.data.groups)):
            group = bpy.data.groups[i]
            if group.name == name:
                debugPrint("found group")
                return True
        debugPrint("group not found")
        return False
    def getGroupByName(self, name):
        for i in range(len(bpy.data.groups)):
            group = bpy.data.groups[i]
            if group.name == name:
                return group
        return False

    def duplicateGroup(self, group):
        debugPrint("duplicating group")
        root = self.getObject(group)
        print ("looked for root " + group.name)
        bpy.ops.object.empty_add(type="PLAIN_AXES")
        empty = self.context.active_object
        if root is None: 
            raise ValueError("There was no group found.")
            return empty
        else:
            debugPrint("has root")
            for i in range(len(root.children)):
                # root.children[i].name
                if root.children[i].name.startswith("Root"):
                    debugPrint("__")
                else :
                    bpy.ops.object.select_all(action="DESELECT")
                    debugPrint("deselected all")
                    root.children[i].select_set(True)
                    debugPrint("select child root")
                    debugPrint(root.children[i].name)
                    # bpy.ops.object.duplicate_move()
                    temp = self.duplicateObject(self.context.scene,root.children[i].name, root.children[i], root)
                    root.children[i].select_set(False)
                    debugPrint(temp.name)
                    debugPrint("duplicated the object")
                    temp.parent = empty
                    debugPrint("empty parent then temp")
                    bpy.ops.object.select_all(action="DESELECT")
                    debugPrint("last deselect")
        return empty
        
    def duplicateObject(self, scene, name, copyobj, root_parent):
 
        # Create new mesh
        debugPrint("create new mesh")
        if copyobj.type == 'LAMP':
            mesh = bpy.data.lamps.new(name, 'AREA')
        else: 
            mesh = bpy.data.meshes.new(name)
 
        # Create new object associated with the mesh
        debugPrint("create new object associated with the mesh")
        ob_new = bpy.data.objects.new(name, mesh)
 
        # Copy data block from the old object into the new object
        debugPrint("copy data block from the old object into the new object")
        if copyobj.data != None:
            ob_new.data = copyobj.data.copy() 
        # ob_new.scale = copyobj.scale.copy()
        debugPrint(root_parent.matrix_world.translation)
        # ob_new.rotation_euler = copyobj.rotation_euler.copy()
        # ob_new.location = copyobj.location.copy() - root_parent.location.copy()
        ob_new.matrix_world = copyobj.matrix_world.copy()
 
        # Link new object to the given scene and select it
        debugPrint("link new object to the given scene and select it")
        scene.objects.link(ob_new)
        ob_new.select_set(True)
        self.context.scene.update()
        if len(copyobj.children) > 0:
            for i in range(len(copyobj.children)):
                obj_ject = self.duplicateObject(scene, copyobj.children[i].name , copyobj.children[i], copyobj)
                obj_ject.parent = ob_new
                # obj_ject.location = obj_ject.location - ob_new.location
 
        return ob_new
    def getObject(self, group):
        return self.selectObject(group.objects,"Root")
    def hasImage(self, imageName):
        for key in bpy.data.images.keys():
            if key == imageName:
                return True
        return False
    def selectObject(self, array, name):
        for i in range(len(array)):
            temp = array[i]
            debugPrint(temp.name)
            if temp.name.startswith(name):
                return temp
        for i in range(len(array)):
            temp = array[i]
            if len(temp.children) > 0:
                res = self.selectObject(temp.children, name)
                if res != None:
                    return res
        return None

    def hasMaterialByName(self, name):
        for i in range(len(bpy.data.materials)):
            material = bpy.data.materials[i]
            if material.name == name:
                return True
        return False
    def materialNameStartsWith(self, name):
        for i in range(len(bpy.data.materials)):
            if name.startswith(bpy.data.materials[i].name):
                return bpy.data.materials[i]
        return None
    def hasWorldsByName(self, name):
        for i in range(len(bpy.data.worlds)):
            environment = bpy.data.worlds[i]
            if environment.name == name:
                return True
        return False

    def getWorldByName(self,name):
        for i in range(len(bpy.data.worlds)):
            world = bpy.data.worlds[i]
            if world.name == name:
                return world
        return None
    def getBlenderObjectByName(self, name):
        for i in range(len(bpy.data.objects)):
            material = bpy.data.objects[i]
            if material.name == name:
                return material
        return None
        
    def getMaterialByName(self,name):
        for i in range(len(bpy.data.materials)):
            material = bpy.data.materials[i]
            if material.name == name:
                return material
        return None

    def processArmatures(self, scene):
        debugPrint("process armatures")
        #self.presentation_armatures.append({"bone_chains":bone_chains,"armature"
        #: armature, "rig":rig})
        debugPrint("setting object mode")
        # bpy.ops.object.mode_set(mode='OBJECT')
        debugPrint("set object mode")
        if len(self.presentation_armatures) > 0 :
            bpy.ops.object.mode_set(mode='POSE')
            debugPrint(len(self.presentation_armatures))
            for i in range(len(self.presentation_armatures)):
                bone_chains = self.presentation_armatures[i]["bone_chains"]
                armature = self.presentation_armatures[i]["armature"]
                config = self.presentation_armatures[i]["configuration"]
                debugPrint("armature chains")
                debugPrint("len(self.presentation_armatures)")
                chains = self.armatures[i]["chain"]
                debugPrint("has armature chains")
                rig = self.presentation_armatures[i]["rig"]
                scn = self.context.scene
                debugPrint("setting active to rig")
                scn.objects.active = rig
                self.arrangeArmature(bone_chains, config, chains)
            bpy.ops.object.mode_set(mode='OBJECT')
           

    def arrangeArmature(self, bone_chains,  config, chains):
        debugPrint("setting to POSE mode")
        debugPrint("arrange armature") 
        arrange = "spiral"
        if "arrange" in config:
            arrange = config["arrange"]

        count = 0
        thresh = 0
        debugPrint("for each bone in chain")
        if arrange == "spiral":
            for j in range(len(bone_chains)):
                bone_chain = bone_chains[j]
                chain = chains[j]
                if count == thresh:
                    # rig.pose.bones["bone.chain." + chain].rotation_quaternion[3] = 1
                    count = 0
                    thresh = thresh + 1
                count = count + 1

    def configureArmature(self, scene):
        debugPrint("armatures")
        
        if self.armatures:
            debugPrint("foreach armature config")
            for i in range(len(self.armatures)):
                armatureConfig = self.armatures[i]
                debugPrint("new armature()")
                armature = bpy.data.armatures.new(armatureConfig["name"])
                debugPrint("new rig()")
                rig = bpy.data.objects.new(armatureConfig["name"], armature) # "Rig$" + 
                if "origin" in armatureConfig:
                    rig.location = [armatureConfig["origin"]["x"],armatureConfig["origin"]["y"],armatureConfig["origin"]["z"]]
                else :
                    rig.location = [0,0,0]
                if "rotation" in armatureConfig:
                    rig.rotation_euler.x = armatureConfig["rotation"]["x"]
                    rig.rotation_euler.y = armatureConfig["rotation"]["y"]
                    rig.rotation_euler.z = armatureConfig["rotation"]["z"]
                    
                if "parent"  in armatureConfig:
                    a_parent = self.getObjectByName(armatureConfig["parent"])
                    if a_parent == 0:
                        raise ValueError("Cant find the armatures parent " + armatureConfig["parent"])
                    else :
                         rig.parent = a_parent["object"]
                    
                rig.show_x_ray = True
                self.presentation_objects.append({"scene": self.scene,  "name" : armatureConfig["name"], "type" : "rig",  "rig" : rig, "mesh": rig.data, "object": rig })
                armature.draw_type = "STICK"
                armature.show_names = True
                scn = self.context.scene
                scn.objects.link(rig)
                scn.objects.active = rig
                debugPrint("update scene")
                scn.update()
                
                bpy.ops.object.mode_set(mode='EDIT')
                chains = armatureConfig["chain"]
                bone_chains = []
                grid = {"x":1,"y":1,"z":1}
                if "grid" in armatureConfig:
                    grid = armatureConfig["grid"]
                x_grid = grid["x"]
                chain_positions = []
                if "chain_positions" in armatureConfig:
                    chain_positions = armatureConfig["chain_positions"] 
                last_bone = False
                info_chains = []
                for j  in range(len(chains)):
                    chain = chains[j]
                    bone_chain = armature.edit_bones.new("bone.chain." + chain)
                    bone_chains.append(bone_chain)
                    chain_position = self.getBoneChain(chain_positions, chain)
                    if chain_position == None :
                        bone_chain.head = (j * x_grid,0,0)
                        bone_chain.tail = ((j + 1) * x_grid,0,0)
                    else:
                        bone_chain.head = (chain_position["head"]["x"], chain_position["head"]["y"], chain_position["head"]["z"])
                        bone_chain.tail = (chain_position["tail"]["x"], chain_position["tail"]["y"], chain_position["tail"]["z"])
                    info_chains.append({ "name" : chain, "chain" : bone_chain})
                    if last_bone:
                        bone_chain.parent = last_bone
                        bone_chain.use_connect = True
                    last_bone = bone_chain
                if "ik_bones" in armatureConfig:
                    debugPrint("has ik_bones")
                    ik_bones = armatureConfig["ik_bones"]
                    debugPrint(len(ik_bones))
                    for y in range(len(ik_bones)):
                        ik_bone = ik_bones[y]
                        bone = self.getBoneChain(info_chains, ik_bone["connectTo"])
                        the_bone = bone["chain"]
                        new_ik_bone = armature.edit_bones.new(ik_bone["id"])
                        if "head" in ik_bone:
                            new_ik_bone.head = mathutils.Vector(((ik_bone["head"]["x"], ik_bone["head"]["y"], ik_bone["head"]["z"])))
                        else:
                            new_ik_bone.head = the_bone.tail
                            
                        if "tail" in ik_bone:
                            new_ik_bone.tail = mathutils.Vector(((ik_bone["tail"]["x"], ik_bone["tail"]["y"], ik_bone["tail"]["z"])))
                        else:
                            new_ik_bone.tail = the_bone.tail + mathutils.Vector((0,0,0.6))
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT') 
                        bpy.ops.object.mode_set(mode='POSE')       
                        the_bone.select_set(True)
                        the_bone = rig.pose.bones["bone.chain." + ik_bone["connectTo"]].bone
                        armature.bones.active = the_bone
                        bpy.ops.pose.constraint_add(type='IK')
                        self.context.selected_pose_bones[0].constraints["IK"].target = rig
                        self.context.selected_pose_bones[0].constraints["IK"].subtarget = ik_bone["id"]
                        if "chain_length" in ik_bone:
                            self.context.selected_pose_bones[0].constraints["IK"].chain_count = ik_bone["chain_length"]
                        bpy.ops.object.mode_set(mode='OBJECT')
                        self.presentation_target_bones.append({"pose_bone": rig.pose.bones[ik_bone["id"]], "armature":armature, "rig" : rig, "name": ik_bone["id"] })       

                #connect bones to targets
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                debugPrint("Object mode")
                for j in range(len(chains)):
                    chain = chains[j]
                    mdObj = self.getObjectByName(chain)
                    debugPrint("Deselect all objects")
                    bpy.ops.object.select_all(action='DESELECT')
                    debugPrint("Deselected all objects")
                    mdObj["object"].select_set(True)
                    mdObj["object"].location = bone_chains[j].head + rig.location
                    debugPrint("Pose mode")
                    if "forceFit" in armatureConfig and armatureConfig["forceFit"] == "True":
                        debugPrint("Force fit")
                        mdObj["object"].dimensions[0] = grid["x"]
                    bpy.ops.object.mode_set(mode='POSE')
                    armature.bones.active = rig.pose.bones["bone.chain." + chain].bone
                    debugPrint("setting parent to bone")
                    bpy.ops.object.parent_set(type='BONE')
                    debugPrint("deselecting")
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    mdObj["object"].select = False
                self.presentation_armatures.append({"bone_chains":bone_chains,"armature" : armature, "rig":rig, "configuration": armatureConfig})
                bpy.ops.object.mode_set(mode='OBJECT')
                
        
    def getBoneChain(self, bones, name):
        for k in range(len(bones)):
            bone  = bones[k]
            if bone["name"] == name:
                return bone
        return None

    def processKeyFrames(self, scene):
        debugPrint("process key frames")
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        keyframes = scene["keyframes"]
        for k in range(len(keyframes)):
            keyframe = keyframes[k]
            #self.setFrame(keyframe)
            self.setObjectsProperty(keyframe)
            debugPrint("finished setting properties")
    def processArmatureFrames(self, scene):
        debugPrint("process armature frames")
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        if "armatureframes" in scene:
            keyframes = scene["armatureframes"]
            for k in range(len(keyframes)):
                keyframe = keyframes[k]
                self.setArmatureObjectsProperties(keyframe)
    def processMaterialKeyFrames(self, scene):
        if "materialframes" in scene:
            materialframes = scene["materialframes"]
            for keyframe in materialframes:
                self.setMaterialObjectProperties(keyframe)
    def setObjectsProperty(self, keyframe):
        debugPrint("set objects property")
        objects = keyframe["objects"]
        for i in range(len(objects)):
            obj = self.getObjectByName(objects[i]["name"])
            if obj == 0:
                debugPrint("object not found, thats not good!")
            else :
                if ("frame" in keyframe):
                    debugPrint()
                else:
                    debugPrint("no frame in key frame ")
                    debugPrint(keyframe)
                self.setObjectProperty(obj, objects[i], keyframe["frame"])
                debugPrint("set object  properties")
    def setArmatureObjectsProperties(self, keyframe):
        debugPrint("set armature objects frames")
        objects = keyframe["objects"]
        
        for i in range(len(objects)):
            debugPrint("getting " + objects[i]["name"])
            obj = self.getBoneByName(objects[i]["name"])
            
            if obj == 0:
                debugPrint("bone not found, thats not good! " +  objects[i]["name"])
                # setArmatureObjectProperties
                debugPrint("get object by name : " + objects[i]["name"])
                obj = self.getObjectByName(objects[i]["name"])
                if obj == 0:
                    debugPrint("still cant find " + objects[i]["name"])
                else:
                    self.setObjectProperty(obj, objects[i], keyframe["frame"])
            else:
                debugPrint("found : " + objects[i]["name"])
                bpy.ops.object.mode_set(mode='OBJECT')
                debugPrint("set mode to object")
                bpy.ops.object.select_all(action='DESELECT')
                debugPrint("deselected")
                rig = obj["rig"]
                debugPrint("got rig")
                armature = obj["armature"]
                rig.select_set(True)
                bpy.ops.object.mode_set(mode='POSE')       
                the_bone = rig.pose.bones[obj["name"]].bone
                armature.bones.active = the_bone
                self.setArmatureObjectProperties({"object": rig.pose.bones[obj["name"]]}, objects[i], keyframe["frame"])
                debugPrint("set armature properties")
                bpy.ops.object.mode_set(mode='OBJECT')
    def getMaterialObject(self, name, material):
        debugPrint(self.presentation_material_animation_points)
        for mat_Target in self.presentation_material_animation_points:
            if mat_Target["name"] == name and mat_Target["material"] == material:
                return mat_Target
        return None
    def setupGroupComposites(self, groupComposites):
        debugPrint("setup group composites")
        groupsToSetup = []
        debugPrint("not done yet")
        for groupMaterial in groupComposites:
            groupsToSetup.append(groupMaterial["name"])
        
        debugPrint("appeded group composites")
        for groupMaterial in groupComposites:
            self.setupGroupComposite(groupMaterial)

        debugPrint("setup group composites")
        while len(groupsToSetup)>0:
            complete = True
            for groupMaterial in groupComposites:
                setup = self.fillInGroupMaterial(groupMaterial, "CompositorNodeGroup")
                if setup:
                    complete = False
                    debugPrint("updating groups to setup")
                    groupsToSetup = list(filter(lambda x: x != groupMaterial["name"], groupsToSetup))
            if complete:
                break
        debugPrint("done setting up group composites")
    def setupGroupMaterials(self, groupMaterials):
        debugPrint("setup group materials")
        groupsToSetup = []
        for groupMaterial in groupMaterials:
            groupsToSetup.append(groupMaterial["name"])
        
        for groupMaterial in groupMaterials:
            self.setupGroupMaterial(groupMaterial)
        
        while len(groupsToSetup)>0:
            complete = True
            for groupMaterial in groupMaterials:
                setup = self.fillInGroupMaterial(groupMaterial)
                if setup:
                    complete = False
                    debugPrint("updating groups to setup")
                    groupsToSetup = list(filter(lambda x: x != groupMaterial["name"], groupsToSetup))
            if complete:
                break
        debugPrint("done setting up group materials")
    def setupGroupComposite(self, groupComposite):
        node_group = None
        debugPrint("setup " + groupComposite["name"])
        if not self.groupCompositeExists(groupComposite["name"]):
            debugPrint("create a composite group")
            node_group = bpy.data.node_groups.new(groupComposite["name"], 'CompositorNodeTree')
            for node in groupComposite["definition"]["nodes"]:
                # create group nodes
                debugPrint("# create group nodes")
                debugPrint(node["id"])
                if  node["type"] == "NodeGroupOutput":
                    debugPrint("# create node outputs")
                    for _input in node["inputs"]:
                        debugPrint("create node out")
                        if _input["name"] != "":
                            node_group.outputs.new(_input["type"], _input["name"])
                    node_group.nodes.new(node["type"])
                if node["type"] == "NodeGroupInput":
                    debugPrint("# create node inputs")
                    for _output in node["outputs"]:
                        debugPrint("create node in")
                        if _output["name"] != "":
                            node_group.inputs.new(_output["type"], _output["name"])
                    node_group.nodes.new(node["type"])
    def setupGroupMaterial(self, groupMaterial):
        node_group = None
        debugPrint("setup  " + groupMaterial["name"])
        if not self.groupMaterialExists(groupMaterial["name"]):
            # create a group
            debugPrint("# create a group")
            node_group = bpy.data.node_groups.new(groupMaterial["name"], 'ShaderNodeTree')
            
            for node in groupMaterial["definition"]["nodes"]:
                # create group nodes
                debugPrint("# create group nodes")
                debugPrint(node["id"])
                if  node["type"] == "NodeGroupOutput":
                    debugPrint("# create node outputs")
                    for _input in node["inputs"]:
                        debugPrint("create node out")
                        if _input["name"] != "":
                            node_group.outputs.new(_input["type"], _input["name"])
                    node_group.nodes.new(node["type"])
                if node["type"] == "NodeGroupInput":
                    debugPrint("# create node inputs")
                    for _output in node["outputs"]:
                        debugPrint("create node in")
                        if _output["name"] != "":
                            node_group.inputs.new(_output["type"], _output["name"])
                    node_group.nodes.new(node["type"])

    def fillInGroupMaterial(self, groupMaterial, type = "ShaderNodeGroup"):
        if not self.allGroupsDependenciesExist(groupMaterial, type):
            return False
        node_group = bpy.data.node_groups[groupMaterial["name"]]

        debugPrint("setup  " + groupMaterial["name"])
        created_nodes = []
        debugPrint("node count " + str(len(groupMaterial["definition"]["nodes"])))
        attr_lst = [
            "use_variable_size", 
            "use_bokeh", 
            "use_gamma_correction", 
            "use_relative",
            "size_x",
            "size_y",
            "use_extended_bounds",
            "aspect_correction",
            "translation",
            "rotation",
            "scale",
            "use_min",
            "use_max",
            "min",
            "max",
            "vector_type",
            "factor_x",
            "factor_y",
            "use_clamp"
            ]
        for node in groupMaterial["definition"]["nodes"]:
            debugPrint(node["type"])
            if node["type"] == "NodeGroupInput":
                debugPrint("Found input group")
            # create group nodes
            if node["type"] == "NodeGroupInput" or node["type"] == "NodeGroupOutput":
                found = False
                for t in node_group.nodes:
                    if t.bl_idname == node["type"]:
                        found = True
                        created_nodes.append(t)
                        new_node = t
                        break
                if not found:
                    raise ValueError("Didnt find the node group Input or output that should be here")
                else:
                    debugPrint("found " + node["type"])
                debugPrint(node["type"] + " looking for node  " + str(node["id"]) + " in " + str(len(created_nodes)) + " nodes ")
                if created_nodes[node["id"]] != new_node:
                    raise ValueError("Node is not in the expected order.")
                continue

            debugPrint("# create group nodes")
            node_group = bpy.data.node_groups[groupMaterial["name"]]
            new_node = node_group.nodes.new(node["type"])
            for al in range(len(attr_lst)):
                ali = attr_lst[al]
                if ali in node:
                    debugPrint("setting "+ ali + " on node")
                    typename = None
                    tmp = None                    
                    try:
                        if "type" in node[ali] and "value" in node[ali]:
                            typename = node[ali]["type"]
                            tmp = node[ali]["value"]
                            debugPrint(tmp)
                    except Exception as e:
                        debugPrint("simple value")

                    if typename == "Vector":
                        debugPrint("setting  new_node with Vector")
                        setattr(new_node, ali, mathutils.Vector(tmp))
                    elif typename == "Euler":
                        debugPrint("setting  new_node with Euler")
                        setattr(new_node, ali, mathutils.Euler((tmp["x"], tmp["y"], tmp["z"]), tmp["order"] ))
                    else:
                        debugPrint("setting new_node with setattr")
                        debugPrint(typename)
                        setattr(new_node, ali, node[ali])
            if node["type"] == "ShaderNodeGroup":
                debugPrint("node_name " + node["node_name"])
                debugPrint("create_nodes : " + str(len(created_nodes)))
                new_node.node_tree = bpy.data.node_groups[node["node_name"]]
                debugPrint("create_nodes : " + str(len(created_nodes)))
            if "location" in node:
                debugPrint("# set node location")
                new_node.location = (node["location"]["x"], node["location"]["y"])
                debugPrint("create_nodes : " + str(len(created_nodes)))
            if "operation" in node:
                debugPrint("# set operation")
                new_node.operation = node["operation"]
            if "use_clamp" in node:
                debugPrint("# set use_clamp")
                new_node.use_clamp = node["use_clamp"]
            if "invert" in node:
                debugPrint("# set invert")
                new_node.invert = node["invert"]
            if "blend_type" in node:
                debugPrint("# set blend type")
                new_node.blend_type = node["blend_type"]
            if "operation" in node:
                new_node.operation = node["operation"]
            if "distribution" in node:
                new_node.distribution = node["distribution"]
            if "musgrave_type" in node:
                new_node.musgrave_type = node["musgrave_type"]
            if "filter_type" in node:
                new_node.filter_type = node["filter_type"]
            if "gradient_type" in node:
                new_node.gradient_type = node["gradient_type"]
            if "coloring" in node:
                new_node.coloring = node["coloring"]
            if "feature" in node:
                new_node.feature = node["feature"]
            if "projection" in node:
                new_node.projection = node["projection"]
            if "interpolation" in node:
                new_node.interpolation = node["interpolation"]
            if "source" in node:
                new_node.source = node["source"]
            if "color_space" in node:
                new_node.color_space = node["color_space"]
            if "image" in node:
                if not self.hasImage(node["image"]["name"]):
                    bpy.data.images.load(filepath=node["image"]["filepath"])
                new_node.image = bpy.data.images[node["image"]["name"]]
            if "color_ramp" in node:
                color_ramp = node["color_ramp"]
                if "color_mode" in color_ramp:
                    debugPrint("setting color_mode")
                    new_node.color_ramp.color_mode = color_ramp["color_mode"]
                if "hue_interpolation" in color_ramp:
                    debugPrint("setting hue_interpolation")
                    new_node.color_ramp.hue_interpolation = color_ramp["hue_interpolation"]
                if "interpolation" in color_ramp:
                    debugPrint("setting interpolation")
                    new_node.color_ramp.interpolation = color_ramp["interpolation"]
                if "elements" in color_ramp:
                    debugPrint("setting elements")
                    elements = color_ramp["elements"]
                    for i in range(len(new_node.color_ramp.elements)-1):
                        debugPrint("removing existing")
                        debugPrint(str(i))
                        new_node.color_ramp.elements.remove(new_node.color_ramp.elements[0])
                        debugPrint("removed existing")
                    existing = len(new_node.color_ramp.elements)
                    for i in range(len(elements) - existing):
                        debugPrint("creating new")
                        new_node.color_ramp.elements.new(elements[i]["position"])
                    for i in range(len(elements)):
                        debugPrint("setting position")
                        new_node.color_ramp.elements[i].position = (elements[i]["position"])
                    for i in range(len(elements)):
                        debugPrint("setting element color")
                        new_node.color_ramp.elements[i].color[0] = elements[i]["color"][0]
                        new_node.color_ramp.elements[i].color[1] = elements[i]["color"][1]
                        new_node.color_ramp.elements[i].color[2] = elements[i]["color"][2]
                        new_node.color_ramp.elements[i].color[3] = elements[i]["color"][3]

            if node["type"] != "NodeReroute":
                for n_i in node["inputs"]:
                    if "default_value" in n_i:
                        debugPrint("setting default value for " + n_i["type"])
                        if n_i["type"] == "NodeSocketVector":
                            vector = n_i["default_value"]
                            new_node.inputs[n_i["socket_index"]]['0'] = vector[0]
                            new_node.inputs[n_i["socket_index"]]['1'] = vector[1]
                            new_node.inputs[n_i["socket_index"]]['2'] = vector[2]
                        else:
                            new_node.inputs[n_i["socket_index"]].default_value = n_i["default_value"]
                for n_i in node["outputs"]:
                    if "default_value" in n_i:
                        debugPrint("setting default value for " + n_i["type"])
                        if n_i["type"] == "NodeSocketVector":
                            vector = n_i["default_value"]
                            new_node.outputs[n_i["socket_index"]]['0'] = vector[0]
                            new_node.outputs[n_i["socket_index"]]['1'] = vector[1]
                            new_node.outputs[n_i["socket_index"]]['2'] = vector[2]
                        else:
                            new_node.outputs[n_i["socket_index"]].default_value = n_i["default_value"]

            debugPrint("appending new_node")
            debugPrint("create_nodes : " + str(len(created_nodes)))
            created_nodes.append(new_node)
            debugPrint("create_nodes : " + str(len(created_nodes)))
            debugPrint("looking for node  " + str(node["id"]) + " in " + str(len(created_nodes)) + " nodes ")
            if created_nodes[node["id"]] != new_node:
                raise ValueError("Node is not in the expected order.")    
            

        for link in groupMaterial["definition"]["links"]:
            from_node = created_nodes[link["from"]]
            to_node = created_nodes[link["to"]]
            debugPrint("create link")
            debugPrint("from node " + str(link["from"]))
            debugPrint(link["from_socket"]["name"])
            debugPrint(from_node.name)
            if hasattr(from_node, "node_tree"):
                debugPrint("from_node " + from_node.node_tree.name)

            debugPrint("to node " + str(link["to"]))
            debugPrint(link["to_socket"]["name"])
            debugPrint(to_node.name)
            if hasattr(to_node, "node_tree"):
                debugPrint("to_node " + to_node.node_tree.name)
            node_group.links.new(from_node.outputs[link["from_socket"]["socket_index"]], to_node.inputs[link["to_socket"]["socket_index"]])
        debugPrint("setting up default inputs")
        if "defaultInputs" in groupMaterial["definition"]:
            debugPrint("has default inputs")
            for defaultInput in groupMaterial["definition"]["defaultInputs"]:
                if "default_value" in defaultInput and defaultInput["default_value"] != None:
                    debugPrint("has default input value")
                    debugPrint(defaultInput["type"])
                    if defaultInput["type"] == "NodeSocketColor":
                        debugPrint("setting default vector input")
                        vector = defaultInput["default_value"]
                        node_group.inputs[defaultInput["socket_index"]].default_value = vector
                    if defaultInput["type"] == "NodeSocketVector":
                        debugPrint("setting default vector input")
                        vector = defaultInput["default_value"]
                        node_group.inputs[defaultInput["socket_index"]]['0'] = vector[0]
                        node_group.inputs[defaultInput["socket_index"]]['1'] = vector[1]
                        node_group.inputs[defaultInput["socket_index"]]['2'] = vector[2]
                    elif defaultInput["type"] == "NodeSocketFloat":
                        debugPrint("setting default input")
                        debugPrint(defaultInput["name"])
                        debugPrint(str(defaultInput["default_value"]))
                        try:
                            node_group.inputs[defaultInput["socket_index"]].default_value = defaultInput["default_value"]
                        except Exception as e:
                            try:
                                node_group.inputs[defaultInput["socket_index"]].default_value = (defaultInput["default_value"], defaultInput["default_value"], defaultInput["default_value"])
                            except Exception as e:
                                node_group.inputs[defaultInput["socket_index"]].default_value = (defaultInput["default_value"],  defaultInput["default_value"], defaultInput["default_value"], defaultInput["default_value"])
                    else:
                        debugPrint("setting default input")
                        debugPrint(defaultInput["name"])
                        node_group.inputs[defaultInput["socket_index"]].default_value = defaultInput["default_value"]

        debugPrint("-------------- created new group ----------------")
        return True
        
    def allGroupsDependenciesExist(self, groupMaterial, nodeType = "ShaderNodeGroup"):
        missing = False
        debugPrint("missing dependency for")
        if groupMaterial != None:
            nodes = groupMaterial["definition"]["nodes"]
            for node in nodes:
                if node["type"] == nodeType:
                    if not self.groupMaterialExists(groupMaterial["name"]):
                        debugPrint(groupMaterial["name"])
                        missing = True

        if missing:
            return False
        return True


    def groupMaterialExists(self, groupMaterial):
        return groupMaterial in bpy.data.node_groups
    def groupCompositeExists(self, groupComposite):
        return groupComposite in bpy.data.node_groups
    def setMaterialObjectProperties(self, keyframe):
        objects = keyframe["objects"] 
        for _obj in objects:
            obj = self.getMaterialObject(_obj["name"], _obj["material"])
            if obj == None:
                raise ValueError("material not found")
            mat_node = obj["node"]
            mat_node_input = mat_node.inputs[obj["index"]]
            setattr(mat_node_input, "default_value", _obj["value"])
            mat_node_input.keyframe_insert(data_path="default_value",frame=keyframe["frame"])
                    
    def parentCreatedObjects(self, scene):
        debugPrint("Parent created objects")
        # for i in range(len(self.scenes)):
        debugPrint("scene parent ")
        #       objs = self.scenes[i]["objects"]
        objs = scene["objects"]
        for j in range(len(objs)):
            obj = objs[j]
            debugPrint("scene parent  > OBJECTS")
            debugPrint("here")
            debugPrint(obj)
            createdObject = self.getObjectByName(obj["name"])
            debugPrint("got created object")
            if "parent" in obj:
                debugPrint("has a parent : " + obj["parent"])
            if createdObject and "parent" in obj:
                parentObj = self.getObjectByName(obj["parent"])
                if parentObj:
                    self.parentObject(parentObj, createdObject)

    def parentObject(self, b, a):
        debugPrint("Parent object a to b")
        a["object"].parent = b["object"]
        #bpy.ops.object.select_all(action='DESELECT')
        #a["object"].select = True
        #b["object"].select = True
        #bpy.context.context.active_object = a["object"]
        #bpy.ops.object.parent_set()
    def deselectAll(self):
        debugPrint("object mode")
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = None
    def setArmatureObjectProperties(self, obj, config, frame):
        debugPrint("setting armature object properties")
        if "position" in config and config["position"]:
            position = config["position"]
            debugPrint("setting armture object position")
            self.translation(obj, position, True, frame)
        if "scale" in config and config["scale"]:
            scale = config["scale"]
            debugPrint("setting armture object scale")
            self.scale(obj, scale, True, frame)
        if "rotation" in config and config["rotation"]:
            rotation = config["rotation"]
            debugPrint("setting armture object rotation")
            self.rotation(obj, rotation , True, frame)
        
    def setObjectProperty(self, obj, config, frame):
        debugPrint(obj)
        debugPrint("obj type : " + obj["type"])
        debugPrint(type(obj["object"]))
        if "position" in config:
            pos = config["position"]
            if "x" in pos:
                obj["object"].location.x = float(pos["x"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=0)
            if "y" in pos:
                obj["object"].location.y = float(pos["y"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=1)
            if "z" in pos:
                obj["object"].location.z = float(pos["z"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=2)
   
        if "scale" in config and config["scale"]: 
            scale = config["scale"] 
            if "x" in scale:
                obj["object"].scale.x = scale["x"]
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                
            if "y" in scale:
                obj["object"].scale.y = float(scale["y"])
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                
            if "z" in scale:
                obj["object"].scale.z = float(scale["z"])
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)
        if "position_rel" in config and config["position_rel"]:
            debugPrint("position relative to ")
            target = config["position_rel"]["target"]
            target_obj = self.getObjectByName(target)
            distance = 7
            if "distance" in config["position_rel"]:
                distance = config["position_rel"]["distance"]
            if "offset" in config["position_rel"]:
                offset = config["position_rel"]["offset"]
            else :
                offset = {"x":0,"y":0,"z":0}
            if config["position_rel"]["position"] == "front":
                debugPrint("matrix world to euler")
                direction = target_obj["object"].matrix_world.to_euler()
                direction = mathutils.Vector(direction)
                direction.normalize()
                debugPrint("direction normalized")
                debugPrint(direction)
                
                location = target_obj["object"].matrix_world * mathutils.Vector((0,-distance ,0)) #target_obj["object"].matrix_world.translation
                
                t = location #+ (7 * direction)
                obj["object"].location.x = t[0] + offset["x"]
                obj["object"].location.y = t[1] + offset["y"]
                obj["object"].location.z = t[2] + offset["z"]
                debugPrint("Set location")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
                debugPrint("set keyframe ")
            elif config["position_rel"]["position"] == "top":
                debugPrint("location + dimension")
                l = target_obj["object"].matrix_world * mathutils.Vector((0,0,distance)) 
                obj["object"].location.x = l[0] + offset["x"]
                obj["object"].location.y = l[1] + offset["y"]
                obj["object"].location.z = l[2] + offset["z"]
                debugPrint("insert key frame")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
            elif config["position_rel"]["position"] == "center":
                debugPrint("location + dimension")
                l = target_obj["object"].matrix_world.translation
                obj["object"].location.x = l[0] 
                obj["object"].location.y = l[1] 
                obj["object"].location.z = l[2]
                debugPrint("insert key frame")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
            
        if "children" in config :
            debugPrint("children")        
            for childConfig in config["children"]:
                debugPrint("Value : %s" % obj.keys())
                if "name" in childConfig:
                    name = childConfig["name"]
                    selectedObj = self.selectObject(obj["object"].children, name)
                    debugPrint("attempted object")
                    if selectedObj != None:
                        tempObject = {}
                        tempObject["object"] = selectedObj
                        debugPrint("got an object")
                        self.applyConfig(tempObject, childConfig, frame)

        if "target" in config and config["target"]: 
            debugPrint("track target")
            target = config["target"]
            target_obj = self.getObjectByName(target)
            debugPrint("target_obj")
            debugPrint(target)
            bpy.ops.object.select_all(action='DESELECT')
            obj["object"].select_set(True)
            # bpy.context.scene.objects.active = obj["object"]
            debugPrint("adding constraint")
            constraint = obj["object"].constraints.new(type='TRACK_TO')
            debugPrint("adding constraint")
            constraint.target = target_obj["object"]
            constraint.track_axis = "TRACK_NEGATIVE_Z"
            constraint.up_axis = "UP_Y"
            debugPrint("added constraints")
            
        if "rotation" in config and config["rotation"]: 
            rotation = config["rotation"] 
            self.rotation(obj, rotation, True, frame)

        if "scale" in config and config["scale"]:
            scale = config["scale"]
            self.scale(obj, scale, True, frame)
        if config:
            self.applyConfig(obj, config, frame)
            
    def applyConfig(self, tempObject, childConfig, frame):
        debugPrint("-----------------------")
        debugPrint("apply config")

        debugPrint("------------animate vertices -------------")
        if "vertex_animation" in childConfig:
            self.animateVertices(tempObject, childConfig["vertex_animation"], True, frame)
        debugPrint("------------rotation-----------")
        if "rotation" in childConfig:
            self.rotation(tempObject , childConfig["rotation"],True,frame)
        
        debugPrint("------------scale-----------")
        if "scale" in childConfig:
            self.scale(tempObject , childConfig["scale"],True,frame)
        debugPrint("----------translate-------------")
        if "translate" in childConfig:
            self.translation(tempObject , childConfig["translate"],True,frame)
        
        debugPrint("----------particles-------------")
        if "particles" in childConfig:
            self.particles(tempObject, childConfig["particles"], True, frame)
            
        debugPrint("----------dynamic paint-------------")
        if "dynamic_paint" in childConfig:
            self.dynamic_paint(tempObject, childConfig["dynamic_paint"], True, frame)
        debugPrint("----------dynamic brush-------------")
        if "dynamic_brush" in childConfig:
            self.dynamic_brush(tempObject, childConfig["dynamic_brush"], True, frame)
        debugPrint("----------collision-------------")
        if "collision" in childConfig:
            self.collision(tempObject, childConfig["collision"], True, frame)
        debugPrint("----------follow path-------------")
        if "follow_path" in childConfig:
            self.follow_path(tempObject, childConfig["follow_path"], True , frame)
        debugPrint("----------track to-------------")
        if "track_to" in childConfig:
            self.track_to(tempObject, childConfig["track_to"], True, frame)
        if "ortho_scale" in childConfig:
            tempObject["object"].data.ortho_scale  = float(childConfig["ortho_scale"])
            tempObject["object"].data.keyframe_insert(data_path="ortho_scale", frame=frame)
        debugPrint("----------limit rotation-------------")
        if "limit_rotation" in childConfig:
            self.limit_rotation(tempObject, childConfig["limit_rotation"], True, frame)
        if "lens" in childConfig:
            tempObject["object"].data.lens  = float(childConfig["lens"])
            tempObject["object"].data.keyframe_insert(data_path="lens", frame=frame)
        if "sensor_width" in childConfig:
            tempObject["object"].data.sensor_width  = float(childConfig["sensor_width"])
            tempObject["object"].data.keyframe_insert(data_path="sensor_width", frame=frame)
        if "dof_object" in childConfig:
            target = self.getObjectByName(childConfig["dof_object"])
            if target != None:
                tempObject["object"].data.dof_object = target["object"]
        if "gpu_dof" in childConfig:
            gpu_dof = childConfig["gpu_dof"]
            if "fstop" in gpu_dof:
                tempObject["object"].data.gpu_dof.fstop = gpu_dof["fstop"]
            if "fstop_anim" in gpu_dof:
                tempObject["object"].data.gpu_dof.keyframe_insert(data_path="fstop", frame=frame)
            if "use_high_quality" in gpu_dof:
                tempObject["object"].data.gpu_dof.use_high_quality = gpu_dof["use_high_quality"]
        if "materialConfig" in childConfig:
            self.setupMaterial(tempObject["object"], childConfig["materialConfig"])
        if self.isCycles():
            if "cycles" in childConfig:
                cycles = childConfig["cycles"]
                if "aperture_type" in cycles:
                    tempObject["object"].data.cycles.aperture_type = cycles["aperture_type"]
                if "aperture_size" in cycles:
                    tempObject["object"].data.cycles.aperture_size = cycles["aperture_size"]
                if "aperture_size_anim" in cycles:
                    tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_size", frame=frame)
                if "aperture_fstop" in cycles:
                    tempObject["object"].data.cycles.aperture_fstop = cycles["aperture_fstop"]
                if "aperture_fstop_anim" in cycles:
                    tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_fstop", frame=frame)
                if "aperture_blades" in cycles:
                    tempObject["object"].data.cycles.aperture_blades = cycles["aperture_blades"]
                if "aperture_blades_anim" in cycles:
                    tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_blades", frame=frame)
                if "aperture_rotation" in cycles:
                    tempObject["object"].data.cycles.aperture_rotation = cycles["aperture_rotation"]
                if "aperture_rotation_anim" in cycles:
                    tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_rotation", frame=frame)
                if "aperture_ratio" in cycles:
                    tempObject["object"].data.cycles.aperture_ratio = cycles["aperture_ratio"]
                if "aperture_ratio_anim" in cycles:
                    tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_ratio", frame=frame)
        debugPrint("-======completed applying config====-")
    def setupMaterial(self, obj, config):
        debugPrint("setting up material for object")
        material = self.getMaterialByName(config["name"])
        if not material:
            material = self.buildMaterial(config)
        obj.data.materials.clear()
        obj.data.materials.append(material)

    def setMaterialProperties(self, material, config):
        if "blend_method" in config:
            material.blend_method = config["blend_method"]
    def buildMaterial(self, config, material = None, parentInput = None):
        debugPrint("build material")
        if material == None:
            # Create a new material
            material = bpy.data.materials.new(name=config["name"])
            material.use_nodes = True
            # Remove default
            count = len(material.node_tree.nodes)
            for i in range(count):
                material.node_tree.nodes.remove(material.node_tree.nodes[0])
        
        self.setMaterialProperties(material, config)
        type_config = config["type"]
        if type_config == SHADER_OUTPUT_MATERIAL:
            self.buildShaderOutputMaterial(config, material)
        elif type_config == SHADER_EMISSION:
            self.buildShaderEmission(config, material, parentInput)
        elif type_config == SHADER_MIX_RGB:
            self.buildShaderMixRGB(config, material, parentInput)
        elif type_config == SHADER_NODE_VALUE:
            self.buildShaderNodeValue(config, material, parentInput)
        elif type_config == SHADER_NODE_MIX:
            self.buildShaderNodeMix(config, material , parentInput)
        elif type_config == SHADER_NODE_DIFFUSE:
            self.builderShaderNodeDiffuse(config, material, parentInput)
        elif type_config == SHADER_WORLD_NODE_OUTPUT:
            self.buildShaderWorldNodeOutput(config, material)
        elif type_config == SHADER_NODE_BACKGROUND:
            self.buildShaderNodeBackground(config, material, parentInput)
        elif type_config == COMPOSITOR_NODE_COMPOSITE:
            self.buildCompositorNodeComposite(config, material, parentInput)
        elif type_config == "CUSTOM":
            self.buildCustomShaderNode(config, material, parentInput)
        elif type_config == "CUSTOM_COMPOSITE":
            self.buildCustomCompositorNode(config, material, parentInput)
        else:
            self.buildUnknownNode(config, material, parentInput)
        return material
    def buildUnknownNode(self, config, material, parentInput = None):
        
        createfunc = lambda _ : material.node_tree.nodes.new(config["type"])
        
        new_node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        
        self.ascribeNameLable(config, new_node)
        
        if "outputs" in config:
            for output in config["outputs"]:
                index = output["index"]
                path_ = output["path"]
                type_ = output["type"]
                if "default_value" in output:
                    value_ = output["default_value"]
                    setattr(new_node.outputs[index], path_, value_)
                    debugPrint("default value was found and set in the output")
                if "value" in output:
                    value_ = output["value"]
                    setattr(new_node.outputs[index], path_, value_)
                    debugPrint("value was found and set in the output")
                else:
                    debugPrint("value was not found in the outputs configuration")
                material.node_tree.links.new(parentInput, new_node.outputs[index])

    def buildShaderOutputMaterial(self, config, material):
        node = material.node_tree.nodes.new(SHADER_OUTPUT_MATERIAL)
        self.buildMaterial(config["surface"], material, node.inputs[0])
        self.setNodeLocation(node, config)

    def setNodeLocation(self, node, config):
        if "location" in config:
            debugPrint("# set node location")
            node.location = (config["location"]["x"], config["location"]["y"])

    def ascribeNameLable(self, config , node):
        if "name" in config:
            node.name = config["name"]
            node.label = config["name"]
        
        self.setNodeLocation(node, config)

    def buildCustomCompositorNode(self, config , material, parentInput = None):
        
        debugPrint("creating compositor node group")
        debugPrint("setting node group")
        debugPrint(config["custom"]["name"])
        debugPrint(material)
        created_nodes = self.buildCustomNodeTree(config["custom"], material.node_tree)
        if "conversion" in config["custom"]:
            conversion = config["custom"]["conversion"]
            for key in conversion:
                debugPrint("found " + key + " in conversion")
                if key in config["custom"]:
                    debugPrint("found " + key + " in config")
                    node_index = conversion[key]["node_index"]
                    socket_index = conversion[key]["socket_index"]
                    debugPrint("building material for conversion")
                    self.buildMaterial(config["custom"][key], material, created_nodes[node_index].inputs[socket_index])

    def buildCustomNodeTree(self, groupMaterial, node_group, type = "CompositorNodeGroup"):
        debugPrint("setup  " + groupMaterial["name"])
        created_nodes = []
        debugPrint("node count " + str(len(groupMaterial["definition"]["nodes"])))
        attr_lst = [
            "use_variable_size", 
            "use_bokeh", 
            "use_gamma_correction", 
            "use_relative",
            "size_x",
            "size_y",
            "use_extended_bounds",
            "aspect_correction",
            "translation",
            "rotation",
            "scale",
            "use_min",
            "use_max",
            "min",
            "max",
            "vector_type",
            "factor_x",
            "factor_y",
            "use_clamp"
            ]
        for node in groupMaterial["definition"]["nodes"]:
            debugPrint(node["type"])
            debugPrint("# create custom nodes")
            new_node = node_group.nodes.new(node["type"])
            if "location" in node:
                debugPrint("# set node location")
                new_node.location = (node["location"]["x"], node["location"]["y"])
                debugPrint("create_nodes : " + str(len(created_nodes)))
                debugPrint(new_node.location)
            for al in range(len(attr_lst)):
                ali = attr_lst[al]
                if ali in node:
                    debugPrint("setting "+ ali + " on node")
                    typename = None
                    tmp = None
                    try:
                        if "type" in node[ali] and "value" in node[ali]:
                            typename = node[ali]["type"]
                            tmp = node[ali]["value"]
                            debugPrint(tmp)
                    except Exception as e:
                            debugPrint("simple value")
                    if typename == "Vector":
                        debugPrint("setting  new_node with Vector")
                        setattr(new_node, ali, mathutils.Vector(tmp))
                    elif typename == "Euler":
                        debugPrint("setting  new_node with Euler")
                        setattr(new_node, ali, mathutils.Euler((tmp["x"], tmp["y"], tmp["z"]), tmp["order"] ))
                    else:
                        debugPrint("setting new_node with setattr")
                        debugPrint(typename)
                        setattr(new_node, ali, node[ali])
            if "operation" in node:
                debugPrint("# set operation")
                new_node.operation = node["operation"]
            if "use_clamp" in node:
                debugPrint("# set use_clamp")
                new_node.use_clamp = node["use_clamp"]
            if "invert" in node:
                debugPrint("# set invert")
                new_node.invert = node["invert"]
            if "blend_type" in node:
                debugPrint("# set blend type")
                new_node.blend_type = node["blend_type"]
            if "operation" in node:
                new_node.operation = node["operation"]
            if "distribution" in node:
                new_node.distribution = node["distribution"]
            if "musgrave_type" in node:
                new_node.musgrave_type = node["musgrave_type"]
            if "filter_type" in node:
                new_node.filter_type = node["filter_type"]
            if "gradient_type" in node:
                new_node.gradient_type = node["gradient_type"]
            if "coloring" in node:
                new_node.coloring = node["coloring"]
            if "feature" in node:
                new_node.feature = node["feature"]
            if "projection" in node:
                new_node.projection = node["projection"]
            if "interpolation" in node:
                new_node.interpolation = node["interpolation"]
            if "source" in node:
                new_node.source = node["source"]
            if "color_space" in node:
                new_node.color_space = node["color_space"]
            if "image" in node:
                if not self.hasImage(node["image"]["name"]):
                    bpy.data.images.load(filepath=node["image"]["filepath"])
                new_node.image = bpy.data.images[node["image"]["name"]]
            if "color_ramp" in node:
                color_ramp = node["color_ramp"]
                if "color_mode" in color_ramp:
                    debugPrint("setting color_mode")
                    new_node.color_ramp.color_mode = color_ramp["color_mode"]
                if "hue_interpolation" in color_ramp:
                    debugPrint("setting hue_interpolation")
                    new_node.color_ramp.hue_interpolation = color_ramp["hue_interpolation"]
                if "interpolation" in color_ramp:
                    debugPrint("setting interpolation")
                    new_node.color_ramp.interpolation = color_ramp["interpolation"]
                if "elements" in color_ramp:
                    debugPrint("setting elements")
                    elements = color_ramp["elements"]
                    for i in range(len(new_node.color_ramp.elements)-1):
                        debugPrint("removing existing")
                        debugPrint(str(i))
                        new_node.color_ramp.elements.remove(new_node.color_ramp.elements[0])
                        debugPrint("removed existing")
                    existing = len(new_node.color_ramp.elements)
                    for i in range(len(elements) - existing):
                        debugPrint("creating new")
                        new_node.color_ramp.elements.new(elements[i]["position"])
                    for i in range(len(elements)):
                        debugPrint("setting position")
                        new_node.color_ramp.elements[i].position = (elements[i]["position"])
                    for i in range(len(elements)):
                        debugPrint("setting element color")
                        new_node.color_ramp.elements[i].color[0] = elements[i]["color"][0]
                        new_node.color_ramp.elements[i].color[1] = elements[i]["color"][1]
                        new_node.color_ramp.elements[i].color[2] = elements[i]["color"][2]
                        new_node.color_ramp.elements[i].color[3] = elements[i]["color"][3]

            if node["type"] != "NodeReroute":
                for n_i in node["inputs"]:
                    if  hasattr(n_i, "default_value"):
                        debugPrint("setting input default value for " + n_i["type"])
                        if n_i["type"] == "NodeSocketVector":
                            vector = n_i["default_value"]
                            new_node.inputs[n_i["socket_index"]]['0'] = vector[0]
                            new_node.inputs[n_i["socket_index"]]['1'] = vector[1]
                            new_node.inputs[n_i["socket_index"]]['2'] = vector[2]
                        else:
                            new_node.inputs[n_i["socket_index"]].default_value = n_i["default_value"]
                for n_i in node["outputs"]:
                    if hasattr(n_i, "default_value"):
                        debugPrint("setting output default value for " + n_i["type"])
                        if n_i["type"] == "NodeSocketVector":
                            vector = n_i["default_value"]
                            new_node.outputs[n_i["socket_index"]]['0'] = vector[0]
                            new_node.outputs[n_i["socket_index"]]['1'] = vector[1]
                            new_node.outputs[n_i["socket_index"]]['2'] = vector[2]
                        else:
                            new_node.outputs[n_i["socket_index"]].default_value = n_i["default_value"]

            debugPrint("appending new_node")
            debugPrint("create_nodes : " + str(len(created_nodes)))
            created_nodes.append(new_node)
            debugPrint("create_nodes : " + str(len(created_nodes)))
            debugPrint("looking for node  " + str(node["id"]) + " in " + str(len(created_nodes)) + " nodes ")
            if created_nodes[node["id"]] != new_node:
                raise ValueError("Node is not in the expected order.")    
            

        for link in groupMaterial["definition"]["links"]:
            from_node = created_nodes[link["from"]]
            to_node = created_nodes[link["to"]]
            debugPrint("create link")
            debugPrint("from node " + str(link["from"]))
            debugPrint(link["from_socket"]["name"])
            debugPrint(from_node.name)
            if hasattr(from_node, "node_tree"):
                debugPrint("from_node " + from_node.node_tree.name)

            debugPrint("to node " + str(link["to"]))
            debugPrint(link["to_socket"]["name"])
            debugPrint(to_node.name)
            if hasattr(to_node, "node_tree"):
                debugPrint("to_node " + to_node.node_tree.name)
            node_group.links.new(from_node.outputs[link["from_socket"]["socket_index"]], to_node.inputs[link["to_socket"]["socket_index"]])

        debugPrint("setting up default inputs")
        if "defaultInputs" in groupMaterial["definition"]:
            debugPrint("has default inputs")
            for defaultInput in groupMaterial["definition"]["defaultInputs"]:
                if "default_value" in defaultInput and defaultInput["default_value"] != None:
                    debugPrint("has default input value")
                    debugPrint(defaultInput["type"])
                    _node_group = created_nodes[defaultInput["node_index"]]
                    if defaultInput["type"] == "NodeSocketColor":
                        debugPrint("setting default vector input")
                        vector = defaultInput["default_value"]
                        _node_group.inputs[defaultInput["socket_index"]].default_value = vector
                    if defaultInput["type"] == "NodeSocketVector":
                        debugPrint("setting default vector input")
                        vector = defaultInput["default_value"]
                        _node_group.inputs[defaultInput["socket_index"]]['0'] = vector[0]
                        _node_group.inputs[defaultInput["socket_index"]]['1'] = vector[1]
                        _node_group.inputs[defaultInput["socket_index"]]['2'] = vector[2]
                    elif defaultInput["type"] == "NodeSocketFloat":
                        debugPrint("setting default input")
                        debugPrint(defaultInput["name"])
                        debugPrint(str(defaultInput["default_value"]))
                        debugPrint("socket_index")
                        debugPrint(defaultInput["socket_index"])
                        try:
                            _node_group.inputs[defaultInput["socket_index"]].default_value = defaultInput["default_value"]
                        except Exception as e:
                            try:
                                _node_group.inputs[defaultInput["socket_index"]].default_value = (defaultInput["default_value"], defaultInput["default_value"], defaultInput["default_value"])
                            except Exception as e:
                                _node_group.inputs[defaultInput["socket_index"]].default_value = (defaultInput["default_value"],  defaultInput["default_value"], defaultInput["default_value"], defaultInput["default_value"])
                    else:
                        debugPrint("setting default input")
                        debugPrint(defaultInput["name"])
                        debugPrint("socket_index")
                        debugPrint(defaultInput["socket_index"])
                        _node_group.inputs[defaultInput["socket_index"]].default_value = defaultInput["default_value"]

        debugPrint("-------------- created new custom node tree ----------------")
        return created_nodes
    def existingMaterialNode(self, nodes , config, lambdfunc = None):
        if "name" in config:
            for i in range(len(nodes)):
                if nodes[i].name == config["name"]:
                    return nodes[i]
        if lambdfunc != None: 
            return lambdfunc(True)
        return False

    def buildCustomShaderNode(self, config , material, parentInput = None):
        debugPrint("creating shader node group")
        node = self.existingMaterialNode(material.node_tree.nodes, config, lambda x : material.node_tree.nodes.new("ShaderNodeGroup"))
        self.ascribeNameLable(config, node)
        
        debugPrint("setting node group")
        debugPrint(config["custom"]["name"])
        node.node_tree = bpy.data.node_groups[config["custom"]["name"]]
        debugPrint("set node_tree")
        custom = config["custom"]
        if parentInput != None:
            if "$output" in custom:
                debugPrint("create new link")
                material.node_tree.links.new(parentInput, node.outputs[custom["$output"]])
        debugPrint("adding conversion")
        if "conversion" in custom:
            for key in custom["conversion"]:
                if key in custom  and custom[key] != None:
                    debugPrint("building material connections")
                    debugPrint("key : " + key)
                    debugPrint(str(custom["conversion"][key]))
                    
                    input_key = custom["conversion"][key]
                    if not isinstance(input_key, numbers.Number):
                        input_key = input_key["input_index"]
                    debugPrint(custom[key])
                    self.buildMaterial(custom[key], material, node.inputs[input_key])

    def buildShaderNodeMix(self, config ,material , parentInput = None):
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_NODE_MIX)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        
        if parentInput != None:
            material.node_tree.links.new(parentInput, node.outputs[0])

        if "factor" in config:
            self.buildMaterial(config["factor"], material, node.inputs[0])
        if "input1" in config:
            self.buildMaterial(config["input1"], material, node.inputs[1])
        if "input2" in config:
            self.buildMaterial(config["input2"], material, node.inputs[2])

    def buildShaderWorldNodeOutput(self, config, material):
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_WORLD_NODE_OUTPUT)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        
        self.buildMaterial(config["surface"], material, node.inputs['Surface'])

    def buildCompositorNodeComposite(self, config, material, parentInput):
        debugPrint(material)
        debugPrint(material.node_tree)
        createfunc = lambda x : material.node_tree.nodes.new(COMPOSITOR_NODE_COMPOSITE)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        
        if "image" in config:
            debugPrint("connecting image")
            self.buildMaterial(config["image"], material, node.inputs[0])
        
    def buildShaderNodeBackground(self, config, material, parentInput):
        debugPrint(material)
        debugPrint(material.node_tree)
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_NODE_BACKGROUND)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        

        if parentInput != None:
            debugPrint("linking to parent input")
            material.node_tree.links.new(parentInput, node.outputs[0])

        if "color" in config:
            debugPrint("connecting color")
            self.buildMaterial(config["color"], material, node.inputs[0])
        
        if "strength" in config:
            debugPrint("connecting strength")
            self.buildMaterial(config["strength"], material, node.inputs[1])

    def builderShaderNodeDiffuse(self, config, material ,parentInput):
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_NODE_DIFFUSE)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        
        if parentInput != None:
            material.node_tree.links.new(parentInput, node.outputs[0])

        if "color" in config:
            self.buildMaterial(config["color"], material, node.inputs[0])
        if "roughness" in config:
            self.buildMaterial(config["roughness"], material, node.inputs[1])
        if "normal" in config:
            self.buildMaterial(config["normal"], material, node.inputs[2])

    def buildShaderEmission(self, config, material, parentInput = None):
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_EMISSION)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        
        if parentInput != None:
            material.node_tree.links.new(parentInput, node.outputs[0])

        if "color" in config:
            self.buildMaterial(config["color"], material, node.inputs['Color'])

    def buildShaderMixRGB(self, config, material, parentInput = None):
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_MIX_RGB)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        

        if parentInput != None:
            material.node_tree.links.new(parentInput, node.outputs[0])
        node.inputs[1].default_value = config["color1"]
        if "color2" not in config:
            node.inputs[2].default_value = config["color1"]
        else:
            node.inputs[2].default_value = config["color2"]

    def buildShaderNodeValue(self, config, material, parentInput = None):
        createfunc = lambda x : material.node_tree.nodes.new(SHADER_NODE_VALUE)
        node = self.existingMaterialNode(material.node_tree.nodes, config, createfunc)
        self.ascribeNameLable(config, node)
        

        if parentInput != None:
            material.node_tree.links.new(parentInput, node.outputs[0])
        node.outputs[0].default_value = config["value"]

        _put = node.outputs[0]
        _path = 'default_value'
        _property = "value"
        self.setupShaderNodeAnimation(_put, _path, _property, config)

    def setupShaderNodeAnimation(self, _put, _path, _property, config):
        if "animation" in config:
            debugPrint("setup shader node animation")
            for a in range(len(config["animation"])):
                anim = config["animation"][a]
                org_frame = self.context.scene.frame_current
                if "frame" in anim:
                    self.context.scene.frame_current = anim["frame"]
                    if "default_value" == _path:
                        _put.default_value = anim[_property]
                    _put.keyframe_insert(data_path=_path, frame=anim["frame"] )
                    self.context.scene.frame_current = org_frame
                else:
                    raise ValueError("no frame in animation")

    def limit_rotation(self, obj, config, keyframe, frame):
        debugPrint("limit rotation")
        meshobject = obj["object"]
        cns = meshobject.constraints.new('LIMIT_ROTATION') 
        if "use_limit_x" in config:
            cns.use_limit_x = self.str2bool(config["use_limit_x"])
        if "use_limit_y" in config:
            cns.use_limit_y = self.str2bool(config["use_limit_y"])
        if "use_limit_z" in config:
            cns.use_limit_z = self.str2bool(config["use_limit_z"])
        if "owner_space" in config:
            cns.owner_space = config["owner_space"]
    def track_to(self, obj, config, keyframe, frame):
        debugPrint("track to")
        meshobject = obj["object"]
        if "target" in config:
            debugPrint("getting track to target" + (config["target"]))
            targetObj = self.getBlenderObjectByName(config["target"])
            debugPrint("got track to target")
            if targetObj != None:
                debugPrint("found track to target")
                cns = meshobject.constraints.new("TRACK_TO")
                cns.target = targetObj
                if "track_axis" in config:
                    cns.track_axis = config["track_axis"]
                if "up_axis" in config:
                    cns.up_axis = config["up_axis"]
            else: 
                raise ValueError("Cant find the target " + config["target"])
                
                
    def follow_path(self, obj, config, keyframe, frame):
        debugPrint("follow path")
        meshobject = obj["object"]
        if "target" in config:
            targetObj = self.getBlenderObjectByName(config["target"])
            if targetObj != None:
                cns = meshobject .constraints.new('FOLLOW_PATH')
                cns.target = targetObj
                cns.use_curve_follow = True
                if "use_curve_follow" in config:
                    cns.use_curve_follow = self.str2bool(config["use_curve_follow"])
                cns.use_curve_radius = True
                if "use_curve_radius" in config:
                    cns.use_curve_radius = self.str2bool(config["use_curve_radius"])
                
                cns.use_fixed_location = False    
                if "use_curve_radius" in config:
                    cns.use_fixed_location = self.str2bool(config["use_fixed_location"])
                
                cns.forward_axis = 'FORWARD_Y'
                if "forward_axis" in config:
                    cns.forward_axis = config["forward_axis"]
                    
                cns.up_axis = 'UP_Z'
                if "up_axis" in config:
                    cns.up_axis = config["up_axis"]
    def collision(self, obj, config, keyframe , frame):
        debugPrint("adding collision")
        bpy.context.scene.objects.active = obj["object"]
        paintlayer = bpy.context.scene.objects.active
        bpy.ops.object.modifier_add(type="COLLISION")
        settings = paintlayer.modifiers["Collision"].settings
        if "use_particle_kill" in config:
            settings.use_particle_kill = self.str2bool(config["use_particle_kill"])
    def dynamic_brush(self, obj , configs , keyframe ,  frame):
        debugPrint("creating dynamic paint brush")
        bpy.context.scene.objects.active = obj["object"]
        paintlayer = bpy.context.scene.objects.active
        bpy.ops.object.modifier_add(type="DYNAMIC_PAINT")
        config = configs[0]
        bpy.ops.dpaint.type_toggle(type="BRUSH")
        settings = paintlayer.modifiers["Dynamic Paint"].brush_settings
        if "paint_source" in config:
            settings.paint_source = config["paint_source"]
        if "particle_system" in config:
            system = obj["particle_systems"][config["particle_system"]]
            settings.particle_system = system
        if "solid_radius" in config:
            settings.solid_radius = config["solid_radius"]
        if "smooth_radius" in config:
            settings.smooth_radius = config["smooth_radius"]
        if "use_particle_radius" in config:
            settings.use_particle_radius = self.str2bool(config["use_particle_radius"])
    def str2bool(self, v):
        if isinstance(v, bool):
            return v
        return v.lower() in ("yes", "true", "t", "1")    
    def dynamic_paint(self, obj , config, keyframe , frame):
        debugPrint("creating dynamic paint")
        bpy.context.scene.objects.active = obj["object"]
        paintlayer = bpy.context.scene.objects.active
        bpy.ops.object.modifier_add(type="DYNAMIC_PAINT")
        
        bpy.ops.dpaint.type_toggle(type="CANVAS")
        settings = paintlayer.modifiers["Dynamic Paint"].canvas_settings
        debugPrint(settings.canvas_surfaces)
        canvas_surface = settings.canvas_surfaces[-1]
        if "surface_type" in config:
            canvas_surface.surface_type = config["surface_type"]
        if "use_dissolve" in config:
            canvas_surface.use_dissolve = bool(config["use_dissolve"])
        if "dissolve_speed" in config and canvas_surface.use_dissolve:
            canvas_surface.dissolve_speed = int(config["dissolve_speed"])
        if "frame_end" in config:
            canvas_surface.frame_end = int(config["frame_end"])
        if "frame_start" in config:
            canvas_surface.frame_start = int(config["frame_start"])
            
            

    def particles( self, obj , configs, keframe , frame):
        debugPrint("creating particles")
        bpy.context.scene.objects.active = obj["object"]
        emitter = bpy.context.scene.objects.active
        for i in range(len(configs)):
            config = configs[i]
            bpy.ops.object.particle_system_add()    
            psys1 = emitter.particle_systems[-1]
            pset1 = psys1.settings
            if "particle_systems" in obj:
                obj["particle_systems"].append(psys1)
            else:
                obj["particle_systems"] = [psys1]
            # Emission
            if "system" in config:
                pset1.name = config["system"]
            else:
                pset1.name = 'ParticleSettings_Gen'
            if "frame_end" in config:
                pset1.frame_end = int(config["frame_end"])
            if "frame_start" in config:
                pset1.frame_start = int(config["frame_start"])
            if "lifetime" in config:
                pset1.lifetime = int(config["lifetime"])
            else:
                pset1.lifetime = 50
            if "lifetime_random" in config:    
                pset1.lifetime_random = float(config["lifetime_random"])
            if "emit_from" in config:  
                pset1.emit_from = config["emit_from"]
            if "emit_from" in config:
                pset1.emit_from = bool(config["use_render_emitter"])
            if "count" in config:
                pset1.count = int(config["count"])
            # Velocity
            if "normal_factor" in config:
                pset1.normal_factor = float(config["normal_factor"])
            # Physics
            pset1.physics_type = 'NEWTON'
            if "mass" in config:
                pset1.mass = float(config["mass"])
            if "particle_size" in config:
                pset1.particle_size = float(config["particle_size"])
            if "use_multiply_size_mass" in config:
                pset1.use_multiply_size_mass = bool(config["use_multiply_size_mass"])
                # Effector weights
                ew = pset1.effector_weights
            if "gravity" in config:
                ew.gravity = float(config["gravity"])
            if "wind" in config:
                ew.wind = float(config["wind"])
            
                # Children
            if "child_nbr" in config:
                pset1.child_nbr = int(config["child_nbr"])
            if "rendered_child_count" in config:            
                pset1.rendered_child_count = int(config["rendered_child_count"])
            if "child_type" in config:
                pset1.child_type = config["child_type"]
            
                # Display and render
            if "draw_percentage" in config:
                pset1.draw_percentage = int(config["draw_percentage"])
            if "draw_method" in config:            
                pset1.draw_method = config["draw_method"]
            if "material" in config:
                pset1.material = int(config["material"])
            if "particle_size" in config:
                pset1.particle_size = float(config["particle_size"])    
            if "render_type" in config:
                pset1.render_type = config["render_type"]
            if "dupli_object" in config:
                ot_targ = self.getObjectByName(config["dupli_object"])
                if ot_targ != None:
                    pset1.dupli_object = ot_targ["object"]
            if "dupli_group" in config:
                #group = self.getGroupByName(config["dupli_group"])
                pset1.dupli_group = bpy.data.groups[config["dupli_group"]]
                
            if "render_step" in config:    
                pset1.render_step = config["render_step"]
                  
    def translation(self, obj, pos, keyframe, frame):
        if pos == None:
                return
        if "x" in pos and pos["x"] != None:
            obj["object"].location.x = float(pos["x"])
            if keyframe:
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=0)
                self.setKeyFrameProperties(obj["object"], pos, "location", "x",  frame)
        if "y" in pos and pos["y"] != None:
            obj["object"].location.y = float(pos["y"])
            if keyframe:
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=1)
                self.setKeyFrameProperties(obj["object"], pos, "location", "y",  frame)
        if "z" in pos and pos["z"] != None:
            obj["object"].location.z = float(pos["z"])
            if keyframe:
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=2)
                self.setKeyFrameProperties(obj["object"], pos, "location", "z",  frame)
        # if "handle_type" in pos:
        #         if keyframe:
        #             self.setHandleType(obj, "location", pos["handle_type"])
                    
    def scale(self, obj, scale, keyframe, frame):
            if scale == None:
                return
            if "x" in scale and scale["x"] != None:
                debugPrint(scale["x"])
                obj["object"].scale.x = (scale["x"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                    self.setKeyFrameProperties(obj["object"], scale, "scale", "x",  frame)
                
            if "y" in scale and scale["y"] != None:
                obj["object"].scale.y = (scale["y"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                    self.setKeyFrameProperties(obj["object"], scale, "scale", "y",  frame)
                
            if "z" in scale and scale["z"] != None:
                obj["object"].scale.z = (scale["z"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)
                    self.setKeyFrameProperties(obj["object"], scale, "scale", "y",  frame)
            # if "handle_type" in scale:
            #     if keyframe:
            #         self.setHandleType(obj, "scale", scale["handle_type"])
    
    def setHandleType(self, obj, data_path, handle_type):
        for curve in obj["object"].animation_data.action.fcurves:
            if curve.data_path == data_path:
                i = len(curve.keyframe_points) - 1
                if i > -1:
                    curve.keyframe_points[i].interpolation = handle_type

    def getFCurve(self, object, data_path, prop):
        if object.animation_data != None:
            fcurves = object.animation_data.action.fcurves
            for fcurve in fcurves:
                if fcurve.data_path == data_path and fcurve.array_index == CONVERT_INDEX[prop]:
                    return fcurve
        raise ValueError("no animation data in {}".format(object.name))
    def getKeyFramePoint(self, object, data_path, prop, frame):
        fcurve = self.getFCurve(object, data_path, prop)
        for f in fcurve.keyframe_points:
            if f.co[0] == frame:
                return f
        raise ValueError("cannot find get keyframe_point")

    def setKeyFrameProperties(self, obj, config, data_path, property, frame):
        # fcurve = self.getFCurve(obj, data_path, property)
        p_keyframe_point = property + "_keyframe_point"
        if p_keyframe_point in config:
            keyframe_config = config[p_keyframe_point]
            keyframepoint = self.getKeyFramePoint(obj, data_path, property, frame)
            debugPrint("{}".format(keyframepoint))
            debugPrint("keyframepoint : {}".format(keyframepoint.co))
            for key in _keypoint_settings:
                try:
                    if key in keyframe_config:
                        if isinstance(keyframe_config[key], (tuple, list)):
                            v = keyframe_config[key]
                            debugPrint("set vector :{}".format(mathutils.Vector(v)))
                            setattr(keyframepoint, key, mathutils.Vector(v))
                            if key == "co":
                                debugPrint("keyframepoint : {}".format(keyframepoint.co))
                        else:
                            debugPrint("setting key {} : {}".format(key, keyframe_config[key]))
                            setattr(keyframepoint, key, keyframe_config[key])
                except Exception as e:
                    debugPrint("couldnt set property : {}".format(e))
            
    def animateVertices(self, obj, animations, keyframe, frame):
        debugPrint("animate vertices")
        if animations == None:
            return
        if "action" in obj:
            action = obj["action"]
        else:
            # obj = obj["object"]
            mesh = obj["object"].data
            action = bpy.data.actions.new("MeshAnimation")
            mesh.animation_data_create()
            mesh.animation_data.action = action
            obj["action"] = action
            data_path = "vertices[%d].co"
            obj["fcurves"] = {}
            if "vertices" in animations:
                for vertex in animations["vertices"]:
                    v = mesh.vertices[vertex["index"]]
                    fcurves = [action.fcurves.new(data_path % v.index, index=i) for i in range(3)]
                    obj["fcurves"][vertex["index"]] = fcurves
            debugPrint("fcurves setup")
            
        if "vertices" in animations:
            for vertex in animations["vertices"]:
                debugPrint("mesh")
                mesh = obj["object"].data
                debugPrint("get vertex")
                v = mesh.vertices[vertex["index"]]
                # co_rest = v.co
                debugPrint("get fcurves")
                fcurves = obj["fcurves"][vertex["index"]]
                ## for t, value in zip(frames, values):
                # co_kf = mathutils.Vector((vertex["position"]["x"], vertex["position"]["y"], vertex["position"]["z"]))
                # insert_keyframe(fcurves, frame, co_kf) 
                debugPrint("set fcurves")
                for i in range(len(fcurves)):
                    fcu = fcurves[i]
                    debugPrint("insert fcurve key frame")
                    fcu.keyframe_points.insert(frame, vertex["position"][i],    options={'FAST'})
                    debugPrint("inserted fcu curve")

    def rotation(self, obj, rotation, keyframe, frame):
            debugPrint("rotation")
            if rotation == None:
                return
            if "x" in rotation and rotation["x"] != None:
                debugPrint(rotation["x"])
                obj["object"].rotation_euler.x = math.radians(rotation["x"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=0)
                    self.setKeyFrameProperties(obj["object"], rotation, "rotation_euler", "x",  frame)
            if "y" in rotation and rotation["y"] != None:
                obj["object"].rotation_euler.y = math.radians(rotation["y"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=1)
                    self.setKeyFrameProperties(obj["object"], rotation, "rotation_euler", "y",  frame)
                
            if "z" in rotation and rotation["z"] != None:
                obj["object"].rotation_euler.z = math.radians(rotation["z"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=2)
                    self.setKeyFrameProperties(obj["object"], rotation, "rotation_euler", "z", frame)
            # if "handle_type" in rotation:
            #         if keyframe:
            #             self.setHandleType(obj, "rotation_euler", rotation["handle_type"])    
                                    
    def getObjectByName(self, name):
        for i in range(len(self.presentation_objects)):
            obj = self.presentation_objects[i]
            if "name" in obj:
                if obj["name"] == name and obj["scene"] == self.scene:
                    return obj
        for obj in bpy.data.objects:
            if obj.name == name:
                newobject = { "name" : name, "object" : obj }
                self.presentation_objects.append(newobject)
                return newobject
        return 0
    def getBoneByName(self, name):
        for i in range(len(self.presentation_target_bones)):
            obj = self.presentation_target_bones[i]
            if "name" in obj:
                if obj["name"] == name:
                    return obj
        return 0
    
    def searchForObject(self, name, root):
        if root == None:
            objects = self.context.scene.objects
        if name.find("#") == -1:
            obj_name = name.split("#")[0]
            if root.name == obj_name:
                v = "#"
                v.join(name.split("#")[1:])
                return self.searchForObject(v, root)
            
        elif name == root.name:
            return root
                     
        for i in range(len(root.children)):
            res = self.searchForObject(name, root.children[i])
            if res != None:
                return res
        return None

    def setFrame(self, keyframe):
        self.context.scene.frame_current = keyframe["frame"]    
    def createStage(self, scene):
        debugPrint("create stage")
        if "stage" in scene:
            stageConfig = scene["stage"]
            if "File" in stageConfig:
                opath = stageConfig["File"]
                if "Group" in stageConfig:
                    if not self.hasGroupByName(stageConfig["Group"]):
                        with bpy.data.libraries.load(opath) as (data_from, data_to):
                            data_to.groups = [stageConfig["Group"]]
                    group = bpy.data.groups[stageConfig["Group"]]
                    for j in range(len(group.objects)):
                        obj = group.objects[j]
                        debugPrint("stage: add object")
                        o = bpy.ops.object.add_named(name=obj.name)
                        self.context.active_object.location.x = 0
                        self.context.active_object.location.y = 0
                        self.context.active_object.location.z = 0
        debugPrint("created stage")

    def attachGroups(self, scene):
        if "groups" in scene:
            groups = scene["groups"]
            if groups != None:
                for groupData in groups:
                    file = groupData["file"]
                    file = self.fixPath(os.path.join(self.relativeDirePath,  file))
                    name = groupData["name"]
                    with bpy.data.libraries.load(file) as (df, dt):
                        dt.groups = [name]
                    group = bpy.data.groups[name]
                    instance = bpy.data.objects.new("dupli_group", None)
                    instance.dupli_type = "GROUP"
                    instance.dupli_group = group
                    self.context.scene.objects.link(instance)
                    obj = { "object" : instance }
                    keyframe = True
                    frame = 1
                    if "position" in groupData:
                        pos = groupData["position"]
                        self.translation(obj, pos, keyframe, frame)
                    if "scale" in groupData:
                        pos = groupData["scale"]
                        self.scale(obj, pos, keyframe, frame)
                    if "rotation" in groupData:
                        pos = groupData["rotation"]
                        self.rotation(obj, pos, keyframe, frame)
                    
                    
    def createObjectsUsed(self, scene):
        objects = []
        objectnames = []
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        keyframes = scene["keyframes"]
        for k in range(len(keyframes)):
            debugPrint("keyframe s" )
            debugPrint(len(keyframes))
            keyframe = keyframes[k]
            debugPrint("keyframe #" )
            keyframe_objects = keyframe["objects"]
            debugPrint("for each keyframe_obect")
            for j in range(len(keyframe_objects)):
                obj = keyframe_objects[j]
                debugPrint("get name keyframe_obect")
                count = objectnames.count(obj["name"])
                debugPrint("got name " + obj["name"])
                debugPrint("count : " + str(count))
                if count == 0:
                    debugPrint("appending object name")
                    objectnames.append(obj["name"])
                    debugPrint("create object")
                    newobj = self.createObject(obj, scene["objects"])
                    if newobj == None:
                        raise ValueError('new object has value of None')
                    debugPrint("created the object")
                    objects.append(newobj)
                    debugPrint("appended object to list")
        debugPrint("created objectes used array")
        return objects

    def createObject(self, obj, scene_objects):
        debugPrint("create object")
        for i in range(len(scene_objects)):
            so = scene_objects[i]
            if so["name"] == obj["name"]:
                res = self.createObjectWithConfig(so)
                debugPrint("created object with config")
                res["name"] = obj["name"]
                return res
    def matchesSelector(self, object, selector):
        if selector:
            if object:
                for i in range(len(selector)):
                    s = selector[i]
                    if object.name.startswith(s):
                        return True
        return False
    def createBespoke(self, scene_object_config):
        full_path_to_file = os.path.join(scene_object_config["folder"], scene_object_config["file"])
        for obj in bpy.data.objects:
            obj.tag = True
        bpy.ops.import_scene.obj(filepath=full_path_to_file)
        imported_objects = [obj for obj in bpy.data.objects if obj.tag is False]
        if "materials" in scene_object_config:
            materials = scene_object_config["materials"]
            for i in range(len(materials)):
                material = materials[i]
                if "name" in material:
                    if not self.hasMaterialByName(material["name"]):
                        if "config" in material:
                            debugPrint("building material " +  material["name"])
                            self.buildMaterial(material["config"])
                if "selector" in material:
                    for j in range(len(imported_objects)):
                        imported_object = imported_objects[j]
                        if self.matchesSelector(imported_object, material["selector"]):
                            mat = self.getMaterialByName(material["name"])
                            if mat:
                                imported_object.data.materials.clear()
                                imported_object.data.materials.append(mat)
                            else:
                                debugPrint("MATERIAL MISSING !!!!")
                                debugPrint(material["name"])
                                raise ValueError("Material Missing")

        bpy.ops.object.empty_add(type="PLAIN_AXES")
        empty = self.context.active_object
        for im_obj in imported_objects:
            im_obj.parent = empty
        return empty
    def createObjectWithConfig(self, scene_object_config):
        debugPrint("Create object with configuration")
        result = {}
        if "type" in scene_object_config:
            debugPrint(scene_object_config["type"])
            result["type"] = scene_object_config["type"]
        if(scene_object_config["type"] == "cube"):
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
        elif scene_object_config["type"] == "bespoke":
            result["object"] = self.createBespoke(scene_object_config)
            result["mesh"] = result["object"].data
        elif scene_object_config["type"] == "custom":
            if "name" in scene_object_config:
                group = self.getGroupByName(scene_object_config["group"])
                if group:
                    res = self.duplicateGroup(group)
                    result["object"] = res
                    result["mesh"] = res.data
        elif scene_object_config["type"] == "path":
            pathobject = self.path(scene_object_config)
            result["object"] = pathobject["object"]
            result["mesh"] = pathobject["mesh"]                
        elif scene_object_config["type"] == "circle":
            bpy.ops.curve.primitive_bezier_circle_add()
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
        elif scene_object_config["type"] == "camera":
            bpy.ops.object.camera_add()
            result["object"] = self.context.active_object
            result["object"].data.clip_end = 10000            
            if "camera_type" in scene_object_config:
                if scene_object_config["camera_type"]:
                    result["object"].data.type = scene_object_config["camera_type"]
        elif scene_object_config["type"] == "plane":
            try:
                bpy.ops.mesh.primitive_plane_add(radius=1,location=(0,0,0))
            except: 
                bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,0))
            
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
        elif scene_object_config["type"] == "empty":
            bpy.ops.object.empty_add(type="PLAIN_AXES")
            result["object"] = self.context.active_object
        elif scene_object_config["type"] == "image" or  scene_object_config["type"] == "movie" or  scene_object_config["type"] == "video":
            debugPrint("--------------------------------------------------------------------------------------")
            debugPrint( scene_object_config["directory"])
            bpy.ops.import_image.to_plane(
                files=[{"name":scene_object_config["fileName"], "name":scene_object_config["fileName"]}], 
                directory= scene_object_config["directory"], 
                filter_image=True, 
                filter_movie=True,
                use_transparency= "use_transparency" in scene_object_config and scene_object_config["use_transparency"],
                filter_glob="", 
                relative=False)
            result["object"] = self.context.active_object
            debugPrint("active_object : {}".format(self.context.active_object))
            result["mesh"] = self.context.active_object.data
            if "fuzzy" in scene_object_config:
                result["fuzzy"] = scene_object_config["fuzzy"]
                result["config"] = scene_object_config
            if "dim_width" in scene_object_config:
                self.context.active_object.dimensions.x = scene_object_config["dim_width"]
                bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
            if "dim_height" in scene_object_config:
                self.context.active_object.dimensions.y = scene_object_config["dim_height"]
                bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
            properties = ["use_cyclic", "frame_duration", "frame_offset", "frame_start"]
            if "settings" in scene_object_config:
                settings_scene_object_config = scene_object_config["settings"]
                if "composite" in settings_scene_object_config and settings_scene_object_config["composite"] and "materials" in settings_scene_object_config["composite"]:
                    if settings_scene_object_config["composite"]["materials"]:
                        compositewriter = CompositeWriter()
                        # this all assumes. that the material will be unique, and used only once in the scene.
                        for mat_custom in settings_scene_object_config["composite"]["materials"]:
                            mat = compositewriter.defineMaterial(mat_custom, self.presentation_material_animation_points)
                            self.context.active_object.data.materials.clear()
                            self.context.active_object.data.materials.append(mat)
                            if mat:
                                nodes = compositewriter.getCreatedNodesOfType("ShaderNodeTexImage")
                                for node in nodes:
                                    debugPrint("a {} node was found ".format(node["type"]))
                                    for prop in properties:
                                        if prop in scene_object_config:
                                            debugPrint("setting prop {} ".format(prop))
                                            setattr(node["node"].image_user, prop, scene_object_config[prop])
            else:
                for prop in properties:
                    if prop in scene_object_config:
                        movie_name = scene_object_config["fileName"]
                        debugPrint("set movie name : {}".format(movie_name))
                        if self.materialNameStartsWith(movie_name):
                            debugPrint("has image movie")
                            mat = self.materialNameStartsWith(movie_name)
                            if mat:
                                debugPrint("mat found")
                                setattr(mat.node_tree.nodes["Image Texture"].image_user, prop, scene_object_config[prop])
            debugPrint("end --------------------------------------------------------------------------------------")
        elif scene_object_config["type"] == "ngon":
            result["object"] = self.createNgon(scene_object_config)
        elif scene_object_config["type"] == "ngon-surface":
            result["object"] = self.createNgonSurface(scene_object_config)
        elif scene_object_config["type"] == "lamp":
            light = "POINT"
            if "light" in scene_object_config:
                light = scene_object_config["light"]
            if bpy.ops.object.light_add:
                bpy.ops.object.light_add(type=light)
            else:
                bpy.ops.object.lamp_add(type=light)
            result["object"] = self.context.active_object
            if "strength" in scene_object_config:
                strength = scene_object_config["strength"]
                debugPrint("setting strength")
                debugPrint(strength)
                if result["object"].data and result["object"].data.node_tree:
                    result["object"].data.node_tree.nodes["Emission"].inputs[1].default_value = strength
        elif scene_object_config["type"] == "text":
            bpy.ops.object.text_add()
            debugPrint("added a text object")
            result["text"] = True
            result["object"] = self.context.active_object
            if "value" in scene_object_config:
                result["object"].data.body = scene_object_config["value"]
            result["mesh"] = self.context.active_object.data
            
            if "extrude" in scene_object_config and scene_object_config["extrude"]:
                result["object"].data.extrude = scene_object_config["extrude"]
                
            if "align" in scene_object_config and scene_object_config["align"]:
                result["object"].data.align_x = scene_object_config["align"]
            if "align_y" in scene_object_config and scene_object_config["align_y"]:
                result["object"].data.align_y = scene_object_config["align_y"]
            if "size" in scene_object_config:
                result["object"].data.size = scene_object_config["size"]
            if "font" in scene_object_config:
                try:
                    loaded = self.ensureFontLoaded(scene_object_config["font"])
                    if loaded: 
                        font = self.getFont(scene_object_config["font"])
                        debugPrint("got font " + scene_object_config["font"])
                        if font != 0:
                            result["object"].data.font = font
                except:
                    debugPrint("couldnt find font")
            if "dim_width" in scene_object_config:
                result["object"].data.text_boxes[0].width = scene_object_config["dim_width"]
            if "dim_height" in scene_object_config:
                result["object"].data.text_boxes[0].height = scene_object_config["dim_height"]
            # bpy.ops.object.convert(target="MESH")
            # bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        if "scale" in scene_object_config and scene_object_config["scale"] and not isinstance(scene_object_config["scale"], int) and not isinstance(scene_object_config["scale"], float):
            scale = scene_object_config["scale"]
            self.scale(result, scale, False, 0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale= True)

        if "rotation" in scene_object_config and not isinstance(scene_object_config["rotation"], int)and not isinstance(scene_object_config["rotation"], float):
            debugPrint("roation {}".format(scene_object_config["rotation"]))
            self.rotation(result, scene_object_config["rotation"], False, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale= False)
        
        
        if "material" in scene_object_config and scene_object_config["material"]:
            if self.hasMaterialByName(scene_object_config["material"]):
                material = self.getMaterialByName(scene_object_config["material"])
                debugPrint("append material " + scene_object_config["material"])
                result["object"].data.materials.append(material)
                debugPrint("appended material")
        if "object" in result:
            result["object"].name = scene_object_config["name"]

        return result
    
    def hasImageMovie(self, movieName):
        for key in bpy.data.images.keys():
            if key == movieName:
                return True
        return False
        
    
    
    def optimalFit(self, obj, h, w):
        debugPrint("optimal fit")
        obj.data.size = .01
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
        _h = obj.dimensions[0]
        _w = obj.dimensions[1]
        _size = obj.data.size
        _step = 3
        prev_high_score = w * h
        prev_low_score = 0
        prev_low_size = 0
        prev_high_size = 10
        newsize = 5
        down = False
        lastdirection = -1
        for i in range(1, 5):
            obj.data.size = newsize
            score = self.calcScore(obj, h , w)
            
            obj.data.size = (prev_high_size + newsize) / 2
            high_score = self.calcScore(obj, h, w)
            
            obj.data.size = (newsize + prev_low_size) / 2
            low_score = self.calcScore(obj, h, w)
            
            if high_score < low_score: # closer to desired value
                prev_low_size = obj.data.size
            else:
                prev_high_size = obj.data.size
                
            newsize = (prev_high_size + prev_low_size) / 2
            print(newsize)
        obj.data.size = newsize      
        # print("size {}, score {}".format(prev_low_size, prev_low_score))  
    def createNgonSurface(self, config):
        debugPrint("Create ngon surface")
        if "file" in config:
            f = open(config["file"], 'r')
            filecontents = f.read()
            obj = json.loads(filecontents)
            faces = obj["faces"]
        else:
            faces = config["faces"]
            vertices = config["vertices"]
        bm = bmesh.new()
        all_vertices = []
        debugPrint("collect vertices")
        for v in vertices:
            _v = bm.verts.new((v[0], v[1], v[2]))
            all_vertices.append(_v)
        debugPrint("collected vertices")
        for f in faces:
            verts = []
            for v in f:
                verts.append(all_vertices[v])
            bm.faces.new(verts)
        debugPrint("built faces0")
        me = bpy.data.meshes.new("")
        # bmesh.ops.automerge(bm, verts=all_vertices,  dist=.000001)
        bm.to_mesh(me)
        ob = bpy.data.objects.new("", me)
        bpy.context.scene.collection.objects.link(ob)
        bpy.context.scene.update()
        return ob
    def createNgon(self, config):
        verts = config["vertices"]
        bm = bmesh.new()
        for v in verts:
            bm.verts.new((v["x"], v["y"], v["z"]))
        bm.faces.new(bm.verts)
        bm.normal_update()

        me = bpy.data.meshes.new("")
        bm.to_mesh(me)

        ob = bpy.data.objects.new("", me)
        bpy.context.scene.collection.objects.link(ob)
        bpy.context.scene.update()
        if "extrude" in config:
            # Go to edit mode, face selection mode and select all faces
            bpy.ops.object.mode_set( mode   = 'EDIT'   )
            bpy.ops.mesh.select_mode( type  = 'FACE'   )
            bpy.ops.mesh.select_all( action = 'SELECT' )

            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value":(config["extrude"]["x"], config["extrude"]["y"], config["extrude"]["z"])}
            )

            bpy.ops.object.mode_set( mode = 'OBJECT' )
        return ob
    def calcScore(self, obj, h, w):
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
        _h = obj.dimensions[0]
        _w = obj.dimensions[1]
        hh = _h-h
        hh = hh * hh
        ww = _w-w
        ww = ww * ww
        score = ww + hh
        return score
    def path(self, config):
        debugPrint("----path-----")
        x = 0
        y = 0
        z = 0
        if "position" in config:
            pconfig = config["position"]
            if "x" in pconfig:
                x = int(pconfig["x"])
            if "y" in pconfig:
                y = int(pconfig["y"])
            if "z" in pconfig:
                z = int(pconfig["z"])
        debugPrint("create new curve")    
        curvename = config["name"]
        debugPrint(curvename)    
        curvedata = bpy.data.curves.new(name=curvename, type='CURVE') 
        objectdata = bpy.data.objects.new(curvename, curvedata)  
        objectdata.location = (x,y,z) #object origin  
        # bpy.context.scene.objects.link(objectdata)   
        bpy.context.scene.collection.objects.link(objectdata) # 2.80
        
        # Set path data
        curvedata.dimensions = '3D'
        if "hooks" in config:
            for k in range(len(config["hooks"])):
                debugPrint("add hook")
                hookConfig = config["hooks"][k]
                debugPrint("hookConfig")
                #create modifiers & set Parent Object
                hookname = hookConfig["hook"]+"_"+str(hookConfig["index"])+"_"+config["name"]
                debugPrint("hook name : " + hookname)
                objectdata.modifiers.new(hookname, type='HOOK')
                debugPrint("added modifier")
                hookObj = bpy.data.objects[hookConfig["hook"]] #self.getObjectByName(hookConfig["hook"]) 
                debugPrint(hookObj)
                objectdata.modifiers[hookname].object = hookObj
                debugPrint("modifier object set")

        curvedata.use_path = True
        if "use_path" in config:
            debugPrint("set use_path" + config["use_path"])
            temp = self.str2bool(config["use_path"])
            curvedata.use_path = temp
            debugPrint("use path set")
        
        debugPrint("use path follow")    
        curvedata.use_path_follow = True
        if "use_path_follow" in config:
            debugPrint("use_path_follow")
            curvedata.use_path_follow = self.str2bool(config["use_path_follow"])
        
        if "twist_mode" in config:
            debugPrint("twist_mode")
            curvedata.twist_mode = config["twist_mode"]
            
        debugPrint("use path_duration")  
        curvedata.path_duration = 100
        if "path_duration" in config:
            debugPrint("path_duration")
            curvedata.path_duration = int(config["path_duration"])
        
        debugPrint("use path_animation") 
        if "path_animation" in config:
            debugPrint("path_animation")
            for num in range(len(config["path_animation"])):
                path_anim_config = config["path_animation"][num]
                curvedata.eval_time = int(path_anim_config["eval_time"])
                path_anim_frame = int(path_anim_config["frame"])
                curvedata.keyframe_insert(data_path="eval_time", frame=path_anim_frame)  
        
    
        curvetype = "POLY"
        if "curvetype" in config:
            curvetype = config["curvetype"]
        polyline = curvedata.splines.new(curvetype)  
        polyline.use_cyclic_u = False
        if "use_cyclic_u" in config:
            debugPrint("use_cyclic_u")
            polyline.use_cyclic_u = self.str2bool(config["use_cyclic_u"])
            
        config["radius_interpolation"] = 'BSPLINE'
        if "radius_interpolation" in config:
            polyline.radius_interpolation = config[ "radius_interpolation"]
    
        polyline.use_endpoint_u = False
        if "use_endpoint_u" in config:
            debugPrint("use_endpoint_u")
            polyline.use_endpoint_u = self.str2bool(config["use_endpoint_u"])
            
        if "bevel_object" in config:
            bevel_object = bpy.data.objects[config["bevel_object"]]
            curvedata.bevel_object = bevel_object
            
        if "taper_object" in config:
            taper_object = bpy.data.objects[config["taper_object"]]
            curvedata.taper_object = taper_object
                
        debugPrint("creating points")
        if "points" in config:
            cList = config["points"]
            debugPrint(str(len(cList)))
            polyline.points.add(len(cList)-1)
            for num in range(len(cList)):  
                x, y, z, w = cList[num]
                polyline.order_u = 4
                if "order_u" in config:
                    polyline.points[num].order_u = int(config["order_u"])
                polyline.points[num].co = (x, y, z, w)
        if "hooks" in config:
            for k in range(len(config["hooks"])):
                debugPrint("hooking up hooks")
                hookConfig = config["hooks"][k]
                hookname = hookConfig["hook"]+"_"+str(hookConfig["index"])+"_"+config["name"]
                index =  int(hookConfig["index"])
                point = polyline.points[index]
                debugPrint("point ")
                debugPrint(point)
                self.deselectAll()
                hookObj = bpy.data.objects[hookConfig["hook"]]
                hookObj.select_set(True)
                # objectdata.select = True
                # bpy.context.scene.objects.active = obj["object"]
                bpy.context.scene.objects.active = objectdata
                debugPrint("object data selected ")
                point.select_set(True)
                objectdata.select_set(True)
                bpy.ops.object.mode_set(mode='EDIT') 
                                #select point
                debugPrint("assigning")
                bpy.ops.object.hook_assign(modifier=hookname)
                point.select_set(False)
                bpy.ops.object.mode_set(mode='OBJECT') 
                debugPrint("assigning")
                
        return { "object": objectdata, "mesh": curvedata}

    def getFont(self, fontname):
        fonts = bpy.data.fonts
        for i in range(len(fonts)):
            font = fonts[i]
            debugPrint(font.name.lower())
            if font.filepath.lower() == self.getFontPath(fontname).lower():
                return font
        return 0
    def fixPath(self, _path):
        if os.path.sep == ("\\"):
            return _path
        return _path.replace("\\",  "/")
    
    def getFontPath(self, fontname):
        debugPrint("get font paths")
        fontlocation = "c:\\Windows\\Fonts\\"
        if "fonts" in self.settings:
            fontlocation = self.fixPath(os.path.join(self.relativeDirePath, self.settings["fonts"]))
        debugPrint("font location = " + fontlocation)
        fontpath = (os.path.join(fontlocation , fontname + ".ttf"))
        debugPrint(fontpath)
        if os.path.isfile(os.path.join(fontlocation , fontname + ".ttf")): 
            
            return fontpath
        return 0

    def ensureFontLoaded(self, fontname):
        fonts = bpy.data.fonts
        for i in range(len(fonts)):
            font = fonts[i]
            if font.name.lower() == fontname.lower():
                return True
        
        fontlocation = self.getFontPath(fontname)
        if os.path.isfile(fontlocation): 
            bpy.data.fonts.load(fontlocation)
            return True
        return False

    def loadSceneConfig(self, config):
        return config["scenes"]
    def loadArmaturesConfig(self,config):
        debugPrint("Load armatures config")
        if "armatures" in config:
            return config["armatures"]
        return None

    def loadSettings(self, config):
        return config["settings"]

    def clearObjects(self):
        del self.presentation_objects[:]
        del self.presentation_armatures[:]
        del self.presentation_target_bones[:]
        del self.presentation_material_animation_points[:]
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action = 'SELECT')
        bpy.ops.object.delete(use_global=False)
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)
        for item in bpy.data.armatures:
            bpy.data.armatures.remove(item)
        for item in bpy.data.cameras:
            bpy.data.cameras.remove(item)
        for item in bpy.data.curves:
            bpy.data.curves.remove(item)
        


def menu_func(self, context):
    self.layout.operator(PresentationBlenderAnimation.bl_idname)
    self.layout.operator(PresentationBlenderMaterialCompositeReader.bl_idname)
    self.layout.operator(PresentationBlenderMatCompReader.bl_idname)
    self.layout.operator(PresentationBlenderFromScene.bl_idname)
    #self.layout.operator(CompositorToBillboard.bl_idname)
    self.layout.operator(CompositorToScene.bl_idname)
    self.layout.operator(WriteConfig.bl_idname)
    self.layout.operator(WriteWorlds.bl_idname)
    self.layout.operator(CopyTextureDirectory.bl_idname)
    self.layout.operator(WriteGroups.bl_idname)
    self.layout.operator(WriteEnvironment.bl_idname)
    self.layout.operator(WriteMaterials.bl_idname)

# store keymaps here to access after registration
# addon_keymaps = []
def register():
    bpy.utils.register_class(PresentationBlenderAnimation)
    bpy.utils.register_class(PresentationBlenderMaterialCompositeReader)
    bpy.utils.register_class(PresentationBlenderMatCompReader)
    bpy.utils.register_class(PresentationBlenderGUI)
    bpy.utils.register_class(PresentationBlenderFromScene)
    #bpy.utils.register_class(CompositorToBillboard)
    bpy.utils.register_class(CompositorToScene)
    bpy.utils.register_class(WriteConfig)
    bpy.utils.register_class(WriteWorlds)
    bpy.utils.register_class(CopyTextureDirectory)
    bpy.utils.register_class(WriteGroups)
    bpy.utils.register_class(WriteEnvironment)
    bpy.utils.register_class(WriteMaterials)
    bpy.types.Scene.presentation_settings = bpy.props.StringProperty \
      (name = "Movie settings",
        subtype = "FILE_PATH",
        description = "JSON description of the movie to generate")
    bpy.types.Scene.presentation_name = bpy.props.StringProperty(name="Name")
    
    bpy.types.Scene.matcompositefile = bpy.props.StringProperty \
      (name = "Material/Composite File",
        subtype = "FILE_PATH",
        description = "JSON description of the material and composite settings")

    bpy.types.Scene.presentation_scene_output_folder = bpy.props.StringProperty \
      (name = "Output folder",
        subtype = "DIR_PATH",
        description = "Output folder for stuff")

    bpy.types.Scene.use_output_folder = bpy.props.BoolProperty(
        name="Use Output folder",
        description="Use the scene output folder to store settings",
        default = False
        )
    
    bpy.types.Scene.isbillboardcomposite = bpy.props.BoolProperty(
        name="Billboard Compositing",
        description="Setting enabled for billboard compositing",
        default = False
        )
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    #wm = bpy.context.window_manager
    #km = wm.keyconfigs.addon.keymaps.new(name='Object Mode',
    #space_type='EMPTY')
    #kmi = km.keymap_items.new(ObjectCursorArray.bl_idname, 'SPACE', 'PRESS',
    #ctrl=True, shift=True)
    #kmi.properties.total = 4
    #addon_keymaps.append((km, kmi))
def unregister():
    bpy.utils.unregister_class(PresentationBlenderAnimation)
    bpy.utils.unregister_class(PresentationBlenderMaterialCompositeReader)
    del bpy.types.Scene.presentation_settings
    del bpy.types.Scene.matcompositefile
    del bpy.types.Scene.presentation_name
    del bpy.types.Scene.presentation_scene_output_folder
    del bpy.types.Scene.use_output_folder
    del bpy.types.Scene.isbillboardcomposite
    bpy.utils.unregister_class(PresentationBlenderMatCompReader)
    bpy.utils.unregister_class(PresentationBlenderGUI)
    bpy.utils.unregister_class(PresentationBlenderFromScene)
    #bpy.utils.unregister_class(CompositorToBillboard)
    bpy.utils.unregister_class(CompositorToScene)
    bpy.utils.unregister_class(WriteConfig)
    bpy.utils.unregister_class(WriteWorlds)
    bpy.utils.unregister_class(CopyTextureDirectory)
    bpy.utils.unregister_class(WriteGroups)
    bpy.utils.unregister_class(WriteEnvironment)
    bpy.utils.unregister_class(WriteMaterials)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    # handle the keymap
    #for km, kmi in addon_keymaps:
    #    km.keymap_items.remove(kmi)
    #addon_keymaps.clear()
if __name__ == "__main__":
    register()