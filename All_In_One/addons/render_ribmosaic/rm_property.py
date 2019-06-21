# #############################################################################
# AUTHOR BLOCK:
# #############################################################################
#
# RIB Mosaic RenderMan(R) IDE, see <http://sourceforge.net/projects/ribmosaic>
# by Eric Nathen Back aka WHiTeRaBBiT, 01-24-2010
# This script is protected by the GPL: Gnu Public License
# GPL - http://www.gnu.org/copyleft/gpl.html
#
# #############################################################################
# GPL LICENSE BLOCK:
# #############################################################################
#
# Script Copyright (C) Eric Nathen Back
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################
# COPYRIGHT BLOCK:
# #############################################################################
#
# The RenderMan(R) Interface Procedures and Protocol are:
# Copyright 1988, 1989, 2000, 2005 Pixar
# All Rights Reserved
# RenderMan(R) is a registered trademark of Pixar
#
# #############################################################################
# COMMENT BLOCK:
# #############################################################################
#
# Property module providing declaration, creation and
# destruction of properties.
#
# This script is PEP 8 compliant
#
# Search TODO for incomplete code
# Search FIXME for improper code
# Search XXX for broken code
#
# #############################################################################
# END BLOCKS
# #############################################################################

import os
import bpy


# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
exec("import " + MODULE + " as rm")

# Enumerators
pass_types = [('BEAUTY', "Beauty", ""),
            ('BAKE', "Bake", ""),
            ('ENVIRONMENT', "Environment", ""),
            ('INDIRECT', "Indirect", ""),
            ('PHOTON', "Photon", ""),
            ('OCCLUSION', "Occlusion", ""),
            ('DEPTH', "Depth", "")]
pass_perspectives = [('CAMERA', "Camera", ""),
            ('PERSP', "Perspective", ""),
            ('ORTH', "Orthographic", ""),
            ('CUBEOBJ', "Cube Object", ""),
            ('CUBEWLD', "Cube World", ""),
            ('LATLONG', "LatLong Object", ""),
            ('LATLONG', "LatLong World", ""),
            ('PLANAR', "Planar", "")]
pass_panel_logic = [('ENABLE', "Enable",
             "Enable all panels in group"),
            ('DISABLE', "Disable",
             "Disable all panels in group"),
            ('EXCLUSIVE', "Exclusive",
             "Enable all panels in group, disable all others"),
            ('TOGGLE', "Toggle",
             "Like Exclusive but toggles enable/disable states in group")]

pass_filters = [('box', "Box", ""),
            ('triangle', "Triangle", ""),
            ('catmull-rom', "Catmull-Rom", ""),
            ('sinc', "Sinc", ""),
            ('gaussian', "Gaussian", ""),
            ('CUSTOM', "Custom",""),
            ('NONE', "None", "")]

gc = 'DEFAULT'
gd = "Scene Default"
archives_material = [('INLINE', "Inline Code", ""),
            ('READARCHIVE', "Read Archive", ""),
            ('UNREADARCHIVE', "Unread Archive", ""),
            ('NOEXPORT', "Disable Export", ""),
            (gc, gd, "")]
archives_object = [('INLINE', "Inline Code", ""),
            ('READARCHIVE', "Read Archive", ""),
            ('DELAYEDARCHIVE', "Delayed Read Archive", ""),
            ('UNREADARCHIVE', "Unread Archive", ""),
            ('NOEXPORT', "Disable Export", ""),
            (gc, gd, "")]
archives_data = [('INLINE', "Inline Code", ""),
            ('INSTANCE', "Object Instance", ""),
            ('READARCHIVE', "Read Archive", ""),
            ('UNREADARCHIVE', "Unread Archive", ""),
            ('NOEXPORT', "Disable Export", ""),
            (gc, gd, "")]
archives_inline = [('INLINE', "Inline Code", ""),
            ('NOEXPORT', "Disable Export", "")]

primvar_desc = "Specify what RenderMan primitive type to export or use" \
               "auto select"
primvar_class = [('vertex', "Vertex", ""),
            ('varying', "Varying", ""),
            ('facevertex', "FaceVertex", ""),
            ('facevarying', "FaceVarying", "")]

csg_desc = " for this object and its children"
csg_ops = [('NOCSG', "No CSG", "Disable Constructive Solid Modelling"),
            ('INTERSECTION', "Intersection", "Use intersect CSG" + csg_desc),
            ('UNION', "Union", "Use union CSG" + csg_desc),
            ('DIFFERENCE', "Difference", "Use difference CSG" + csg_desc)]

# Property lists
exporter_props = [
            ("World", "world", archives_object, 'DEFAULT'),
            ("Object", "object", archives_object, 'DEFAULT'),
            ("Mesh", "mesh", archives_data, 'DEFAULT'),
            ("Curve", "curve", archives_data, 'DEFAULT'),
            ("MetaBall", "metaball", archives_data, 'DEFAULT'),
            ("Lamp", "lamp", archives_inline, 'INLINE'),
            ("Camera", "camera", archives_inline, 'INLINE'),
            ("Material", "material", archives_material, 'DEFAULT'),
            ("ParticleSettings", "particle", archives_data, 'DEFAULT')]

manager_props = ["WindowManager",
             "Scene",
             "World",
             "Object",
             "Mesh",
             "Curve",
             "SurfaceCurve",
             "MetaBall",
             "Lamp",
             "Camera",
             "Material",
             "Texture",
             "ParticleSettings"]

