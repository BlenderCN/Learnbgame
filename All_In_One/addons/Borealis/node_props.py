# -*- coding: utf-8 -*-
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
Contains definitions of node properties as allowed in Neverwinter Nights.

This module contains definitions of allowed node properties and how they
should be treated in Blender.

@author: Erik Ylipää
'''
from . import props_classes
from .props_classes import *


class NodeProperties():
    node_types = None
    props_list = None
    props_dict = None
    gui_groups = None
    node_gui_groups = None

    @classmethod
    def build_dictionary(cls):
        cls.props_dict = {}
        if cls.props_list:
            for prop in cls.props_list:
                for node in prop.nodes:
                    if node in cls.props_dict:
                        cls.props_dict[node].append(prop)
                    else:
                        cls.props_dict[node] = [prop]

    @classmethod
    def get_node_properties(cls, node_type):
        if not cls.props_dict:
            cls.build_dictionary()
        return cls.props_dict[node_type]

    @classmethod
    def get_properties(cls):
        return cls.props_list

    @classmethod
    def get_node_types(cls):
        if not cls.node_types:
            cls.build_types()
        return cls.node_types

    @classmethod
    def build_types(cls):
        if not cls.props_dict:
            cls.build_dictionary()
        cls.node_types = cls.props_dict.keys()

    @classmethod
    def get_gui_groups(cls):
        if not cls.gui_groups:
            cls.gui_groups = {"default": []}
            for prop in cls.props_list:
                if prop.gui_group:
                    if prop.gui_group not in cls.gui_groups:
                        cls.gui_groups[prop.gui_group] = []
                    cls.gui_groups[prop.gui_group].append(prop)
                else:
                    cls.gui_groups["default"].append(prop)
        return cls.gui_groups

    @classmethod
    def get_node_gui_groups(cls, node_type):
        if not cls.node_gui_groups:
            cls.build_node_gui_groups()
        return cls.node_gui_groups[node_type]

    @classmethod
    def build_node_gui_groups(cls):
        cls.node_gui_groups = {}
        for node_type in cls.get_node_types():
            props = []
            group_dict = {"props": props, "subgroups": {}}
            for prop in cls.get_node_properties(node_type):
                if isinstance(prop.gui_group, list):
                    #if the gui_group attribute is a list, the prop is in a nested group
                    groups = prop.gui_group[:]
                    current_group = group_dict
                    while(groups):
                        subgroup = groups.pop(0)
                        if subgroup not in current_group["subgroups"]:
                            current_group["subgroups"][subgroup] = {"props": [], "subgroups": {}}
                        current_group = current_group["subgroups"][subgroup]
                    if prop not in current_group["props"]:
                        current_group["props"].append(prop)
                else:
                    #If gui_group is not a list, the prop is in the first level
                    if prop.gui_group not in group_dict["subgroups"]:
                        group_dict["subgroups"][prop.gui_group] = {"props": [], "subgroups": {}}
                    group_dict["subgroups"][prop.gui_group]["props"].append(prop)
            cls.node_gui_groups[node_type] = group_dict


class GeometryNodeProperties(NodeProperties):
    """ Class for collecting all geometry-node properties
    """
    props_list = [StringProperty(name="parent", nodes=["dummy", "trimesh", "danglymesh", "skin", "emitter", "light", "aabb", "reference"], blender_ignore=True),
                FloatVectorProperty(name="position", nodes=["dummy", "trimesh", "danglymesh", "skin", "aabb", "emitter", "light", "reference"], blender_ignore=True),
                FloatVectorProperty(name="orientation", nodes=["dummy", "trimesh", "danglymesh", "skin", "aabb", "emitter", "light", "reference"], blender_ignore=True),

                ### mesh ###
                ColorProperty(name="ambient", nodes=["trimesh", "danglymesh", "skin", "aabb"], gui_group=["Material settings", "Colors"]),
                ColorProperty(name="diffuse", nodes=["trimesh", "danglymesh", "skin", "aabb"], gui_group=["Material settings", "Colors"]),
                ColorProperty(name="specular", nodes=["trimesh", "danglymesh", "skin", "aabb"], gui_group=["Material settings", "Colors"]),
                IntProperty(name="shininess", nodes=["trimesh", "danglymesh", "skin", "aabb"], gui_group="Material settings", default=26, min=0, max=255),
                FloatProperty(name="alpha", nodes=["trimesh", "danglymesh", "skin"], gui_group="Material settings", min=0, max=1, default=1),
                ColorProperty(name="selfillumcolor", nodes=["trimesh", "danglymesh", "skin"], gui_name="Self illumination color", gui_group="Material settings"),

                BooleanProperty(name="shadow", nodes=["trimesh", "danglymesh", "skin", "aabb"], default=True, gui_group="Render Options"),
                BooleanProperty(name='beaming', nodes=["trimesh", "danglymesh", "skin"], default=False, gui_group="Render Options"),
                BooleanProperty(name='rotatetexture', nodes=["trimesh", "danglymesh", "skin"], default=False, gui_group="Render Options"),
                EnumProperty(name='tilefade', nodes=["trimesh", "danglymesh", "skin"], default="Don't fade", gui_group="Render Options", enums={"Don't fade": 0, "Fade": 1, "Neighbour": 2, "Base": 4}),

                StringProperty(name="bitmap", nodes=["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatMatrixProperty(name="verts", nodes=["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                FloatMatrixProperty(name="tverts", nodes=["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),
                IntMatrixProperty(name="faces", nodes=["trimesh", "danglymesh", "skin", "aabb"], blender_ignore=True),

                FloatProperty(name="scale", nodes=["trimesh", "danglymesh", "skin"], default=1),
                BooleanProperty(name='transparencyhint', nodes=["trimesh", "danglymesh", "skin", "aabb"], default=False),
                BooleanProperty(name='inheritcolor', nodes=["trimesh", "danglymesh", "skin"], default=False),
                FloatVectorProperty(name='center', nodes=["trimesh", "danglymesh", "skin"]),
                ColorProperty(name="wireocolor", nodes=["trimesh", "danglymesh", "skin", "aabb", "reference"]),
                BooleanProperty(name='render',
                                nodes=["trimesh", "danglymesh", "skin"],
                                default=True,
                                gui_group="Render Options",
                                description="If render is on, then the part "
                                    "renders, if it is not then it doesn't. "
                                    "The geometry is still in memory though, "
                                    "it is not culled. Use this in conjunction "
                                    "with the shadows checkbox to make simpler "
                                    "shadow volume objects than the visible "
                                    "geometry."),
                FloatMatrixProperty(name='colors', nodes=["trimesh", "danglymesh", "skin"], blender_ignore=True),

                ### danglymesh ###
                FloatProperty(name="displacement", nodes=["danglymesh"], gui_group="Dangly Mesh settings", min=0),
                IntProperty(name="period", nodes=["danglymesh"], gui_group="Dangly Mesh settings", min=0, default=6),
                IntProperty(name="tightness", nodes=["danglymesh"], gui_group="Dangly Mesh settings", min=0),
                IntMatrixProperty(name="constraints", nodes=["danglymesh"], blender_ignore=True),

                ### skin ###
                MatrixProperty(name="weights", nodes=["skin"], blender_ignore=True),

                ### aabb ###
                AABBTree("aabb", nodes=["aabb"], blender_ignore=True),

                ### Emitter properties ###
                ColorProperty(name='colorstart', nodes=["emitter"], gui_group="Particles", gui_name="Color Start"),
                ColorProperty(name='colorend', nodes=["emitter"], gui_group="Particles", gui_name="Color End"),
                FloatProperty(name='alphastart', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='alphaend', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='sizestart', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='sizeend', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='sizestart_y', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='sizeend_y', nodes=["emitter"], gui_group="Particles"),
                IntProperty(name='birthrate', nodes=["emitter"], gui_group="Particles"),
                EnumProperty(name='spawntype', nodes=["emitter"], enums={"Normal": 0, "Trail": 1}),
                FloatProperty(name='lifeexp', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='mass', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='spread', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='particlerot', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='velocity', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='randvel', nodes=["emitter"], gui_group="Particles"),
                BooleanProperty(name='bounce', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='bounce_co', nodes=["emitter"], gui_group="Particles"),
                BooleanProperty(name='loop', nodes=["emitter"], gui_group="Particles"),
                FloatProperty(name='blurlength', nodes=["emitter"], gui_group="Particles"),
                EnumProperty(name='affectedbywind', nodes=["emitter"], enums=['true', 'false'], gui_group="Particles"),
                BooleanProperty(name='m_istinted', nodes=["emitter"], gui_group="Particles", gui_name="Tinted"),
                BooleanProperty(name='splat', nodes=["emitter"], gui_group="Particles"),

                IntProperty(name='framestart', nodes=["emitter"], gui_group="Animation"),
                IntProperty(name='frameend', nodes=["emitter"], gui_group="Animation"),
                IntProperty(name='fps', nodes=["emitter"], gui_group="Animation", gui_name="Speed (fps)"),
                IntProperty(name='xgrid', nodes=["emitter"], gui_group="Animation", gui_name="Grid width"),
                IntProperty(name='ygrid', nodes=["emitter"], gui_group="Animation", gui_name="Grid height"),
                BooleanProperty(name='random', nodes=["emitter"], gui_group="Animation", gui_name="Random playback"),
                BooleanProperty(name='inherit', nodes=["emitter"], gui_group="Inherit Properties", gui_name="Inherit"),
                BooleanProperty(name='inherit_local', nodes=["emitter"], gui_group="Inherit Properties"),
                BooleanProperty(name='inherit_part', nodes=["emitter"], gui_group="Inherit Properties"),
                BooleanProperty(name='inheritvel', nodes=["emitter"], gui_group="Inherit Properties"),
                IntProperty(name='xsize', nodes=["emitter"], gui_group="Emitter Size", gui_name="X-size"),
                IntProperty(name='ysize', nodes=["emitter"], gui_group="Emitter Size", gui_name="Y-size"),

                EnumProperty(name='update', nodes=["emitter"],
                             enums=["Fountain", "Single", "Explosion", "Lightning"], gui_group="Styles"),
                EnumProperty(name='render', nodes=["emitter"],
                             enums=["Normal", "Linked",
                                    "Billboard_to_Local_Z",
                                    "Billboard_to_World_Z",
                                    "Aligned_to_World_Z",
                                    "Aligned_to_Particle_Dir",
                                    "Motion_Blur"],
                             gui_group="Styles"),
                EnumProperty(name='blend', nodes=["emitter"],
                             enums={"normal": "Normal",
                                      "lighten": "Lighten",
                                      "diffuse": "Diffuse",
                                      "punch-through": "Punch-Through"},
                             gui_group="Styles"),
                BooleanProperty(name='update_sel', nodes=["emitter"], gui_group="Styles"),
                BooleanProperty(name='render_sel', nodes=["emitter"], gui_group="Styles"),
                BooleanProperty(name='blend_sel', nodes=["emitter"], gui_group="Styles"),
                FloatProperty(name='deadspace', nodes=["emitter"], gui_group="Miscellaneous"),
                FloatProperty(name='combinetime', nodes=["emitter"], gui_group="Miscellaneous"),
                FloatProperty(name='threshold', nodes=["emitter"], gui_group="Miscellaneous"),
                IntProperty(name='renderorder', nodes=["emitter"], gui_group="Miscellaneous"),

                FloatProperty(name='opacity', nodes=["emitter"]),

                FloatProperty(name='lightningdelay', nodes=["emitter"], gui_group="Lightning Properties"),
                FloatProperty(name='lightningradius', nodes=["emitter"], gui_group="Lightning Properties"),
                FloatProperty(name='lightningscale', nodes=["emitter"], gui_group="Lightning Properties"),
                FloatProperty(name='blastradius', nodes=["emitter"], gui_group="Blast Properties"),
                FloatProperty(name='blastlength', nodes=["emitter"], gui_group="Blast Properties"),

                BooleanProperty(name='p2p', nodes=["emitter"], gui_group="P2P Properties"),
                BooleanProperty(name='p2p_sel', nodes=["emitter"], gui_group="P2P Properties"),
                EnumProperty(name='p2p_type', nodes=["emitter"], enums=["Bezier", "Gravity"], gui_group="P2P Properties"),
                FloatProperty(name='p2p_bezier2', nodes=["emitter"], gui_group="P2P Properties"),
                FloatProperty(name='p2p_bezier3', nodes=["emitter"], gui_group="P2P Properties"),
                FloatProperty(name='drag', nodes=["emitter"], gui_group="P2P Properties"),
                FloatProperty(name='grav', nodes=["emitter"], gui_group="P2P Properties"),

                StringProperty(name='texture', nodes=["emitter"], gui_group="Texture Properties"),
                BooleanProperty(name='twosidedtex', nodes=["emitter"], gui_group="Texture Properties"),

                ### Light properties ###
                BooleanProperty(name='ambientonly', nodes=["light"]),        # This controls if the light is only an ambient lightsource or if it is directional as well.
                BooleanProperty(name='shadow', nodes=["light"]),        # Probably determines if this light is capable of casting shadows.
                BooleanProperty(name='isdynamic', nodes=["light"]),       # Unknown.
                BooleanProperty(name='affectdynamic', nodes=["light"]),        # Unknown.
                IntProperty(name='lightpriority', nodes=["light"], min=1, max=5),
                BooleanProperty(name='fadinglight', nodes=["light"]),        # Unknown. Might activate some kind of distance fall off for the light. Or it could do just about anything.
                BooleanProperty(name='lensflares', nodes=["light"]),            # Possibly causes the light source to produce a lens flare effect,' sounds cool anyway.
                FloatProperty(name='flareradius', nodes=["light"]),
                ColorProperty(name='color', nodes=["light"], blender_ignore=True),        # The color of the light source.
                FloatProperty(name='multiplier', nodes=["light"]),  # Unknown
                FloatProperty(name='radius', nodes=["light"], blender_ignore=True),        # Probably the range of the light.

                ### Reference Properties ###
                StringProperty(name='refModel', nodes=["reference"]),
                BooleanProperty(name='reattachable', nodes=["reference"]),
                ]


class AnimationNodeProperties(NodeProperties):
    """
    Class containing all animation node properties
    """

    props_list = [  # general properties
                  StringProperty(name="parent", nodes=["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"], blender_ignore=True),
                  FloatMatrixProperty(name="orientationkey", nodes=["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"]),
                  FloatMatrixProperty(name="positionkey", nodes=["dummy", "trimesh", "danglymesh", "skin", "emitter", "light"]),

                  #emitter properties
                  FloatMatrixProperty(name="alphaEndkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="alphaStartkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="alphakey", nodes=["emitter"]),
                  FloatMatrixProperty(name="birthratekey", nodes=["emitter"]),
                  FloatMatrixProperty(name="colorEndkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="colorStartkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="colorkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="fpskey", nodes=["emitter"]),
                  FloatMatrixProperty(name="frameEndkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="frameStartkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="lifeExpkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="masskey", nodes=["emitter"]),

                  FloatMatrixProperty(name="radiuskey", nodes=["emitter"]),
                  FloatMatrixProperty(name="randvelkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="sizeEndkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="sizeStartkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="spreadkey", nodes=["emitter"]),
                  FloatMatrixProperty(name="velocitykey", nodes=["emitter"]),
                  FloatMatrixProperty(name="xsizekey", nodes=["emitter"]),
                  FloatMatrixProperty(name="ysizekey", nodes=["emitter"]),
                  ]
