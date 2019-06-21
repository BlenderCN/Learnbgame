# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  version 2 as published by the Free Software Foundation.
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

import bpy
import pterocolmat

bl_info = {
    "name"       : "Vietcong BES",
    "author"     : "Jan Havran",
    "version"    : (0, 1),
    "blender"    : (2, 79, 0),
    "location"   : "Properties > Material",
    "description": "Vietcong BES Material Tools",
    "wiki_url"   : "https://github.com/OpenVietcong/blender-plugin-vietcong",
    "tracker_url": "https://github.com/OpenVietcong/blender-plugin-vietcong/issues",
    "category": "Learnbgame",
}

def update_material_view(context):
    material = context.active_object.active_material
    if "bes_props" in material and "type" in material["bes_props"] and \
            material["bes_props"]["type"] == "pteromat" and \
            "transparency" in material["bes_props"] and \
            material["bes_props"]["transparency"] != "none":
        material.use_transparency = True
        material.alpha = 0.0
    else:
        material.use_transparency = False
        material.alpha = 1.0

def update_material_type(self, context):
    material = context.active_object.active_material
    if "bes_props" not in material:
        material["bes_props"] = dict()

    material["bes_props"]["type"] = self.material_type
    update_material_view(context)

def update_transparency_type(self, context):
    material = context.active_object.active_material
    if "bes_props" not in material:
        material["bes_props"] = dict()
    material["bes_props"]["transparency"] = self.pteromat_transparency
    update_material_view(context)

class BESMaterialProperties(bpy.types.PropertyGroup):
    material_type = bpy.props.EnumProperty(
        name = "Material",
        description = "BES material type",
        items = [
            ("standard", "Standard", "Standard 3DS Max texturing material"),
            ("pteromat", "PteroMat", "Ptero-Engine II Material"),
        ],
        update=update_material_type
    )

    pteromat_collision = bpy.props.EnumProperty(
        name = "Collision Material",
        description = "PteroMat collision material",
        items = [("none", "- NONE -", "")] +
                ([(collision, collision, "") for collision in pterocolmat.ptero_colls]),
    )

    pteromat_transparency = bpy.props.EnumProperty(
        name = "Type of transparent",
        description = "PteroMat transparency type",
        items = [
            ("none", "- none - (opaque)", ""),
            ("#0",   "#0 - transparent, zbufwrite, sort", ""),
            ("#1",   "#1 - transparent, zbufwrite, sort, 1-bit alpha", ""),
            ("#2",   "#2 - translucent, no_zbufwrite, sort", ""),
            ("#3",   "#3 - transparent, zbufwrite, nosort, 1-bit alpha", ""),
            ("#4",   "#4 - translucent, add with background, no_zbufwrite, sort", ""),
        ],
        update=update_transparency_type
    )

class BESMaterialPanel(bpy.types.Panel):
    bl_idname = "material.bes"
    bl_label = "BES Materials"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object and bpy.context.active_object.active_material

    def draw(self, context):
        material = context.active_object.active_material

        layout = self.layout
        layout.prop(material.bes_mat_panel, "material_type")

        if "bes_props" in material and "type" in material["bes_props"] and \
            material["bes_props"]["type"] == "pteromat":
            self.draw_pteromat(material, layout)
        else:
            self.draw_standard(material, layout)

    def draw_standard(self, material, layout):
        layout.label("Ambient Color",     icon="IMAGE_DATA")
        layout.label("Diffuse Color",     icon="IMAGE_DATA")
        layout.label("Specular Color",    icon="IMAGE_DATA")
        layout.label("Specular Level",    icon="IMAGE_DATA")
        layout.label("Glossiness",        icon="IMAGE_DATA")
        layout.label("Self-Illumination", icon="IMAGE_DATA")
        layout.label("Opacity",           icon="IMAGE_DATA")
        layout.label("Filter Color",      icon="IMAGE_DATA")
        layout.label("Bump",              icon="IMAGE_DATA")
        layout.label("Reflection",        icon="IMAGE_DATA")
        layout.label("Refraction",        icon="IMAGE_DATA")
        layout.label("Displacement",      icon="IMAGE_DATA")

    def draw_pteromat(self, material, layout):
        layout.prop(material.bes_mat_panel, "pteromat_collision")
        layout.prop(material.bes_mat_panel, "pteromat_transparency")

        layout.label("Diffuse #1 - Ground",       icon="IMAGE_DATA")
        layout.label("Diffuse #2 - Multitexture", icon="IMAGE_DATA")
        layout.label("Diffuse #3 - Overlay",      icon="IMAGE_DATA")
        layout.label("LightMap",                  icon="IMAGE_DATA")
        layout.label("Environment",               icon="IMAGE_DATA")

def register():
    bpy.utils.register_class(BESMaterialPanel)
    bpy.utils.register_class(BESMaterialProperties)
    bpy.types.Material.bes_mat_panel = bpy.props.PointerProperty(type=BESMaterialProperties)

def unregister():
    del bpy.types.Material.bes_mat_panel
    bpy.utils.unregister_class(BESMaterialProperties)
    bpy.utils.unregister_class(BESMaterialPanel)

if __name__ == "__main__":
    register()