geometry_props = ["Mesh",
             "Curve",
             "MetaBall",
             "ParticleSettings"]


# #############################################################################
# ENGINE SETUP
# #############################################################################

# Setup which Blender panels will be visible
from bl_ui import properties_render
properties_render.RENDER_PT_render.COMPAT_ENGINES.add(rm.ENGINE)
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add(rm.ENGINE)
properties_render.RENDER_PT_layers.COMPAT_ENGINES.add(rm.ENGINE)
properties_render.RENDER_PT_output.COMPAT_ENGINES.add(rm.ENGINE)
properties_render.RENDER_PT_post_processing.COMPAT_ENGINES.add(rm.ENGINE)
properties_render.RENDER_PT_stamp.COMPAT_ENGINES.add(rm.ENGINE)
del properties_render

from bl_ui import properties_world
properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add(rm.ENGINE)
properties_world.WORLD_PT_custom_props.COMPAT_ENGINES.add(rm.ENGINE)
del properties_world

from bl_ui import properties_material
properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add(rm.ENGINE)
properties_material.MATERIAL_PT_custom_props.COMPAT_ENGINES.add(rm.ENGINE)
del properties_material

from bl_ui import properties_texture
properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.add(rm.ENGINE)
properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add(rm.ENGINE)
del properties_texture

from bl_ui import properties_data_lamp
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add(rm.ENGINE)
properties_data_lamp.DATA_PT_custom_props_lamp.COMPAT_ENGINES.add(rm.ENGINE)
del properties_data_lamp

# Use all panels in the following Blender module list
modules = ["properties_data_armature",
           "properties_data_bone",
           "properties_data_camera",
           "properties_data_curve",
           "properties_data_empty",
           "properties_data_lattice",
           "properties_data_mesh",
           "properties_data_metaball",
           "properties_data_modifier",
           "properties_object",
           "properties_particle",
           "properties_scene"]

for module in modules:
    exec("from bl_ui import " + module + " as m")

    for member in dir(m):
        subclass = getattr(m, member)
        try:
            subclass.COMPAT_ENGINES.add(rm.ENGINE)
        except:
            pass
    del m


# #############################################################################
# GROUP AND COLLECTION CLASSES
# #############################################################################

# #### Global classes

class RibmosaicFiles(bpy.types.PropertyGroup):
    """Group for name property collection of multiple file selections"""

    pass


class RibmosaicCollectionProps(bpy.types.PropertyGroup):
    """Generic collection properties"""

    # ### Public attributes

    name = bpy.props.StringProperty(name="Name",
                description="Name of item",
                maxlen=256,
                default="")

    pipeline = bpy.props.StringProperty(name="pipeline",
                description="Text datablock name of pipeline",
                maxlen=256,
                default="")

    xmlpath = bpy.props.StringProperty(name="xmlpath",
                description="Path to items XML data",
                maxlen=256,
                default="")


class RibmosaicCollectionGroup(bpy.types.PropertyGroup):
    """Generic collection group"""

    # ### Public attributes

    collection = bpy.props.CollectionProperty(type=RibmosaicCollectionProps,
                name="Collection of items",
                description="")

    active_index = bpy.props.IntProperty(name="Active Index",
                description="Index of the active item",
                default=-1,
                min=-1,
                max=65535)

    window = bpy.props.StringProperty(name="Window",
                description="The window space this collection represents",
                maxlen=256,
                default="")

    revision = bpy.props.IntProperty(name="Revision",
                description="Pipeline revision last collected",
                default=0,
                min=0,
                max=65535)


# #### Render space classes

