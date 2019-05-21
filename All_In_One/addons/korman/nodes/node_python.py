#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *
from contextlib import contextmanager
from pathlib import Path
from PyHSPlasma import *

from ..korlib import replace_python2_identifier
from .node_core import *
from .node_deprecated import PlasmaVersionedNode
from .. import idprops

_single_user_attribs = {
    "ptAttribBoolean", "ptAttribInt", "ptAttribFloat", "ptAttribString", "ptAttribDropDownList",
    "ptAttribSceneobject", "ptAttribDynamicMap", "ptAttribGUIDialog", "ptAttribExcludeRegion",
    "ptAttribWaveSet", "ptAttribSwimCurrent", "ptAttribAnimation", "ptAttribBehavior",
    "ptAttribMaterial", "ptAttribMaterialAnimation", "ptAttribGUIPopUpMenu", "ptAttribGUISkin",
    "ptAttribGrassShader",
}

_attrib2param = {
    "ptAttribInt": plPythonParameter.kInt,
    "ptAttribFloat": plPythonParameter.kFloat,
    "ptAttribBoolean": plPythonParameter.kBoolean,
    "ptAttribString": plPythonParameter.kString,
    "ptAttribDropDownList": plPythonParameter.kString,
    "ptAttribSceneobject": plPythonParameter.kSceneObject,
    "ptAttribSceneobjectList": plPythonParameter.kSceneObjectList,
    "ptAttribActivator": plPythonParameter.kActivator,
    "ptAttribActivatorList": plPythonParameter.kActivator,
    "ptAttribNamedActivator": plPythonParameter.kActivator,
    "ptAttribResponder": plPythonParameter.kResponder,
    "ptAttribResponderList": plPythonParameter.kResponder,
    "ptAttribNamedResponder": plPythonParameter.kResponder,
    "ptAttribDynamicMap": plPythonParameter.kDynamicText,
    "ptAttribGUIDialog": plPythonParameter.kGUIDialog,
    "ptAttribExcludeRegion": plPythonParameter.kExcludeRegion,
    "ptAttribAnimation": plPythonParameter.kAnimation,
    "ptAttribBehavior": plPythonParameter.kBehavior,
    "ptAttribMaterial": plPythonParameter.kMaterial,
    "ptAttribMaterialList": plPythonParameter.kMaterial,
    "ptAttribGUIPopUpMenu": plPythonParameter.kGUIPopUpMenu,
    "ptAttribGUISkin": plPythonParameter.kGUISkin,
    "ptAttribWaveSet": plPythonParameter.kWaterComponent,
    "ptAttribSwimCurrent": plPythonParameter.kSwimCurrentInterface,
    "ptAttribClusterList": plPythonParameter.kClusterComponent,
    "ptAttribMaterialAnimation": plPythonParameter.kMaterialAnimation,
    "ptAttribGrassShader": plPythonParameter.kGrassShaderComponent,
}

_attrib_key_types = {
    "ptAttribSceneobject": plFactory.ClassIndex("plSceneObject"),
    "ptAttribSceneobjectList": plFactory.ClassIndex("plSceneObject"),
    "ptAttribActivator": plFactory.ClassIndex("plLogicModifier"),
    "ptAttribActivatorList": plFactory.ClassIndex("plLogicModifier"),
    "ptAttribNamedActivator": plFactory.ClassIndex("plLogicModifier"),
    "ptAttribResponder": plFactory.ClassIndex("plResponderModifier"),
    "ptAttribResponderList": plFactory.ClassIndex("plResponderModifier"),
    "ptAttribNamedResponder": plFactory.ClassIndex("plResponderModifier"),
    "ptAttribDynamicMap": plFactory.ClassIndex("plDynamicTextMap"),
    "ptAttribGUIDialog": plFactory.ClassIndex("pfGUIDialogMod"),
    "ptAttribExcludeRegion": plFactory.ClassIndex("plExcludeRegionMod"),
    "ptAttribAnimation": plFactory.ClassIndex("plAGMasterMod"),
    "ptAttribBehavior": plFactory.ClassIndex("plMultistageBehMod"),
    "ptAttribMaterial": plFactory.ClassIndex("plLayer"),
    "ptAttribMaterialList": plFactory.ClassIndex("plLayer"),
    "ptAttribGUIPopUpMenu": plFactory.ClassIndex("pfGUIPopUpMenu"),
    "ptAttribGUISkin": plFactory.ClassIndex("pfGUISkin"),
    "ptAttribWaveSet": plFactory.ClassIndex("plWaveSet7"),
    "ptAttribSwimCurrent": (plFactory.ClassIndex("plSwimRegionInterface"),
                            plFactory.ClassIndex("plSwimCircularCurrentRegion"),
                            plFactory.ClassIndex("plSwimStraightCurrentRegion")),
    "ptAttribClusterList": plFactory.ClassIndex("plClusterGroup"),
    "ptAttribMaterialAnimation": plFactory.ClassIndex("plLayerAnimation"),
    "ptAttribGrassShader": plFactory.ClassIndex("plGrassShaderMod"),
}


