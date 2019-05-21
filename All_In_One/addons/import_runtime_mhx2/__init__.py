# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    'name': 'Import-Runtime: MakeHuman Exchange 2 (.mhx2)',
    'author': 'Thomas Larsson',
    'version': (0,28),
    "blender": (2, 74, 0),
    'location': "File > Import > MakeHuman (.mhx2)",
    'description': 'Import files in the new MakeHuman eXhange format (.mhx2)',
    'warning': '',
    'wiki_url': 'http://thomasmakehuman.wordpress.com/mhx2-documentation/',
    'category': 'MakeHuman'}

if "bpy" in locals():
    print("Reloading MHX2 importer-runtime v %d.%d" % bl_info["version"])
    import imp
    imp.reload(armature)
    imp.reload(hm8)
    imp.reload(utils)
    imp.reload(error)
    imp.reload(config)
    imp.reload(load_json)
    imp.reload(masks)
    imp.reload(materials)
    imp.reload(shaders)
    imp.reload(proxy)
    imp.reload(hair)
    imp.reload(geometries)
    imp.reload(layers)
    imp.reload(fkik)
    imp.reload(drivers)
    imp.reload(bone_drivers)
    imp.reload(faceshift)
    imp.reload(hide)
    imp.reload(shapekeys)
    imp.reload(visemes)
    imp.reload(merge)
    imp.reload(importer)
else:
    print("Loading MHX2 importer-runtime v %d.%d" % bl_info["version"])
    from . import armature
    from . import hm8
    from . import utils
    from . import error
    from . import config
    from . import load_json
    from . import masks
    from . import materials
    from . import shaders
    from . import proxy
    from . import hair
    from . import geometries
    from . import layers
    from . import fkik
    from . import drivers
    from . import bone_drivers
    from . import faceshift
    from . import hide
    from . import shapekeys
    from . import visemes
    from . import merge
    from . import importer

import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from .error import *
from .utils import *

import os

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

HairColorProperty = FloatVectorProperty(
    name = "Hair Color",
    subtype = "COLOR",
    size = 4,
    min = 0.0,
    max = 1.0,
    default = (0.15, 0.03, 0.005, 1.0)
    )

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

