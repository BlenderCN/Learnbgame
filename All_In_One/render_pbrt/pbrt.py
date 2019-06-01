import bpy
from bl_ui import (
    properties_render,
    properties_material,
    properties_data_camera,
    properties_world
)
from bpy.types import Menu, Panel
import os
import subprocess
import math
import time
import shutil
import json

import sceneParser
import install
import renderer

# =============================================================================
# Find config storage path

currDir = os.path.abspath(os.path.dirname(__file__))

DEFAULT_IILE_PROJECT_PATH = os.path.join(currDir, "PBRT-IILE", "iile", "build")

# UI elements =======================================================

class RENDER_PT_pbrtoutput(properties_render.RenderButtonsPanel, Panel):
    bl_label = "PBRT Output"
    COMPAT_ENGINES = {renderer.IILERenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        rd = context.scene.render
        layout.prop(rd, "filepath", text="Exporter output directory")

class RENDER_PT_iile(properties_render.RenderButtonsPanel, Panel):
    bl_label = "PBRT Build Path"
    COMPAT_ENGINES = {renderer.IILERenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout

        s = context.scene
        layout.prop(s, "iilePath", text="PBRT binaries directory")

        layout.prop(s, "iileIntegrator", text="Integrator")

        if bpy.context.scene.iileIntegrator == "IILE":
            layout.prop(s, "iileStartRenderer", text="Autostart OSR GUI")
            layout.prop(s, "iileIntegratorIileIndirect", text="Indirect")
            layout.prop(s, "iileIntegratorIileDirect", text="Direct")

        elif bpy.context.scene.iileIntegrator == "PATH":
            layout.prop(s, "iileIntegratorPathSampler", text="Sampler")
            layout.prop(s, "iileIntegratorPathSamples", text="Samples")
        
        elif bpy.context.scene.iileIntegrator == "BDPT":
            layout.prop(s, "iileIntegratorPathSampler", text="Sampler")
            layout.prop(s, "iileIntegratorPathSamples", text="Samples")
            layout.prop(s, "iileIntegratorBdptMaxdepth", text="Max Depth")
            layout.prop(s, "iileIntegratorBdptLightsamplestrategy", text="Light Sample Strategy")
            layout.prop(s, "iileIntegratorBdptVisualizestrategies", text="Visualize Strategies")
            layout.prop(s, "iileIntegratorBdptVisualizeweights", text="Visualize weights")

        else:
            raise Exception("Unsupported integrator {}".format(bpy.context.scene.iileIntegrator))

class WORLD_PT_iileEnv(properties_world.WorldButtonsPanel, Panel):
    bl_label = "Environment map"
    COMPAT_ENGINES = {renderer.IILERenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout

        world = context.world

        layout.prop(world, "iileEnvcolor", "Env Color")
        layout.prop(world, "iileEnvMagnitude", "Env Magnitude")
        layout.prop(world, "iileEnvmapPath", "Env Map")
        layout.prop(world, "iileEnvmapRotation", "Rotation")

class MATERIAL_PT_material(properties_material.MaterialButtonsPanel, Panel):
    bl_label = "Material"
    COMPAT_ENGINES = {renderer.IILERenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout

        mat = properties_material.active_node_mat(context.material)

        layout.prop(mat, "iileMaterial", text="Surface type")

        if mat.iileMaterial == "MATTE":
            layout.prop(mat, "iileMatteColor", text="Diffuse color")
            layout.prop(mat, "iileMatteColorTexture", text="Diffuse texture")
        
        elif mat.iileMaterial == "PLASTIC":
            layout.prop(mat, "iilePlasticDiffuseColor", text="Diffuse color")
            layout.prop(mat, "iilePlasticDiffuseTexture", text="Diffuse texture")
            layout.prop(mat, "iilePlasticSpecularColor", text="Specular color")
            layout.prop(mat, "iilePlasticSpecularTexture", text="Specular texture")
            layout.prop(mat, "iilePlasticRoughnessValue", text="Roughness")
            layout.prop(mat, "iilePlasticRoughnessTexture", text="Roughness texture")

        elif mat.iileMaterial == "MIRROR":
            layout.prop(mat, "iileMirrorKr", text="Reflectivity")
            layout.prop(mat, "iileMirrorKrTex", text="Reflectivity texture")

        elif mat.iileMaterial == "MIX":
            layout.prop(mat, "iileMatMixSlot1", text="Mix 1")
            layout.prop(mat, "iileMatMixSlot2", text="Mix 2")
            layout.prop(mat, "iileMatMixAmount", text="Amount")
            layout.prop(mat, "iileMatMixAmountTex", text="Amount texture")
        
        elif mat.iileMaterial == "GLASS":
            layout.prop(mat, "iileMatGlassKr", text="Reflectivity")
            layout.prop(mat, "iileMatGlassKrTex", text="Reflectivity Texture")
            layout.prop(mat, "iileMatGlassKt", text="Transmission")
            layout.prop(mat, "iileMatGlassKtTex", text="Transmission Texture")
            layout.prop(mat, "iileMatGlassIor", text="IOR")
            layout.prop(mat, "iileMatGlassIorTex", text="IOR Texture")
            layout.prop(mat, "iileMatGlassURough", text="U Roughness")
            layout.prop(mat, "iileMatGlassURoughTex", text="U Roughness Texture")
            layout.prop(mat, "iileMatGlassVRough", text="V Roughness")
            layout.prop(mat, "iileMatGlassVRoughTex", text="V Roughness Texture")

class MATERIAL_PT_emission(properties_material.MaterialButtonsPanel, Panel):
    bl_label = "Emission"
    COMPAT_ENGINES = {renderer.IILERenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout

        mat = properties_material.active_node_mat(context.material)

        layout.prop(mat, "emit", text="Emission Intensity")

        layout.prop(mat, "iileEmission", text="Emission color")

# Register ==================================================================

def iileMatMixGenMaterials(self, context):
    try:
        res = []
        theObj = context.object
        theMaterials = theObj.material_slots
        currMatIndex = theObj.active_material_index
        for i in range(len(theMaterials)):
            if i != currMatIndex:
                matName = theMaterials[i].name
                newVal = (matName, matName, matName)
                res.append(newVal)

        return res
    except:
        return [("", "", "")]

def updateMatMixSlot1Val(self, context):
    context.material.iileMatMixSlot1Val = context.material.iileMatMixSlot1

def updateMatMixSlot2Val(self, context):
    context.material.iileMatMixSlot2Val = context.material.iileMatMixSlot2

def register():
    bpy.utils.register_class(renderer.IILERenderEngine)

    # Add properties -------------------------------------------------------

    Scene = bpy.types.Scene

    Scene.iilePath = bpy.props.StringProperty(
        name="PBRT build path",
        description="Directory that contains the pbrt executable",
        default=DEFAULT_IILE_PROJECT_PATH,
        subtype='DIR_PATH'
    )

    Scene.iileStartRenderer = bpy.props.BoolProperty(
        name="Start OSR renderer",
        description="Automatically start OSR renderer after exporting. Not compatible with vanilla PBRTv3",
        default=False
    )

    Scene.iileIntegrator = bpy.props.EnumProperty(
        name="Integrator",
        description="Surface Integrator",
        items=[
            ("PATH", "Path", "Path Integrator"),
            ("IILE", "OSR", "OSR Integrator"),
            ("BDPT", "BDPT", "BDPT Integrator")
        ]
    )

    Scene.iileIntegratorIileIndirect = bpy.props.IntProperty(
        name="Indirect Tasks",
        description="Number of OSR Indirect Tasks to be executed",
        default=16,
        min=0
    )

    Scene.iileIntegratorIileDirect = bpy.props.IntProperty(
        name="Direct Samples",
        description="Number of Direct Illumination samples",
        default=16,
        min=1
    )

    Scene.iileIntegratorPathSampler = bpy.props.EnumProperty(
        name="Sampler",
        description="Sampler",
        items=[
            ("RANDOM", "Random", "Random Sampler"),
            ("SOBOL", "Sobol", "Sobol Sampler"),
            ("HALTON", "Halton", "Halton Sampler"),
        ]
    )

    Scene.iileIntegratorPathSamples = bpy.props.IntProperty(
        name="Samples",
        description="Number of samples/px",
        default=4,
        min=1
    )

    Scene.iileIntegratorBdptMaxdepth = bpy.props.IntProperty(
        name="Max Depth",
        default=5,
        min=0,
        max=128
    )

    Scene.iileIntegratorBdptLightsamplestrategy = bpy.props.EnumProperty(
        name="Light Sample Strategy",
        items=[
            ("POWER", "Power", "samples light sources according to their emitted power"),
            ("UNIFORM", "Uniform", "samples all light sources uniformly"),
            ("SPATIAL", "Spatial", "computes light contributions in regions of the scene and samples from a related distribution")
        ]
    )

    Scene.iileIntegratorBdptVisualizestrategies = bpy.props.BoolProperty(
        name="Visualize Strategies",
        default=False
    )

    Scene.iileIntegratorBdptVisualizeweights = bpy.props.BoolProperty(
        name="Visualize Weights",
        default=False
    )

    World = bpy.types.World

    World.iileEnvcolor = bpy.props.FloatVectorProperty(
        name="Environment Color",
        description="Environment Color Multiplier",
        subtype="COLOR",
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0)
    )

    World.iileEnvMagnitude = bpy.props.FloatProperty(
        name="Environment Magnitude",
        description="Environment Magnitude",
        default=1.0,
        min=0.0
    )

    World.iileEnvmapPath = bpy.props.StringProperty(
        name="Environment Map Image",
        description="Environment Map Image",
        subtype="FILE_PATH"
    )

    World.iileEnvmapRotation = bpy.props.FloatProperty(
        name="Environment map rotation",
        description="Rotates the environment map on the Z axis. If you need to rotate on other axis, the best option is to select every object in your scene and rotate everything, as the environment map is fixed",
        default=0.0,
        min=0.0,
        max=360.0
    )

    Mat = bpy.types.Material

    Mat.iileMaterial = bpy.props.EnumProperty(
        name="PBRT Material",
        description="Material type",
        items=[
            ("MATTE", "Matte", "Lambertian Diffuse Material"),
            ("PLASTIC", "Plastic", "Plastic glossy"),
            ("MIRROR", "Mirror", "Mirror material"),
            ("MIX", "Mix", "Mix material"),
            ("GLASS", "Glass", "Glass material"),
            ("NONE", "None", "None material")
        ]
    )

    Mat.iileMatteColor = bpy.props.FloatVectorProperty(
        name="Diffuse color",
        description="Diffuse color",
        subtype="COLOR",
        precision=4,
        step=0.01,
        min=0.0,
        soft_max=1.0,
        default=(0.75, 0.75, 0.75)
    )

    Mat.iileMatteColorTexture = bpy.props.StringProperty(
        name="Diffuse texture",
        description="Diffuse Texture. Overrides the diffuse color",
        subtype="FILE_PATH"
    )

    Mat.iilePlasticDiffuseColor = bpy.props.FloatVectorProperty(
        name="Diffuse color",
        description="Diffuse color",
        subtype="COLOR",
        precision=4,
        step=0.01,
        min=0.0,
        max=1.0,
        default=(0.75, 0.75, 0.75)
    )

    Mat.iilePlasticDiffuseTexture = bpy.props.StringProperty(
        name="Diffuse texture",
        description="Diffuse Texture. Overrides the diffuse color",
        subtype="FILE_PATH"
    )

    Mat.iilePlasticSpecularColor = bpy.props.FloatVectorProperty(
        name="Specular color",
        description="Specular color",
        subtype="COLOR",
        precision=4,
        step=0.01,
        min=0.0,
        max=1.0,
        default=(0.25, 0.25, 0.25)
    )

    Mat.iilePlasticSpecularTexture = bpy.props.StringProperty(
        name="Specular texture",
        description="Specular Texture. Overrides the specular color",
        subtype="FILE_PATH"
    )

    Mat.iilePlasticRoughnessValue = bpy.props.FloatProperty(
        name="Roughness",
        description="Roughness. Larger values create blurrier reflections",
        default=0.1,
        min=0.0,
        max=1.0
    )

    Mat.iilePlasticRoughnessTexture = bpy.props.StringProperty(
        name="Roughness texture",
        description="Roughness texture. Overrides the roughness value",
        subtype="FILE_PATH"
    )

    Mat.iileMirrorKr = bpy.props.FloatVectorProperty(
        name="Reflectivity",
        description="Reflectivity of the mirror material",
        subtype="COLOR",
        precision=4,
        step=0.01,
        min=0.0,
        max=1.0,
        default=(0.9, 0.9, 0.9)
    )

    Mat.iileMirrorKrTex = bpy.props.StringProperty(
        name="Reflectivity texture",
        description="Reflectivity texture for mirror. Overrides the Reflectivity value",
        subtype="FILE_PATH"
    )

    Mat.iileMatMixSlot1Val = bpy.props.StringProperty(
        name="Slot 1 hidden"
    )

    Mat.iileMatMixSlot2Val = bpy.props.StringProperty(
        name="Slot 2 hidden"
    )

    Mat.iileMatMixSlot1 = bpy.props.EnumProperty(
        name="Mix 1",
        description="Choose the first material to be mixed. If the slot is empty, please add a new material to this object using the + button in the section above and creating a new material. Then come back to this material and you'll be able to assign the other material as the first one to be mixed.",
        items=iileMatMixGenMaterials,
        update=updateMatMixSlot1Val
    )

    Mat.iileMatMixSlot2 = bpy.props.EnumProperty(
        name="Mix 2",
        description="Choose the second material to be mixed. If the slot is empty, please add a new material to this object using the + button in the section above and creating a new material. Then come back to this material and you'll be able to assign the other material as the second one to be mixed.",
        items=iileMatMixGenMaterials,
        update=updateMatMixSlot2Val
    )

    Mat.iileMatMixAmount = bpy.props.FloatVectorProperty(
        name="Mix amount",
        description="Mix amount",
        subtype="COLOR",
        precision=4,
        step=0.01,
        min=0.0,
        max=1.0,
        default=(0.9, 0.9, 0.9)
    )

    Mat.iileMatMixAmountTex = bpy.props.StringProperty(
        name="Mix amount texture",
        description="Mix amount texture. Overrides the Mix Amount",
        subtype="FILE_PATH"
    )

    # Glass material ----------------------------------------------------------

    Mat.iileMatGlassKr = bpy.props.FloatVectorProperty(
        name="Reflectivity",
        subtype="COLOR",
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )

    Mat.iileMatGlassKrTex = bpy.props.StringProperty(
        name="Reflectivity texture",
        subtype="FILE_PATH"
    )

    Mat.iileMatGlassKt = bpy.props.FloatVectorProperty(
        name="Transmission",
        subtype="COLOR",
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )

    Mat.iileMatGlassKtTex = bpy.props.StringProperty(
        name="Transmission texture",
        subtype="FILE_PATH"
    )

    Mat.iileMatGlassIor = bpy.props.FloatProperty(
        name="IOR",
        default=1.5,
        min=1.0,
        max=5.0
    )

    Mat.iileMatGlassIorTex = bpy.props.StringProperty(
        name="IOR texture",
        subtype="FILE_PATH"
    )

    Mat.iileMatGlassURough = bpy.props.FloatProperty(
        name="U Roughness",
        default=0.0,
        min=0.0,
        max=1.0
    )

    Mat.iileMatGlassURoughTex = bpy.props.StringProperty(
        name="U Roughness texture",
        subtype="FILE_PATH"
    )

    Mat.iileMatGlassVRough = bpy.props.FloatProperty(
        name="V Roughness",
        default=0.0,
        min=0.0,
        max=1.0
    )

    Mat.iileMatGlassVRoughTex = bpy.props.StringProperty(
        name="V Roughness texture",
        subtype="FILE_PATH"
    )

    # Emission material -------------------------------------------------------

    Mat.iileEmission = bpy.props.FloatVectorProperty(
        name="Emission",
        description="Color of the emission",
        subtype="COLOR",
        precision=4,
        step=0.01,
        min=0.0,
        soft_max=1.0,
        default=(1, 1, 1)
    )

    # UI -------------------------------------------------------------

    # Render Button
    properties_render.RENDER_PT_output.COMPAT_ENGINES.add(renderer.IILERenderEngine.bl_idname)
    # Dimensions
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add(
        renderer.IILERenderEngine.bl_idname)
    # Output
    bpy.utils.register_class(RENDER_PT_pbrtoutput)
    # IILE Settings
    bpy.utils.register_class(RENDER_PT_iile)

    bpy.utils.register_class(WORLD_PT_iileEnv)

    # Material slots
    properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add(renderer.IILERenderEngine.bl_idname)
    # Material type
    bpy.utils.register_class(MATERIAL_PT_material)
    # Material emission
    bpy.utils.register_class(MATERIAL_PT_emission)

    # Camera
    properties_data_camera.DATA_PT_lens.COMPAT_ENGINES.add(renderer.IILERenderEngine.bl_idname)


def unregister():
    bpy.utils.unregister_class(renderer.IILERenderEngine)
    properties_render.RENDER_PT_pbrtoutput.COMPAT_ENGINES.remove(renderer.IILERenderEngine.bl_idname)
    properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.remove(
        renderer.IILERenderEngine.bl_idname)