class RibmosaicPassProps(bpy.types.PropertyGroup):
    """Render passes properties"""

    # ### Public attributes

    name = bpy.props.StringProperty(name="Pass Name",
                description="Name of render pass",
                maxlen=256,
                default="Beauty Pass")

    pass_enabled = bpy.props.BoolProperty(name="Pass Enable",
                description="Enable or disable this render pass",
                default=True)

    pass_type = bpy.props.EnumProperty(name="Render Pass Type",
                description="Specify what type of pass this is",
                items=pass_types,
                default='BEAUTY')

    # Pass output properties
    pass_display_file = bpy.props.StringProperty(name="Display File",
                description="Output path/file.ext used by displays for render",
                maxlen=512,
                default="Renders/P@[EVAL:.current_pass:####]@"
                        "_F@[EVAL:.current_frame:####]@.tif")

    pass_multilayer = bpy.props.BoolProperty(name="MultiLayer Output",
                description="This passes display output is a MultiLayer EXR",
                default=False)

    pass_shadingrate = bpy.props.FloatProperty(name="Shading Rate",
                description="Pass shading rate, 0 disables",
                precision=3,
                default=0.0,
                min=0.0,
                max=1024.0,
                soft_min=0.0,
                soft_max=1024.0)

    pass_eyesplits = bpy.props.IntProperty(name="Eye Splits",
                description="Eye-plane failure threshold, 0 disables",
                default=0,
                min=0,
                max=1024,
                soft_min=0,
                soft_max=1024)

    pass_bucketsize_width = bpy.props.IntProperty(name="Bucket Width",
                description="Render Bucket width size in pixels",
                default=16,
                min=1,
                max=1024,
                soft_min=0,
                soft_max=1024)

    pass_bucketsize_height = bpy.props.IntProperty(name="Bucket Height",
                description="Render Bucket height size in pixels",
                default=16,
                min=1,
                max=1024,
                soft_min=0,
                soft_max=1024)

    pass_gridsize = bpy.props.IntProperty(name="Grid Size",
                description="Number of micro-polygons shaded, 0 disables",
                default=0,
                min=0,
                max=10000,
                soft_min=0,
                soft_max=9000)

    pass_texturemem = bpy.props.IntProperty(name="Texture Mem",
                description="Maximum texture space in memory in kb,"
                            "0 disables",
                default=0,
                min=0,
                soft_min=0,
                soft_max=262144)

    # Pass camera properties
    pass_camera = bpy.props.StringProperty(name="",
                description="Override active camera, null uses scene's camera",
                maxlen=256,
                default="")

    pass_camera_group = bpy.props.BoolProperty(name="",
                description="Use group for multiple perspectives per pass",
                default=False)

    pass_camera_persp = bpy.props.EnumProperty(name="Camera Perspective",
                description="Specify perspective type used for active camera",
                items=pass_perspectives,
                default='CAMERA')

    pass_camera_lensadj = bpy.props.FloatProperty(name="Lens Adjust",
                description="Adjust camera's lens size +/-",
                precision=3,
                default=0.0,
                min=-1024.0,
                max=1024.0,
                soft_min=-1024.0,
                soft_max=1024.0)

    pass_camera_nearclip = bpy.props.FloatProperty(name="Near Clip",
                description="Force near clipping plane, 0 disables",
                precision=3,
                default=0.0,
                min=0,
                soft_min=0.0,
                soft_max=65535.0)

    pass_camera_farclip = bpy.props.FloatProperty(name="Far Clip",
                description="Force far clipping plane, 0 disables",
                precision=3,
                default=0.0,
                min=0,
                soft_min=0.0,
                soft_max=65535.0)

    # Pass samples properties
    pass_samples_x = bpy.props.IntProperty(name="X",
                description="Samples horizontally, 0 disables",
                default=0,
                min=0,
                max=1024,
                soft_min=0,
                soft_max=1024)

    pass_samples_y = bpy.props.IntProperty(name="Y",
                description="Samples vertically, 0 disables",
                default=0,
                min=0,
                max=1024,
                soft_min=0,
                soft_max=1024)

    # Pass filter properties
    pass_filter = bpy.props.EnumProperty(name="Pixel Filter",
                description="Pixel filter (box, sinc, triangle,"
                            "gaussian, ect)",
                items=pass_filters,
                default='NONE')
    pass_customfilter = bpy.props.StringProperty(name="Custom Pixel Filter",
                description="custom Pixel filter name",
                maxlen=256,
                default="")

    pass_width_x = bpy.props.IntProperty(name="X",
                description="Filter width horizontally",
                default=1,
                min=1,
                max=1024,
                soft_min=1,
                soft_max=1024)

    pass_width_y = bpy.props.IntProperty(name="Y",
                description="Filter width vertically",
                default=1,
                min=1,
                max=1024,
                soft_min=1,
                soft_max=1024)

    # Pass control properties
    pass_subpasses = bpy.props.IntProperty(name="Sub Passes",
                description="Add additional passes per camera, 0 disables",
                default=0,
                min=0,
                max=512,
                soft_min=0,
                soft_max=512)

    pass_passid = bpy.props.IntProperty(name="Pass ID",
                description="Use to uniquely identify passes from"
                            "panel scripts",
                default=0,
                min=0,
                soft_min=0,
                soft_max=65535)

    # Pass tile passes properties
    pass_tile_x = bpy.props.IntProperty(name="Tiles X",
                description="Number of horizontal tiles, 0 disables",
                default=0,
                min=0,
                max=512,
                soft_min=0,
                soft_max=512)

    pass_tile_y = bpy.props.IntProperty(name="Tiles Y",
                description="Number of vertical tiles, 0 disables",
                default=0,
                min=0,
                max=512,
                soft_min=0,
                soft_max=512)

    pass_tile_index = bpy.props.IntProperty(name="Tile Index",
                description="Index of tile this pass belongs to",
                default=0,
                min=0,
                max=262144,
                soft_min=0,
                soft_max=262144)

    # Pass sequence passes properties
    pass_seq_width = bpy.props.IntProperty(name="Sequence Width",
                description="Number of frames in each sequence pass,"
                            "0 disables",
                default=0,
                min=0,
                max=300000,
                soft_min=0,
                soft_max=300000)

    pass_seq_index = bpy.props.IntProperty(name="Sequence Index",
                description="Index of animation sequence this pass belongs to",
                default=0,
                min=0,
                max=300000,
                soft_min=0,
                soft_max=300000)

    # Pass frame range properties
    pass_range_start = bpy.props.IntProperty(name="Start",
                description="First frame of rendering range, 0 uses scene's",
                default=0,
                min=0,
                max=300000,
                soft_min=0,
                soft_max=300000)

    pass_range_end = bpy.props.IntProperty(name="End",
                description="Last frame of rendering range, 0 uses scene's",
                default=0,
                min=0,
                max=300000,
                soft_min=0,
                soft_max=300000)

    pass_range_step = bpy.props.IntProperty(name="Step",
                description="Number of frames to skip range, 0 uses scene's",
                default=0,
                min=0,
                max=32767,
                soft_min=0,
                soft_max=100)

    # Pass resolution properties
    pass_res_x = bpy.props.IntProperty(name="X",
                description="Horizontal pixel resolution, 0 uses scene's",
                default=0,
                min=0,
                soft_min=0,
                soft_max=65535)

    pass_res_y = bpy.props.IntProperty(name="Y",
                description="Vertical pixel resolution, 0 uses scene's",
                default=0,
                min=0,
                soft_min=0,
                soft_max=65535)

    # Pass aspect ratio properties
    pass_aspect_x = bpy.props.FloatProperty(name="X",
                description="Horizontal aspect ratio, 0 uses scene's",
                precision=3,
                default=0.0,
                min=0.0,
                max=200.0,
                soft_min=0.0,
                soft_max=200.0)

    pass_aspect_y = bpy.props.FloatProperty(name="Y",
                description="Vertical aspect ratio, 0 uses scene's",
                precision=3,
                default=0.0,
                min=0.0,
                max=200.0,
                soft_min=0.0,
                soft_max=200.0)

    # Pass scene filters properties
    pass_layerfilter = bpy.props.StringProperty(name="Render Layer",
                description="Specify a render layer to filter this passes"
                            " objects and assign render output to Blender's"
                            " render result",
                maxlen=32,
                default="")

    pass_panelfilter = bpy.props.StringProperty(name="Panel Filter",
                description="Specify a Python expression to filter all"
                            " pipeline panels in this pass (0/False=disable,"
                            " 1/True=enable)",
                maxlen=512,
                default="")

    pass_rib_string = bpy.props.StringProperty(name="RIB String",
                description="Custom RIB code to be passed to utility panels",
                maxlen=2048,
                default="")