class ImportMHX2(bpy.types.Operator, ImportHelper):
    """Import from MHX2 file format (.mhx2)"""
    bl_idname = "import_scene.makehuman_mhx2"
    bl_description = 'Import from MHX2 file format (.mhx2)'
    bl_label = "Import MHX2"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".mhx2"
    filter_glob = StringProperty(default="*.mhx2", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    useHelpers = BoolProperty(name="Helper Geometry", description="Keep helper geometry", default=False)
    useOffset = BoolProperty(name="Offset", description="Add offset for feet on ground", default=True)
    useOverride = BoolProperty(name="Override Exported Data", description="Override rig and mesh definitions in mhx2 file", default=False)

    useCustomShapes = BoolProperty(name="Custom Shapes", description="Custom bone shapes", default=True)
    useFaceShapes = BoolProperty(name="Face Shapes", description="Face shapes", default=False)
    useFaceShapeDrivers = BoolProperty(name="Face Shape Drivers", description="Drive face shapes with rig properties", default=False)
    useFaceRigDrivers = BoolProperty(name="Face Rig Drivers", description="Drive face rig with rig properties", default=True)
    useFacePanel = BoolProperty(name="Face Panel", description="Face panel", default=False)
    useRig = BoolProperty(name="Add Rig", description="Add rig", default=True)
    finalizeRigify = BoolProperty(name="Finalize Rigify", description="If off, only load metarig. Press Finalize Rigify to complete rigification later", default=True)
    useRotationLimits = BoolProperty(name="Rotation Limits", description="Use rotation limits for MHX rig", default=True)
    useDeflector = BoolProperty(name="Add Deflector", description="Add deflector", default=False)
    useHairDynamics = BoolProperty(name="Hair Dynamics", description="Add dynamics to hair", default=False)
    useHairOnProxy = BoolProperty(name="Hair On Proxy", description="Add hair to proxy rather than base human", default=False)
    useConservativeMasks = BoolProperty(name="Conservative Masks", description="Only delete faces with two delete-verts", default=True)

    useSubsurf = BoolProperty(name="Subsurface", description="Add a subsurf modifier to all meshes", default=False)
    subsurfLevels = IntProperty(name="Levels", description="Subsurface levels (viewport)", default=0)
    subsurfRenderLevels = IntProperty(name=" Render Levels", description="Subsurface levels (render)", default=1)

    useMasks = EnumProperty(
        items = [('IGNORE', "Ignore", "Ignore masks"),
                 ('APPLY', "Apply", "Apply masks (delete vertices permanently)"),
                 ('MODIFIER', "Modifier", "Create mask modifier"),
                 ],
        name = "Masks",
        description = "How to deal with masks",
        default = 'MODIFIER')

    useHumanType = EnumProperty(
        items = [('BASE', "Base", "Base mesh"),
                 ('PROXY', "Proxy", "Exported topology (if exists)"),
                 ('BOTH', "Both", "Both base mesh and proxy mesh"),
                 ],
        name = "Import Human Type",
        description = "Human types to be imported",
        default = 'BOTH')
    mergeBodyParts = BoolProperty(name="Merge Body Parts", description="Merge body parts", default=False)
    mergeToProxy = BoolProperty(name="Merge To Proxy", description="Merge body parts to proxy mesh is such exists", default=False)
    mergeMaxType = EnumProperty(
        items = [('BODY', "Body", "Merge up to body"),
                 ('HAIR', "Hair", "Merge up to hair"),
                 ('CLOTHES', "Clothes", "Merge all"),
                 ],
        name = "Maximum Merge Type",
        description = "Maximum type to merge",
        default = 'BODY')

    rigTypes = []
    folder = os.path.dirname(__file__)
    for file in os.listdir(os.path.join(folder, "armature/data/rigs")):
        fname = os.path.splitext(file)[0]
        if fname == "mhx":
            mhx = ("MHX", "MHX", "An advanced control rig")
        elif fname == "exported_mhx":
            exp_mhx = ("EXPORTED_MHX", "Exported MHX", "MHX rig based on exported deform rig")
        elif fname == "rigify":
            rigify = ("RIGIFY", "Rigify", "Modified Rigify rig")
        elif fname == "exported_rigify":
            exp_rigify = ("EXPORTED_RIGIFY", "Exported Rigify", "Rigify rig based on exported deform rig")
        else:
            entry = (fname.upper(), fname.capitalize(), "%s-compatible rig" % fname.capitalize())
            rigTypes.append(entry)
    rigTypes = [('EXPORTED', "Exported", "Use rig in mhx2 file"),
                exp_mhx, exp_rigify, mhx, rigify] + rigTypes

    rigType = EnumProperty(
        items = rigTypes,
        name = "Rig Type",
        description = "Rig type",
        default = 'EXPORTED')

    genitalia = EnumProperty(
        items = [("NONE", "None", "None"),
                 ("PENIS", "Male", "Male genitalia"),
                 ("PENIS2", "Male 2", "Better male genitalia"),
                 ("VULVA", "Female", "Female genitalia"),
                 ("VULVA2", "Female 2", "Better female genitalia")],
        name = "Genitalia",
        description = "Genitalia",
        default = 'NONE')
    usePenisRig = BoolProperty(name="Penis Rig", description="Add a penis rig", default=False)

    hairlist = [("NONE", "None", "None")]
    folder = os.path.join(os.path.dirname(__file__), "data", "hm8", "hair")
    for file in os.listdir(folder):
        fname,ext = os.path.splitext(file)
        if ext == ".mxa":
            hairlist.append((file, fname, fname))

    hairType = EnumProperty(
        items = hairlist,
        name = "Hair",
        description = "Hair",
        default = "NONE")

    hairColor = HairColorProperty

    def execute(self, context):
        from .config import Config
        cfg = Config().fromSettings(self)
        try:
            importer.importMhx2File(self.filepath, cfg, context)
        except MhxError:
            handleMhxError(context)

        if AutoWeight:
            scn = context.scene
            rig = scn.objects["Bar"]
            ob = scn.objects["Bar:Body"]
            ob.select = True
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "useOverride")
        if not self.useOverride:
            return

        layout.separator()
        layout.label("Import Human Type:")
        layout.prop(self, "useHumanType", expand=True)

        layout.prop(self, "useHelpers")
        layout.prop(self, "useOffset")
        layout.prop(self, "useFaceShapes")
        if (self.useFaceShapes and
            not self.useFacePanel):
            layout.prop(self, "useFaceShapeDrivers")

        layout.separator()
        box = layout.box()
        box.label("Subdivision surface")
        box.prop(self, "useSubsurf")
        if self.useSubsurf:
            box.prop(self, "subsurfLevels")
            box.prop(self, "subsurfRenderLevels")

        layout.separator()
        layout.label("Masking:")
        layout.prop(self, "useMasks", expand=True)
        layout.prop(self, "useConservativeMasks")

        layout.separator()
        box = layout.box()
        box.label("Merging")
        box.prop(self, "mergeBodyParts")
        if self.mergeBodyParts and self.useHumanType != 'BODY':
            box.prop(self, "mergeToProxy")
        if self.mergeBodyParts:
            box.prop(self, "mergeMaxType")

        layout.prop(self, "genitalia", text="Genitalia")

        layout.separator()
        box = layout.box()
        box.prop(self, "hairType")
        if self.hairType != 'NONE':
            box.prop(self, "hairColor")
            box.prop(self, "useHairOnProxy")
            box.prop(self, "useHairDynamics")
        box.prop(self, "useDeflector")

        layout.separator()
        box = layout.box()
        box.label("Rigging")
        box.prop(self, "useRig")
        if self.useRig:
            box.prop(self, "rigType")
            box.prop(self, "useCustomShapes")
            if self.rigType in ('MHX', 'EXPORTED_MHX'):
                box.prop(self, "useRotationLimits")
            #elif self.rigType in ('RIGIFY', 'EXPORTED_RIGIFY'):
            #    box.prop(self, "finalizeRigify")
            if self.useFaceShapes and not self.useFaceShapeDrivers:
                box.prop(self, "useFacePanel")
            if self.rigType[0:8] == 'EXPORTED':                
                box.prop(self, "useFaceRigDrivers")                
            if self.genitalia[0:5] == 'PENIS' and self.rigType[0:8] != 'EXPORTED':
                box.prop(self, "usePenisRig")

