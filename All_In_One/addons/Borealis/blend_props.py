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

'''
Contains custom blender properties for keeping track of Neverwinter specific data

@author: Erik Ylipää
'''
import bpy
import mathutils
from mathutils import Color

from . import basic_props
from . import props_classes
from . import node_props


def register():
    bpy.types.Object.nwn_props = bpy.props.PointerProperty(type=BorealisDummySettings)
    bpy.types.Mesh.nwn_props = bpy.props.PointerProperty(type=BorealisMeshSettings)
    bpy.types.Lamp.nwn_props = bpy.props.PointerProperty(type=BorealisLightSettings)
    bpy.types.Scene.nwn_props = bpy.props.PointerProperty(type=BorealisBasicProperties)


def unregister():
    pass


def get_nwn_props(obj):
    if obj.type == 'LAMP':
        return obj.data.nwn_props
    elif obj.type == 'MESH':
        return obj.data.nwn_props
    else:
        return obj.nwn_props


def get_node_props(obj):
    props = get_nwn_props(obj)
    node_type = props.nwn_node_type
    if node_type in ["trimesh", "skin", "danglymesh", "aabb", "light"]:
        return props.node_properties
    elif node_type == "dummy":
        return props.node_properties


def create_walkmesh_materials(ob):
     #Make sure the materials already exist, otherwise we create them
    for i, material in enumerate(basic_props.walkmesh_materials):
        if material["name"] not in bpy.data.materials:
            mat = bpy.data.materials.new(material["name"])
            mat.diffuse_color = material["color"]
            mat.specular_color = (mat.diffuse_color
                                  + Color((0.2, 0.2, 0.2)))
            mat["nwn_walkmesh_index"] = i
        else:
            mat = bpy.data.materials[material["name"]]
        if mat.name not in ob.data.materials:
            ob.data.materials.append(mat)


def remove_walkmesh_materials(ob):
    for i, mat in enumerate(basic_props.walkmesh_materials):
        if mat["name"] in ob.data.materials:
            index = ob.data.materials.keys().index(mat["name"])
            ob.data.materials.pop(index)


def add_properties(data_path, node_types, classname="BorealisNodeProps"):
    #We create a dynamic class to use for node properties
    attribute_dict = {"bl_idname": classname,
                      "bl_label": "Neverwinter Nights Node properties",
                      "properties": []}
    props = []
    for node_type in node_types:
        props.extend(node_props.GeometryNodeProperties.get_node_properties(node_type))
    props = set(props)

    #we build the attribute dictionary by using the definitions from borealis_mdl_definitions
    for prop in props:
        if  prop.blender_ignore:
            continue
        kwargs = {}
        kwargs["name"] = prop.name
        if prop.get_default_value():
            kwargs["default"] = prop.get_default_value()

        if isinstance(prop, props_classes.NumberProperty):
            if prop.max:
                kwargs["max"] = prop.max
            if prop.min:
                kwargs["min"] = prop.min

        if isinstance(prop, props_classes.VectorProperty):
            if prop.size:
                kwargs["size"] = prop.size

        ##The order of the cases are important since some properties are subtypes of other
        if isinstance(prop, props_classes.ColorProperty):
            kwargs["subtype"] = 'COLOR'
            attribute_dict[prop.name] = bpy.props.FloatVectorProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        elif isinstance(prop, props_classes.StringProperty):
            attribute_dict[prop.name] = bpy.props.StringProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        elif isinstance(prop, props_classes.FloatVectorProperty):
            attribute_dict[prop.name] = bpy.props.FloatVectorProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        elif isinstance(prop, props_classes.BooleanProperty):
            attribute_dict[prop.name] = bpy.props.BoolProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        elif isinstance(prop, props_classes.EnumProperty):
            items = prop.get_blender_items()
            kwargs["items"] = items
            attribute_dict[prop.name] = bpy.props.EnumProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        elif isinstance(prop, props_classes.IntProperty):
            attribute_dict[prop.name] = bpy.props.IntProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        elif isinstance(prop, props_classes.FloatProperty):
            attribute_dict[prop.name] = bpy.props.FloatProperty(**kwargs)
            attribute_dict["properties"].append(prop)

        if prop.name not in attribute_dict:
            print("Failed to add property %s of type %s" % (prop.name, prop.__class__))

    #we now create a dynamic class and register it so it will be usable by others
    node_props_class = type(classname, (bpy.types.PropertyGroup,), attribute_dict)
    bpy.utils.register_class(node_props_class)

    data_path.node_properties = bpy.props.PointerProperty(type=node_props_class)


class BorealisDummySettings(bpy.types.PropertyGroup):
    """
    Properties specific for the nwn models, gets attached to all objects.
    """
    node_types = ["dummy", "emitter", "reference"]
    nwn_node_type = bpy.props.EnumProperty(items=[(t, t, t) for t in node_types],
                                       name="Node Type",
                                       description="The NWN Node type of this object")

    is_nwn_object = bpy.props.BoolProperty(name="Is Neverwinter Nights Object",
                                   description="Toggles whether this object is "
                                                "an nwn object and should be "
                                                "included in exports",
                                   default=False)

    @classmethod
    def register(cls):
        add_properties(cls, cls.node_types, "BorealisDummyNodeProps")


