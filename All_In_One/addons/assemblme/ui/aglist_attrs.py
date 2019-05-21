# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *
props = bpy.props

# Addon imports
from ..functions import *
from .aglist_utils import *

# Create custom property group
class ASSEMBLME_UL_animated_collections(bpy.types.PropertyGroup):
    name = StringProperty(update=uniquifyName)
    id = IntProperty()
    idx = IntProperty()

    collection = PointerProperty(
        type=bpy.types.Collection if b280() else bpy.types.Group,
        name="Object Collection" if b280() else "Object Group",
        description="Group of objects to animate",
        update=collectionUpdate)

    firstFrame = IntProperty(
        name="Start",
        description="First frame of the (dis)assembly animation",
        min=0, max=500000,
        default=1)
    buildSpeed = FloatProperty(
        name="Step",
        description="Number of frames to skip forward between each object selection",
        unit="TIME",
        min=1, max=1000,
        precision=0,
        default=1)
    velocity = FloatProperty(
        name="Velocity",
        description="Speed of individual object layers (2^(10 - Velocity) = object animation duration in frames)",
        unit="VELOCITY",
        min=0.001, max=100,
        precision=1,
        step=1,
        default=6)
    objectVelocity = FloatProperty(default=-1)

    layerHeight = FloatProperty(
        name="Layer Height",
        description="Height of the bounding box that selects objects for each layer in animation",
        unit="LENGTH",
        subtype="DISTANCE",
        min=0.0001, max=1000,
        precision=4,
        default=.1)

    pathObject = StringProperty(
        name="Path",
        description="Path object for animated objects to follow",
        default="")

    xLocOffset = FloatProperty(
        name="X",
        description="Move objects by this x value",
        unit="LENGTH",
        precision=0,
        default=0)
    yLocOffset = FloatProperty(
        name="Y",
        description="Move objects by this y value",
        unit="LENGTH",
        precision=0,
        default=0)
    zLocOffset = FloatProperty(
        name="Z",
        description="Move objects by this z value",
        unit="LENGTH",
        precision=0,
        default=10)
    locationRandom = FloatProperty(
        name="Randomize",
        description="Randomize object location offset",
        min=0, max=10000,
        precision=1,
        default=0)

    xRotOffset = FloatProperty(
        name="X",
        description="Rotate objects by this x value (local space only)",
        unit="ROTATION",
        subtype="ANGLE",
        min=-10000, max=10000,
        precision=1, step=20,
        default=0)
    yRotOffset = FloatProperty(
        name="Y",
        description="Rotate objects by this y value (local space only)",
        unit="ROTATION",
        subtype="ANGLE",
        min=-10000, max=10000,
        precision=1, step=20,
        default=0)
    zRotOffset = FloatProperty(
        name="Z",
        description="Rotate objects by this z value (local space only)",
        unit="ROTATION",
        subtype="ANGLE",
        min=-10000, max=10000,
        precision=1, step=20,
        default=0)
    rotationRandom = FloatProperty(
        name="Randomize",
        description="Randomize object rotation offset",
        min=0, max=10000,
        precision=1,
        default=0)

    interpolationModes = [("CONSTANT", "Constant", "Set interpolation mode for each object in assembly animation: Constant", "IPO_CONSTANT", 1),
                                ("LINEAR", "Linear", "Set interpolation mode for each object in assembly animation: Linear", "IPO_LINEAR", 2),
                                ("BEZIER", "Bezier", "Set interpolation mode for each object in assembly animation: Bezier", "IPO_BEZIER", 3),
                                ("SINE", "Sinusoidal", "Set interpolation mode for each object in assembly animation: Sinusoidal", "IPO_SINE", 4),
                                ("QUAD", "Quadratic", "Set interpolation mode for each object in assembly animation: Quadratic", "IPO_QUAD", 5),
                                ("CUBIC", "Cubic", "Set interpolation mode for each object in assembly animation: Cubic", "IPO_CUBIC", 6),
                                ("QUART", "Quartic", "Set interpolation mode for each object in assembly animation: Quartic", "IPO_QUART", 7),
                                ("QUINT", "Quintic", "Set interpolation mode for each object in assembly animation: Quintic", "IPO_QUINT", 8),
                                ("EXPO", "Exponential", "Set interpolation mode for each object in assembly animation: Exponential", "IPO_EXPO", 9),
                                ("CIRC", "Circular", "Set interpolation mode for each object in assembly animation: Circular", "IPO_CIRC", 10),
                                ("BACK", "Back", "Set interpolation mode for each object in assembly animation: Back", "IPO_BACK", 11),
                                ("BOUNCE", "Bounce", "Set interpolation mode for each object in assembly animation: Bounce", "IPO_BOUNCE", 12),
                                ("ELASTIC", "Elastic", "Set interpolation mode for each object in assembly animation: Elastic", "IPO_ELASTIC", 13)]


    locInterpolationMode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolationModes,
        default="LINEAR")

    rotInterpolationMode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolationModes,
        default="LINEAR")

    xOrient = FloatProperty(
        name="X",
        description="Orientation of the bounding box that selects objects for each layer in animation",
        unit="ROTATION",
        subtype="ANGLE",
        min=-1.570796, max=1.570796,
        precision=1, step=20,
        default=0)
    yOrient = FloatProperty(
        name="Y",
        description="Orientation of the bounding box that selects objects for each layer in animation",
        unit="ROTATION",
        subtype="ANGLE",
        min=-1.570796, max=1.570796,
        # min=-0.785398, max=0.785398,
        precision=1, step=10,
        default=0)
    orientRandom = FloatProperty(
        name="Random",
        description="Randomize orientation of the bounding box that selects objects for each frame",
        min=0, max=100,
        precision=1,
        default=0)

    buildType = EnumProperty(
        name="Build Type",
        description="Choose whether to assemble or disassemble the objects",
        items=[("ASSEMBLE", "Assemble", "Assemble the objects to current location"),
               ("DISASSEMBLE", "Disassemble", "Disassemble objects from current location"),
               # the following is for backwards compatibility with old assemblme presets
               ("Assemble", "", ""),
               ("Disassemble", "", "")],
        update=handleOutdatedPreset,
        default="ASSEMBLE")
    invertBuild = BoolProperty(
        name="Assemble from other direction",
        description="Invert the animation so that the objects start (dis)assembling from the other side",
        default=False)

    useGlobal = BoolProperty(
        name="Use Global Orientation",
        description="Use global object orientation for creating animation (local orientation if disabled)",
        default=False)
    meshOnly = BoolProperty(
        name="Mesh Objects Only",
        description="Non-mesh objects will be excluded from the animation",
        update=setMeshesOnly,
        default=True)
    skipEmptySelections = BoolProperty(
        name="Skip Empty Selections",
        description="Skip frames where nothing is selected if checked (Recommended)",
        default=True)

    animated = BoolProperty(default=False)
    animBoundsStart = IntProperty(default=-1)
    animBoundsEnd = IntProperty(default=-1)
    time_created = FloatProperty(default=float('inf'))

    ## DO THESE BELONG HERE??? ##
    frameWithOrigLoc = IntProperty(
        default=-1)
    animLength = IntProperty(
        default=0)
    lastLayerVelocity = IntProperty(
        default=-1)
    visualizerAnimated = BoolProperty(
        default=False)
    visualizerActive = BoolProperty(
        default=False)

    lastActiveObjectName = StringProperty(default="")
    activeUserIndex = IntProperty(default=0)
    version = StringProperty(default="1.1.6")
