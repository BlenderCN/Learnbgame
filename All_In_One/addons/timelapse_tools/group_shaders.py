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
if "bpy" in locals():
    import importlib
    importlib.reload(node_groups)
else:
    from . import node_groups

import bpy

'''
XXX handle zero distance case, esp at limits of color ramps
'''

OFFSET_X = 200
OFFSET_X_SMALL = 20
OFFSET_X_LARGE = 500
OFFSET_Y = 400
VECTOR_SOCKETS = ('RGBA')
SCALAR_SOCKETS = ('VALUE')


def make_group(nodes, type):
    ''' avoid replicating two lines '''
    grp = nodes.new(type="ShaderNodeGroup")
    grp.node_tree = type
    return grp


def make_node_group(grp_data):
    ''' Make a group that doesn't yet exist '''
    grp = bpy.data.node_groups.new(grp_data['group'], 'ShaderNodeTree')
    for node_data in grp_data['nodes']:
        node = grp.nodes.new(node_data['bl_idname'])
        for prop in node_data:
            if not prop in ('node_tree', 'bl_idname'):
                setattr(node, prop, node_data[prop])
        if 'node_tree' in node_data:
            sub_grp = get_node_group(node_data['node_tree'])
            node.node_tree = sub_grp
    links = grp_data['links'].copy() # we're going to remove stuff
    input_links = []
    input_orders = []
    output_links = []
    output_orders = []
    dead_links = []
    for link in links:
        if (
                link['from_node'] == 'Group Input' and
                link['from_order'] not in input_orders):
            input_links.append(link)
            input_orders.append(link['from_order'])
            dead_links.append(link)
        if (
                link['to_node'] == 'Group Output' and
                link['to_order'] not in output_orders):
            output_links.append(link)
            output_orders.append(link['to_order'])
            dead_links.append(link)
    for link in dead_links:
        links.remove(link)
    input_links.sort(key=lambda x: x['from_order'])
    output_links.sort(key=lambda x: x['to_order'])
    inputs = {}
    for idx, grp_input in enumerate(grp_data['inputs']):
        inputs[grp_input[0]] = inp = grp.nodes['Group Input'].outputs.new(
            grp_input[1], grp_input[0])
        to_node = input_links[idx]['to_node']
        socket_order = input_links[idx]['to_order']
        grp.links.new(
            inp,
            grp.nodes[to_node].inputs[socket_order])
        grp.inputs[idx].name = grp_input[0]
    outputs = {}
    for idx, grp_output in enumerate(grp_data['outputs']):
        outputs[grp_output[0]] = outp = grp.nodes['Group Output'].inputs.new(
            grp_output[1], grp_output[0])
        from_node = output_links[idx]['from_node']
        socket_order = output_links[idx]['to_order']
        grp.links.new(
            grp.nodes[from_node].outputs[socket_order],
            outp)
        grp.outputs[idx].name = grp_output[0]
    for link_data in links:
        if link_data['to_node'] == 'Group Output' and False:
            to_socket = outputs[link_data['to_socket']]
        else:
            to_socket = grp.nodes[
                link_data['to_node']].inputs[link_data['to_order']]
        if link_data['from_node'] == 'Group Input' and False:
            from_socket = inputs[link_data['from_socket']]
        else:
            from_socket = grp.nodes[
                link_data['from_node']].outputs[link_data['from_order']]
        grp.links.new(from_socket, to_socket)

    for default in grp_data['defaults']:
        node = grp.nodes[default]
        input_defaults = grp_data['defaults'][default][0]
        output_defaults = grp_data['defaults'][default][1]
        for idx, value in enumerate(input_defaults):
            node.inputs[idx].default_value = value
        for idx, value in enumerate(output_defaults):
            node.outputs[idx].default_value = value
    grp[grp_data['prop']] = grp_data['prop'] # tag it because names
    return grp


def get_node_group(grp_type):
    ''' Generic group getter '''
    grp_data = node_groups.pre_requisites[grp_type]
    grp_prop = grp_data['prop']
    group =[grp for grp in bpy.data.node_groups if grp_prop in grp.keys()]
    if group:
        return group[0]
    return make_node_group(grp_data)


