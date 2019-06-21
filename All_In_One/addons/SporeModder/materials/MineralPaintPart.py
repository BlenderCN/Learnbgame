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


class MineralPaintPart(RWMaterial):
    material_name = "MineralPaint Part"
    material_description = "A part for the Vehicle, Building, UFO and Cake editors."
    material_has_material_color = BoolProperty(default=True)
    material_has_ambient_color = BoolProperty(default=False)
    material_use_alpha = BoolProperty(default=False)

    diffuse_texture = StringProperty(
        name="Diffuse Texture",
        description="The diffuse texture of this material (leave empty if no texture desired)",
        default="",
        subtype='FILE_PATH'
    )

    paint_region = IntProperty(
        name="Paint Region",
        default=1
    )

    use_paint_texture = BoolProperty(
        name="Use Paint Texture",
        description="Uncheck if this material doesn't use textures (everything will be painted with a matte color).",
        default=True
    )

    # uv_projection = IntProperty(
    #     name="UV Projection"
    # )

    uv_projection = EnumProperty(
        name="UV Projection",
        items=(
            ('0', "Project XY", ""),  # 0
            ('1', "Project XZ", ""),  # 1
            ('2', "Project YZ", ""),  # 2
            ('3', "BoxMap", ""),  # 3
            ('4', "Cylindrical Z", ""),  # 4
            ('5', "Disc", ""),  # 5
            ('6', "Cylindrical X", ""),  # 6
            ('7', "Cylindrical Y", ""),  # 7
        )
    )

    uv_scale = FloatVectorProperty(
        name="UV Scale",
        default=(1.0, 1.0),
        step=0.1,
        size=2
    )
    uv_offset = FloatVectorProperty(
        name="UV Offset",
        default=(0.0, 0.0),
        step=0.1,
        size=2
    )

    @staticmethod
    def set_pointer_property(cls):
        cls.material_data_MineralPaintPart = PointerProperty(
            type=MineralPaintPart
        )

    @staticmethod
    def get_material_data(rw4_material):
        return rw4_material.material_data_MineralPaintPart

    @staticmethod
    def draw_panel(layout, rw4_material):

        data = rw4_material.material_data_MineralPaintPart

        layout.row().prop(data, 'diffuse_texture')
        layout.row().prop(data, 'paint_region')
        layout.row().prop(data, 'use_paint_texture')

        if data.use_paint_texture:
            layout.row().prop(data, 'uv_projection')

            layout.row().prop(data, 'uv_scale')
            layout.row().prop(data, 'uv_offset')

    @staticmethod
    def get_material_builder(exporter, rw4_material):
        renderWare = exporter.renderWare
        material_data = rw4_material.material_data_MineralPaintPart

        material = RWMaterialBuilder()

        RWMaterial.set_general_settings(material, rw4_material, material_data)

        material.shader_ID = 0x80000004
        material.unknown_booleans.append(True)  # the rest are going to be False

        # -- RENDER STATES -- #

        material.set_render_states(rw4_material.alpha_type)

        # -- SHADER CONSTANTS -- #

        skinMatrixBuffers = renderWare.getObjects(RW4Base.SkinMatrixBuffer.type_code)

        if len(skinMatrixBuffers) > 0:
            skinMatrixIndex = renderWare.getIndex(
                skinMatrixBuffers[0],
                sectionType=RW4Base.INDEX_SUB_REFERENCE)

        else:
            skinMatrixIndex = renderWare.getIndex(None, sectionType=RW4Base.INDEX_NO_OBJECT)

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
                             skinMatrixIndex
                             )
        ))

        material.shader_constants.append(ShaderConstant(
            index=0x20F,
            offset=0,
            data=struct.pack('<ii', material_data.paint_region, 0x00C7E300)
        ))

        if material_data.use_paint_texture:
            material.shader_constants.append(ShaderConstant(
                index=ShaderConstants['uvTweak'],
                offset=0,
                data=struct.pack('<iffff',
                                 int(material_data.uv_projection),
                                 material_data.uv_scale[0],
                                 material_data.uv_scale[1],
                                 material_data.uv_offset[0],
                                 material_data.uv_offset[1],
                                 )
            ))
        else:
            material.shader_constants.append(ShaderConstant(
                index=0x244,
                offset=0,
                data=struct.pack('<i', 0)
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
            texture_raster=None,
            unknown_has_stage_states=9,
            unknown_has_sampler_states=0,
        ))

        return material

    @staticmethod
    def parse_material_builder(material, rw4_material):

        if material.shader_ID != 0x80000004:
            return False

        shConst = material.get_shader_constant(0x20F)
        if shConst is None or shConst.data is None or len(shConst.data) != 8:
            return False

        material_data = rw4_material.material_data_MineralPaintPart

        material_data.paint_region = struct.unpack('<ii', shConst.data)[0]

        RWMaterial.parse_material_builder(material, rw4_material)

        shConst = material.get_shader_constant(0x211)
        if shConst is not None and len(shConst.data) == struct.calcsize('<iffff'):
            material_data.use_paint_texture = True

            values = struct.unpack('<iffff', shConst.data)
            material_data.uv_projection = str(values[0])
            material_data.uv_scale[0] = values[1]
            material_data.uv_scale[1] = values[2]
            material_data.uv_offset[0] = values[3]
            material_data.uv_offset[1] = values[4]
        else:
            material_data.use_paint_texture = False

        return True