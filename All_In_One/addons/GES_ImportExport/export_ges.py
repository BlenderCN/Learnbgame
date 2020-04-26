import bpy
import os
import shutil
import xml.etree.cElementTree as ET
from . import gntd
from . import mdsf
from bpy_extras.wm_utils.progress_report import (
    ProgressReport,
    ProgressReportSubstep,
)


bl_types = {"RGBA": "color4",
            "VALUE": "float",
            "VECTOR": "vector3",
            "SHADER": "closure",
            "BOOL": "bool"}

node_type_normalizer = {"Valtorgb": "ColorRamp",
                        "Combhsv": "CombineHSV",
                        "Combrgb": "CombineRGB",
                        "Combxyz": "CombineXYZ",
                        "Rgbtobw": "RGBtoBW",
                        "Sephsv": "SeparateHSV",
                        "Seprgb": "SeparateRGB",
                        "Brightcontrast": "BrightContrast",
                        "CurveVec": "VectorCurves",
                        "HueSat": "HueSaturationValue",
                        "MixRgb": "MixRGB",
                        "CurveRgb": "RGBCurves",
                        "NewGeometry": "Geometry",
                        "Rgb": "RGB",
                        "TexCoord": "TextureCoordinate",
                        "Uvmap": "UVMap",
                        "VectMath": "VectorMath"}

COLOR_CURVE_SAMPLES = 32
GROUP_HASH_LENGH = 5


def form_library_name(scene_path):
    return os.path.splitext(os.path.basename(scene_path))[0]


def conver_path_to_gem(file_path, light_suffix=False):
    return os.path.splitext(file_path)[0] + ("_lights" if light_suffix else "") + ".gem"


def conver_path_to_ges(file_path):
    return os.path.splitext(file_path)[0] + ".ges"