class StringVectorProperty(bpy.types.PropertyGroup):
    value = StringProperty()


class PlasmaAttributeArguments(bpy.types.PropertyGroup):
    byObject = BoolProperty()
    default = StringProperty()
    options = CollectionProperty(type=StringVectorProperty)
    range_values = FloatVectorProperty(size=2)
    netForce = BoolProperty()
    netPropagate = BoolProperty()
    stateList = CollectionProperty(type=StringVectorProperty)
    visListId = IntProperty()
    visListStates = CollectionProperty(type=StringVectorProperty)

    def set_arguments(self, args):
        for name in args:
            if name == "byObject":
                self.byObject = bool(args[name])
            elif name == "default":
                self.default = str(args[name])
            elif name == "options":
                for option in args[name]:
                    item = self.options.add()
                    item.value = str(option)
            elif name in ("range", "rang"):
                self.range_values = args[name]
            elif name == "netForce":
                self.netForce = bool(args[name])
            elif name in ("netPropagate", "netProp"):
                self.netPropagate = bool(args[name])
            elif name == "stateList":
                for state in args[name]:
                    item = self.stateList.add()
                    item.value = str(state)
            elif name == "vislistid":
                self.visListId = int(args[name])
            elif name == "visliststates":
                for state in args[name]:
                    item = self.visListStates.add()
                    item.value = str(state)
            else:
                print("Unknown argument '{}' with value '{}'!".format(name, args[name]))


class PlasmaAttribute(bpy.types.PropertyGroup):
    attribute_id = IntProperty()
    attribute_type = StringProperty()
    attribute_name = StringProperty()
    attribute_description = StringProperty()

    # These shall be default values
    value_string = StringProperty()
    value_int = IntProperty()
    value_float = FloatProperty()
    value_bool = BoolProperty()

    # Special Arguments
    attribute_arguments = PointerProperty(type=PlasmaAttributeArguments)

    _simple_attrs = {
        "ptAttribString": "value_string",
        "ptAttribDropDownList": "value_string",
        "ptAttribInt": "value_int",
        "ptAttribFloat": "value_float",
        "ptAttribBoolean": "value_bool",
    }

    @property
    def is_simple_value(self):
        return self.attribute_type in self._simple_attrs

    def _get_simple_value(self):
        return getattr(self, self._simple_attrs[self.attribute_type])
    def _set_simple_value(self, value):
        setattr(self, self._simple_attrs[self.attribute_type], value)
    simple_value = property(_get_simple_value, _set_simple_value)