class RibmosaicPassGroup(bpy.types.PropertyGroup):
    """Render passes group"""

    # ### Public attributes

    collection = bpy.props.CollectionProperty(
                type=RibmosaicPassProps,
                name="List of passes",
                description="")

    active_index = bpy.props.IntProperty(
                name="Index of the active pass",
                description="",
                default=0,
                min=0,
                max=65535)


# #############################################################################
# PROPERTY CONSTRUCTION
# #############################################################################

def create_props():
    """Create all addon properties (to be used from __init__.register())"""

    # #### Insure group classes are registered properly
    # FIXME This should not be neccessary!!

    try:
        bpy.types.register(RibmosaicFiles)

        try:
            bpy.types.unregister(
                rm.rm_operator.WM_OT_ribmosaic_library_addpanel)
            bpy.types.register(
                rm.rm_operator.WM_OT_ribmosaic_library_addpanel)
        except:
            pass

        try:
            bpy.types.unregister(rm.rm_operator.WM_OT_ribmosaic_pipeline_load)
            bpy.types.register(rm.rm_operator.WM_OT_ribmosaic_pipeline_load)
        except:
            pass
    except:
        pass

    try:
        bpy.utils.register_class(RibmosaicCollectionProps)
    except:
        pass

    try:
        bpy.utils.register_class(RibmosaicCollectionGroup)
    except:
        pass

    try:
        bpy.utils.register_class(RibmosaicPassProps)
    except:
        pass

    try:
        bpy.utils.register_class(RibmosaicPassGroup)
    except:
        pass

    # #### Global properties

    for p in exporter_props:
        data = "bpy.types." + p[0]

        exec(data + ".ribmosaic_mblur = bpy.props.BoolProperty("
             "name=\"Motion Blur\","
             "description=\"Enable " + p[1] + " motion blur\","
             "default=False)")

        exec(data + ".ribmosaic_mblur_steps = bpy.props.IntProperty("
             "name=\"Steps\","
             "description=\"Number of steps between start and end subframes\","
             "default=2,"
             "min=2,"
             "max=512,"
             "soft_min=2,"
             "soft_max=512)")

        exec(data + ".ribmosaic_mblur_start = bpy.props.FloatProperty("
             "name=\"Start\","
             "description=\"Subframe where blur begins (as offset of frame)\","
             "default=-0.5,"
             "min=-128.0,"
             "max=128.0,"
             "soft_min=-128.0,"
             "soft_max=128.0)")

        exec(data + ".ribmosaic_mblur_end = bpy.props.FloatProperty("
             "name=\"End\","
             "description=\"Subframe where blur ends (as offset of frame)\","
             "default=0.5,"
             "min=-128.0,"
             "max=128.0,"
             "soft_min=-128.0,"
             "soft_max=128.0)")

        exec(data + ".ribmosaic_rib_archive = bpy.props.EnumProperty("
             "name=\"RIB Archive\","
             "description=\"Specify archive and linking method for " + p[1] +
             " RIBs\","
             "items=p[2],"
             "default=p[3])")

    for p in manager_props:
        data = "bpy.types." + p

        exec(data + ".ribmosaic_active_script = bpy.props.StringProperty("
             "name=\"Scripts\","
             "description=\"Search python scripts in selected pipeline\","
             "default=\"\","
             "maxlen=512)")

        exec(data + ".ribmosaic_active_source = bpy.props.StringProperty("
             "name=\"Sources\","
             "description=\"Search shader sources in selected pipeline\","
             "default=\"\","
             "maxlen=512)")

        exec(data + ".ribmosaic_active_shader = bpy.props.StringProperty("
             "name=\"Shaders\","
             "description=\"Search shader panels in selected pipeline\","
             "default=\"\","
             "maxlen=512)")

        exec(data + ".ribmosaic_active_utility = bpy.props.StringProperty("
             "name=\"Utilities\","
             "description=\"Search utility panels in selected pipeline\","
             "default=\"\","
             "maxlen=512)")

        exec(data + ".ribmosaic_active_command = bpy.props.StringProperty("
             "name=\"Commands\","
             "description=\"Search command panels in selected pipeline\","
             "default=\"\","
             "maxlen=512)")

    for p in geometry_props:
        data = "bpy.types." + p
        seq = [("range", p + "'s range of visibility from last level to next",
                25.0),
               ("trans", "Transitional distance between this and next level",
                5.0)]

        exec(data + ".ribmosaic_lod = bpy.props.IntProperty("
             "name=\"Levels of Detail\","
             "description=\"Use LOD by defining what data-blocks show at what"
             " ranges\","
             "default=0,"
             "min=0,"
             "max=8,"
             "soft_min=0,"
             "soft_max=8)")

        for l in range(1, 9):
            exec(data + ".ribmosaic_lod_data_l" + str(l) +
                 " = bpy.props.StringProperty("
                 "name=\"Mesh ID\","
                 "description=\"Data-block for LOD level " + str(l) +
                 ", blank disables\","
                 "maxlen=256,"
                 "default=\"\")")

            for s in seq:
                exec(data + ".ribmosaic_lod_" + s[0] + "_l" + str(l) +
                     " = bpy.props.FloatProperty("
                     "name=s[0][0].capitalize(),"
                     "description=s[1],"
                     "precision=3,"
                     "default=s[2],"
                     "min=0.0,"
                     "soft_min=0.0,"
                     "soft_max=65535.0)")

    # #### Window manager properties

    bpy.types.WindowManager.ribmosaic_pipeline_search = \
        bpy.props.StringProperty(
                name="Pipeline Search",
                description="Specify XML pipeline path to element to select",
                default="",
                maxlen=512)

    bpy.types.WindowManager.ribmosaic_pipelines = bpy.props.PointerProperty(
                type=RibmosaicCollectionGroup,
                name="Pipeline Collection",
                description="")

    bpy.types.WindowManager.ribmosaic_scripts = bpy.props.PointerProperty(
                type=RibmosaicCollectionGroup,
                name="Scripts Collection",
                description="")

    bpy.types.WindowManager.ribmosaic_sources = bpy.props.PointerProperty(
                type=RibmosaicCollectionGroup,
                name="Sources Collection",
                description="")

    bpy.types.WindowManager.ribmosaic_shaders = bpy.props.PointerProperty(
                type=RibmosaicCollectionGroup,
                name="Shader Panel Collection",
                description="")

    bpy.types.WindowManager.ribmosaic_utilities = bpy.props.PointerProperty(
                type=RibmosaicCollectionGroup,
                name="Utility Panel Collection",
                description="")

    bpy.types.WindowManager.ribmosaic_commands = bpy.props.PointerProperty(
                type=RibmosaicCollectionGroup,
                name="Command Panel Collection",
                description="")

    bpy.types.WindowManager.ribmosaic_preview_samples = bpy.props.IntProperty(
                name="Samples",
                description="Preview samples quality",
                default=2,
                min=1,
                max=1024,
                soft_min=1,
                soft_max=1024)

    bpy.types.WindowManager.ribmosaic_preview_shading = \
        bpy.props.FloatProperty(
                name="Shading",
                description="Preview shading rate quality",
                precision=3,
                default=2.0,
                min=0.001,
                max=1024.0,
                soft_min=0.001,
                soft_max=1024.0)

    bpy.types.WindowManager.ribmosaic_preview_compile = \
        bpy.props.BoolProperty(
                name="Compile Shaders",
                description="Compile shaders for preview render",
                default=True)

    bpy.types.WindowManager.ribmosaic_preview_optimize = \
        bpy.props.BoolProperty(
                name="Optimize Textures",
                description="Optimize textures for preview render",
                default=True)

    # #### Render space properties

    bpy.types.Scene.ribmosaic_interactive = bpy.props.BoolProperty(
                name="Realtime Interactive Export",
                description="Exports and renders active render pass as"
                            " scene changes (renderer must support"
                            " progressive rendering)",
                default=False)

    bpy.types.Scene.ribmosaic_activepass = bpy.props.BoolProperty(
                name="Active Pass",
                description="Only export and render selected render pass",
                default=False)

    bpy.types.Scene.ribmosaic_activeobj = bpy.props.BoolProperty(
                name="Active Object",
                description="Only export selected object"
                            " (and any data in object)",
                default=False)

    bpy.types.Scene.ribmosaic_purgerib = bpy.props.BoolProperty(
                name="Purge RIB",
                description="Purge RIB passes"
                            " (existing RIB reused if disabled)",
                default=True)

    bpy.types.Scene.ribmosaic_exportrib = bpy.props.BoolProperty(
                name="Export RIB",
                description="Export RIB passes"
                            " (existing RIB reused if disabled)",
                default=True)

    bpy.types.Scene.ribmosaic_renderrib = bpy.props.BoolProperty(
                name="Render RIB",
                description="Render RIB passes (disable to only update RIB)",
                default=True)

    bpy.types.Scene.ribmosaic_purgeshd = bpy.props.BoolProperty(
                name="Purge Shaders",
                description="Purge shaders"
                            " (existing shaders reused if disabled)",
                default=True)

    bpy.types.Scene.ribmosaic_compileshd = bpy.props.BoolProperty(
                name="Compile Shaders",
                description="Compile shaders"
                            " (existing shaders reused if disabled)",
                default=True)

    bpy.types.Scene.ribmosaic_purgetex = bpy.props.BoolProperty(
                name="Purge Textures",
                description="Purge textures"
                            " (existing textures reused if disabled)",
                default=True)

    bpy.types.Scene.ribmosaic_optimizetex = bpy.props.BoolProperty(
                name="Optimize Textures",
                description="Optimize textures"
                            " (existing textures reused if disabled)",
                default=True)

    # #### Scene space properties

    bpy.types.Scene.ribmosaic_passes = bpy.props.PointerProperty(
                type=RibmosaicPassGroup,
                name="Render Pass Settings",
                description="")

    bpy.types.Scene.ribmosaic_export_threads = bpy.props.IntProperty(
                name="Export Threads",
                description="How many threads to use for RIB object export",
                default=4,
                min=0,
                max=1024,
                soft_min=0,
                soft_max=1024)

    bpy.types.Scene.ribmosaic_compressrib = bpy.props.BoolProperty(
                name="Compress All RIB",
                description="Compress RIB export"
                            " (gzip archives with .rib extensions)",
                default=False)

    bpy.types.Scene.ribmosaic_use_frame = bpy.props.BoolProperty(
                name="Export RiFrameBegin",
                description="Export RiFrameBegin/End blocks"
                            " (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_world = bpy.props.BoolProperty(
                name="Export RiWorldBegin",
                description="Export RiWorldBegin/End blocks"
                            " (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_screenwindow = bpy.props.BoolProperty(
                name="Export RiScreenWindow",
                description="Export RiScreenWindow (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_projection = bpy.props.BoolProperty(
                name="Export RiProjection",
                description="Export RiProjection (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_clipping = bpy.props.BoolProperty(
                name="Export RiClipping",
                description="Export RiClipping (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_sides = bpy.props.BoolProperty(
                name="Export RiSides",
                description="Export RiSides (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_bound = bpy.props.BoolProperty(
                name="Export RiBound",
                description="Export RiBound (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_use_attribute = bpy.props.BoolProperty(
                name="Export RiAttribute",
                description="Export RiAttribute (compatibility switch)",
                default=True)

    bpy.types.Scene.ribmosaic_export_path = bpy.props.StringProperty(
                name="Export Path",
                description="Path for export and execution"
                            " (created if not present)",
                default="//@[EVAL:.addon_name:]@_"
                        "@[EVAL:.blend_name+os.sep:]@"
                        "@[EVAL:.data_name:]@",
                maxlen=512)

    bpy.types.Scene.ribmosaic_archive_searchpath = bpy.props.StringProperty(
                name="Archive Paths",
                description="Shader search path RIB option, null disables",
                default="",
                maxlen=512)

    bpy.types.Scene.ribmosaic_shader_searchpath = bpy.props.StringProperty(
                name="Shader Paths",
                description="Archive search path RIB option, null disables",
                default="",
                maxlen=512)

    bpy.types.Scene.ribmosaic_texture_searchpath = bpy.props.StringProperty(
                name="Texture Paths",
                description="Texture search path RIB option, null disables",
                default="",
                maxlen=512)

    bpy.types.Scene.ribmosaic_display_searchpath = bpy.props.StringProperty(
                name="Display Paths",
                description="Display search path RIB option, null disables",
                default="",
                maxlen=512)

    bpy.types.Scene.ribmosaic_procedural_searchpath = bpy.props.StringProperty(
                name="Procedural Paths",
                description="Procedural search path RIB option, null disables",
                default="",
                maxlen=512)

    bpy.types.Scene.ribmosaic_resource_searchpath = bpy.props.StringProperty(
                name="Resource Paths",
                description="Resource search path RIB option, null disables",
                default="",
                maxlen=512)

    bpy.types.Scene.ribmosaic_object_archives = bpy.props.EnumProperty(
            name="Object Archives",
            description="Specify archive and linking method for all"
                        " object RIBs",
            items=archives_object[:-3],
            default='DELAYEDARCHIVE')

    bpy.types.Scene.ribmosaic_data_archives = bpy.props.EnumProperty(
            name="Data Archives",
            description="Specify archive and linking method for all data RIBs",
            items=archives_data[:-3],
            default='INSTANCE')

    bpy.types.Scene.ribmosaic_material_archives = bpy.props.EnumProperty(
            name="Material Archives",
            description="Specify archive and linking method for all"
                        " material RIBs",
            items=archives_material[:-3],
            default='READARCHIVE')

    # #### Object space properties

    bpy.types.Object.ribmosaic_csg = bpy.props.EnumProperty(
                name="CSG Operation",
                description="Specify CSG operation" + csg_desc,
                items=csg_ops,
                default='NOCSG')

    # #### Object data space properties

    # Mesh properties

    bpy.types.Mesh.ribmosaic_n_class = bpy.props.EnumProperty(
                name="N Class",
                description="Specify what N primitive variable"
                            " class to export",
                items=primvar_class,
                default='facevarying')

    bpy.types.Mesh.ribmosaic_cs_class = bpy.props.EnumProperty(
                name="Cs Class",
                description="Specify what Cs primitive variable"
                            " class to export",
                items=primvar_class,
                default='facevarying')

    bpy.types.Mesh.ribmosaic_st_class = bpy.props.EnumProperty(
                name="st Class",
                description="Specify what st primitive variable class"
                            " to export",
                items=primvar_class,
                default='facevarying')

    bpy.types.Mesh.ribmosaic_primitive = bpy.props.EnumProperty(
                name="Primitive Type",
                description=primvar_desc,
                items=[('POINTSPOLYGONS', "PointsPolygons", ""),
                       ('SUBDIVISIONMESH', "SubdivisionMesh", ""),
                       ('CURVES', "Curves", ""),
                       ('POINTS', "Points", ""),
                       ('AUTOSELECT', "Auto Select", "")],
                default='AUTOSELECT')

    bpy.types.Mesh.ribmosaic_n_export = bpy.props.BoolProperty(
                name="Export Normals as N",
                description="Export normals as N primitive variables",
                default=True)

    bpy.types.Mesh.ribmosaic_cs_export = bpy.props.BoolProperty(
                name="Export VertCol as Cs",
                description="Export active vertex color as Cs primitive"
                            " variables",
                default=True)

    bpy.types.Mesh.ribmosaic_st_export = bpy.props.BoolProperty(
                name="Export UV as st",
                description="Export active UV as st primitive variables",
                default=True)

    # Surface curve properties

    bpy.types.SurfaceCurve.ribmosaic_primitive = bpy.props.EnumProperty(
                name="Primitive Type",
                description=primvar_desc,
                items=[('NUPATCH', "NUPatch", ""),
                       ('POINTS', "Points", ""),
                       ('AUTOSELECT', "Auto Select", "")],
                default='AUTOSELECT')

    # Curve properties

    bpy.types.Curve.ribmosaic_primitive = bpy.props.EnumProperty(
                name="Primitive Type",
                description=primvar_desc,
                items=[('CURVES', "Curves", ""),
                       ('POINTS', "Points", ""),
                       ('AUTOSELECT', "Auto Select", "")],
                default='AUTOSELECT')

    # Metaball properties

    bpy.types.MetaBall.ribmosaic_primitive = bpy.props.EnumProperty(
                name="Primitive Type",
                description=primvar_desc,
                items=[('BLOBBY', "Blobby", ""),
                       ('POINTS', "Points", ""),
                       ('AUTOSELECT', "Auto Select", "")],
                default='AUTOSELECT')

    # Camera properties

    bpy.types.Camera.ribmosaic_dof = bpy.props.BoolProperty(
                name="Depth of Field",
                description="Export depth of field",
                default=False)

    bpy.types.Camera.ribmosaic_f_stop = bpy.props.FloatProperty(
                name="fstop",
                description="Depth of field fstop setting",
                precision=2,
                default=22.0,
                min=0.0,
                max=1024.0,
                soft_min=0.0,
                soft_max=1024.0)

    bpy.types.Camera.ribmosaic_focal_length = bpy.props.FloatProperty(
                name="focal",
                description="Depth of field focal length setting",
                precision=2,
                default=45.0,
                min=0.0,
                max=1024.0,
                soft_min=0.0,
                soft_max=1024.0)

    bpy.types.Camera.ribmosaic_shutter_min = bpy.props.FloatProperty(
                name="Min",
                description="Fraction of time within the blur shutter opens",
                precision=3,
                default=0.0,
                min=-10.0,
                max=10.0,
                soft_min=-10.0,
                soft_max=10.0)

    bpy.types.Camera.ribmosaic_shutter_max = bpy.props.FloatProperty(
                name="Max",
                description="Fraction of time within the blur shutter closes",
                precision=3,
                default=1.0,
                min=-10.0,
                max=10.0,
                soft_min=-10.0,
                soft_max=10.0)

    bpy.types.Camera.ribmosaic_relative_detail = bpy.props.FloatProperty(
                name="Adjust Relative LOD",
                description="Scale the calculated LOD for all objects"
                            " in scene",
                precision=3,
                default=1.0,
                min=0.0,
                soft_min=0.0,
                soft_max=65535.0)

    # #### Material space properties

    bpy.types.Material.ribmosaic_ri_color = bpy.props.BoolProperty(
                name="Export RiColor",
                description="Export material color as RiColor",
                default=True)

    bpy.types.Material.ribmosaic_ri_opacity = bpy.props.BoolProperty(
                name="Export RiOpacity",
                description="Export material alpha as RiOpacity",
                default=True)

    bpy.types.Material.ribmosaic_disp_pad = bpy.props.FloatProperty(
                name="Displace Bound",
                description="Adjust bounding box for displacements,"
                            " 0 disables",
                precision=3,
                default=0.0,
                min=0.0,
                max=64.0,
                soft_min=0.0,
                soft_max=64.0)

    bpy.types.Material.ribmosaic_wire_size = bpy.props.FloatProperty(
                name="Wire Size",
                description="Size of linear curves when using wire option",
                precision=3,
                default=0.01,
                min=0.0,
                max=100.0,
                soft_min=0.0,
                soft_max=100.0)

    bpy.types.Material.ribmosaic_disp_coor = bpy.props.EnumProperty(
                name="Coordinate System",
                description="Coordinate system the displacement bound is"
                            " measured in",
                items=[('WORLD', "World", ""),
                       ('OBJECT', "Object", ""),
                       ('CAMERA', "Camera", ""),
                       ('SCREEN', "Screen", ""),
                       ('RASTER', "Raster", ""),
                       ('SHADER', "Shader", "")],
                default='SHADER')

    # #### Particle space properties

    bpy.types.ParticleSettings.ribmosaic_primitive = bpy.props.EnumProperty(
                name="Primitive Type",
                description=primvar_desc,
                items=[('CURVES', "Curves", ""),
                       ('POINTS', "Points", ""),
                       ('AUTOSELECT', "Auto Select", "")],
                default='AUTOSELECT')


