from copy import deepcopy

import bpy
from ocvl.core.settings import SOCKET_COLORS
from ocvl.core.exceptions import LackRequiredSocket, NoDataError
from ocvl.core.globals import SOCKET_DATA_CACHE
from ocvl.core.register_utils import ocvl_register, ocvl_unregister


sentinel = object()


def get_socket_id(socket):
    return str(hash(socket.id_data.name + socket.node.name + socket.identifier))


def process_from_socket(self, context):
    """Update function of exposed properties in Sockets"""
    self.node.process_node(context)


def get_other_socket(socket):
    """
    Get next real upstream socket.
    This should be expanded to support wifi nodes also.
    Will return None if there isn't a another socket connect
    so no need to check socket.links
    """
    if not socket.is_linked or not socket.links:
        return None
    if socket.is_output:
        other = socket.links[0].to_socket
    else:
        other = socket.links[0].from_socket

    if other.node.bl_idname == 'NodeReroute':
        if not socket.is_output:
            return get_other_socket(other.node.inputs[0])
        else:
            return get_other_socket(other.node.outputs[0])
    else:  #other.node.bl_idname == 'WifiInputNode':
        return other


def set_socket(socket, out):
    """sets socket data for socket"""
    # if data_structure.DEBUG_MODE:
    #     if not socket.is_output:
    #         warning("{} setting input socket: {}".format(socket.node.name, socket.name))
    #     if not socket.is_linked:
    #         warning("{} setting unconncted socket: {}".format(socket.node.name, socket.name))
    s_id = socket.socket_id
    s_ng = socket.id_data.name
    if s_ng not in SOCKET_DATA_CACHE:
        SOCKET_DATA_CACHE[s_ng] = {}
    SOCKET_DATA_CACHE[s_ng][s_id] = out


def get_socket(socket, deepcopy_=True):
    """gets socket data from socket,
    if deep copy is True a deep copy is make_dep_dict,
    to increase performance if the node doesn't mutate input
    set to False and increase performance substanstilly
    """
    if socket.is_linked:
        other = socket.other
        if other:
            s_id = other.socket_id
            s_ng = other.id_data.name
            if s_ng not in SOCKET_DATA_CACHE:
                raise LookupError
            if s_id in SOCKET_DATA_CACHE[s_ng]:
                out = SOCKET_DATA_CACHE[s_ng][s_id]
                if deepcopy_:
                    return deepcopy(out)
                else:
                    return out
            else:
                # if data_structure.DEBUG_MODE:
                #     debug("cache miss: %s -> %s from: %s -> %s",
                #             socket.node.name, socket.name, other.node.name, other.name)
                raise NoDataError(socket)
    # not linked
    raise NoDataError(socket)


def get_socket_info(socket):
    """returns string to show in socket label"""
    ng = socket.id_data.name

    if socket.is_output:
        s_id = socket.socket_id
    elif socket.is_linked:
        other = socket.other
        if other:
            s_id = other.socket_id
        else:
            return ''
    else:
        return ''
    if ng in SOCKET_DATA_CACHE:
        if s_id in SOCKET_DATA_CACHE[ng]:
            data = SOCKET_DATA_CACHE[ng][s_id]
            if data:
                return str(len(data))
    return ''


def recursive_framed_location_finder(node, loc_xy):
    locx, locy = loc_xy
    if node.parent:
        locx += node.parent.location.x
        locy += node.parent.location.y
        return recursive_framed_location_finder(node.parent, (locx, locy))
    else:
        return locx, locy