class PlasmaPythonFileNode(PlasmaVersionedNode, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaPythonFileNode"
    bl_label = "Python File"
    bl_width_default = 290

    def _poll_pytext(self, value):
        return value.name.endswith(".py")

    def _update_pyfile(self, context):
        if self.no_update:
            return
        text_id = bpy.data.texts.get(self.filename, None)
        if text_id:
            self.text_id = text_id

    def _update_pytext(self, context):
        if self.no_update:
            return
        with self.NoUpdate():
            self.filename = self.text_id.name if self.text_id is not None else ""
            self.attributes.clear()
            self.inputs.clear()
        if self.text_id is not None:
            bpy.ops.node.plasma_attributes_to_node(node_path=self.node_path, text_path=self.text_id.name)

    filename = StringProperty(name="File Name",
                              description="Python Filename",
                              update=_update_pyfile)
    filepath = StringProperty(options={"HIDDEN"})
    text_id = PointerProperty(name="Script File",
                              description="Script file datablock",
                              type=bpy.types.Text,
                              poll=_poll_pytext,
                              update=_update_pytext)

    # This property exists for UI purposes ONLY
    package = BoolProperty(options={"HIDDEN", "SKIP_SAVE"})

    attributes = CollectionProperty(type=PlasmaAttribute, options={"HIDDEN"})
    no_update = BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    @property
    def attribute_map(self):
        return { i.attribute_id: i for i in self.attributes }

    def draw_buttons(self, context, layout):
        main_row = layout.row(align=True)
        row = main_row.row(align=True)
        row.alert = self.text_id is None and bool(self.filename)
        row.prop(self, "text_id", text="Script")

        # open operator
        sel_text = "Load Script" if self.text_id is None else ""
        operator = main_row.operator("file.plasma_file_picker", icon="FILESEL", text=sel_text)
        operator.filter_glob = "*.py"
        operator.data_path = self.node_path
        operator.filename_property = "filename"

        if self.text_id is not None:
            # package button
            row = main_row.row(align=True)
            if self.text_id is not None:
                row.enabled = True
                icon = "PACKAGE" if self.text_id.plasma_text.package else "UGLYPACKAGE"
                row.prop(self.text_id.plasma_text, "package", icon=icon, text="")
            else:
                row.enabled = False
                row.prop(self, "package", text="", icon="UGLYPACKAGE")
            # rescan operator
            row = main_row.row(align=True)
            row.enabled = self.text_id is not None
            operator = row.operator("node.plasma_attributes_to_node", icon="FILE_REFRESH", text="")
            if self.text_id is not None:
                operator.text_path = self.text_id.name
                operator.node_path = self.node_path

        # This could happen on an upgrade
        if self.text_id is None and self.filename:
            layout.label(text="Script '{}' is not loaded in Blender".format(self.filename), icon="ERROR")

    def get_key(self, exporter, so):
        return exporter.mgr.find_create_key(plPythonFileMod, name=self.key_name, so=so)

    def export(self, exporter, bo, so):
        pfm = self.get_key(exporter, so).object
        py_name = Path(self.filename).stem
        pfm.filename = py_name

        # Check to see if we should pack this file
        if exporter.output.want_py_text(self.text_id):
            exporter.report.msg("Including Python '{}' for package", self.filename, indent=3)
            exporter.output.add_python_mod(self.filename, text_id=self.text_id)
            # PFMs can have their own SDL...
            sdl_text = bpy.data.texts.get("{}.sdl".format(py_name), None)
            if sdl_text is not None:
                exporter.report.msg("Including corresponding SDL '{}'", sdl_text.name, indent=3)
                exporter.output.add_sdl(sdl_text.name, text_id=sdl_text)

        # Handle exporting the Python Parameters
        attrib_sockets = (i for i in self.inputs if i.is_linked)
        for socket in attrib_sockets:
            attrib = socket.attribute_type
            from_node = socket.links[0].from_node

            value = from_node.value if socket.is_simple_value else from_node.get_key(exporter, so)
            if not isinstance(value, tuple):
                value = (value,)
            for i in value:
                param = plPythonParameter()
                param.id = socket.attribute_id
                param.valueType = _attrib2param[attrib]
                param.value = i

                # Key type sanity checking... Because I trust no user.
                if not socket.is_simple_value:
                    if i is None:
                        msg = "'{}' Node '{}' didn't return a key and therefore will be unavailable to Python".format(
                            self.id_data.name, from_node.name)
                        exporter.report.warn(msg, indent=3)
                    else:
                        key_type = _attrib_key_types[attrib]
                        if isinstance(key_type, tuple):
                            good_key = i.type in key_type
                        else:
                            good_key = i.type == key_type
                        if not good_key:
                            msg = "'{}' Node '{}' returned an unexpected key type '{}'".format(
                                self.id_data.name, from_node.name, plFactory.ClassName(i.type))
                            exporter.report.warn(msg, indent=3)
                pfm.addParameter(param)

    def _get_attrib_sockets(self, idx):
        for i in self.inputs:
            if i.attribute_id == idx:
                yield i

    @property
    def key_name(self):
        # PFM names ***must*** be valid Python identifiers, but Blender likes inserting
        # periods into the object names "Foo.001" -- this causes bad internal chaos in PotS
        return replace_python2_identifier("{}_{}".format(self.id_data.name, self.name))

    def _make_attrib_socket(self, attrib, is_init=False):
        new_pos = len(self.inputs)
        if not is_init:
            for i, socket in enumerate(self.inputs):
                if attrib.attribute_id < socket.attribute_id:
                    new_pos = i
                    break
        old_pos = len(self.inputs)
        socket = self.inputs.new("PlasmaPythonFileNodeSocket", attrib.attribute_name)
        socket.attribute_id = attrib.attribute_id
        if not is_init and new_pos != old_pos:
            self.inputs.move(old_pos, new_pos)

    @contextmanager
    def NoUpdate(self):
        self.no_update = True
        try:
            yield self
        finally:
            self.no_update = False

    def update(self):
        if self.no_update:
            return
        with self.NoUpdate():
            # First, we really want to make sure our junk matches up. Yes, this does dupe what
            # happens in PlasmaAttribNodeBase, but we can link much more than those node types...
            toasty_sockets = []
            input_nodes = (i for i in self.inputs if i.is_linked and i.links)
            for i in input_nodes:
                link = i.links[0]
                allowed_attribs = getattr(link.from_node, "pl_attrib", set())
                if i.attribute_type not in allowed_attribs:
                    self.id_data.links.remove(link)
                    # Bad news, old chap... Even though we're doing this before we figure out
                    # how many socket we need, the changes won't be committed to the socket's links
                    # until later. damn. We'll have to track it manually
                    toasty_sockets.append(i)

            attribs = self.attribute_map
            empty = not self.inputs
            for idx in sorted(attribs):
                attrib = attribs[idx]

                # Delete any attribute sockets whose type changed
                for i in self._get_attrib_sockets(idx):
                    if i.attribute_type != attrib.attribute_type:
                        self.inputs.remove(i)

                # Fetch the list of sockets again because we may have nuked some
                inputs = list(self._get_attrib_sockets(idx))
                if not inputs:
                    self._make_attrib_socket(attrib, empty)
                elif attrib.attribute_type not in _single_user_attribs:
                    unconnected = [socket for socket in inputs if not socket.is_linked or socket in toasty_sockets]
                    if not unconnected:
                        self._make_attrib_socket(attrib, empty)
                    while len(unconnected) > 1:
                        self.inputs.remove(unconnected.pop())

    @property
    def latest_version(self):
        return 2

    def upgrade(self):
        # In version 1 of this node, Python scripts were referenced by their filename in the
        # python package and by their path on the local machine. This created an undue dependency
        # on the artist's environment. In version 2, we will use Blender's text data blocks to back
        # Python scripts. It is still legal to export Python File nodes that are not backed by a script.
        if self.version == 1:
            text_id = bpy.data.texts.get(self.filename, None)
            if text_id is None:
                path = Path(self.filepath)
                try:
                    if path.exists():
                        text_id = bpy.data.texts.load(self.filepath)
                except OSError:
                    pass
            with self.NoUpdate():
                self.text_id = text_id
            self.property_unset("filepath")
            self.version = 2


class PlasmaPythonFileNodeSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    attribute_id = IntProperty(options={"HIDDEN"})

    @property
    def attribute_description(self):
        return self.node.attribute_map[self.attribute_id].attribute_description

    @property
    def attribute_name(self):
        return self.node.attribute_map[self.attribute_id].attribute_name

    @property
    def attribute_type(self):
        return self.node.attribute_map[self.attribute_id].attribute_type

    def draw(self, context, layout, node, text):
        layout.alignment = "LEFT"
        layout.label("ID: {}".format(self.attribute_id))
        layout.label(self.attribute_description)

    def draw_color(self, context, node):
        return _attrib_colors.get(self.attribute_type, (0.0, 0.0, 0.0, 1.0))

    @property
    def is_simple_value(self):
        return self.node.attribute_map[self.attribute_id].is_simple_value

    @property
    def simple_value(self):
        return self.node.attribute_map[self.attribute_id].simple_value

    @property
    def attribute_arguments(self):
        return self.node.attribute_map[self.attribute_id].attribute_arguments


class PlasmaPythonAttribNodeSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    def draw(self, context, layout, node, text):
        attrib = node.to_socket
        if attrib is None:
            layout.label(text)
        else:
            layout.label("ID: {}".format(attrib.attribute_id))

    def draw_color(self, context, node):
        return _attrib_colors.get(node.pl_attrib, (0.0, 0.0, 0.0, 1.0))


class PlasmaPythonReferenceNodeSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.031, 0.110, 0.290, 1.0)


