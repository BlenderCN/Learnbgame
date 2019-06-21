__author__ = 'Eric'


import bpy
from bpy.props import BoolProperty
from sporemodder import materials


# All RW materials must extend this class
class RWMaterial(bpy.types.PropertyGroup):
    material_name = ""
    material_description = ""
    material_has_material_color = BoolProperty(default=False)
    material_has_ambient_color = BoolProperty(default=False)
    material_use_alpha = BoolProperty(default=False)

    @staticmethod
    def set_pointer_property(cls):
        pass

    @staticmethod
    def get_material_data(rw4_material):
        return None

    @staticmethod
    def draw_panel(layout, rw4_material):
        pass

    @staticmethod
    def get_material_builder(exporter, rw4_material):
        return None

    @staticmethod
    def parse_material_builder(material, rw4_material):
        # parse the basic things
        
        if material.material_color is not None:
            rw4_material.material_color = material.material_color
            
        if material.ambient_color is not None:
            rw4_material.ambient_color = material.ambient_color
            
        rw4_material.alpha_type = material.detect_render_states()
        
        return False  # return True if the material was of the specified type

    @staticmethod
    def set_general_settings(material_builder, rw4_material, material_data):

        if material_data.material_has_material_color:
            material_builder.material_color = rw4_material.material_color

        if material_data.material_has_ambient_color:
            material_builder.ambient_color = rw4_material.ambient_color
            
        if material_data.material_use_alpha:
            material_builder.set_render_states(rw4_material.alpha_type)