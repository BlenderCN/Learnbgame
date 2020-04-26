__author__ = 'Eric'

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


from sporemodder import materials
from collections import namedtuple


ActiveMaterial = namedtuple('ActiveMaterial', ('material_data', 'material_class'))


def get_materials_enum():
    return [(cls.__name__, cls.material_name, cls.material_description) for cls in materials.material_classes]


def set_material_type(rw4_material, context):
    for cls in materials.material_classes:
        print(cls.__name__)
        cls.set_is_active_material(rw4_material, cls.__name__ == rw4_material.material_type)


    return None


def parse_material_builder(material_builder, rw4_material):
    for cls in materials.material_classes:
        if cls.parse_material_builder(material_builder, rw4_material):
            rw4_material.material_type = cls.__name__
            break


def get_active_material(rw4_material):
    for cls in materials.material_classes:
        if cls.__name__ == rw4_material.material_type:
            return ActiveMaterial(cls.get_material_data(rw4_material), cls)

    return None


materials_enum = get_materials_enum()


def material_type_getter(self):
    for i in range(len(materials_enum)):
        if materials_enum[i][0] == self.material_type_str:
            return i

    return -1


def material_type_setter(self, value):
    self.material_type_str = materials_enum[value][0]


class RWBaseMaterial(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.renderWare4 = PointerProperty(type=cls)

        cls.material_type = EnumProperty(
            items=materials_enum,
            name="Material Type",
            description="The type of material used by this mesh, determines the shader, textures, etc",
            get=material_type_getter,
            set=material_type_setter,
            default="SkinPaintPart"
        )

        # get_materials_enum() doesn't always return the same order, so we must store a string instead of an int
        cls.material_type_str = StringProperty(
            default="SkinPaintPart"
        )

        cls.material_color = FloatVectorProperty(
            name="Material Color",
            subtype='COLOR',
            default=(1.0, 1.0, 1.0, 1.0),
            min=0.0,
            max=1.0,
            size=4
        )

        cls.ambient_color = FloatVectorProperty(
            name="Ambient Color",
            subtype='COLOR',
            default=(1.0, 1.0, 1.0),
            min=0.0,
            max=1.0,
            size=3
        )

        cls.alpha_type = EnumProperty(
            name="Material Opacity",
            items=[('NO_ALPHA', 'Opaque', "The material has no transparency."),
                   ('ALPHA', "Alpha", "The material can have transparency, determined by the texture's alpha channel."),
                   ('EXCLUDING_ALPHA', "Excluding", "Pixels with transpareny < 127 won't be rendered.")],
            default='NO_ALPHA'
        )

        for clazz in materials.material_classes:
            clazz.set_pointer_property(cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Material.renderWare4


class RWMaterialPanel(bpy.types.Panel):
    bl_label = "RenderWare4 Material Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        if context.material is not None:

            materialData = context.material.renderWare4

            row = self.layout.row()
            row.prop(materialData, 'material_type')

            active_material = get_active_material(materialData)

            if active_material is not None:

                if active_material.material_data.material_has_material_color:
                    row = self.layout.row()
                    row.prop(materialData, 'material_color')

                if active_material.material_data.material_has_ambient_color:
                    row = self.layout.row()
                    row.prop(materialData, 'ambient_color')
                    
                if active_material.material_data.material_use_alpha:
                    row = self.layout.row()
                    row.prop(materialData, 'alpha_type')

                active_material.material_class.draw_panel(self.layout, materialData)


def register():
    for cls in materials.material_classes:
        bpy.utils.register_class(cls)

    bpy.utils.register_class(RWBaseMaterial)


def unregister():
    for cls in materials.material_classes:
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(RWBaseMaterial)