class SvLinkNewNodeInput(bpy.types.Operator):
    ''' Spawn and link new node to the left of the caller node'''
    bl_idname = "node.sv_quicklink_new_node"
    bl_label = "Add a new node to the left"

    socket_index = bpy.props.IntProperty()
    origin = bpy.props.StringProperty()
    is_input_mode = bpy.props.BoolProperty(default=True)
    new_node_idname = bpy.props.StringProperty()
    new_node_offsetx = bpy.props.IntProperty(default=-200)
    new_node_offsety = bpy.props.IntProperty(default=0)

    def execute(self, context):
        tree = context.space_data.edit_tree
        nodes, links = tree.nodes, tree.links

        caller_node = nodes.get(self.origin)
        new_node = nodes.new(self.new_node_idname)
        new_node.location[0] = caller_node.location[0] + self.new_node_offsetx
        new_node.location[1] = caller_node.location[1] + self.new_node_offsety
        if self.is_input_mode:
            links.new(new_node.outputs[0], caller_node.inputs[self.socket_index])
        else:
            links.new(new_node.inputs[0], caller_node.outputs[self.socket_index])

        if caller_node.parent:
            new_node.parent = caller_node.parent
            loc_xy = new_node.location[:]
            locx, locy = recursive_framed_location_finder(new_node, loc_xy)
            new_node.location = locx, locy

        return {'FINISHED'}


class OCVLSocketBase:
    bl_idname = None
    bl_label = None
    draw_socket_color = None

    use_prop: bpy.props.BoolProperty(default=False)
    use_expander: bpy.props.BoolProperty(default=True)
    use_quicklink: bpy.props.BoolProperty(default=True)
    expanded: bpy.props.BoolProperty(default=False)

    prop_name: bpy.props.StringProperty(default='')
    prop_type: bpy.props.StringProperty(default='')
    prop_index: bpy.props.IntProperty()
    custom_draw: bpy.props.StringProperty()

    @property
    def socket_id(self):
        return str(hash(self.id_data.name + self.node.name + self.identifier))

    @property
    def other(self):
        return get_other_socket(self)

    def set_default(self, value):
        if self.prop_name:
            setattr(self.node, self.prop_name, value)

    @property
    def index(self):
        node = self.node
        sockets = node.outputs if self.is_output else node.inputs
        for i, s in enumerate(sockets):
            if s == self:
                return i

    @property
    def extra_info(self):
        return ""

    def sv_set(self, data):
        set_socket(self, data)

    def sv_get(self):
        return get_socket(self)

    def draw_expander_template(self, context, layout, prop_origin, prop_name="prop"):

        if self.bl_idname == "StringsSocket":
            layout.prop(prop_origin, prop_name)
        else:
            if self.use_expander:
                split = layout.split(factor=.2, align=True)
                c1 = split.column(align=True)
                c2 = split.column(align=True)

                if self.expanded:
                    c1.prop(self, "expanded", icon='TRIA_UP', text='')
                    c1.label(text=self.name[0])
                    c2.prop(prop_origin, prop_name, text="", expand=True)
                else:
                    c1.prop(self, "expanded", icon='TRIA_DOWN', text="")
                    row = c2.row(align=True)
                    if self.bl_idname == "SvColorSocket":
                        row.prop(prop_origin, prop_name)
                    else:
                        row.template_component_menu(prop_origin, prop_name, name=self.name)

            else:
                layout.template_component_menu(prop_origin, prop_name, name=self.name)

    def draw_quick_link_input(self, context, layout, node):

        if self.use_quicklink:
            if self.bl_idname == "ImageSocket":
                new_node_idname = "OCVLImageSampleNode"
            elif self.bl_idname == "VerticesSocket":
                new_node_idname = "GenVectorsNode"
            else:
                return

            op = layout.operator('node.sv_quicklink_new_node', text="", icon="PLUGIN")
            op.socket_index = self.index
            op.origin = node.name
            op.is_input_mode = True
            op.new_node_idname = new_node_idname
            op.new_node_offsetx = -250 - 40 #* self.index
            op.new_node_offsety = -350 * self.index

    def draw_quick_link_output(self, context, layout, node):

        if self.use_quicklink:
            if self.bl_idname == "ImageSocket":
                new_node_idname = "OCVLImageViewerNode"
            elif self.bl_idname == "VerticesSocket":
                new_node_idname = "GenVectorsNode"
            else:
                return

            try:
                node.check_input_requirements(node.n_requirements)
                op_icon = "LIGHT"
            except (Exception, LackRequiredSocket) as e:
                op_icon = "NONE"

            op = layout.operator('node.sv_quicklink_new_node', text="", icon=op_icon)
            op.socket_index = self.index
            op.origin = node.name
            op.is_input_mode = False
            op.new_node_idname = new_node_idname
            op.new_node_offsetx = 250 + 40 * self.index
            op.new_node_offsety = 230 * self.index

    def draw(self, context, layout, node, text):

        if self.is_linked:  # linked INPUT or OUTPUT
            t = text
            if not self.is_output:
                if self.prop_name:
                    prop = node.rna_type.properties.get(self.prop_name, None)
                    t = prop.name if prop else text
            info_text = t + '. ' + get_socket_info(self)
            info_text += self.extra_info
            layout.label(text=info_text)

        elif self.is_output:  # unlinked OUTPUT
            layout.label(text=text)
            self.draw_quick_link_output(context, layout, node)

        else:  # unlinked INPUT
            if self.prop_name:  # has property
                self.draw_expander_template(context, layout, prop_origin=node, prop_name=self.prop_name)

            elif self.use_prop:  # no property but use default prop
                self.draw_expander_template(context, layout, prop_origin=self)

            # elif self.quicklink_func_name:
            #     try:
            #         getattr(node, self.quicklink_func_name)(self, context, layout, node)
            #     except Exception as e:
            #         self.draw_quick_link(context, layout, node)
            #     layout.label(text=text)
            #
            else:  # no property and not use default prop
                self.draw_quick_link_input(context, layout, node)
                layout.label(text=text)

    def draw_color(self, context, node):
        _draw_socket = getattr(self, "draw_socket_color", None)
        return _draw_socket or SOCKET_COLORS.__getattribute__(self.bl_idname)


