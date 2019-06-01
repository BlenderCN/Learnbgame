"""
.. module:: thea_gui
   :platform: OS X, Windows, Linux
   :synopsis: GUI definition

.. moduleauthor:: Grzegorz Rakoczy <grzegorz.rakoczy@solidiris.com>


"""

# ##### BEGIN GPL LICENSE BLOCK #####
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
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
from . import thea_globals
from . import thea_properties
from . import thea_render_main
from bpy.props import *
from bpy.types import Header, Menu, Panel

# Use some of the existing buttons.
from bl_ui import properties_render
from tempfile import gettempdir
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('THEA_RENDER')
properties_render.RENDER_PT_output.COMPAT_ENGINES.add('THEA_RENDER')
properties_render.RENDER_PT_post_processing.COMPAT_ENGINES.add('THEA_RENDER')
del properties_render

from bl_ui import properties_render_layer
properties_render_layer.RENDERLAYER_PT_layers.COMPAT_ENGINES.add('THEA_RENDER')
properties_render_layer.RENDERLAYER_PT_layer_options.COMPAT_ENGINES.add('THEA_RENDER')
del properties_render_layer

# Use only a subset of the world panels
from bl_ui import properties_world
#properties_world.WORLD_PT_preview.COMPAT_ENGINES.add('THEA_RENDER')
properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add('THEA_RENDER')
properties_world.WORLD_PT_world.COMPAT_ENGINES.add('THEA_RENDER')
properties_world.WORLD_PT_ambient_occlusion.COMPAT_ENGINES.add('THEA_RENDER')
del properties_world

# from bl_ui import properties_data_lamp
# for member in dir(properties_data_lamp):
#     subclass = getattr(properties_data_lamp, member)
#     try:        subclass.COMPAT_ENGINES.add('THEA_RENDER')
#     except: pass
# del properties_data_lamp


