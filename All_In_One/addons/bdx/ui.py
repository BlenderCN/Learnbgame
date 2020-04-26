import os
import bpy
from . import utils as ut

P = bpy.props

class BdxSceneProps(bpy.types.PropertyGroup):
    proj_name = P.StringProperty(name="Project Name")
    java_pack = P.StringProperty(name="Java Package")
    base_path = P.StringProperty(name="Base Path", subtype="DIR_PATH")
    dir_name = P.StringProperty(name="Directory")
    android_sdk = P.StringProperty(name="Android SDK", subtype="DIR_PATH")
    
class BdxObjectProps(bpy.types.PropertyGroup):
    cls_use_custom = P.BoolProperty(name="", description="Use custom Java class for this object")
    cls_custom_name = P.StringProperty(name="", description="Java class name for this object")
    cls_use_priority = P.BoolProperty(name="", description="Use execution priority for this object")
    
bpy.utils.register_class(BdxSceneProps)
bpy.utils.register_class(BdxObjectProps)
bpy.types.Scene.bdx = P.PointerProperty(type=BdxSceneProps)
bpy.types.Object.bdx = P.PointerProperty(type=BdxObjectProps)

prop_move_support = sum([n * pow(10, i) for n, i in zip(bpy.app.version, (4, 2, 0))]) >= 27500


class BdxProject(bpy.types.Panel):
    """Crates the BDX panel in the render properties window"""
    bl_idname = "RENDER_PT_bdx"
    bl_label = "BDX"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        r = layout.row

        if ut.in_bdx_project():
            r().label(text="In BDX project: " + ut.project_name())

            r().operator("object.bdxexprun")
            r().operator("object.packproj")
            r().operator("object.externjava")

        else:
            sc_bdx = context.scene.bdx

            if ut.in_packed_bdx_blend():
                r().label(text="In packed BDX blend.")
            else:
                r().prop(sc_bdx, "proj_name")
                r().prop(sc_bdx, "java_pack")
                r().prop(sc_bdx, "base_path")
                r().prop(sc_bdx, "dir_name")
                r().prop(sc_bdx, "android_sdk")

            r().operator("scene.create_bdx_project", text="Create BDX project")


class BdxObject(bpy.types.Panel):
    """Creates the BDX Panel in the Object properties window"""
    bl_label = "BDX"
    bl_idname = "OBJECT_PT_bdx"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        ob = context.object
        ob_bdx = ob.bdx
        game = ob.game

        layout = self.layout

        row = layout.row()
        col = row.column()
        if ob_bdx.cls_use_priority:
            col.prop(ob_bdx, "cls_use_priority", icon="FONTPREVIEW")
        else:
            col.prop(ob_bdx, "cls_use_priority", icon="BOOKMARKS")
        col = row.column()
        if ob_bdx.cls_use_custom:
            col.active = True
            col.prop(ob_bdx, "cls_custom_name")
        else:
            col.active = False
            col.label(ob.name + ".java")
        col = row.column()
        col.prop(ob_bdx, "cls_use_custom")
        
        row = layout.row(align=True)
        is_font = (ob.type == "FONT")
        if is_font:
            prop_index = game.properties.find("Text")
            if prop_index != -1:
                layout.operator("object.game_property_remove", text="Remove Text Game Property", icon="X").index = prop_index
                row = layout.row()
                sub = row.row()
                sub.enabled = 0
                prop = game.properties[prop_index]
                sub.prop(prop, "name", text="")
                row.prop(prop, "type", text="")
                row.label("See Text Object")
            else:
                props = layout.operator("object.game_property_new", text="Add Text Game Property", icon="ZOOMIN")
                props.name = "Text"
                props.type = "STRING"

        props = layout.operator("object.game_property_new", text="Add Game Property", icon="ZOOMIN")
        props.name = ""

        for i, prop in enumerate(game.properties):
            if is_font and i == prop_index:
                continue
            box = layout.box()
            row = box.row()
            row.prop(prop, "name", text="")
            row.prop(prop, "type", text="")
            row.prop(prop, "value", text="")
            row.prop(prop, "show_debug", text="", toggle=True, icon="INFO")
            if prop_move_support:
                sub = row.row(align=True)
                props = sub.operator("object.game_property_move", text="", icon="TRIA_UP")
                props.index = i
                props.direction = "UP"
                props = sub.operator("object.game_property_move", text="", icon="TRIA_DOWN")
                props.index = i
                props.direction = "DOWN"
            row.operator("object.game_property_remove", text="", icon="X", emboss=False).index = i


def register():
    bpy.utils.register_class(BdxProject)
    bpy.utils.register_class(BdxObject)

    @bpy.app.handlers.persistent
    def P_mapto_bdxexprun(dummy):
        """Override P to export and run BDX game, instead of running BGE game"""

        kmi = bpy.data.window_managers["WinMan"].keyconfigs["Blender"].keymaps["Object Mode"].keymap_items

        if ut.in_bdx_project():
            if "view3d.game_start" in kmi:
                kmi["view3d.game_start"].idname = "object.bdxexprun"
        else:
            if "objects.bdxexprun" in kmi:
                kmi["objects.bdxexprun"].idname = "view3d.game_start"

    bpy.app.handlers.load_post.append(P_mapto_bdxexprun)


def unregister():
    bpy.utils.unregister_class(BdxProject)
    bpy.utils.unregister_class(BdxObject)


if __name__ == "__main__":
    register()