class SvColorSocket(bpy.types.NodeSocket, OCVLSocketBase):
    '''For color data'''
    bl_idname = "SvColorSocket"
    bl_label = "Color Socket"

    prop = bpy.props.FloatVectorProperty(default=(0, 0, 0, 1), size=4, subtype='COLOR', min=0, max=1, update=process_from_socket)
    prop_name = bpy.props.StringProperty(default='')
    use_prop = bpy.props.BoolProperty(default=False)

    def get_prop_data(self):
        if self.prop_name:
            return {"prop_name": self.prop_name}
        elif self.use_prop:
            return {"use_prop": True,
                    "prop": self.prop[:]}
        else:
            return {}

    def sv_get(self, default=sentinel, deepcopy=True, implicit_conversions=None):
        if self.is_linked and not self.is_output:
            return self.convert_data(get_socket(self, deepcopy), implicit_conversions)

        if self.prop_name:
            return [[getattr(self.node, self.prop_name)[:]]]
        elif self.use_prop:
            return [[self.prop[:]]]
        elif default is sentinel:
            raise NoDataError(self)
        else:
            return default


class StringsSocket(bpy.types.NodeSocket, OCVLSocketBase):
    bl_idname = 'StringsSocket'
    bl_label = 'StringsSocket'


class ImageSocket(bpy.types.NodeSocket, OCVLSocketBase):
    bl_idname = 'ImageSocket'
    bl_label = 'ImageSocket'


class RectSocket(bpy.types.NodeSocket, OCVLSocketBase):
    bl_idname = 'RectSocket'
    bl_label = 'RectSocket'
    draw_socket_color = 0.1, 0.2, 0.2, 1


def register():
    ocvl_register(StringsSocket)
    ocvl_register(ImageSocket)
    ocvl_register(SvLinkNewNodeInput)
    ocvl_register(SvColorSocket)
    ocvl_register(RectSocket)


def unregister():
    ocvl_unregister(StringsSocket)
    ocvl_unregister(ImageSocket)
    ocvl_unregister(SvLinkNewNodeInput)
    ocvl_unregister(SvColorSocket)
    ocvl_unregister(RectSocket)