def indent_xml(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class SimpleNodeData(object):

    def __init__(self, n_type, n_name, n_inputs=None):
        self.type = n_type
        self.name = n_name
        self.inputs = n_inputs


class SimpleSocketData(object):

    def __init__(self, s_name):
        self.name = s_name


class SimpleLinkData(object):  # mimics blender link object. For polymorphism purposes

    def __init__(self, from_node, to_node, from_socket, to_socket):
        self.from_node = from_node
        self.to_node = to_node
        self.from_socket = from_socket
        self.to_socket = to_socket


def normalize_name(name):
    parts = name.split("_")
    str_array = []
    for p in parts:
        str_array.append(p.title())
    return "".join(str_array)


def normalize_node_type(name):
    n = normalize_name(name)
    if n in node_type_normalizer:
        return node_type_normalizer[n]
    else:
        return n


def get_blender_type(bl_input_type):
    if bl_input_type in bl_types:
        return bl_types[bl_input_type]
    else:
        return None


def get_blender_default_value(bl_input):
    if str(bl_input.type) in bl_types:
        if str(bl_input.type) == "SHADER":
            return gntd.Closure()
        else:
            value = bl_input.default_value
            if str(bl_input.type) == "RGBA":
                return gntd.Color4(value[0], value[1], value[2], value[3])
            elif str(bl_input.type) == "VALUE":
                return float(value)
            elif str(bl_input.type) == "VECTOR":
                return gntd.Normal(value[0], value[1], value[2])
            else:
                return None
    else:
        if str(bl_input.type) == "STRING":
            return str(bl_input.default_value)
        else:
            return None


def get_file_path(image, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath):
    file_path = None
    if image is not None:
        abs_image_path = bpy.path.abspath(image.filepath)
        lib_path = False
        if image.library is not None:
            lib_path = True
            abs_image_path_from_lib = os.path.split(bpy.path.abspath(image.library.filepath))[0] + image.filepath[1:]
        if is_texture_copy:
            dir_path = os.path.split(gem_filepath)[0] + "\\" + str(lib_name) + "_textures"
            # create directory if it is not exist
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if os.path.isfile(abs_image_path):  # file exists, copy it
                shutil.copy2(abs_image_path, dir_path)
                abs_image_path = dir_path + "\\" + os.path.split(abs_image_path)[1]
            else:
                if lib_path:
                    # try to get image from library
                    if os.path.isfile(abs_image_path_from_lib):
                        shutil.copy2(abs_image_path_from_lib, dir_path)
                        abs_image_path = dir_path + "\\" + os.path.split(abs_image_path_from_lib)[1]
                else:  # we should extract from packed blender file (if it is possible)
                    original_path = image.filepath
                    abs_image_path = dir_path + "\\" + os.path.split(abs_image_path)[1]
                    image.filepath = abs_image_path
                    try:
                        image.save()
                    except Exception:
                        print("Can't export image " + abs_image_path)
                    image.filepath = original_path
        if is_texture_absolute_path:
            file_path = abs_image_path
        else:
            file_path = "\\\\" + os.path.relpath(abs_image_path, os.path.split(gem_filepath)[0])

    return file_path


def convert_file_path(raw_path, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath):
    if len(raw_path) > 0:
        abs_path = bpy.path.abspath(raw_path)
        if is_texture_copy:
            dir_path = os.path.split(gem_filepath)[0] + "\\" + str(lib_name) + "_textures"
            # create directory if it is not exist
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            if os.path.isfile(abs_path):  # file exists, copy it
                shutil.copy2(abs_path, dir_path)
                abs_path = dir_path + "\\" + os.path.split(abs_path)[1]
            else:
                return None
        if is_texture_absolute_path:
            file_path = abs_path
        else:
            file_path = "\\\\" + os.path.relpath(abs_path, os.path.split(gem_filepath)[0])
        return file_path
    else:
        return None


# return answer in the form [(param_name, param_type(string),
# param_value), ...] bsdf_node.add_parameter("InnerParameter", "vector3",
# Normal(1.0))
def get_node_parameters(node, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath):
    node_type = str(node.type)
    if node_type == "TEX_VORONOI":
        return [("Coloring", "string", node.coloring),
                ("Distance", "string", node.distance),
                ("Feature", "string", node.feature)]
    elif node_type == "TEX_MUSGRAVE":
        return [("Musgrave Type", "string", node.musgrave_type)]
    elif node_type == "TEX_POINTDENSITY":
        return [("Space", "string", node.space),
                ("Interpolation", "string", node.interpolation),
                ("Point Source", "string", node.point_source),
                ("Radius", "float", node.radius),
                ("Resolution", "int", node.resolution),
                ("Particle Color Source", "string", node.particle_color_source)]
    elif node_type == "TEX_IMAGE":
        file_name = get_file_path(node.image, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath)
        to_return = [("Color Space", "string", node.color_space),
                     ("Interpolation", "string", node.interpolation),
                     ("Extension", "string", node.extension),
                     ("Projection", "string", node.projection),
                     ("Projection Blend", "float", node.projection_blend)]
        if file_name is None:
            return to_return
        else:
            return to_return + [("Filename", "string", file_name)]
    elif node_type == "TEX_MAGIC":
        return [("Turbulence Depth", "int", node.turbulence_depth)]
    elif node_type == "TEX_GRADIENT":
        return [("Gradient Type", "string", node.gradient_type)]
    elif node_type == "TEX_BRICK":
        return [("Offset", "float", node.offset),
                ("Offset Frequency", "int", node.offset_frequency),
                ("Squash", "float", node.squash),
                ("Squash Frequency", "int", node.squash_frequency)]
    elif node_type == "TEX_ENVIRONMENT":
        file_name = get_file_path(node.image, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath)
        to_return = [("Color Space", "string", node.color_space),
                     ("Interpolation", "string", node.interpolation),
                     ("Projection", "string", node.projection)]
        if file_name is None:
            return to_return
        else:
            return to_return + [("Filename", "string", file_name)]
    elif node_type == "TEX_SKY":
        return [("Sky Type", "string", node.sky_type), ("Sun Direction", "vector3", gntd.Vector3(node.sun_direction[0], node.sun_direction[1], node.sun_direction[2])), ("Turbidity", "float", node.turbidity), ("Ground Albedo", "float", node.ground_albedo)]
    elif node_type == "TEX_WAVE":
        return [("Wave Type", "string", node.wave_type), ("Profile", "string", node.wave_profile)]
    elif node_type == "TEX_IES":
        file_name = convert_file_path(node.filepath, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath)
        if file_name is None:
            return []
        else:
            return [("Filename", "string", file_name)]
    elif node_type == "BSDF_GLOSSY":
        return [("Distribution", "string", node.distribution)]
    elif node_type == "BSDF_HAIR":
        return [("Component", "string", node.component)]
    elif node_type == "BSDF_REFRACTION":
        return [("Distribution", "string", node.distribution)]
    elif node_type == "BSDF_PRINCIPLED":
        return [("Distribution", "string", node.distribution), ("Subsurface Method", "string", node.subsurface_method)]
    elif node_type == "BSDF_HAIR_PRINCIPLED":
        return [("Parametrization", "string", node.parametrization)]
    elif node_type == "BSDF_GLASS":
        return [("Distribution", "string", node.distribution)]
    elif node_type == "BSDF_ANISOTROPIC":
        return [("Distribution", "string", node.distribution)]
    elif node_type == "SUBSURFACE_SCATTERING":
        return [("Falloff", "string", node.falloff)]
    elif node_type == "BSDF_TOON":
        return [("Component", "string", node.component)]
    elif node_type == "BUMP":
        return [("Invert", "bool", node.invert)]
    elif node_type == "VECT_TRANSFORM":
        return [("Vector Type", "string", node.vector_type), ("Convert From", "string", node.convert_from), ("Convert To", "string", node.convert_to)]
    elif node_type == "MIX_RGB":
        return [("Blend Type", "string", node.blend_type), ("Use Clamp", "bool", node.use_clamp)]
    elif node_type == "UVMAP":
        return [("From Instancer", "bool", node.from_instancer), ("Attribute", "string", node.uv_map)]
    elif node_type == "ATTRIBUTE":
        return [("Attribute", "string", node.attribute_name)]
    elif node_type == "TEX_COORD":
        return [("From Instancer", "bool", node.from_instancer)]
    elif node_type == "TANGENT":
        return [("Direction Type", "string", node.direction_type), ("Axis", "string", node.axis), ("Attribute", "string", node.uv_map)]
    elif node_type == "VALUE":
        return [("Value", "float", node.outputs[0].default_value)]
    elif node_type == "AMBIENT_OCCLUSION":
        return [("Samples", "int", node.samples),
                ("Inside", "bool", node.inside),
                ("Only Local", "bool", node.only_local)]
    elif node_type == "WIREFRAME":
        return [("Use Pixel Size", "bool", node.use_pixel_size)]
    elif node_type == "RGB":
        return [("Value", "color4", gntd.Color4(node.outputs[0].default_value[0], node.outputs[0].default_value[1], node.outputs[0].default_value[2]))]
    elif node_type == "CURVE_RGB":
        is_sampling = True
        if is_sampling:  # evaluate on additional points
            node.mapping.initialize()
            r_curve = node.mapping.curves[0]
            g_curve = node.mapping.curves[1]
            b_curve = node.mapping.curves[2]
            c_curve = node.mapping.curves[3]
            r_array = []
            g_array = []
            b_array = []
            c_array = []
            for p_index in range(COLOR_CURVE_SAMPLES):
                pos = float(p_index) / float(COLOR_CURVE_SAMPLES - 1)
                r_array.append(gntd.Vector2(pos, r_curve.evaluate(pos)))
                g_array.append(gntd.Vector2(pos, g_curve.evaluate(pos)))
                b_array.append(gntd.Vector2(pos, b_curve.evaluate(pos)))
                c_array.append(gntd.Vector2(pos, c_curve.evaluate(pos)))
            return [("R", "vectorArray", gntd.VectorArray(r_array)), ("G", "vectorArray", gntd.VectorArray(g_array)), ("B", "vectorArray", gntd.VectorArray(b_array)), ("C", "vectorArray", gntd.VectorArray(c_array))]
        else:  # save only points int hte curves
            # curve R
            points_r = node.mapping.curves[0].points
            r_array = []
            for p in points_r:
                r_array.append(gntd.Vector2(p.location[0], p.location[1]))
            # curve G
            points_g = node.mapping.curves[1].points
            g_array = []
            for p in points_g:
                g_array.append(gntd.Vector2(p.location[0], p.location[1]))
            # curve B
            points_b = node.mapping.curves[2].points
            b_array = []
            for p in points_b:
                b_array.append(gntd.Vector2(p.location[0], p.location[1]))
            # curve Combined
            points_c = node.mapping.curves[3].points
            c_array = []
            for p in points_c:
                c_array.append(gntd.Vector2(p.location[0], p.location[1]))
            return [("R", "vectorArray", gntd.VectorArray(r_array)), ("G", "vectorArray", gntd.VectorArray(g_array)), ("B", "vectorArray", gntd.VectorArray(b_array)), ("C", "vectorArray", gntd.VectorArray(c_array))]
    elif node_type == "CURVE_VEC":
        points_x = node.mapping.curves[0].points
        points_y = node.mapping.curves[1].points
        points_z = node.mapping.curves[2].points
        x_array = []
        y_array = []
        z_array = []
        for x in points_x:
            x_array.append(gntd.Vector2(x.location[0], x.location[1]))
        for y in points_y:
            y_array.append(gntd.Vector2(y.location[0], y.location[1]))
        for z in points_z:
            z_array.append(gntd.Vector2(z.location[0], z.location[1]))
        return [("X", "vectorArray", gntd.VectorArray(x_array)),
                ("Y", "vectorArray", gntd.VectorArray(y_array)),
                ("Z", "vectorArray", gntd.VectorArray(z_array))]
    elif node_type == "MAPPING":
        return [("Vector Type", "string", node.vector_type),
                ("Translation", "vector3", gntd.Vector3(node.translation[0], node.translation[1], node.translation[2])),
                ("Rotation", "vector3", gntd.Vector3(node.rotation[0], node.rotation[1], node.rotation[2])),
                ("Scale", "vector3", gntd.Vector3(node.scale[0], node.scale[1], node.scale[2])),
                ("Use Min", "bool", node.use_min),
                ("Use Max", "bool", node.use_max),
                ("Min", "vector3", gntd.Vector3(node.min[0], node.min[1], node.min[2])),
                ("Max", "vector3", gntd.Vector3(node.max[0], node.max[1], node.max[2]))]
    elif node_type == "NORMAL_MAP":
        return [("Space", "string", node.space), ("Attribute", "string", node.uv_map)]
    elif node_type == "NORMAL":
        return [("Direction", "vector3", gntd.Normal(node.outputs[0].default_value[0], node.outputs[0].default_value[1], node.outputs[0].default_value[2]))]
    elif node_type == "VECT_MATH":
        return [("Operation", "string", node.operation)]
    elif node_type == "VALTORGB":
        # read positions
        bl_elements = node.color_ramp.elements
        pos_array = []
        color_array = []
        for e in bl_elements:
            pos_array.append(e.position)
            color_array.append(
                gntd.Color4(e.color[0], e.color[1], e.color[2], e.color[3]))
        return [("Color Mode", "string", node.color_ramp.color_mode),
                ("Interpolation", "string", node.color_ramp.interpolation),
                ("Position", "vectorArray", gntd.VectorArray(pos_array)),
                ("Color", "vectorArray", gntd.VectorArray(color_array))]
    elif node_type == "MATH":
        return [("Operation", "string", node.operation), ("Use Clamp", "bool", node.use_clamp)]
    elif node_type == "BEVEL":
        return [("Samples", "int", node.samples)]
    elif node_type == "VECTOR_DISPLACEMENT":
        return [("Space", "string", node.space)]
    elif node_type == "DISPLACEMENT":
        return [("Space", "string", node.space)]
    else:
        return []


def node_name(node):
    node_type = node.type
    if node_type == "GROUP":
        return node.name + str(hash(node))[-GROUP_HASH_LENGH:]
    else:
        return node.name


def add_node_to_tree(tree, node, nodes_counter, is_texture_absolute_path=False, is_texture_copy=False, lib_name="", gem_filepath=""):
    node_type = normalize_node_type(node.type)
    # node_name = node.name
    n_name = node_name(node)
    '''if node_type == "Group":
        node_name += str(nodes_counter)'''
    td_node = tree.add_node(node_type, n_name, node.label)
    input_index = 0
    for bl_input in node.inputs:
        t = get_blender_type(str(bl_input.type))
        if t is not None:
            # create default value
            default = get_blender_default_value(bl_input)
            if default is not None:
                if normalize_node_type(node.type) == "VectorMath" or normalize_node_type(node.type) == "Math" or (normalize_node_type(node.type) == "MixShader" and str(bl_input.name) != "Fac") or normalize_node_type(node.type) == "AddShader":  # for Math input ports (both Value in default) convert to Value1 and Value2
                    input_index = input_index + 1
                    td_node.add_input(str(bl_input.name) + str(input_index), t, default)
                else:
                    td_node.add_input(str(bl_input.name), t, default)
        else:
            if str(bl_input.type) == "STRING":  # string input save as parameter
                td_node.add_parameter(normalize_name(bl_input.name), "string", get_blender_default_value(bl_input))
    for bl_output in node.outputs:
        t = get_blender_type(str(bl_output.type))
        if t is not None:
            td_node.add_output(bl_output.name, t)
    node_params = get_node_parameters(node, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath)
    for p in node_params:
        td_node.add_parameter(p[0], p[1], p[2])
    return td_node


def is_node_correct(bl_node):
    name = str(bl_node.type)
    if name != "FRAME" and name != "REROUTE":
        return True


def get_in_socket_index(node, in_socket):
    inputs = node.inputs
    if inputs is not None:
        return node.inputs.values().index(in_socket)
    else:
        return None


def get_exeptional_suffix(node, in_socket):
    if normalize_node_type(node.type) == "VectorMath" or normalize_node_type(node.type) == "Math" or normalize_node_type(node.type) == "AddShader":
        index = get_in_socket_index(node, in_socket)
        if index is not None:
            return str(index + 1)
        else:
            return ""
    elif normalize_node_type(node.type) == "MixShader" and in_socket.name != "Fac":
        index = get_in_socket_index(node, in_socket)
        if index is not None:
            return str(index)
        else:
            return ""
    else:
        return ""


def add_link_to_tree(tree, link, is_subtree=False):
    if is_subtree:
        n_from_type = str(link.from_node.type)
        n_to_type = str(link.to_node.type)
        if n_from_type == "GROUP_INPUT" and n_to_type != "GROUP_OUTPUT":
            tree.add_external_input_connection(node_name(link.to_node), link.to_socket.name + get_exeptional_suffix(link.to_node, link.to_socket), link.from_socket.name)
        elif n_from_type != "GROUP_INPUT" and n_to_type == "GROUP_OUTPUT":
            tree.add_external_output_connection(node_name(link.from_node), link.from_socket.name, link.to_socket.name + get_exeptional_suffix(link.to_node, link.to_socket))
        elif n_from_type == "GROUP_INPUT" and n_to_type == "GROUP_OUTPUT":
            tree.add_external_throw_connection(link.from_socket.name, link.to_socket.name + get_exeptional_suffix(link.to_node, link.to_socket))
        else:
            tree.add_connection(node_name(link.from_node), link.from_socket.name, node_name(link.to_node), link.to_socket.name + get_exeptional_suffix(link.to_node, link.to_socket))
    else:
        tree.add_connection(node_name(link.from_node), link.from_socket.name, node_name(link.to_node), link.to_socket.name + get_exeptional_suffix(link.to_node, link.to_socket))


def add_nodes_and_links(root, bl_nodes, bl_links, nodes_counter, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath, is_subtree=False):
    for bl_node in bl_nodes:
        if is_node_correct(bl_node):
            n_type = str(bl_node.type)
            if (is_subtree is True and n_type != "GROUP_INPUT" and n_type != "GROUP_OUTPUT") or (is_subtree is False):
                new_node = add_node_to_tree(root, bl_node, nodes_counter, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath)
                nodes_counter += 1
                if str(bl_node.type) == "GROUP" and bl_node.node_tree is not None:
                    group_node = new_node.add_subtree()
                    add_nodes_and_links(group_node, bl_node.node_tree.nodes, bl_node.node_tree.links, nodes_counter, is_texture_absolute_path, is_texture_copy, lib_name, gem_filepath, True)
    half_links = []
    for bl_link in bl_links:
        if str(bl_link.from_node.type) != "REROUTE" and str(bl_link.to_node.type) != "REROUTE":
            if is_node_correct(bl_link.from_node) and is_node_correct(bl_link.to_node):
                add_link_to_tree(root, bl_link, is_subtree)
        else:
            # collect this links
            half_links.append(bl_link)
    # reorganize links. Make it without middle reroute nodes
    links = []
    for l in half_links:
        if str(l.to_node.type) != "REROUTE" and is_node_correct(l.to_node):
            to_node = SimpleNodeData(l.to_node.type, node_name(l.to_node), l.to_node.inputs)
            # to_socket = SimpleSocketData(l.to_socket.name)
            to_socket = l.to_socket
            # next we should find from_node
            find_target = node_name(l.from_node)
            is_find = False
            l_index = 0
            while not is_find:
                t_link = half_links[l_index]
                if node_name(t_link.to_node) == find_target:
                    if str(t_link.from_node.type) != "REROUTE":
                        is_find = True
                    else:
                        l_index = 0
                        find_target = node_name(t_link.from_node)
                else:
                    l_index = l_index + 1
                if l_index >= len(half_links):
                    is_find = True
            if l_index < len(half_links):
                from_node = SimpleNodeData(half_links[l_index].from_node.type, node_name(half_links[l_index].from_node))
                from_socket = SimpleSocketData(half_links[l_index].from_socket.name)
                links.append(SimpleLinkData(from_node, to_node, from_socket, to_socket))
    for link in links:
        add_link_to_tree(root, link, is_subtree)


def actual_material_export(progress, file_path, is_texture_absolute, is_save_textures, materials):
    library_name = form_library_name(file_path)
    doc = gntd.NodeTreeDescriptor(library_name)
    m_index = 0
    is_progress = False
    if progress is not None:
        is_progress = True
    if is_progress:
        progress.enter_substeps(len(materials))
    for bl_material in materials:
        if is_progress:
            progress.step()
        if bl_material is not None and bl_material.node_tree is not None:
            td_node_tree = doc.add_material(str(bl_material.name), normalize_name(str(bpy.context.scene.render.engine)))
            nodes_counter = 0
            add_nodes_and_links(td_node_tree, bl_material.node_tree.nodes, bl_material.node_tree.links, nodes_counter, is_texture_absolute, is_save_textures, library_name, file_path)
        m_index = m_index + 1
    doc.write_xml(file_path)
    if is_progress:
        progress.leave_substeps()


def export_materials(progress, file_path, is_save_textures, is_texture_absolute, only_active=False):
    if bpy.context.scene.render.engine == "CYCLES":
        if only_active:
            if len(bpy.context.selected_objects) > 0:
                material = bpy.context.selected_objects[0].active_material
                if material.node_tree is not None:
                    actual_material_export(progress, file_path, is_texture_absolute, is_save_textures, [material])
            else:
                print("Select object and material on it.")
        else:
            all_materials = bpy.data.materials
            is_should_export = False
            for bl_mat in all_materials:
                if bl_mat.node_tree is not None:
                    is_should_export = True
            if is_should_export:
                actual_material_export(progress, file_path, is_texture_absolute, is_save_textures, all_materials)


def float_to_str(value):
    return str(round(value, 6))


def color_to_str(color):
    return " ".join([float_to_str(color[0]), float_to_str(color[1]), float_to_str(color[2])])


def matrix_to_string(matrix, position_row=False):  # position_row=False is default matrix from Blender. If True, we should transpose it
    # writing elements by rows
    row0 = matrix[0]
    row1 = matrix[1]
    row2 = matrix[2]
    row3 = matrix[3]
    if position_row is False:
        return " ".join([float_to_str(row0[0]), float_to_str(row0[1]), float_to_str(row0[2]), float_to_str(row0[3]),
                         float_to_str(row1[0]), float_to_str(row1[1]), float_to_str(row1[2]), float_to_str(row1[3]),
                         float_to_str(row2[0]), float_to_str(row2[1]), float_to_str(row2[2]), float_to_str(row2[3]),
                         float_to_str(row3[0]), float_to_str(row3[1]), float_to_str(row3[2]), float_to_str(row3[3])])
    else:  # write transposed matrix
        return " ".join([float_to_str(row0[0]), float_to_str(row1[0]), float_to_str(row2[0]), float_to_str(row3[0]),
                         float_to_str(row0[1]), float_to_str(row1[1]), float_to_str(row2[1]), float_to_str(row3[1]),
                         float_to_str(row0[2]), float_to_str(row1[2]), float_to_str(row2[2]), float_to_str(row3[2]),
                         float_to_str(row0[3]), float_to_str(row1[3]), float_to_str(row2[3]), float_to_str(row3[3])])


def export_transform(root, object, only_local=False):
    ET.SubElement(root, "transform", {"space": "Local", "mode": "Column", "matrix": matrix_to_string(object.matrix_local)})
    if only_local is False:
        ET.SubElement(root, "transform", {"space": "Global", "mode": "Column", "matrix": matrix_to_string(object.matrix_world)})


def export_visibility(root, hide_render, hide_viewport):
    ET.SubElement(root, "visibility", {"render": str(not hide_render), "viewport": str(not hide_viewport)})


def export_light(root, object, light, hide_mode=(False, False), only_local=False):
    is_cycles = bpy.context.scene.render.engine == "CYCLES"
    prop_dict = {}
    prop_dict["type"] = normalize_name(light.type)
    prop_dict["color"] = color_to_str(light.color)

    ET.SubElement(root, "material", {"material_0": str(light.name)})

    if light.type == "AREA":
        if light.shape == "SQUARE":
            prop_dict["size_x"] = float_to_str(light.size)
            prop_dict["size_y"] = float_to_str(light.size)
        else:
            prop_dict["size_x"] = float_to_str(light.size)
            prop_dict["size_y"] = float_to_str(light.size_y)
        if is_cycles:
            prop_dict["portal"] = str(light.cycles.is_portal)
    else:
        prop_dict["size"] = float_to_str(light.shadow_soft_size)
    if is_cycles:
        prop_dict["cast_shadow"] = str(light.cycles.cast_shadow)
        prop_dict["multiple_importance"] = str(light.cycles.use_multiple_importance_sampling)
        prop_dict["max_bounces"] = str(light.cycles.max_bounces)
    else:
        # for non-Cycles lights add strength
        prop_dict["strength"] = float_to_str(light.energy)
        # also existing of the shadows
        # prop_dict["cast_shadow"] = str(light.shadow_method != "NOSHADOW")
    if light.type == "SPOT":
        prop_dict["spot_size"] = float_to_str(light.spot_size)
        prop_dict["spot_blend"] = float_to_str(light.spot_blend)
    if light.node_tree is not None:
        prop_dict["use_nodes"] = str(True)
    else:
        prop_dict["use_nodes"] = str(False)
    ET.SubElement(root, "properties", prop_dict)
    export_transform(root, object, only_local)
    export_visibility(root, hide_mode[0], hide_mode[1])


def export_ray_visibility(vis, use_shadow=False):
    prop_dict = {}
    prop_dict["camera"] = str(vis.camera)
    prop_dict["diffuse"] = str(vis.diffuse)
    prop_dict["glossy"] = str(vis.glossy)
    prop_dict["transmission"] = str(vis.transmission)
    prop_dict["scatter"] = str(vis.scatter)
    if use_shadow:
        prop_dict["shadow"] = str(vis.shadow)
    return prop_dict


def export_background(root):
    world = bpy.context.scene.world
    if world is not None:
        world_xml = ET.SubElement(root, "background", {"name": str(world.name), "render": normalize_name(str(bpy.context.scene.render.engine))})
        prop_dict = {}
        if world.node_tree is None:
            prop_dict["use_nodes"] = str(False)
            prop_dict["color"] = color_to_str(world.horizon_color)
        else:
            prop_dict["use_nodes"] = str(True)
        if bpy.context.scene.render.engine == "CYCLES":  # export Cycles parameters
            prop_dict["use_ao"] = str(world.light_settings.use_ambient_occlusion)
            prop_dict["ao_factor"] = str(world.light_settings.ao_factor)
            prop_dict["ao_distance"] = str(world.light_settings.distance)
            # settings
            # prop_dict["max_resolution"] = str(world.cycles.sample_map_resolution)
            # prop_dict["max_bounces"] = str(world.cycles.max_bounces)
            prop_dict["volume_sampling"] = normalize_name(world.cycles.volume_sampling)
            prop_dict["volume_interpolation"] = normalize_name(world.cycles.volume_interpolation)
            prop_dict["homogeneous_volume"] = str(world.cycles.homogeneous_volume)
            # ray visibility
            ET.SubElement(world_xml, "ray_visibility", export_ray_visibility(world.cycles_visibility))
        ET.SubElement(world_xml, "properties", prop_dict)


def export_object(root, object, hide_mode=(False, False), over_matrix=None, only_local=False):
    # transforms
    if over_matrix is None:
        export_transform(root, object, only_local)
    else:
        ET.SubElement(root, "transform", {"space": "Global", "mode": "Column", "matrix": matrix_to_string(over_matrix)})
    export_visibility(root, hide_mode[0], hide_mode[1])
    # materials
    materials = object.material_slots
    mat_data = {}
    for mat_index in range(len(materials)):
        mat_data["material_" + str(mat_index)] = materials[mat_index].name
    prop_materials = ET.SubElement(root, "material", mat_data)
    if bpy.context.scene.render.engine == "CYCLES":
        ET.SubElement(root, "ray_visibility", export_ray_visibility(object.cycles_visibility, True))
        prop_dict = {}
        prop_dict["shadow_catcher"] = str(object.cycles.is_shadow_catcher)
        # prop_dict["holdout"] = str(object.cycles.is_holdout)
        prop_dict["camera_cull"] = str(object.cycles.use_camera_cull)
        prop_dict["distance_cull"] = str(object.cycles.use_distance_cull)
        ET.SubElement(root, "properties", prop_dict)


def export_null(root, null, hide_mode=(False, False), only_local=False):
    # for null export only transforms
    export_transform(root, null, only_local)


def conver_matrix_to_arrays(matrix):
    to_return = [[matrix[i][j] for j in range(4)] for i in range(4)]
    return to_return


def mult_matrix_to_vector(matrix, vector):
    to_return = [0 for i in range(4)]
    for i in range(4):
        s = 0
        for j in range(4):
            s = s + matrix[i][j] * vector[j]
        to_return[i] = s
    return to_return


def vector_to_str(vector):
    str_array = []
    for v in vector:
        str_array.append(float_to_str(v))
    return " ".join(str_array)


def export_camera(root, camera, camera_object):
    is_cycles = bpy.context.scene.render.engine == "CYCLES"
    # export transform
    export_transform(root, camera_object)
    # export target position
    dof_distance = camera.dof_distance
    target_ghost = None
    if abs(dof_distance) < 0.0001:
        target_ghost = [0, 0, -10, 1]
    else:
        target_ghost = [0, 0, -1 * dof_distance, 1]
    ET.SubElement(root, "target", {"position": vector_to_str(mult_matrix_to_vector(conver_matrix_to_arrays(camera_object.matrix_world), target_ghost))})
    prop_dict = {}
    # lens parameters
    prop_dict["type"] = normalize_name(camera.type)
    if camera.type == "PERSP":
        prop_dict["fov"] = float_to_str(camera.angle)
    elif camera.type == "ORTHO":
        prop_dict["ortho_scale"] = float_to_str(camera.ortho_scale)
    elif camera.type == "PANO":
        if is_cycles:
            prop_dict["panorama_type"] = normalize_name(camera.cycles.panorama_type)
            if camera.cycles.panorama_type == "MIRRORBALL":
                pass
            elif camera.cycles.panorama_type == "FISHEYE_EQUISOLID":
                prop_dict["fisheye_lens"] = float_to_str(camera.cycles.fisheye_lens)
                prop_dict["fisheye_fov"] = float_to_str(camera.cycles.fisheye_fov)
            elif camera.cycles.panorama_type == "FISHEYE_EQUIDISTANT":
                prop_dict["fisheye_fov"] = float_to_str(camera.cycles.fisheye_fov)
            elif camera.cycles.panorama_type == "EQUIRECTANGULAR":
                prop_dict["latitude_min"] = float_to_str(camera.cycles.latitude_min)
                prop_dict["latitude_max"] = float_to_str(camera.cycles.latitude_max)
                prop_dict["longitude_min"] = float_to_str(camera.cycles.longitude_min)
                prop_dict["longitude_max"] = float_to_str(camera.cycles.longitude_max)
        else:
            prop_dict["fov"] = float_to_str(camera.angle)
    prop_dict["shift_x"] = float_to_str(camera.shift_x)
    prop_dict["shift_y"] = float_to_str(camera.shift_y)
    prop_dict["clip_start"] = float_to_str(camera.clip_start)
    prop_dict["clip_end"] = float_to_str(camera.clip_end)
    prop_dict["sensor_fit"] = normalize_name(camera.sensor_fit)
    prop_dict["sensor_width"] = float_to_str(camera.sensor_width)
    prop_dict["sensor_height"] = float_to_str(camera.sensor_height)
    prop_dict["dof_distance"] = float_to_str(dof_distance)
    if is_cycles:
        prop_dict["aperture_type"] = normalize_name(camera.cycles.aperture_type)
        if camera.cycles.aperture_type == "RADIUS":
            prop_dict["aperture_size"] = float_to_str(camera.cycles.aperture_size)
        elif camera.cycles.aperture_type == "FSTOP":
            prop_dict["aperture_fstop"] = float_to_str(camera.cycles.aperture_fstop)
        prop_dict["aperture_blades"] = str(camera.cycles.aperture_blades)
        prop_dict["aperture_rotation"] = float_to_str(camera.cycles.aperture_rotation)
        prop_dict["aperture_ratio"] = float_to_str(camera.cycles.aperture_ratio)
    ET.SubElement(root, "properties", prop_dict)


def export_render_settings(root):
    scene = bpy.context.scene
    render = bpy.context.scene.render
    render_dict = {}
    render_dict["render"] = normalize_name(render.engine)
    # export dimensions
    render_dict["resolution_x"] = str(render.resolution_x)
    render_dict["resolution_y"] = str(render.resolution_y)
    render_dict["frame_start"] = str(scene.frame_start)
    render_dict["frame_end"] = str(scene.frame_end)
    render_dict["frame_step"] = str(scene.frame_step)
    render_xml = ET.SubElement(root, "render_settings", render_dict)
    is_cycles = render.engine == "CYCLES"
    # next Cycles specific options
    if is_cycles:
        # sampling
        cycles = bpy.context.scene.cycles
        sampling_dict = {}
        sampling_dict["method"] = normalize_name(cycles.progressive)
        sampling_dict["pattern"] = normalize_name(cycles.sampling_pattern)
        sampling_dict["clamp_direct"] = float_to_str(cycles.sample_clamp_direct)
        sampling_dict["clamp_indirect"] = float_to_str(cycles.sample_clamp_indirect)
        sampling_dict["light_threshold"] = float_to_str(cycles.light_sampling_threshold)
        sampling_dict["seed"] = str(cycles.seed)
        if cycles.progressive == "PATH":
            sampling_dict["samples"] = str(cycles.samples)
        elif cycles.progressive == "BRANCHED_PATH":
            sampling_dict["samples"] = str(cycles.aa_samples)
            sampling_dict["diffuse_samples"] = str(cycles.diffuse_samples)
            sampling_dict["glossy_samples"] = str(cycles.glossy_samples)
            sampling_dict["transmission_samples"] = str(cycles.transmission_samples)
            sampling_dict["ao_samples"] = str(cycles.ao_samples)
            sampling_dict["mesh_light_samples"] = str(cycles.mesh_light_samples)
            sampling_dict["subsurface_samples"] = str(cycles.subsurface_samples)
            sampling_dict["volume_samples"] = str(cycles.volume_samples)
        sampling_dict["volume_step_size"] = float_to_str(cycles.volume_step_size)
        sampling_dict["volume_max_steps"] = str(cycles.volume_max_steps)
        sampling_dict["sample_all_lights_direct"] = str(cycles.sample_all_lights_direct)
        sampling_dict["sample_all_lights_indirect"] = str(cycles.sample_all_lights_indirect)
        sampling_xml = ET.SubElement(render_xml, "sampling", sampling_dict)
        # light paths
        bounces_dict = {}
        bounces_dict["transparent_max_bounces"] = str(cycles.transparent_max_bounces)
        bounces_dict["max_bounces"] = str(cycles.max_bounces)
        bounces_dict["diffuse_bounces"] = str(cycles.diffuse_bounces)
        bounces_dict["glossy_bounces"] = str(cycles.glossy_bounces)
        bounces_dict["transmission_bounces"] = str(cycles.transmission_bounces)
        bounces_dict["volume_bounces"] = str(cycles.volume_bounces)
        bounces_dict["caustics_reflective"] = str(cycles.caustics_reflective)
        bounces_dict["caustics_refractive"] = str(cycles.caustics_refractive)
        bounces_dict["filter_glossy"] = str(cycles.blur_glossy)
        path_xml = ET.SubElement(render_xml, "bounces", bounces_dict)
        # film settings
        film_dict = {}
        film_dict["exposure"] = float_to_str(cycles.film_exposure)
        film_dict["film_transparent"] = str(cycles.film_transparent)
        film_dict["film_transparent_glass"] = str(cycles.film_transparent_glass)
        film_dict["filter"] = normalize_name(cycles.pixel_filter_type)
        if cycles.pixel_filter_type == "BLACKMAN_HARRIS" or cycles.pixel_filter_type == "GAUSSIAN":
            film_dict["width"] = float_to_str(cycles.filter_width)
        film_xml = ET.SubElement(render_xml, "film", film_dict)
        # performance
        pref_dict = {}
        pref_dict["threads_mode"] = normalize_name(render.threads_mode)
        pref_dict["threads"] = str(render.threads)
        pref_dict["tile_order"] = normalize_name(cycles.tile_order)
        pref_dict["tile_x"] = str(render.tile_x)
        pref_dict["tile_y"] =str(render.tile_y)
        pref_dict["progressive"] = str(cycles.use_progressive_refine)
        pref_dict["spatial_splits"] = str(cycles.debug_use_spatial_splits)
        pref_dict["hair_bvh"] = str(cycles.debug_use_hair_bvh)
        pref_dict["bvh_step"] = str(cycles.debug_bvh_time_steps)
        performance_xml = ET.SubElement(render_xml, "performance", pref_dict)
        # dnoising
        '''denois_xml = ET.SubElement(render_xml, "denoising", {"use_denoising": str(scene.use_denoising)})
        if scene.use_denoising:
            prop_radius = ET.SubElement(denois_xml, "property", {"radius": str(scene.denoising_radius)})
            prop_strength = ET.SubElement(denois_xml, "property", {"strength": float_to_str(scene.denoising_strength)})
            prop_feature_strength = ET.SubElement(denois_xml, "property", {"feature_strength": float_to_str(scene.denoising_feature_strength)})
            prop_relative = ET.SubElement(denois_xml, "property", {"relative_filter": str(scene.denoising_relative_pca)})
            prop_diffuse = ET.SubElement(denois_xml, "property", {"diffuse_direct": str(scene.denoising_diffuse_direct), "diffuse_indirect": str(scene.denoising_diffuse_indirect)})
            prop_glossy = ET.SubElement(denois_xml, "property", {"glossy_direct": str(scene.denoising_glossy_direct), "glossy_indirect": str(scene.denoising_glossy_indirect)})
            prop_transmission = ET.SubElement(denois_xml, "property", {"transmission_direct": str(scene.denoising_transmission_direct), "transmission_indirect": str(scene.denoising_transmission_indirect)})
            prop_subsurface = ET.SubElement(denois_xml, "property", {"subsurface_direct": str(scene.denoising_subsurface_direct), "subsurface_indirect": str(scene.denoising_subsurface_indirect)})'''
        # simpify
        simpl_dict = {}
        simpl_dict["use_simplify"] = str(render.use_simplify)
        if render.use_simplify:
            simpl_dict["camera_cull"] = str(cycles.use_camera_cull)
            simpl_dict["distance_cull"] = str(cycles.use_distance_cull)
            simpl_dict["camera_cull_margin"] = float_to_str(cycles.camera_cull_margin)
            simpl_dict["distance_cull_margin"] = float_to_str(cycles.distance_cull_margin)
            simpl_dict["ao_bounces"] = str(cycles.ao_bounces_render)
        simplify_xml = ET.SubElement(render_xml, "simplify", simpl_dict)


'''def export_geo_pickle(mesh, item_name, ges_path):
    dir_path = os.path.split(ges_path)[0] + "\\" + os.path.splitext(os.path.basename(ges_path))[0] + "_meshes"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    geo_path = dir_path + "\\" + item_name + ".geo"
    new_mesh = mesh.to_mesh(bpy.context.scene, True, "RENDER")
    p_mesh = pmd.PolymeshDescription(mesh.name)
    p_mesh.add_vertices([v.co for v in new_mesh.vertices], [v.normal for v in new_mesh.vertices])
    for bl_polygon in new_mesh.polygons:
        p_mesh.add_polygon([v.numerator for v in bl_polygon.vertices], bl_polygon.normal)
    # p_mesh.add_uvs(new_mesh.uv_layers)
    for uv_layer in new_mesh.uv_layers:
        uv_name = uv_layer.name
        uv_data = []
        for d in uv_layer.data:
            d_uv = d.uv
            uv_data.append(d_uv[0])
            uv_data.append(d_uv[1])
        p_mesh.add_uv(uv_data, uv_name)
    if p_mesh.get_vertex_count() > 0 and p_mesh.get_polygons_count() > 0:
        with open(geo_path, "wb") as file:
            pickle.dump(p_mesh, file, protocol=2)
        bpy.data.meshes.remove(new_mesh)
        return geo_path
    else:
        bpy.data.meshes.remove(new_mesh)
        return None'''


def export_geo(original_mesh, item_name, ges_path):
    dir_path = os.path.split(ges_path)[0] + "\\" + os.path.splitext(os.path.basename(ges_path))[0] + "_meshes"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    geo_path = dir_path + "\\" + item_name + ".geo"
    mesh = original_mesh.to_mesh(bpy.context.depsgraph, True)
    saver = mdsf.MeshSerializer()
    container = saver.create_container()
    point_positions = []  # each position should be tuple (x, y, z)
    polygon_vertices = []  # [(p_index, v_index), ...], where v_index is the index of vertex, pairs enumerate for the first polygon, then for the second and so on
    polygon_normals = []  # [(p_index, c_index, n_x, n_y, n_z), ...], where c_index - index of the polygon corner
    # fill the data arrays
    # 1. point positions
    for v in mesh.vertices:
        point_positions.append((v.co[0], v.co[1], v.co[2]))
    container.add_data(point_positions, data_name="point positions", data_context=mdsf.KEY_CONTEXT_VERTEX, data_type=mdsf.KEY_TYPE_POSITION)
    # 2. polygons
    poly_index = 0
    poly_sizes = []  # contains sizes of polygons
    for poly in mesh.polygons:
        poly_sizes.append(len(poly.vertices))
        for v in poly.vertices:
            polygon_vertices.append((poly_index, v.numerator))
        poly_index += 1
    container.add_data(polygon_vertices, data_name="polygons", data_context=mdsf.KEY_CONTEXT_POLYGON_CORNER, data_type=mdsf.KEY_TYPE_POLYGON_CORNER_INDEX)
    # 3. normals, skip it for now
    if len(polygon_normals) > 0:
        container.add_data(polygon_normals, data_name="normals", data_context=mdsf.KEY_CONTEXT_POLYGON_CORNER, data_type=mdsf.KEY_TYPE_NORMAL)
    # 4. uv coordinates
    for uv_layer in mesh.uv_layers:
        uv_name = uv_layer.name
        uv_data = []  # in the form [(p_index, s_index, u, v), ...]
        current_polygon = 0
        current_sample = 0
        for d in uv_layer.data:
            d_uv = d.uv
            uv_data.append((current_polygon, current_sample, d_uv[0], d_uv[1]))
            current_sample += 1
            if current_sample >= poly_sizes[current_polygon]:
                current_polygon += 1
                current_sample = 0
        container.add_data(uv_data, data_name=uv_name, data_context=mdsf.KEY_CONTEXT_POLYGON_CORNER, data_type=mdsf.KEY_TYPE_UV_COORDINATES)
    # 5. vertex colors
    # clear the mesh
    bpy.data.meshes.remove(mesh)
    # save data
    if len(point_positions) > 0 and len(polygon_vertices) > 0:
        saver.save_to_file(geo_path)
        return geo_path
    else:
        return None


def filter_string(str):
    return "".join([c if c.isalnum() else "_" for c in str])


def form_item_name(name, prefix):
    if len(prefix) == 0:
        return filter_string(name)
    else:
        return prefix + "." + filter_string(name)


def save_ges_item(progress, name_prefix, root, item, is_absolute, ges_path, scene_name, saved_names, dupli_parents, over_matrix=None, only_local=False):
    progress.step()
    should_finish = True
    # if item.name not in saved_names:
    # if item not in saved_names:
    item_name = form_item_name(item.name, name_prefix)
    if True:
        if item.type == "MESH" or item.type == "FONT" or item.type == "CURVE":
            hide_render = item.hide_render
            hide_viewport = item.hide_viewport
            if hide_render is False or hide_viewport is False:
                should_finish = False
                # saved_names.append(item.name)
                saved_names.append(item)
                geo_path = export_geo(item, item_name, ges_path)
                if geo_path is not None:
                    item_xml = ET.SubElement(root, "polymesh", {"name": item.name, "path": ((geo_path if is_absolute else "\\\\" + os.path.relpath(geo_path, os.path.split(ges_path)[0])) if geo_path is not None else "")})
                    export_object(item_xml, item, (hide_render, hide_viewport), over_matrix, only_local)
                else:
                    item_xml = ET.SubElement(root, "null", {"name": item.name})
                    export_null(item_xml, item, (hide_render, hide_viewport), only_local)
        elif item.type == "CAMERA":
            should_finish = False
            # saved_names.append(item.name)
            saved_names.append(item)
            item_xml = ET.SubElement(root, "camera", {"name": item.name, "render": normalize_name(str(bpy.context.scene.render.engine))})
            export_camera(item_xml, item.data, item)
        elif item.type == "LIGHT":
            hide_render = item.hide_render
            hide_viewport = item.hide_viewport
            if hide_render is False or hide_viewport is False:
                should_finish = False
                # saved_names.append(item.name)
                saved_names.append(item)
                item_xml = ET.SubElement(root, "light", {"name": item.name, "render": normalize_name(str(bpy.context.scene.render.engine))})
                export_light(item_xml, item, item.data, (hide_render, hide_viewport), only_local)
        elif item.type == "EMPTY" or item.type == "ARMATURE":
            should_finish = False
            hide_render = item.hide_render
            hide_viewport = item.hide_viewport
            # saved_names.append(item.name)
            saved_names.append(item)
            item_xml = ET.SubElement(root, "null", {"name": item.name})
            export_null(item_xml, item, (hide_render, hide_viewport), only_local)
    else:
        # print("Item " + item.name + " allready exported")
        pass
    if should_finish is False:
        if item in dupli_parents:
            progress.enter_substeps(len(dupli_parents[item]))
            for ch_item, ch_matrix in dupli_parents[item]:
                save_ges_item(progress, item_name, item_xml, ch_item, is_absolute, ges_path, scene_name, saved_names, dupli_parents, ch_matrix, True)
            progress.leave_substeps()
        progress.enter_substeps(len(item.children))
        for ch_item in item.children:
            save_ges_item(progress, item_name, item_xml, ch_item, is_absolute, ges_path, scene_name, saved_names, dupli_parents, None, only_local)
        progress.leave_substeps()


def get_all_objects(selected_set, scene=None):  # get the list of all children objects of selected ones
    to_return = []
    for obj in selected_set:
        to_return.append(obj)
        to_return = to_return + get_all_objects(obj.children, scene)
    return to_return


def get_top_parents(objects):
    to_return = []
    for obj in objects:
        if obj.parent is None:
            to_return.append(obj)
    return to_return


def export_collection(progress, file_path, is_save_textures, is_texture_absolute, obj_collection, selection_collection=False):
    if selection_collection:
        all_selected = get_all_objects(obj_collection)
    else:
        all_selected = obj_collection

    top_parents = get_top_parents(all_selected)
    # next collect all duplies. Form two arrys. The first one is total list of objects. The second one is dictionary from instance to it realizations
    total_list = []
    dupli_parents = {}
    clear_dupli_list = []
    for i, ob_main in enumerate(all_selected):
        if ob_main.parent and ob_main.parent.instance_type in {'VERTS', 'FACES'}:
            continue
        total_list.append(ob_main)
        if ob_main.is_instancer:
            # ob_main.dupli_list_create(bpy.context.scene)
            inst_list = [(dup.instance_object.original, dup.matrix_world.copy())
                            for dup in bpy.context.depsgraph.object_instances
                            if dup.parent and dup.parent.original == ob_main]
            # clear_dupli_list.append(ob_main)
            new_dupli_item = []
            for (dob, dob_matrix) in inst_list:
                if dob not in total_list:
                    total_list.append(dob)
                if dob.parent is None:
                    new_dupli_item.append((dob, dob_matrix))
            dupli_parents[ob_main] = new_dupli_item

    if len(total_list) > 0:
        selected_materials = []
        material_names = []
        light_materials = []
        for obj in total_list:
            if obj.type == "LIGHT":
                light_materials.append(obj.data)
            else:
                obj_materials = obj.material_slots
                for o_mat in obj_materials:
                    if o_mat.material is not None and o_mat.material.node_tree is not None and not (o_mat.name in material_names):
                        selected_materials.append(o_mat.material)
                        material_names.append(o_mat.name)
        # save selected materials
        if len(selected_materials) > 0:
            mat_file_path = conver_path_to_gem(file_path)
            actual_material_export(progress, mat_file_path, is_texture_absolute, is_save_textures, selected_materials)

        # also try to add backgroun node_tree
        if selection_collection is False:
            light_materials.append(bpy.context.scene.world)
        if len(light_materials) > 0:
            lights_file_path = conver_path_to_gem(file_path, True)
            actual_material_export(progress, lights_file_path, is_texture_absolute, is_save_textures, light_materials)
        # next actual objects
        # create the root xml-object
        lib_name = form_library_name(bpy.data.filepath)
        root = ET.Element("scene", {"name": lib_name, "up_axis": "Z", "render": normalize_name(str(bpy.context.scene.render.engine))})
        # next export ges items
        saved_names = []
        progress.enter_substeps(len(top_parents))
        for item in top_parents:
            save_ges_item(progress, "", root, item, is_texture_absolute, file_path, lib_name, saved_names, dupli_parents)
        progress.leave_substeps()
        if selection_collection is False:
            # export background
            export_background(root)
            # export render settings
            export_render_settings(root)
        for ob in clear_dupli_list:
            ob.dupli_list_clear()
        # write the file
        indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(file_path)


def export_selected_objects(progress, file_path, is_save_textures, is_texture_absolute):
    export_collection(progress, file_path, is_save_textures, is_texture_absolute, bpy.context.selected_objects, True)


def export_all_scene(progress, file_path, is_save_textures, is_texture_absolute):
    export_collection(progress, file_path, is_save_textures, is_texture_absolute, bpy.context.scene.objects)


def save(operator, context, **kwargs):
    with ProgressReport(context.window_manager) as progress:
        progress.enter_substeps(1)
        file_path = kwargs["filepath"]
        mode = kwargs["mode"]
        texture_path = kwargs["texture_path_mode"]
        is_copy_textures = kwargs["is_copy_textures"]
        if mode == "ALL_SCENE":
            file_path = conver_path_to_ges(file_path)
            export_all_scene(progress, file_path, is_copy_textures, texture_path == "ABSOLUTE")
        elif mode == "SELECTED_OBJECTS":
            file_path = conver_path_to_ges(file_path)
            export_selected_objects(progress, file_path, is_copy_textures, texture_path == "ABSOLUTE")
        elif mode == "ALL_MATERIALS":
            file_path = conver_path_to_gem(file_path)
            export_materials(progress, file_path, is_copy_textures, texture_path == "ABSOLUTE")
        elif mode == "SELECTED_MATERIAL":
            file_path = conver_path_to_gem(file_path)
            export_materials(progress, file_path, is_copy_textures, texture_path == "ABSOLUTE", True)
        progress.leave_substeps()

    return {'FINISHED'}


def test_function():
    print("345")
