# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

# <pep8 compliant>

bl_info = {
    "name": "IES to Cycles",
    "author": "Lockal S.",
    "version": (0, 8),
    "blender": (2, 6, 7),
    "location": "File > Import > IES Lamp Data (.ies)",
    "description": "Import IES lamp data to cycles",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
import bmesh
import mathutils
import os

from math import pi
from operator import add, truediv
      
def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    return x

# Temperature to RGB
# OSL version:
# http://blenderartists.org/forum/showthread.php?270332&p=2268693#post2268693
def t2rgb(t):
    if t <= 6500:
        a = [0, -2902.1955373783176, -8257.7997278925690]
        b = [0, 1669.5803561666639, 2575.2827530017594]
        c = [1, 1.3302673723350029, 1.8993753891711275]

    else:
        a = [1745.0425298314172, 1216.6168361476490, -8257.7997278925690]
        b = [-2666.3474220535695, -2173.1012343082230, 2575.2827530017594]
        c = [0.55995389139931482, 0.70381203140554553, 1.8993753891711275]

    color = map(add, map(truediv, a, map(add, [t] * 3, b)), c)
    return [max(0, min(x, 1)) for x in color] + [1]


def simple_interp(k, x, y):
    for i in range(len(x)):
        if k == x[i]:
            return y[i]
        elif k < x[i]:
            return y[i] + (k - x[i]) * (y[i - 1] - y[i]) / (x[i - 1] - x[i])


def gen_rig_object(name, data):
    mesh = bpy.data.meshes.new('lamp rig ' + name)
    bm = bmesh.new()
    
    scale = 1.0
    
    first = bm.verts.new((0, 0, data[0][0] * scale))
    last = bm.verts.new((0, 0, -data[0][-1] * scale))
    
    v_angles = [pi * (i+1)/(len(data[0])-1) for i in range(len(data[0])-2)]
    h_angles = [2 * pi * i/(len(data)) for i in range(len(data))]

    for h_angle, angle_data in zip(h_angles, data):
        verts = []
        for v_angle, value in zip(v_angles, angle_data[1:-1]):
            vec = mathutils.Vector((0.0, 0.0, 1.0))
            vec.rotate(mathutils.Euler((v_angle, 0.0, h_angle - pi / 2), 'XYZ'))
            verts.append(bm.verts.new((vec * value * scale)))
    
        for i in range(len(verts)-1):
            bm.edges.new((verts[i], verts[i+1]))
    
        bm.edges.new((first, verts[0]))
        bm.edges.new((last, verts[-1]))
    
    bm.to_mesh(mesh)
    mesh.update()
    
    ob = bpy.data.objects.new('lamp rig ' + name, mesh)
    ob.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(ob)
    
    return ob.name


def reinterpolate_line(x_data, y_data, new_width):
    new_x_data = [i/(new_width-1) for i in range(new_width)]
    new_y_data = [simple_interp(k, x_data, y_data) for k in new_x_data]
    return new_y_data


# default number of vertices for vertical and horizontal directions in rig
rig_v = {'TYPE90': 10, 'TYPE180': 20}
rig_h = {'TYPE90': 16, 'TYPE180': 16}


def gen_vcurves_rig(name, x_data, y_data, cone_type):
    new_data = [reinterpolate_line(x_data, y_data, rig_v[cone_type])] * rig_h[cone_type]
    return gen_rig_object(name, new_data)


def reinterpolate_2d(data, size, h_type):
    if h_type == 'TYPE90' or h_type == 'TYPE180':
        data += list(reversed(data))[1:]
    
    if h_type == 'TYPE90':
        data += list(reversed(data))[1:]
    
    if len(data) == 1:
        data = [data[0]] * 2
    
    for length in size:
        x_data = [i / (len(data[0]) - 1) for i in range(len(data[0]))]
        for i in range(len(data)):
            data[i] = reinterpolate_line(x_data, data[i], length)
        data = list(zip(*data))

    return data


def gen_2d_rig(name, data, cone_type, h_type):
    # reinterpolate a deep copy of data
    new_size = [rig_v[cone_type], rig_h[cone_type]]
    new_data = reinterpolate_2d(data[:], new_size, h_type)
    return gen_rig_object(name, new_data)


def read_lamp_data(log, filename, generate_rig, multiplier, image_format, color_temperature):
    # log({'INFO'}, 'Start IES import')
    rig_name = ''
    
    version_table = {
        'IESNA:LM-63-1986': 1986,
        'IESNA:LM-63-1991': 1991,
        'IESNA91': 1991,
        'IESNA:LM-63-1995': 1995,
        'IESNA:LM-63-2002': 2002,
    }
    
    name = os.path.splitext(os.path.split(filename)[1])[0]

    file = open(filename, 'rt', encoding='cp1252')
    content = file.read()
    file.close()
    s, content = content.split('\n', 1)

    if s in version_table:
        version = version_table[s]
    else:
        log({'INFO'}, "IES file does not specify any version")
        version = None

    keywords = dict()

    while content and not content.startswith('TILT='):
        s, content = content.split('\n', 1)

        if s.startswith('['):
            endbracket = s.find(']')
            if endbracket != -1:
                keywords[s[1:endbracket]] = s[endbracket + 1:].strip()

    s, content = content.split('\n', 1)

    if not s.startswith('TILT'):
        log({'ERROR'}, "TILT keyword not found, check your IES file")
        return {'CANCELLED'}

    # fight against ill-formed files
    file_data = content.replace(',', ' ').split()

    lamps_num = int(file_data[0])
    if lamps_num != 1:
        log({'INFO'}, "Only 1 lamp is supported, %d in IES file" % lamps_num)

    lumens_per_lamp = float(file_data[1])
    candela_mult = float(file_data[2])

    v_angles_num = int(file_data[3])
    h_angles_num = int(file_data[4])
    if not v_angles_num or not h_angles_num:
        log({'ERROR'}, "TILT keyword not found, check your IES file")
        return {'CANCELLED'}

    photometric_type = int(file_data[5])

    units_type = int(file_data[6])
    if units_type not in [1, 2]:
        log({'INFO'}, "Units type should be either 1 (feet) or 2 (meters)")

    width, length, height = map(float, file_data[7:10])

    ballast_factor = float(file_data[10])

    future_use = float(file_data[11])
    if future_use != 1.0:
        log({'INFO'}, "Invalid future use field")

    input_watts = float(file_data[12])

    v_angs = [float(s) for s in file_data[13:13 + v_angles_num]]
    h_angs = [float(s) for s in file_data[13 + v_angles_num:
                                          13 + v_angles_num + h_angles_num]]

    if v_angs[0] == 0 and v_angs[-1] == 90:
        lamp_cone_type = 'TYPE90'
    elif v_angs[0] == 0 and v_angs[-1] == 180:
        lamp_cone_type = 'TYPE180'
    else:
        log({'INFO'}, "Lamps with vertical angles (%d-%d) are not supported" %
                       (v_angs[0], v_angs[-1]))
        lamp_cone_type = 'TYPE180'


    if len(h_angs) == 1 or abs(h_angs[0] - h_angs[-1]) == 360:
        lamp_h_type = 'TYPE360'
    elif abs(h_angs[0] - h_angs[-1]) == 180:
        lamp_h_type = 'TYPE180'
    elif abs(h_angs[0] - h_angs[-1]) == 90:
        lamp_h_type = 'TYPE90'
    else:
        log({'INFO'}, "Lamps with horizontal angles (%d-%d) are not supported" %
                       (h_angs[0], h_angs[-1]))
        lamp_h_type = 'TYPE360'
        
    # print(h_angs, lamp_h_type)

    # read candela values
    offset = 13 + len(v_angs) + len(h_angs)
    candela_num = len(v_angs) * len(h_angs)
    candela_values = [float(s) for s in file_data[offset:offset + candela_num]]

    # reshape 1d array to 2d array
    candela_2d = list(zip(*[iter(candela_values)] * len(v_angs)))

    if image_format == 'VCURVES':
        # scale vertical angles to [0, 1] range
        x_rig_data = [x / v_angs[-1] for x in v_angs]
        x_data = [0.5 + 0.5 * x for x in x_rig_data]
        
        # approximate multidimentional lamp data to single dimention
        y_data = [sum(x) / len(x) for x in zip(*candela_2d)]
        y_data_max = max(y_data)
        
        intensity = max(500, min(y_data_max * multiplier * candela_mult, 5000))
        
        lamp_rig_y_data = [y / y_data_max for y in y_data]
        lamp_y_data = [0.5 + 0.5 * y for y in lamp_rig_y_data]
        
        lamp_data = list(zip(x_data, lamp_y_data))
        if generate_rig:
            rig_name = gen_vcurves_rig(name, x_rig_data, lamp_rig_y_data, lamp_cone_type)

        return add_img(name=name,
                       intensity=intensity,
                       lamp_cone_type=lamp_cone_type,
                       lamp_h_type=lamp_h_type,
                       image_format=image_format,
                       color_temperature=color_temperature,
                       lamp_data=lamp_data,
                       rig_name=rig_name)

    # check if angular offsets are the same
    v_d = [v_angs[i] - v_angs[i - 1] for i in range(1, len(v_angs))]
    h_d = [h_angs[i] - h_angs[i - 1] for i in range(1, len(h_angs))]

    v_same = all(abs(v_d[i] - v_d[i - 1]) < 0.001 for i in range(1, len(v_d)))
    h_same = all(abs(h_d[i] - h_d[i - 1]) < 0.001 for i in range(1, len(h_d)))

    if not v_same:
        vmin, vmax = v_angs[0], v_angs[-1]
        divisions = int((vmax - vmin) / max(1, min(v_d)))
        step = (vmax - vmin) / divisions

        # Approximating non-uniform vertical angles with step = step
        new_v_angs = [vmin + i * step for i in range(divisions + 1)]
        new_candela_2d = [[simple_interp(ang, v_angs, line)
                           for ang in new_v_angs] for line in candela_2d]
        # print(candela_2d)
        # print(new_candela_2d)
        v_angs = new_v_angs
        candela_2d = new_candela_2d

    if not h_same:
        log({'INFO'}, "Different offsets for horizontal angles!")
        
    # normalize candela values
    maxval = max([max(row) for row in candela_2d])
    candela_2d = [[val / maxval for val in row] for row in candela_2d]
    
    # generate rig object
    if generate_rig:
        rig_name = gen_2d_rig(name, candela_2d, lamp_cone_type, lamp_h_type)

    # add extra left and right rows to bypass cycles repeat of uv coordinates
    candela_2d = [[line[0]] + list(line) + [line[-1]] for line in candela_2d]
    
    if len(candela_2d) > 1:
        candela_2d = [candela_2d[0]] + candela_2d + [candela_2d[-1]]

    # flatten 2d array to 1d
    candela_values = [y for x in candela_2d for y in x]
    
    intensity = max(500, min(maxval * multiplier * candela_mult, 5000))

    if image_format == 'PNG':
        float_buffer = False
        filepath = '//' + name + '.png'
    else:
        float_buffer = True
        filepath = '//' + name + '.exr'

    img = bpy.data.images.new(name, len(candela_2d[0]), len(candela_2d),
                              float_buffer=float_buffer)

    for i, val in enumerate(candela_values):
        img.pixels[4 * i] = img.pixels[4 * i + 1] = img.pixels[4 * i + 2] = val

    bpy.ops.import_lamp.gen_exr('INVOKE_DEFAULT',
                                image_name=img.name,
                                intensity=intensity,
                                lamp_cone_type=lamp_cone_type,
                                lamp_h_type=lamp_h_type,
                                image_format=image_format,
                                color_temperature=color_temperature,
                                filepath=filepath,
                                rig_name=rig_name)

    return {'FINISHED'}


def scale_coords(nt, sock_in, sock_out, size):
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    nt.links.new(add.inputs[0], sock_in)
    add.inputs[1].default_value = 1.0 / (size - 2)

    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    nt.links.new(mul.inputs[0], add.outputs[0])
    mul.inputs[1].default_value = (size - 2.0) / size

    nt.links.new(sock_out, mul.outputs[0])


def add_h_angles(nt, x, y, out, lamp_h_type):
    na = nt.nodes.new('ShaderNodeMath')
    na.operation = 'MULTIPLY'
    nt.links.new(na.inputs[0], x)
    nt.links.new(na.inputs[1], x)

    nb = nt.nodes.new('ShaderNodeMath')
    nb.operation = 'MULTIPLY'
    nt.links.new(nb.inputs[0], y)
    nt.links.new(nb.inputs[1], y)

    nc = nt.nodes.new('ShaderNodeMath')
    nc.operation = 'ADD'
    nt.links.new(nc.inputs[0], na.outputs[0])
    nt.links.new(nc.inputs[1], nb.outputs[0])

    nd = nt.nodes.new('ShaderNodeMath')
    nd.operation = 'POWER'
    nt.links.new(nd.inputs[0], nc.outputs[0])
    nd.inputs[1].default_value = 0.5

    nf = nt.nodes.new('ShaderNodeMath')
    nf.operation = 'ADD'
    nt.links.new(nf.inputs[0], x)
    nt.links.new(nf.inputs[1], nd.outputs[0])

    ng = nt.nodes.new('ShaderNodeMath')
    ng.operation = 'DIVIDE'
    nt.links.new(ng.inputs[0], y)
    nt.links.new(ng.inputs[1], nf.outputs[0])

    nh = nt.nodes.new('ShaderNodeMath')
    nh.operation = 'ARCTANGENT'
    nt.links.new(nh.inputs[0], ng.outputs[0])

    nj = nt.nodes.new('ShaderNodeMath')
    nj.operation = 'DIVIDE'
    nt.links.new(nj.inputs[0], nh.outputs[0])

    # add abs() cascade for lamps with horizontal angles from 0 to 180
    if lamp_h_type == 'TYPE90' or lamp_h_type == 'TYPE180':
        repeat_times = 4 if lamp_h_type == 'TYPE90' else 2
        nj.inputs[1].default_value = pi / repeat_times
    
        nk = nt.nodes.new('ShaderNodeMath')
        nk.operation = 'MULTIPLY'
        nt.links.new(nj.outputs[0], nk.inputs[0])
        nk.inputs[1].default_value = -1.0
        
        nl = nt.nodes.new('ShaderNodeMath')
        nl.operation = 'MAXIMUM'
        nt.links.new(nj.outputs[0], nl.inputs[0])
        nt.links.new(nk.outputs[0], nl.inputs[1])
        nt.links.new(nl.outputs[0], out)
    else:
        nj.inputs[1].default_value = pi
        nt.links.new(nj.outputs[0], out)


def add_uv_mapping_node(nt, input, output, img_size):
    nt_map = nt.nodes.new('ShaderNodeMapping')
    
    for i in range(2):
        nt_map.translation[i] = 1 / (img_size[i] - 2)
        nt_map.scale[i] = (img_size[i] - 2) / img_size[i]
    
    nt.links.new(nt_map.inputs[0], input)
    nt.links.new(nt_map.outputs[0], output)


def add_img(name, intensity, lamp_cone_type, lamp_h_type, image_format, 
            color_temperature, filepath=None, lamp_data=None, rig_name=None):
    if image_format != 'VCURVES':
        img = bpy.data.images[name]
        img.filepath_raw = filepath
        img.file_format = image_format
        img.save()

    nt = bpy.data.node_groups.new("Lamp " + name, 'ShaderNodeTree')
    
    nt.inputs.new('NodeSocketVector', "Vector")
    nt.inputs.new('NodeSocketFloat', "Strength")
    nt.inputs.new('NodeSocketFloat', "Size")
    
    nt.outputs.new('NodeSocketFloat', "Intensity")
    
    nt_input = nt.nodes.new('NodeGroupInput')
    nt_output = nt.nodes.new('NodeGroupOutput')
    
    n0 = nt.nodes.new('ShaderNodeSeparateRGB')

    ne = nt.nodes.new('ShaderNodeMath')
    ne.operation = 'ARCCOSINE'
    nt.links.new(ne.inputs[0], n0.outputs[2])

    ni = nt.nodes.new('ShaderNodeMath')
    ni.operation = 'DIVIDE'
    nt.links.new(ni.inputs[0], ne.outputs[0])

    if lamp_cone_type == 'TYPE180':
        ni.inputs[1].default_value = pi
    else:  # TYPE90:
        ni.inputs[1].default_value = pi / 2

    if image_format == 'VCURVES':
        nt_data = nt.nodes.new('ShaderNodeVectorCurve')
        nt.links.new(nt_data.inputs[1], ni.outputs[0])
        for x, y in lamp_data[:-1]:
            pt = nt_data.mapping.curves[0].points.new(x, y)
            pt.handle_type = 'VECTOR'

        if lamp_cone_type == 'TYPE180':
            nt_data.mapping.curves[0].points[-1].location[1] = lamp_data[-1][1]
            nt_data.mapping.curves[0].points[-1].handle_type = 'VECTOR'
        else:
            pt = nt_data.mapping.curves[0].points.new(0.9999, lamp_data[-1][1])
            pt.handle_type = 'VECTOR'
            nt_data.mapping.curves[0].points[-1].location[1] = 0.5  # no light
            nt_data.mapping.curves[0].points[-1].handle_type = 'VECTOR'

        nt_data_sep = nt.nodes.new('ShaderNodeSeparateRGB')
        nt.links.new(nt_data_sep.inputs[0], nt_data.outputs[0])
        nt_data_out = nt_data_sep.outputs[0]
    else:  # image-based
        nt_combine = nt.nodes.new('ShaderNodeCombineRGB')
        
        # use (x+a)*b cascade for Nx1 images
        if img.size[1] == 1:
            scale_coords(nt, ni.outputs[0], nt_combine.inputs[0], img.size[0])
        else:
            nt.links.new(ni.outputs[0], nt_combine.inputs[0])
        
        if img.size[1] > 1:
            add_h_angles(nt, n0.outputs[0], n0.outputs[1], nt_combine.inputs[1], lamp_h_type)
        
        nt_data = nt.nodes.new('ShaderNodeTexImage')
        nt_data.image = img
        nt_data.color_space = 'NONE'
        
        if img.size[1] > 1:
            add_uv_mapping_node(nt, nt_combine.outputs[0], nt_data.inputs[0], img.size)
        else:
            nt.links.new(nt_combine.outputs[0], nt_data.inputs[0])
        
        nt_data_out = nt_data.outputs[0]

    nt.links.new(n0.inputs[0], nt_input.outputs[0])
    
    nt_intensity = nt.nodes.new('ShaderNodeMath')
    nt_intensity.operation = 'MULTIPLY'
    nt.links.new(nt_input.outputs[1], nt_intensity.inputs[0])
    nt.links.new(nt_input.outputs[2], nt_intensity.inputs[1])

    nmult = nt.nodes.new('ShaderNodeMath')
    nmult.operation = 'MULTIPLY'
    nt.links.new(nt_intensity.outputs[0], nmult.inputs[0])

    nt.links.new(nt_output.inputs[0], nmult.outputs[0])

    if lamp_cone_type == 'TYPE180' or image_format == 'VCURVES':
        nt.links.new(nmult.inputs[1], nt_data_out)
    else:  # TYPE90
        nlt = nt.nodes.new('ShaderNodeMath')
        nlt.operation = 'LESS_THAN'
        nt.links.new(nlt.inputs[0], ni.outputs[0])
        nlt.inputs[1].default_value = 1.0

        nif = nt.nodes.new('ShaderNodeMath')
        nif.operation = 'MULTIPLY'
        nt.links.new(nif.inputs[0], nt_data_out)
        nt.links.new(nif.inputs[1], nlt.outputs[0])

        nt.links.new(nmult.inputs[1], nif.outputs[0])

    lampdata = bpy.data.lamps.new('Lamp ' + name, 'POINT')
    lampdata.shadow_soft_size = 0.01
    lampdata.use_nodes = True
    lnt = lampdata.node_tree

    lnt_grp = lnt.nodes.new('ShaderNodeGroup')
    lnt_grp.node_tree = nt
    
    
    for node in lnt.nodes:
        if node.bl_idname == 'ShaderNodeEmission':
            emission_node = node
            break
    
    emission_node.inputs[0].default_value = t2rgb(color_temperature)
    lnt.links.new(emission_node.inputs[1], lnt_grp.outputs[0])
    
    lnt_grp.inputs[1].default_value = intensity
    lnt_grp.inputs[2].default_value = 1.0

    lnt_map = lnt.nodes.new('ShaderNodeMapping')
    lnt_map.rotation[0] = pi
    lnt.links.new(lnt_grp.inputs[0], lnt_map.outputs[0])
    
    if rig_name:
        lampdata["rigged_ies"] = True
        rig_object = bpy.data.objects[rig_name]
        
        # add RGBA color drivers
        fcurves = lnt.driver_add(emission_node.inputs[0].path_from_id("default_value"))
        for i, fcurve in enumerate(fcurves):
            var = fcurve.driver.variables.new()
            var.targets[0].id = rig_object
            var.targets[0].data_path = '["ies_settings"]["color"][%d]' % i
            fcurve.driver.type = 'SUM'
        
        rig_object.ies_settings.color = t2rgb(color_temperature)[0:3]
        
        # add factor -> intensity driver
        strength_fc = lnt.driver_add(lnt_grp.inputs[1].path_from_id("default_value"))
        strength_fc.driver.type = 'SUM'
        strength_var = strength_fc.driver.variables.new()
        strength_var.targets[0].id = rig_object
        strength_var.targets[0].data_path = '["ies_settings"]["strength_mult"]'
        
        # add size -> intensity driver
        strength_fc = lnt.driver_add(lnt_grp.inputs[2].path_from_id("default_value"))
        strength_fc.driver.type = 'SUM'
        strength_var = strength_fc.driver.variables.new()
        strength_var.type = 'TRANSFORMS'
        strength_var.targets[0].id = rig_object
        strength_var.targets[0].transform_type = 'SCALE_Z'
        
        # set and recalculate intensity
        rig_object.ies_settings.strength_mult = intensity
        
        # add rotation drivers
        fcurves = lnt.driver_add(lnt_map.path_from_id('rotation'))
        fc_types = ['ROT_X', 'ROT_Y', 'ROT_Z']
        fc_coeffs = [[0.0, 1.0], [0.0, 1.0], [pi, -1.0]]
        
        for fcurve, trans_type, coeffs in zip(fcurves, fc_types, fc_coeffs):
            v = fcurve.driver.variables.new()
            v.type = 'TRANSFORMS'
            v.targets[0].id = rig_object
            v.targets[0].transform_type = trans_type
            fcurve.driver.type = 'SUM'
            fcurve.modifiers[0].coefficients = coeffs
            
        # recalculate driver data by changing rig angle
        rig_object.rotation_euler.x = pi
        

    lnt_geo = lnt.nodes.new('ShaderNodeNewGeometry')
    lnt.links.new(lnt_map.inputs[0], lnt_geo.outputs[1])

    lamp = bpy.data.objects.new("Lamp " + name, lampdata)
    
    bpy.context.scene.objects.link(lamp)
    
    for ob in bpy.data.objects:
        ob.select = False

    lamp.select = True

    if rig_name:
        rig_object = bpy.data.objects[rig_name]
        lamp.parent = rig_object
        lamp.lock_location[:] = [True] * 3
        lamp.lock_rotation[:] = [True] * 3
        lamp.lock_scale[:] = [True] * 3
        # lamp.hide_select = True
        rig_object.select = True
        bpy.context.scene.objects.active = rig_object
    else:
        lamp.location = bpy.context.scene.cursor_location
        bpy.context.scene.objects.active = lamp

    return {'FINISHED'}


from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, FloatProperty, EnumProperty, IntProperty, BoolProperty
from bpy.types import Operator

format_prop_items = (
    ('VCURVES', "Vector Curves", "Save lamp data in Vector Curves node"),
    ('OPEN_EXR', "EXR", "Save images to EXR format (up to 5 textures)"),
    ('PNG', "PNG", "Save images to PNG format")
)

format_prop_default = 'VCURVES'
# format_prop_default = 'PNG'


temperature_prop_items = (
    ('T1700', "1700K: Match flame", "Match flame"),
    ('T1850', "1850K: Candle light", "Candle light or sunlight at sunrise or sunset"),
    ('T2700', "2700K: Very Warm White", "Similar light to \"normal\" incandescent bulbs, giving a warm \"cosy\" feel"),
    ('T3000', "3000K: Warm White", "The colour of most halogen lamps. Appears slightly \"whiter\" than ordinary incandescent lamps"),
    ('T3200', "3200K: Studio Lamp", "Studio Lamps/Photofloods"),
    ('T3500', "3500K: White", "The standard colour for many fluorescent and compact fluorescent tubes"),
    ('T4000', "4000K: Cool White", "Gives a more clinical or \"high tech\" feel"),
    ('T4100', "4100K: Moonlight", "Moonlight, xenon arc lamp"),
    ('T5000', "5000K: Horizon daylight", "Horizon daylight, tubular fluorescent lamps or Cool White/Daylight compact fluorescent lamps (CFL)"),
    ('T5600', "5600K: Nominal Sunlight", "Nominal Sunlight, mid day during mid summer"),
    ('T6000', "6000K: Daylight", "Fluorescent or compact fluorescent lamps simulating natural daylight"),
    ('T6500', "6500K: Cool Daylight", "Extremely \"white\" light used in specialist daylight lamps"),
    ('T7000', "7000K: LCD/CRT screen", "LCD or CRT screen"),
    ('T8000', "8000K: LCD/CRT screen", "LCD or CRT screen"),
    ('T9000', "9000K: LCD/CRT screen", "LCD or CRT screen"),
    ('T20000', "20000K: Open Sky", "Clear blue poleward sky")
)

temperature_prop_default = 'T6500'

class ImportIES(Operator, ImportHelper):
    """Import IES lamp data and generate a node group for cycles"""
    bl_idname = "import_lamp.ies"
    bl_label = "Import IES to Cycles"

    filter_glob = StringProperty(default="*.ies", options={'HIDDEN'})

    generate_rig = BoolProperty(
        name="Generate Rig",
        description="Generate rig for lamp",
        default=True,
    )
    
    lamp_strength = FloatProperty(
        name="Strength",
        description="Multiplier for lamp strength",
        default=1.0,
    )

    image_format = EnumProperty(
        name="Convert to",
        items=format_prop_items,
        default=format_prop_default,
    )

    color_temperature = EnumProperty(
        name="Color Temperature",
        description="Color temperature of lamp",
        items=temperature_prop_items,
        default=temperature_prop_default,
    )

    def execute(self, context):
        return read_lamp_data(self.report, self.filepath, self.generate_rig, 
                              self.lamp_strength, self.image_format,
                              int(self.color_temperature[1:]))


class ExportLampEXR(Operator, ExportHelper):
    """Export IES lamp data in EXR format"""
    bl_idname = "import_lamp.gen_exr"
    bl_label = "Export lamp to image"

    image_name = StringProperty(options={'HIDDEN'})
    intensity = FloatProperty(options={'HIDDEN'})
    lamp_cone_type = EnumProperty(
        items=(('TYPE90', "0-90", ""),
               ('TYPE180', "0-180", "")),
        options={'HIDDEN'}
    )
    lamp_h_type = EnumProperty(
        items=(('TYPE90', "0-90", ""),
               ('TYPE180', "0-180", ""),
               ('TYPE360', "0-360", "")),
        options={'HIDDEN'}
    )
    image_format = EnumProperty(items=format_prop_items, options={'HIDDEN'})
    color_temperature = IntProperty(options={'HIDDEN'})
    rig_name = StringProperty(options={'HIDDEN'})
    use_filter_image = True

    def execute(self, context):
        return add_img(name=self.image_name,
                       intensity=self.intensity,
                       lamp_cone_type=self.lamp_cone_type,
                       lamp_h_type=self.lamp_h_type,
                       image_format=self.image_format,
                       color_temperature=self.color_temperature,
                       filepath=self.filepath,
                       rig_name=self.rig_name)

    def invoke(self, context, event):
        if self.image_format == 'PNG':
            self.filename_ext = ".png"
        else:
            self.filename_ext = ".exr"

        return ExportHelper.invoke(self, context, event)


def menu_func(self, context):
    self.layout.operator(ImportIES.bl_idname, text="IES Lamp Data (.ies)")


# Rig panel and data
class IesRigSettings(bpy.types.PropertyGroup):
    strength_mult = bpy.props.FloatProperty(name="Strength Multiplier", 
                                            default=1, min=0, max=1e4)
    color = bpy.props.FloatVectorProperty(name="Color", subtype="COLOR")


class IesRigPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Lamp Properties"
    
    @classmethod
    def poll(self, context):
        try:
            return context.active_object.children[0].data['rigged_ies']
        except:
            return False
        
    def draw(self, context):
        ob = context.active_object
        self.layout.prop(ob.ies_settings, "strength_mult")
        self.layout.prop(ob.ies_settings, "color")


registered_classes = [IesRigSettings, IesRigPanel, ImportIES, ExportLampEXR]


def register():
    for cls in registered_classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.ies_settings = bpy.props.PointerProperty(type=IesRigSettings)
    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)

    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.import_lamp.ies('INVOKE_DEFAULT')