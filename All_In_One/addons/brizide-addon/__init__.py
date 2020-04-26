import os
import bpy
import json
from mathutils import Matrix
from bpy.props import (
    BoolProperty,
    # BoolVectorProperty,
    # EnumProperty,
    # FloatProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    # CollectionProperty,
    # IntVectorProperty,
    # FloatVectorProperty,
    PointerProperty
)

bl_info = {"name": "BriZide", "category": "Learnbgame",
}


def enable_texture_mode():
    """ Enables textured shading in the viewport """
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.viewport_shade = "TEXTURED"
    return


def setup_blender():
        bpy.context.scene.render.engine = "BLENDER_GAME"
        bpy.data.worlds["World"].light_settings.use_environment_light = True
        bpy.data.worlds["World"].light_settings.environment_energy = 2.0
        bpy.context.scene.game_settings.material_mode = "GLSL"
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.space_data.clip_end = 10000.0
        bpy.context.space_data.show_backface_culling = True
        bpy.context.space_data.grid_scale = 32

        enable_texture_mode()


def load_level(context):
    props = context.scene.brizide
    level_name = props.level
    level_path = os.path.join(props.game_path, "levels")
    print(f"Loading {level_name}")
    with open(os.path.join(level_path, level_name), "r") as f:
        level = json.load(f)
    for block in level["blocks"]:
        ob = bpy.data.objects.get(block["type"])
        ob_dup = ob.copy()
        ob_dup.matrix_world = Matrix(block["orientation"]).to_4x4()
        ob_dup.location = block["position"]
        bpy.data.scenes[0].objects.link(ob_dup)

    props.cube_size = int(level["cube_size"])
    props.author = level["author"]
    props.version = int(level["version"])
    
    return level


def save_level(context):
    sce = bpy.context.scene
    blocks = []


    props = context.scene.brizide

    for obj in sce.objects:
        if not obj.layers[0]:
            continue
        if "Block_" in obj.name:

            # Save the start orientation as an euler matrix
            wo = obj.matrix_world.to_3x3()

            block = {
                "type" : obj.name.split('.')[0],
                "position" : [obj.location[0],
                    obj.location[1],
                    obj.location[2]],
                "orientation" : [list(v) for v in wo],
                "properties" : {}
            }


            # Copy properties set by the level editor into the dict
            # for prop in obj.getPropertyNames():
            #     try:
            #         properties[prop] = block[prop]
            #     except Exception as e:
            #         print(e)
            blocks.append(block)

    blk_file = {
        "name": props.level_name,
        "cube_size": props.cube_size,
        "version" : 1,
        "author" : props.author,
        "blocks" : blocks
    }

    json_path = os.path.join(props.game_path, "levels", props.level_name)
    with open(json_path, 'w') as outfile:
        json.dump(blk_file, outfile, sort_keys=False, indent=4)

    print("Saved level file.")


def load_blocklib():
    props = bpy.context.scene.brizide
    brizide_path = props.game_path
    scn = bpy.context.scene
    filepath = os.path.join(brizide_path, "components", "blocklib.blend")
    obj_name = "Block_"

    with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith(obj_name)]

    load_objs = []
    for obj in data_to.objects:
        
        if obj is not None and not obj.name in scn.objects:
           o = scn.objects.link(obj)
           o.layers[1] = True
           o.layers[0] = False
           load_objs.append(obj)
    
    return load_objs


def resize_cube(self, context):
    if "CubeSimple" in context.scene.objects:
        context.scene.objects["CubeSimple"].scale = [self.cube_size for x in range(3)]
        context.scene.objects["CubeSimple"].location = [(self.cube_size*32)/2 - 16, (self.cube_size*32)/2 - 16, (self.cube_size*32)/2 - 16]
        bpy.data.materials["Floor"].texture_slots[0].scale = [self.cube_size for x in range(3)]
        bpy.data.materials["Floor"].texture_slots[0].offset = [1.0 if self.cube_size % 2 else 0.5 for x in range(3)]
    else:
        load_cube(self.cube_size)
        setup_blender()


