import bpy
import json
from shutil import copyfile
from .common import *


def copy_linked_map(input_name, directory, blender_material, node):
    node_input = node.inputs.get(input_name)
    if not node_input:
        return None
    filepath = None
    if node_input.is_linked:
        image = node_input.links[0].from_node.image
        filename = image.name
        source_filepath = bpy.path.abspath(image.filepath, library=image.library)
        filepath = library_path(blender_material) + "textures/" + filename
        full_filepath = directory + '/' + filepath
        os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
        copyfile(source_filepath, full_filepath)
    return filepath


def material_path(blender_material: bpy.types.Material):
    path = library_path(blender_material) + "materials/" + blender_material.name + ".material"
    return path.strip('/')


def write(report, directory):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        print("WRITING " + str(blender_material.name))
        report({'INFO'}, "Writing: " + str(blender_material.name))
        node = blender_material.node_tree.nodes.get("Material Output").inputs[0].links[0].from_node

        albedo_input = node.inputs.get("Base Color")
        albedo_map = copy_linked_map("Base Color", directory, blender_material, node)
        albedo = (0.0, 0.0, 0.0) if not albedo_input.default_value[:3] else albedo_input.default_value[:3]

        normal_map = copy_linked_map("Normal", directory, blender_material, node)
        metallic_map = copy_linked_map("Metallic", directory, blender_material, node)
        roughness_map = copy_linked_map("Roughness", directory, blender_material, node)
        ambient_occlusion_map = copy_linked_map("Ambient occlusion", directory, blender_material, node)

        roughness = node.inputs.get("Roughness").default_value
        metallic = node.inputs.get("Metallic").default_value

        opacity_node = node.inputs.get("Opacity")
        opacity = opacity_node.default_value if opacity_node else 1.0

        emission_node = node.inputs.get("Emission")
        emission = emission_node.default_value if emission_node else 0.0

        transmission = node.inputs.get("Transmission").default_value

        ambient_occlusion_input = node.inputs.get("Ambient occlusion")
        ambient_occlusion = ambient_occlusion_input.default_value if ambient_occlusion_input else 1.0

        material = {"albedo": tuple(albedo),
                    "opacity": opacity,
                    "transmission": transmission,
                    "roughness": float(roughness),
                    "metallic": float(metallic),
                    "emission": float(emission),
                    "ambient_occlusion": float(ambient_occlusion),
                    "albedo_map": albedo_map,
                    "normal_map": normal_map,
                    "metallic_map": metallic_map,
                    "roughness_map": roughness_map,
                    "ambient_occlusion_map": ambient_occlusion_map}

        path = directory + '/' + material_path(blender_material)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        json_file = open(path, 'w')
        json.dump(material, json_file)
        json_file.close()

        report({'INFO'}, "Wrote: " + path)
        report({'INFO'}, "Wrote material " + blender_material.name)
    report({'INFO'}, "Wrote all materials.")