class AvailableCurves(object):
    ''' Keep track and return curve node/available index '''
    def __init__(self, node_tree):
        self.node_tree = node_tree
        self.nodes = node_tree.nodes
        x_locations = [node.location.x for node in self.nodes if node.select]
        self.x_anchor = sum(x_locations) / max(len(x_locations), 1)
        self.x_anchor -= OFFSET_X_LARGE + OFFSET_X_SMALL + OFFSET_X * 3
        y_locations = [node.location.y for node in self.nodes if node.select]
        self.y_anchor = sum(y_locations) / max(len(y_locations), 1)
        self.y_anchor -= OFFSET_Y # arbitrary
        self.links = node_tree.links
        self.time = node_tree.nodes.new(type="ShaderNodeValue")
        self.time.name = self.time.label = "time"
        self.time.select = False # we don't want it in the node group
        self.time.location.x = self.x_anchor
        self.time.location.y = self.y_anchor
        self.x_anchor = (
            min(x_locations) - OFFSET_X_LARGE - OFFSET_X_SMALL - OFFSET_X * 2)
        self.route = node_tree.nodes.new(type="NodeReroute")
        self.links.new(self.time.outputs[0], self.route.inputs[0])
        self.route.location.x = self.x_anchor + OFFSET_X
        self.route.location.y = self.y_anchor
        self.__create_new_node() # commit to providing mappings once inited

    def __create_new_node(self):
        ''' create a new curve node to create outputs '''
        nodes, links = (self.nodes, self.links)
        self.combiner_current = nodes.new(type="ShaderNodeCombineXYZ")
        for input_socket in self.combiner_current.inputs:
            links.new(self.route.outputs[0], input_socket)
        self.combiner_current.location.x = (
            self.route.location.x + OFFSET_X_SMALL)
        self.combiner_current.location.y = self.y_anchor
        self.node_current = nodes.new(type="ShaderNodeRGBCurve")
        self.node_current.location.x = (
            self.combiner_current.location.x + OFFSET_X)
        self.node_current.location.y = self.y_anchor
        settings = {'clip_min_x': 0, 'clip_min_y': 0}
        for key, value in settings.items():
            setattr(self.node_current.mapping, key, value)
        links.new(
            self.combiner_current.outputs[0],
            self.node_current.inputs['Color'])
        self.available_mapping_curves = [
            (i, self.node_current.mapping.curves[i]) for i in range(3)]
        self.splitter_current = nodes.new(type="ShaderNodeSeparateXYZ")
        self.splitter_current.location.x = (
            self.node_current.location.x + OFFSET_X_LARGE)
        self.splitter_current.location.y = self.y_anchor
        links.new(
            self.node_current.outputs[0], self.splitter_current.inputs[0])
        self.y_anchor += OFFSET_Y

    def map_curves(self, pointstruct, reroute=False):
        ''' map curves for a single float thing '''
        pointlist = pointstruct[0]
        extend = pointstruct[1]
        if not self.available_mapping_curves:
            self.__create_new_node()
        current_curve = self.available_mapping_curves[0][1]
        current_index = self.available_mapping_curves[0][0]
        current_curve.extend = extend
        pre_existing = [point for point in current_curve.points]
        for point in pointlist:
            if pre_existing:
                new_point = pre_existing.pop(0)
                new_point.location = (point[0], point[1])
            else:
                new_point = current_curve.points.new(point[0], point[1])
            new_point.handle_type = point[2]
        self.node_current.mapping.update()
        self.available_mapping_curves.pop(0)
        if reroute:
            reroute = self.nodes.new(type="NodeReroute")
            self.links.new(
                self.splitter_current.outputs[current_index],
                reroute.inputs[0])
            return(reroute.outputs[0], reroute)
        else:
            return self.splitter_current.outputs[current_index]

    def map_curves_array(self, pointstructs, reroute=False):
        ''' map curves for a triple float thing - e.g. a color '''
        outputs = [
            self.map_curves(pointstruct) for pointstruct in pointstructs]
        if all(outputs[0].node == output.node for output in outputs):
            if reroute:
                reroute = self.nodes.new(type="NodeReroute")
                self.links.new(self.node_current.outputs[0], reroute.inputs[0])
                return (reroute.outputs[0], reroute)
            else:
                return self.node_current.outputs[0]
        else:
            color_combiner = self.nodes.new(type="ShaderNodeCombineRGB")
            color_combiner.location.y = self.y_anchor
            color_combiner.location.x = (
                self.node_current.location.x + OFFSET_X_LARGE + OFFSET_X)
            for idx, output in enumerate(outputs):
                self.links.new(output, color_combiner.inputs[idx])
            if reroute:
                reroute = self.nodes.new(type="NodeReroute")
                self.links.new(color_combiner.outputs[0], reroute.inputs[0])
                return(reroute.outputs[0], reroute)
            else:
                return color_combiner.outputs[0]


def time_minmax(fcurves):
    ''' return the minimum and maximum frame number for a bunch of curves '''
    mins = []
    maxs = []
    for fcurve in fcurves:
        frames = [kp.co[0] for kp in fcurve.keyframe_points]
        mins.append(min(frames))
        maxs.append(max(frames))
    return (min(mins), max(maxs))


def time_remap(frame, frame_start, frame_length):
    ''' remap frame to a 0 to 1 range based on start and length '''
    return (frame - frame_start) / frame_length


def anim_to_node(curves, limits):
    ''' Create and return a node for a bunch of curves '''
    return None


