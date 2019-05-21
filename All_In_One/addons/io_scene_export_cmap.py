bl_info = {
    "name": "Export cube map .cmap for VectorBlast",
    "author": "KaadmY",
    "version": (0, 1),
    "blender": (2, 69, 0),
    "location": "File > Import-Export > cube map (.cmap)",
    "description": "Export cube map(.cmap)",
    "warning": "",
    "category": "Learnbgame"
}

import bpy
import math
import json
import mathutils

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

def write(filepath):
    out=""

    scene=bpy.context.scene

    for ob in bpy.context.selected_objects:
        if ob.type == "MESH":
            if ob.cmap.MeshEntityType in ["cube", "physcube", "gfxcube", "glasscube"]:
                size=ob.dimensions
                pos=ob.location-(size*0.5)
                pos.z+=size.z*0.5
                args=[pos.x, pos.y, pos.z, size.x, size.y, size.z]
                if ob.cmap.MeshEntityType in ["cube", "gfxcube", "glasscube"]:
                    args.append(ob.cmap.CubeTextureScale)
                    if ob.cmap.CubeTopTexture != "":
                        args.append(ob.cmap.CubeTopTexture)
                    if ob.cmap.CubeBottomTexture != "":
                        args.append(ob.cmap.CubeBottomTexture)
                    if ob.cmap.CubeSideTexture != "":
                        args.append(ob.cmap.CubeSideTexture)
            elif ob.cmap.MeshEntityType == "jumppad":
                size=ob.dimensions
                pos=ob.location-(size*0.5)
                pos.z+=size.z*0.5

                vel=[
                    ob.cmap.JumppadX,
                    ob.cmap.JumppadY,
                    ob.cmap.JumppadZ]

                args=[pos.x, pos.y, pos.z, size.x, size.y, size.z, vel[0], vel[1], vel[2]]
            else:
                args=[]
            out+=ob.cmap.MeshEntityType+", "+", ".join([str(x) for x in args])+"\n"
            
        elif ob.type == "EMPTY":
            if ob.cmap.EmptyEntityType in ["model"]:
                pos=ob.location
                rot=ob.rotation_euler
                args=[pos.x, pos.y, pos.z, math.degrees(rot[2]), ob.cmap.ModelName]
            else:
                args=[]
            out+=ob.cmap.EmptyEntityType+", "+", ".join([str(x) for x in args])+"\n"

    f=open(filepath, "w")
    f.write(out)
    f.close()

def get_items(obtype):
    items=[]

    if obtype == "MESH":
        items.append(("cube", "Cube", "The default cube"))
        items.append(("glasscube", "Glass cube", "Half-transparent cube"))
        items.append(("gfxcube", "Graphics-only cube", "This will not calculate physics"))
        items.append(("physcube", "Physics-only cube", "This will not draw"))
        items.append(("jumppad", "Jumppad", "This will fling you in whatever direction you set"))
    elif obtype == "EMPTY":
        items.append(("dummy", "Dummy", "Entity that won't export; use for placeholders"))
        items.append(("model", "Model", "Draw a mapmodel at this position"))

    return items

class CubemapExporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.cmap"
    bl_label = "Export Cubemap"

    filename_ext = ".cmap"
    filter_glob = StringProperty(default="*.cmap", options={'HIDDEN'})

    def execute(self, context):
        write(self.filepath)

        return {'FINISHED'}

class CubemapObjectSettings(bpy.types.PropertyGroup):

    MeshEntityType=bpy.props.EnumProperty(
        name="Entity type",
        description="The object entity type",
        items=get_items("MESH"),
        default=get_items("MESH")[0][0],
        )
    
    CubeTopTexture=bpy.props.StringProperty(
        name="Top texture",
        description="What texture the cube will have on top(Empty for default)",
        default=""
        )

    CubeBottomTexture=bpy.props.StringProperty(
        name="Bottom texture",
        description="What texture the cube will have on bottom(Empty for default)",
        default=""
        )

    CubeSideTexture=bpy.props.StringProperty(
        name="Side texture",
        description="What texture the cube will have on its sides(Empty for default)",
        default=""
        )

    CubeTextureScale=bpy.props.FloatProperty(
        name="Texture scale",
        description="The texture scale; defaults to 0.5",
        default=0.5
        )

    JumppadX=bpy.props.FloatProperty(
        name="Jumppad X",
        description="The force to push the player in the X direction",
        default=0
        )

    JumppadY=bpy.props.FloatProperty(
        name="Jumppad Y",
        description="The force to push the player in the Y direction",
        default=0
        )

    JumppadZ=bpy.props.FloatProperty(
        name="Jumppad Z",
        description="The force to push the player in the Z direction",
        default=10
        )

    EmptyEntityType=bpy.props.EnumProperty(
        name="Entity type",
        description="The object entity type",
        items=get_items("EMPTY"),
        default=get_items("EMPTY")[0][0],
        )
    
    ModelName=bpy.props.StringProperty(
        name="Model name",
        description="The model name, ie. light01",
        default=""
        )

class CubemapObjectPanel(bpy.types.Panel):
    bl_label="Cubemap Object panel"
    bl_space_type="PROPERTIES"
    bl_region_type="WINDOW"
    bl_context="object"

    @classmethod
    def poll(self, context):
        obj=bpy.context.active_object
        if not obj:
            return False
        if obj.type in ["EMPTY", "MESH"]:
            return True
        return False

    def draw(self, context):
        obj=bpy.context.active_object
        layout=self.layout
        if obj.type == "MESH":
            layout.prop(obj.cmap, "MeshEntityType")
            if obj.cmap.MeshEntityType in ["gfxcube", "cube", "glasscube"]:
                layout.prop(obj.cmap, "CubeTopTexture")
                layout.prop(obj.cmap, "CubeBottomTexture")
                layout.prop(obj.cmap, "CubeSideTexture")
                layout.prop(obj.cmap, "CubeTextureScale")
            elif obj.cmap.MeshEntityType == "jumppad":
                layout.prop(obj.cmap, "JumppadX")
                layout.prop(obj.cmap, "JumppadY")
                layout.prop(obj.cmap, "JumppadZ")
        elif obj.type == "EMPTY":
            layout.prop(obj.cmap, "EmptyEntityType")
            if obj.cmap.EmptyEntityType == "model":
                layout.prop(obj.cmap, "ModelName")

def menu_export(self, context):
    self.layout.operator(CubemapExporter.bl_idname, text="Cube map (.cmap)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Object.cmap=bpy.props.PointerProperty(type=CubemapObjectSettings)

    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
