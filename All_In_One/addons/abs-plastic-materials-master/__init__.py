# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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

bl_info = {
    "name"        : "ABS Plastic Materials",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (2, 1, 1),
    "blender"     : (2, 80, 0),
    "description" : "Append ABS Plastic Materials to current blender file with a simple click",
    "location"    : "PROPERTIES > Materials > ABS Plastic Materials",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "https://www.blendermarket.com/products/abs-plastic-materials",
    "tracker_url" : "https://github.com/bblanimation/abs-plastic-materials/issues",
    "category": "Learnbgame",
   }
# NOTE: Comment out `abs.mark_outdated` ui button

# Blender imports
import bpy
from bpy.props import *
from bpy.types import Scene, Material
from bpy.utils import register_class, unregister_class
props = bpy.props

# Addon imports
from .ui.app_handlers import *
from .functions import *
from .lib import preferences, classesToRegister
from . import addon_updater_ops
from .lib.mat_properties import mat_properties

def register():
    for cls in classesToRegister.classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    bpy.props.abs_plastic_materials_module_name = __name__
    bpy.props.abs_plastic_version = str(bl_info["version"])[1:-1].replace(", ", ".")
    bpy.props.abs_mat_properties = mat_properties

    bpy.props.abs_mats_common = [
        "ABS Plastic Black",
        "ABS Plastic Blue",
        "ABS Plastic Brown",
        "ABS Plastic Dark Azur",
        "ABS Plastic Dark Blue",
        "ABS Plastic Dark Brown",
        "ABS Plastic Dark Green",
        "ABS Plastic Dark Grey",
        "ABS Plastic Dark Red",
        "ABS Plastic Dark Tan",
        "ABS Plastic Green",
        "ABS Plastic Light Grey",
        "ABS Plastic Lime",
        "ABS Plastic Orange",
        "ABS Plastic Purple",
        "ABS Plastic Red",
        "ABS Plastic Sand Blue",
        "ABS Plastic Sand Green",
        "ABS Plastic Tan",
        "ABS Plastic White",
        "ABS Plastic Yellow"]

    bpy.props.abs_mats_transparent = [
        "ABS Plastic Trans-Blue",
        "ABS Plastic Trans-Bright Orange",
        "ABS Plastic Trans-Brown",
        "ABS Plastic Trans-Clear",
        "ABS Plastic Trans-Green",
        "ABS Plastic Trans-Light Blue",
        "ABS Plastic Trans-Light Green",
        "ABS Plastic Trans-Orange",
        "ABS Plastic Trans-Red",
        "ABS Plastic Trans-Yellow",
        "ABS Plastic Trans-Yellowish Clear"]

    bpy.props.abs_mats_uncommon = [
        "ABS Plastic Bright Green",
        "ABS Plastic Bright Light Orange",
        "ABS Plastic Bright Pink",
        "ABS Plastic Cool Yellow",
        "ABS Plastic Dark Purple",
        "ABS Plastic Gold",
        "ABS Plastic Lavender",
        "ABS Plastic Light Blue",
        "ABS Plastic Light Flesh",
        "ABS Plastic Light Pink",
        "ABS Plastic Magenta",
        "ABS Plastic Medium Dark Flesh",
        "ABS Plastic Medium Lavender",
        "ABS Plastic Silver",
        "ABS Plastic Teal"]

    Scene.abs_subsurf = FloatProperty(
        name="Subsurface Scattering",
        description="Amount of subsurface scattering for ABS Plastic Materials (higher values up to 1 are more accurate, but increase render times)",
        subtype="FACTOR",
        min=0, soft_max=1,
        update=update_abs_subsurf,
        default=1)
    Scene.abs_roughness = FloatProperty(
        name="Roughness",
        description="Amount of roughness for the ABS Plastic Materials",
        subtype="FACTOR",
        min=0, max=1,
        precision=3,
        update=update_abs_roughness,
        default=0.005)
    Scene.abs_randomize = FloatProperty(
        name="Randomize",
        description="Amount of per-object randomness for ABS Plastic Material colors",
        subtype="FACTOR",
        min=0, soft_max=1,
        update=update_abs_randomize,
        default=0.02)
    Scene.abs_fingerprints = FloatProperty(
        name="Fingerprints",
        description="Amount of fingerprints and dust to add to the specular map of the ABS Plastic Materials (mesh must be unwrapped)",
        subtype="FACTOR",
        min=0, max=1,
        update=update_abs_fingerprints,
        default=0.25)
    Scene.abs_displace = FloatProperty(
        name="Displacement",
        description="Bumpiness of the ABS Plastic Materials (mesh must be unwrapped; 0.002 recommended)",
        subtype="FACTOR",
        min=0, soft_max=1,
        precision=3,
        update=update_abs_displace,
        default=0.0)
    Scene.uv_detail_quality = FloatProperty(
        name="UV Detail Quality",
        description="Quality of the fingerprints and dust detailing (save memory by reducing quality)",
        subtype="FACTOR",
        min=0, max=1,
        precision=1,
        update=update_image,
        default=1)
    Scene.abs_uv_scale = FloatProperty(
        name="UV Scale",
        description="Update the universal scale of the Fingerprints & Dust UV Texture",
        min=0,
        update=update_abs_uv_scale,
        default=1)
    Scene.save_datablocks = BoolProperty(
        name="Save Data-Blocks",
        description="Save ABS Plastic Materials even if they have no users",
        update=toggle_save_datablocks,
        default=True)
    Scene.abs_viewport_transparency = BoolProperty(
        name="Viewport Transparency",
        description="Display trans- materials as partially transparent in the 3D viewport",
        update=update_viewport_transparency,
        default=True)

    # Attribute for tracking version
    Material.abs_plastic_version = StringProperty(default="2.1.0")

    # register app handlers
    bpy.app.handlers.load_post.append(handle_upconversion)

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)


def unregister():
    Scn = bpy.types.Scene

    # addon updater unregister
    addon_updater_ops.unregister()

    # unregister app handlers
    bpy.app.handlers.load_post.remove(handle_upconversion)

    del Material.abs_plastic_version
    del Scene.abs_viewport_transparency
    del Scene.save_datablocks
    del Scene.uv_detail_quality
    del Scene.abs_displace
    del Scene.abs_fingerprints
    del Scene.abs_randomize
    del Scene.abs_roughness
    del Scene.abs_subsurf
    del bpy.props.abs_mats_uncommon
    del bpy.props.abs_mats_transparent
    del bpy.props.abs_mats_common
    del bpy.props.abs_mat_properties
    del bpy.props.abs_plastic_version
    del bpy.props.abs_plastic_materials_module_name

    for cls in reversed(classesToRegister.classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
