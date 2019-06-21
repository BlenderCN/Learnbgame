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


class SkinPaintPart(RWMaterial):
    material_name = "SkinPaint Part"
    material_description = "A part for the Cell, Creature, Outfit and Flora editors."
    material_has_material_color = BoolProperty(default=True)
    material_has_ambient_color = BoolProperty(default=False)
    material_use_alpha = BoolProperty(default=False)

    diffuse_texture = StringProperty(
        name="Diffuse Texture",
        description="The diffuse texture of this material (leave empty if no texture desired)",
        default="",
        subtype='FILE_PATH'
    )

    @staticmethod
    def set_pointer_property(cls):
        cls.material_data_SkinPaintPart = PointerProperty(
            type=SkinPaintPart
        )

    @staticmethod
    def get_material_data(rw4_material):
        return rw4_material.material_data_SkinPaintPart

    @staticmethod
    def draw_panel(layout, rw4_material):

        data = rw4_material.material_data_SkinPaintPart

        row = layout.row()
        row.prop(data, 'diffuse_texture')

    @staticmethod
    def get_material_builder(exporter, rw4_material):
        renderWare = exporter.renderWare

        material = RWMaterialBuilder()

        RWMaterial.set_general_settings(material, rw4_material, rw4_material.material_data_SkinPaintPart)

        material.shader_ID = 0x80000004
        material.unknown_booleans.append(True)  # the rest are going to be False

        # -- RENDER STATES -- #

        material.set_render_states(rw4_material.alpha_type)

        # -- SHADER CONSTANTS -- #

        material.shader_constants.append(ShaderConstant(
            index=ShaderConstants['skinWeights'],
            offset=0,
            data=struct.pack('<i', 4)  # in the shader, skinWeights.x = numWeights
        ))
        material.shader_constants.append(ShaderConstant(
            index=ShaderConstants['skinBones'],
            offset=0,
            data=struct.pack('<iiiii',
                             0,  # firstBone
                             exporter.get_bone_count(),  # numBones
                             0,
                             renderWare.getIndex(None, sectionType=RW4Base.INDEX_NO_OBJECT),  # ?
                             exporter.get_skin_matrix_buffer_index()
                             )
        ))
        material.shader_constants.append(ShaderConstant(
            index=0x216,  # used for selecting skinPaint shader
            offset=0,
            data=struct.pack('<i', 0)
        ))

        # -- TEXTURE SLOTS -- #

        material.texture_slots.append(RWTextureSlot(
            sampler_index=0,
            texture_raster=exporter.add_texture(rw4_material.material_data_SkinPaintPart.diffuse_texture),
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

        if material.shader_ID != 0x80000004:
            return False

        shConst = material.get_shader_constant(0x216)
        if shConst is None or shConst.data is None or len(shConst.data) != 4:
            return False

        RWMaterial.parse_material_builder(material, rw4_material)

        return True