#------------------------------------------------------------------------
#    Setup panel
#------------------------------------------------------------------------

class MhxSetupPanel(bpy.types.Panel):
    bl_label = "MHX Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        scn = context.scene

        layout.operator("import_scene.makehuman_mhx2")
        #layout.operator("mhx2.make_skin_shader")

        if (ob is None or
            (ob.type == 'MESH' and not ob.MhxUuid) or
            (ob.type == 'ARMATURE' and not ob.MhxRig) or
            (ob.type not in ['MESH', 'ARMATURE'])):
            return

        layout.separator()
        layout.operator("mhx2.add_simple_materials")
        layout.operator("mhx2.merge_objects")
        if ob.MhxRigify:
            layout.operator("mhx2.finalize_rigify")

        layout.separator()
        box = layout.box()
        box.label("Design Human")
        box.prop(scn, "MhxDesignHuman", text="")
        box.operator("mhx2.set_design_human")
        box.operator("mhx2.clear_design_human")

        layout.separator()
        box = layout.box()
        box.label("Assets")
        box.operator("mhx2.add_asset")
        box.prop(scn, "MhxUseConservativeMasks")
        box.prop(scn, "MhxHairColor")
        box.prop(scn, "MhxUseHairDynamics")
        #box.prop(scn, "MhxUseDeflector")
        box.prop(scn, "MhxMinHairLength")
        box.prop(scn, "MhxMinHairOrientation")
        box.prop(scn, "MhxHairKeySeparation")

        #Not in release
        #box.operator("mhx2.particlify_hair")

        layout.separator()
        box = layout.box()
        box.label("Visibility")
        box.operator("mhx2.add_hide_drivers")
        box.operator("mhx2.remove_hide_drivers")

        layout.separator()
        box = layout.box()
        box.label("Facial Rig")
        #box.operator("mhx2.add_facerig_drivers")
        box.operator("mhx2.remove_facerig_drivers")

        layout.separator()
        box = layout.box()
        box.label("Shapekeys")
        op = box.operator("mhx2.add_shapekeys", text="Add Face Shapes")
        op.filename="data/hm8/faceshapes/faceshapes.mxa"
        box.separator()
        box.operator("mhx2.add_face_shape_drivers")
        box.operator("mhx2.remove_face_shape_drivers")
        box.separator()
        box.operator("mhx2.add_other_shape_drivers")
        box.operator("mhx2.remove_other_shape_drivers")


