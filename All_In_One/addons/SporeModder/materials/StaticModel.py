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


class StaticModel(RWMaterial):
    material_name = "Static Model"
    material_description = "A simple model which allows normal maps, used for props, backgrounds, etc."
    material_has_material_color = BoolProperty(default=True)
    material_has_ambient_color = BoolProperty(default=False)
    material_use_alpha = BoolProperty(default=True)

    diffuse_texture = StringProperty(
        name="Diffuse Texture",
        description="The diffuse texture of this material (leave empty if no texture desired)",
        default="",
        subtype='FILE_PATH'
    )

    normal_texture = StringProperty(
        name="Normal Texture",
        description="The normal texture of this material (leave empty if no texture desired)",
        default="",
        subtype='FILE_PATH'
    )

    material_params_1 = FloatProperty(
        name="Specular Exponent",
        default=10
    )
    material_params_2 = FloatProperty(
        name="Inverse Bumpiness",
		description="This value is multiplied with the 'z' coordinate of the normal map",
        default=1
    )
    material_params_3 = FloatProperty(
        name="Material Params[3]",
        default=1
    )
    material_params_4 = FloatProperty(
        name="Gloss",
        default=0
    )

    @staticmethod
    def set_pointer_property(cls):
        cls.material_data_StaticModel = PointerProperty(
            type=StaticModel
        )

    @staticmethod
    def get_material_data(rw4_material):
        return rw4_material.material_data_StaticModel

    @staticmethod
    def draw_panel(layout, rw4_material):

        data = rw4_material.material_data_StaticModel

        row = layout.row()
        row.prop(data, 'diffuse_texture')

        row = layout.row()
        row.prop(data, 'normal_texture')

        row = layout.row()
        row.prop(data, 'material_params_1')

        row = layout.row()
        row.prop(data, 'material_params_2')

        row = layout.row()
        row.prop(data, 'material_params_3')

        row = layout.row()
        row.prop(data, 'material_params_4')

    @staticmethod
    def get_material_builder(exporter, rw4_material):
        renderWare = exporter.renderWare

        material_data = rw4_material.material_data_StaticModel

        material = RWMaterialBuilder()

        RWMaterial.set_general_settings(material, rw4_material, material_data)

        material.shader_ID = 0x80000002
        material.unknown_booleans.append(True)
        material.unknown_booleans.append(True)  # the rest are going to be False

        # -- SHADER CONSTANTS -- #

        material.shader_constants.append(ShaderConstant(
            index=ShaderConstants['materialParams'],
            offset=0,
            data=struct.pack('<iffff',
                             0x26445C02,
                             material_data.material_params_1,
                             material_data.material_params_2,
                             material_data.material_params_3,
                             material_data.material_params_4
                             )
        ))

        material.shader_constants.append(ShaderConstant(
            index=0x218,  # used for selecting static model shader
            offset=0,
            data=struct.pack('<i', 0x028B7C00)  # probably an address and we shouldn't care
        ))

        # -- TEXTURE SLOTS -- #

        material.texture_slots.append(RWTextureSlot(
            sampler_index=0,
            texture_raster=exporter.add_texture(material_data.diffuse_texture),
            unknown_has_stage_states=0x3f,
            unknown_has_sampler_states=0x73,
        ))

        material.texture_slots.append(RWTextureSlot(
            sampler_index=1,
            texture_raster=exporter.add_texture(material_data.normal_texture),
            unknown_has_stage_states=9,
            unknown_has_sampler_states=0x73,
        ))

        return material

    @staticmethod
    def parse_material_builder(material, rw4_material):

        if material.shader_ID != 0x80000002:
            return False

        shConst = material.get_shader_constant(0x218)
        if shConst is None or shConst.data is None or len(shConst.data) != 4:
            return False

        material_data = rw4_material.material_data_StaticModel

        RWMaterial.parse_material_builder(material, rw4_material)

        shConst = material.get_shader_constant(ShaderConstants['materialParams'])
        if shConst is not None and len(shConst.data) == struct.calcsize('<iffff'):
            values = struct.unpack('<iffff', shConst.data)
            material_data.material_params_1 = values[1]
            material_data.material_params_2 = values[2]
            material_data.material_params_3 = values[3]
            material_data.material_params_4 = values[4]

        return True