def convert_kps(fcurve, kp, nextkp, start, length):
    ''' convert a segment from fcurve for curves node '''

    # Sampling Functions; try to get exact behavior with minimum points:


    def segment_linear(kp, nextkp):
        print('LINEAR')
        return [(
            time_remap(kp.co[0], start, length),
            kp.co[1],
            'VECTOR')]


    def segment_constant(kp, nextkp):
        print('CONSTANT')
        return [
            (time_remap(kp.co[0], start, length), kp.co[1], 'VECTOR'),
            (time_remap(nextkp.co[0]-.002, start, length), kp.co[1], 'VECTOR'),
            (time_remap(nextkp.co[0]-.001, start, length), nextkp.co[1], 'VECTOR')]


    def segment_auto(kp, nextkp):
        print('AUTO')
        return [(time_remap(kp.co[0], start, length), kp.co[1], 'AUTO')]


    def segment_sample(kp, nextkp):
        print('SAMPLE')
        result =[]
        stepsize = (int(nextkp.co[0]) - int(kp.co[0]))//5
        if stepsize == 0:
            stepsize = 1
        for frame in range(int(kp.co[0]), int(nextkp.co[0]), stepsize):
            val = fcurve.evaluate(frame)
            result.append((time_remap(frame, start, length), val, 'VECTOR'))
        return result

    #Logic to figure out which sampling to use:

    interp_map = {
        'CONSTANT': segment_constant, 'LINEAR': segment_linear,
        'BEZIER': 'BEZIER', # First 3 are keyframe interps
        'VECTOR':segment_linear, 'AUTO':segment_auto,
        'AUTO_CLAMPED': 'CHECK'} # last 3 are bezier handle types
    try:
        sampling = interp_map[kp.interpolation]
    except KeyError: # If it's something unexpected, just sample every pt.
        sampling = segment_sample
    if callable(sampling):
        return sampling(kp, nextkp)
    # Check for bezier case
    if (
            sampling == 'BEZIER' and
            kp.handle_right_type == nextkp.handle_left_type):
        try:
            sampling = interp_map[kp.handle_right_type]
        except:
            sampling = segment_sample
        if sampling == 'CHECK': # if it's flat treat segment as linear
            if kp.co[1] == nextkp.co[1]:
                sampling = segment_linear
            else:
                sampling = segment_sample
    else:
        sampling = segment_sample
    return sampling(kp, nextkp) # return appropriate sampling


def convert_fcurve(fcurve, frame_start, frame_length):
    ''' convert an fcurve into an appropriate set of points for node '''
    kps = [kp for kp in fcurve.keyframe_points]
    kps.sort(key=lambda x: x.co[0]) # sort by time just in case
    sample_points = []
    for idx, kp in enumerate(kps[:-1]):
        sample_points.extend(convert_kps(
            fcurve, kp, kps[idx + 1], frame_start, frame_length))
    extend = 'EXTRAPOLATED' if fcurve.extrapolation == 'LINEAR' else 'HORIZONTAL'
    return sample_points, extend