#------------------------------------------------------------------------
#    Mhx License Panel
#------------------------------------------------------------------------

class MhxLicensePanel(bpy.types.Panel):
    bl_label = "License"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        ob = context.object
        if ob and ob.type == 'MESH':
            layout.label("Mesh:")
            layout.prop(ob, "MhxAuthor", text="Author")
            layout.prop(ob, "MhxLicense", text="License")
            layout.prop(ob, "MhxHomePage", text="Homepage")

            if ob.particle_systems:
                layout.separator()
                layout.label("Hair:")
                layout.prop(ob, "MhxHairAuthor", text="Author")
                layout.prop(ob, "MhxHairLicense", text="License")
                layout.prop(ob, "MhxHairHomePage", text="Homepage")

#------------------------------------------------------------------------
#    Mhx Layers Panel
#------------------------------------------------------------------------

from .layers import MhxLayers, OtherLayers

class MhxLayersPanel(bpy.types.Panel):
    bl_label = "Layers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig in ('MHX', 'EXPORTED_MHX'))

    def draw(self, context):
        layout = self.layout
        layout.operator("mhx2.pose_enable_all_layers")
        layout.operator("mhx2.pose_disable_all_layers")

        rig = context.object
        if rig.MhxRig in ('MHX', 'EXPORTED_MHX'):
            layers = MhxLayers
        else:
            layers = OtherLayers

        for (left,right) in layers:
            row = layout.row()
            if type(left) == str:
                row.label(left)
                row.label(right)
            else:
                for (n, name, prop) in [left,right]:
                    row.prop(rig.data, "layers", index=n, toggle=True, text=name)

        return
        layout.separator()
        layout.label("Export/Import MHP")
        layout.operator("mhx2.saveas_mhp")
        layout.operator("mhx2.load_mhp")


#------------------------------------------------------------------------
#    Mhx FK/IK switch panel
#------------------------------------------------------------------------