def load_cube(cube_size):
    if "CubeSimple" in bpy.context.scene.objects:
        return
    scn = bpy.context.scene
    props = scn.brizide
    load_objs = []
    brizide_path = props.game_path
    filepath = os.path.join(brizide_path, "components", "cube.blend")
    obj_name = "CubeSimple"

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name.startswith(obj_name)]

    for obj in data_to.objects:
        obj.scale = [cube_size for x in range(3)]
        obj.location = [(cube_size*32)/2 - 16, (cube_size*32)/2 - 16, (cube_size*32)/2 - 16]
        bpy.data.materials["Floor"].texture_slots[0].offset = [1.0 if cube_size % 2 else 0.5 for x in range(3)]
        bpy.data.materials["Floor"].texture_slots[0].scale = [cube_size for x in range(3)]
        obj.hide_select = True
        if not obj.name in scn.objects:
            bpy.data.scenes[0].objects.link(obj)


def get_levels(self, context):
    items = []
    if self.game_path:
        levels = os.listdir(os.path.join(self.game_path, "levels"))
        items = [(levels[x], levels[x], "", x) for x in range(len(levels))]
    return sorted(items)
    

def select_level(self, context):
    context.scene.brizide.level_name = context.scene.brizide.level


class LoadBrizide(bpy.types.Operator):
    bl_idname = "brizide.load"
    bl_label = "Load"
    bl_description = "Load level"

    def execute(self, context):
        blocklib = load_blocklib()
        level = load_level(context)
        # for obj in blocklib:
        #    bpy.data.objects.remove(obj, do_unlink=True)
        load_cube(level["cube_size"])
        setup_blender()

        return {"FINISHED"}


class SaveBrizide(bpy.types.Operator):
    bl_idname = "brizide.save"
    bl_label = "Save"
    bl_description = "Save level"

    def execute(self, context):
        save_level(context)

        return {"FINISHED"}


class GetBlocks(bpy.types.Operator):
    bl_idname = "brizide.get_blocks"
    bl_label = "Get all Blocks"
    bl_description = "Dumps all blocks into the scene"

    def execute(self, context):
        load_blocklib()
        for ob in context.scene.objects:
            if ob.layers[1]:
                ob_dup = ob.copy()
                bpy.data.scenes[0].objects.link(ob_dup)
        setup_blender()

        return {"FINISHED"}


class BriZidePanel(bpy.types.Panel):
    """

    """
    bl_label = "BriZide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "BriZide"

    def draw_header(self, context):
        self.layout.label("", icon="SCRIPTWIN")

    def draw(self, context):
        props = context.scene.brizide
        layout = self.layout

        # General settings
        
        layout.label("BriZide Directory:")
        box = self.layout.box()
        box.prop(props, "game_path", text="")
        if props.game_path == "":
            box.label("No directory specified", icon="INFO")
            return
        elif os.path.isdir(props.game_path):
            if "brizide.blend" in os.listdir(props.game_path):
                box.label(
                    "Folder exists",
                    icon="FILE_TICK"
                )
            else:
                box.label(
                    "Folder exists, BriZide not found",
                    icon="INFO"
                )
        else:
            box.label("Not found", icon="ERROR")
            return
            
        layout.separator()

        col = layout.column(align=True)

        col.prop(props, "author")
        col.prop(props, "version")
        col.prop(props, "cube_size")

        layout.separator()
        
        col = layout.column(align=True)
        col.prop(props, "level", text="Level")
        col.operator("brizide.load")

        col = layout.column(align=True)
        col.prop(props, "level_name", text="Save as")
        col.operator("brizide.save")

        layout.separator()

        layout.operator("brizide.get_blocks")


class BriZideSceneProps(bpy.types.PropertyGroup):
    game_path = StringProperty(
        name = "BriZide Path",
        default = "",
        description = "Path of the game folder"
    )
    level_name = StringProperty(
        name = "Level Name",
        default = "template.json",
        description = "Levelname including .json"
    )
    level = EnumProperty(
        items = get_levels,
        update = select_level
    )
    cube_size = IntProperty(
        name = "Cube Size",
        default = 60,
        min = 0,
        description = "Size of the level cube. 0 to disable",
        update = resize_cube
    )
    version = IntProperty(
        name = "Version",
        default = 0,
        description = "Version of the game the level was made for"
    )
    author = StringProperty(
        name = "Author",
        default = "",
        description = "Author of the Level"
    )


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.brizide = bpy.props.PointerProperty(
        type=BriZideSceneProps
    )
