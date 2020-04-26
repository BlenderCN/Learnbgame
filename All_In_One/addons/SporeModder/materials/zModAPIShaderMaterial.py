__author__ = 'Eric'

from .RWMaterial import RWMaterial
from .RWMaterialBuilder import RWMaterialBuilder, ShaderConstants, ShaderConstant, RWTextureSlot
from . import DirectXEnums
from .. import RW4Base
import struct

import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty
                       )


class ModAPIShaderMaterial(RWMaterial):
    material_name = "Custom Shader Material"
    material_description = "A base material for using custom shaders."
    material_has_material_color = BoolProperty(default=True)
    material_has_ambient_color = BoolProperty(default=False)

    diffuse_texture = StringProperty(
        name="Diffuse Texture",
        description="The diffuse texture of this material (leave empty if no texture desired)",
        default="",
        subtype='FILE_PATH'
    )

    shader_name = StringProperty(
        name="Shader Name",
        description="The name or hex code of the shader to be used.",
        default="",
    )

    @staticmethod
    def set_pointer_property(cls):
        cls.material_data_ModAPIShaderMaterial = PointerProperty(
            type=ModAPIShaderMaterial
        )

    @staticmethod
    def get_material_data(rw4_material):
        return rw4_material.material_data_ModAPIShaderMaterial

    @staticmethod
    def draw_panel(layout, rw4_material):

        data = rw4_material.material_data_ModAPIShaderMaterial

        row = layout.row()
        row.prop(data, 'shader_name')

        row = layout.row()
        row.prop(data, 'diffuse_texture')

    @staticmethod
    def get_material_builder(exporter, rw4_material):

        material_data = rw4_material.material_data_ModAPIShaderMaterial

        material = RWMaterialBuilder()

        RWMaterial.set_general_settings(material, rw4_material, material_data)

        material.shader_ID = RW4Base.getHash(material_data.shader_name)
        material.unknown_booleans.append(True)
        material.unknown_booleans.append(True)  # the rest are going to be False

        # -- RENDER STATES -- #

        material.set_render_states('ALPHA')

        # -- SHADER CONSTANTS -- #
        # Add here any shader constants related with your shaders
        # For example:

        # material.shader_constants.append(ShaderConstant(
        #     index=ShaderConstants['materialParams'],
        #     offset=0,
        #     data=struct.pack('<f', material_data.specularExponent)
        # ))

        # -- TEXTURE SLOTS -- #

        material.texture_slots.append(RWTextureSlot(
            sampler_index=0,
            texture_raster=exporter.add_texture(material_data.diffuse_texture),
            unknown_has_stage_states=0x3f,
            unknown_has_sampler_states=0x73,
        ))

        material.texture_slots.append(RWTextureSlot(
            sampler_index=1,
            texture_raster=None,
            unknown_has_stage_states=9,
            unknown_has_sampler_states=0,
        ))

        return material

    @staticmethod
    def parse_material_builder(material, rw4_material):

        material_data.shader_name = "0x%X" % material.shader_ID

        material_data = rw4_material.material_data_ModAPIShaderMaterial

        RWMaterial.parse_material_builder(material, rw4_material)

        return True
