bl_info = {
    "name": "Nothing-is-3D tools",
    "description": "Some scripts 3D realtime workflow oriented.",
    "author": "Vincent (V!nc3r) Lamy",
    "location": "3D view toolshelf > Nthg-is-3D tab",
    "category": "3D View",
    "wiki_url": 'https://github.com/Vinc3r/BlenderScripts',
    "tracker_url": 'https://github.com/Vinc3r/BlenderScripts/issues',
    "version": (1, 0, 0),
}

"""A bunch of Thanks for some snippets, ideas, inspirations, to:
    - of course, Ton & all Blender devs,
    - Henri Hebeisen (henri-hebeisen.com), Pitiwazou (pitiwazou.com), Pistiwique (github.com/pistiwique),
    - and finally all Blender community and the ones I forget.
"""

# from https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
    from importlib import reload
    if "meshes" in locals():
        reload(meshes)
    if "materials_bi" in locals():
        reload(materials_bi)
    if "commons" in locals():
        reload(selection_sets)
    if "stats" in locals():
        reload(stats)
    print("addOn Nothing-is-3D tools reloaded")
else:
    from . import meshes, materials_bi, selection_sets, stats
    print("addOn Nothing-is-3D tools imported")

import bpy
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty


class NTHG3D_PT_MaterialBIPanel(bpy.types.Panel):
    bl_idname = "nothing3d.material_bi_panel"
    bl_label = "Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Nthg is 3D"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.render.engine == "BLENDER_RENDER" or bpy.context.scene.render.engine == "BLENDER_GAME"

    def draw(self, context):
        layout = self.layout
        fbxCleanerBox = layout.box()
        fbxCleanerBox.label(text="Import cleaner:")
        row = fbxCleanerBox.row(align=True)
        row.operator("nothing3d.mtl_bi_buttons",
                     text="intensity", icon="ANTIALIASED").action = "reset_intensity"
        row.operator("nothing3d.mtl_bi_buttons",
                     text="color", icon="MATSPHERE").action = "reset_color"
        row.operator("nothing3d.mtl_bi_buttons",
                     text="spec", icon="MESH_CIRCLE").action = "reset_spec"
        row.operator("nothing3d.mtl_bi_buttons",
                     text="alpha", icon="IMAGE_RGB_ALPHA").action = "reset_alpha"


class NTHG3D_OT_MaterialBIButtons(bpy.types.Operator):
    # note: no uppercase char in idname, use _ instead!
    bl_idname = "nothing3d.mtl_bi_buttons"
    bl_label = "Add material Blender Internal panel buttons"
    action = bpy.props.StringProperty()

    def execute(self, context):
        if self.action == "reset_intensity":
            materials_bi.reset_intensity()
        if self.action == "reset_color":
            materials_bi.reset_color_value()
        if self.action == "reset_spec":
            materials_bi.reset_spec_value()
        if self.action == "reset_alpha":
            materials_bi.reset_alpha_value()
        return{'FINISHED'}


class NTHG3D_PT_MeshPanel(bpy.types.Panel):
    bl_label = "Meshes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Nthg is 3D"

    def draw(self, context):
        layout = self.layout
        UVchanBox = layout.box()
        UVchanBox.label(text="UV channels :")
        row = UVchanBox.row(align=True)
        row.label(text="Select:")
        row.operator("nothing3d.mesh_buttons", text="1").action = "select_UV1"
        row.operator("nothing3d.mesh_buttons", text="2").action = "select_UV2"
        row = UVchanBox.row()
        row.operator("nothing3d.mesh_buttons",
                     text="Rename channels").action = "rename_UV"


class NTHG3D_OT_MeshButtons(bpy.types.Operator):
    # note: no uppercase char in idname, use _ instead!
    bl_idname = "nothing3d.mesh_buttons"
    bl_label = "Add mesh panel buttons"
    action = bpy.props.StringProperty()

    def execute(self, context):
        if self.action == "rename_UV":
            meshes.rename_UV_channels()
        if self.action == "select_UV1":
            meshes.activate_UV_channels(0)
        if self.action == "select_UV2":
            meshes.activate_UV_channels(1)
        return{'FINISHED'}


class NTHG3D_PT_StatsPanel(bpy.types.Panel):
    bl_label = "Stats"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()

        if scene.stats_enabled == True:
            row.operator("nothing3d.stats_buttons",
                         text="Enable").show_stats = False
        else:
            row.operator("nothing3d.stats_buttons",
                         text="Disable").show_stats = True
            statsTable, totalStatsTable = stats.calculate_mesh_stats()

            box = layout.box()
            row = box.row(align=True)
            row.label(text="Object")
            row.label(text="Verts")
            row.label(text="Tris")
            if statsTable is not None:
                for obj in statsTable:
                    print(obj[0])
                    row = box.row(align=True)
                    row.operator("nothing3d.stats_buttons", text=str(
                        obj[0]), emboss=True).mesh_to_select = obj[0]
                    row.label(text=str(obj[1]))
                    if not obj[3]:
                        row.label(text=str(obj[2]))
                    else:
                        # visual indicator if ngon
                        row.label(text="± %i" % (obj[2]))
            # show total stats
            row = box.row(align=True)
            row.label(text="TOTAL")
            if totalStatsTable != 0:
                row.label(text="%i" % (totalStatsTable[0]))
                row.label(text="%i" % (totalStatsTable[1]))
            else:
                row.label(text="-")
                row.label(text="-")


class NTHG3D_OT_StatsPanel(bpy.types.Operator):
    bl_idname = "nothing3d.stats_buttons"
    bl_label = "Toogle stats panel"
    mesh_to_select = bpy.props.StringProperty()
    show_stats = bpy.props.BoolProperty()

    def execute(self, context):
        if self.mesh_to_select is not "":
            context.scene.objects.active = bpy.data.objects[str(
                self.mesh_to_select)]
        if self.show_stats:
            context.scene.stats_enabled = True
        else:
            context.scene.stats_enabled = False
        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.stats_enabled = bpy.props.BoolProperty(default=False)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.stats_enabled


if __name__ == "__main__":
    register()
