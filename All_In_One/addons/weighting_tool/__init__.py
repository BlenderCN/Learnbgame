"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Bone weighting utility

"""

bl_info = {
    "name": "Weighting Tools",
    "author": "Thomas Larsson",
    "version": "1.02",
    "blender": (2, 6, 6),
    "location": "View3D > Properties > MH Weighting Tools",
    "description": "MakeHuman Utilities",
    "warning": "",
    'wiki_url': "http://www.makehuman.org",
    "category": "Learnbgame"
}

if "bpy" in locals():
    print("Reloading MH weighting tools v %s" % bl_info["version"])
    import imp
    imp.reload(numbers)
    imp.reload(vgroup)
    imp.reload(symmetry)
    imp.reload(helpers)
    imp.reload(export)
    imp.reload(varia)
    imp.reload(io_json)
else:
    print("Loading MH weighting tools v %s" % bl_info["version"])
    import bpy
    import os
    from bpy.props import *
    from . import numbers
    from . import vgroup
    from . import symmetry
    from . import helpers
    from . import export
    from . import varia
    from . import io_json

#
#    class MhxWeightToolsPanel(bpy.types.Panel):
#

class MhxWeightToolsPanel(bpy.types.Panel):
    bl_label = "MH Weighting Tools v %s" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.prop(scn, "MhxShowNumbers")
        if scn.MhxShowNumbers:
            layout.operator("mhw.print_vnums")
            layout.operator("mhw.print_first_vnum")
            layout.operator("mhw.print_enums")
            layout.operator("mhw.print_fnums")
            layout.operator("mhw.select_quads")
            layout.prop(scn, 'MhxVertNum')
            layout.operator("mhw.select_vnum")
            layout.operator("mhw.list_vert_pairs")
            layout.separator()


        layout.prop(scn, "MhxShowVGroups")
        if scn.MhxShowVGroups:
            layout.operator("mhw.show_only_group")
            layout.operator("mhw.remove_unlinked_from_group")

            layout.separator()
            layout.operator("mhw.unvertex_selected")
            layout.operator("mhw.unvertex_diamonds")
            layout.operator("mhw.delete_diamonds")
            layout.operator("mhw.integer_vertex_groups")
            layout.operator("mhw.copy_vertex_groups")
            layout.operator("mhw.remove_vertex_groups")
            layout.separator()
            layout.prop(scn, "MhxBlurFactor")
            layout.operator("mhw.blur_vertex_groups")
            layout.operator("mhw.prune_four")
            layout.prop(scn, "MhxVG0")
            layout.prop(scn, "MhxFactor")
            layout.operator("mhw.factor_vertex_group")
            layout.separator()

            layout.prop(scn, "MhxVG0")
            layout.prop(scn, "MhxVG1")
            layout.prop(scn, "MhxVG2")
            layout.prop(scn, "MhxVG3")
            layout.prop(scn, "MhxVG4")
            layout.operator("mhw.merge_vertex_groups")

            layout.label('Weight pair')
            layout.prop(context.scene, 'MhxWeight')
            layout.operator("mhw.multiply_weights")
            layout.prop(context.scene, 'MhxBone1')
            layout.prop(context.scene, 'MhxBone2')
            layout.operator("mhw.pair_weight")
            layout.operator("mhw.ramp_weight")
            layout.operator("mhw.create_left_right")

            layout.separator()
            layout.operator("mhw.weight_lid", text="Weight Upper Left Lid").lidname = "uplid.L"
            layout.operator("mhw.weight_lid", text="Weight Lower Left Lid").lidname = "lolid.L"


        layout.prop(scn, "MhxShowSymmetry")
        if scn.MhxShowSymmetry:
            layout.prop(scn, "MhxEpsilon")
            row = layout.row()
            row.label("Weights")
            row.operator("mhw.symmetrize_weights", text="L=>R").left2right = True
            row.operator("mhw.symmetrize_weights", text="R=>L").left2right = False

            row = layout.row()
            row.label("Clean")
            row.operator("mhw.clean_right", text="Right side of left vgroups").doRight = True
            row.operator("mhw.clean_right", text="Left side of right vgroups").doRight = False

            row = layout.row()
            row.label("Shapes")
            row.operator("mhw.symmetrize_shapes", text="L=>R").left2right = True
            row.operator("mhw.symmetrize_shapes", text="R=>L").left2right = False

            #row = layout.row()
            #row.label("Verts")
            #row.operator("mhw.symmetrize_verts", text="L=>R").left2right = True
            #row.operator("mhw.symmetrize_verts", text="R=>L").left2right = False

            row = layout.row()
            row.label("Selection")
            row.operator("mhw.symmetrize_selection", text="L=>R").left2right = True
            row.operator("mhw.symmetrize_selection", text="R=>L").left2right = False

            layout.separator()


        layout.prop(scn, "MhxShowExport")
        if scn.MhxShowExport:
            layout.prop(scn, 'MhxVertexGroupFile', text="File")
            row = layout.row()
            row.prop(scn, 'MhxExportAsWeightFile', text="As Weight File")
            row.prop(scn, 'MhxExportSelectedOnly', text="Selected Only")
            row.prop(scn, 'MhxVertexOffset', text="Offset")
            layout.operator("mhw.export_vertex_groups")
            layout.operator("mhw.export_left_right")
            layout.operator("mhw.export_sum_groups")
            layout.operator("mhw.export_custom_shapes")
            layout.operator("mhw.print_vnums_to_file")
            layout.operator("mhw.read_vnums_from_file")
            layout.operator("mhw.print_fnums_to_file")
            layout.separator()
            layout.operator("mhw.shapekeys_from_objects")
            layout.operator("mhw.export_shapekeys")


        layout.prop(scn, "MhxShowVaria")
        if scn.MhxShowVaria:
            layout.operator("mhw.localize_files")
            layout.operator("mhw.transfer_vgroups")
            layout.operator("mhw.check_vgroups_sanity")
            layout.separator()
            layout.operator("mhw.create_hair_rig")
            layout.separator()
            layout.operator("mhw.statistics")


        layout.prop(scn, "MhxShowHelpers")
        if scn.MhxShowHelpers:
            layout.operator("mhw.join_meshes")
            layout.operator("mhw.fix_base_file")
            layout.operator("mhw.project_weights")
            layout.operator("mhw.smoothen_skirt")
            layout.operator("mhw.project_materials")
            layout.operator("mhw.export_base_obj")


#
#    initInterface(context):
#    class VIEW3D_OT_InitInterfaceButton(bpy.types.Operator):
#

def initInterface(context):
    bpy.types.Scene.MhxEpsilon = FloatProperty(
        name="Epsilon",
        description="Maximal distance for identification",
        default=1.0e-3,
        min=0, max=1)

    bpy.types.Scene.MhxFactor = FloatProperty(
        name="Factor",
        default=1.0,
        min=0, max=2)

    bpy.types.Scene.MhxVertNum = IntProperty(
        name="Vert number",
        description="Vertex number to select")

    bpy.types.Scene.MhxBlurFactor = FloatProperty(
        name="Blur Factor",
        default=0,
        min=0, max=1)

    bpy.types.Scene.MhxWeight = FloatProperty(
        name="Weight",
        description="Weight of bone1, 1-weight of bone2",
        default=1.0,
        min=0, max=1)

    bpy.types.Scene.MhxBone1 = StringProperty(
        name="Bone 1",
        maxlen=40,
        default='Bone1')

    bpy.types.Scene.MhxBone2 = StringProperty(
        name="Bone 2",
        maxlen=40,
        default='Bone2')

    bpy.types.Scene.MhxExportAsWeightFile = BoolProperty(
        name="Export as weight file",
        default=False)

    bpy.types.Scene.MhxExportSelectedOnly = BoolProperty(
        name="Export selected verts only",
        default=False)

    bpy.types.Scene.MhxVertexOffset = IntProperty(
        name="Offset",
        default=0,
        description="Export vertex numbers with offset")

    bpy.types.Scene.MhxVertexGroupFile = StringProperty(
        name="Vertex group file",
        maxlen=100,
        default="/home/vgroups.txt")


    bpy.types.Scene.MhxVG0 = StringProperty(name="MhxVG0", maxlen=40, default='')
    bpy.types.Scene.MhxVG1 = StringProperty(name="MhxVG1", maxlen=40, default='')
    bpy.types.Scene.MhxVG2 = StringProperty(name="MhxVG2", maxlen=40, default='')
    bpy.types.Scene.MhxVG3 = StringProperty(name="MhxVG3", maxlen=40, default='')
    bpy.types.Scene.MhxVG4 = StringProperty(name="MhxVG4", maxlen=40, default='')

    bpy.types.Scene.MhxShowNumbers = BoolProperty(name="Show numbers", default=False)
    bpy.types.Scene.MhxShowVGroups = BoolProperty(name="Show vertex groups", default=False)
    bpy.types.Scene.MhxShowSymmetry = BoolProperty(name="Show symmetry", default=False)
    bpy.types.Scene.MhxShowHelpers = BoolProperty(name="Show helpers", default=False)
    bpy.types.Scene.MhxShowExport = BoolProperty(name="Show export", default=False)
    bpy.types.Scene.MhxShowVaria = BoolProperty(name="Show varia", default=False)
    return

#
#    Init and register
#

initInterface(bpy.context)

def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()


