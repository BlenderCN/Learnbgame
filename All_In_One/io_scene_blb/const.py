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
"""
Various constants used in multiple modules.

@author: Demian Wright
"""

from decimal import Decimal
from enum import Enum, IntEnum
from math import pi

# The BLB file extension.
BLB_EXT = ".blb"

# The log file extension.
LOG_EXT = ".log"

# One log indent level.
LOG_INDENT = "  "

# Generic.
X = 0
Y = 1
Z = 2

# Humans have wibbly-wobbly hands.
HUMAN_BRICK_GRID_ERROR = Decimal("0.1")

# The defined height of a Blockland plate at 100% scale.
DEFAULT_PLATE_HEIGHT = Decimal("0.4")

# Blockland does not accept bricks that are wide/deeper than 64 bricks or taller than 256 plates.
MAX_BRICK_HORIZONTAL_PLATES = 64
MAX_BRICK_VERTICAL_PLATES = 256
# Blockland supports up to 10 collision cuboids per BLB.
MAX_BRICK_COLLISION_CUBOIDS = 10


class BLBQuadSection(IntEnum):
    """The quad sections in the correct order for writing to a BLB file. Indexed from 0 to 6."""
    TOP = 0
    BOTTOM = 1
    NORTH = 2
    EAST = 3
    SOUTH = 4
    WEST = 5
    OMNI = 6


class BrickTexture(Enum):
    """Valid brick texture names in alphabetical order."""
    BOTTOMEDGE = 0
    BOTTOMLOOP = 1
    PRINT = 2
    RAMP = 3
    SIDE = 4
    TOP = 5

    def __str__(self):
        """Returns the name of the enum value in uppercase characters."""
        return self.name

    @classmethod
    def as_list(cls):
        """Returns the names of the members of this enum as a list of uppercase strings."""
        return [member.name for member in BrickTexture]


# BLB file strings.
BLB_BRICK_TYPE_SPECIAL = "SPECIAL"
BLB_SECTION_SEPARATOR = "---------------- {} QUADS ----------------"
BLB_HEADER_COVERAGE = "COVERAGE:"
BLB_PREFIX_TEXTURE = "TEX:"
BLB_HEADER_POSITION = "POSITION:"
BLB_HEADER_UV = "UV COORDS:"
BLB_HEADER_COLORS = "COLORS:"
BLB_HEADER_NORMALS = "NORMALS:"

# The default coverage value = no coverage. (Number of plates that need to cover a brick side to hide it.)
# The maximum area a brick's side can cover is 64 * 256 = 16384 plates.
DEFAULT_COVERAGE = 99999

# Brick grid symbols.
GRID_INSIDE = "x"  # Disallow building inside brick.
GRID_OUTSIDE = "-"  # Allow building in empty space.
GRID_UP = "u"  # Allow placing bricks above this plate.
GRID_DOWN = "d"  # Allow placing bricks below this plate.
GRID_BOTH = "b"  # Allow placing bricks above and below this plate.

# Blender has 20 layers.
BLENDER_MAX_LAYER_IDX = 19

# Maximum number of decimal places to write to file.
MAX_FP_DECIMALS_TO_WRITE = 16

# The width and height of the default brick textures in pixels.
BRICK_TEXTURE_RESOLUTION = 512

# The UV coordinates are a single point in the middle of the image = no uv coordinates.
# The middle of the image is used instead of (0,0) due to the way Blockland brick textures are designed.
DEFAULT_UV_COORDINATES = ((0.5, 0.5),) * 4

# Often used Decimal values.
DECIMAL_ONE = Decimal("1.0")
DECIMAL_HALF = Decimal("0.5")

# Useful angles in radians.
RAD_45_DEG = pi * 0.25
RAD_135_DEG = pi - RAD_45_DEG
RAD_225_DEG = pi + RAD_45_DEG
RAD_315_DEG = pi + RAD_135_DEG

TWO_PI = 2.0 * pi


class Axis3D(Enum):
    """An enum with values representing each axis in three-dimensional space, indexed as follows:
           0: POS_X
           1: NEG_X
           2: POS_Y
           3: NEG_Y
           4: POS_Z
           5: NEG_Z
    """
    POS_X = 0
    NEG_X = 1
    POS_Y = 2
    NEG_Y = 3
    POS_Z = 4
    NEG_Z = 5

    def index(self):
        """Determines the index of this three-dimensional axis.

        Returns:
            The index 0, 1, or 2 for the axes X, Y, and Z respectively.
        """
        if self is Axis3D.POS_X or self is Axis3D.NEG_X:
            return X
        elif self is Axis3D.POS_Y or self is Axis3D.NEG_Y:
            return Y
        else:
            return Z

    @classmethod
    def from_property_name(cls, axis_name):
        """Parses the 3D axis from the specified string.

        Args:
            axis_name (string): The name of the axis in the same format as the axis_blb_forward Blender property.

        Returns:
            An Axis3D value corresponding to the specified axis name.
        """
        if axis_name == "POSITIVE_X":
            return Axis3D.POS_X
        elif axis_name == "NEGATIVE_X":
            return Axis3D.NEG_X
        elif axis_name == "POSITIVE_Y":
            return Axis3D.POS_Y
        elif axis_name == "NEGATIVE_Y":
            return Axis3D.NEG_Y
        elif axis_name == "POSITIVE_Z":
            return Axis3D.POS_Z
        else:  # axis_name == "NEGATIVE_Z":
            return Axis3D.NEG_Z

    def is_positive(self):
        """Determines if this three-dimensional axis is positive or negative.

        Returns:
            True if this value represents a positive axis.
        """
        return self is Axis3D.POS_X or self is Axis3D.POS_Y or self is Axis3D.POS_Z


class AxisPlane3D(Enum):
    """An enum with values representing each axis-aligned plane in three-dimensional space, indexed as follows:
           0: XY-plane
           1: XZ-plane
           2: YZ-plane
    """
    XY = 0
    XZ = 1
    YZ = 2