# #############################################################################
# PROPERTY DESTRUCTION
# #############################################################################

def destroy_props():
    """Destroy all addon properties (to be used from __init__.unregister())"""

    # #### Global properties

    for p in exporter_props:
        data = "del bpy.types." + p[0]

        exec(data + ".ribmosaic_mblur")
        exec(data + ".ribmosaic_mblur_steps")
        exec(data + ".ribmosaic_mblur_start")
        exec(data + ".ribmosaic_mblur_end")
        exec(data + ".ribmosaic_rib_archive")

    for p in manager_props:
        data = "del bpy.types." + p

        exec(data + ".ribmosaic_active_script")
        exec(data + ".ribmosaic_active_source")
        exec(data + ".ribmosaic_active_shader")
        exec(data + ".ribmosaic_active_utility")
        exec(data + ".ribmosaic_active_command")

    for p in geometry_props:
        data = "del bpy.types." + p
        seq = ["range", "trans"]

        exec(data + ".ribmosaic_lod")

        for l in range(1, 9):
            exec(data + ".ribmosaic_lod_data_l" + str(l))

            for s in seq:
                exec(data + ".ribmosaic_lod_" + s + "_l" + str(l))

    # #### Window manager properties

    del bpy.types.WindowManager.ribmosaic_pipelines
    del bpy.types.WindowManager.ribmosaic_scripts
    del bpy.types.WindowManager.ribmosaic_sources
    del bpy.types.WindowManager.ribmosaic_shaders
    del bpy.types.WindowManager.ribmosaic_utilities
    del bpy.types.WindowManager.ribmosaic_commands
    del bpy.types.WindowManager.ribmosaic_preview_samples
    del bpy.types.WindowManager.ribmosaic_preview_shading
    del bpy.types.WindowManager.ribmosaic_preview_compile
    del bpy.types.WindowManager.ribmosaic_preview_optimize

    # #### Render space properties

    del bpy.types.Scene.ribmosaic_interactive
    del bpy.types.Scene.ribmosaic_activepass
    del bpy.types.Scene.ribmosaic_purgerib
    del bpy.types.Scene.ribmosaic_renderrib
    del bpy.types.Scene.ribmosaic_purgeshd
    del bpy.types.Scene.ribmosaic_compileshd
    del bpy.types.Scene.ribmosaic_purgetex
    del bpy.types.Scene.ribmosaic_optimizetex

    # #### Scene space properties

    del bpy.types.Scene.ribmosaic_passes
    del bpy.types.Scene.ribmosaic_export_threads
    del bpy.types.Scene.ribmosaic_compressrib
    del bpy.types.Scene.ribmosaic_use_frame
    del bpy.types.Scene.ribmosaic_use_world
    del bpy.types.Scene.ribmosaic_use_screenwindow
    del bpy.types.Scene.ribmosaic_use_projection
    del bpy.types.Scene.ribmosaic_use_clipping
    del bpy.types.Scene.ribmosaic_use_sides
    del bpy.types.Scene.ribmosaic_use_bound
    del bpy.types.Scene.ribmosaic_use_attribute
    del bpy.types.Scene.ribmosaic_export_path
    del bpy.types.Scene.ribmosaic_archive_searchpath
    del bpy.types.Scene.ribmosaic_shader_searchpath
    del bpy.types.Scene.ribmosaic_texture_searchpath
    del bpy.types.Scene.ribmosaic_display_searchpath
    del bpy.types.Scene.ribmosaic_procedural_searchpath
    del bpy.types.Scene.ribmosaic_resource_searchpath
    del bpy.types.Scene.ribmosaic_object_archives
    del bpy.types.Scene.ribmosaic_data_archives
    del bpy.types.Scene.ribmosaic_material_archives

    # #### Object space properties

    del bpy.types.Object.ribmosaic_csg

    # #### Object data space properties

    # Mesh properties

    del bpy.types.Mesh.ribmosaic_n_class
    del bpy.types.Mesh.ribmosaic_cs_class
    del bpy.types.Mesh.ribmosaic_st_class
    del bpy.types.Mesh.ribmosaic_primitive
    del bpy.types.Mesh.ribmosaic_n_export
    del bpy.types.Mesh.ribmosaic_cs_export
    del bpy.types.Mesh.ribmosaic_st_export

    # Surface curve properties

    del bpy.types.SurfaceCurve.ribmosaic_primitive

    # Curve properties

    del bpy.types.Curve.ribmosaic_primitive

    # Metaball properties

    del bpy.types.MetaBall.ribmosaic_primitive

    # Camera properties

    del bpy.types.Camera.ribmosaic_dof
    del bpy.types.Camera.ribmosaic_f_stop
    del bpy.types.Camera.ribmosaic_focal_length
    del bpy.types.Camera.ribmosaic_shutter_min
    del bpy.types.Camera.ribmosaic_shutter_max
    del bpy.types.Camera.ribmosaic_relative_detail

    # #### Material space properties

    del bpy.types.Material.ribmosaic_ri_color
    del bpy.types.Material.ribmosaic_ri_opacity
    del bpy.types.Material.ribmosaic_disp_pad
    del bpy.types.Material.ribmosaic_wire_size
    del bpy.types.Material.ribmosaic_disp_coor

    # #### Particle space properties

    del bpy.types.ParticleSettings.ribmosaic_primitive