class MhxFKIKPanel(bpy.types.Panel):
    bl_label = "FK/IK Switch"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig in ('MHX', 'EXPORTED_MHX'))

    def draw(self, context):
        rig = context.object
        layout = self.layout

        row = layout.row()
        row.label("")
        row.label("Left")
        row.label("Right")

        layout.label("FK/IK switch")
        row = layout.row()
        row.label("Arm")
        self.toggleButton(row, rig, "MhaArmIk_L", " 3", " 2")
        self.toggleButton(row, rig, "MhaArmIk_R", " 19", " 18")
        row = layout.row()
        row.label("Leg")
        self.toggleButton(row, rig, "MhaLegIk_L", " 5", " 4")
        self.toggleButton(row, rig, "MhaLegIk_R", " 21", " 20")

        layout.label("IK Influence")
        row = layout.row()
        row.label("Arm")
        row.prop(rig, '["MhaArmIk_L"]', text="")
        row.prop(rig, '["MhaArmIk_R"]', text="")
        row = layout.row()
        row.label("Leg")
        row.prop(rig, '["MhaLegIk_L"]', text="")
        row.prop(rig, '["MhaLegIk_R"]', text="")

        layout.separator()
        layout.label("Snapping")
        row = layout.row()
        row.label("Rotation Limits")
        row.prop(rig, "MhaRotationLimits", text="")
        #row.prop(rig, "MhxSnapExact", text="Exact Snapping")

        layout.label("Snap Arm bones")
        row = layout.row()
        row.label("FK Arm")
        row.operator("mhx2.snap_fk_ik", text="Snap L FK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx2.snap_fk_ik", text="Snap R FK Arm").data = "MhaArmIk_R 18 19 28"
        row = layout.row()
        row.label("IK Arm")
        row.operator("mhx2.snap_ik_fk", text="Snap L IK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx2.snap_ik_fk", text="Snap R IK Arm").data = "MhaArmIk_R 18 19 28"

        layout.label("Snap Leg bones")
        row = layout.row()
        row.label("FK Leg")
        row.operator("mhx2.snap_fk_ik", text="Snap L FK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx2.snap_fk_ik", text="Snap R FK Leg").data = "MhaLegIk_R 20 21 28"
        row = layout.row()
        row.label("IK Leg")
        row.operator("mhx2.snap_ik_fk", text="Snap L IK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx2.snap_ik_fk", text="Snap R IK Leg").data = "MhaLegIk_R 20 21 28"


    def toggleButton(self, row, rig, prop, fk, ik):
        if getattr(rig, prop) > 0.5:
            row.operator("mhx2.toggle_fk_ik", text="IK").toggle = prop + " 0" + fk + ik
        else:
            row.operator("mhx2.toggle_fk_ik", text="FK").toggle = prop + " 1" + ik + fk


#------------------------------------------------------------------------
#   MHX Control panel
#------------------------------------------------------------------------

class MhxControlPanel(bpy.types.Panel):
    bl_label = "MHX Control"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig in ('MHX', 'EXPORTED_MHX'))

    def draw(self, context):
        ob = context.object
        layout = self.layout

        lrProps = []
        props = []
        lrFaceProps = []
        plist = list(ob.keys())
        plist.sort()
        for prop in plist:
            if prop[0:3] == 'Mha':
                if prop[-2:] == '_L':
                    lrProps.append(prop[:-2])
                elif prop[-2:] != '_R':
                    props.append(prop)

        for prop in props:
            layout.prop(ob,prop, text=prop[3:])

        layout.separator()
        row = layout.row()
        row.label("Left")
        row.label("Right")
        for prop in lrProps:
            row = layout.row()
            row.prop(ob, prop+"_L", text=prop[3:])
            row.prop(ob, prop+"_R", text=prop[3:])

#------------------------------------------------------------------------
#   Visibility panel
#------------------------------------------------------------------------

class VisibilityPanel(bpy.types.Panel):
    bl_label = "Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'ARMATURE' and ob.MhxVisibilityDrivers)

    def draw(self, context):
        ob = context.object
        layout = self.layout
        layout.operator("mhx2.prettify_visibility")
        props = list(ob.keys())
        props.sort()
        for prop in props:
            if prop[0:3] == "Mhh":
                if hasattr(ob, prop):
                    path = prop
                else:
                    path = '["%s"]' % prop
                layout.prop(ob, path, text=prop[3:])

#------------------------------------------------------------------------
#   Facerig panel
#------------------------------------------------------------------------

class FaceUnitsPanel(bpy.types.Panel):
    bl_label = "Face Units"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers)

    def draw(self, context):
        rig = context.object
        layout = self.layout
        layout.operator("mhx2.reset_props", text="Reset Expressions").prefix = "Mfa"
        layout.operator("mhx2.load_faceshift_bvh")
        drawProperties(layout, rig, "Mfa")