class PlasmaAttribNodeBase(PlasmaNodeBase):
    def init(self, context):
        self.outputs.new("PlasmaPythonAttribNodeSocket", "Python File", "pfm")

    @property
    def attribute_name(self):
        attr = self.to_socket
        return "Value" if attr is None else attr.attribute_name

    @property
    def to_socket(self):
        """Returns the socket linked to IF only one link has been made"""
        socket = self.outputs[0]
        if len(socket.links) == 1:
            return socket.links[0].to_socket
        return None

    @classmethod
    def register(cls):
        pl_attrib = cls.pl_attrib
        if isinstance(pl_attrib, tuple):
            color = _attrib_colors.get(pl_attrib, None)
            if color is not None:
                for i in pl_attrib:
                    _attrib_colors[i] = color

    def update(self):
        pl_id = self.pl_attrib
        socket = self.outputs[0]
        for link in socket.links:
            if link.to_node.bl_idname != "PlasmaPythonFileNode":
                self.id_data.links.remove(link)
            if isinstance(pl_id, tuple):
                if link.to_socket.attribute_type not in pl_id:
                    self.id_data.links.remove(link)
            else:
                if pl_id != link.to_socket.attribute_type:
                    self.id_data.links.remove(link)


class PlasmaAttribBoolNode(PlasmaAttribNodeBase, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaAttribBoolNode"
    bl_label = "Boolean Attribute"

    def _on_update(self, context):
        self.inited = True

    pl_attrib = "ptAttribBoolean"
    pl_label_attrib = "value"
    value = BoolProperty()
    inited = BoolProperty(options={"HIDDEN"})

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text=self.attribute_name)

    def update(self):
        super().update()
        attrib = self.to_socket
        if attrib is not None and not self.inited:
            self.value = attrib.simple_value
            self.inited = True