class BorealisMeshSettings(bpy.types.PropertyGroup):
    """
    Properties specific for the nwn models, gets attached to all objects.
    """
    node_types = ["trimesh", "danglymesh", "skin", "aabb"]
    nwn_node_type = bpy.props.EnumProperty(items=[(t, t, t) for t in node_types],
                                       name="Node Type",
                                       description="The NWN Node type of this object")

    is_nwn_object = bpy.props.BoolProperty(name="Is Neverwinter Nights Object",
                                   description="Toggles whether this object is an nwn object and should be included in exports",
                                   default=False)

    danglymesh_vertexgroup = bpy.props.StringProperty(name="Dangle Mesh vertex group")

    @classmethod
    def register(cls):
        add_properties(cls, cls.node_types, "BorealisMeshNodeProps")


class BorealisLightSettings(bpy.types.PropertyGroup):
    """
    Properties specific for the nwn models, gets attached to all objects.
    """
    node_types = ["light"]
    nwn_node_type = bpy.props.EnumProperty(items=[(t, t, t) for t in node_types],
                                       name="Node Type",
                                       description="The NWN Node type of this object")

    is_nwn_object = bpy.props.BoolProperty(name="Is Neverwinter Nights Object",
                                   description="Toggles whether this object is an nwn object and should be included in exports",
                                   default=False)

    @classmethod
    def register(cls):
        add_properties(cls, cls.node_types, "BorealisLightNodeProps")


class AnimationEvent(bpy.types.PropertyGroup):
    def update_name(self, foo):
        self.name = "%s %.4g" % (self.type, self.time,)
    name = bpy.props.StringProperty(name="Name")
    events = ["cast", "hit", "blur_start", "blur_end",
              "snd_footstep", "snd_hitground", "draw_arrow", "draw_weapon"]
    type = bpy.props.EnumProperty(name="Event Type", items=[('cast', 'cast', 'cast'),
                                                        ('hit', 'hit', 'hit'),
                                                        ('blur_start', 'blur_start', 'blur_start'),
                                                        ('blur_end', 'blur_end', 'blur_end'),
                                                        ('snd_footstep', 'snd_footstep', 'snd_footstep'),
                                                        ('snd_hitground', 'snd_hitground', 'snd_hitground'),
                                                        ('draw_arrow', 'draw_arrow', 'draw_arrow'),
                                                        ('draw_weapon', 'draw_weapon', 'draw_weapon')],
                                  default="hit", update=update_name)
    time = bpy.props.FloatProperty(name="Event time",
                                   description="Time at which event occurs "
                                   "(in seconds)",
                                   default=0.5, min=0, step=0.1,
                                   precision=2, update=update_name)


class Animation(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name")
    start_marker_name = bpy.props.StringProperty(name="Start Marker")
    end_marker_name = bpy.props.StringProperty(name="End Marker")
    transtime = bpy.props.FloatProperty(name="Transition time", default=1)
    events = bpy.props.CollectionProperty(type=AnimationEvent)
    event_index = bpy.props.IntProperty(name="Current event")
    animroot = bpy.props.StringProperty(name="Animation root")

    #We save away the frames so we can recreate the markers if they are removed
    saved_start_frame = bpy.props.IntProperty(name="Original Start frame", default=1)
    saved_end_frame = bpy.props.IntProperty(name="Original End frame", default=1)

    ### Since the animations are tightly coupled to the markers
    ### dynamic properties are used for it's attributes
    def get_start_frame(self):
        return self.get_start_marker().frame

    def set_start_frame(self, value):
        self.saved_start_frame = value
        marker = self.get_start_marker()
        if not marker:
            marker = self.create_start_marker()
        marker.frame = value

    def create_start_marker(self):
        timeline_markers = bpy.context.scene.timeline_markers
        marker = timeline_markers.new(name=(self.name + "_start"))
        self.start_marker_name = marker.name
        marker.frame = self.saved_start_frame
        return marker

    def get_start_marker(self):
        if self.start_marker_name in bpy.context.scene.timeline_markers:
            return bpy.context.scene.timeline_markers[self.start_marker_name]
        else:
            return None

    def set_start_marker(self, value):
        self.start_marker_name = value.name

    def get_end_frame(self):
        return self.get_end_marker().frame

    def set_end_frame(self, value):
        self.saved_end_frame = value
        marker = self.get_end_marker()
        if not marker:
            marker = self.create_end_marker()
        marker.frame = value

    def create_end_marker(self):
        timeline_markers = bpy.context.scene.timeline_markers
        marker = timeline_markers.new(name=self.name + "_end")
        self.end_marker_name = marker.name
        marker.frame = self.saved_end_frame
        return marker

    def get_end_marker(self):
        if self.end_marker_name in bpy.context.scene.timeline_markers:
            return bpy.context.scene.timeline_markers[self.end_marker_name]
        else:
            return None

    def set_end_marker(self, value):
        self.end_marker_name = value.name

    end_marker = property(get_end_marker, set_end_marker)
    start_marker = property(get_start_marker, set_start_marker)
    end_frame = property(get_end_frame, set_end_frame)
    start_frame = property(get_start_frame, set_start_frame)


class BorealisBasicProperties(bpy.types.PropertyGroup):
    def get_classification_items(self, context):
        return [(c.lower(), c, c) for c in basic_props.classifications]

    classification = bpy.props.EnumProperty(items=get_classification_items,
                                            name="Classification",
                                            description="The classification of the current model")
    supermodel = bpy.props.StringProperty(name="Supermodel")
    animationscale = bpy.props.FloatProperty(name="Animation Scale", min=0, max=1000, default=1)
    root_object_name = bpy.props.StringProperty(name="Root object name")
    animations = bpy.props.CollectionProperty(type=Animation)
    animation_index = bpy.props.IntProperty(name="Index of currently selected animation", min=-1, default=-1)


class AnimationName(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Animation name", default="default")