from bl_ui import properties_material
#for member in ('MATERIAL_PT_context_material', 'MATERIAL_PT_preview', 'MATERIAL_PT_custom_props', 'MaterialButtonsPanel', 'PropertyPanel', 'bpy', 'check_material', 'simple_material'):
for member in ('MATERIAL_PT_context_material', 'MATERIAL_PT_custom_props', 'MaterialButtonsPanel', 'PropertyPanel', 'bpy', 'check_material', 'simple_material'):
    subclass = getattr(properties_material, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_material
from bl_ui import properties_data_mesh
for member in dir(properties_data_mesh):
    subclass = getattr(properties_data_mesh, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_data_mesh
from bl_ui import properties_texture
properties_texture.TEXTURE_PT_colors.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_clouds.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_wood.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_marble.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_magic.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_stucci.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_clouds.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_blend.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_musgrave.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_voronoi.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_ocean.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_pointdensity.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_pointdensity_turbulence.COMPAT_ENGINES.add('THEA_RENDER')
properties_texture.TEXTURE_PT_distortednoise.COMPAT_ENGINES.add('THEA_RENDER')
#properties_texture.TEXTURE_PT_mapping.COMPAT_ENGINES.add('THEA_RENDER')


# for member in dir(properties_texture):
#     subclass = getattr(properties_texture, member)
#     print(subclass)
#     try:
#         subclass.COMPAT_ENGINES.add('THEA_RENDER')
#     except:
#         pass
# del properties_texture
from bl_ui import properties_data_camera
for member in dir(properties_data_camera):
    subclass = getattr(properties_data_camera, member)
    try:

        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_data_camera

from bl_ui import properties_particle
for member in dir(properties_particle):
    subclass = getattr(properties_particle, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_particle

from bl_ui import properties_physics_common
for member in dir(properties_physics_common):
    subclass = getattr(properties_physics_common, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_common

from bl_ui import properties_physics_cloth
for member in dir(properties_physics_cloth):
    subclass = getattr(properties_physics_cloth, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_cloth

from bl_ui import properties_physics_dynamicpaint
for member in dir(properties_physics_dynamicpaint):
    subclass = getattr(properties_physics_dynamicpaint, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_dynamicpaint

from bl_ui import properties_physics_field
for member in dir(properties_physics_field):
    subclass = getattr(properties_physics_field, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_field

from bl_ui import properties_physics_fluid
for member in dir(properties_physics_fluid):
    subclass = getattr(properties_physics_fluid, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_fluid

from bl_ui import properties_physics_rigidbody
for member in dir(properties_physics_rigidbody):
    subclass = getattr(properties_physics_rigidbody, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_rigidbody

from bl_ui import properties_physics_rigidbody_constraint
for member in dir(properties_physics_rigidbody_constraint):
    subclass = getattr(properties_physics_rigidbody_constraint, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_rigidbody_constraint

from bl_ui import properties_physics_smoke
for member in dir(properties_physics_smoke):
    subclass = getattr(properties_physics_smoke, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_smoke

from bl_ui import properties_physics_softbody
for member in dir(properties_physics_softbody):
    subclass = getattr(properties_physics_softbody, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_physics_softbody

from bl_ui import properties_scene
for member in dir(properties_scene):
    subclass = getattr(properties_scene, member)
    try:
        subclass.COMPAT_ENGINES.add('THEA_RENDER')
    except:
        pass
del properties_scene


def particle_panel_poll(cls, context):
    psys = context.particle_system
    engine = context.scene.render.engine
    settings = 0

    if psys:
        settings = psys.settings
    elif isinstance(context.space_data.pin_id, bpy.types.ParticleSettings):
        settings = context.space_data.pin_id

    if not settings:
        return False

    return settings.is_fluid is False and (engine in cls.COMPAT_ENGINES)


class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (context.scene and rd.use_game_engine is False) and (rd.engine in cls.COMPAT_ENGINES)

class WorldButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        return (context.world and context.scene.render.engine in cls.COMPAT_ENGINES)

class CameraButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.camera and (engine in cls.COMPAT_ENGINES)


class MaterialButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        return context.material and (context.scene.render.engine in cls.COMPAT_ENGINES)

class ObjectButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object and (context.scene.render.engine in cls.COMPAT_ENGINES)

class TextureButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        tex = context.texture
        return tex and (tex.type != 'NONE' or tex.use_nodes) and (context.scene.render.engine in cls.COMPAT_ENGINES)

class DisplayButtonsPanel():
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_context = "image"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.image and context.scene.render.engine in cls.COMPAT_ENGINES

class View3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

class ParticleButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"

    @classmethod
    def poll(cls, context):
        return particle_panel_poll(cls, context)


class RENDER_PT_InstallThea(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Install Thea Studio"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (thea_globals.theaPath is False) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("thea.install_thea_studio", "Install Thea Studio")


class MATERIAL_PT_LUT(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Library"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return getattr(context.scene, 'thea_useLUT') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material
        split = layout.split()
        col = split.column()
        colL = col
        colL.label("Thea Materials:")
        #       colR = col.row(align=True)
        colR = split.column(align=True)
        colR.prop(mat, "thea_LUT", text="")
        colR.operator("thea.lutmenu", text="Search", icon="VIEWZOOM")
#       thea_globals.log.debug("*** LUT current index: %s" % mat.get('thea_LUT'))
       #col.operator("thea.set_library_material", text="Set library material")


#---------------------------------------
# Material preview UI
#---------------------------------------
class TheaMaterialPreview(MaterialButtonsPanel, bpy.types.Panel):
    bl_idname = "MATERIAL_PT_MatPreview"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_label = "Preview"
    bl_options = {"DEFAULT_CLOSED"}

    COMPAT_ENGINES = set(['THEA_RENDER'])
    panelMatPreview = True

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES) and context.object is not None and context.object.active_material is not None and (thea_globals.panelMatPreview is True)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        split = row.split(percentage=0.9)
        colL = split.column()
        colL.operator("thea.big_preview")
        colR = split.column()
        colR.label("")
        layout.template_preview(context.material, show_buttons = True, preview_id = "MATERIAL_PT_MatPreview")




class MATERIAL_PT_Color(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Color"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (not thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)
        #return (thea_globals.showMatGui)and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material
        split = layout.split(percentage=0.8)
        row = layout.row()
        colL = split.column()
        colR = split.column()
        try:
            colL.prop(mat, "diffuse_color", text="")
            colR.operator("thea.refresh_diffuse_color", text="", icon="FILE_REFRESH")
            if (getattr(mat, "diffuse_color") == mat.diffuse_color/255):
                row.label(text="Preview to dark (hit E colorpicker)", icon="ERROR")(percentage=1)
            else:
                pass
        except:
            pass

class MATERIAL_PT_Header(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Material Settings"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        thea_globals.showMatGui = False
        if hasattr(bpy.context, 'active_object'):
            try:
                extMat = os.path.exists(os.path.abspath(bpy.path.abspath(bpy.context.active_object.active_material.get('thea_extMat'))))
                if extMat == False:
                    context.window_manager.fileselect_add(self)
#                    self.report({'ERROR'}, "Please save the scene before exporting!")
                    thea_globals.log.debug( "Please relink material!")
                else:
                    pass
            except:
                extMat = False
#                thea_globals.report({'ERROR'}, "Please relink et material!")
            if getattr(bpy.context.active_object, 'active_material') is not None:
                thea_globals.showMatGui = True
            else:
                thea_globals.showMatGui = False
            if extMat:
                thea_globals.showMatGui = False
            if int(getattr(bpy.context.active_object.active_material, 'thea_LUT', 0)) > 0:
                thea_globals.showMatGui = False
        else:
            thea_globals.showMatGui = True2
        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material
        #    CHANGED > Added new layout for general mat panel
        layout.label(text="Scene Preview")
        split = layout.split(percentage=0.4)
        colL = split.column()
        colR = split.column()
        colL.prop(mat, "thea_EnableUnbiasedPreview")
        colR.prop(mat, "thea_PreviewScenesMenu")

        split = layout.split()
        layout.label(text="General Options")
        split = layout.split()
        colL = split.column()
        colR = split.column()
        colL.prop(mat, "thea_ShadowCatcher")
        #    CHANGED > added more material options
        colR.prop(mat, "thea_twoSided")
        colL.prop(mat, "thea_repaintable")
        colR.prop(mat, "thea_dirt")
        layout.prop(mat, "thea_description")
        colL.prop(mat, "thea_ClippingAuto")
        #        layout.operator("thea.sync_cycles_to_thea", text="Convert Cycles material")


#
#class MATERIAL_PT_Coating(MaterialButtonsPanel, bpy.types.Panel):
#    bl_label = "Coating Component"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#
#        if (not (len(bpy.context.active_object.data.materials)>0)):
#            return False
#
#        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)
#
#    def draw_header(self, context):
#        scene = context.scene
#        mat = context.material
#        self.layout.prop(mat, "thea_Coating", text="")
#
#    def draw(self, context):
#        layout = self.layout
#        scene = context.scene
#        mat = context.material
#        split = layout.split()
#        row = layout.row()
#
#        if mat.get('thea_Coating'):
#            split = layout.split()
#            row = layout.row()
#            row.prop(mat, "thea_CoatingWeight")
#            row.prop(mat, "thea_CoatingWeightFilename", text="", icon='TEXTURE_DATA')
##           CHANGED>Added split to set layer weight more to top
#            split = layout.split()
#            row = layout.row()
#            if mat.thea_CoatingReflectanceFilename == "":
#                row.prop(mat, "thea_CoatingReflectanceCol")
#            row.prop(mat, "thea_CoatingReflectanceFilename", text="", icon='TEXTURE_DATA')
#            row = layout.row()
#            layout.prop(mat, "thea_CoatingIOR")
#            layout.prop(mat, "thea_CoatingEC")
#            split = layout.split()
#            row = layout.row()
#            row.prop(mat, "thea_CoatingThicknessEnable")
#            if(getattr(mat, "thea_CoatingThicknessEnable", False)):
#               row.prop(mat, "thea_CoatingThickness")
#               row.prop(mat, "thea_CoatingThicknessFilename", text="", icon='TEXTURE_DATA')
#            #             CHANGED > Added absorption color coatin thickness
#            split = layout.split()
#            row = layout.row()
#            col = split.column()
#            col.prop(mat, "thea_CoatingAbsorptionEnable")
#            if(getattr(mat, "thea_CoatingAbsorptionEnable", False)):
#                if(mat.thea_CoatingAbsorptionFilename==""):
#                    row.prop(mat, "thea_CoatingThicknessAbsorptionCol")
#                row.prop(mat, "thea_CoatingAbsorptionFilename", text="", icon='TEXTURE_DATA')
#            split = layout.split()
#            row = layout.row()
#            col = split.column()
#            col.prop(mat, "thea_CoatingTraceReflections")
#            split = layout.split()
#            layout.label(text="Structure")
#            row = layout.row()
#            row.prop(mat, "thea_CoatingStructureRoughness")
#            row.prop(mat, "thea_CoatingRoughnessFilename", text="", icon='TEXTURE_DATA')
#            row = layout.row()
#            row.prop(mat, "thea_CoatingStructureAnisotropy")
#            row.prop(mat, "thea_CoatingAnisotropyFilename", text="", icon='TEXTURE_DATA')
#            row = layout.row()
#            row.prop(mat, "thea_CoatingStructureRotation")
#            row.prop(mat, "thea_CoatingRotationFilename", text="", icon='TEXTURE_DATA')
#            row = layout.row()
#            row.prop(mat, "thea_CoatingStructureBump")
#            row.prop(mat, "thea_CoatingBumpFilename", text="", icon='TEXTURE_DATA')
#            row = layout.row()
#            layout.prop(mat, "thea_CoatingStructureNormal")
#            row = layout.row()
#            row.prop(mat, "thea_CoatingMicroRoughness")
#            if (getattr(mat, "thea_CoatingMicroRoughness", False)):
#                row.prop(mat, "thea_CoatingMicroRoughnessWidth")
#                row.prop(mat, "thea_CoatingMicroRoughnessHeight")
#            if (((getattr(mat, 'thea_CoatingReflectanceCol')[0], getattr(mat, 'thea_CoatingReflectanceCol')[1], getattr(mat, 'thea_CoatingReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat, 'thea_CoatingReflectanceFilename'))>1:
#                layout.separator()
#                layout.label(text = "Fresnel")
#                row = layout.row()
#                if(mat.thea_CoatingReflect90Filename == ""):
#                    row.prop(mat, "thea_CoatingReflect90Col")
#                row.prop(mat, "thea_CoatingReflect90Filename", text="", icon='TEXTURE_DATA')
#                layout.prop(mat, "thea_CoatingReflectionCurve")
#                if mat.thea_CoatingReflectionCurve:
#                    layout.prop(mat, "thea_CoatingReflectCurve", text="Curve Name")
#                    layout.template_curve_mapping(myCurveData(getattr(mat, "thea_CoatingReflectCurve"), "thea_CoatingReflectCurve"), "mapping")
#                    layout.prop(mat, "thea_CoatingReflectCurveList", text="CurveList")
#



class MATERIAL_PT_Extras(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Material Extra's"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine

        if (not (len(bpy.context.active_object.data.materials)>0)):
            return False

        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material
        tex = context.texture

        layout.prop(mat, "thea_materialExtras", expand=True)


#------ Coating Component
        if getattr(mat, "thea_materialExtras") in ("Coating"):
            box = layout.box()
            row = box.row()
#            row.label(text="Coating")
            row.prop(mat, "thea_Coating", text="Coating enable")

            layout.separator()
            if mat.get('thea_Coating'):
#                split = layout.split()
#                row = layout.row()
#                row.label("Weight")
                row = layout.row()
                row.prop(mat, "thea_CoatingWeight")
                row.prop(mat, "thea_CoatingWeightFilename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_CoatingWeightFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingWeightFilename"
                layout.separator()

                layout.label("Scattering")
                split = layout.split()
                row = layout.row()
                if mat.thea_CoatingReflectanceFilename == "":
                    row.prop(mat, "thea_CoatingReflectanceCol")
                    row.prop(mat, "thea_CoatingReflectanceFilename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_CoatingReflectanceFilename", text="Reflectance", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_CoatingReflectanceFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingReflectanceFilename"

                row = layout.row()
                layout.prop(mat, "thea_CoatingIOR")
                layout.prop(mat, "thea_CoatingEC")
                split = layout.split()
                row = layout.row()
                row.prop(mat, "thea_CoatingThicknessEnable")
                if(getattr(mat, "thea_CoatingThicknessEnable", False)):
                    row.prop(mat, "thea_CoatingThickness")
                    row.prop(mat, "thea_CoatingThicknessFilename", text="", icon='TEXTURE_DATA')
                    sub = row.row()
                    sub.active = (len(mat.thea_CoatingThicknessFilename) > 1) == True
                    sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingThicknessFilename"

                #             CHANGED > Added absorption color coatin thickness
                split = layout.split()
                row = layout.row()
                col = split.column()
                col.prop(mat, "thea_CoatingAbsorptionEnable")
                if(getattr(mat, "thea_CoatingAbsorptionEnable", False)):
                    if(mat.thea_CoatingAbsorptionFilename==""):
                        row.prop(mat, "thea_CoatingThicknessAbsorptionCol")
                    row.prop(mat, "thea_CoatingAbsorptionFilename", text="", icon='TEXTURE_DATA')
                    sub = row.row()
                    sub.active = (len(mat.thea_CoatingAbsorptionFilename) > 1) == True
                    sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingAbsorptionFilename"

                split = layout.split()
                row = layout.row()
                col = split.column()
                col.prop(mat, "thea_CoatingTraceReflections")
                split = layout.split()

                row = layout.row()
                row.label(text="Structure")
                row = layout.row()
                row.prop(mat, "thea_CoatingStructureRoughness")
                row.prop(mat, "thea_CoatingRoughnessFilename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_CoatingRoughnessFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingRoughnessFilename"

                row = layout.row()
                row.prop(mat, "thea_CoatingStructureAnisotropy")
                row.prop(mat, "thea_CoatingAnisotropyFilename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_CoatingAnisotropyFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingAnisotropyFilename"

                row = layout.row()
                row.prop(mat, "thea_CoatingStructureRotation")
                row.prop(mat, "thea_CoatingRotationFilename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_CoatingRotationFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingRotationFilename"

                row = layout.row()
                row.prop(mat, "thea_CoatingStructureBump")
                row.prop(mat, "thea_CoatingBumpFilename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_CoatingBumpFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingBumpFilename"

                row = layout.row()
                layout.prop(mat, "thea_CoatingStructureNormal")
                row = layout.row()
                row.prop(mat, "thea_CoatingMicroRoughness")
                if (getattr(mat, "thea_CoatingMicroRoughness", False)):
                    row.prop(mat, "thea_CoatingMicroRoughnessWidth")
                    row.prop(mat, "thea_CoatingMicroRoughnessHeight")
                if (((getattr(mat, 'thea_CoatingReflectanceCol')[0], getattr(mat, 'thea_CoatingReflectanceCol')[1], getattr(mat, 'thea_CoatingReflectanceCol')[2])) != (0, 0, 0)) or len(getattr(mat, 'thea_CoatingReflectanceFilename')) > 1:
                    layout.separator()
                    layout.label(text="Fresnel")
                    row = layout.row()
                    if(mat.thea_CoatingReflect90Filename == ""):
                        row.prop(mat, "thea_CoatingReflect90Col")
                        row.prop(mat, "thea_CoatingReflect90Filename", text="", icon='TEXTURE_DATA')
                    else:
                        row.prop(mat, "thea_CoatingReflect90Filename", text="Reflectance 90", icon='TEXTURE_DATA')
                    sub = row.row()
                    sub.active = (len(mat.thea_CoatingReflect90Filename) > 1) == True
                    sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_CoatingReflect90Filename"

                    layout.prop(mat, "thea_CoatingReflectionCurve")
                    if mat.thea_CoatingReflectionCurve:
                        layout.operator("update.curve_list")
#                        layout.prop(mat, "thea_CoatingReflectCurve", text="Curve Name")
                        layout.template_curve_mapping(myCurveData(getattr(mat, "thea_CoatingReflectCurve"), "thea_CoatingReflectCurve"), "mapping")
#                        layout.prop(mat, "thea_CoatingReflectCurveList", text="CurveList")


#------ Clipping
        if getattr(mat, "thea_materialExtras") in ("Clipping"):
            box = layout.box()
            row = box.row()
#            row.label(text="Clipping")
            row.prop(mat, "thea_Clipping", text="Clipping enable")

            layout.separator()
            if mat.get('thea_Clipping'):
                row = layout.row()
                row.prop(mat, "thea_ClippingFilename", text="Clipping", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_ClippingFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_ClippingFilename"

                col = layout.column()
                col.prop(mat, "thea_ClippingThreshold", text="Threshold (%):")
                row = layout.row()
                row.prop(mat, "thea_ClippingSoft")

#------ Displacement
        if getattr(mat, "thea_materialExtras") in ("Displacement"):
            box = layout.box()
            row = box.row()
#            row.label(text="Displacement")
            row.prop(mat, "thea_Displacement", text="Displacement enable")

            layout.separator()
            if mat.get('thea_Displacement'):
                row = layout.row()
                row.prop(mat, "thea_DisplacementFilename", text="Displacement", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_DisplacementFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_DisplacementFilename"

                split = layout.split()
                col = split.column()
                col.prop(mat, "thea_DispSub")
                #            col.prop(mat, "thea_DispBump")
                col.prop(mat, "thea_DisplacementHeight")
                col.prop(mat, "thea_DisplacementCenter")
                col.separator()
                col.prop(mat, "thea_DisplacementNormalSmooth")
                col.prop(mat, "thea_DisplacementTightBounds")


#------ Emittance
        if getattr(mat, "thea_materialExtras") in ("Emittance"):
            box = layout.box()
            row = box.row()
#            row.label(text="Emittance")
            row.prop(mat, "thea_Emittance", text="Emittance enable")

            layout.separator()
            if mat.get('thea_Emittance'):
                row = layout.row()
                if (mat.thea_EmittanceFilename == ""):
                    row.prop(mat, "thea_EmittanceCol")
                    row.prop(mat, "thea_EmittanceFilename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_EmittanceFilename", text="Color", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_EmittanceFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_EmittanceFilename"

                row = layout.row()
                row.prop(mat, "thea_EmittancePower")
                #      CHANGED > Added this to hide with other light units
                if getattr(context.material, "thea_EmittanceUnit") in ("Watts", "W/m2", "W/sr", "W/sr/m2"):
                   row.prop(mat, "thea_EmittanceEfficacy")
                #           row.prop(mat, "thea_EmittanceEfficacy")
                layout.prop(mat, "thea_EmittanceUnit")
                row = layout.row()
                row.prop(mat, "thea_EmittanceIES")
                if(getattr(mat, "thea_EmittanceIES")):
                   row.prop(mat, "thea_EmittanceIESFilename", text="", icon='LAMP_DATA')
                   row = layout.row()
                   layout.prop(mat, "thea_EmittanceIESMultiplier")

                split = layout.split()
                col = split.column()
                col.prop(mat, "thea_EmittancePassiveEmitter")
                row = layout.row()
                row.prop(mat, "thea_EmittanceAmbientEmitter")
                if(getattr(mat, "thea_EmittanceAmbientEmitter")):
                   row.prop(mat, "thea_EmittanceAmbientLevel")

#------ Medium
        if getattr(mat, "thea_materialExtras") in ("Medium"):
            box = layout.box()
            row = box.row()
#            row.label(text="Medium")
            row.prop(mat, "thea_Medium", text="Medium enable")

            layout.separator()
            if mat.get('thea_Medium'):
                row = layout.row()
                if(mat.thea_MediumAbsorptionFilename==""):
                    row.prop(mat, "thea_MediumAbsorptionCol")
                    row.prop(mat, "thea_MediumAbsorptionFilename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_MediumAbsorptionFilename", text="Absorption Color", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_MediumAbsorptionFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_MediumAbsorptionFilename"

                row = layout.row()
                if(mat.thea_MediumScatterFilename==""):
                    row.prop(mat, "thea_MediumScatterCol")
                    row.prop(mat, "thea_MediumScatterFilename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_MediumScatterFilename", text="Scatter Color", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_MediumScatterFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_MediumScatterFilename"

                row = layout.row()
                if(mat.thea_MediumAbsorptionDensityFilename==""):
                    row.prop(mat, "thea_MediumAbsorptionDensity")
                    row.prop(mat, "thea_MediumAbsorptionDensityFilename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_MediumAbsorptionDensityFilename", text="Absorption Density", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_MediumAbsorptionDensityFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_MediumAbsorptionDensityFilename"

                row = layout.row()
                if(mat.thea_MediumScatterDensityFilename==""):
                    row.prop(mat, "thea_MediumScatterDensity")
                    row.prop(mat, "thea_MediumScatterDensityFilename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_MediumScatterDensityFilename", text="Scatter Density", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_MediumScatterDensityFilename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_MediumScatterDensityFilename"

                split = layout.split()
                split.separator()
                row = layout.row()
                row.prop(mat, "thea_MediumCoefficient")
                if(mat.thea_MediumCoefficient):
                   row.prop(mat, "thea_MediumMenu")
                row = layout.row()
                row.prop(mat, "thea_MediumPhaseFunction")
                row = layout.row()
                if (getattr(mat, "thea_MediumPhaseFunction") in ("Henyey Greenstein")):
                   row.prop(mat, "thea_Asymetry")





class MATERIAL_PT_Components(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Layer Weight"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        mat = context.material

        matTuples = [(mat.thea_BasicOrder, "Basic", "thea_BasicOrder", "thea_BasicWeight"),
                     (mat.thea_Basic2Order, "Basic2", "thea_Basic2Order", "thea_Basic2Weight"),
                     (mat.thea_GlossyOrder, "Glossy", "thea_GlossyOrder", "thea_GlossyWeight"),
                     (mat.thea_Glossy2Order, "Glossy2", "thea_Glossy2Order", "thea_Glossy2Weight"),
                     (mat.thea_SSSOrder, "SSS", "thea_SSSOrder", "thea_SSSWeight"),
                     (mat.thea_ThinFilmOrder, "ThinFilm", "thea_ThinFilmOrder", "thea_ThinFilmWeight"),
                    ]
        sortedMats = sorted(matTuples, key=lambda mat: mat[0])
        for order, label, orderProp, weithProp in sortedMats:
            if getattr(mat, 'thea_'+label, 0):
                row = layout.row()
                row.label(label)
                row.prop(mat, 'thea_'+label, text="")
                row.prop(mat, orderProp)
                row.prop(mat, weithProp, text="Weight")
                row.prop(mat, 'thea_'+label+"WeightFilename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(getattr(mat,'thea_'+label+"WeightFilename")) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = 'thea_' + label + "WeightFilename"


def myCurveData(curve_name, origin=""):
#    myNodeTree(curve_name)
#    mat = bpy.context.material
    mat = bpy.context.active_object.active_material
    nodes = mat.node_tree.nodes
#    thea_globals.log.debug("Mat: %s - Nodes: %s" % (mat, nodes))
#    if 'ShaderNodeRGBCurve' not in mat.node_tree.nodes.type:
    for mat_node in mat.node_tree.nodes:
        if mat_node == 'CURVE_RGB':
            cn = nodes.new('ShaderNodeRGBCurve')

    if origin == "thea_BasicReflectCurve":
        return nodes[getattr(mat, "thea_BasicReflectCurve")]
    if origin == "thea_Basic2ReflectCurve":
        return nodes[getattr(mat, "thea_Basic2ReflectCurve")]
    if origin == "thea_GlossyReflectCurve":
        return nodes[getattr(mat, "thea_GlossyReflectCurve")]
    if origin == "thea_Glossy2ReflectCurve":
        return nodes[getattr(mat, "thea_Glossy2ReflectCurve")]
    if origin == "thea_CoatingReflectCurve":
        return nodes[getattr(mat, "thea_CoatingReflectCurve")]
    if origin == "thea_SSSReflectCurve":
        return nodes[getattr(mat, "thea_SSSReflectCurve")]


class toneMenu(TextureButtonsPanel, bpy.types.Menu):
    bl_label = "Tone Menu"
    bl_idname = "view3d.myMenu"
    COMPAT_ENGINES = {'THEA_RENDER'}
    origin = ""
    @classmethod
    def poll(cls, context):
        context = bpy.context.material
        thea_globals.log.debug("Context Tex panel 1: %s" % context)
        thea_globals.log.debug("Context Tex origin: %s" % origin)
#        context = bpy.data.textures

        thea_globals.log.debug("Context Tex panel 2: %s" % cls)
#        if (not getattr(context, "texture_slot", None)) or (context.texture_slot.name == ''):
#            return False
        engine = bpy.context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        thea_globals.log.debug("Context Tex panel CLS: %s - Context: %s" % (self, context))
        layout = self.layout
#        obj = bpy.context.object
        mat = bpy.context.material
        texName = bpy.context.object.active_material.active_texture.name
#        texName = Mat.name+ "_"
        tex = mat.texture_slots[texName].texture
#        tex = texName.texture
        thea_globals.log.debug("Context Tex panel 3: %s" % texName)
#        thea_globals.log.debug("Context Tex panel 3: %s" % tex)
#        layout.template_texture_user()
#        layout.template_image()
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colL.prop(tex,"thea_TexInvert")
        colL.prop(tex,"thea_TexGamma")
        colL.prop(tex,"thea_TexRed")
        colL.prop(tex,"thea_TexGreen")
        colL.prop(tex,"thea_TexBlue")
        colL.prop(tex,"thea_TexSaturation")
        colL.prop(tex,"thea_TexBrightness")
        colL.prop(tex,"thea_TexContrast")
        colL.prop(tex,"thea_TexClampMin")
        colL.prop(tex,"thea_TexClampMax")
        colL.separator()
        colL.operator("edit.externally", text="Edit externally")



class MATERIAL_PT_Component(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Material"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (thea_globals.showMatGui)and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material
        tex = context.texture

#------ Scattering
#        layout.separator()
#        layout.separator()
#        box = layout.box()
#        row = box.row()
#        row.label(text="Material Components")
        layout.label(text="Scattering")
        split = layout.split(percentage=0.3)
        split.label(text="Material:")
        row = split.row(align=True)
        row.prop(mat, "thea_MaterialComponent", text="")
#------ Basic
        if mat.thea_MaterialComponent == "Basic":
            row.prop(mat, "thea_Basic", text="Enabled")
            #row.operator("thea.sync_basic_to_blender", text="T>B")
            layout.operator("thea.sync_blender_to_basic", text="B>T")
            layout.separator()
#            split = layout.split()
#            row = layout.row()
#            row.label("     ")
#            row.label("     ")
            row = layout.row()
            if(mat.thea_BasicDiffuseFilename==""):
                row.prop(mat, "diffuse_color", text="Diffuse")
                row.prop(mat, "thea_BasicDiffuseFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_BasicDiffuseFilename", text="Diffuse", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicDiffuseFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicDiffuseFilename"

            row = layout.row()
            if(mat.thea_BasicReflectanceFilename==""):
                row.prop(mat, "thea_BasicReflectanceCol")
                row.prop(mat, "thea_BasicReflectanceFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_BasicReflectanceFilename", text= "Reflecance", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicReflectanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicReflectanceFilename"

            row = layout.row()
            if(mat.thea_BasicTranslucentFilename==""):
                row.prop(mat, "thea_BasicTranslucentCol")
                row.prop(mat, "thea_BasicTranslucentFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_BasicTranslucentFilename", text= "Translucency", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicTranslucentFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicTranslucentFilename"

            row = layout.row()
            row.prop(mat, "thea_BasicAbsorptionCol")
            row.prop(mat, "thea_BasicAbsorption")

            row = layout.row()
            layout.prop(mat, "thea_BasicIOR")
            layout.prop(mat, "thea_BasicEC")
            layout.prop(mat, "thea_BasicTrace")

            split = layout.split()
            layout.label(text="Structure")
            row = layout.row()
            row.prop(mat, "thea_BasicStructureSigma")
            row.prop(mat, "thea_BasicSigmaFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicSigmaFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicSigmaFilename"

            row = layout.row()
            row.prop(mat, "thea_BasicStructureRoughness")
            row.prop(mat, "thea_BasicRoughnessFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicRoughnessFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicRoughnessFilename"

            row = layout.row()
            row.prop(mat, "thea_BasicStructureAnisotropy")
            row.prop(mat, "thea_BasicAnisotropyFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicAnisotropyFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicAnisotropyFilename"

            row = layout.row()
            row.prop(mat, "thea_BasicStructureRotation")
            row.prop(mat, "thea_BasicRotationFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicRotationFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicRotationFilename"

            row = layout.row()
            row.prop(mat, "thea_BasicStructureBump")
            row.prop(mat, "thea_BasicBumpFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicBumpFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicBumpFilename"

            row = layout.row()
            layout.prop(mat, "thea_BasicStructureNormal")

            row = layout.row()
            row.prop(mat, "thea_BasicMicroRoughness")
            if(getattr(mat, "thea_BasicMicroRoughness", False)):
                row.prop(mat, "thea_BasicMicroRoughnessWidth")
                row.prop(mat, "thea_BasicMicroRoughnessHeight")
            if (((getattr(mat, 'thea_BasicReflectanceCol')[0], getattr(mat, 'thea_BasicReflectanceCol')[1], getattr(mat, 'thea_BasicReflectanceCol')[2])) != (0, 0, 0)) or len(getattr(mat, 'thea_BasicReflectanceFilename')) > 1:
                layout.separator()
                layout.label(text="Fresnel")
                row = layout.row()
                if(mat.thea_BasicReflect90Filename==""):
                    row.prop(mat, "thea_BasicReflect90Col")
                    row.prop(mat, "thea_BasicReflect90Filename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_BasicReflect90Filename", text="Reflectance 90", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_BasicReflect90Filename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicReflect90Filename"

                layout.prop(mat, "thea_BasicReflectionCurve")
                if mat.thea_BasicReflectionCurve:
                    layout.operator("update.curve_list")
#                    layout.prop(mat, "thea_BasicReflectCurve", text="Curve Name")
                    layout.template_curve_mapping(myCurveData(getattr(mat, "thea_BasicReflectCurve"), "thea_BasicReflectCurve"), "mapping")
                    layout.prop(mat, "thea_BasicReflectCurveList", text="CurveList")

#------ Basic2
        if mat.thea_MaterialComponent == "Basic2":
            row.prop(mat, "thea_Basic2", text="Enabled")
#             row = layout.row()
#             row.operator("thea.sync_basic_to_blender", text="T>B")
#             row.operator("thea.sync_blender_to_basic", text="B>T")
            layout.separator()
            #layout.prop(mat, "thea_BasicWeight")
            row = layout.row()
            if(mat.thea_Basic2DiffuseFilename==""):
                row.prop(mat, "thea_Basic2DiffuseCol")
                row.prop(mat, "thea_Basic2DiffuseFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_Basic2DiffuseFilename", text="Diffuse", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2DiffuseFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2DiffuseFilename"

            row = layout.row()
            if(mat.thea_Basic2ReflectanceFilename==""):
                row.prop(mat, "thea_Basic2ReflectanceCol")
                row.prop(mat, "thea_Basic2ReflectanceFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_BasicReflectanceFilename", text= "Reflecance", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_BasicReflectanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_BasicReflectanceFilename"

            row = layout.row()
            if(mat.thea_Basic2TranslucentFilename==""):
                row.prop(mat, "thea_Basic2TranslucentCol")
                row.prop(mat, "thea_Basic2TranslucentFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_Basic2TranslucentFilename", text= "Translucency", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2TranslucentFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2TranslucentFilename"

            row = layout.row()
            row.prop(mat, "thea_Basic2AbsorptionCol")
            row.prop(mat, "thea_Basic2Absorption")

            row = layout.row()
            layout.prop(mat, "thea_Basic2IOR")
            layout.prop(mat, "thea_Basic2EC")
            layout.prop(mat, "thea_Basic2Trace")

            split = layout.split()
            layout.label(text="Structure")
            row = layout.row()
            row.prop(mat, "thea_Basic2StructureSigma")
            row.prop(mat, "thea_Basic2SigmaFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2SigmaFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2SigmaFilename"

            row = layout.row()
            row.prop(mat, "thea_Basic2StructureRoughness")
            row.prop(mat, "thea_Basic2RoughnessFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2RoughnessFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2RoughnessFilename"

            row = layout.row()
            row.prop(mat, "thea_Basic2StructureAnisotropy")
            row.prop(mat, "thea_Basic2AnisotropyFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2AnisotropyFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2AnisotropyFilename"

            row = layout.row()
            row.prop(mat, "thea_Basic2StructureRotation")
            row.prop(mat, "thea_Basic2RotationFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2RotationFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2RotationFilename"

            row = layout.row()
            row.prop(mat, "thea_Basic2StructureBump")
            row.prop(mat, "thea_Basic2BumpFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Basic2BumpFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2BumpFilename"

            row = layout.row()
            layout.prop(mat, "thea_Basic2StructureNormal")
            row = layout.row()
            row.prop(mat, "thea_Basic2MicroRoughness")
            if(getattr(mat, "thea_Basic2MicroRoughness", False)):
                row.prop(mat, "thea_Basic2MicroRoughnessWidth")
                row.prop(mat, "thea_Basic2MicroRoughnessHeight")
            if (((getattr(mat, 'thea_Basic2ReflectanceCol')[0], getattr(mat, 'thea_Basic2ReflectanceCol')[1], getattr(mat, 'thea_Basic2ReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat, 'thea_Basic2ReflectanceFilename'))>1:
                layout.separator()
                layout.label(text="Fresnel")
                row = layout.row()
                if(mat.thea_Basic2Reflect90Filename==""):
                    row.prop(mat, "thea_Basic2Reflect90Col")
                row.prop(mat, "thea_Basic2Reflect90Filename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_Basic2Reflect90Filename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Basic2Reflect90Filename"

                layout.prop(mat, "thea_Basic2ReflectionCurve")
                if mat.thea_Basic2ReflectionCurve:
                    layout.operator("update.curve_list")
#                    layout.prop(mat, "thea_Basic2ReflectCurve", text="Curve Name")
                    layout.template_curve_mapping(myCurveData(getattr(mat, "thea_Basic2ReflectCurve"), "thea_Basic2ReflectCurve"), "mapping")
#                    layout.prop(mat, "thea_Basic2ReflectCurveList", text="CurveList")

#------ Glossy
        if mat.thea_MaterialComponent == "Glossy":
            row.prop(mat, "thea_Glossy", text="Enabled")
            #colL.operator("thea.sync_glossy_to_blender", text="T>B")
            layout.operator("thea.sync_blender_to_glossy", text="B>T")
            layout.separator()

            row = layout.row()
            sub = row
            sub.active = mat.thea_GlossyIORFileEnable == False
            if(mat.thea_GlossyReflectanceFilename==""):
                sub.prop(mat, "thea_GlossyReflectanceCol")
            sub.prop(mat, "thea_GlossyReflectanceFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_GlossyReflectanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyReflectanceFilename"

            #col.prop(mat, "thea_GlossyReflectanceCol")
            row = layout.row()
            sub = row
            sub.active = mat.thea_GlossyIORFileEnable == False
            if (mat.thea_GlossyTransmittanceFilename == ""):
                sub.prop(mat, "thea_GlossyTransmittanceCol")
            sub.prop(mat, "thea_GlossyTransmittanceFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_GlossyTransmittanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyTransmittanceFilename"
            #col.prop(mat, "thea_GlossyTransmittanceCol")
#            split = layout.split()
            row = layout.row()
            sub = row
            sub.active = mat.thea_GlossyIORFileEnable == False
            sub.prop(mat, "thea_GlossyAbsorptionCol")
            sub.prop(mat, "thea_GlossyAbsorption")

            split = layout.split()
            row = layout.row()
            col = split.column()
            sub = col
            sub.active = mat.thea_GlossyIORFileEnable == False
            sub.prop(mat, "thea_GlossyIOR")
            sub.prop(mat, "thea_GlossyEC")

            split = layout.split()
            row = layout.row()
            colL = split.column()
            sub = colL
            colR = split.column()
            sub.enabled = mat.thea_GlossyIORFileEnable == False
#            sub.active = mat.thea_GlossyIORFileEnable == False
            sub.prop(mat, "thea_GlossyAbbeNumberEnable")
            sub = colR
            sub.active = mat.thea_GlossyIORFileEnable == False
            sub.prop(mat, "thea_GlossyAbbeNumber")

            row = layout.row()
            split = layout.split()
            colL = split.column()
            sub = colL
            sub.enabled = mat.thea_GlossyAbbeNumberEnable == False
            sub.active = mat.thea_GlossyAbbeNumberEnable == False
            sub.prop(mat, "thea_GlossyIORFileEnable")
            colR = split.column(align=True)
            sub = colR
            sub.active = mat.thea_GlossyIORFileEnable == True
            sub.prop(mat, "thea_GlossyIORMenu", text="")
            sub.operator("glossy.iormenu", text="Search", icon="VIEWZOOM")

            split = layout.split()
            col = split.column()
            col.prop(mat, "thea_GlossyTraceReflections")
            col.prop(mat, "thea_GlossyTraceRefractions")

            split = layout.split()
            layout.label(text="Structure")
            row = layout.row()
            row.prop(mat, "thea_GlossyStructureRoughness")
            row.prop(mat, "thea_GlossyRoughnessFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_GlossyRoughnessFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyRoughnessFilename"

            row = layout.row()
            row.prop(mat, "thea_GlossyStructureRoughTrEn")
            sub = layout.row()
            sub.active = mat.thea_GlossyStructureRoughTrEn == True
            sub.prop(mat, "thea_GlossyStructureRoughnessTr")
            sub.prop(mat, "thea_GlossyRoughnessTrFilename", text="", icon='TEXTURE_DATA')
            sub = sub.row()
            sub.active = (len(mat.thea_GlossyRoughnessTrFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyRoughnessTrFilename"

            row = layout.row()
            row.prop(mat, "thea_GlossyStructureAnisotropy")
            row.prop(mat, "thea_GlossyAnisotropyFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_GlossyAnisotropyFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyAnisotropyFilename"

            row = layout.row()
            row.prop(mat, "thea_GlossyStructureRotation")
            row.prop(mat, "thea_GlossyRotationFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_GlossyRotationFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyRotationFilename"

            row = layout.row()
            row.prop(mat, "thea_GlossyStructureBump")
            row.prop(mat, "thea_GlossyBumpFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_GlossyBumpFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyBumpFilename"

            row = layout.row()
            layout.prop(mat, "thea_GlossyStructureNormal")
            row = layout.row()
            row.prop(mat, "thea_GlossyMicroRoughness")
            if(getattr(mat, "thea_GlossyMicroRoughness", False)):
                row.prop(mat, "thea_GlossyMicroRoughnessWidth")
                row.prop(mat, "thea_GlossyMicroRoughnessHeight")
            if (((getattr(mat, 'thea_GlossyReflectanceCol')[0], getattr(mat, 'thea_GlossyReflectanceCol')[1], getattr(mat, 'thea_GlossyReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat, 'thea_GlossyReflectanceFilename'))>1:
                layout.separator()
                layout.label(text="Fresnel")
                row = layout.row()
                if(mat.thea_GlossyReflect90Filename==""):
                    row.prop(mat, "thea_GlossyReflect90Col")
                row.prop(mat, "thea_GlossyReflect90Filename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_GlossyReflect90Filename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_GlossyReflect90Filename"
                layout.prop(mat, "thea_GlossyReflectionCurve")
                if mat.thea_GlossyReflectionCurve:
                    layout.operator("update.curve_list")
#                    layout.prop(mat, "thea_GlossyReflectCurve", text="Curve Name")
                    layout.template_curve_mapping(myCurveData(getattr(mat, "thea_GlossyReflectCurve"), "thea_GlossyReflectCurve"), "mapping")
                    layout.prop(mat, "thea_GlossyReflectCurveList", text="CurveList")


#------ Glossy2
        if mat.thea_MaterialComponent == "Glossy2":
            row.prop(mat, "thea_Glossy2", text="Enabled")
            layout.separator()

            row = layout.row()
            sub = row
            sub.active = mat.thea_Glossy2IORFileEnable == False
            if(mat.thea_Glossy2ReflectanceFilename==""):
                sub.prop(mat, "thea_Glossy2ReflectanceCol")
            sub.prop(mat, "thea_Glossy2ReflectanceFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Glossy2ReflectanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2ReflectanceFilename"

            row = layout.row()
            sub = row
            sub.active = mat.thea_Glossy2IORFileEnable == False
            if(mat.thea_Glossy2TransmittanceFilename==""):
                sub.prop(mat, "thea_Glossy2TransmittanceCol")
            sub.prop(mat, "thea_Glossy2TransmittanceFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Glossy2TransmittanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2TransmittanceFilename"

            row = layout.row()
            sub = row
            sub.active = mat.thea_Glossy2IORFileEnable == False
            sub.prop(mat, "thea_Glossy2AbsorptionCol")
            sub.prop(mat, "thea_Glossy2Absorption")

            split = layout.split()
            row = layout.row()
            col = split.column()
            sub = col
            sub.active = mat.thea_Glossy2IORFileEnable == False
            sub.prop(mat, "thea_Glossy2IOR")
            sub.prop(mat, "thea_Glossy2EC")

            split = layout.split()
            row = layout.row()
            colL = split.column()
            sub = colL
            colR = split.column()
            sub.enabled = mat.thea_Glossy2IORFileEnable == False
#            sub.active = mat.thea_Glossy2IORFileEnable == False
            sub.prop(mat, "thea_Glossy2AbbeNumberEnable")
            sub = colR
            sub.active = mat.thea_Glossy2IORFileEnable == False
            sub.prop(mat, "thea_Glossy2AbbeNumber")

            row = layout.row()
            split = layout.split()
            colL = split.column()
            sub = colL
            sub.enabled = mat.thea_Glossy2AbbeNumberEnable == False
            sub.active = mat.thea_Glossy2AbbeNumberEnable == False
            sub.prop(mat, "thea_Glossy2IORFileEnable")
            colR = split.column(align=True)
            sub = colR
            sub.active = mat.thea_Glossy2IORFileEnable == True
            sub.prop(mat, "thea_Glossy2IORMenu", text="")
            sub.operator("glossy2.iormenu", text="Search", icon="VIEWZOOM")

            split = layout.split()
            col = split.column()
            col.prop(mat, "thea_Glossy2TraceReflections")
            col.prop(mat, "thea_Glossy2TraceRefractions")

            split = layout.split()
            layout.label(text="Structure")
            row = layout.row()
            row.prop(mat, "thea_Glossy2StructureRoughness")
            row.prop(mat, "thea_Glossy2RoughnessFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Glossy2RoughnessFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2RoughnessFilename"

            row = layout.row()
            row.prop(mat, "thea_Glossy2StructureRoughTrEn")
            sub = layout.row()
            sub.active = mat.thea_Glossy2StructureRoughTrEn == True
            sub.prop(mat, "thea_Glossy2StructureRoughnessTr")
            sub.prop(mat, "thea_Glossy2RoughnessTrFilename", text="", icon='TEXTURE_DATA')
            sub = sub.row()
            sub.active = (len(mat.thea_Glossy2RoughnessTrFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2RoughnessTrFilename"

            row = layout.row()
            row.prop(mat, "thea_Glossy2StructureAnisotropy")
            row.prop(mat, "thea_Glossy2AnisotropyFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Glossy2AnisotropyFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2AnisotropyFilename"

            row = layout.row()
            row.prop(mat, "thea_Glossy2StructureRotation")
            row.prop(mat, "thea_Glossy2RotationFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Glossy2RotationFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2RotationFilename"

            row = layout.row()
            row.prop(mat, "thea_Glossy2StructureBump")
            row.prop(mat, "thea_Glossy2BumpFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_Glossy2BumpFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2BumpFilename"

            row = layout.row()
            layout.prop(mat, "thea_Glossy2StructureNormal")
            row = layout.row()
            row.prop(mat, "thea_Glossy2MicroRoughness")
            if(getattr(mat, "thea_Glossy2MicroRoughness", False)):
               row.prop(mat, "thea_Glossy2MicroRoughnessWidth")
               row.prop(mat, "thea_Glossy2MicroRoughnessHeight")
            if (((getattr(mat, 'thea_Glossy2ReflectanceCol')[0], getattr(mat, 'thea_Glossy2ReflectanceCol')[1], getattr(mat, 'thea_Glossy2ReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat, 'thea_Glossy2ReflectanceFilename'))>1:
                layout.separator()
                layout.label(text="Fresnel")
                row = layout.row()
                if(mat.thea_Glossy2Reflect90Filename==""):
                    row.prop(mat, "thea_Glossy2Reflect90Col")
                    row.prop(mat, "thea_Glossy2Reflect90Filename", text="", icon='TEXTURE_DATA')
                else:
                    row.prop(mat, "thea_Glossy2Reflect90Filename", text="Reflectance 90", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_Glossy2Reflect90Filename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_Glossy2Reflect90Filename"

                layout.prop(mat, "thea_Glossy2ReflectionCurve")
                if mat.thea_Glossy2ReflectionCurve:
                    layout.operator("update.curve_list")
#                    layout.prop(mat, "thea_Glossy2ReflectCurve", text="Curve Name")
                    layout.template_curve_mapping(myCurveData(getattr(mat, "thea_Glossy2ReflectCurve"), "thea_Glossy2ReflectCurve"), "mapping")
#                    layout.prop(mat, "thea_Glossy2ReflectCurveList", text="CurveList")


#------ SSS
        if mat.thea_MaterialComponent == "SSS":
            row.prop(mat, "thea_SSS", text="Enabled")
            layout.separator()

            row = layout.row()
            if(mat.thea_SSSReflectanceFilename==""):
                row.prop(mat, "thea_SSSReflectanceCol")
                row.prop(mat, "thea_SSSReflectanceFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_SSSReflectanceFilename", text="Reflectance", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_SSSReflectanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSReflectanceFilename"

            row = layout.row()
            row.prop(mat, "thea_SSSAbsorptionCol")
            row.prop(mat, "thea_SSSAbsorption")
            row = layout.row()
            row.prop(mat, "thea_SSSScatteringCol")
            row.prop(mat, "thea_SSSScattering")
            split = layout.split()
            row = layout.row()
            col = split.column()
            col.prop(mat, "thea_SSSAsymetry")
            col.prop(mat, "thea_SSSIOR")
            col.prop(mat, "thea_SSSTraceReflections")
            col.prop(mat, "thea_SSSTraceRefractions")

            split = layout.split()
            layout.label(text="Structure")
            row = layout.row()
            row.prop(mat, "thea_SSSStructureRoughness")
            row.prop(mat, "thea_SSSRoughnessFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_SSSRoughnessFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSRoughnessFilename"

            row = layout.row()
            row.prop(mat, "thea_SSSStructureRoughTrEn")
            sub = layout.row()
            sub.active = mat.thea_SSSStructureRoughTrEn == True
            sub.prop(mat, "thea_SSSStructureRoughnessTr")
            sub.prop(mat, "thea_SSSRoughnessTrFilename", text="", icon='TEXTURE_DATA')
            sub = sub.row()
            sub.active = (len(mat.thea_SSSRoughnessTrFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSRoughnessTrFilename"

            row = layout.row()
            row.prop(mat, "thea_SSSStructureAnisotropy")
            row.prop(mat, "thea_SSSAnisotropyFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_SSSAnisotropyFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSAnisotropyFilename"

            row = layout.row()
            row.prop(mat, "thea_SSSStructureRotation")
            row.prop(mat, "thea_SSSRotationFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_SSSRotationFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSRotationFilename"

            row = layout.row()
            row.prop(mat, "thea_SSSStructureBump")
            row.prop(mat, "thea_SSSBumpFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_SSSBumpFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSBumpFilename"

            row = layout.row()
            layout.prop(mat, "thea_SSSStructureNormal")
            row = layout.row()
            row.prop(mat, "thea_SSSMicroRoughness")
            if(getattr(mat, "thea_SSSMicroRoughness", False)):
                row.prop(mat, "thea_SSSMicroRoughnessWidth")
                row.prop(mat, "thea_SSSMicroRoughnessHeight")
            if (((getattr(mat, 'thea_SSSReflectanceCol')[0], getattr(mat, 'thea_SSSReflectanceCol')[1], getattr(mat, 'thea_SSSReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat, 'thea_SSSReflectanceFilename'))>1:
                layout.separator()
                layout.label(text="Fresnel")
                row = layout.row()
                if(mat.thea_SSSReflect90Filename==""):
                    row.prop(mat, "thea_SSSReflect90Col")
                row.prop(mat, "thea_SSSReflect90Filename", text="", icon='TEXTURE_DATA')
                sub = row.row()
                sub.active = (len(mat.thea_SSSReflect90Filename) > 1) == True
                sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSReflect90Filename"

                layout.prop(mat, "thea_SSSReflectionCurve")
                if mat.thea_SSSReflectionCurve:
                    layout.operator("update.curve_list")
#                    layout.prop(mat, "thea_SSSReflectCurve", text="Curve Name")
                    layout.template_curve_mapping(myCurveData(getattr(mat, "thea_SSSReflectCurve"), "thea_SSSReflectCurve"), "mapping")
#                    layout.prop(mat, "thea_SSSReflectCurveList", text="CurveList")

#------ Thinfilm
        if mat.thea_MaterialComponent == "ThinFilm":
            row.prop(mat, "thea_ThinFilm", text="Enabled")
            layout.separator()

            row = layout.row()
            split = layout.split()
            row = layout.row()
            #col.prop(mat, "thea_ThinFilmWeight")
            if(mat.thea_ThinFilmTransmittanceFilename==""):
                row.prop(mat, "thea_ThinFilmTransmittanceCol")
                row.prop(mat, "thea_ThinFilmTransmittanceFilename", text="", icon='TEXTURE_DATA')
            else:
                row.prop(mat, "thea_ThinFilmTransmittanceFilename", text="Transmittance", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_ThinFilmTransmittanceFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_ThinFilmTransmittanceFilename"

            split = layout.split()
            row = layout.row()
            col = split.column()
            col.prop(mat, "thea_ThinFilmIOR")

            row = layout.row()
            row.prop(mat, "thea_ThinFilmInterference")
            row = layout.row()
#            sub = col.row(align=False)
            row.active = mat.thea_ThinFilmInterference == True
            row.prop(mat, "thea_ThinFilmThickness")
            row.prop(mat, "thea_ThinFilmThicknessFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_ThinFilmThicknessFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_ThinFilmThicknessFilename"

#            col.prop(mat, "thea_ThinFilmThickness")
            row = layout.row()

            row.label(text="Structure")
#           CHANGED > Was given the name of glossy
            col = layout.column()
            row = col.row(align=False)
            row.prop(mat, "thea_ThinFilmStructureBump")
            row.prop(mat, "thea_ThinFilmBumpFilename", text="", icon='TEXTURE_DATA')
            sub = row.row()
            sub.active = (len(mat.thea_ThinFilmBumpFilename) > 1) == True
            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_ThinFilmBumpFilename"

            row = layout.row()
            row.prop(mat, "thea_ThinFilmStructureNormal")


#class MATERIAL_PT_Clipping(MaterialButtonsPanel, bpy.types.Panel):
#    bl_label = "Clipping"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#
#        if (not (len(bpy.context.active_object.data.materials)>0)):
#            return False
#
#        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)
#
#    def draw_header(self, context):
#        scene = context.scene
#        mat = context.material
#        self.layout.prop(mat, "thea_Clipping", text="")
#
#    def draw(self, context):
#        layout = self.layout
#        scene = context.scene
#        mat = context.material
#        split = layout.split()
#        row = layout.row()
#
#        if mat.get('thea_Clipping'):
##            col = layout.column()
#            row = layout.row()
#            row.prop(mat, "thea_ClippingFilename", text="Clipping", icon='TEXTURE_DATA')
#            sub = row.row()
#            sub.active = (len(mat.thea_SSSBumpFilename) > 1) == True
#            sub.operator("wm.call_tonemenu", text="", icon='SETTINGS').origin = "thea_SSSBumpFilename"
#
#            col = layout.column()
#            col.prop(mat, "thea_ClippingThreshold")
#            row = layout.row()
#            row.prop(mat, "thea_ClippingSoft")

#
#class MATERIAL_PT_Emittance(MaterialButtonsPanel, bpy.types.Panel):
#    bl_label = "Emittance"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#
#        if (not (len(bpy.context.active_object.data.materials)>0)):
#            return False
#
#        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)
#
#    def draw_header(self, context):
#       scene = context.scene
#       mat = context.material
#       self.layout.prop(mat, "thea_Emittance", text="")
#
#    def draw(self, context):
#       layout = self.layout
#       scene = context.scene
#       mat = context.material
#       split = layout.split()
#       row = layout.row()
#
#       if mat.get('thea_Emittance'):
#           row = layout.row()
#           if(mat.thea_EmittanceFilename==""):
#                row.prop(mat, "thea_EmittanceCol")
#           row.prop(mat, "thea_EmittanceFilename", text="", icon='TEXTURE_DATA')
#           row = layout.row()
#           row.prop(mat, "thea_EmittancePower")
##      CHANGED > Added this to hide with other light units
#           if getattr(context.material, "thea_EmittanceUnit") in ("Watts", "W/m2", "W/sr", "W/sr/m2"):
#               row.prop(mat, "thea_EmittanceEfficacy")
##           row.prop(mat, "thea_EmittanceEfficacy")
#           layout.prop(mat, "thea_EmittanceUnit")
#           row = layout.row()
#           row.prop(mat, "thea_EmittanceIES")
#           if(getattr(mat, "thea_EmittanceIES")):
#               row.prop(mat, "thea_EmittanceIESFilename", text="", icon='LAMP_DATA')
#               row = layout.row()
#               layout.prop(mat, "thea_EmittanceIESMultiplier")
#           row = layout.row()
#           layout.prop(mat, "thea_EmittancePassiveEmitter")
#           row = layout.row()
#           row.prop(mat, "thea_EmittanceAmbientEmitter")
#           if(getattr(mat, "thea_EmittanceAmbientEmitter")):
#               row.prop(mat, "thea_EmittanceAmbientLevel")
#           col = split.column()


#class MATERIAL_PT_Medium(MaterialButtonsPanel, bpy.types.Panel):
#    bl_label = "Medium"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#
#        if (not (len(bpy.context.active_object.data.materials)>0)):
#            return False
#
#        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)
#
#    def draw_header(self, context):
#       scene = context.scene
#       mat = context.material
#       self.layout.prop(mat, "thea_Medium", text="")
#
#    def draw(self, context):
#       layout = self.layout
#       scene = context.scene
#       mat = context.material
#       split = layout.split()
#       row = layout.row()
#
#       if mat.get('thea_Medium'):
#           row = layout.row()
#           if(mat.thea_MediumAbsorptionFilename==""):
#                row.prop(mat, "thea_MediumAbsorptionCol")
#           row.prop(mat, "thea_MediumAbsorptionFilename", text="", icon='TEXTURE_DATA')
#           row = layout.row()
#           if(mat.thea_MediumScatterFilename==""):
#                row.prop(mat, "thea_MediumScatterCol")
#           row.prop(mat, "thea_MediumScatterFilename", text="", icon='TEXTURE_DATA')
#           row = layout.row()
#           if(mat.thea_MediumAbsorptionDensityFilename==""):
#               row.prop(mat, "thea_MediumAbsorptionDensity")
#           row.prop(mat, "thea_MediumAbsorptionDensityFilename", text="", icon='TEXTURE_DATA')
#           row = layout.row()
#           if(mat.thea_MediumScatterDensityFilename==""):
#               row.prop(mat, "thea_MediumScatterDensity")
#           row.prop(mat, "thea_MediumScatterDensityFilename", text="", icon='TEXTURE_DATA')
#           row = layout.row()
#           row.prop(mat, "thea_MediumCoefficient")
#           if(mat.thea_MediumCoefficient):
#               row.prop(mat, "thea_MediumMenu")
#           row = layout.row()
#           row.prop(mat, "thea_MediumPhaseFunction")
#           row = layout.row()
#           if (getattr(mat, "thea_MediumPhaseFunction") in ("Henyey Greenstein")):
#               row.prop(mat, "thea_Asymetry")

#
#class MATERIAL_PT_Displacement(MaterialButtonsPanel, bpy.types.Panel):
#    bl_label = "Displacement"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#
#        if (not (len(bpy.context.active_object.data.materials)>0)):
#            return False
#
#        return (thea_globals.showMatGui) and (engine in cls.COMPAT_ENGINES)
#
#    def draw_header(self, context):
#       scene = context.scene
#       mat = context.material
#       self.layout.prop(mat, "thea_Displacement", text="")
#
#    def draw(self, context):
#       layout = self.layout
#       scene = context.scene
#       mat = context.material
#       split = layout.split()
#       row = layout.row()
#
#       if mat.get('thea_Displacement'):
#           row = layout.row()
#           col = split.column()
#           col.prop(mat, "thea_DisplacementFilename", text="", icon='TEXTURE_DATA')
#           col.prop(mat, "thea_DispSub")
##            col.prop(mat, "thea_DispBump")
#           col.prop(mat, "thea_DisplacementHeight")
#           col.prop(mat, "thea_DisplacementCenter")
#           col.prop(mat, "thea_DisplacementNormalSmooth")
#           col.prop(mat, "thea_DisplacementTightBounds")


class MATERIAL_PT_Thea_Strand(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Strand"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if hasattr(bpy.context, 'active_object'):
            try:
#               CHANGED > ADDED BETTER FILE CHECK
                extMat = os.path.isfile(os.path.abspath(bpy.path.abspath(bpy.context.active_object.active_material.get('thea_extMat'))))
            except:
                extMat = False
        try:
            return ((thea_globals.showMatGui) or extMat) and (engine in cls.COMPAT_ENGINES)
        except:
            pass

    def draw(self, context):
       layout = self.layout
       scene = context.scene
       mat = context.material
       tan = mat.strand
       split = layout.split()
       row = layout.row()
       col = split.column()
       col.prop(mat, "thea_StrandRoot")
       col.prop(mat, "thea_StrandTip")
       col.prop(mat, "thea_FastHairExport")
       col.prop(mat, "thea_ColoredHair")

class MATERIAL_PT_theaEditMaterial(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "External Thea Material"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        if hasattr(bpy.context, 'active_object'):
            try:
#               CHANGED > ADDED BETTER FILE CHECK
                extMat = os.path.isfile(os.path.abspath(bpy.path.abspath(bpy.context.active_object.active_material.get('thea_extMat'))))
            except:
                extMat = False
        return ((thea_globals.showMatGui) or extMat) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
       missing_Materials = []
       layout = self.layout
       scene = context.scene
       mat = context.material
       split = layout.split()
       row = layout.row()
       colL = split.column()
       colR = split.column()
       colL.operator("thea.thea_material_editor", text="Edit in Thea")
       colR.operator("thea.delete_material_link", text="Delete link")
       split = layout.split()
       row = layout.row()
       col = split.column()
       col.prop(mat, "thea_extMat")
# CHANGED > ADDED BETTER FILE CHECK
       try:
           if (os.path.exists(os.path.abspath(bpy.path.abspath(bpy.context.active_object.active_material.get('thea_extMat')))))==False:
                colR = split.column()
#                row = layout.row()
                colR.label(text="Missing link!", icon='ERROR')
                if getattr(mat, "thea_extMat"):
#                    row = layout.row()
                    layout.operator("thea.check_thea_mat")
                if missing_Materials:
                    thea_globals.log.debug("missing materials: %s" % missing_Materials)
                    for mis in missing_Materials:
                        row = col.row(align=True)
                        row.alignment = "LEFT"
                        row.label(text=mis[0], icon="IMAGE_DATA")
       except:
                pass
#       split = layout.split()
       if len(getattr(mat, "thea_extMat"))>5:
           if not thea_render_main.isMaterialLinkLocal(getattr(mat, "thea_extMat")):
                if os.path.exists(os.path.abspath(bpy.path.abspath(getattr(mat, "thea_extMat")))):
                    row = layout.row()
                    row.operator("thea.copy_material_locally")
           if getattr(mat, "thea_extMat"):
                row = layout.row()
                row.operator("thea.list_linked_materials")

#
##        print("local: ", thea_render_main.isMaterialLinkLocal(getattr(mat, "thea_extMat")))
##        print("exists: ", os.path.exists(os.path.abspath(bpy.path.abspath(getattr(mat, "thea_extMat")))), os.path.abspath(bpy.path.abspath(getattr(mat, "thea_extMat"))))

from bl_ui.properties_material import active_node_mat

def context_tex_datablock(context):
    idblock = context.material
    if idblock:
        return active_node_mat(idblock)

    idblock = context.lamp
    if idblock:
        return idblock

    idblock = context.world
    if idblock:
        return idblock

    idblock = context.brush
    if idblock:
        return idblock

    idblock = context.line_style
    if idblock:
        return idblock

    if context.particle_system:
        idblock = context.particle_system.settings

    return idblock


class TextureSlotPanel(TextureButtonsPanel):
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "texture_slot"):
            return False

        engine = context.scene.render.engine
        return TextureButtonsPanel.poll(cls, context) and (engine in cls.COMPAT_ENGINES)


# Texture Type Panels #


class TextureTypePanel(TextureButtonsPanel):

    @classmethod
    def poll(cls, context):
        tex = context.texture
        engine = context.scene.render.engine
        return tex and ((tex.type == cls.tex_type and not tex.use_nodes) and (engine in cls.COMPAT_ENGINES))

class TEXTURE_PT_Thea_mapping(TextureSlotPanel, Panel):
    bl_label = "Mapping"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        idblock = context_tex_datablock(context)
#         if isinstance(idblock, Brush) and not context.sculpt_object:
#             return False

        if (not getattr(context, "texture_slot", None)) or (context.texture_slot.name == ''):
            return False

        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        idblock = context_tex_datablock(context)

        tex = context.texture_slot


        if tex.rna_type.identifier=="MaterialTextureSlot":
            split = layout.split(percentage=0.3)
#            col = split.column()
            split.label(text="Coordinates:")
            split.prop(tex.texture, "thea_texture_coords")
            if getattr(tex.texture,"thea_texture_coords") == 'UV':
#                row = layout.row()
#                split = row
                split = layout.split(percentage=0.3)
                split.label(text="UV Channel:")
                split.prop(tex.texture, 'thea_TexUVChannel', text="")
#                 ob = context.object
#                 if ob and ob.type == 'MESH':
#                     split.prop_search(tex, "uv_layer", ob.data, "uv_textures", text="")
#                 else:
#                     split.prop(tex, "uv_layer", text="")
#            split = layout.split(percentage=0.3)
#            row = layout.row()
            if getattr(tex.texture, "thea_texture_coords") == 'Camera Map':
                split = layout.split(percentage=0.3)
                split.label(text="Camera:")
                split.prop(tex.texture, "thea_camMapName", text="")
#           CHANGED> if UV active dont show other mappings
#            if not tex.texture.thea_texture_coords == 'UV':
#                split.label(text="Projection:")
#                split.prop(tex, "mapping", text="")
            split = layout.split(percentage=0.3)
            split.label(text="Channel:")
            split.prop(tex.texture, "thea_TexChannel", text="")
            row = layout.row()
                #           CHANGED > Added repeat function textures
            row.prop(tex.texture,"thea_TexRepeat")
            if not getattr(tex.texture, "thea_texture_coords") == 'UV':
                row = layout.row()
#           CHANGED> Added spatial
                row.label(text="Spatial:")
                row.prop(tex.texture, "thea_TexSpatialXtex", text="X:")
                row.prop(tex.texture, "thea_TexSpatialYtex", text="Y:")

        row = layout.row()
        row.column().prop(tex, "offset")
        row.column().prop(tex, "scale")
        row = layout.row()
        row.prop(context.texture,"thea_TexRotation")


class TEXTURE_PT_Thea_ToneMap(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Tone"
    COMPAT_ENGINES = {'THEA_RENDER'}

    @classmethod
    def poll(cls, context):
        if (not getattr(context, "texture_slot", None)) or (context.texture_slot.name == ''):
            return False
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        tex = context.texture
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colL.prop(tex,"thea_TexInvert")
        colL.prop(tex,"thea_TexGamma")
        colL.prop(tex,"thea_TexRed")
        colL.prop(tex,"thea_TexGreen")
        colL.prop(tex,"thea_TexBlue")
        colL.prop(tex,"thea_TexSaturation")
        colL.prop(tex,"thea_TexBrightness")
        colL.prop(tex,"thea_TexContrast")
        colL.prop(tex,"thea_TexClampMin")
        colL.prop(tex,"thea_TexClampMax")
        colL.separator()
        colL.operator("edit.externally", text="Edit externally")


# class TEXTURE_PT_Thea_Component(TextureButtonsPanel, bpy.types.Panel):
#     bl_label = "Mapping"
#     COMPAT_ENGINES = {'THEA_RENDER'}
#
#
#     def draw(self, context):
#         layout = self.layout
#
#         tex = context.texture
#         split = layout.split()
#         row = layout.row()
#         colL = split.column()
#         colR = split.column()
#         colL.prop(tex,"thea_Basic")
#         colR.prop(tex,"thea_Basic2")
#         colL.prop(tex,"thea_Glossy")
#         colR.prop(tex,"thea_Coating")
#         colL.prop(tex,"thea_SSS")
#         colR.prop(tex,"thea_Clipping")
#         colR.prop(tex,"thea_Emittance")
#         colL.prop(tex,"thea_ThinFilm")


class RENDER_PT_theaTools(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Tools"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       mat = context.material
       self.layout.prop(scene, "thea_showTools", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        rd = context.scene.render

        if getattr(scene, "thea_showTools"):

            split = layout.split()
            colL = split.column()
            colR = split.column()
            colL.operator("thea.enable_animation_export", text="Enable animation export")
            colR.operator("thea.disable_animation_export", text="Disable animation export")
            colL.operator("thea.enable_animated", text="Enable mesh animation")
            colR.operator("thea.disable_animated", text="Disable mesh animation")
            colL.operator("thea.enable_caustic_receiver", text="Enable caustic receiver")
            colR.operator("thea.disable_caustic_receiver", text="Disable caustic receiver")
            colL.operator("thea.enable_trace_reflections", text="Enable trace reflections")
            colR.operator("thea.disable_trace_reflections", text="Disable trace reflections")
            colL.operator("thea.export_anim", text="Export Animation")
            colR.operator("thea.export_still_cameras", text="Export Still Cameras")
            colL.operator("thea.sync_with_thea", text="Sync with Thea")
            colR.operator("thea.sync_blender_to_thea", text="Enable basic components")
            colL.operator("thea.sync_cycles_to_thea", text="Convert Cycles materials")

class RENDER_PT_theaLUTTools(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Use Thea LUT"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       mat = context.material
       self.layout.prop(scene, "thea_useLUT", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        rd = context.scene.render

        if(getattr(scene, 'thea_useLUT')):
            split = layout.split()
            col = split.column()
            col.prop(scene, "thea_nameBasedLUT")
            col.prop(scene, "thea_materialsPath")
            col.operator("thea.materials_path", text="Set materials path")
            col.prop(scene, "thea_overwriteLUT")
            col.prop(scene, "thea_LUTScanSubdirectories")
            col.operator("thea.make_lut", text="Generate LUT file from Thea materials")
            try:
                col.label(text=" %s" % scene['thea_lutMessage'])
            except:
                pass


#class RENDER_PT_theaRender(RenderButtonsPanel, bpy.types.Panel):
##   CHANGED > Different naming so i made more sense
#    bl_label = "Thea Production & Export"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#        return (engine in cls.COMPAT_ENGINES)
#
#    def draw(self, context):
#
#        layout = self.layout
#        scene = context.scene
#
#        rd = context.scene.render
#
#        split = layout.split()
#
#        col = split.column()
#
#        if scene.get('thea_Warning'):
#            if len(scene.get('thea_Warning')) > 5:
#                row = layout.row()
#                row.label(text=scene['thea_Warning'])
##    CHANGED> Added render option window like cycles
#        split = layout.split(percentage=0.33)
#        split.label(text="Display:")
#        row = split.row(align=True)
#        row.prop(rd, "display_mode", text="")
#        row.prop(rd, "use_lock_interface", icon_only=True)
#        split = layout.split()
#        colL = split.column()
#        colR = split.column()
#        colL.operator("render.render", text="Image", icon='RENDER_STILL')
##      CHANGED > Changged to shorter name
#        colR.operator("thea.export_frame", text="Export to Studio" )
#        split = layout.split()
#        colL = split.column()
#        colR = split.column()
#        colL.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True
#        #colL.operator("thea.render_animation", text="Render Animation")
#        #colR.prop(scene,"thea_startTheaAfterExport")
##        CHANGED > Changed to shorter name
#        colR.operator("thea.save_frame", text="Save XML file")
#        col = layout.column()
#        col.label("Extra Options:")
#        split = layout.split()
#        colL = split.column()
#        colL.prop(scene,"thea_regionRender", text="Region Render")
#        if scene.thea_regionRender:
#            colL.prop(bpy.context.scene, "thea_regionSettings")
##            colL = split.column()
#            colR = split.column()
#            colR.prop(scene, "thea_regionDarkroom")
#            colR.operator("thea.export_frame", text="Render Region Studio" )
#            col = layout.column()
#        if scene.thea_regionRender !=True:
#            col = layout.column()
##        split = layout.split()
##        row = layout.row()
#
#        col.prop(scene,"thea_ExportAnimation")
#        col.prop(scene,"thea_AnimationEveryFrame")
#        col.prop(scene,"thea_HideThea")
#        col.prop(scene,"thea_ExitAfterRender")
#        col.prop(scene,"thea_stopOnErrors")
#        col.prop(scene,"thea_Reuse")
#        col.prop(scene,"thea_Selected")
#        col.prop(scene,"thea_RenderRefreshResult")
#        row = layout.row()


class VIEW3D_PT_theaIR(bpy.types.Panel):
    '''
    New GUI layout by Tomasz Muszynski
    '''

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Thea Interactive Render"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene = context.scene
        wm = context.window_manager
        layout = self.layout
        split = layout.split()
        row = layout.row()

        layout.prop(scene,"thea_IRAdvancedIR", text="Use Advanced IR Control")

# --- IR STOPPED -------------------------------------------------------------
        if not thea_globals.IrIsRunning:
            if not getattr(scene, 'thea_IRAdvancedIR'):

                layout.operator("thea.start_ir", text="Start IR", icon='PLAY')
            else:
                layout.label("Launch IR:")
                layout.operator("thea.start_ir", text="Start IR: FULL", icon='PLAY')
                layout.prop(scene,"thea_Selected", text="Export only selected objects")

                layout.separator()
                if not getattr(scene, "thea_Selected"):
                        if getattr(context.scene, 'thea_WasExported'):

                            layout.operator("thea.start_ir_reuse", text="Start IR: FAST", icon='NEXT_KEYFRAME')

                            layout.prop(scene, "thea_IRFullExportSelected", text="Do Full Export For Selected Objects and resue rest")
                layout.separator()

# --- IR is RUNNING -------------------------------------------------------------
        else:
            if not getattr(scene, 'thea_IRAdvancedIR'):

                layout.operator("thea.start_ir", text="Stop IR", icon='CANCEL')
            else:
                layout.label("Running IR Control:")
                layout.operator("thea.start_ir", text="Stop IR", icon='CANCEL')
                layout.separator()
                layout.separator()
                if not thea_globals.IrIsPaused:
                    layout.operator("thea.pause_ir", text="Pause IR", icon='PAUSE')
                else:
                    layout.operator("thea.pause_ir", text="Continue IR", icon='PLAY')
                layout.separator()
                layout.label("Scene objects update section:");
                layout.operator("thea.update_ir", text="Update selected objects", icon='FILE_REFRESH')
                layout.separator()
                layout.label("IR Image Operations:");
                layout.operator("thea.save_ir", text="Save IR result")
                layout.separator()

class VIEW3D_PT_theaIR_Advanced(bpy.types.Panel):
    '''
    New GUI layout by Tomasz Muszynski
    '''

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Thea IR Advanced Settings"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene = context.scene
        wm = context.window_manager
        layout = self.layout
        split = layout.split()
        row = layout.row()
# --- Advanced Settings-------------------------------------------------------------
#         layout.separator()

#         layout.prop(scene, 'thea_IRAdvancedSettings',text="Show Advanced Settings")
#         if getattr(scene, 'thea_IRAdvancedSettings'):

#         layout.separator()
        layout.label(" IR Engine Settings:", icon="FORWARD")
#         box = layout.box()
#         row = box.row()
        row.prop(scene, "thea_IRRenderEngineMenu")
        if getattr(scene, "thea_IRRenderEngineMenu").startswith("Presto"):
#             row = box.row()
            row = layout.row()
            row.prop(scene,"thea_IRDevice")
        if thea_globals.IrIsRunning == False:
#             row = box.row()
            row = layout.row()
            row.prop(scene,"thea_IRResolution")

        layout.separator()
        layout.label(" IR Draw Settings:", icon="FORWARD")
        box = layout.box()
        row = box.row()
        row.prop(scene,"thea_DrawPreviewto3dView")
        row = box.row()
        row.prop(scene,"thea_SavePreviewtoImage")
        row = box.row()
#        row.prop(scene,"thea_RefreshDelay")
        if getattr(scene,"thea_DrawPreviewto3dView"):# or getattr(scene,"thea_SavePreviewtoImage"):
            row = box.row()
            row.prop(scene,"thea_Fit3dView")
            row = box.row()
            row.prop(scene,"thea_IRBlendAlpha")
            row = box.row()
            row.prop(scene,"thea_RefreshDelay")
            row = box.row()
            row.prop(scene,"thea_IRShowTheaWindow")



            layout.separator()
            layout.label(" Export Behaviour:", icon="FORWARD")
            box = layout.box()
            row = box.row()
            row.prop(scene,"thea_IRFullUpdate")
            row = box.row()
            row.prop(scene,"thea_IRExportAnimation")

class VIEW3D_PT_theaIR_Keyboard(bpy.types.Panel):
    '''
    New GUI layout by Tomasz Muszynski
    '''

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Thea IR Keyboard control"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene = context.scene
        wm = context.window_manager
        layout = self.layout
        split = layout.split()
        row = layout.row()
# --- Keyboard control-------------------------------------------------------------


#         layout.separator()
#         layout.label(" Keyboard IR control:", icon="FORWARD")
#         box = layout.box()
#         row = box.row()
        row.prop(scene,"thea_IRRemapIRKeys", text="Use F11&F12 keys for IR" )
        row = layout.row()
#         row = box.row()
        row.label(" Change needs Blender restart.", icon="ERROR")
        row = layout.row()
#         row = box.row()
        row.label("Mapped Keys:")
        row = layout.row()
#         row = box.row()
        row.label("F12 - Start/Pause/Continue IR")
        row = layout.row()
#         row = box.row()
        row.label("CTRL+F12 - Stop IR")
        row = layout.row()
#         row = box.row()
        row.label("F11 - Update Selected")



#         layout.separator()


# class VIEW3D_PT_theaIR(bpy.types.Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_label = "Thea Interactive Render"
#     COMPAT_ENGINES = set(['THEA_RENDER'])
#
#     @classmethod
#     def poll(cls, context):
#         engine = context.scene.render.engine
#         return (engine in cls.COMPAT_ENGINES)
#
#     def draw(self, context):
#         scene = context.scene
#         wm = context.window_manager
#         layout = self.layout
#         split = layout.split()
#         row = layout.row()
# #        col = split.column()
# #         if not scene.thea_ir_running:
#
#         if not thea_globals.IrIsRunning:
#             layout.operator("thea.start_ir", text="Start IR", icon='PLAY')
# #                 layout.prop(scene, "thea_IRFullExportSelected", text="Export selected objects when starting IR")
#         else:
#             layout.operator("thea.start_ir", text="Stop IR", icon='CANCEL')
#             if not thea_globals.IrIsPaused:
#                 layout.operator("thea.pause_ir", text="Pause IR", icon='PAUSE')
#             else:
#                 layout.operator("thea.pause_ir", text="Continue IR", icon='PLAY')
#             layout.operator("thea.save_ir", text="Save IR result",)
# #@        col.prop(scene,"thea_Reuse")
#         #layout.label(getattr(scene, "thea_IRMessage"))
#         layout.prop(scene, 'thea_IRAdvancedSettings')
#         if getattr(scene, 'thea_IRAdvancedSettings'):
#             if getattr(context.scene, 'thea_WasExported'):
#                 if not thea_globals.IrIsRunning:
#                     layout.operator("thea.start_ir", text="Start IR: reuse mesh data", icon='PLAY').reuseProp = True
#                     layout.label("_______________________________________________________________________________________________")
#             layout.prop(scene, "thea_IRRenderEngineMenu")
#             if getattr(scene, "thea_IRRenderEngineMenu").startswith("Presto"):
#                 layout.prop(scene,"thea_IRDevice")
#             if thea_globals.IrIsRunning == False:
#                 layout.prop(scene,"thea_IRResolution")
#             layout.label("_______________________________________________________________________________________________")
#             layout.prop(scene,"thea_DrawPreviewto3dView")
#             layout.prop(scene,"thea_SavePreviewtoImage")
#             if getattr(scene,"thea_DrawPreviewto3dView"):# or getattr(scene,"thea_SavePreviewtoImage"):
#                 layout.prop(scene,"thea_Fit3dView")
#                 layout.prop(scene,"thea_IRBlendAlpha")
#
#
# #                 layout.prop(scene,"thea_RefreshDelay")
#
#             layout.prop(scene,"thea_IRShowTheaWindow")
#             layout.label("_______________________________________________________________________________________________")
#             if thea_globals.IrIsRunning:
# #                 layout.operator("thea.refresh_ir", text="Refresh", icon='FILE_REFRESH')
#                 layout.operator("thea.update_ir", text="Update selected objects", icon='FILE_REFRESH')
#                 layout.label("_______________________________________________________________________________________________")
#             layout.prop(scene,"thea_IRFullUpdate")
#             layout.prop(scene,"thea_Reuse", text="Prevent mesh export")
#             if getattr(scene, "thea_Reuse", False):
#                 layout.prop(scene, "thea_IRFullExportSelected", text="    Always full export selected objects when starting IR")
#             layout.prop(scene,"thea_Selected", text="Export only selected objects")
#             layout.prop(scene,"thea_IRExportAnimation")
#


class RENDER_PT_theaPresets(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Render Presets"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       mat = context.material
       self.layout.prop(scene, "thea_enablePresets", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if getattr(scene, "thea_enablePresets"):
           layout.prop(scene,"thea_RenderPresetsMenu")


class RENDER_PT_theaMain(RenderButtonsPanel, bpy.types.Panel):
#   CHANGED > Better and more understanding naming
    bl_label = "Thea Render"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)
#        return (getattr(context.scene, "thea_enablePresets") != True) and (engine in cls.COMPAT_ENGINES)
#                (getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (AMC)", "Presto (MC)", "Presto (AO)")))and

    def draw(self, context):
       layout = self.layout
       rd = context.scene.render
       scene = context.scene
       layout.prop(scene, "thea_enginesMenu", expand=True)
       split = layout.split()
       row = layout.row()
       col = split.column()
       if getattr(context.scene, "thea_enablePresets") != False:
            try:
                scene.thea_enginesMenu.Settings
            except:
                pass
#       layout.prop(scene, "thea_enginesMenu", expand=True)
       if getattr(scene, "thea_enginesMenu") in ("Render & Export"):
           if scene.get('thea_Warning'):
               if len(scene.get('thea_Warning')) > 5:
                  row = layout.row()
                  row.label(text=scene['thea_Warning'])
    #    CHANGED> Added render option window like cycles
           split = layout.split(percentage=0.33)
           split.label(text="Display:")
           row = split.row()
           row.prop(rd, "display_mode", text="")
           row.prop(rd, "use_lock_interface", icon_only=True)
           split = layout.split()
           colL = split.column(align=True)
           colR = split.column(align=True)
           colL.operator("render.render", text="Image", icon='RENDER_STILL')
           colL.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True
    #      CHANGED > Changged to shorter name

#           split = layout.split(align=True)
#           colL = split.column(align=True)
#           colR = split.column(align=True)
           colR.operator("thea.export_frame", text="Export to Studio" )
           #colL.operator("thea.render_animation", text="Render Animation")
           #colR.prop(scene,"thea_startTheaAfterExport")
    #       CHANGED > Changed to shorter name
           colR.operator("thea.save_frame", text="Save XML file")
           col = layout.column(align=True)
           col.label("Extra Options:")
           split = layout.split(align=True)
           colL = split.column()
           colL.prop(scene,"thea_regionRender", text="Region Render")
           if scene.thea_regionRender:
               colL.prop(bpy.context.scene, "thea_regionSettings")
    #           colL = split.column()
               colR = split.column()
               colR.prop(scene, "thea_regionDarkroom")
               colR.operator("thea.export_frame", text="Render Region Studio" )
               col = layout.column(align=True)
           if scene.thea_regionRender !=True:
               col = layout.column(align=True)
    #       split = layout.split()
    #       row = layout.row()

           col.prop(scene,"thea_ExportAnimation")
           col.prop(scene,"thea_AnimationEveryFrame")
           col.prop(scene,"thea_HideThea")
           col.prop(scene,"thea_ExitAfterRender")
           col.prop(scene,"thea_stopOnErrors")
           col.prop(scene,"thea_Reuse")
           col.prop(scene,"thea_Selected")
           col.prop(scene,"thea_RenderRefreshResult")
       if getattr(scene, "thea_enginesMenu") in ("Engines"):

           col = layout.column(align=True)#align=True)
           col.label("Main:")
           col.prop(scene,"thea_RenderEngineMenu")
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", ("Presto (MC)")):
               col.prop(scene,"thea_IRDevice")
           col.prop(scene,"thea_AASamp")
           col = layout.column(align=True)
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (AMC)", "Presto (AO)", "Presto (MC)"):
               col.prop(scene,"thea_RTTracingDepth")
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (AMC)"):
               col.prop(scene,"thea_adaptiveBias")
#           split = layout.split()
#           col.label("Tracing Depth:")
    #       CHANGED > Caustics only for AMC engine
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)"):
               col.prop(scene,"thea_RTGlossyDepth")
               col.prop(scene,"thea_RTDiffuseDepth")
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (AMC)"):
               col.prop(scene, "thea_GICaustics", text="Caustics")
    #       CHANGED > Extended only for PResto engine

           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", "Presto (MC)"):
               col = layout.column(align=True)
               col.prop(scene, "thea_ExtendedTracing")
               sub = layout.column(align=True)#align=True)
               sub.active = scene.thea_ExtendedTracing == True
               sub.prop(scene, "thea_TransparencyDepth")
               sub.prop(scene, "thea_InternalReflectionDepth")
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (MC)"):
               sub.prop(scene, "thea_SSSDepth")
    #           layout.label("Ambient Occlusion:")
    #           split = layout.split()
    #           col = split.column()
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)"):
               col = layout.column(align=True)
               col.prop(scene, "thea_AOEnable", text="Ambient Occlusion:")
               sub = layout.column(align=True)#align=True)
               sub.active = scene.thea_AOEnable == True
               sub.prop(scene,"thea_AODistance")
               sub.prop(scene,"thea_AOIntensity")
           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", "Presto (MC)"):
    #           split = layout.split()
               col = layout.column(align=True)
               col.prop(scene, "thea_ClampLevelEnable", text="Clamp Level:")
               sub = col
               sub.active = scene.thea_ClampLevelEnable == True
               sub.prop(scene, "thea_ClampLevel")
           split = layout.split()
           col = layout.column(align=True)
           col.prop(scene,"thea_RenderMBlur")
    #       CHANGED> added displacement
           col.prop(scene,"thea_displacemScene")
           col.prop(scene,"thea_RenderVolS")
           col.prop(scene,"thea_RenderLightBl")
    #      CHANGED > Added Clay render


           split = layout.split()
           colL = split.column()
           colR = split.column()
           colL.label("Clay Render:")
           colR.label("")
           colL.prop(scene,"thea_clayRender", text="Enable:")
           sub = colR
           sub.active = bpy.context.scene.thea_clayRender == True
           sub.prop(bpy.context.scene, "thea_clayRenderReflectance")

           split = layout.split()
           col.separator()
           col = layout.column(align=True)
           col.label("Termination:")
           col.prop(scene,"thea_RenderTime")
           #col.prop(scene,"thea_RenderMaxPasses")
           col.prop(scene,"thea_RenderMaxSamples")

           split = layout.split()
           col.separator()
           col = layout.column(align=True)
           col.label("Distribution Render:")
           col.prop(scene,"thea_distributionRender", text="Enable")
           if scene.thea_distributionRender:
               col.prop(scene,"thea_DistTh")
               col.prop(scene,"thea_DistPri")
               col.prop(scene,"thea_DistNet")
               if getattr(context.scene,"thea_DistNet") in ("1","2", "3"):
                  col.prop(scene,"thea_DistPort")
                  col.prop(scene,"thea_DistAddr")
               if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", "Presto (MC)"):
                  col.prop(scene,"thea_BucketRendering")

#           if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", "Presto (MC)"):
#               col = layout.column(align=True)
#               col.label("Device:")
#               col.prop(scene,"thea_IRDevice")
#               col.prop(scene,"thea_cpuDevice")
#               split = layout.split()
#               col = split.column()
#               colL = col
#               colR = col
#               sub = colR
#               colL.prop(scene,"thea_cpuThreadsEnable")
#               sub.active = scene.thea_cpuThreadsEnable == True
#               sub.prop(scene,"thea_cpuThreads")
#               col.separator()

    #      CHANGED > Added Marker names + Custom Name
#           col.separator()
#           col = split.column()
           col.separator()
           col = layout.column(align=True)

           col.label("Extra Options:")
    #      CHANGED > Added button to save img.thea file
           col.prop(scene,"thea_ImgTheaFile")
           col.prop(scene,"thea_save2Export")
           col.prop(scene,"thea_markerName")
           col.prop(scene,"thea_customOutputName")
           if getattr(scene, "thea_customOutputName"):
               col.prop(scene,"thea_customName")


       if getattr(scene, "thea_enginesMenu") in ("Channels"):
#           if getattr(scene, "thea_showChannels"):

           if (getattr(scene, "thea_enablePresets")!=False):
               col = layout.column()
               col = col.box()
               col.label("Not all channels are supported with certain presets.")
#               col.label(" ")
           split = layout.split()
           row = layout.row()
           col = split.column(align=True)
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelNormal")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelPosition")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelUV")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelDepth")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelAlpha")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelObject_Id")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
               col.prop(scene,"thea_channelMaterial_Id")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")) or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelShadow")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelRaw_Diffuse_Color")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelRaw_Diffuse_Lighting")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelRaw_Diffuse_GI")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelDirect")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelAO")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelGI")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelSelf_Illumination")
#CHANGED> Turned this back on
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelSSS")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelSeparatePassesPerLight")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelReflection")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelRefraction")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelTransparent")
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelIrradiance")
#CHANGED> Turned mask id back ON
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelMask")
#CHNAGED> Turned invert mask channel back ON
           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)"))or (getattr(scene, "thea_enablePresets")!=False):
               col.prop(scene,"thea_channelInvert_Mask")



class RENDER_PT_theaDisplay(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Display"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        scene = context.scene
        layout = self.layout
#        CHANGED > added for object picker zdepth
        obj = context.object
        split = layout.split()
        col = split.column()
        col.prop(scene,"thea_DisplayMenuEnable", text="Display Presets")
        if getattr(scene, "thea_DisplayMenuEnable"):
#            layout.label("Display presets:")
            col.prop(scene,"thea_DisplayMenu", text="")
            split = layout.split()
            row = layout.row()
            colL = split.column()
            colR = split.column()
            sub = colL
            sub.operator("unload.displaypreset", text="Revert")
            sub.active = thea_globals.displayPreset == True
            sub.enabled = thea_globals.displayPreset == True
            sub = colR
            colR.operator("load.displaypreset", text="Set")
            if getattr(scene,"thea_DisplayMenu") == thea_globals.displaySet:
                sub.enabled = thea_globals.displayPreset == False

        layout.separator()
        split = layout.split(percentage=0.35)
        colL = split.column()
        colR = split.column()
        colL.label("Channel:")
        colR.prop(scene,"thea_viewChannel", text="")
        layout.separator()
        layout.prop(scene,"thea_DispISO")
        layout.prop(scene,"thea_DispShutter")
        layout.prop(scene,"thea_DispFNumber")
        layout.prop(scene,"thea_DispGamma")
        layout.prop(scene,"thea_DispBrightness")
        layout.prop(scene,"thea_DispCRFMenu")
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
#       CHANGED > added the new active/inactive menu's, new sharpness, bloom items and diaphgrama options
#       CHANGED > Redid order
        colL.prop(scene,"thea_DispSharpness")
#        if getattr(scene,"thea_DispSharpness"):
#            colR.prop(scene,"thea_DispSharpnessWeight")
        sub = colR.row()
        sub.active = scene.thea_DispSharpness == True
        sub.prop(scene, "thea_DispSharpnessWeight")
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispBurn")
#        if getattr(scene,"thea_DispBurn"):
#            colR.prop(scene,"thea_DispBurnWeight")
        sub = colR.row()
        sub.active = scene.thea_DispBurn == True
        sub.prop(scene,"thea_DispBurnWeight")
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispVignetting")
        sub = colR.row()
        sub.active = scene.thea_DispVignetting == True
        sub.prop(scene,"thea_DispVignettingWeight")

        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispChroma")
        sub = colR.row()
        sub.active = scene.thea_DispChroma == True
        sub.prop(scene,"thea_DispChromaWeight")

        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispContrast")
        sub = colR.row()
        sub.active = scene.thea_DispContrast == True
        sub.prop(scene,"thea_DispContrastWeight")

        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispTemperature")
        sub = colR.row()
        sub.active = scene.thea_DispTemperature == True
        sub.prop(scene,"thea_DispTemperatureWeight")

        split = layout.split()
        row = layout.row()
        colL.prop(scene,"thea_DispBloom")
        sub = colR.row()
        sub.active = scene.thea_DispBloom == True
        sub.prop(scene,"thea_DispBloomItems")
#        split = layout.split()
        row = layout.row()
        if getattr(scene,"thea_DispBloom"):
            colR.prop(scene,"thea_DispBloomWeight")
            colR.prop(scene,"thea_DispGlareRadius")
#      CHANGED > Added label + Z-depth camera numbers
        layout.label(text="Z-depth:")
        sub = layout.row()
        sub.active = scene.thea_ZdepthClip | scene.thea_ZdepthDOF == False
        sub.prop(scene,"thea_DispMinZ")
        sub.prop(scene,"thea_DispMaxZ")
        row = layout.row()
        colL = row.column()
        colR = row.column()
#        colL.prop(scene, "thea_zdepthObj", text="Distance")
#        if not scene.thea_zdepthObj:
#                view = context.space_data
#                if view and view.camera == scene and view.region_3d.view_perspective == 'CAMERA':
#                    props = layout.operator("ui.eyedropper_depth", text="DOF Distance (Pick)")
#                else:
#                    props = layout.operator("wm.context_modal_mouse", text="DOF Distance")
#                    props.data_path_iter = "selected_editable_objects"
#                    props.data_path_item = "data.zdepth_object"
#                    props.input_scale = 0.02
#                    props.header_text = "Z-depth Distance: %.3f"
#                del view
#        else:
#            pass

#        colL.prop(cam, "thea_ZdepthObj", text="Distance")
        colL.prop(scene, "thea_ZdepthDOF")
        colL.prop(scene,"thea_ZdepthDOFmargin")
        colR.prop(scene, "thea_ZdepthClip")

        layout.separator()
#        col.prop(scene,"thea_analysis", text="Analysis:")
        split = layout.split()
        colL = split.column()
        colR = split.column()
        colL.label("Analysis:")
        colR.prop(scene,"thea_analysisMenu", text="")
#        thea_globals.log.debug(getattr(scene,"thea_analysisMenu"))
        sub = layout.column()
#        col.prop(scene,"thea_analysis", text="Analysis:")
        sub.prop(scene,"thea_minIlLum")
        sub.prop(scene,"thea_maxIlLum")
        sub.active = scene.thea_analysisMenu == '1'
        layout.separator()


#class RENDER_PT_theaDistribution(RenderButtonsPanel, bpy.types.Panel):
#    bl_label = "Distribution"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
##   CHANGED > Added this to hide when remote is not active
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#        return (getattr(context.scene, "thea_showRemoteSetup") != False) and (engine in cls.COMPAT_ENGINES)
#
##    @classmethod
##    def poll(cls, context):
##        engine = context.scene.render.engine
##        return (engine in cls.COMPAT_ENGINES)
#
#    def draw(self, context):
#       layout = self.layout
#       scene = context.scene
#       split = layout.split()
#       row = layout.row()
#       col = split.column()
#       col.prop(scene,"thea_DistTh")
#       col.prop(scene,"thea_DistPri")
#       col.prop(scene,"thea_DistNet")
#       col.prop(scene,"thea_DistPort")
#       col.prop(scene,"thea_DistAddr")
#       col.prop(scene,"thea_BucketRendering")

class RENDER_PT_BiasedSettings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Biased Settings"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return ((getattr(context.scene, "thea_enablePresets") != True) and
                (getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (BSD)"))) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
       layout = self.layout
       scene = context.scene
       #split = layout.split()
       #row = layout.row()
       box = layout.box()
       row = box.row()
       row.label("Biased RT")
       row = box.row()
       row.prop(scene,"thea_RTTracingDepth")
       row = box.row()
       row.prop(scene,"thea_RTGlossyDepth")
       row = box.row()
       row.prop(scene,"thea_RTDiffuseDepth")
       row = box.row()
       row.prop(scene,"thea_RTTraceReflections")
       row = box.row()
       row.prop(scene,"thea_RTTraceRefractions")
       row = box.row()
       row.prop(scene,"thea_RTTraceTransparencies")
       row = box.row()
       row.prop(scene,"thea_RTTraceDispersion")
       layout.separator()
       box = layout.box()
       row = box.row()
#        layout.label("_______________________________________________________________________________________________")
       row.label("Biased Antialiasing")
       row = box.row()
       row.prop(scene,"thea_AACont")
       row = box.row()
       row.prop(scene,"thea_AAMinSub")
       row = box.row()
       row.prop(scene,"thea_AAMaxSub")
       row = box.row()

       layout.separator()
       box = layout.box()
       row = box.row()
       row.label("Biased Direct Lighting")
       row.prop(scene, "thea_DLEnable", text="")
       if scene.thea_DLEnable:
           row = box.row()
           row.prop(scene,"thea_DLPerceptualBased")
           row = box.row()
           row.prop(scene,"thea_DLMaxError")

       layout.separator()
       box = layout.box()
       row = box.row()
       row.label("Biased Blurred Reflections")
       row.prop(scene, "thea_BREnable", text="")
       if scene.thea_BREnable:
           row = box.row()
           row.prop(scene,"thea_BRMinSub")
           row = box.row()
           row.prop(scene,"thea_BRMaxSub")

       layout.separator()
       box = layout.box()
       row = box.row()

       row.label("Field Mapping")
       row.prop(scene, "thea_FMEnable", text="")
       row = box.row()
       if scene.thea_FMEnable:
           row = box.row()
           row.prop(scene,"thea_FMFieldDensity")
           row = box.row()
           row.prop(scene,"thea_FMCellSize")

       layout.separator()
       box = layout.box()
       row = box.row()
       row.label("Caustics")
       row.prop(scene, "thea_GICaustics", text="")
       if scene.thea_GICaustics:
           row = box.row()
           row.prop(scene,"thea_CausticLock")
           row = box.row()
           row.prop(scene,"thea_GICausticSharp")
           row = box.row()
           row.prop(scene,"thea_GICausticCaptured")
           row = box.row()
           row.prop(scene,"thea_GICausPh")
       layout.separator()
       box = layout.box()
       row = box.row()
       row.label("Biased Final Gathering")
       row.prop(scene, "thea_FGEnable", text="")
       if scene.thea_FGEnable:
           row = box.row()
           row.prop(scene,"thea_GIRays")
           row = box.row()
           row.prop(scene,"thea_FGAdaptiveSteps")
           row = box.row()
           row.prop(scene,"thea_FGEnableSecondary")
           if scene.thea_FGEnableSecondary:
               row = box.row()
               row.prop(scene,"thea_FGDistanceThreshold")
           row = box.row()
           row.prop(scene,"thea_FGDiffuseDepth")
           row = box.row()
           row.prop(scene,"thea_GITracingDepth")
           row = box.row()
           row.prop(scene,"thea_FGGlossyDepth")
           row.prop(scene,"thea_FGGlossyEvaluation")
           row = box.row()
           row.prop(scene,"thea_FGCausticEvaluation")
       layout.separator()
       box = layout.box()
       row = box.row()
       row.label("Biased Irradiance Cache")
       row = box.row()
       row.prop(scene, "thea_ICEnable", text="")
       if scene.thea_ICEnable:
           row = box.row()
           row.prop(scene,"thea_ICLock")
           row = box.row()
           row.prop(scene,"thea_ICAccuracy")
           row = box.row()
           row.prop(scene,"thea_ICMinDistance")
           row = box.row()
           row.prop(scene,"thea_ICMaxDistance")
           row.prop(scene,"thea_ICPrepass")
           row = box.row()
           row.prop(scene,"thea_ICPrepassBoost")
           row = box.row()
           row.prop(scene,"thea_ICForceInterpolation")


#class RENDER_PT_IREngineSettings(RenderButtonsPanel, bpy.types.Panel):
#    bl_label = "Interactive Engine Settings"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#        return ((getattr(context.scene, "thea_enablePresets") != True) and
#                (getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (AMC)", "Presto (MC)", "Presto (AO)"))) and (engine in cls.COMPAT_ENGINES)
#
#    def draw(self, context):
#       layout = self.layout
#       scene = context.scene
##       split = layout.split()
#       col = layout.column()#align=True)
#       col.prop(scene,"thea_RTTracingDepth")
##       CHANGED > Caustics only for AMC engine
#       if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)"):
#           col.prop(scene,"thea_RTGlossyDepth")
#           col.prop(scene,"thea_RTDiffuseDepth")
#       if getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (AMC)"):
#           layout.prop(scene, "thea_GICaustics", text="Caustics")
##       CHANGED > Extended only for PResto engine
#
#       if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", "Presto (MC)"):
##           col = layout.column()
#           layout.prop(scene, "thea_ExtendedTracing")
#           sub = layout.column()#align=True)
#           sub.active = scene.thea_ExtendedTracing == True
#           sub.prop(scene, "thea_TransparencyDepth")
#           sub.prop(scene, "thea_InternalReflectionDepth")
#       if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (MC)"):
#           sub.prop(scene, "thea_SSSDepth")
##           layout.label("Ambient Occlusion:")
##           split = layout.split()
##           col = split.column()
#       if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)"):
##           col = layout.column()
#           layout.prop(scene, "thea_AOEnable", text="Ambient Occlusion:")
#           sub = layout.column()#align=True)
#           sub.active = scene.thea_AOEnable == True
#           sub.prop(scene,"thea_AODistance")
#           sub.prop(scene,"thea_AOIntensity")
#       if getattr(context.scene, "thea_RenderEngineMenu") in ("Presto (AO)", "Presto (MC)"):
##           split = layout.split()
##           col = layout.column()
#           layout.prop(scene, "thea_ClampLevelEnable", text="Clamp Level:")
#           sub = layout.column()
#           sub.active = scene.thea_ClampLevelEnable == True
#           sub.prop(scene, "thea_ClampLevel")
#




class RENDER_PT_theaAO(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Ambient Occlusion"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return ((getattr(context.scene, "thea_enablePresets") != True) and
#               CHANGED > Added this to hide with MCp and AMC
               (getattr(context.scene, "thea_RenderEngineMenu") in ("Adaptive (BSD)")))and (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_AOEnable", text="")

    def draw(self, context):
       layout = self.layout
       scene = context.scene
       split = layout.split()
       row = layout.row()
       col = split.column()
       if scene.thea_AOEnable:
           col.prop(scene,"thea_AOMultiply")
           col.prop(scene,"thea_AOClamp")
           col.prop(scene,"thea_AOSamples")
           col.prop(scene,"thea_AODistance")
           col.prop(scene,"thea_AOIntensity")
           col.prop(scene,"thea_AOLowColor")
           col.prop(scene,"thea_AOHighColor")



class RENDER_PT_theaSetup(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Setup"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       mat = context.material
       self.layout.prop(scene, "thea_showSetup", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if getattr(scene, "thea_showSetup"):
            layout.prop(scene,"thea_LogLevel")
            layout.prop(scene,"thea_ApplicationPath")
            layout.prop(scene,"thea_DataPath")
            layout.prop(scene,"thea_IRFontSize")
            layout.label("Merge settigns:")
            layout.prop(scene,"thea_MerModels")
            layout.prop(scene,"thea_MerLights")
            layout.prop(scene,"thea_MerCameras")
            layout.prop(scene,"thea_MerEnv")
            layout.prop(scene,"thea_MerRender")
            layout.prop(scene,"thea_MerMaterials")
            layout.prop(scene,"thea_MerSurfaces")


class RENDER_PT_theaSDKSetup(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Remote Setup"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       mat = context.material
       self.layout.prop(scene, "thea_showRemoteSetup", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if getattr(scene, "thea_showRemoteSetup"):
           scene = context.scene
           split = layout.split()
           row = layout.row()
           col = split.column()
           col.prop(scene,"thea_SDKPort")
           col.prop(scene,"thea_PreviewSDKPort")
           #col.prop(scene,"thea_StartTheaDelay")

class RENDER_PT_theaMergeScene(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Merge Scene"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       mat = context.material
       self.layout.prop(scene, "thea_showMerge", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if getattr(scene, "thea_showMerge"):
           split = layout.split()
           row = layout.row()
           col = split.column()

           col.prop(scene,"thea_SceneMerModels")
           col.prop(scene,"thea_SceneMerLights")
           col.prop(scene,"thea_SceneMerCameras")
           col.prop(scene,"thea_SceneMerRender")
           col.prop(scene,"thea_SceneMerEnv")
           col.prop(scene,"thea_SceneMerMaterials")
           col.prop(scene,"thea_SceneMerReverseOrder")
           col.prop(scene,"thea_mergeFilePath")
           col.operator("thea.merge_file", text="Select file")



#class RENDER_PT_theaChannels(RenderButtonsPanel, bpy.types.Panel):
#    bl_label = "Thea Channels"
#    COMPAT_ENGINES = set(['THEA_RENDER'])
#
#    @classmethod
#    def poll(cls, context):
#        engine = context.scene.render.engine
#        return (engine in cls.COMPAT_ENGINES)
#
#    def draw_header(self, context):
#       scene = context.scene
#       mat = context.material
#       self.layout.prop(scene, "thea_showChannels", text="")
#
#    def draw(self, context):
#        layout = self.layout
#        scene = context.scene
#
#        if getattr(scene, "thea_showChannels"):
#           split = layout.split()
#           row = layout.row()
#           col = split.column()
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelNormal")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelPosition")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelUV")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelDepth")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelAlpha")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelObjectId")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelMaterialId")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelShadow")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelRawDiffuseColor")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelRawDiffuseLighting")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelRawDiffuseGI")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelDirect")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)")):
#               col.prop(scene,"thea_channelAO")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelGI")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelSelfIllumination")
##CHANGED> Turned this back on
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (MC)")):
#               col.prop(scene,"thea_channelSSS")
##           if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
##               col.prop(scene,"thea_channelSeparatePassesPerLight")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelReflection")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
#               col.prop(scene,"thea_channelRefraction")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)")):
#               col.prop(scene,"thea_channelTransparent")
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)")):
#               col.prop(scene,"thea_channelIrradiance")
##CHANGED> Turned mask id back ON
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelMask")
##CHNAGED> Turned invert mask channel back ON
#           if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
#               col.prop(scene,"thea_channelInvertMask")
#CHANGED > Added GLobal Medium Panel
class RENDER_PT_theaGlobMedium(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Global Medium"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_GlobalMediumEnable", text="")

    def draw(self, context):
       layout = self.layout
       scene = context.scene
#       mat = context.material
       split = layout.split()
       row = layout.row()

       if scene.thea_GlobalMediumEnable:
           row = layout.row()
           row .prop(scene, "thea_GlobalMediumIOR")
           row = layout.row()
#           split = layout.split()
           if(scene.thea_MediumAbsorptionFilename==""):
                row.prop(scene, "thea_MediumAbsorptionCol")
           row.prop(scene, "thea_MediumAbsorptionFilename", text="", icon='TEXTURE_DATA')
           row = layout.row()
           if(scene.thea_MediumScatterFilename==""):
                row.prop(scene, "thea_MediumScatterCol")
           row.prop(scene, "thea_MediumScatterFilename", text="", icon='TEXTURE_DATA')
           row = layout.row()
           if(scene.thea_MediumAbsorptionDensityFilename==""):
               row.prop(scene, "thea_MediumAbsorptionDensity")
           row.prop(scene, "thea_MediumAbsorptionDensityFilename", text="", icon='TEXTURE_DATA')
           row = layout.row()
           if(scene.thea_MediumScatterDensityFilename==""):
               row.prop(scene, "thea_MediumScatterDensity")
           row.prop(scene, "thea_MediumScatterDensityFilename", text="", icon='TEXTURE_DATA')
           row = layout.row()
           row.prop(scene, "thea_MediumCoefficient")
           if(scene.thea_MediumCoefficient):
               row.prop(scene, "thea_MediumMenu")
           row = layout.row()
           row.prop(scene, "thea_MediumPhaseFunction")
           row = layout.row()
           if (getattr(context.scene, "thea_MediumPhaseFunction") in ("Henyey Greenstein")):
               row.prop(scene, "thea_Asymetry")



class RENDER_PT_theaIBL(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Image Based Lighting"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_IBLEnable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        if scene.thea_IBLEnable:
           layout.prop(scene,"thea_IBLTypeMenu")
           layout.prop(scene,"thea_IBLWrappingMenu")
           layout.prop(scene,"thea_IBLFilename", icon='TEXTURE_DATA')
           layout.prop(scene,"thea_IBLRotation")
           layout.prop(scene,"thea_IBLIntensity")
           split = layout.split()
           col = split.column()
           col.prop(scene,"thea_IBLEnableColor")
           sub = split.column()
           sub.active = scene.thea_IBLEnableColor == True
           sub.prop(scene, "thea_IBLColorFilename", icon='TEXTURE_DATA')


class RENDER_PT_theaBackgroundMapping(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Background Mapping"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_BackgroundMappingEnable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        split = layout.split()
        row = layout.row()
        col = split.column()
        if scene.thea_BackgroundMappingEnable:
          col.prop(scene,"thea_BackgroundMappingWrappingMenu")
          col.prop(scene,"thea_BackgroundMappingFilename", icon='TEXTURE_DATA')
          #col.operator("thea.backgroundmapping_file", text="Select file")
          col.prop(scene,"thea_BackgroundMappingRotation")
          col.prop(scene,"thea_BackgroundMappingIntensity")

class RENDER_PT_theaReflectionMapping(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Reflection Mapping"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_ReflectionMappingEnable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        split = layout.split()
        row = layout.row()
        col = split.column()
        if scene.thea_ReflectionMappingEnable:
          col.prop(scene,"thea_ReflectionMappingWrappingMenu")
          col.prop(scene,"thea_ReflectionMappingFilename", icon='TEXTURE_DATA')
          #col.operator("thea.reflectionmapping_file", text="Select file")
          col.prop(scene,"thea_ReflectionMappingRotation")
          col.prop(scene,"thea_ReflectionMappingIntensity")

class RENDER_PT_theaRefractionMapipng(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Refraction Mapping"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_RefractionMappingEnable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        split = layout.split()
        row = layout.row()
        col = split.column()
        if scene.thea_RefractionMappingEnable:
           col.prop(scene,"thea_RefractionMappingWrappingMenu")
           col.prop(scene,"thea_RefractionMappingFilename", icon='TEXTURE_DATA')
           #col.operator("thea.refractionmapping_file", text="Select file")
           col.prop(scene,"thea_RefractionMappingRotation")
           col.prop(scene,"thea_RefractionMappingIntensity")


class OBJECT_OT_ResetPhysicalSky(bpy.types.Operator):
    bl_idname = "reset.sky"
    bl_label = "Reset Sky"

    def execute(self, context):
        scene = context.scene
        scene.thea_EnvPSTurb = 2.5
        scene.thea_EnvPSOzone = 0.35
        scene.thea_EnvPSWatVap = 2.0
        scene.thea_EnvPSTurbCo = 0.046
        scene.thea_EnvPSWaveExp = 1.3
        scene.thea_EnvPSalbedo = 0.5
        return{'FINISHED'}

class RENDER_PT_theaPhysicalSky(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Physical Sky"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
       scene = context.scene
       self.layout.prop(scene, "thea_EnvPSEnable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        split = layout.split()
        col = split.column()
        if scene.thea_EnvPSEnable:
            col.prop(scene, "thea_SkyTypeMenu")
            col.prop(scene, "thea_EnvPSTurb")
            col.prop(scene, "thea_EnvPSOzone")
            col.prop(scene, "thea_EnvPSWatVap")
            col.prop(scene, "thea_EnvPSTurbCo")
            col.prop(scene, "thea_EnvPSWaveExp")
            col.prop(scene, "thea_EnvPSalbedo")
            col.operator("reset.sky", text="Reset Sky", icon='X')


class RENDER_PT_theaLocationTime(WorldButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Location/Time"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw_header(self, context):
        scene = context.scene
        self.layout.prop(scene, "thea_locationEnable", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        split = layout.split()
        row = layout.row()

#        box = layout.box()
#        box.label(getattr(scene, "thea_Envlocation"))
        layout.operator("thea.location_search", text="Search", icon="VIEWZOOM")

        split = layout.split(percentage=0.33)
        colL = split.column()
        colR = split.column()
#        box = colR.box()
#        colR = colR.box()
        colL.label("Location:")
        colR.label(getattr(scene, "thea_Envlocation"))
#        colR.operator("thea.location_search", text="Search", icon="VIEWZOOM")

#        colR.enabled = True
#        col.prop(scene,"thea_EnvLocationsMenu")
        #       colL = split.column()
        #       colL.label("")
        split = layout.split()
        col = split.column()
        col.prop(scene,"thea_EnvLat")
        col.prop(scene,"thea_EnvLong")
        col.prop(scene,"thea_EnvTZ")
        col.prop(scene,"thea_EnvDate")
        col.prop(scene,"thea_EnvTime")




class IMAGE_PT_thea_Display(DisplayButtonsPanel, bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Thea Display"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    thea_globals.displayPreset = False

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)


    def draw(self, context):
        scene = context.scene
        layout = self.layout
        split = layout.split()

        col = split.column()
        col.prop(scene,"thea_DisplayMenuEnable", text="Display Presets")
        if getattr(scene, "thea_DisplayMenuEnable"):
#            layout.label("Display presets:")
            col.prop(scene,"thea_DisplayMenu", text="")
            split = layout.split()
            row = layout.row()
            colL = split.column()
            colR = split.column()
            sub = colL
            sub.operator("unload.displaypreset", text="Revert")
            sub.active = thea_globals.displayPreset == True
            sub.enabled = thea_globals.displayPreset == True
            sub = colR
            colR.operator("load.displaypreset", text="Set")
#            sub.active = thea_globals.displayPreset == False
#            thea_globals.log.debug("DisplayReset: %s" % thea_globals.displayReset)
            if getattr(scene,"thea_DisplayMenu") == thea_globals.displaySet:
                sub.enabled = thea_globals.displayPreset == False


        layout.separator()
        split = layout.split(percentage=0.35)
        colL = split.column()
        colR = split.column()
        colL.label("Channel:")
        colR.prop(scene,"thea_viewChannel", text="")
        layout.separator()
#        sub = col.column()
#        sub.active = scene.thea_DisplayMenuEnable == False
#        split = layout.split()
        layout.prop(scene,"thea_DispISO")
        layout.prop(scene,"thea_DispShutter")
        layout.prop(scene,"thea_DispFNumber")
        layout.prop(scene,"thea_DispGamma")
        layout.prop(scene,"thea_DispBrightness")
#        layout.separator()
        layout.prop(scene,"thea_DispCRFMenu")
        split = layout.split()
        colL = split.column()
        colR = split.column()
#       CHANGED > added the new active/inactive menu's, new sharpness, bloom items and diaphgrama options
#       CHANGED > Redid order
        colL.prop(scene,"thea_DispSharpness")
#        if getattr(scene,"thea_DispSharpness"):
#            colR.prop(scene,"thea_DispSharpnessWeight")
        sub = colR.row()
        sub.active = scene.thea_DispSharpness == True
        sub.prop(scene, "thea_DispSharpnessWeight")
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispBurn")
#        if getattr(scene,"thea_DispBurn"):
#            colR.prop(scene,"thea_DispBurnWeight")
        sub = colR.row()
        sub.active = scene.thea_DispBurn == True
        sub.prop(scene,"thea_DispBurnWeight")
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispVignetting")
        sub = colR.row()
        sub.active = scene.thea_DispVignetting == True
        sub.prop(scene,"thea_DispVignettingWeight")

        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispChroma")
        sub = colR.row()
        sub.active = scene.thea_DispChroma == True
        sub.prop(scene,"thea_DispChromaWeight")

        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispContrast")
        sub = colR.row()
        sub.active = scene.thea_DispContrast == True
        sub.prop(scene,"thea_DispContrastWeight")

        split = layout.split()
        row = layout.row()
        colL = split.column()
        colR = split.column()
        colL.prop(scene,"thea_DispTemperature")
        sub = colR.row()
        sub.active = scene.thea_DispTemperature == True
        sub.prop(scene,"thea_DispTemperatureWeight")

        split = layout.split()
        row = layout.row()
        colL.prop(scene,"thea_DispBloom")
        sub = colR.row()
        sub.active = scene.thea_DispBloom == True
        sub.prop(scene,"thea_DispBloomItems")
#        split = layout.split()
        row = layout.row()
        if getattr(scene,"thea_DispBloom"):
            colR.prop(scene,"thea_DispBloomWeight")
            colR.prop(scene,"thea_DispGlareRadius")

        layout.label(text="Z-depth:")
        layout.prop(scene,"thea_DispMinZ")
        layout.prop(scene,"thea_DispMaxZ")

        layout.separator()
        col = layout.column()

#        col.prop(scene,"thea_analysis", text="Analysis:")
        split = layout.split()
        colL = split.column()
        colR = split.column()
        colL.label("Analysis:")
        colR.prop(scene,"thea_analysisMenu", text="")
#        thea_globals.log.debug(getattr(scene,"thea_analysisMenu"))
        sub = layout.column()
#        col.prop(scene,"thea_analysis", text="Analysis:")
        sub.prop(scene,"thea_minIlLum")
        sub.prop(scene,"thea_maxIlLum")
        sub.active = scene.thea_analysisMenu == '1'


        row = layout.row()
        layout.operator("thea.refresh_render")

class OBJECT_PT_thea_GetMaterials(bpy.types.Operator):
    bl_idname = "thea.get_materials"
    bl_label = "Get materials"

    def invoke(self, context, event):

       scene = context.scene
       sceneMaterials = []
       sceneMaterials.append(("0","None","0"))
       i = 1
       for mat in bpy.data.materials:
           sceneMaterials.append((str(i), mat.name, str(i)))
           i += 1

       propNameIf = ""
       try:
           del scene[propNameIf]
       except:
            pass

       Scene = bpy.types.Scene

       return {'FINISHED'}


# class OBJECT_PT_thea_SetInterface(bpy.types.Operator):
#     bl_idname = "thea.set_interface"
#     bl_label = "Set interface"
#
#     def invoke(self, context, event):
#
#        scene = context.scene
#        propNameIf = "thea_Interface"
#        matInt = bpy.data.materials[scene.get(propNameIf)-1].name
#        if scene['thea_Interface'] > 0:
#            ob = bpy.context.active_object
#            bpy.types.Object.thea_MatInterface = bpy.props.StringProperty()
#            ob.thea_MatInterface=matInt
#
#
#
#        return {'FINISHED'}

class OBJECT_PT_theaMaterialInterface(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Container"
    COMPAT_ENGINES = set(['THEA_RENDER'])
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
       layout = self.layout
       obj = context.active_object

       layout.prop(obj, "thea_Container")


class OBJECT_PT_theaTools(ObjectButtonsPanel, bpy.types.Panel):
    bl_label = "Thea object settings"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
       layout = self.layout
       scene = context.scene
       split = layout.split()
       row = layout.row()
       col = split.column()


       Scene = bpy.types.Scene
       col.prop(bpy.context.active_object, "thEnabled")
       col.prop(bpy.context.active_object, "thExportAnimation")
       col.prop(bpy.context.active_object, "thVisible")
       col.prop(bpy.context.active_object, "thShadowTight")
       col.prop(bpy.context.active_object, "thShadowCaster")
       col.prop(bpy.context.active_object, "thShadowReceiver")
       col.prop(bpy.context.active_object, "thCausticsTransmitter")
       col.prop(bpy.context.active_object, "thCausticsReceiver")
       col.prop(bpy.context.active_object, "thNoRecalcNormals")
       split = layout.split()
#       row = layout.row()
       colL = split.column()
       colR = split.column()
       active = colL
       active.prop(bpy.context.active_object, "thMaskID")
       sub = colR
       sub.active = bpy.data.objects[bpy.context.active_object.name].thMaskID == True
       sub.prop(bpy.context.active_object, "thMaskIDindex")
#       layout.separator()
       layout.prop(bpy.context.active_object, "thSectionFrame")

class OBJECT_OT_setCamProjection(bpy.types.Operator):
    bl_idname = "set.cam"
    bl_label = "set cam"

    def execute(self, context):
        cam = context.object
        camera = context.camera
        camShiftXNew = camera.shift_x
        camShiftYNew = camera.shift_y
#        thea_globals.log.debug("OBJ cam: %s" % cam.thea_projection)
        if cam.thea_projection == "Perspective":
            camera.type = 'PERSP'
            camera.shift_x = camShiftXNew
            camera.shift_y = camShiftYNew
        if cam.thea_projection == "Parallel":
            camera.type = 'ORTHO'
            camShiftXOld = camera.shift_x
            camShiftYOld = camera.shift_y
            camera.shift_x = 0
            camera.shift_y = 0
        return{'FINISHED'}

def checkCamera():
    bl_idname = "check_camera"
    bl_label = "Check camera name and data name"

    if not bpy.context.active_object.name == bpy.data.objects[bpy.context.active_object.name]:
        thea_globals.log.debug("No cam")
        bpy.data.objects[bpy.context.active_object.name].errorCam = "Change name"


class DATA_PT_theaCamera(CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Thea Camera"
    COMPAT_ENGINES = set(['THEA_RENDER'])
    errorCam = ""

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
#        checkCamera()
        return (engine in cls.COMPAT_ENGINES) and context.active_object.type=='CAMERA'

    def draw_header(self, context):
        scene = context.scene
        cam = context.active_object

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cam = context.object
        object = bpy.context.active_object
        camera = context.camera
        if (bpy.context.active_object.name != camera.name):
            layout.label(text="Camera Data & Object name must be same", icon="ERROR")
            layout.separator()
        else:
            layout.label(text="Film:")
            if bpy.data.objects[bpy.context.active_object.name].thea_projection == "Perspective":
               if camera.sensor_fit in {'VERTICAL'} :
                   layout.prop(bpy.data.cameras[bpy.context.active_object.name], "sensor_height", text="Film Height (mm)")
               if camera.sensor_fit in {'HORIZONTAL' and 'AUTO'} :
                   layout.prop(bpy.data.cameras[bpy.context.active_object.name], "sensor_width", text="Film Height (mm)")
               layout.prop(bpy.data.cameras[bpy.context.active_object.name], "lens", text="Focal Lenght (mm)")
               layout.operator("set.cam", text="Preview Perspective", icon='CAMERA_DATA')
            if bpy.data.objects[bpy.context.active_object.name].thea_projection == "Parallel":
               layout.prop(bpy.data.cameras[bpy.context.active_object.name], "ortho_scale", text="View Area")
               layout.operator("set.cam", text="Preview Parallel", icon='CAMERA_DATA')


            split = layout.split()
            layout.label(text="Lens:")
            layout.prop(bpy.context.active_object, "thea_projection")
            layout.prop(bpy.context.active_object, "shutter_speed")
            row = layout.row()

            split = layout.split()
            colL = split.column()
            colR = split.column()
            colL.label(text="Diaphragm:")
            colR.prop(bpy.context.active_object, "thea_diaphragma")
            if bpy.data.objects[bpy.context.active_object.name].thea_diaphragma == "Polygonal":
               colR.prop(bpy.context.active_object, "thea_diapBlades")

            row = layout.row()
            #       colL.label(text="")
            # ADD spcer to align Shift again when blades is ON
            if bpy.data.objects[bpy.context.active_object.name].thea_diaphragma == "Polygonal":
               colL.label(text="")
            colL.label(text="Shift:")
            colR.prop(camera, "shift_x", text="X")
            colR.prop(camera, "shift_y", text="Y")

            row = layout.row()
            layout.label(text="Depth of Field:")
            layout.prop(bpy.context.active_object, "autofocus")

            split = layout.split()

            colL = split.column()
            colR = split.column()
            sub = colL
            sub.enabled = bpy.data.objects[bpy.context.active_object.name].thea_enableDOFpercentage == False
            #       sub.enabled = bpy.data.objects[bpy.context.active_object.name].thea_pinhole == False
            sub.prop(bpy.context.active_object, "thea_pinhole")
            sub = colR.row()
            sub.enabled = bpy.data.objects[bpy.context.active_object.name].thea_enableDOFpercentage == False
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_pinhole == False
            #       sub.active = bpy.data.objects[bpy.context.active_object.name].thea_enableDOFpercentage == False
            sub.prop(bpy.context.active_object, "aperture")

            split = layout.split()

            colL = split.column()
            colR = split.column()
            sub = colL

            sub.label(text="Distance:")
            sub = colR
            sub.enabled = bpy.data.objects[bpy.context.active_object.name].thea_pinhole == False
            sub.prop(bpy.data.cameras[bpy.context.active_object.name], "dof_distance")
            split = layout.split()
            #       row = layout.row()
            colL = split.column()
            colR = split.column()
            sub = colL

            sub.enabled = bpy.data.objects[bpy.context.active_object.name].thea_pinhole == False
            sub.prop(bpy.context.active_object,"thea_enableDOFpercentage")
            #       if (bpy.data.objects[bpy.context.active_object.name].thea_enableDOFpercentage == True):
            #           bpy.data.objects[bpy.context.active_object.name].aperture = False
            sub = colR.row()
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_enableDOFpercentage == True
            sub.prop(bpy.context.active_object, "thea_DOFpercentage")
            split = layout.split()

            col = split.column(align=True)
            sub = col
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_ZclipDOF == False
            sub.prop(bpy.context.active_object, "thea_zClippingNear")
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_zClippingNear == True
            sub.prop(bpy.data.cameras[bpy.context.active_object.name], "clip_start")


            col = split.column(align=True)
            sub = col
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_ZclipDOF == False
            sub.prop(bpy.context.active_object, "thea_zClippingFar")
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_zClippingFar == True
            sub.prop(bpy.data.cameras[bpy.context.active_object.name], "clip_end")

            layout.prop(bpy.context.active_object, "thea_ZclipDOF")
            sub = layout.split()
            sub.active = bpy.data.objects[bpy.context.active_object.name].thea_ZclipDOF == True
            sub.prop(bpy.context.active_object,"thea_ZclipDOFmargin")


class PARTICLE_PT_Thea(ParticleButtonsPanel, bpy.types.Panel):
    bl_label = "Thea"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES) and (context.particle_system is not None)

    def draw(self, context):
       layout = self.layout
       scene = context.scene
       psys = context.particle_system
       part = psys.settings
       split = layout.split()
       row = layout.row()
       split = layout.split()
       row = layout.row()
       col = split.column()
       col.prop(part,"thea_ApplyModifier")


class DataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.lamp and (engine in cls.COMPAT_ENGINES)


class DATA_PT_thea_context_lamp(DataButtonsPanel, Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        ob = context.object
        lamp = context.lamp
        space = context.space_data

        split = layout.split(percentage=0.65)
        if(lamp is not None):
            texture_count = len(lamp.texture_slots.keys())

            if ob:
                split.template_ID(ob, "data")
            elif lamp:
                split.template_ID(space, "pin_id")

            if texture_count != 0:
                split.label(text=str(texture_count), icon='TEXTURE')



class DATA_PT_thea_lamp(DataButtonsPanel, Panel):
    bl_label = "Lamp"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
#        CHANGED > Added context.lamp so emttance wont show in other tabs
        return context.lamp and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp
        if(lamp is not None):

            #layout.operator('thea.refresh_lamp', "Refresh lamp data", icon="FILE_REFRESH")
            layout.prop(lamp, "type", expand=True)

            layout.prop(lamp, "thea_enableLamp")
            layout.prop(lamp, "thea_enableShadow")
#            CHANGED > Added manual sun
            if lamp.type == "SUN":
                layout.prop(lamp, "thea_manualSun")
            row = layout.row()
            row.prop(lamp, "thea_enableSoftShadow")
            if getattr(lamp, "thea_enableSoftShadow"):
                if lamp.type == "SUN":
#                CHANGED> Deleted softradius doesnt do anything for sune
                    layout.prop(lamp, "thea_radiusMultiplier", text="Radius Multiplier")

                else:
                    row.prop(lamp, "thea_softRadius")
            row = layout.row()
            layout.prop(lamp, "thea_minRays")
            layout.prop(lamp, "thea_maxRays")
            layout.prop(lamp, "thea_globalPhotons")
            layout.prop(lamp, "thea_causticPhotons")
            layout.prop(lamp, "thea_bufferIndex")



class DATA_PT_thea_Emittance(DataButtonsPanel, Panel):
    bl_label = "Emittance"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
#        CHANGED > Added context.lamp so emttance wont show in other tabs
        return context.lamp and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        checked = False
        layout = self.layout
        obj = context.object
        lamp = context.lamp
        row = layout.row()
        if(lamp is not None):
            if (lamp.thea_TextureFilename==""):
                row.prop(lamp, "color", text="")
            row.prop(lamp, "thea_TextureFilename", text="", icon='TEXTURE_DATA')

            split = layout.split()
            colL = split.column()
            colR = split.column()
            if lamp.type in {'SPOT'} :
                sub = colL
                sub.enabled = lamp.thea_enableProjector == False
                sub.prop(lamp, "thea_enableIES")
            if lamp.type in {'SPOT'} and lamp.thea_enableIES:
                colR.prop(lamp, "thea_IESFilename", text="", icon='LAMP_DATA')
                layout.prop(lamp, "thea_IESMultiplier")

            row = layout.row()
            split = layout.split()
            colL = split.column()
            colR = split.column()
            if lamp.type in {'SPOT'} :
                sub = row
                sub.enabled = lamp.thea_enableIES == False
                sub.prop(lamp, "thea_enableProjector")
#                obj.use_square = True
            if lamp.type in {'SPOT'} and lamp.thea_enableProjector:
                colL.prop(lamp, "thea_ProjectorWidth")
                colR.prop(lamp, "thea_ProjectorHeight")
                split = layout.split()


            split = layout.split()
            colL = split.column()
            colR = split.column()
            split = layout.split()
            if (lamp.thea_enableIES == False) and lamp.type != 'SUN':
                colL.prop(lamp, "thea_EmittancePower")
#                sub = row
#                sub.enabled = lamp.thea_enableIES == False
#                sub.prop(lamp, "thea_enableProjector")
                layout.prop(lamp, "thea_EmittanceEfficacy")
            if lamp.type == 'SUN':
                colL.prop(lamp, "thea_EmittancePower")
                colR.prop(lamp, "thea_SunEmittanceUnit")
                layout.prop(lamp, "thea_SunAttenuation")
            elif (lamp.thea_enableIES == False):
                colR.prop(lamp, "thea_EmittanceUnit")
#            CHANGED > Added Sun for attenuation
            if lamp.type in {'POINT', 'SPOT', 'AREA'} and lamp.thea_enableIES != True:
                layout.prop(lamp, "thea_EmittanceAttenuation")
                #sub.prop(lamp, "distance")

    #             if lamp.falloff_type == 'LINEAR_QUADRATIC_WEIGHTED':
    #                 col.label(text="Attenuation Factors:")
    #                 sub = col.column(align=True)
    #                 sub.prop(lamp, "linear_attenuation", slider=True, text="Linear")
    #                 sub.prop(lamp, "quadratic_attenuation", slider=True, text="Quadratic")

                #col.prop(lamp, "use_sphere")

#            if lamp.type == 'AREA':
#                setattr(lamp, "thea_EmittancePower", "100")
#                col.prop(lamp, "distance")
#                col.prop(lamp, "gamma")







class DATA_PT_thea_shadow(DataButtonsPanel, Panel):
    bl_label = "Shadow"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.scene.render.engine
        #return (lamp and lamp.type in {'POINT', 'SUN', 'SPOT', 'AREA'}) and (engine in cls.COMPAT_ENGINES)
        return False

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        layout.prop(lamp, "shadow_method", expand=True)

        if lamp.shadow_method == 'NOSHADOW' and lamp.type == 'AREA':
            split = layout.split()

            col = split.column()
            col.label(text="Form factor sampling:")

            sub = col.row(align=True)

            if lamp.shape == 'SQUARE':
                sub.prop(lamp, "shadow_ray_samples_x", text="Samples")
            elif lamp.shape == 'RECTANGLE':
                sub.prop(lamp, "shadow_ray_samples_x", text="Samples X")
                sub.prop(lamp, "shadow_ray_samples_y", text="Samples Y")

        if lamp.shadow_method != 'NOSHADOW':
            split = layout.split()

            col = split.column()
            col.prop(lamp, "shadow_color", text="")

            col = split.column()
            col.prop(lamp, "use_shadow_layer", text="This Layer Only")
            col.prop(lamp, "use_only_shadow")

        if lamp.shadow_method == 'RAY_SHADOW':
            split = layout.split()

            col = split.column()
            col.label(text="Sampling:")

            if lamp.type in {'POINT', 'SUN', 'SPOT'}:
                sub = col.row()

                sub.prop(lamp, "shadow_ray_samples", text="Samples")
                sub.prop(lamp, "shadow_soft_size", text="Soft Size")

            elif lamp.type == 'AREA':
                sub = col.row(align=True)

                if lamp.shape == 'SQUARE':
                    sub.prop(lamp, "shadow_ray_samples_x", text="Samples")
                elif lamp.shape == 'RECTANGLE':
                    sub.prop(lamp, "shadow_ray_samples_x", text="Samples X")
                    sub.prop(lamp, "shadow_ray_samples_y", text="Samples Y")

            col.row().prop(lamp, "shadow_ray_sample_method", expand=True)

            if lamp.shadow_ray_sample_method == 'ADAPTIVE_QMC':
                layout.prop(lamp, "shadow_adaptive_threshold", text="Threshold")

            if lamp.type == 'AREA' and lamp.shadow_ray_sample_method == 'CONSTANT_JITTERED':
                row = layout.row()
                row.prop(lamp, "use_umbra")
                row.prop(lamp, "use_dither")
                row.prop(lamp, "use_jitter")

        elif lamp.shadow_method == 'BUFFER_SHADOW':
            col = layout.column()
            col.label(text="Buffer Type:")
            col.row().prop(lamp, "shadow_buffer_type", expand=True)

            if lamp.shadow_buffer_type in {'REGULAR', 'HALFWAY', 'DEEP'}:
                split = layout.split()

                col = split.column()
                col.label(text="Filter Type:")
                col.prop(lamp, "shadow_filter_type", text="")
                sub = col.column(align=True)
                sub.prop(lamp, "shadow_buffer_soft", text="Soft")
                sub.prop(lamp, "shadow_buffer_bias", text="Bias")

                col = split.column()
                col.label(text="Sample Buffers:")
                col.prop(lamp, "shadow_sample_buffers", text="")
                sub = col.column(align=True)
                sub.prop(lamp, "shadow_buffer_size", text="Size")
                sub.prop(lamp, "shadow_buffer_samples", text="Samples")
                if lamp.shadow_buffer_type == 'DEEP':
                    col.prop(lamp, "compression_threshold")

            elif lamp.shadow_buffer_type == 'IRREGULAR':
                layout.prop(lamp, "shadow_buffer_bias", text="Bias")

            split = layout.split()

            col = split.column()
            col.prop(lamp, "use_auto_clip_start", text="Autoclip Start")
            sub = col.column()
            sub.active = not lamp.use_auto_clip_start
            sub.prop(lamp, "shadow_buffer_clip_start", text="Clip Start")

            col = split.column()
            col.prop(lamp, "use_auto_clip_end", text="Autoclip End")
            sub = col.column()
            sub.active = not lamp.use_auto_clip_end
            sub.prop(lamp, "shadow_buffer_clip_end", text=" Clip End")


class DATA_PT_thea_area(DataButtonsPanel, Panel):
    bl_label = "Area Shape"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.scene.render.engine
        return (lamp and lamp.type == 'AREA') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        col = layout.column()
        col.row().prop(lamp, "shape", expand=True)
        sub = col.row(align=True)

        if lamp.shape == 'SQUARE':
            sub.prop(lamp, "size")
        elif lamp.shape == 'RECTANGLE':
            sub.prop(lamp, "size", text="Size X")
            sub.prop(lamp, "size_y", text="Size Y")


class DATA_PT_thea_spot(DataButtonsPanel, Panel):
    bl_label = "Spot Shape"
    COMPAT_ENGINES = set(['THEA_RENDER'])

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.scene.render.engine
#        changed > Added check for IES / Projecktor enable if true hide this
        return (lamp and lamp.type == 'SPOT') and (getattr(lamp, "thea_enableProjector") == False) and (getattr(lamp, "thea_enableIES") == False) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        split = layout.split()
        col = split.column()
        sub = col.column()
        sub.prop(lamp, "spot_size", text="Size")
        sub.prop(lamp, "spot_blend", text="Blend", slider=True)
        col.prop(lamp, "use_square")
        col.prop(lamp, "show_cone")

        col = split.column()

        col.prop(lamp, "use_halo")
        sub = col.column(align=True)
        sub.active = lamp.use_halo
        sub.prop(lamp, "halo_intensity", text="Intensity")
        if lamp.shadow_method == 'BUFFER_SHADOW':
            sub.prop(lamp, "halo_step", text="Step")