class MathRamp():
    ''' Convert Animated Ramps into Math nodes with a time input '''

    def __init__(
            self, node_tree, node, availabe_curves, limits,
            position=False, color=False):
        self.node_tree = node_tree
        if node.bl_idname == "ShaderNodeValToRGB" and 'color_ramp' in dir(node):
            self.node = node
        else:
            raise ValueError("Node {} is not a Color Ramp".format(node.name))
        if node_tree.animation_data and node_tree.animation_data.action:
            self.fcurves = node_tree.animation_data.action.fcurves
        else:
            self.fcurves = []
        if limits:
            self.frame_start = limits[0]
            self.frame_length = limits[1] - limits[0]
        else:
            self.frame_start = 0
            self.frame_length = 100
        self.availabe_curves = availabe_curves
        self.wire_positions = position
        self.wire_colors = color
        self.me = []
        self.anim_inputs = {}
        self.convert()

    def setup_input(
            self, nodes, value, anim_points, availabe_curves,
            alpha=False, wire=True):
        ''' input value, later can become time based '''
        print(anim_points)
        if not anim_points or not anim_points[0]:
            node = nodes.new(type="ShaderNodeValue")
            socket = node.outputs[0]
            node.outputs[0].default_value = value
            node.name = "{}_{}".format(
                'Alpha' if alpha else 'Position', self.index)
        else:
            wire = False
            socket, node = availabe_curves.map_curves(anim_points, True)
            name = 'Alpha' if alpha else 'Position'
            if self.index in self.anim_inputs:
                self.anim_inputs[self.index][name] = node.name
            else:
                self.anim_inputs[self.index] = {name: node.name}
        node.location.x = self.anchor_x - 4 * OFFSET_X + alpha * OFFSET_X
        node.location.y = (
            self.anchor_y - (OFFSET_Y * self.count // 2)
            + self.index * OFFSET_Y)

        if (
                ((self.wire_positions and not alpha) or
                (self.wire_colors and alpha)) and wire):
            reroute = nodes.new(type="NodeReroute")
            self.node_tree.links.new(socket, reroute.inputs[0])
            reroute.location.x = node.location.x
            reroute.location.y = node.location.y
            self.me.append(reroute)
            socket = reroute.outputs[0]
            return socket
        else:
            self.me.append(node)
            return socket

    def setup_output(
            self, nodes, col, anim_points, availabe_curves, wire=True):
        ''' output value, later can become time based '''
        try:
            print(anim_points)
            points = anim_points[3]
        except:
            print(self.index)
            print("setting points to none")
            points = None
        alpha_output = self.setup_input(
            nodes, col[3], points, availabe_curves, True, wire)
        alpha_output.node.location.y += OFFSET_Y / 2
        if not anim_points or not anim_points[0]:
            print("static colors")
            node = nodes.new(type="ShaderNodeRGB")
            node.outputs[0].default_value = col
            node.name = "{}_{}".format('Color', self.index)
            socket = node.outputs[0]
        else:
            print("animated colors")
            wire = False
            socket, node = availabe_curves.map_curves_array(
                anim_points[:-1], True)
            if self.index in self.anim_inputs:
                self.anim_inputs[self.index]['Color'] = node.name
            else:
                self.anim_inputs[self.index] = {'Color': node.name}
        node.location.x = self.anchor_x - 3 * OFFSET_X
        node.location.y = (
            self.anchor_y - (OFFSET_Y * self.count // 2)
            + self.index * OFFSET_Y)
        if wire and self.wire_colors:
            reroute = nodes.new(type="NodeReroute")
            self.node_tree.links.new(socket, reroute.inputs[0])
            reroute.location.x = node.location.x
            reroute.location.y = node.location.y
            self.me.append(reroute)
            socket = reroute.outputs[0]
            return socket, alpha_output
        else:
            self.me.append(node)
            return socket, alpha_output

    def get_curve(self, idx):
        ''' return fcurve for ramp element if it's animated '''
        node = self.node
        fcurves = self.fcurves
        base = 'nodes["{}"].color_ramp.elements[{}]'.format(node.name, idx)
        color = [
            fc for fc in fcurves if "{}.color".format(base) in fc.data_path]
        position = [
            fc for fc in fcurves if "{}.position".format(base) in fc.data_path]
        color.sort(key=lambda x: x.array_index)
        position = position[0] if position else None
        color = color if color else None
        return position, color

    def make_section(self, a, b, idx):
        ''' creates a single ramp section between a and b positions '''
        location_y =  (
                self.anchor_y - (OFFSET_Y * self.count // 2)
                + self.index * OFFSET_Y)
        location_x = self.anchor_x - 2 * OFFSET_X
        nodes = self.node_tree.nodes
        links = self.node_tree.links
        interpolation = self.interpolation
        # inputs:
        min_in, max_in = (a[0], b[0])
        # outputs are just a[1]/b[1] [0] (color) and a[1]/b[1][1] (alpha)
        min_out, max_out = (a[1], b[1])

        # the smarts:
        # create an inbetween group
        inbetween = make_group(nodes, get_node_group('between'))
        inbetween.location.x = location_x
        inbetween.location.y = location_y
        self.me.append(inbetween)
        location_x += OFFSET_X
        inbetween.name = inbetween.label = "inbetween_{}".format(idx)
        links.new(min_in, inbetween.inputs["Min"])
        links.new(max_in, inbetween.inputs["Max"])
        links.new(self.input_socket, inbetween.inputs["Fac"])
        mix_factor = inbetween.outputs[0]
        # create a fac group if interpolation is not constant
        if interpolation != 'CONSTANT':
            fac = make_group(nodes, get_node_group('fac'))
            fac.name = fac.label = "fac_{}".format(idx)
            fac.location.x = location_x
            fac.location.y = location_y
            self.me.append(fac)
            links.new(self.input_socket, fac.inputs["Fac"])
            links.new(min_in, fac.inputs["Min"])
            links.new(max_in, fac.inputs["Max"])
            mix_factor = fac.outputs[0]
            # create an ease group if interpolation is ease
            if interpolation == 'EASE':
                ease = make_group(nodes, get_node_group('ease'))
                ease.name = ease.label = "ease_{}".format(idx)
                links.new(fac.outputs[0], ease.inputs["Fac"])
                mix_factor = ease.outputs[0]
                ease.location.x = location_x + OFFSET_X
                ease.location.y = location_y
                self.me.append(ease)
        else:
            invert = nodes.new(type="ShaderNodeMath")
            invert.operation = 'SUBTRACT'
            invert.inputs[0].default_value = 1.0
            invert.location.x = location_x
            invert.location.y = location_y
            self.me.append(invert)
            links.new(mix_factor, invert.inputs[1])
            mix_factor = invert.outputs[0]
        # create and wire the output mixes
        location_x += 2 * OFFSET_X
        outs = []
        for channel in (0, 1):
            mix = nodes.new(type="ShaderNodeMixRGB")
            mix.name = mix.label = "mix_{}_{}".format(channel, idx)
            mix.location.x = location_x
            mix.location.y = location_y - channel * OFFSET_Y / 2
            self.me.append(mix)
            location_x += OFFSET_X
            links.new(mix_factor, mix.inputs['Fac'])
            links.new(min_out[channel], mix.inputs['Color1'])
            links.new(max_out[channel], mix.inputs['Color2'])
            out = mix.outputs[0]

            mask = nodes.new(type="ShaderNodeMixRGB")
            mask.name = mask.label = "mask_{}_{}".format(channel, idx)
            mask.inputs['Color1'].default_value = [0, 0, 0, 1]
            mask.location.x = location_x
            mask.location.y = location_y
            self.me.append(mask)
            links.new(inbetween.outputs[0], mask.inputs['Fac'])
            links.new(out, mask.inputs['Color2'])
            outs.append(mask.outputs[0])
        return outs

    def convert(self):
        ''' convert ramp node into a nodegroup of discrete nodes '''
        node = self.node
        nodes = self.node_tree.nodes
        links = self.node_tree.links
        availabe_curves = self.availabe_curves
        ramp = node.color_ramp
        self.anchor_x = node.location.x
        self.anchor_y = node.location.y
        input_link = node.inputs['Fac'].links[0]
        # Sanitization of inputs, first, temporary node for type:
        input_convert = nodes.new(type="ShaderNodeRGBToBW")
        links.new(input_link.from_socket, input_convert.inputs[0])
        # Second part of Sanitization, permanent nodes for limiting:
        max_limit = nodes.new(type="ShaderNodeMath")
        max_limit.operation = 'MINIMUM'
        links.new(input_convert.outputs[0], max_limit.inputs[0])
        max_limit.inputs[1].default_value = 1.0
        self.me.append(max_limit)
        max_limit.location.x = self.anchor_x - OFFSET_X * 6
        max_limit.location.y = self.anchor_y

        min_limit = nodes.new(type="ShaderNodeMath")
        min_limit.operation = 'MAXIMUM'
        links.new(max_limit.outputs[0], min_limit.inputs[0])
        min_limit.inputs[1].default_value = 0.0
        self.me.append(min_limit)
        min_limit.location.x = max_limit.location.x + OFFSET_X
        min_limit.location.y = max_limit.location.y


        input_socket = min_limit.outputs[0]
        self.temp_converter = input_convert
        input_reroute = nodes.new(type="NodeReroute")
        input_reroute.location.x = min_limit.location.x + OFFSET_X
        input_reroute.location.y = self.anchor_y
        links.new(input_socket, input_reroute.inputs[0])
        self.input_socket = input_reroute.outputs[0]
        self.me.append(input_reroute)

        self.color_links = node.outputs['Color'].links
        self.alpha_links = node.outputs['Alpha'].links

        self.count = len(ramp.elements)
        self.index = 0
        frame_start = self.frame_start
        frame_length = self.frame_length
        cos = []
        for idx, element in enumerate(ramp.elements):
            self.index = idx + 1 # first element is second!
            position_curve, color_curves = self.get_curve(idx)
            if position_curve:
                position_curve = convert_fcurve(
                    position_curve, frame_start, frame_length)
            position = self.setup_input(
                nodes, element.position, position_curve,
                availabe_curves, alpha=False)
            if color_curves:
                color_curves = [
                    convert_fcurve(curve, frame_start, frame_length)
                    for curve in color_curves]
            color = self.setup_output(
                nodes, element.color, color_curves, availabe_curves)
            if idx == 0:
                self.index = 0
                zero_position = self.setup_input(
                    nodes, -0.0001, None, availabe_curves,
                    alpha=False, wire=False) # XXX Avoid clipping
                cos.append((zero_position, color))
            cos.append((position, color))
            if idx == len(ramp.elements) - 1:
                self.index += 1
                final_position = self.setup_input(
                    nodes, 1.0001, None, availabe_curves,
                    alpha=False, wire=False) # XXX Avoid clipping
                cos.append((final_position, color))
        self.interpolation = ramp.interpolation
        sections = []
        for index in range(0,len(cos) - 1):
            self.index = index
            section = self.make_section(cos[index], cos[index + 1], index)
            sections.append(section)


        def link_sections(pairs, idx, most_recent):
            ''' Make sure you start at 1 for a proper countdown '''
            first = most_recent if most_recent else pairs[0]
            second = pairs[idx]
            location_y = (
                self.anchor_y - (OFFSET_Y * self.count // 2)
                + idx * OFFSET_Y)
            location_x = self.anchor_x + 3 * OFFSET_X + idx * OFFSET_X
            color_mix = nodes.new(type="ShaderNodeMixRGB")
            color_mix.blend_type = 'ADD'
            color_mix.inputs['Fac'].default_value = 1.0
            color_mix.location.y = location_y
            color_mix.location.x = location_x
            self.me.append(color_mix)
            links.new(first[0], color_mix.inputs['Color1'])
            links.new(second[0], color_mix.inputs['Color2'])
            value_mix = nodes.new(type="ShaderNodeMath")
            value_mix.operation = 'ADD'
            value_mix.location.y = location_y - OFFSET_Y / 2
            value_mix.location.x = location_x
            self.me.append(value_mix)
            links.new(first[1], value_mix.inputs[0])
            links.new(second[1], value_mix.inputs[1])
            if idx + 1 < len(pairs):
                return link_sections(
                    pairs,
                    idx + 1,
                    (color_mix.outputs[0], value_mix.outputs[0]))
            else:
                return (color_mix.outputs[0], value_mix.outputs[0])

        final_outputs = link_sections(sections, 1, None) # start at 1


        def get_socket(the_links):
            if len(the_links) != 1:
                reroute = nodes.new(type="NodeReroute")
                reroute.location.x = self.anchor_x + OFFSET_X * 2
                reroute.location.y = self.anchor_y
                self.anchor_y -= OFFSET_Y/4
                outputs = [link.to_socket for link in the_links]
                for idx, output in enumerate(outputs):
                    links.remove(the_links[idx])
                    links.new(reroute.outputs[0], output)
                return reroute.inputs[0]
            else:
                return the_links[0].to_socket

        links.new(final_outputs[0], get_socket(self.color_links))
        links.new(final_outputs[1], get_socket(self.alpha_links))

        selected = [
            node for node in self.node_tree.nodes
            if node.select and node not in self.me]
        for node in selected:
            node.select = False
        bpy.ops.node.group_make() # Create a Group with the usual Operator
        bpy.ops.node.group_edit(exit=True)

        new_group = self.node_tree.nodes.active
        new_group.node_tree.name = "{}_math".format(self.node.name)
        new_group.label = self.node.label if self.node.label else self.node.name
        new_group.name = new_group.node_tree.name

        # Rename some of the IO
        fac_source = self.temp_converter.outputs[0]
        for idx, inp in enumerate(new_group.inputs):
            if any(link.from_socket == fac_source for link in inp.links):
                break
        else:
            raise ValueError("New Node not connected")
        new_group.node_tree.inputs[idx].name = 'Fac'
        new_group.node_tree.inputs[idx].min_value = 0.0
        new_group.node_tree.inputs[idx].max_value = 1.0
        links.new(
            self.temp_converter.inputs[0].links[0].from_socket,
            new_group.inputs[idx])
        nodes.remove(self.temp_converter)
        for output in new_group.node_tree.outputs:
            if output.type == 'VALUE':
                output.name = 'Alpha'
                output.min_value = 0.0
                output.max_value = 1.0

        for index in self.anim_inputs:
            data = self.anim_inputs[index]
            for socket_type in data:
                socket = new_group.node_tree.nodes[data[socket_type]].inputs[0]
                for idx, inp in enumerate(
                            new_group.node_tree.nodes['Group Input'].outputs):
                    if any(link.to_socket == socket for link in inp.links):
                        new_group.node_tree.inputs[idx].name = "{}{}".format(
                            socket_type, index)
                        break

        for node in selected:
            node.select = True
        self.math_ramp = new_group


class Animalizer(object):
    ''' replaces animated nodes with timed ones '''

    def __init__(self, node_tree, available_curves, limits):
        ''' side effects classes are my favorite '''
        self.node_tree = node_tree
        self.nodes = node_tree.nodes
        self.links = node_tree.links
        self.available_curves = available_curves
        self.selected = [
            node for node in node_tree.nodes if node.select]
        self.action = node_tree.animation_data.action
        self.frame_start = limits[0]
        self.frame_length = limits[1] - limits[0]

        fcurves = self.action.fcurves
        # XXX exceptions might cause problems, resolve when you get it
        animated = (
            (
                fc.data_path,
                node_tree.path_resolve(
                    fc.data_path.replace('.default_value','')))
            for fc in fcurves if fc.data_path.startswith('nodes["')
            and fc.data_path.endswith('default_value'))
        self.inputs = {}
        self.outputs = {}
        for path, socket in animated:
            if (
                    socket.is_output and socket.is_linked and
                    socket.node.select):
                self.outputs[path] = socket
            elif (
                    not socket.is_output and not socket.is_linked and
                    socket.node.select):
                self.inputs[path] = socket
        self.fixup('outputs')
        self.fixup('inputs')
        self.cleanup_outputs()

    def fixup(self, socket_type):
        ''' replace time->curves->splitters connecting to output's inputs '''
        fcurves = self.action.fcurves
        frame_start = self.frame_start
        frame_length = self.frame_length
        links = self.links
        available_curves = self.available_curves
        if socket_type == 'inputs':
            sockets = self.inputs
        else:
            sockets = self.outputs
        for path in sockets:
            path_curves = [fc for fc in fcurves if fc.data_path == path]
            socket = sockets[path]
            if socket.type in SCALAR_SOCKETS:

                pointlist = convert_fcurve(
                    path_curves[0], frame_start, frame_length)
                new_socket = available_curves.map_curves(pointlist)
            elif socket.type in VECTOR_SOCKETS:
                pointlists = []
                for i in range(3):
                    fcurve = [fc for fc in path_curves if fc.array_index == i]
                    if fcurve:
                        pointlist = convert_fcurve(
                            fcurve[0], frame_start, frame_length)
                    else:
                        pointlist = [
                            (0.0, socket.default_value[i], 'VECTOR'),
                            (1.0, socket.default_value[i], 'VECTOR')]
                    pointlists.append(pointlist)
                new_socket = available_curves.map_curves_array(pointlists)
            else:
                new_socket = None
                raise ValueError(
                    "Unsupported Socket Type {}".format(type(socket)))
            if socket_type == 'inputs':
                new_link = links.new(new_socket, socket)
            else:
                for link in socket.links:
                    new_link = links.new(new_socket, link.to_socket)

    def cleanup_outputs(self):
        ''' remove unconnected output nodes that we fixed up earlier '''
        for socket in self.outputs.values():
            node = socket.node
            for output in node.outputs:
                if output.is_linked:
                    break
            else:
                self.node_tree.nodes.remove(node)

def is_ramp_animated(ramp, fcurves):
    ''' return True if it's in the the curves '''
    prefix = 'nodes["{}"].color_ramp.elements['.format(ramp.name)
    for fcurve in fcurves:
        if fcurve.data_path.startswith(prefix):
            return True
    return False


def ramp_fixer(node_tree, availabe_curves, limits):
    ''' Fix up all selected ramps '''
    nodes = node_tree.nodes
    fcurves = node_tree.animation_data.action.fcurves
    ramps = [
        node for node in nodes
        if node.bl_label == 'ColorRamp'
        and node.select
        and is_ramp_animated(node, fcurves)]
    for ramp in ramps:
        mathramp = MathRamp(
            node_tree,
            ramp,
            availabe_curves,
            limits)


class AddRampChannel(bpy.types.Operator):
    ''' Add a new channel to a ramp group, for spec, bump, etc '''
    bl_idname = 'nodes.add_ramp_channel'
    bl_label = 'Add a new Channel to a group'

    make_color_channel = bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space.type == 'NODE_EDITOR' and
            space.tree_type == 'ShaderNodeTree' and
            space.edit_tree and space.edit_tree.nodes.active and
            space.edit_tree.nodes.active.bl_idname == 'ShaderNodeGroup')

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # get the nodetree for the active node
        node_tree = context.space_data.edit_tree.nodes.active.node_tree
        # determine the type we want to add (color or alpha)
        y_locations = [node.location.y for node in node_tree.nodes]
        y_max = max(y_locations)
        y_min = min(y_locations)
        prefix = '0' if self.make_color_channel else '1'
        mix = 'mix_{}'.format(prefix)
        mask = 'mask_{}'.format(prefix)

        index  = 1 + max(
            int(n.name.split('.')[0].split('_')[1])
            for n in node_tree.nodes if n.name.startswith('mask_'))
        print('index is ', index)
        # locate the alpha or color inputs

        # locate the associated segments and mixes
        segment_nodes = [
            node for node in node_tree.nodes
            if node.name.startswith(mix) or node.name.startswith(mask)]

        add_nodes = [
            node for node in node_tree.nodes
            if node.bl_idname == 'ShaderNodeMath' and node.operation ==  'ADD']


        def _get_more_nodes(dupli_nodes):
            ''' get all the add nodes attached to our segments '''
            segment_adders = [
                node for node in add_nodes
                if any(
                    link.from_node in dupli_nodes
                    for inp in node.inputs for link in inp.links)]
            if segment_adders:
                dupli_nodes.extend(segment_adders)
                for node in segment_adders:
                    add_nodes.remove(node)
                dupli_nodes = _get_more_nodes(dupli_nodes)
            else:
                return dupli_nodes
            return dupli_nodes

        dupli_nodes = _get_more_nodes(segment_nodes)
        print("dupli nodes ", [n.name for n in dupli_nodes])

        group_output = [
            node for node in node_tree.nodes
            if node.bl_idname == "NodeGroupOutput"][0]
        print(group_output.name)
        group_input = [
            node for node in node_tree.nodes
            if node.bl_idname == "NodeGroupInput"][0]

        penultimate = [
            node for node in dupli_nodes
            if node.bl_idname == "ShaderNodeMath"
            and node.operation == 'ADD' and
            any(
                link.to_node == group_output
                for link in node.outputs[0].links)][0]

        duplicated_nodes = []
        for node in dupli_nodes:
            duplicate = node_tree.nodes.new(type=node.bl_idname)
            duplicated_nodes.append(duplicate)
            for attr in dir(node):
                try:
                    setattr(duplicate, attr, getattr(node, attr))
                except:
                    pass # print(attr)
            duplicate.name = duplicate.label = node.name.replace(
                mix, mix.replace(prefix, str(index))).replace(
                    mask, mask.replace(prefix, str(index)))
        for count, node in enumerate(dupli_nodes):
            duplicate = duplicated_nodes[count]
            for idx, inp in enumerate(node.inputs):
                duplicate.inputs[idx].default_value = inp.default_value
                for link in inp.links:
                    if link.from_node in dupli_nodes:
                        from_node = duplicated_nodes[
                            dupli_nodes.index(link.from_node)]
                        output_idx = [
                            o_idx for o_idx, out in enumerate(
                                link.from_node.outputs)
                            if out == link.from_socket][0]
                        from_socket = from_node.outputs[output_idx]
                        nlink = node_tree.links.new(
                            from_socket, duplicate.inputs[idx])
                    else:
                        nlink = node_tree.links.new(
                            link.from_socket, duplicate.inputs[idx])
            for idx, out in enumerate(node.outputs):
                for link in out.links:
                    if node == penultimate:
                        nlink = node_tree.links.new(
                            duplicate.outputs[idx], group_output.inputs[-1]
                        )
                    elif link.to_node in dupli_nodes:
                        to_node = duplicated_nodes[
                            dupli_nodes.index(link.to_node)]
                        input_idx = [
                            i_idx for i_idx, inp in enumerate(
                                link.to_node.inputs)
                            if inp == link.to_socket][0]
                        to_socket = to_node.inputs[input_idx]
                        nlink = node_tree.links.new(
                            duplicate.outputs[idx], to_socket)
                    else:
                        nlink = node_tree.links.new(
                            duplicate.outputs[idx], link.to_socket)

            duplicate.location.y = duplicate.location.y + y_max - y_min
        # wire up the new inputs
        inputs = [
            node for node in node_tree.nodes
            if node.bl_idname == "ShaderNodeValue"
            and any(
                link.to_node in duplicated_nodes and
                link.to_node.name.startswith('mix') and
                link.to_socket.name.startswith('Color')
                for link in node.outputs[0].links)]
        reroutes = [
            node for node in node_tree.nodes
            if node.bl_idname == "NodeReroute"
            and any(
                link.to_node in duplicated_nodes and
                link.to_node.name.startswith('mix') and
                link.to_socket.name.startswith('Color')
                for link in node.outputs[0].links)]
        # The following works because of our constructed ramp:
        final_sockets = [
            reroute.inputs[0].links[0].from_socket for reroute in reroutes]
        values = [
            (int(inp.name.split('.')[0].split('_')[1]), 'input', inp, idx)
            for idx, inp in enumerate(inputs)]
        def get_end_digits(thing):
            return ''.join(
                c for i, c in enumerate(thing) if c.isdigit() and
                (i == len(thing) - 1 or all(j.isdigit() for j in thing[i+1:])))
        values.extend([
            (int(get_end_digits(sock.name)), 'reroute', reroutes[idx], idx)
            for idx, sock in enumerate(final_sockets)])
        values.sort(key=lambda x: x[0])
        for value in values:
            name = "Channel {} {}".format(index, value[0])
            sockets = [
                socket for node in duplicated_nodes
                if node.name.startswith('mix') for socket in node.inputs
                if socket.name.startswith('Color') and
                socket.links[0].from_node == value[2] ]
            new_reroute = node_tree.nodes.new(type="NodeReroute")
            for socket in sockets:
                node_tree.links.new(new_reroute.outputs[0], socket)
            link = node_tree.links.new(
                group_input.outputs[-1], new_reroute.inputs[0])
            node_tree.inputs[-1].name = name
        # name the output
        node_tree.outputs[-1].name = "Channel {}".format(index)
        return {'FINISHED'}


class GroupRamp(bpy.types.Operator):
    ''' Transform the active ramp node to a group '''
    bl_idname = 'nodes.group_ramp'
    bl_label = 'Turn a Ramp Node into a Group'

    make_position_inputs = bpy.props.BoolProperty(default=True)
    make_color_inputs = bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space.type == 'NODE_EDITOR' and
            space.tree_type == 'ShaderNodeTree' and
            space.edit_tree and space.edit_tree.nodes.active and
            space.edit_tree.nodes.active.bl_idname == 'ShaderNodeValToRGB')

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        space = context.space_data
        node_tree = space.edit_tree
        node = node_tree.nodes.active
        math_ramp = MathRamp(
            node_tree, node, None, [],
            self.make_position_inputs, self.make_color_inputs)
        group = math_ramp.math_ramp
        group.location.x = node.location.x
        group.location.y = node.location.y
        for idx, inp in enumerate(group.inputs):
           if inp.name != 'Fac':
               from_node = inp.links[0].from_node
               from_socket = inp.links[0].from_socket
               name = from_node.name
               tree_input = group.node_tree.inputs[idx]
               tree_input.name = name.replace('_','')
               tree_input.default_value = from_socket.default_value
               inp.default_value = from_socket.default_value
               if tree_input.type == 'VALUE':
                   tree_input.min_value = 0.0
                   tree_input.max_value = 1.0
               node_tree.nodes.remove(from_node)
        for out in group.outputs:
            for link in out.links:
                to_node = link.to_node
                if to_node.bl_idname == 'NodeReroute':
                    if not to_node.outputs[0].links:
                        node_tree.nodes.remove(to_node)

        return {'FINISHED'}


class GroupAnimatedMake(bpy.types.Operator):
    ''' Transform Animated Nodes into a group with time input '''
    bl_idname = 'nodes.group_animated_make'
    bl_label = 'Make Animated Group'

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space.type == 'NODE_EDITOR' and
            space.tree_type == 'ShaderNodeTree' and
            space.edit_tree and space.edit_tree.animation_data and
            space.edit_tree.animation_data.action)

    def execute(self, context):
        space = context.space_data
        node_tree = space.edit_tree
        available_curves = AvailableCurves(node_tree)
        action = node_tree.animation_data.action
        limits = time_minmax(action.fcurves)
        animalizer = Animalizer(node_tree, available_curves, limits)
        ramp_fixer(node_tree, available_curves, limits)

        bpy.ops.node.group_make() # Create a Group with the usual Operator
        bpy.ops.node.group_edit(exit=True)
        new_group = node_tree.nodes.active
        new_group.node_tree.name = "Animed"
        #find the link to time:
        for idx, socket in enumerate(new_group.inputs):
            for link in socket.links:
                if link.from_node == available_curves.time:
                    new_group.node_tree.inputs[idx].name = 'Time'
                    new_group.node_tree.inputs[idx].min_value = 0.0
                    new_group.node_tree.inputs[idx].max_value = 1.0
                    break
        node_tree.nodes.remove(available_curves.time)
        new_group.node_tree.animation_data_clear()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(GroupAnimatedMake)
    bpy.utils.register_class(GroupRamp)
    bpy.utils.register_class(AddRampChannel)


def unregister():
    bpy.utils.unregister_class(GroupAnimatedMake)
    bpy.utils.unregister_class(GroupRamp)
    bpy.utils.unregister_class(AddRampChannel)

if __name__ == '__main__':
    register()