#------------------------------------------------------------------------
#   Expression
#------------------------------------------------------------------------

class ExpressionPanel(bpy.types.Panel):
    bl_label = "Expressions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers and rig.MhxExpressions != "")

    def draw(self, context):
        rig = context.object
        layout = self.layout
        layout.operator("mhx2.reset_props", text="Reset Expressions").prefix = "Mfa"
        layout.prop(rig, "MhxExprStrength")
        exprs = rig.MhxExpressions.split("&")
        for ename in exprs:
            btn = layout.operator("mhx2.set_expression", text=ename)
            btn.units = rig["Mhu"+ename]

#------------------------------------------------------------------------
#   Face Shape panel
#------------------------------------------------------------------------

class MhxFaceShapePanel(bpy.types.Panel):
    bl_label = "Facial Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxFaceShapeDrivers)

    def draw(self, context):
        rig = context.object
        if rig:
            layout = self.layout
            layout.operator("mhx2.reset_props").prefix = "Mhf"
            drawProperties(layout, rig, "Mhf")

#------------------------------------------------------------------------
#   Pose panel
#------------------------------------------------------------------------

class MhxPosePanel(bpy.types.Panel):
    bl_label = "Poses"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxPoses)

    def draw(self, context):
        rig = context.object
        layout = self.layout
        for anim in rig.MhxPoses.split("&"):
            aname,rest = anim.split(":",1)
            layout.operator("mhx2.set_pose", text=aname).string = rest

#------------------------------------------------------------------------
#   Other Shape panel
#------------------------------------------------------------------------

class MhxOtherShapePanel(bpy.types.Panel):
    bl_label = "Other Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        rig = context.object
        return (rig and rig.MhxOtherShapeDrivers)

    def draw(self, context):
        rig = context.object
        if rig:
            layout = self.layout
            layout.operator("mhx2.reset_props").prefix = "Mho"
            drawProperties(layout, rig, "Mho")

#------------------------------------------------------------------------
#   Common drawing code for property panels
#------------------------------------------------------------------------

def drawProperties(layout, rig, prefix):
    for prop in rig.keys():
        if prop[0:3] != prefix:
            continue
        row = layout.split(0.8)
        row.prop(rig, '["%s"]' % prop, text=prop[3:])
        op = row.operator("mhx2.pin_prop", icon='UNPINNED')
        op.key = prop
        op.prefix = prefix

#------------------------------------------------------------------------
#   Visemes panel
#------------------------------------------------------------------------

class MhxVisemesPanel(bpy.types.Panel):
    bl_label = "Visemes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX2 Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and (ob.MhxFaceShapeDrivers or ob.MhxFacePanel))

    def draw(self, context):
        from .visemes import getLayout
        for vrow in getLayout():
            row = self.layout.row()
            for vis in vrow:
                row.operator("mhx2.set_viseme", text=vis).viseme = vis

        self.layout.separator()
        self.layout.operator("mhx2.load_moho")
        self.layout.operator("mhx2.delete_lipsync")


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def menu_func(self, context):
    self.layout.operator(ImportMHX2.bl_idname, text="MakeHuman (.mhx2)...")