class PlasmaAttribDropDownListNode(PlasmaAttribNodeBase, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaAttribDropDownListNode"
    bl_label = "Drop Down List Attribute"

    pl_attrib = "ptAttribDropDownList"
    pl_label_attrib = "value"

    def _list_items(self, context):
        attrib = self.to_socket
        if attrib is not None:
            return [(option.value, option.value, "") for option in attrib.attribute_arguments.options]
        else:
            return []
    value = EnumProperty(items=_list_items)

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text=self.attribute_name)

    def update(self):
        super().update()
        attrib = self.to_socket
        if attrib is not None and not self.value:
            self.value = attrib.simple_value


class PlasmaAttribIntNode(PlasmaAttribNodeBase, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaAttribIntNode"
    bl_label = "Numeric Attribute"

    def _get_int(self):
        return round(self.value_float)
    def _set_int(self, value):
        self.value_float = float(value)
    def _on_update_float(self, context):
        self.inited = True

    pl_attrib = ("ptAttribFloat", "ptAttribInt")
    pl_label_attrib = "value"
    value_int = IntProperty(get=_get_int, set=_set_int, options={"HIDDEN"})
    value_float = FloatProperty(update=_on_update_float, options={"HIDDEN"})
    inited = BoolProperty(options={"HIDDEN"})

    def init(self, context):
        super().init(context)
        # because we're trying to be for both int and float...
        self.outputs[0].link_limit = 1

    def draw_buttons(self, context, layout):
        attrib = self.to_socket

        if attrib is None:
            layout.prop(self, "value_int", text="Value")
        elif attrib.attribute_type == "ptAttribFloat":
            self._range_label(layout)
            layout.alert = self._out_of_range(self.value_float)
            layout.prop(self, "value_float", text=attrib.name)
        elif attrib.attribute_type == "ptAttribInt":
            self._range_label(layout)
            layout.alert = self._out_of_range(self.value_int)
            layout.prop(self, "value_int", text=attrib.name)
        else:
            raise RuntimeError()

    def update(self):
        super().update()
        attrib = self.to_socket
        if attrib is not None and not self.inited:
            self.value = attrib.simple_value
            self.inited = True

    def _get_value(self):
        attrib = self.to_socket
        if attrib is None or attrib.attribute_type == "ptAttribInt":
            return self.value_int
        else:
            return self.value_float
    def _set_value(self, value):
        self.value_float = value
    value = property(_get_value, _set_value)

    def _range_label(self, layout):
        attrib = self.to_socket
        layout.label(text="Range: [{}, {}]".format(attrib.attribute_arguments.range_values[0], attrib.attribute_arguments.range_values[1]))

    def _out_of_range(self, value):
        attrib = self.to_socket
        if attrib.attribute_arguments.range_values[0] == attrib.attribute_arguments.range_values[1]:
            # Ignore degenerate intervals
            return False
        if attrib.attribute_arguments.range_values[0] <= value <= attrib.attribute_arguments.range_values[1]:
            return False
        return True


class PlasmaAttribObjectNode(idprops.IDPropObjectMixin, PlasmaAttribNodeBase, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaAttribObjectNode"
    bl_label = "Object Attribute"

    pl_attrib = ("ptAttribSceneobject", "ptAttribSceneobjectList", "ptAttribAnimation",
                 "ptAttribSwimCurrent", "ptAttribWaveSet")

    target_object = PointerProperty(name="Object",
                                    description="Object containing the required data",
                                    type=bpy.types.Object)

    def init(self, context):
        super().init(context)
        # keep the code simple
        self.outputs[0].link_limit = 1

    def draw_buttons(self, context, layout):
        layout.prop(self, "target_object", text=self.attribute_name)

    def get_key(self, exporter, so):
        attrib = self.to_socket
        if attrib is None:
            self.raise_error("must be connected to a Python File node!")
        attrib = attrib.attribute_type

        bo = self.target_object
        if bo is None:
            self.raise_error("Target object must be specified")
        ref_so_key = exporter.mgr.find_create_key(plSceneObject, bl=bo)
        ref_so = ref_so_key.object

        # Add your attribute type handling here...
        if attrib in {"ptAttribSceneobject", "ptAttribSceneobjectList"}:
            return ref_so_key
        elif attrib == "ptAttribAnimation":
            anim = bo.plasma_modifiers.animation
            agmod = exporter.mgr.find_create_key(plAGModifier, so=ref_so, name=anim.key_name)
            agmaster = exporter.mgr.find_create_key(plAGMasterModifier, so=ref_so, name=anim.key_name)
            return agmaster
        elif attrib == "ptAttribSwimCurrent":
            swimregion = bo.plasma_modifiers.swimregion
            return swimregion.get_key(exporter, ref_so)
        elif attrib == "ptAttribWaveSet":
            waveset = bo.plasma_modifiers.water_basic
            if not waveset.enabled:
                self.raise_error("water modifier not enabled on '{}'".format(self.object_name))
            return exporter.mgr.find_create_key(plWaveSet7, so=ref_so, bl=bo)

    @classmethod
    def _idprop_mapping(cls):
        return {"target_object": "object_name"}


class PlasmaAttribStringNode(PlasmaAttribNodeBase, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaAttribStringNode"
    bl_label = "String Attribute"

    pl_attrib = "ptAttribString"
    pl_label_attrib = "value"
    value = StringProperty()

    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text=self.attribute_name)

    def update(self):
        super().update()
        attrib = self.to_socket
        if attrib is not None and not self.value:
            self.value = attrib.simple_value


class PlasmaAttribTextureNode(idprops.IDPropMixin, PlasmaAttribNodeBase, bpy.types.Node):
    bl_category = "PYTHON"
    bl_idname = "PlasmaAttribTextureNode"
    bl_label = "Texture Attribute"
    bl_width_default = 175

    pl_attrib = ("ptAttribMaterial", "ptAttribMaterialList",
                 "ptAttribDynamicMap", "ptAttribMaterialAnimation")

    def _poll_texture(self, value):
        if self.material is not None:
            # is this the type of dealio that we're looking for?
            attrib = self.to_socket
            if attrib is not None:
                attrib = attrib.attribute_type
                if attrib == "ptAttribDynamicMap":
                    if not self._is_dyntext(value):
                        return False
                elif attrib == "ptAttribMaterialAnimation":
                    if not self._is_animated(self.material, value):
                        return False

            # must be a legal option... but is it a member of this material?
            return value.name in self.material.texture_slots
        return False

    material = PointerProperty(name="Material",
                               description="Material the texture is attached to",
                               type=bpy.types.Material)
    texture = PointerProperty(name="Texture",
                              description="Texture to expose to Python",
                              type=bpy.types.Texture,
                              poll=_poll_texture)

    def init(self, context):
        super().init(context)
        # keep the code simple
        self.outputs[0].link_limit = 1

    def draw_buttons(self, context, layout):
        layout.prop(self, "material")
        if self.material is not None:
            layout.prop(self, "texture")

    def get_key(self, exporter, so):
        if self.material is None:
            self.raise_error("Material must be specified")
        if self.texture is None:
            self.raise_error("Texture must be specified")

        attrib = self.to_socket
        if attrib is None:
            self.raise_error("must be connected to a Python File node!")
        attrib = attrib.attribute_type
        material = self.material
        texture = self.texture

        # Your attribute stuff here...
        if attrib == "ptAttribDynamicMap":
            if not self._is_dyntext(texture):
                self.raise_error("Texture '{}' is not a Dynamic Text Map".format(self.texture_name))
            name = "{}_{}_DynText".format(material.name, texture.name)
            return exporter.mgr.find_create_key(plDynamicTextMap, name=name, so=so)
        elif self._is_animated(material, texture):
            name = "{}_{}_LayerAnim".format(material_name, texture.name)
            return exporter.mgr.find_create_key(plLayerAnimation, name=name, so=so)
        else:
            name = "{}_{}".format(material.name, texture.name)
            return exporter.mgr.find_create_key(plLayer, name=name, so=so)

    @classmethod
    def _idprop_mapping(cls):
        return {"material": "material_name",
                "texture": "texture_name"}

    def _idprop_sources(self):
        return {"material_name": bpy.data.materials,
                "texture_name": bpy.data.textures}

    def _is_animated(self, material, texture):
        return   ((material.animation_data is not None and material.animation_data.action is not None)
               or (texture.animation_data is not None and texture.animation_data.action is not None))

    def _is_dyntext(self, texture):
        return texture.type == "IMAGE" and texture.image is None


_attrib_colors = {
    "ptAttribActivator": (0.188, 0.086, 0.349, 1.0),
    "ptAttribActivatorList": (0.188, 0.086, 0.349, 1.0),
    "ptAttribBoolean": (0.71, 0.706, 0.655, 1.0),
    "ptAttribExcludeRegion": (0.031, 0.110, 0.290, 1.0),
    "ptAttribDropDownList": (0.475, 0.459, 0.494, 1.0),
    "ptAttribNamedActivator": (0.188, 0.086, 0.349, 1.0),
    "ptAttribNamedResponder": (0.031, 0.110, 0.290, 1.0),
    "ptAttribResponder": (0.031, 0.110, 0.290, 1.0),
    "ptAttribResponderList": (0.031, 0.110, 0.290, 1.0),
    "ptAttribString": (0.675, 0.659, 0.494, 1.0),

    PlasmaAttribIntNode.pl_attrib: (0.443, 0.439, 0.392, 1.0),
    PlasmaAttribObjectNode.pl_attrib: (0.565, 0.267, 0.0, 1.0),
    PlasmaAttribTextureNode.pl_attrib: (0.035, 0.353, 0.0, 1.0),
}
