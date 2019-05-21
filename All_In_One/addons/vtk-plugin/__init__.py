"""
Blender plugin to import vtk unstrucutred grids
author:diehlpk
date: 13.10.2014
"""

bl_info = {"name": "VTK-Importer",
        "author": "diehlpk",
        "blender": (2, 6, 9),
        "version": (0, 0, 1),
        "location": "File > Import-Export",
        "description": "Import VTK unstructured grid",
        "category": "Import-Export"
}

# Imports for readinf vtk
from xml.etree import ElementTree
import re

# Import blender addon api
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty)


def add_particle(x_pos, y_pos, z_pos, radius):
    """Adds a primitive uV sphere to the blender engine
    @param x_pos X coordinate of the center of the sphere
    @param y_pos Y coordinate of the center of the sphre
    @param z_pos Z Coordinate of the center of the sphre
    @param radius Radius of the sphere
    """
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=6,
            ring_count=6,
            size=radius,
            location=(x_pos, y_pos, z_pos),
            rotation=(0, 0, 0),
            layers=(
                True, False, False, False, False, False, False, False,
                    False, False, False, False, False, False, False, False,
                    False, False, False, False
            )
    )


def value_to_rgb(minimum, maximum, value):
    """ Converts the value to a RGB map
    @param minimum The minimum of all values
    @param maximum The maximum of all values
    @param value The value
    """
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b_color = int(max(0, 255 * (1 - ratio)))
    r_color = int(max(0, 255 * (1 - ratio)))
    g_color = 255 - b_color - r_color
    return r_color, g_color, b_color


def values_to_rgb(ranges, values):
    """ Converts a three dimensional tuple to a RGB map
    @param ranges The mininum and maximum of each dimension
    @param values The value to transform
    """
    r_color = (float(values[0]) - float(ranges[0][0])) / float(ranges[0][1])
    g_color = (float(values[1]) - float(ranges[1][0])) / float(ranges[1][1])
    b_color = (float(values[2]) - float(ranges[2][0])) / float(ranges[2][1])
    return r_color, g_color, b_color


class ImportVTK(Operator, ImportHelper):

    """VTK unstructured grid importer"""
    bl_idname = "import.vtk"
    bl_label = "VTK importer"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def __init__(self):
        pass

    @classmethod
    def poll(cls, context):
        """Method polls"""
        return context.object is not None

    def execute(self, context):
        """Configuration"""
        radius = 0.05
        name = ""

        bpy.ops.object.select_all(action='DESELECT')

        add_particle(0, 0, 0, radius)
        self.sphere = bpy.context.object
        self.sphere.name = 'vtk_import_root_object'

        points = []
        material = []

        with open(self.filepath, 'r') as input_file:
            tree = ElementTree.parse(input_file)

        for node in tree.getiterator('DataArray'):
            if (node.attrib.get('Name') == 'Points' or
               node.attrib.get('Name') == 'coordinates'):

                dim = int(node.attrib.get('NumberOfComponents'))
                text = re.sub("\n", "", node.text)
                text = re.sub("\t", "", text)
                text = re.sub(" +", " ", text)
                text = text.lstrip(' ').rstrip(' ')
                splitted = text.split(' ')
                pos = []
                for element in splitted:
                    pos.append(element)
                    if len(pos) == dim:
                        points.append(pos)
                        pos = []

            if node.attrib.get('Name') == name and len(name) > 0:
                dim = int(node.attrib.get('NumberOfComponents'))
                colors = []
                if dim == 1:
                    text = re.sub(" +", "", node.text)
                    text = re.sub(" ", "", text)
                    text = re.sub("\t", "", text)
                    text = text.lstrip().rstrip()
                    splitted = text.split("\n")
                    for element in splitted:
                        colors.append(float(element))

                    minimum = min(colors)
                    maximum = max(colors)

                    for i in range(len(colors)):
                        material_object = bpy.data.materials.new(str(i))
                        material_object.diffuse_color = value_to_rgb(
                            minimum, maximum, colors[i])
                        material.append(material_object)
                if dim == 3:
                    text = re.sub("\n", "", node.text)
                    text = re.sub("\t", "", text)
                    text = re.sub(" +", " ", text)
                    text = text.lstrip(' ').rstrip(' ')
                    splitted = text.split(' ')
                    color = []
                    for element in splitted:
                        color.append(element)
                        if len(color) == dim:
                            colors.append(color)
                            color = []

                    min_r = min(zip(range(len(colors)), colors[0]))[1]
                    max_r = max(zip(range(len(colors)), colors[0]))[1]
                    min_g = min(zip(range(len(colors)), colors[0]))[1]
                    max_g = max(zip(range(len(colors)), colors[0]))[1]
                    min_b = min(zip(range(len(colors)), colors[0]))[1]
                    max_b = max(zip(range(len(colors)), colors[0]))[1]
                    ranges = [[min_r, max_r], [min_g, max_g], [min_b, max_b]]

                    for i in range(len(colors)):
                        material_object = bpy.data.materials.new(str(i))
                        material_object.diffuse_color = values_to_rgb(
                            ranges, colors[i])
                        material.append(material_object)
        index = 0
        len_points = len(points)
        len_material = len(material)
        for i in range(len_points):

            actual_object = self.sphere.copy()
            actual_object.name = 'particle_' + str(index)
            actual_object.data = self.sphere.data.copy()
            pos = points[i]
            actual_object.location = (
                float(pos[0]), float(pos[1]), float(pos[2]))
            bpy.context.scene.objects.link(actual_object)
            if len_points == len_material:
                actual_object.data.materials.append(material[i])
            index = index + 1

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(
            pattern='vtk_import_root_object',
                case_sensitive=False, extend=False)
        bpy.ops.object.delete()

        bpy.context.scene.update()

        return {'FINISHED'}


def invoke(self, context, event):
    """Method invokes the file pick up action"""
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}


def menu_func(self, context):
    """Method add the plugin to the menu"""
    self.layout.operator(ImportVTK.bl_idname, text="VTK Importer")


def register():
    """Method register the plugin"""
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    """Method unregister the plugin"""
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