def register():
    bpy.types.Object.MhxRig = StringProperty(default="")
    bpy.types.Object.MhxHuman = BoolProperty(default=False)
    bpy.types.Object.MhxUuid = StringProperty(default="")
    bpy.types.Object.MhxScale = FloatProperty(default=1.0)
    bpy.types.Object.MhxOffset = StringProperty(default="[0,0,0]")
    bpy.types.Object.MhxMesh = BoolProperty(default=False)
    bpy.types.Object.MhxSeedMesh = BoolProperty(default=False)
    bpy.types.Object.MhxRigify = BoolProperty(default=False)
    bpy.types.Object.MhxSnapExact = BoolProperty(default=False)
    bpy.types.Object.MhxVisibilityDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxHasFaceShapes = BoolProperty(default=False)
    bpy.types.Object.MhxFacePanel = BoolProperty(default=False)
    bpy.types.Object.MhxFaceShapeDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxOtherShapeDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRig = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRigDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxExpressions = StringProperty(default="")
    bpy.types.Object.MhxExprStrength = FloatProperty(name="Expression strength", default=1.0, min=0.0, max=1.0)

    bpy.types.Object.MhxPoses = StringProperty(default="")

    # License properties
    bpy.types.Object.MhxAuthor = StringProperty(default="")
    bpy.types.Object.MhxLicense = StringProperty(default="")
    bpy.types.Object.MhxHomePage = StringProperty(default="")
    bpy.types.Object.MhxHairAuthor = StringProperty(default="")
    bpy.types.Object.MhxHairLicense = StringProperty(default="")
    bpy.types.Object.MhxHairHomePage = StringProperty(default="")

    # MHX Control properties
    bpy.types.Object.MhaGazeFollowsHead = FloatProperty(default=1.0, min=0.0, max=1.0)
    bpy.types.Object.MhaRotationLimits = FloatProperty(default=0.8, min=0.0, max=1.0)

    bpy.types.Object.MhaArmHinge_L = BoolProperty(default=False)
    bpy.types.Object.MhaArmIk_L = FloatProperty(default=0.0, min=0.0, max=1.0)
    #bpy.types.Object.MhaElbowPlant_L = BoolProperty(default=False)
    bpy.types.Object.MhaFingerControl_L = BoolProperty(default=False)
    bpy.types.Object.MhaLegHinge_L = BoolProperty(default=False)
    bpy.types.Object.MhaLegIkToAnkle_L = BoolProperty(default=False)
    bpy.types.Object.MhaLegIk_L = FloatProperty(default=0.0, min=0.0, max=1.0)

    bpy.types.Object.MhaArmHinge_R = BoolProperty(default=False)
    bpy.types.Object.MhaArmIk_R = FloatProperty(default=0.0, min=0.0, max=1.0)
    #bpy.types.Object.MhaElbowPlant_R = BoolProperty(default=False)
    bpy.types.Object.MhaFingerControl_R = BoolProperty(default=False)
    bpy.types.Object.MhaLegHinge_R = BoolProperty(default=False)
    bpy.types.Object.MhaLegIkToAnkle_R = BoolProperty(default=False)
    bpy.types.Object.MhaLegIk_R = FloatProperty(default=0.0, min=0.0, max=1.0)

    bpy.types.Scene.MhxHairColor = HairColorProperty
    bpy.types.Scene.MhxMinHairLength = IntProperty(default=10, min=4, max=40)
    bpy.types.Scene.MhxMinHairOrientation = FloatProperty(default=0.6, min=0.0, max=1.0)
    bpy.types.Scene.MhxHairKeySeparation = FloatProperty(default=0.2, min=0.001, max=10.0)

    bpy.types.Scene.MhxUseDeflector = BoolProperty(name="Add Deflector", description="Add deflector", default=False)
    bpy.types.Scene.MhxUseHairDynamics = BoolProperty(name="Hair Dynamics", description="Add dynamics to hair", default=False)

    bpy.types.Scene.MhxUseConservativeMasks = BoolProperty(name="Conservative Masks", description="Only delete faces with two delete-verts", default=True)
    bpy.types.Scene.MhxDesignHuman = StringProperty(default="None")

    bpy.utils.register_class(ErrorOperator)
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    for cls in [ErrorOperator]:
        try:
            bpy.utils.register_class(cls)
        except:
            pass
    try:
        bpy.utils.unregister_module(__name__)
    except:
        pass
    try:
        bpy.types.INFO_MT_file_import.remove(menu_func)
    except:
        pass


if __name__ == "__main__":
    unregister()
    register()

print("MHX2 successfully (re)loaded")
