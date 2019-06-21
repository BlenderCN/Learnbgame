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
A module for processing Blender data into the BLB file format for writing.

@author: Demian Wright
"""
# Set the Decimal number context for operations: 0.5 is rounded up. (Precision can be whatever.)
# NOTE: prec=n limits the number of digits for the whole number.
# E.g. 1234.56 has a precision of 6, not 2.


from collections import OrderedDict, Sequence
from decimal import Context, Decimal, ROUND_HALF_UP, setcontext
from math import atan, ceil, modf, pi, radians, sqrt
import bpy

from mathutils import Euler, Vector
import bmesh
import numpy

from . import common, const, logger
from .const import Axis3D, AxisPlane3D, X, Y, Z


setcontext(Context(rounding=ROUND_HALF_UP))

# Globals.

# Number of decimal places to round floating point numbers to when performing calculations.
# The value was chosen to eliminate most floating points errors but it does
# have the side effect of quantizing the positions of all vertices to
# multiples of the value since everything is rounded using this precision.
__CALCULATION_FP_PRECISION_STR = None

# ==============
# Math Functions
# ==============


def __is_even(value):
    """Checks if the specified value is even.

    Args:
        value (number): A numerical value to check.

    Returns:
        True if the specified value is exactly divisible by 2.
    """
    return value % 2 == 0


def __is_sequence(seq, allow_string=False):
    # String check is XNOR.
    is_str = isinstance(seq, str)
    return (isinstance(seq, Sequence) and ((allow_string and is_str) or (not allow_string and not is_str))) or isinstance(seq, Vector)


def __to_decimal(val, quantize=None):
    """Creates a Decimal number of the specified value and rounds it to the closest specified quantize value.
    The number of decimal digits in the quantize value will determine the number of decimal digits in the returned value
    This is a recursive function.

    Args:
        val (sequence or Number): A Number or a sequence of numerical values to create Decimals out of.
                                  Sequence may contain other sequences.
        quantize (string or Decimal): The optional value to round the specified numbers to.
                                      The value may be given as a string or a Decimal number.
                                      If no value is specified, the floating point precision user has specified in export properties will be used.

    Returns:
        A Decimal representation of the specified number or all the numbers in the specified sequence(s) as the closest multiple of the quantize value, with half rounded up.
    """
    def make_decimal(value, quantize=None):
        """Creates a Decimal number of the specified value and rounds it to the closest specified quantize value.
        The number of decimal digits in the quantize value will determine the number of decimal digits in the returned value.

        Args:
            value (number): A numerical value to create a Decimal out of.
            quantize (string or Decimal): The optional value to round the specified number to.
                                          The value may be given as a string or a Decimal number.
                                          If no value is specified, the user-specified floating point precision will be used.

        Returns:
            A Decimal representation of the specified value as the closest multiple of the quantize value, with half rounded up.
        """
        if quantize is None:
            quantize = __CALCULATION_FP_PRECISION_STR

        # Make a Decimal out of the quantize value if it already isn't.
        if isinstance(quantize, str):
            quantize = Decimal(quantize)
        elif isinstance(quantize, Decimal):
            pass
        else:
            # EXCEPTION
            raise ValueError("__to_decimal(value) quantize must be a string or a Decimal, was '{}'.".format(type(quantize)))

        # Calculate the fraction that will be used to do the rounding to an arbitrary number.
        fraction = const.DECIMAL_ONE / quantize

        # If the value is not a Decimal, convert the value to string and create a Decimal out of the formatted string.
        # Using strings is the only way to create Decimals accurately from numbers as the Decimal representation of
        # the input will be identical to that of the string.
        # I.e. I'm pushing the issue of accurate floating point representation to whatever is the default formatting.
        if not isinstance(value, Decimal):
            value = Decimal("{}".format(value))

        # Multiply the Decimal value with the Decimal fraction.
        # Round to the nearest integer with quantize.
        # Divide with the Decimal fraction.
        # Quantize the result to get the correct number of decimal digits.
        # Result: value is rounded to the nearest value of quantize (half rounded up)
        return ((value * fraction).quantize(const.DECIMAL_ONE) / fraction).quantize(quantize)

    result = []

    if quantize is None:
        quantize = __CALCULATION_FP_PRECISION_STR

    if __is_sequence(val):
        for value in val:
            result.append(__to_decimal(value, quantize))
    else:
        # ROUND & CAST
        return make_decimal(val, quantize)

    return result


def __force_to_ints(values):
    """Casts all values in the specified sequence to ints.

    Args:
        values (sequence of numbers): A sequence of numerical values to be casted to ints.

    Returns:
        A list of the sequence values casted to integers.
    """
    return [int(val) for val in values]


def __are_ints(values):
    """Checks if all values in the specified sequence are ints.

    Args:
        values (sequence of numbers): A sequence of numerical values.

    Returns:
        True if all values in the specified sequence are numerically equal to their integer counterparts.
    """
    for value in values:
        if value != int(value):
            return False

    return True


def __like_int(value):
    """Checks if the specified string is like a pure integer.
    Handles negative integers.

    Args:
        value (string): A string representing a number.

    Returns:
        True if the specified string is like an integer and has no fractional part.
    """
    return value.isdigit() or (value.startswith("-") and value[1:].isdigit())


def __get_world_min(obj):
    """Gets the world space coordinates of the vertex in the specified object that is the closest to the world origin.

    Args:
        obj (Blender object): A Blender mesh.

    Returns:
        A new Vector of the minimum world space coordinates of the specified object.
    """
    # This function deals with Vectors instead of Decimals because it works with Blender object data, which uses Vectors.
    vec_min = Vector((float("+inf"), float("+inf"), float("+inf")))

    for vert in obj.data.vertices:
        # Local coordinates to world space.
        coord = obj.matrix_world * vert.co

        for i in range(3):
            vec_min[i] = min(vec_min[i], coord[i])

    return vec_min


def __get_world_min_max(obj, min_coords=None, max_coords=None):
    """Checks if the specified Blender object's vertices' world space coordinates are smaller or greater than the coordinates stored in their respective minimum and maximum vectors.

    Args:
        obj (Blender object): The Blender object whose vertex coordinates to check against the current minimum and maximum coordinates.
        min_coords (Vector): The Vector of smallest XYZ world space coordinates to compare against. (Optional)
        max_coords (Vector): The Vector of largest XYZ world space coordinates to compare against. (Optional)

    Returns:
        The smallest and largest world coordinates from the specified vectors or object's vertex coordinates.
    """
    # I have no idea why but if I create the vectors as default values for the
    # arguments, the min/max coord vectors from the last time this function
    # was called are somehow carried over. I tried creating a new instance
    # with the vector values but that didn't work either so it isn't an issue
    # with object references.
    if min_coords is None:
        min_coords = Vector((float("+inf"), float("+inf"), float("+inf")))
    if max_coords is None:
        max_coords = Vector((float("-inf"), float("-inf"), float("-inf")))

    for vert in obj.data.vertices:
        coordinates = obj.matrix_world * vert.co

        for i in range(3):
            min_coords[i] = min(min_coords[i], coordinates[i])
            max_coords[i] = max(max_coords[i], coordinates[i])

    return min_coords, max_coords


def __get_vert_world_coord(obj, mesh, vert_idx):
    """Calculates the world coordinates for the vertex at the specified index in the specified mesh's polygon loop.

    Args:
        obj (Blender object): The Blender object that is the parent of the mesh.
        mesh (Blender mesh): The Blender mesh where the vertex is stored.
        vert_idx (int): The index of the vertex in the specified mesh's polygon loop.

    Returns:
        A Vector of the world coordinates of the vertex.
    """
    # Get the vertex index in the loop.
    # Get the vertex coordinates in object space.
    # Convert object space to world space.
    return obj.matrix_world * mesh.vertices[mesh.loops[vert_idx].vertex_index].co


def __loop_index_to_normal_vector(obj, mesh, index):
    """Calculates the normalized vertex normal vector for the vertex at the specified index in the specified Blender object.

    Args:
        obj (Blender object): The Blender object that is the parent of the mesh.
        mesh (Blender mesh): The Blender mesh where the vertex is stored.
        index (int): The index of the loop in the specified objects's loop data sequence.

    Returns:
        A normalized normal vector of the specified vertex.
    """
    return (obj.matrix_world.to_3x3() * mesh.vertices[mesh.loops[index].vertex_index].normal).normalized()


def __normalize_vector(obj, normal):
    """ Gets rid of the object's rotation from the specified normal and calculates the normalized vector for it.

    Args:
        obj (Blender object): The Blender object the normal is in.
        normal (Vector): A normal vector to be normalized.

    Returns:
        A normalized normal vector.
    """
    # Multiplying the normals with the world matrix gets rid of the OBJECT's rotation from the MESH NORMALS.
    return (obj.matrix_world.to_3x3() * normal).normalized()


def __all_within_bounds(local_coordinates, bounding_dimensions):
    """Checks if all the values in the specified local coordinates are within the specified bounding box dimensions.
    Assumes that both sequences have the same number of elements.

    Args:
        local_coordinates (sequence of numbers): A sequence of local space coordinates.
        bounding_dimensions (sequence of numbers): A sequence of dimensions of a bounding box centered at the origin.

    Returns:
        True if all values are within the bounding dimensions.
    """
    # Divide all dimension values by 2.
    halved_dimensions = [value * const.DECIMAL_HALF for value in bounding_dimensions]

    # Check if any values in the given local_coordinates are beyond the given bounding_dimensions.
    # bounding_dimensions / 2 = max value
    # -bounding_dimensions / 2 = min value

    for index, value in enumerate(local_coordinates):
        if value > halved_dimensions[index]:
            return False

    for index, value in enumerate(local_coordinates):
        if value < -(halved_dimensions[index]):
            return False

    return True


def __calculate_center(object_minimum_coordinates, object_dimensions):
    """Calculates the coordinates of the center of a 3D object.

    Args:
        object_minimum_coordinates (sequence of numbers): A sequence of minimum XYZ coordinates of the object.
                                                          This function is only useful is these are world space coordinates.
                                                          If local space coordinates are given, (0, 0, 0) will always be returned as the center regardless of the specified dimensions.
        object_dimensions (sequence of numbers): The dimensions of the object.

    Returns:
        A tuple of Decimal type XYZ coordinates.
    """
    return (object_minimum_coordinates[X] + (object_dimensions[X] * const.DECIMAL_HALF),
            object_minimum_coordinates[Y] + (object_dimensions[Y] * const.DECIMAL_HALF),
            object_minimum_coordinates[Z] + (object_dimensions[Z] * const.DECIMAL_HALF))


def __world_to_local(coordinates, new_origin):
    """Translates the specified coordinates to be relative to the specified new origin coordinates.
    Commonly used to translate coordinates from world space (centered on (0, 0, 0)) to local space (arbitrary center).
    Performs rounding with __to_decimal().

    Args:
        coordinates (sequence of numbers): The sequence of XYZ coordinates to be translated.
        new_origin (sequence of numbers): The new origin point as a sequence of XYZ coordinates in the same space as the specified coordinates.

    Returns:
        A list of Decimal type coordinates relative to the specified new origin coordinates.
    """
    # Make the coordinates Decimals if all of them are not.
    if not all(isinstance(coord, Decimal) for coord in coordinates):
        # ROUND & CAST
        coordinates = __to_decimal(coordinates)

    # Make the new origin Decimals if all of them are not.
    if not all(isinstance(coord, Decimal) for coord in new_origin):
        # ROUND & CAST
        new_origin = __to_decimal(new_origin)

    return [old_coord - new_origin[index] for index, old_coord in enumerate(coordinates)]


def __mirror(xyz, forward_axis):
    """Mirrors the given XYZ sequence according to the specified forward axis.

    Args:
        xyz (sequence): A sequence of elements to be mirrored.
        forward_axis (Axis3D): A value of the Axis3D enum. The axis that will point forwards in-game.

    Returns:
        A new list of XYZ values.
    """
    mirrored = xyz

    if forward_axis is Axis3D.POS_X or forward_axis is Axis3D.NEG_X:
        mirrored[Y] = -mirrored[Y]
    else:
        mirrored[X] = -mirrored[X]

    return mirrored


def __multiply_sequence(multiplier, sequence):
    """Multiplies every value in the specified sequence with a number.

    Args:
        multiplier (numerical value): A number to multiply with.
        sequence (sequence of numerical values): The sequence to whose elements to multiply.

    Returns:
        A new sequence with the values of the specified sequence multiplied with the specified multiplier.
    """
    return [multiplier * value for value in sequence]


def __sequence_product(sequence):
    """Multiplies all values in the specified sequence together.

    Args:
        sequence (sequence of numerical values): The sequence to get the product of.

    Returns:
        The product of the sequence.
    """
    product = 1

    for value in sequence:
        product *= value

    return product


def __has_volume(min_coords, max_coords):
    """Checks if a n-dimensional object has volume in n-dimensional space.

    Args:
        min_coords (sequence of numbers): The minimum coordinates of an object.
        max_coords (sequence of numbers): The maximum coordinates of an object.

    Returns:
        True if an object with the specified coordinates has volume, False otherwise.
    """
    for index, value in enumerate(max_coords):
        if (value - min_coords[index]) == 0:
            return False

    return True


def __count_occurrences(value, sequence, not_equal=False):
    """Counts the number of occurrences of the specified value in the sequence.

    Args:
        value (value): Value to count the occurrences of.
        sequence (sequence): Sequence to iterate over.
        not_equal (boolean): Count the number of times the value does not appear in the sequence instead. (Default: False)

    Return:
        The number of times the value did/did not appear in the sequence.
    """
    if not_equal:
        return len([val for val in sequence if val != value])
    else:
        return len([val for val in sequence if val == value])

# =================================
# Blender Data Processing Functions
# =================================


class BrickBounds(object):
    """A class for storing the Blender data of brick bounds.

    Stores the following data:
        - Blender object name,
        - object dimensions,
        - object center world coordinates,
        - minimum vertex world coordinates,
        - maximum vertex world coordinates,
        - dimensions of the axis-aligned bounding box of visual meshes,
        - and world center coordinates of the axis-aligned bounding box of visual meshes.
    """

    def __init__(self):
        # The name of the Blender object.
        self.object_name = None

        # The dimensions are stored separately even though it is trivial to calculate them from the coordinates because they are used often.
        self.dimensions = []

        # The object center coordinates are stored separately for convenience.
        self.world_center = []

        self.world_coords_min = []
        self.world_coords_max = []

        # TODO: Consider moving to another object?
        # The axis-aligned bounding box of visual meshes of this brick.
        self.aabb_dimensions = None
        self.aabb_world_center = None

    def __repr__(self):
        return "<BrickBounds object_name:{} dimensions:{} world_center:{} world_coords_min:{} world_coords_max:{} aabb_dimensions:{} aabb_world_center:{}>".format(
            self.object_name, self.dimensions, self.world_center, self.world_coords_min, self.world_coords_max, self.aabb_dimensions, self.aabb_world_center)


class BLBData(object):
    """A class for storing the brick data to be written to a BLB file.

    Stores the following data:
        - BLB file name without extension
        - size (dimensions) in plates,
        - brick grid data,
        - collision cuboids,
        - coverage data,
        - and sorted quad data.
    """

    def __init__(self):
        # Brick BLB file name.
        self.brick_name = None

        # Brick XYZ integer size in plates.
        self.brick_size = []

        # Brick grid data sequences.
        self.brick_grid = []

        # Brick collision box coordinates.
        self.collision = []

        # Brick coverage data sequences.
        self.coverage = []

        # Sorted quad data sequences.
        self.quads = []


class OutOfBoundsException(Exception):
    """An exception thrown when a vertex position is outside of brick bounds."""
    pass


class ZeroSizeException(Exception):
    """An exception thrown when a definition object has zero brick size on at least one axis."""
    pass

# ================
# Helper Functions
# ================


def __round_to_plate_coordinates(local_coordinates, brick_dimensions, plate_height):
    """Rounds the specified sequence of local space XYZ coordinates to the nearest valid plate coordinates in a brick with the specified dimensions.

    Args:
        local_coordinates (sequence of numbers): A sequence of local space coordinates.
        brick_dimensions (sequence of numbers): A sequence of dimensions of the brick.
        plate_height (Decimal): The height of a Blockland plate in Blender units.

    Returns:
        A list of rounded local space coordinates as Decimal values.
    """
    result = []

    # 1 plate is 1.0 Blender units wide and deep.
    # Plates can only be 1.0 units long on the X and Y axes.
    # Valid plate positions exist every 0.5 units on odd sized bricks and every 1.0 units on even sized bricks.
    if __is_even(brick_dimensions[X]):
        # ROUND & CAST
        result.append(__to_decimal(local_coordinates[X], "1.0"))
    else:
        # ROUND & CAST
        result.append(__to_decimal(local_coordinates[X], "0.5"))

    if __is_even(brick_dimensions[Y]):
        # ROUND & CAST
        result.append(__to_decimal(local_coordinates[Y], "1.0"))
    else:
        # ROUND & CAST
        result.append(__to_decimal(local_coordinates[Y], "0.5"))

    # Round to the nearest full plate height. (Half is rounded up)
    if __is_even(brick_dimensions[Z] / plate_height):
        # ROUND & CAST
        result.append(__to_decimal(local_coordinates[Z], plate_height))
    else:
        # ROUND & CAST
        result.append(__to_decimal(local_coordinates[Z], (plate_height * const.DECIMAL_HALF)))

    return result


def __sequence_z_to_plates(xyz, plate_height):
    """Performs __to_decimal(sequence) on the given sequence and scales the Z component to match Blockland plates.
    If the given sequence does not have exactly three components (assumed format is (X, Y, Z)) the input is returned unchanged.

    Args:
        xyz (sequence of numbers): A sequence of three numerical values.
        plate_height (Decimal): The height of a Blockland plate in Blender units.

    Returns:
        A list of three Decimal type numbers.
    """
    if len(xyz) == 3:
        # ROUND & CAST
        sequence = __to_decimal(xyz)
        sequence[Z] /= plate_height
        return sequence
    else:
        return xyz


def __split_object_string_to_tokens(name, replace_commas=False):
    """Splits a Blender object name into its token parts.
    Correctly takes into account duplicate object names with .### at the end.

    Args:
        name (string): A Blender object name.
        replace_commas (bool): Replace all commas with periods in the object name? (Default: False)

    Returns:
        The name split into a list of uppercase strings at whitespace characters.
    """
    if replace_commas:
        name = name.replace(",", ".")

    # If the object name has "." as the fourth last character, it could mean that Blender has added the index (e.g. ".002") to the end of the object name because an object with the same name already exists.
    # Removing the end of the name fixes an issue where for example two grid definition objects exist with identical names (which is very common) "gridx" and "gridx.001".
    # When the name is split at whitespace, the first object is recognized as a grid definition object and the second is not.
    if len(name) > 4 and name[-4] == ".":
        # Remove the last 4 characters of from the name before splitting at whitespace.
        tokens = name[:-4].upper().split()
    else:
        # Split the object name at whitespace.
        tokens = name.upper().split()

    return tokens


def __get_tokens_from_object_name(name, tokens):
    """Retrieves a set of common tokens from the specified name and sequence of tokens.

    Args:
        name (string or sequence of strings): A raw Blender object name or a sequence of tokens.
        tokens (sequence of strings): A sequence of tokens.

    Returns:
        A set of tokens that exist both in the Blender object name and the specified sequence of tokens, in the order they appeared in the name.
    """
    if isinstance(name, str):
        name_tokens = __split_object_string_to_tokens(name)
    else:
        name_tokens = name

    # In case tokens sequence contains mixed case characters, convert everything to uppercase.
    tokens = [token.upper() for token in tokens]

    # Convert name tokens and wanted tokens into sets.
    # Get their intersection.
    # Sort the set according to the order the elements were in the object tokens.
    # Returned tokens contain all tokens that were in the object tokens AND in the wanted tokens.
    # It contains zero or more tokens.
    return sorted(set(name_tokens) & set(tokens), key=name_tokens.index)


def __modify_brick_grid(brick_grid, volume, symbol):
    """Modifies the specified brick grid by adding the specified symbol to every grid slot specified by the volume.

    Will crash if specified volume extends beyond the 3D space defined by the brick grid.

    Args:
        brick_grid (3D array): A pre-initialized three dimensional array representing every plate of a brick.
        volume (sequence of numerical ranges): A sequence of three (XYZ) sequences representing the dimensions of a 3D volume.
                                               Each element contains a sequence of two numbers representing a range of indices ([min, max[) in the brick grid.
        symbol (string): A valid brick grid symbol to place in the elements specified by the volume.
    """
    # Ranges are exclusive [min, max[ index ranges.
    width_range = volume[X]
    depth_range = volume[Y]
    height_range = volume[Z]

    # Example data for a cuboid brick that is:
    # - 2 plates wide
    # - 3 plates deep
    # - 4 plates tall
    # Ie. a brick of size "3 2 4"
    #
    # uuu
    # xxx
    # xxx
    # ddd
    #
    # uuu
    # xxx
    # xxx
    # ddd

    # For every slice of the width axis.
    for w in range(width_range[0], width_range[1]):
        # For every row from top to bottom.
        for h in range(height_range[0], height_range[1]):
            # For every character the from left to right.
            for d in range(depth_range[0], depth_range[1]):
                # Set the given symbol.
                brick_grid[w][h][d] = symbol


def __calculate_coverage(calculate_side=None, hide_adjacent=None, brick_grid=None, forward_axis=None):
    """Calculates the BLB coverage data for a brick.

    Args:
        calculate_side (sequence of booleans): An optional sequence of boolean values where the values must in the same order as const.QUAD_SECTION_ORDER.
                                               A value of true means that coverage will be calculated for that side of the brick according the specified size of the brick.
                                               A value of false means that the default coverage value will be used for that side.
                                               If not defined, default coverage will be used.
        hide_adjacent (sequence of booleans): An optional sequence of boolean values where the values must in the same order as const.QUAD_SECTION_ORDER.
                                              A value of true means that faces of adjacent bricks covering this side of this brick will be hidden.
                                              A value of false means that adjacent brick faces will not be hidden.
                                              Must be defined if calculate_side is defined.
        brick_grid (sequence of integers): An optional sequence of the sizes of the brick on each of the XYZ axes.
                                           Must be defined if calculate_side is defined.
        forward_axis (Axis): The optional user-defined BLB forward axis.
                             Must be defined if calculate_side is defined.

    Returns:
        A sequence of BLB coverage data.
    """
    coverage = []

    # Does the user want to calculate coverage in the first place?
    if calculate_side is not None:
        # Initially assume that forward axis is +X, data will be swizzled later.
        for index, side in enumerate(calculate_side):
            if side:
                # Bricks are cuboid in shape.
                # The brick sides in the grid are as follows:
                # - Blender top    / grid top   : first row   of every slice.
                # - Blender bottom / grid bottom: last  row   of every slice.
                # - Blender north  / grid east  : last  index of every row.
                # - Blender east   / grid south : last  slice in grid.
                # - Blender south  / grid west  : first index of every row.
                # - Blender west   / grid north : first slice in grid.
                # Coverage only takes into account symbols that are not empty space "-".
                # Calculate the area of the brick grid symbols on each the brick side.
                area = 0

                if index == const.BLBQuadSection.TOP.value:
                    for axis_slice in brick_grid:
                        area += __count_occurrences(const.GRID_OUTSIDE, axis_slice[0], True)

                elif index == const.BLBQuadSection.BOTTOM.value:
                    slice_last_row_idx = len(brick_grid[0]) - 1

                    for axis_slice in brick_grid:
                        area += __count_occurrences(const.GRID_OUTSIDE, axis_slice[slice_last_row_idx], True)

                elif index == const.BLBQuadSection.NORTH.value:
                    row_last_symbol_idx = len(brick_grid[0][0]) - 1
                    for axis_slice in brick_grid:
                        for row in axis_slice:
                            area += 0 if row[row_last_symbol_idx] == const.GRID_OUTSIDE else 1

                elif index == const.BLBQuadSection.EAST.value:
                    for row in brick_grid[len(brick_grid) - 1]:
                        area += __count_occurrences(const.GRID_OUTSIDE, row, True)

                elif index == const.BLBQuadSection.SOUTH.value:
                    for axis_slice in brick_grid:
                        for row in axis_slice:
                            area += 0 if row[0] == const.GRID_OUTSIDE else 1

                elif index == const.BLBQuadSection.WEST.value:
                    for row in brick_grid[0]:
                        area += __count_occurrences(const.GRID_OUTSIDE, row, True)

                else:
                    # EXCEPTION
                    raise RuntimeError("Invalid quad section index '{}'.".format(index))

            else:
                area = const.DEFAULT_COVERAGE

            # Hide adjacent face?
            # Valid values are 1 and 0, Python will write True and False as integers.
            coverage.append((hide_adjacent[index], area))

        # Swizzle the coverage values around according to the defined forward axis.
        # Coverage was calculated with forward axis at +X.

        # ===========================================
        # The order of the values in the coverage is:
        # 0 = a = +Z: Top
        # 1 = b = -Z: Bottom
        # 2 = c = +X: North
        # 3 = d = -Y: East
        # 4 = e = -X: South
        # 5 = f = +Y: West
        # ===========================================

        # Technically this is wrong as the order would be different for -Y
        # forward, but since the bricks must be cuboid in shape, the
        # transformations are symmetrical.
        if forward_axis is Axis3D.POS_Y or forward_axis is Axis3D.NEG_Y:
            # New North will be +Y.
            # Old North (+X) will be the new East
            coverage = common.swizzle(coverage, "abfcde")

        # Else forward_axis is +X or -X: no need to do anything, the calculation was done with +X.

        # No support for Z axis remapping yet.
    else:
        # Use the default coverage.
        # Do not hide adjacent face.
        # Hide this face if it is covered by const.DEFAULT_COVERAGE plates.
        coverage = [(0, const.DEFAULT_COVERAGE)] * 6

    return coverage


def __sort_quad(positions, bounds_dimensions, plate_height):
    """Calculates the section (brick side) for the specified quad within the specified bounds dimensions.

    The section is determined by whether all vertices of the quad are in the same plane as one of the planes (brick sides) defined by the (cuboid) brick bounds.
    The quad's section is needed for brick coverage.

    Args:
        positions (sequence of numbers): A sequence containing the vertex positions of the quad to be sorted.
        bounds_dimensions (sequence of Decimals): The dimensions of the brick bounds.
        plate_height (Decimal): The height of a Blockland plate in Blender units.

    Returns:
        The section of the quad as a value of the BLBQuadSection enum.
    """
    # ROUND & CAST
    # Divide all dimension values by 2 to get the local bounding plane values.
    # The dimensions are in Blender units so Z height needs to be converted to plates.
    local_bounds = __sequence_z_to_plates([value * const.DECIMAL_HALF for value in bounds_dimensions], plate_height)

    # Assume omni direction until otherwise proven.
    direction = const.BLBQuadSection.OMNI

    # Each position list has exactly 3 values.
    # 0 = X
    # 1 = Y
    # 2 = Z
    for axis in range(3):
        # This function only handles quads so there are always exactly 4 position lists. (One for each vertex.)
        # If the vertex coordinate is the same on an axis for all 4 vertices, this face is parallel to the plane perpendicular to that axis.
        if positions[0][axis] == positions[1][axis] == positions[2][axis] == positions[3][axis]:
            # If the common value is equal to one of the bounding values the quad is on the same plane as one of the edges of the brick.
            # Stop searching as soon as the first plane is found because it is impossible for the quad to be on multiple planes at the same time.
            # If the vertex coordinates are equal on more than one axis, it means that the quad is either a line (2 axes) or a point (3 axes).

            # Blockland assumes by default that forward axis is Blender +X. (In terms of the algorithm.)
            # Then in-game the brick north is to the left of the player, which is +Y in Blender.

            # All vertex coordinates are the same on this axis, only the first one needs to be checked.

            # Positive values.
            if positions[0][axis] == local_bounds[axis]:
                # +X = East
                if axis == X:
                    direction = const.BLBQuadSection.EAST
                    break
                # +Y = North
                elif axis == Y:
                    direction = const.BLBQuadSection.NORTH
                    break
                # +Z = Top
                else:
                    direction = const.BLBQuadSection.TOP
                    break

            # Negative values.
            elif positions[0][axis] == -local_bounds[axis]:
                # -X = West
                if axis == X:
                    direction = const.BLBQuadSection.WEST
                    break
                # -Y = South
                elif axis == Y:
                    direction = const.BLBQuadSection.SOUTH
                    break
                # -Z = Bottom
                else:
                    direction = const.BLBQuadSection.BOTTOM
                    break
            # Else the quad is not on the same plane with one of the bounding planes = Omni
        # Else the quad is not planar = Omni

    return direction


def __rotate_section_value(section, forward_axis):
    """
    Args:
        section (BLBQuadSection): A value of the BLBQuadSection enum.
        forward_axis (Axis3D): A value of the Axis3D enum. The axis that will point forwards in-game.

    Returns:
        The input section rotated according to the specified forward_axis as a value in the BLBQuadSection.
    """
    # ==========
    # TOP    = 0
    # BOTTOM = 1
    # NORTH  = 2
    # EAST   = 3
    # SOUTH  = 4
    # WEST   = 5
    # OMNI   = 6
    # ==========

    # Top and bottom always the same and do not need to be rotated because Z axis remapping is not yet supported.
    # Omni is not planar and does not need to be rotated.
    # The initial values are calculated according to +X forward axis.
    if section <= const.BLBQuadSection.BOTTOM or section == const.BLBQuadSection.OMNI or forward_axis is Axis3D.POS_X:
        return section

    # ========================================================================
    # Rotate the section according the defined forward axis.
    # 0. section is in the range [2, 5].
    # 1. Subtract 2 to put section in the range [0, 3]: sec - 2
    # 2. Add the rotation constant:                     sec - 2 + R
    # 3. Use modulo make section wrap around 3 -> 0:    sec - 2 + R % 4
    # 4. Add 2 to get back to the correct range [2, 5]: sec - 2 + R % 4 + 2
    # ========================================================================
    elif forward_axis is Axis3D.POS_Y:
        # 90 degrees clockwise.
        # [2] North -> [3] East:  (2 - 2 + 1) % 4 + 2 = 3
        # [5] West  -> [2] North: (5 - 2 + 1) % 4 + 2 = 2
        return const.BLBQuadSection((section - 1) % 4 + 2)
    elif forward_axis is Axis3D.NEG_X:
        # 180 degrees clockwise.
        # [2] North -> [4] South: (2 - 2 + 2) % 4 + 2 = 4
        # [4] South -> [2] North
        return const.BLBQuadSection(section % 4 + 2)
    elif forward_axis is Axis3D.NEG_Y:
        # 270 degrees clockwise.
        # [2] North -> [5] West:  (2 - 2 + 3) % 4 + 2 = 5
        # [5] West  -> [4] South
        return const.BLBQuadSection((section + 1) % 4 + 2)


def __record_bounds_data(properties, blb_data, bounds_data):
    """Adds the brick bounds data to the specified BLB data object.

    Args:
        properties (Blender properties object): A Blender object containing user preferences.
        blb_data (BLBData): A BLBData object containing all the necessary data for writing a BLB file.
        bounds_data (BrickBounds): A BrickBounds object containing the bounds data.

    Returns:
        The modified blb_data object containing the bounds data.
    """
    # ROUND & CAST
    # Get the dimensions of the Blender object and convert the height to plates.
    bounds_size = __sequence_z_to_plates(bounds_data.dimensions, properties.plate_height)

    # Are the dimensions of the bounds object not integers?
    if not __are_ints(bounds_size):
        if bounds_data.object_name is None:
            logger.warning("IOBLBW000", "Calculated bounds have a non-integer size {} {} {}, rounding up.".format(bounds_size[X],
                                                                                                                  bounds_size[Y],
                                                                                                                  bounds_size[Z]), 1)

            # In case height conversion or rounding introduced floating point errors, round up to be on the safe side.
            for index, value in enumerate(bounds_size):
                bounds_size[index] = ceil(value)
        else:
            logger.warning("IOBLBW001", "Defined bounds have a non-integer size {} {} {}, rounding to a precision of {}.".format(bounds_size[X],
                                                                                                                                 bounds_size[Y],
                                                                                                                                 bounds_size[Z],
                                                                                                                                 properties.human_brick_grid_error), 1)

            for index, value in enumerate(bounds_size):
                # Round to the specified error amount.
                bounds_size[index] = round(properties.human_brick_grid_error * round(value / properties.human_brick_grid_error))

    # The value type must be int because you can't have partial plates. Returns a list.
    blb_data.brick_size = __force_to_ints(bounds_size)

    if properties.blendprop.export_count == "SINGLE" and properties.blendprop.brick_name_source == "BOUNDS":
        if bounds_data.object_name is None:
            logger.warning("IOBLBW002", "Brick name was supposed to be in the bounds definition object but no such object exists, file name used instead.", 1)
        else:
            if len(bounds_data.object_name.split()) == 1:
                logger.warning("IOBLBW003", "Brick name was supposed to be in the bounds definition object but no name (separated with a space) was found after the definition token, file name used instead.",
                               1)
            else:
                # Brick name follows the bounds definition, must be separated by a space.
                # Substring the object name: everything after properties.deftokens.bounds and 1 space character till the end of the name.
                blb_data.brick_name = bounds_data.object_name[
                    bounds_data.object_name.upper().index(properties.deftokens.bounds) + len(properties.deftokens.bounds) + 1:]
                logger.info("Found brick name from bounds definition: {}".format(blb_data.brick_name), 1)
    elif properties.blendprop.export_count == "MULTIPLE" and properties.blendprop.brick_name_source_multi == "BOUNDS":
        if bounds_data.object_name is None:
            if properties.blendprop.brick_definition == "LAYERS":
                # RETURN ON ERROR
                return "IOBLBF000 When exporting multiple bricks in separate layers, a bounds definition object must exist in every layer. It is also used to provide a name for the brick."
            else:
                # TODO: Does this work? Does it actually export multiple bricks or overwrite the first one?
                logger.warning("IOBLBW002", "Brick name was supposed to be in the bounds definition object but no such object exists, file name used instead.", 1)
        else:
            if len(bounds_data.object_name.split()) == 1:
                if properties.blendprop.brick_definition == "LAYERS":
                    # RETURN ON ERROR
                    return "IOBLBF001 When exporting multiple bricks in separate layers, the brick name must be after the bounds definition token (separated with a space) in the bounds definition object name."
                else:
                    logger.warning("IOBLBW003", "Brick name was supposed to be in the bounds definition object but no name (separated with a space) was found after the definition token, file name used instead.",
                                   1)
            else:
                # Brick name follows the bounds definition, must be separated by a space.
                # Substring the object name: everything after properties.deftokens.bounds and 1 space character till the end of the name.
                blb_data.brick_name = bounds_data.object_name[
                    bounds_data.object_name.upper().index(properties.deftokens.bounds) + len(properties.deftokens.bounds) + 1:]
                logger.info("Found brick name from bounds definition: {}".format(blb_data.brick_name), 1)

    return blb_data


def __calculate_bounding_box_size(min_coords, max_coords):
    """Calculates the XYZ dimensions of a cuboid with the specified minimum and maximum coordinates.

    Args:
        min_coords (sequence of numbers): The minimum coordinates as a sequence: [X, Y, Z]
        max_coords (sequence of numbers): The maximum coordinates as a sequence: [X, Y, Z]

    Returns:
        A sequence with the [X, Y, Z] dimensions of a cuboid as Decimal values.
    """
    # Get the dimensions defined by the vectors.
    # ROUND & CAST: calculated bounds object dimensions into Decimals for accuracy.
    return __to_decimal((max_coords[X] - min_coords[X],
                         max_coords[Y] - min_coords[Y],
                         max_coords[Z] - min_coords[Z]))


def __calculate_bounds(export_scale, min_world_coordinates, max_world_coordinates):
    """Calculates the brick bounds data from the recorded minimum and maximum vertex world coordinates.

    Args:
        export_scale (float): A user defined value to scale all values by. Value must be in the range [0.0,1.0].
        min_world_coordinates (sequence of numbers): A sequence containing the minimum world coordinates of the brick to be exported.
        max_world_coordinates (sequence of numbers): A sequence containing the maximum world coordinates of the brick to be exported.

    Returns:
        A BrickBounds object containg the brick bounds data.
    """
    bounds_data = BrickBounds()

    # ROUND & CAST: The minimum and maximum calculated world coordinates.
    # USER SCALE: Multiply by user defined scale.
    min_coords = __to_decimal(__multiply_sequence(export_scale, min_world_coordinates))
    max_coords = __to_decimal(__multiply_sequence(export_scale, max_world_coordinates))

    bounds_data.world_coords_min = min_coords
    bounds_data.world_coords_max = max_coords

    # USER SCALE: Multiply by user defined scale.
    bounds_data.dimensions = __calculate_bounding_box_size(min_coords, max_coords)
    bounds_data.world_center = __calculate_center(min_coords, bounds_data.dimensions)

    bounds_data.aabb_dimensions = bounds_data.dimensions
    bounds_data.aabb_world_center = bounds_data.world_center

    return bounds_data


def __get_color_values(tokens):
    """Parses color values from the specified list of tokens, if they exist.
    Colors can be defined with integers, floats, or both.
    If integers are used, they are converted to floats by dividing with 255.

    Args:
        tokens (sequence of strings): A sequence to get colors values from.

    Returns:
        A list of 4 float representing red, green, blue, and alpha color values or None if all 4 values are not defined.
    """
    floats = []

    for val in tokens:
        if __like_int(val):
            floats.append(int(val) / 255.0)
        else:
            # Value wasn't an integer, try a float.
            fval = common.to_float_or_none(val)

            # If value was a float.
            if fval is not None:
                floats.append(fval)

    return floats


def __grid_object_to_volume(properties, bounds_data, grid_obj):
    """Calculates the brick grid definition index range [min, max[ for each axis from the vertex coordinates of the specified object.
    The indices represent a three dimensional volume in the local space of the bounds object where the origin is in the -X +Y +Z corner.
    Can raise OutOfBoundsException and ZeroSizeException.

    Args:
        properties (Blender properties object): A Blender object containing user preferences.
        bounds_data (BrickBounds): A BrickBounds object containing the bounds data.
        grid_obj (Blender object): A Blender object representing a brick grid definition.

    Returns:
        A tuple in the following format: ( (min_width, max_width), (min_depth, max_depth), (min_height, max_height) )
    """
    halved_dimensions = [value * const.DECIMAL_HALF for value in bounds_data.dimensions]

    # Find the minimum and maximum coordinates for the brick grid object.
    grid_min, grid_max = __get_world_min_max(grid_obj)

    # ROUND & CAST
    # USER SCALE: Multiply by user defined scale.
    grid_min = __multiply_sequence(properties.scale, __to_decimal(grid_min))
    grid_max = __multiply_sequence(properties.scale, __to_decimal(grid_max))

    # Recenter the coordinates to the bounds. (Also rounds the values.)
    grid_min = __world_to_local(grid_min, bounds_data.world_center)
    grid_max = __world_to_local(grid_max, bounds_data.world_center)

    # Round coordinates to the nearest plate.
    grid_min = __round_to_plate_coordinates(grid_min, bounds_data.dimensions, properties.plate_height)
    grid_max = __round_to_plate_coordinates(grid_max, bounds_data.dimensions, properties.plate_height)

    if __all_within_bounds(grid_min, bounds_data.dimensions) and __all_within_bounds(grid_max, bounds_data.dimensions):
        # Convert the coordinates into brick grid sequence indices.

        # Minimum indices.
        if properties.forward_axis is Axis3D.NEG_X or properties.forward_axis is Axis3D.NEG_Y:
            # Translate coordinates to negative X axis.
            # -X: Index 0 = front of the brick.
            # -Y: Index 0 = left of the brick.
            grid_min[X] = grid_min[X] - halved_dimensions[X]
        else:
            # Translate coordinates to positive X axis.
            # +X: Index 0 = front of the brick.
            # +Y: Index 0 = left of the brick.
            grid_min[X] = grid_min[X] + halved_dimensions[X]

        if properties.forward_axis is Axis3D.POS_X or properties.forward_axis is Axis3D.NEG_Y:
            # Translate coordinates to negative Y axis.
            # +X: Index 0 = left of the brick.
            # -Y: Index 0 = front of the brick.
            grid_min[Y] = grid_min[Y] - halved_dimensions[Y]
        else:
            # Translate coordinates to positive Y axis.
            # +Y: Index 0 = front of the brick.
            # -X: Index 0 = left of the brick.
            grid_min[Y] = grid_min[Y] + halved_dimensions[Y]

        # Translate coordinates to negative Z axis, height to plates.
        grid_min[Z] = (grid_min[Z] - halved_dimensions[Z]) / properties.plate_height

        # Maximum indices.
        if properties.forward_axis is Axis3D.NEG_X or properties.forward_axis is Axis3D.NEG_Y:
            grid_max[X] = grid_max[X] - halved_dimensions[X]
        else:
            grid_max[X] = grid_max[X] + halved_dimensions[X]

        if properties.forward_axis is Axis3D.POS_X or properties.forward_axis is Axis3D.NEG_Y:
            grid_max[Y] = grid_max[Y] - halved_dimensions[Y]
        else:
            grid_max[Y] = grid_max[Y] + halved_dimensions[Y]

        grid_max[Z] = (grid_max[Z] - halved_dimensions[Z]) / properties.plate_height

        # Swap min/max Z index and make it positive. Index 0 = top of the brick.
        temp = grid_min[Z]
        grid_min[Z] = abs(grid_max[Z])
        grid_max[Z] = abs(temp)

        if properties.forward_axis is Axis3D.POS_X:
            # Swap min/max depth and make it positive.
            temp = grid_min[Y]
            grid_min[Y] = abs(grid_max[Y])
            grid_max[Y] = abs(temp)

            grid_min = common.swizzle(grid_min, "bac")
            grid_max = common.swizzle(grid_max, "bac")
        elif properties.forward_axis is Axis3D.NEG_X:
            # Swap min/max width and make it positive.
            temp = grid_min[X]
            grid_min[X] = abs(grid_max[X])
            grid_max[X] = abs(temp)

            grid_min = common.swizzle(grid_min, "bac")
            grid_max = common.swizzle(grid_max, "bac")
        elif properties.forward_axis is Axis3D.NEG_Y:
            # Swap min/max depth and make it positive.
            temp = grid_min[Y]
            grid_min[Y] = abs(grid_max[Y])
            grid_max[Y] = abs(temp)

            # Swap min/max width and make it positive.
            temp = grid_min[X]
            grid_min[X] = abs(grid_max[X])
            grid_max[X] = abs(temp)
        # Else properties.forward_axis is Axis3D.POS_Y: do nothing

        grid_min = __force_to_ints(grid_min)
        grid_max = __force_to_ints(grid_max)

        if not __has_volume(grid_min, grid_max):
            raise ZeroSizeException()
        else:
            # Return the index ranges as a tuple: ( (min_width, max_width), (min_depth, max_depth), (min_height, max_height) )
            return ((grid_min[X], grid_max[X]),
                    (grid_min[Y], grid_max[Y]),
                    (grid_min[Z], grid_max[Z]))
    else:
        raise OutOfBoundsException()

# =========================
# Main Processing Functions
# =========================


def __process_bounds_object(export_scale, obj):
    """Processes a manually defined bounds Blender object.

    Args:
        export_scale (float): A user defined percentage value to scale all values by.
        obj (Blender object): The Blender object defining the bounds of the brick that the user created.

    Returns:
        A BrickBounds object.
    """
    # Find the minimum and maximum world coordinates for the bounds object.
    bounds_min, bounds_max = __get_world_min_max(obj)

    # ROUND & CAST
    bounds_data = __calculate_bounds(export_scale, __to_decimal(bounds_min), __to_decimal(bounds_max))

    # Store the name for logging and determining whether the bounds were defined or automatically calculated.
    bounds_data.object_name = obj.name

    return bounds_data


def __process_coverage(properties, blb_data):
    """Calculates the coverage data if the user has defined so in the properties.
    If user does not want coverage, default coverage data will be used.

    Args:
        properties (Blender properties object): A Blender object containing user preferences.
        blb_data (BLBData): A BLBData object containing all the necessary data for writing a BLB file.

    Returns:
        A sequence of BLB coverage data.
    """
    if properties.blendprop.calculate_coverage:
        calculate_side = ((properties.blendprop.coverage_top_calculate,
                           properties.blendprop.coverage_bottom_calculate,
                           properties.blendprop.coverage_north_calculate,
                           properties.blendprop.coverage_east_calculate,
                           properties.blendprop.coverage_south_calculate,
                           properties.blendprop.coverage_west_calculate))

        hide_adjacent = ((properties.blendprop.coverage_top_hide,
                          properties.blendprop.coverage_bottom_hide,
                          properties.blendprop.coverage_north_hide,
                          properties.blendprop.coverage_east_hide,
                          properties.blendprop.coverage_south_hide,
                          properties.blendprop.coverage_west_hide))

        return __calculate_coverage(calculate_side,
                                    hide_adjacent,
                                    blb_data.brick_grid,
                                    properties.forward_axis)
    else:
        return __calculate_coverage()


def __vector_length(va, vb):
    """Calculates the length of the vector starting at va and ending at vb.

    Args:
        va (Vector): Vector A.
        vb (Vector): Vector B.

    Returns:
        The length of the vector AB.
    """
    return (vb - va).length


def __distance(a, b):
    """Calculates the Euclidean distance between the specified coordinates A and B in three-dimensional space.

    Args:
        a (sequence of numbers): Coordinates of point A.
        b (sequence of numbers): Coordinates of point B.

    Returns:
        The distance between points A and B.
    """
    return sqrt((b[X] - a[X]) ** 2 +
                (b[Y] - a[Y]) ** 2 +
                (b[Z] - a[Z]) ** 2)


def __calculate_quad_width_height(len_top, len_right, len_bottom, len_left):
    """Calculates the best width and height of a quad with the specified coordinates.
    If one quad side has zero length, in other words the quad has degenerated into a triangle, the length of the opposing side is used instead.
    If neither side has zero length, the average of the two is returned.

    Args:
        len_top (Decimal): The length of the top edge of the quad.
        len_right (Decimal): The length of the right edge of the quad.
        len_bottom (Decimal): The length of the bottom edge of the quad.
        len_left (Decimal): The length of the left edge of the quad.

    Returns:
        A tuple (width, height) containing the width and height of the quad as Decimals.
    """
    # If zero, return the other length.
    if Decimal.is_zero(len_top):
        # If len_bottom is zero, quad width is zero as both sides are points.
        width = len_bottom
    elif Decimal.is_zero(len_bottom):
        width = len_top
    else:
        width = (len_top + len_bottom) * const.DECIMAL_HALF

    if Decimal.is_zero(len_left):
        # If len_bottom is zero, quad width is zero as both sides are points.
        height = len_right
    elif Decimal.is_zero(len_right):
        height = len_left
    else:
        height = (len_left + len_right) * const.DECIMAL_HALF

    return (width, height)


def __get_longest_vector_length(points):
    """Gets the length of the longest vector in the specified sequence of points.

    Args:
        points (sequence of Vectors): A sequence of points in n-dimensional space where two successive points make a vector.
                                      Must have an even number of elements.

    Returns:
        The length of the longest vector or None if a sequence with an odd number of elements was provided.
    """
    count = len(points)
    longest = 0

    if __is_even(count):
        for idx in range(0, count, 2):
            length = __vector_length(points[idx], points[idx + 1])

            if length > longest:
                longest = length

        # ROUND & CAST
        return __to_decimal(longest)
    else:
        return None


def __get_quad_dir_idx_top_tex(coords):
    """Gets an index representing the direction the top edge of the quad is pointing for UV mapping the TOP brick texture.

    Args:
        coords (sequence of Vectors): A sequence of 4 vectors representing the 3D positions of the vertices of a quad.

    Returns:
        An integer representing a 90 degree sector where sector index:
        0 is from ]315, 45] degrees
        1 is from ]45, 135] degrees
        2 is from ]135, 225] degrees
        3 is from ]225, 315] degrees
    """
    # TODO: Make this better. Why is the start of the sector exclusive?
    # A vector pointing to the right of the quad.
    vec_right = coords[0] - coords[3]

    horizontal = Decimal.is_zero(__to_decimal(vec_right[Z], "1.0"))

    # There are 4 sectors of 90 degrees.
    # Sector 0 is from 315 degrees to 45 degrees.
    # Sector 1 is from 45 degrees to 135 degrees and so on.
    # However, by rotating the brick right vector by +45 degrees and assuming the sectors are:
    # 0: 0 to 90
    # 1: 90 to 180 etc.
    # I'm doing the exact same thing as with the non-axis aligned sectors but the math is much simpler.

    if horizontal:
        # +45 degree rotation around the Z axis.
        vec_right.rotate(Euler((0.0, 0.0, radians(45.0)), 'XYZ'))

        # ROUND & CAST
        posx = __to_decimal(vec_right[X]) >= 0
        posy = __to_decimal(vec_right[Y]) >= 0

        if posx and posy:
            return 0
        elif not posx and posy:
            return 1
        elif not posx and not posy:
            return 2
        else:
            # posx and not posy
            return 3
    else:
        # +45 degree rotation around the Y axis.
        vec_right.rotate(Euler((0.0, radians(45.0), 0.0), 'XYZ'))

        # ROUND & CAST
        posx = __to_decimal(vec_right[X]) > 0
        posz = __to_decimal(vec_right[Y]) > 0

        # You cannot win with vertical TOP texture.
        # This order is the best I could find.
        if posx and posz:
            return 2
        elif not posx and posz:
            return 3
        elif not posx and not posz:
            return 0
        else:
            # posx and not posz
            return 1


def __get_2d_angle_axis(angle, plane=AxisPlane3D.XY):
    """Gets an enum value representing the axis that is the closest to the specified angle.

    Args:
        angle (Number): An angle in radians in the range [0,2pi].
        plane (AxisPlane3D): The AB-plane the angle is aligned on. XY-plane by default.

    Returns:
        An Axis3D value representing a 90 degree sector on the specified AB-plane.
        Angles are CCW from the +A-axis.
           +A axis, sector [315, 45[ degrees.
           +B axis, sector [45, 135[ degrees.
           -A axis, sector [135, 225[ degrees.
           -B axis, sector [225, 315[ degrees.
    """
    # The angle could easily be normalized here, but doing this has helped me track a couple of mistakes in the code.
    if angle < 0 or angle > const.TWO_PI:
        # EXCEPTION
        raise ValueError("__get_2d_angle_axis(angle) expects angle to be normalized to range [0,2pi], value was:", angle)

    if angle >= const.RAD_315_DEG or angle >= 0 and angle < const.RAD_45_DEG:
        if plane == AxisPlane3D.XY:
            return Axis3D.POS_X
        elif plane == AxisPlane3D.XZ:
            return Axis3D.POS_X
        else:  # plane == AxisPlane3D.YZ
            return Axis3D.POS_Y

    # angle >= 45 and
    elif angle < const.RAD_135_DEG:
        if plane == AxisPlane3D.XY:
            return Axis3D.POS_Y
        elif plane == AxisPlane3D.XZ:
            return Axis3D.POS_Z
        else:  # plane == AxisPlane3D.YZ
            return Axis3D.POS_Z

    # angle >= 135 and
    elif angle < const.RAD_225_DEG:
        if plane == AxisPlane3D.XY:
            return Axis3D.NEG_X
        elif plane == AxisPlane3D.XZ:
            return Axis3D.NEG_X
        else:  # plane == AxisPlane3D.YZ
            return Axis3D.NEG_Y

    # angle >= 225 and angle < 315
    else:
        if plane == AxisPlane3D.XY:
            return Axis3D.NEG_Y
        elif plane == AxisPlane3D.XZ:
            return Axis3D.NEG_Z
        else:  # plane == AxisPlane3D.YZ
            return Axis3D.NEG_Z


def __get_normal_axis(normal):
    """Determines the closest axis of the specified normal vector.

    Args:
        normal (Vector): A normal vector in XYZ-space.

    Returns:
        An Axis3D value.
    """
    sign_x = numpy.sign(normal[X])
    sign_y = numpy.sign(normal[Y])
    sign_z = numpy.sign(normal[Z])
    point = False

    # atan(a/b) output is in range ]-pi/2,pi/2[
    # We need the angle in range [0,2pi] (or [0,2pi[, doesn't actually matter) for __get_2d_angle_axis(angle)
    # if a > 0 and b > 0: angle > 0: angle       is in range [0,2pi[
    # if a > 0 and b < 0: angle < 0: angle + pi  is in range [0,2pi[
    # if a < 0 and b > 0: angle < 0: 2pi + angle is in range [0,2pi[
    # if a < 0 and b < 0: angle > 0: angle + pi  is in range [0,2pi[

    # Check for axis-aligned cases.
    # Determine the plane the normal lies on (if any).
    # Calculate the angle of the normal on that plane with atan.

    # Normal in XYZ-space.
    if sign_x == 0:

        # Normal on YZ-plane.
        if sign_y == 0:

            # Normal on Z-axis.
            if sign_z == 0:
                # Normal is a point.
                point = True
            elif sign_z > 0:
                # Normal on +Z-axis.
                return Axis3D.POS_Z
            else:
                # Normal on -Z-axis.
                return Axis3D.NEG_Z

        elif sign_z == 0:

            # Normal on Y-axis.
            if sign_y > 0:
                # Normal on +Y-axis.
                return Axis3D.POS_Y
            else:
                # Normal on -Y-axis.
                return Axis3D.NEG_Y

        else:
            # Normal on YZ-plane, Y != 0.
            plane = AxisPlane3D.YZ
            angle = atan(normal[Z] / normal[Y])

            # Signs must be checked in this order.
            if sign_y < 0:
                angle = angle + pi
            elif sign_z < 0:  # angle < 0
                angle = const.TWO_PI + angle
    else:

        # Normal in XYZ-space, X != 0.
        if sign_y == 0:

            # Normal on XZ-plane.
            if sign_z == 0:

                # Normal on X-axis.
                if sign_x > 0:
                    # Normal on +X-axis.
                    return Axis3D.POS_X
                else:
                    # Normal on -X-axis.
                    return Axis3D.NEG_X

            else:
                # Normal on XZ-plane, X != 0, Z != 0.
                plane = AxisPlane3D.XZ
                angle = atan(normal[Z] / normal[X])

                if sign_x < 0:
                    angle = angle + pi
                elif sign_z < 0:  # angle < 0
                    angle = const.TWO_PI + angle

        elif sign_z == 0:
            # Normal in XY-plane, X != 0, Y != 0.
            plane = AxisPlane3D.XY
            angle = atan(normal[Y] / normal[X])

            if sign_x < 0:
                angle = angle + pi
            elif sign_y < 0:  # angle < 0
                angle = const.TWO_PI + angle

        else:
            # Normal in XYZ-space, X != 0, Y != 0, Z != 0.
            angle = None
            plane = None

    if point:
        # EXCEPTION
        raise ValueError("__get_normal_axis(normal) expects a vector, point '{}' given instead.".format(normal))

    if plane is None:
        # TODO: Z-axis is ignored for now. Assume XY-plane.
        plane = AxisPlane3D.XY
        angle = atan(normal[Y] / normal[X])

        if sign_x < 0:
            angle = angle + pi
        elif sign_y < 0:  # angle < 0
            angle = const.TWO_PI + angle

    return __get_2d_angle_axis(angle, plane)


def __string_to_uv_layer_name(string):
    """Creates the UV layer name for automatically calculated UVs from the specified string.

    Args:
        string (string): A string.

    Returns:
        A UV layer name.
    """
    return "{}{}".format(const.BLB_PREFIX_TEXTURE, string.upper())


def __calc_quad_max_edge_len_idx(sorted_verts):
    """Gets an index representing the axis that is the closest to the specified angle.

    Args:
        sorted_verts (2D matrix of Numbers): A sequence of 4 sequences, where each sequence contains the (X, Y, Z) coordinates of a vertex in a quad in CW order.

    Returns:
        A tuple containing two elements.
        Element 0: The length of the longest edge in the specified quad.
        Element 1: The index of the first vertex in CW order of the longest edge in the specified quad.
    """
    max_len = Decimal("-1")
    max_len_idx = -1
    #quad_center = Vector((0, 0))

    for idx in range(0, 4):
        this_vert = sorted_verts[idx]
        # ROUND & CAST: Length of edge from this vertex to the next one.
        length = __to_decimal(__distance(this_vert, sorted_verts[(idx + 1) % 4]))

        if length > max_len:
            max_len = length
            max_len_idx = idx

        #quad_center.x += this_vert[X]
        #quad_center.y += this_vert[Y]

    #quad_center.x /= 4.0
    #quad_center.y /= 4.0

    #v0 = sorted_verts[max_len_idx]
    #v1 = sorted_verts[(max_len_idx + 1) % 4]

    #max_len_center = Vector(((v0[X] + v1[X]) * 0.5, (v0[Y] + v1[Y]) * 0.5))

    #dx = max_len_center[X] - quad_center[X]
    #dy = max_len_center[Y] - quad_center[Y]

    # Angle in range [-pi, pi] from the positive X-axis.
    #max_len_angle = atan2(dy, dx)
    # Convert to range [0,2pi]
    #max_len_angle = 2 * pi + max_len_angle if max_len_angle < 0 else max_len_angle

    #angle_idx = __get_angle_axis_idx(max_len_angle)
    return (max_len, max_len_idx)


def __calculate_uvs(brick_texture, vert_coords, normal, forward_axis):
    """Calculates the UV coordinates for the specified texture and quad containing the specified vertices.
    In unsupported cases, default UVs are returned.

    Args:
        brick_texture (BrickTexture): A value from the BrickTexture enum.
        vert_coords (sequence of coordinates): A sequence of 4 local space coordinates of a face in CW order.
                                              The vertex order must be the same that is written to the BLB file.
        normal (sequence of numbers): The normal vector of the quad.
        forward_axis (Axis3D): A value of the Axis3D enum. The axis that will point forwards in-game.

    Returns:
        A tuple with two elements.
        The first element is a tuple containing 4 sets of UV coordinates (One pair for each vertex in the quad.) as tuples for the BLB file.
        The second element is a tuple containing the UV coordinates to be stored in the Blender mesh, or None if the coordinates are the same as the BLB ones.
    """
    def get_side_uv(length):
        """Calculates the U and V component for an edge of the specified length to use with the SIDE texture.

        Args:
            length (number): The length of an edge.

        Returns:
            The U or V component to use with SIDE texture UVs as a Decimal.
        """
        # The UV coordinate calculation equations were created by a Blockland Forums user BlackDragonIV about 5 years ago.
        # How he came up with it is anyone's guess.
        # The original equation uses a multiplier of 5 for the height, but I believe that is because it was designed to be used with brick sizes where the height is the height of the brick in number of plates.
        # The values used here are derived from vertex coordinates which means I can use the same equation for both U and V components.
        # Alternatively: (11 - (11 / length) * 2) / const.BRICK_TEXTURE_RESOLUTION
        # ROUND & CAST
        return __to_decimal((11 - 22 / length) / const.BRICK_TEXTURE_RESOLUTION)

    normal_axis = __get_normal_axis(normal)

    # Sanity check.
    if len(vert_coords) < 4:
        # EXCEPTION
        raise ValueError("__calculate_uvs(brick_texture, vert_coords, normal) function expects a quad, input polygon was not a quad.")

    idx_coord = [(idx, coord) for idx, coord in enumerate(vert_coords)]

    # Find the top left vertex of an arbitrary quad.

    # Sort sequence by Z coordinates high to low.
    max_z_coords = sorted(idx_coord, key=lambda k: [k[1][Z]], reverse=True)

    # Get maximum Z coordinate.
    max_z = max_z_coords[0][1][Z]

    # Remove coordinates from the sequence that are not on the same height with the highest vert.
    max_z_coords = [idx_coord for idx_coord in max_z_coords if idx_coord[1][Z] == max_z]

    # max_z_coords now contains all topmost vertices in the quad.
    # Now determine what "left" means according to the normal of the quad.

    if normal_axis.index() is X:
        # Quad aligned with X axis.
        # Sort sequence by Y coordinates.
        # If facing positive X axis, sort coordinates from -Y to +Y = not reversed.
        # Break ties by sorting by index.
        top_left_candidates = sorted(max_z_coords, key=lambda k: [k[1][Y], k[0]], reverse=not normal_axis.is_positive())
    elif normal_axis.index() is Y:
        # Quad aligned with Y axis.
        # Sort sequence by X coordinates.
        # If facing positive Y axis, sort coordinates from +X to -X = reversed.
        # Break ties by sorting by index.
        top_left_candidates = sorted(max_z_coords, key=lambda k: [k[1][X], k[0]], reverse=normal_axis.is_positive())
    else:  # normal_axis.index() is Z:
        # Quad aligned with Z axis.
        # Sort sequence by X coordinates.
        # Regardless if facing positive or negative Z axis, sort coordinates from -X to +X = not reversed.
        # Break ties by sorting by index.
        top_left_candidates = sorted(max_z_coords, key=lambda k: [k[1][X], k[0]], reverse=False)

    # top_left_candidates[0] is the vertex with the largest Z coordinate and smallest/largest coordinate on the appropriate axis.
    # Thus it is the top left corner of the quad in its local space.
    top_left_idx = top_left_candidates[0][0]

    sorted_idx_coord = idx_coord[top_left_idx:] + idx_coord[:top_left_idx]
    # Split the sorted sequence of (idx, coord) tuples into separate lists for ease of use.
    sorted_verts_idxs, sorted_verts = zip(*sorted_idx_coord)

    # print("__calculate_uvs | Sorted quad:")
    # for icoord in sorted_idx_coord:
    #    print("\t", icoord)

    # sorted_verts must be in CW order with element 0 being the top left corner.
    # ROUND & CAST: length using user specified precision.
    len_top = __to_decimal(__distance(sorted_verts[0], sorted_verts[1]))
    len_right = __to_decimal(__distance(sorted_verts[1], sorted_verts[2]))
    len_bottom = __to_decimal(__distance(sorted_verts[2], sorted_verts[3]))
    len_left = __to_decimal(__distance(sorted_verts[3], sorted_verts[0]))

    best_quad_size = __calculate_quad_width_height(len_top, len_right, len_bottom, len_left)

    # For clarity.
    # Width.
    w = best_quad_size[0]
    # Height.
    h = best_quad_size[1]

    # Initialize with default UVs.
    uvs_sorted = const.DEFAULT_UV_COORDINATES
    # May be assigned a value later.
    uvs_blender = None

    # UV tuples are in order: (u, v)
    # Where u is the x axis increasing from left to right.
    # Where v is the y axis increasing from top to bottom.
    if brick_texture is const.BrickTexture.TOP:
        # Works well for axis aligned faces horizontal faces.
        # Works well enough for axis aligned faces vertical faces.
        # Doesn't look bad for all other face orientations.
        # direction = __get_quad_dir_idx_top_tex(sorted_verts)

        uvs_sorted = ((w, h),
                      (0, h),
                      (0, 0),
                      (w, 0))

        if forward_axis is Axis3D.POS_X:
            uvs_blender = ((0, h),
                           (0, 0),
                           (w, 0),
                           (w, h))
        elif forward_axis is Axis3D.NEG_X:
            uvs_blender = ((w, 0),
                           (w, h),
                           (0, h),
                           (0, 0))
        elif forward_axis is Axis3D.POS_Y:
            uvs_blender = ((h, w),
                           (0, w),
                           (0, 0),
                           (h, 0))
        else:  # NEG_Y
            uvs_blender = ((0, 0),
                           (h, 0),
                           (h, w),
                           (0, w))

    elif brick_texture is const.BrickTexture.SIDE:
        # To calculate the UV coordinates for a non-rectangular quad, the and U and V components must be calculated separately for each side.
        # Calculate the UV components for top, left, right, and bottom edges of the quad.
        # If the quad is rectangular then the components of opposing sides are equal.
        u_t = get_side_uv(len_top)
        v_r = get_side_uv(len_right)
        u_b = get_side_uv(len_bottom)
        v_l = get_side_uv(len_left)

        # print("__calculate_uvs | Lengths:")
        # print("\tt", u_t, len_top)
        # print("\tr", v_r, len_right)
        # print("\tb", u_b, len_bottom)
        # print("\tl", v_l, len_left)

        # Subtracting from 1 mirrors the coordinate.
        uvs_sorted = ((u_t, v_l),
                      (1 - u_t, v_r),
                      (1 - u_b, 1 - v_r),
                      (u_b, 1 - v_l))
    elif brick_texture is const.BrickTexture.BOTTOMEDGE:
        # Bottom edge is a special case where the average width/height does not work and the top left may not be what was determined by the sorting algorithm above.
        # We need the length of the longest edge in the quad, the direction it is pointing, and the index of the first vertex of the longest edge (CW order).
        edge_info = __calc_quad_max_edge_len_idx(sorted_verts)
        max_len = edge_info[0]
        # This is the index of the new top left corner.
        top_left_offset = edge_info[1]

        # print("__calculate_uvs | bottomedge, first vertex of longest edge (CW):", top_left_offset)
        # print("__calculate_uvs | bottomedge, longest edge length:", max_len)

        uvs_sorted = ((-0.5, 0),
                      (max_len - const.DECIMAL_HALF, 0),
                      (max_len - 1, 0.5),
                      (0, 0.5))

        uvs_blender = __bl_blender_uv_origin_swap(uvs_sorted)

        if top_left_offset != 0:
            # Move each element in sorted_order forwards by top_left_offset and wrap around.
            # This maps element 0 = first vertex of longest edge in uvs_sorted to element 0 = first vertex in sorted_verts.
            # The UVs are later swizzled from sorted_verts order back to the BLB/Blender order for use in Blender.
            uvs_sorted = common.offset_sequence(uvs_sorted, top_left_offset)

            # print("__calculate_uvs | uvs_sorted after bottomedge swizzle:")
            # for uv in uvs_sorted:
            #     print("\t", uv)

    elif brick_texture is const.BrickTexture.BOTTOMLOOP:
        uvs_sorted = ((0, w),
                      (0, 0),
                      (h, 0),
                      (h, w))

    elif brick_texture is const.BrickTexture.PRINT:
        uvs_sorted = ((0, 0),
                      (1, 0),
                      (1, 1),
                      (0, 1))

    elif brick_texture is const.BrickTexture.RAMP:
        uvs_sorted = ((0, w),
                      (0, 0),
                      (h, 0),
                      (h, w))

    else:
        # EXCEPTION
        raise ValueError("Unknown texture name '{}'".format(brick_texture))

    #print("__calculate_uvs | uvs_sorted:")
    # for uv in uvs_sorted:
    #    print("\t", uv)

    # Calculate the offset.
    # Index 0 is always the first element in the input vertex order by definition.
    # Negate because we are doing the transformation backwards: we want 0 back to the start of the list.
    blb_to_blender_offset = -sorted_verts_idxs.index(0)
    # print("__calculate_uvs | Index offset:", blb_to_blender_offset)

    if blb_to_blender_offset == 0:
        uvs_blb = uvs_sorted
    else:
        # The vertices in Blender are in the order stored in idx_coord.
        # To calculate the UVs the vertices had to be sorted into sorted_verts.
        # sorted_verts are not necessarily in the same order as the vertices in idx_coord.
        # sorted_verts sequence contains 4 tuples where the first element of each tuple is the old index of that vertex (or UV coordinate).
        # To map the calculated BLB UV coordinates into something usable in Blender, we need to swizzle the UV pairs back into the old order.
        uvs_blb = common.offset_sequence(uvs_sorted, blb_to_blender_offset)

    #print("__calculate_uvs | uvs_blb:")
    # for uv in uvs_blb:
    #    print("\t", uv)
    # if uvs_blender:
    #    print("__calculate_uvs | uvs_blender:")
    #    for uv in uvs_blender:
    #        print("\t", uv)

    return (uvs_blb, uvs_blender)


def __bl_blender_uv_origin_swap(uvs):
    """Converts Blockland (origin is top left) to Blender (origin is bottom left) UV coordinates and the other way around.

    Args:
        uvs (sequence): A sequence of sequences containing UV pairs.

    Returns:
        A new tuple of transformed coordinate tuples.
    """
    return tuple([(uv[X], 1 - uv[Y]) for uv in uvs])


def __get_first_uv_data(uv_layers, mesh_loops, loop_indices, generated_uv_layer_names=None):
    """Finds the alphabetically first UV layer that contains UV coordinates other than (0.0, 0.0) for at least one vertex in the specified loop in the specified mesh.

    Args:
        uv_layers (OrderedDict): An ordered dictionary containing the UV layer name as key, and the UV layer data as value, alphabetically ordered by UV layer name.
        mesh_loops (sequence of MeshLoop): A Blender collection of MeshLoop objects.
        loop_indices (sequence of numbers): The sequence of indices of this loop (polygon) in the specified mesh.
        generated_uv_layer_names (sequence of strings): A sequence of UV layer names that are generated in code.
                                                        If not None, only manually created UV data (not in any of the generated layers) is checked for.

    Returns:
        A tuple containing the UV layer name in the first element and the sequence of UV coordinates in the second element.
        None if the specified polygon had no UV data in any of the UV layers.
    """
    uv_key = None

    # Loop through loop indices (vertices).
    for loop_idx in loop_indices:
        current_loop = mesh_loops[loop_idx]

        # Check UV coordinates for each vertex on every UV layer.
        for name, uv_loop in uv_layers.items():
            if generated_uv_layer_names is not None and name in generated_uv_layer_names:
                # Skip generated UV layers.
                continue
            vertex_uv = uv_loop.data[current_loop.index].uv
            # ROUND & CAST
            # By default all UV coordinates in a layer are (0.0, 0.0).
            # If either UV coordinate is not zero, this UV layer is the first that has some data.
            if not Decimal.is_zero(__to_decimal(vertex_uv[X])) or not Decimal.is_zero(__to_decimal(vertex_uv[Y])):
                uv_key = name
                break
        # Did we find a name?
        if uv_key is not None:
            break

    if uv_key is None:
        return None
    else:
        uv_loop_data = uv_layers[uv_key].data
        return (uv_key, [uv_loop_data[mesh_loops[loop_idx].index].uv for loop_idx in loop_indices])


def __store_uvs_in_mesh(poly_index, mesh, uvs, layer_name):
    """Stores the specified UV coordinates in a UV layer.
    A new UV layer is created if it does not exist, data in an existing UV layer with the same name will be overwritten.

    Args:
        poly_index (int): Index of the polygon in the mesh.
        mesh (Blender Mesh): The mesh to store the UVs in.
        uvs (sequence of sequences): A sequence containing UV pairs.
        layer_name (string): Name to give the UV layer.

    Returns:
        None if UVs were stored successfully or a string containing an error message.
    """
    error_string = "IOBLBF002 Unable to store UV coordinates in object '{}' while it is in edit mode.".format(mesh.name)

    # If no UV layer exists, create one.
    if layer_name not in mesh.uv_layers.keys():
        mesh.uv_textures.new(layer_name)

    # You need BMesh to modify the UV layers.
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Blender complains if this isn't done.
    # Apparently you shouldn't do this in tight loops.
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # Get the UV layer in BMesh format.
    bm_uv_layer = bm.loops.layers.uv.get(layer_name)

    # RETURN ON ERROR
    for vert_idx, uv_pair in enumerate(uvs):
        try:
            bm.faces[poly_index].loops[vert_idx][bm_uv_layer].uv = uv_pair
        except AttributeError:
            return error_string
    try:
        bm.to_mesh(mesh)
    except ValueError:
        return error_string


def __process_grid_definitions(properties, blb_data, bounds_data, definition_objects):
    """Processes the specified brick grid definitions.

    Args:
        properties (DerivateProperties): An object containing user properties.
        blb_data (BLBData): A BLBData object containing all the necessary data for writing a BLB file.
        bounds_data (BrickBounds): A BrickBounds object containing the bounds data.
        definition_objects (a sequence of sequences of Blender objects): A sequence containing five sequences of Blender objects representing brick grid definitions.
                                                                        The second sequences must ordered in the reverse priority order.

    Returns:
        A three dimensional array of brick grid symbols, ready for writing to a file.
    """
    # Make one empty list for each of the 5 brick grid definition.
    definition_volumes = [[] for i in range(5)]
    processed = 0
    total_definitions = 0

    for index in range(5):
        for grid_obj in definition_objects[index]:
            total_definitions += 1

            try:
                definition_volumes[index].append(__grid_object_to_volume(properties, bounds_data, grid_obj))
                processed += 1
            except OutOfBoundsException:
                if bounds_data.object_name is None:
                    logger.error(
                        "IOBLBE000",
                        "Brick grid definition object '{}' has vertices outside the calculated brick bounds. Definition ignored.".format(
                            grid_obj.name),
                        1)
                else:
                    logger.error("IOBLBE001", "Brick grid definition object '{}' has vertices outside the bounds definition object '{}'. Definition ignored.".format(
                        grid_obj.name, bounds_data.object_name))
            except ZeroSizeException:
                logger.error("IOBLBE002", "Brick grid definition object '{}' has no volume. Definition ignored.".format(grid_obj.name))

    # Log messages for brick grid definitions.
    if total_definitions < 1:
        logger.warning("IOBLBW004", "No brick grid definitions found. Full cuboid brick grid may be undesirable.", 1)
    elif total_definitions == 1:
        if processed < 1:
            logger.warning("IOBLBW005", "{} brick grid definition found but was not processed. Full cuboid brick grid may be undesirable.".format(total_definitions), 1)
        else:
            logger.info("Processed {} of {} brick grid definition.".format(processed, total_definitions), 1)
    else:
        # Found more than one.
        if processed < 1:
            logger.warning("IOBLBW005", "{} brick grid definitions found but were not processed. Full cuboid brick grid may be undesirable.".format(total_definitions), 1)
        else:
            logger.info("Processed {} of {} brick grid definitions.".format(processed, total_definitions), 1)

    # Take the custom forward axis into account.
    if properties.forward_axis is Axis3D.POS_X or properties.forward_axis is Axis3D.NEG_X:
        grid_width = blb_data.brick_size[X]
        grid_depth = blb_data.brick_size[Y]
    else:
        grid_width = blb_data.brick_size[Y]
        grid_depth = blb_data.brick_size[X]

    grid_height = blb_data.brick_size[Z]

    # Initialize the brick grid with the empty symbol with the dimensions of the brick.
    brick_grid = [[[const.GRID_OUTSIDE for w in range(grid_width)] for h in range(grid_height)] for d in range(grid_depth)]

    if total_definitions < 1:
        # Write the default brick grid.
        for d in range(grid_depth):
            for h in range(grid_height):
                is_top = (h == 0)  # Current height is the top of the brick?
                is_bottom = (h == grid_height - 1)  # Current height is the bottom of the brick?

                if is_bottom and is_top:
                    symbol = const.GRID_BOTH
                elif is_bottom:
                    symbol = const.GRID_DOWN
                elif is_top:
                    symbol = const.GRID_UP
                else:
                    symbol = const.GRID_INSIDE

                # Create a new list of the width of the grid filled with the selected symbol.
                # Assign it to the current height.
                brick_grid[d][h] = [symbol] * grid_width
    else:
        # Write the calculated definition_volumes into the brick grid.
        for index, volumes in enumerate(definition_volumes):
            # Get the symbol for these volumes.
            symbol = properties.grid_definitions_priority[index]
            for volume in volumes:
                # Modify the grid by adding the symbol to the correct locations.
                __modify_brick_grid(brick_grid, volume, symbol)

    return brick_grid


def __process_collision_definitions(properties, blb_data, bounds_data, definition_objects):
    """Processes the specified collision definitions.

    Args:
        properties (DerivateProperties): An object containing user properties.
        blb_data (BLBData): A BLBData object containing all the necessary data for writing a BLB file.
        bounds_data (BrickBounds): A BrickBounds object containing the bounds data.
        definition_objects (a sequence of Blender object): A sequence of Blender objects representing collision definitions.

    Returns:
        A sequence of tuples: [ (center coordinates in the local space of the brick, collision cuboid dimensions), ]
        Sequence can be empty.
    """
    collisions = []
    processed = 0

    if properties.blendprop.custom_collision:
        if len(definition_objects) > const.MAX_BRICK_COLLISION_CUBOIDS:
            logger.error("IOBLBE003", "{0} collision cuboids defined but {1} is the maximum. Only the first {1} will be processed.".format(
                len(definition_objects), const.MAX_BRICK_COLLISION_CUBOIDS), 1)

        for obj in definition_objects[:const.MAX_BRICK_COLLISION_CUBOIDS]:
            vert_count = len(obj.data.vertices)

            # At least two vertices are required for a valid bounding box.
            if vert_count < 2:
                logger.error("IOBLBE004", "Collision definition object '{}' has less than 2 vertices. Definition ignored.".format(obj.name), 1)
                # Skip the rest of the loop and return to the beginning.
                continue
            elif vert_count > 8:
                logger.info(
                    "Collision definition object '{}' has more than 8 vertices suggesting a shape other than a cuboid. The bounding box of this mesh will be used.".format(
                        obj.name),
                    1)
                # The mesh is still valid.

            # Find the minimum and maximum coordinates for the collision object.
            col_min, col_max = __get_world_min_max(obj)

            # ROUND & CAST
            # USER SCALE: Multiply by user defined scale.
            col_min = __multiply_sequence(properties.scale, __to_decimal(col_min))
            col_max = __multiply_sequence(properties.scale, __to_decimal(col_max))

            # Recenter the coordinates to the bounds. (Also rounds the values.)
            col_min = __world_to_local(col_min, bounds_data.world_center)
            col_max = __world_to_local(col_max, bounds_data.world_center)

            # Technically collision outside brick bounds is not invalid but the collision is also horribly broken and as such is not allowed.
            if __all_within_bounds(col_min, bounds_data.dimensions) and __all_within_bounds(col_max, bounds_data.dimensions):
                if not __has_volume(col_min, col_max):
                    logger.error("IOBLBE005", "Collision definition object '{}' has no volume. Definition ignored.".format(obj.name), 1)
                    # Skip the rest of the loop.
                    continue

                center = []
                dimensions = []

                # Find the center coordinates and dimensions of the cuboid.
                for index, value in enumerate(col_max):
                    center.append((value + col_min[index]) * const.DECIMAL_HALF)
                    dimensions.append(value - col_min[index])

                # ROUND & CAST
                # Add the center and dimensions to the definition data as a tuple.
                # The center coordinates and dimensions are in plate coordinates.
                collisions.append((__sequence_z_to_plates(center, properties.plate_height), __sequence_z_to_plates(dimensions, properties.plate_height)))

                processed += 1
            else:
                if bounds_data.object_name is None:
                    logger.error(
                        "IOBLBE006",
                        "Collision definition object '{}' has vertices outside the calculated brick bounds. Definition ignored.".format(
                            obj.name),
                        1)
                else:
                    logger.error("IOBLBE007", "Collision definition object '{}' has vertices outside the bounds definition object '{}'. Definition ignored.".format(
                        obj.name, bounds_data.object_name), 1)

        defcount = len(definition_objects)

        # Log messages for collision definitions.
        if defcount < 1:
            logger.info("No custom collision definitions found.", 1)
        elif defcount == 1:
            if processed < 1:
                logger.warning("IOBLBW006", "{} collision definition found but was not processed.".format(defcount), 1)
            else:
                logger.info("Processed {} of {} collision definition.".format(processed, defcount), 1)
        else:
            # Found more than one.
            if processed < 1:
                logger.warning("IOBLBW006", "{} collision definitions found but were not processed.".format(defcount), 1)
            else:
                logger.info("Processed {} of {} collision definitions.".format(processed, defcount), 1)

    if processed < 1:
        # No custom collision definitions.
        if properties.blendprop.fallback_collision == "BOUNDS":
            logger.info("Using bounds as the collision cuboid.", 1)
            # Center of the full brick collision cuboid is at the middle of the brick.
            # The size of the cuboid is the size of the bounds.
            collisions.append(([0, 0, 0], blb_data.brick_size))
        else:
            # properties.blendprop.default_collision == "AABB"
            logger.info("Using the axis-aligned bounding box of visual meshes as the collision cuboid.", 1)
            collisions.append(
                (__world_to_local(
                    bounds_data.aabb_world_center,
                    bounds_data.world_center),
                 __sequence_z_to_plates(
                     bounds_data.aabb_dimensions,
                     properties.plate_height)))

    return collisions


def __process_definition_objects(properties, objects):
    """"Processes all definition objects that are not exported as a 3D model but will affect the brick properties.blendprop.

    Processed definition objects:
        - bounds
        - brick grid
        - collision

    If no bounds object is found, the brick bounds will be automatically calculated using the minimum and maximum coordinates of the vertices in the visible mesh objects.

    Args:
        properties (DerivateProperties): An object containing user properties.
        objects (sequence of Blender objects): The sequence of objects to be processed.

    Returns:
        A tuple containing:
            0. A BLBData object containing the bounds, brick grid, and collision data.
            1. A BrickBounds object containing the brick bounds data.
            2. A sequence of mesh objects that will be exported as visible 3D models.
        Or an error message to be displayed to the user.
    """
    def calculate_aabb(bounds_data, min_world_coord, max_world_coord):
        """Calculates the axis-aligned bounding box data for the specified minimum and maximum world coordinates of visual meshes and stores them to the specified bounds_data object.

        Args:
            bounds_data (BrickBounds): A BrickBounds object containing the bounds data.
            min_coords (sequence of numbers): The minimum coordinates as a sequence: [X, Y, Z]
            max_coords (sequence of numbers): The maximum coordinates as a sequence: [X, Y, Z]
        """
        min_coord = __multiply_sequence(properties.scale, __to_decimal(min_world_coord))
        max_coord = __multiply_sequence(properties.scale, __to_decimal(max_world_coord))

        bounds_data.aabb_dimensions = __calculate_bounding_box_size(min_coord, max_coord)
        bounds_data.aabb_world_center = __calculate_center(min_coord, bounds_data.aabb_dimensions)
        # print("Calculated AABB. Min:", min_coord, "Max:", max_coord, "Size:", bounds_data.aabb_dimensions, "Center:", bounds_data.aabb_world_center)

    blb_data = BLBData()
    bounds_data = None
    collision_objects = []

    # There are 5 brick grid definitions.
    # During this first pass of the objects in the scene we can already sort the definition objects.
    brick_grid_objects = [[] for i in range(5)]

    mesh_objects = []

    # These are vectors because Blender vertex coordinates are stored as vectors.
    # They are used for recording the minimum and maximum vertex world
    # coordinates of all visible meshes so that the brick bounds can be
    # calculated, if they are not defined manually.
    min_world_coordinates = Vector((float("+inf"), float("+inf"), float("+inf")))
    max_world_coordinates = Vector((float("-inf"), float("-inf"), float("-inf")))

    # Loop through all objects in the sequence.
    # The objects in the sequence are sorted so that the oldest created object is last.
    # Process the objects in reverse: from oldest to newest.
    for obj in reversed(objects):

        # PROCESS TOKENS.

        obj_name = obj.name
        obj_name_tokens = __split_object_string_to_tokens(obj_name)
        object_grid_definitions = __get_tokens_from_object_name(obj_name_tokens, properties.grid_def_obj_token_priority)

        # Ignore non-mesh objects
        if obj.type != "MESH":
            if obj_name.upper().startswith(properties.deftokens.bounds):
                logger.error("IOBLBE008", "Object '{}' cannot be used to define bounds, must be a mesh.".format(obj_name), 1)
            elif obj_name.upper().startswith(properties.grid_def_obj_token_priority):
                logger.error("IOBLBE009", "Object '{}' cannot be used to define brick grid, must be a mesh.".format(obj_name), 1)
            elif obj_name.upper().startswith(properties.deftokens.collision):
                logger.error("IOBLBE010", "Object '{}' cannot be used to define collision, must be a mesh.".format(obj_name), 1)

            # Skip the rest of the if.
            continue

        # Is the current object a bounds definition object?
        elif properties.deftokens.bounds in obj_name_tokens:
            if bounds_data is None:
                bounds_data = __process_bounds_object(properties.scale, obj)
                blb_data = __record_bounds_data(properties, blb_data, bounds_data)

                if isinstance(blb_data, str):
                    # Got an error message.
                    return blb_data
                else:
                    plates, bricks = modf(blb_data.brick_size[Z] / 3)
                    bricks = int(bricks)

                    if plates == 0.0:
                        logger.info("Defined brick size: {} wide {} deep and {} tall".format(blb_data.brick_size[X],
                                                                                             blb_data.brick_size[Y],
                                                                                             logger.build_countable_message("", bricks, (" brick", " bricks"))), 1)
                    else:
                        logger.info("Defined brick size: {} wide {} deep {} and {} tall".format(blb_data.brick_size[X],
                                                                                                blb_data.brick_size[Y],
                                                                                                logger.build_countable_message(
                                                                                                    "", bricks, (" brick", " bricks")),
                                                                                                logger.build_countable_message("", blb_data.brick_size[Z] - bricks * 3, (" plate", " plates"))), 1)
            else:
                logger.error("IOBLBE011", "Bounds already defined by '{}', bounds definition '{}' ignored.".format(bounds_data.object_name, obj_name), 1)
                continue

        # Is the current object a collision definition object?
        elif properties.deftokens.collision in obj_name_tokens:
            # Collision definition objects cannot be processed until after the bounds have been defined.
            collision_objects.append(obj)

        # Is the current object a brick grid definition object?
        elif len(object_grid_definitions) > 0:
            if len(object_grid_definitions) > 1:
                logger.error("IOBLBE012", "Multiple brick grid definitions in object '{}', only the first one is used.".format(obj_name), 1)

            # Get the priority index of this grid definition.
            index = properties.grid_def_obj_token_priority.index(object_grid_definitions[0])

            # Brick grid definition objects cannot be processed until after the bounds have been defined.
            # Append the current definition object into the appropriate list.
            brick_grid_objects[index].append(obj)

        # Else the object must be a regular visible mesh that is exported as a 3D model.
        else:
            mesh_objects.append(obj)

            # Record min/max world coordinates for calculating the axis-aligned bounding box.
            min_world_coordinates, max_world_coordinates = __get_world_min_max(obj, min_world_coordinates, max_world_coordinates)

    # No manually created bounds object was found, calculate brick bounds based on the minimum and maximum recorded mesh vertex positions.
    if bounds_data is None:
        logger.warning("IOBLBW007", "No brick bounds definition found. Calculated brick size may be undesirable.", 1)

        # ROUND & CAST
        bounds_data = __calculate_bounds(properties.scale, __to_decimal(min_world_coordinates), __to_decimal(max_world_coordinates))

        blb_data = __record_bounds_data(properties, blb_data, bounds_data)

        if isinstance(blb_data, str):
            # Got an error message.
            return blb_data
        else:
            plates, bricks = modf(blb_data.brick_size[Z] / 3)

        bricks = int(bricks)

        if plates == 0.0:
            logger.info("Calculated brick size: {} wide {} deep and {} tall".format(blb_data.brick_size[X],
                                                                                    blb_data.brick_size[Y],
                                                                                    logger.build_countable_message("", bricks, (" brick", " bricks"))), 1)
        else:
            logger.info("Calculated brick size: {} wide {} deep {} and {} tall".format(blb_data.brick_size[X],
                                                                                       blb_data.brick_size[Y],
                                                                                       logger.build_countable_message("", bricks, (" brick", " bricks")),
                                                                                       logger.build_countable_message("", blb_data.brick_size[Z] - bricks * 3, (" plate", " plates"))), 1)
    elif len(mesh_objects) > 0:
        # Manually defined bounds found, store the axis-aligned bounding box of the visible meshes, provided there are any.
        calculate_aabb(bounds_data, min_world_coordinates, max_world_coordinates)

    # Bounds have been defined, check that brick size is within the limits.
    if blb_data.brick_size[X] <= const.MAX_BRICK_HORIZONTAL_PLATES and blb_data.brick_size[
            Y] <= const.MAX_BRICK_HORIZONTAL_PLATES and blb_data.brick_size[Z] <= const.MAX_BRICK_VERTICAL_PLATES:
        # Multiply the dimensions of the bounding box together: if any dimension is 0.0 the product is 0.0.
        if __sequence_product(blb_data.brick_size) < 1.0:
            # TODO: Actually test this.
            # TODO: Round 0 brick size up to 1?
            # RETURN ON ERROR
            return "IOBLBF003 Brick has no volume, brick could not be rendered in-game."
        else:
            # Process brick grid and collision definitions now that a bounds definition exists.
            blb_data.brick_grid = __process_grid_definitions(properties, blb_data, bounds_data, brick_grid_objects)
            blb_data.collision = __process_collision_definitions(properties, blb_data, bounds_data, collision_objects)

            # Return the data.
            return (blb_data, bounds_data, mesh_objects)
    else:
        # RETURN ON ERROR
        # The formatter fails miserably if this return is on one line so I've broken it in two.
        msg = "IOBLBF004 Brick size ({0}x{1}x{2}) exceeds the maximum brick size of {3} wide {3} deep and {4} plates tall.".format(blb_data.brick_size[X],
                                                                                                                                   blb_data.brick_size[Y],
                                                                                                                                   blb_data.brick_size[Z],
                                                                                                                                   const.MAX_BRICK_HORIZONTAL_PLATES,
                                                                                                                                   const.MAX_BRICK_VERTICAL_PLATES)
        return "{}\nThe exported brick would not be loaded by the game.".format(msg)


def __process_mesh_data(context, properties, bounds_data, mesh_objects, forward_axis):
    """Gets all the necessary data from the specified Blender objects and sorts all the quads of the mesh_objects into sections for brick coverage to work.

    Args:
        context (Blender context object): A Blender object containing scene data.
        properties (DerivateProperties): An object containing user properties.
        bounds_data (BrickBounds): A BrickBounds object containing the bounds data.
        mesh_objects (sequence of Blender objects): Meshes to be processed.
        forward_axis (Axis3D): A value of the Axis3D enum. The axis that will point forwards in-game.

    Returns:
        A sequence of mesh data sorted into sections or a string containing an error message to display to the user.
    """
    # Create an empty list for each quad section.
    # This is my workaround to making a sort of dictionary where the keys are in insertion order.
    # The quads must be written in a specific order.
    # A tuple cannot be used because the values are changed afterwards when the brick is rotated.
    quads = [[] for i in range(len(const.BLBQuadSection))]

    for obj in mesh_objects:
        count_tris = 0
        count_ngon = 0
        object_name = obj.name
        current_mesh = obj.data

        # Alpha is per-object.
        vertex_color_alpha = None

        logger.info("Exporting object: {}".format(object_name), 1)

        # PROCESS TOKENS

        # PROCESS OBJECT DATA

        # =============
        # Object Colors
        # =============
        colors = None

        if properties.blendprop.use_object_colors:
            tokens = __split_object_string_to_tokens(object_name, True)

            # Does the object name contain the color definition token signifying that it defines the object's color?
            if properties.deftokens.color in tokens:
                # Parse floats from the expected color values.
                floats = __get_color_values(tokens[tokens.index(properties.deftokens.color) + 1:])
                num_count = len(floats)

                # Did user define at least 4 numerical values?
                if num_count >= 4:
                    if num_count > 4:
                        logger.error("IOBLBE013", "More than 4 color values defined for object '{}', only the first 4 values (RGBA) are used.".format(object_name), 2)

                        # We're only interested in the first 4 values: R G B A
                        floats = floats[:4]

                    # Add the RGBA values to the colors, 4 vertices per quad.
                    colors = ([tuple(floats)] * 4)
                elif num_count > 0:
                    logger.info(
                        "Object '{}' is named as if it has custom color but it was ignored because all 4 values (red green blue alpha) were not defined.".format(object_name), 2)

        # Vertex color layer message.
        if len(current_mesh.vertex_colors) > 1:
            logger.warning("IOBLBW008", "Object '{}' has {} vertex color layers, only using the first.".format(
                object_name, len(current_mesh.vertex_colors)), 2)

        # ===================
        # Manual Quad Sorting
        # ===================
        # Manual sorting is per-object.
        section = None
        reset_section = True

        quad_sections = __get_tokens_from_object_name(object_name, properties.quad_sort_definitions)
        section_count = len(quad_sections)

        if section_count >= 1:
            section = const.BLBQuadSection(properties.quad_sort_definitions.index(quad_sections[0]))
            if section_count > 1:
                logger.error("IOBLBE014", "Object '{}' has {} section definitions, only using the first one: {}".format(
                    object_name, section_count, section), 2)

            # TODO: Do forward axis rotation of section in the format_blb_data function?
            # The section needs to rotated according to the forward axis.
            section = __rotate_section_value(section, properties.forward_axis)
            reset_section = False
        # Else: No manual sort.

        # This function creates a new mesh datablock.
        # It needs to be manually deleted later to release the memory, otherwise it will stick around until Blender is closed.
        mesh = obj.to_mesh(context.scene, properties.blendprop.use_modifiers, "PREVIEW", False, False)

        # PROCESS QUAD DATA

        for poly in mesh.polygons:
            # ===================
            # Vertex loop indices
            # ===================
            # Reverse the loop_vert_idxs tuple to CW order. (Blender has a CCW winding order in regards to the face normal.)
            if poly.loop_total == 4:
                # Quad.
                loop_vert_idxs = tuple(reversed(poly.loop_indices))
            elif poly.loop_total == 3:
                # Tri.
                loop_vert_idxs = tuple(reversed(poly.loop_indices)) + (poly.loop_start,)
                count_tris += 1
            else:
                # N-gon.
                count_ngon += 1
                # Cannot process n-gons, skip.
                continue

            # ================
            # Vertex positions
            # ================
            poly_vertex_obj_coords = []
            positions = []

            for vert_idx in loop_vert_idxs:
                # ROUND & CAST
                # Center the position to the current bounds object: coordinates are now in local object space.
                coords = __world_to_local(__to_decimal(__get_vert_world_coord(obj, mesh, vert_idx)), bounds_data.world_center)
                poly_vertex_obj_coords.append(coords)

                # Scale local coordinates according to user-specified scale.
                # Scale local coordinates to brick grid: adjust Z-coordinate.
                # Append to the list of coordinates.
                # USER SCALE: Multiply by user defined scale.
                positions.append(__sequence_z_to_plates(__multiply_sequence(properties.scale, coords), properties.plate_height))

            # ======================
            # Automatic Quad Sorting
            # ======================
            # And the current object does not have a manual definition?
            if section is None:
                reset_section = True
                # Does user want to automatically sort quads?
                if properties.blendprop.auto_sort_quads:
                    # Calculate the section name the quad belongs to.
                    section = __sort_quad(positions, bounds_data.dimensions, properties.plate_height)
                    section = __rotate_section_value(section, properties.forward_axis)
                else:
                    # No auto sort, no definition, use omni.
                    section = const.BLBQuadSection.OMNI
            # Else: The quad had a manual sort, in which case there is no point in calculating the section per quad.

            # =======
            # Normals
            # =======
            poly_normal_normalized = __normalize_vector(obj, poly.normal)

            if poly.use_smooth:
                # Smooth shading.
                # For every loop index in the loop_vert_idxs, calculate the vertex normal and add it to the list.

                # Does the user want to round normals?
                if properties.blendprop.round_normals:
                    # ROUND & CAST
                    normals = [__to_decimal(__loop_index_to_normal_vector(obj, mesh, vert_idx)) for vert_idx in loop_vert_idxs]
                else:
                    normals = [__loop_index_to_normal_vector(obj, mesh, vert_idx) for vert_idx in loop_vert_idxs]
            else:
                # Flat shading: every vertex in this loop has the same normal.
                # A tuple cannot be used because the values are changed afterwards when the brick is rotated.
                # Note for future: I initially though it would be ideal to NOT round the normal values in order to acquire the most accurate results but this is actually false.
                # Vertex coordinates are rounded. The old normals are no longer valid even though they are very close to the actual value.

                # Does the user want to round normals?
                if properties.blendprop.round_normals:
                    # ROUND & CAST
                    normals = [__to_decimal(poly_normal_normalized), ] * 4
                else:
                    normals = [poly_normal_normalized, ] * 4

            # ================
            # BLB texture name
            # ================
            brick_texture = None

            if current_mesh.materials and current_mesh.materials[poly.material_index] is not None:
                matname = current_mesh.materials[poly.material_index].name
                texnames = __get_tokens_from_object_name(matname, const.BrickTexture.as_list())
                texcount = len(texnames)

                if texcount > 0:
                    brick_texture = const.BrickTexture[texnames[0]]

                    if texcount > 1:
                        logger.error("IOBLBE015", "More than one brick texture name found in material '{}', only using the first one.".format(matname), 2)
            # else: No material name or a brick texture was not specified. Keep None to skip automatic UV generation.

            # ===
            # UVs
            # ===
            # TODO: Generate mesh data for the brick bottom if 'bottom' material is used.
            uvs = None

            # Join all material names into one string.
            generated_uv_layer_names = " ".join(current_mesh.materials.keys())
            # Get only the brick texture names.
            generated_uv_layer_names = __get_tokens_from_object_name(generated_uv_layer_names, const.BrickTexture.as_list())
            # List of possible layer names based on the materials of this mesh.
            generated_uv_layer_names = [__string_to_uv_layer_name(texnames) for texnames in generated_uv_layer_names]

            # Sort UV layers by name.
            uv_dict = {key: value for key, value in mesh.uv_layers.items()}
            sorted_uv_layers = OrderedDict(sorted(uv_dict.items()))

            # Get the UV data from the first UV layer that contains non (0.0, 0.0) coordinates for this polygon and doesn't have a generated name.
            uv_data = __get_first_uv_data(sorted_uv_layers, current_mesh.loops, poly.loop_indices, generated_uv_layer_names)

            if uv_data is None:
                # Get the UV data from the first UV layer that contains non (0.0, 0.0) coordinates for this polygon.
                uv_data = __get_first_uv_data(sorted_uv_layers, current_mesh.loops, poly.loop_indices)

            # Does UV data exist for this polygon?
            if uv_data:
                uv_data_generated = uv_data[0] in generated_uv_layer_names

                # Is the UV data manually created?
                if not uv_data_generated:
                    # Swap UV coordinate origin from bottom left to top left.
                    # Blender UV (and vertex) coordinates are in reverse order compared to Blockland so their order needs to be reversed.
                    uvs = __bl_blender_uv_origin_swap(uv_data[1])[::-1]

                    if brick_texture is None:
                        # Fall back to SIDE texture if nothing was specified.
                        brick_texture = const.BrickTexture.SIDE
                        logger.warning("IOBLBW009", "Face has UV coordinates but no brick texture was set in the material name, using SIDE by default.", 2)

                    # Do we have UV coordinates for a tri?
                    if len(uvs) == 3:
                        # Repeat last coordinate.
                        uvs = uvs + (uvs[2],)
                # else: UV data is generated, overwrite data.
            # else: No UV data, generate UVs, or use defaults.

            if uvs is None:
                # Calculating UVs and a brick texture was specified
                if properties.blendprop.calculate_uvs and brick_texture is not None:
                    uvs = __calculate_uvs(brick_texture, poly_vertex_obj_coords, poly_normal_normalized, forward_axis)

                    if properties.blendprop.store_uvs:
                        if uvs[1] is not None:
                            # Put the special Blender UVs into the Blender mesh.
                            error_message = __store_uvs_in_mesh(poly.index, current_mesh, uvs[1], __string_to_uv_layer_name(brick_texture.name))
                        else:
                            # Put the calculated UVs into the Blender mesh.
                            error_message = __store_uvs_in_mesh(poly.index, current_mesh, uvs[0], __string_to_uv_layer_name(brick_texture.name))

                    if error_message is None:
                        uvs = uvs[0]
                    else:
                        return error_message
                else:
                    # No UVs present, no calculation: use the defaults.
                    # These UV coordinates with the SIDE texture lead to a blank textureless face.
                    uvs = const.DEFAULT_UV_COORDINATES
                    brick_texture = const.BrickTexture.SIDE

            # ===============
            # Material Colors
            # ===============
            # Material colors override objects colors since they are better and easier to use.
            if properties.blendprop.use_materials:
                # Object has material slots?
                if len(obj.material_slots) > 0:
                    material = obj.material_slots[poly.material_index].material
                    tokens = __split_object_string_to_tokens(material.name)

                    if material is not None:
                        if properties.deftokens.color_add in tokens:
                            # Negative alpha.
                            colors = ([(material.diffuse_color.r, material.diffuse_color.g, material.diffuse_color.b, -material.alpha)] * 4)
                        elif properties.deftokens.color_sub in tokens:
                            # Negative everything.
                            colors = ([(-material.diffuse_color.r, -material.diffuse_color.g, -material.diffuse_color.b, -material.alpha)] * 4)
                        elif properties.deftokens.color_blank in tokens:
                            # If the material name is "blank", use the spray can color by not defining any color for this quad.
                            # This is how quads that can change color (by colorshifting) in DTS meshes (which Blockland uses) are defined.
                            colors = None
                        else:
                            # 4 vertices per quad.
                            colors = ([(material.diffuse_color.r, material.diffuse_color.g, material.diffuse_color.b, material.alpha)] * 4)

            # =============
            # Vertex Colors
            # =============
            # Vertex colors override material colors since they are more detailed.

            if properties.blendprop.use_vertex_colors:
                # A vertex color layer exists.
                if len(current_mesh.vertex_colors) != 0:
                    colors = []

                    for index in loop_vert_idxs:
                        # Only use the first color layer.
                        # color_layer.data[index] may contain more than 4 values.
                        loop_color = current_mesh.vertex_colors[0].data[index]
                        layer_name = current_mesh.vertex_colors[0].name.replace(",", ".")
                        tokens = __split_object_string_to_tokens(layer_name)

                        if properties.deftokens.color_add in tokens:
                            addsub = 1
                            # Remove the token and only leave the alpha value.
                            tokens.remove(properties.deftokens.color_add)
                        elif properties.deftokens.color_sub in tokens:
                            addsub = -1
                            tokens.remove(properties.deftokens.color_sub)
                        else:
                            addsub = 0

                        # Use the color layer name as the value for alpha, if it is numerical.
                        # This does limit the alpha to be per-face but Blockland does not support per-vertex alpha anyway.
                        # The game can actually render per-vertex alpha but it doesn't seem to stick for longer than a second for whatever reason.
                        name = common.to_float_or_none(" ".join(tokens))

                        # Only log the vertex alpha message once per object: vertex color layers are per-object.
                        if vertex_color_alpha is None:
                            if name is None:
                                vertex_color_alpha = 1.0
                                logger.warning("IOBLBW010", "No alpha value set in vertex color layer name, using 1.0.", 2)
                            else:
                                vertex_color_alpha = name
                                logger.info("Vertex color layer alpha set to {}.".format(vertex_color_alpha), 2)

                        if addsub > 0:
                            # Negative alpha.
                            colors.append((loop_color.color.r, loop_color.color.g, loop_color.color.b, -vertex_color_alpha))
                        elif addsub < 0:
                            # Negative everything.
                            colors.append((-loop_color.color.r, -loop_color.color.g, -loop_color.color.b, -vertex_color_alpha))
                        else:
                            # Normal color.
                            colors.append((loop_color.color.r, loop_color.color.g, loop_color.color.b, vertex_color_alpha))

            # Sanity check.
            if not len(positions) is len(normals) is len(uvs) is 4:
                # EXCEPTION
                raise ValueError("Vertex positions ({}), normals ({}), or UV coordinates ({}) did not contain data for all 4 vertices.".format(
                    len(positions),
                    len(normals),
                    len(uvs)))

            if colors is not None:
                if len(colors) is not 4:
                    # EXCEPTION
                    raise ValueError("Quad color data only defined for {} vertices, 4 required.".format(len(colors)))

                # ROUND & CAST: Color values.
                colors = __to_decimal(colors)

            # ROUND & CAST: UV coordinates.
            uvs = __to_decimal(uvs)

            # A tuple cannot be used because the values are changed afterwards when the brick is rotated.
            quads[section.value].append([positions, normals, uvs, colors, brick_texture.name])

            if reset_section:
                section = None

        # Delete the mesh datablock that was created earlier.
        bpy.data.meshes.remove(mesh)

        if count_tris > 0:
            logger.warning("IOBLBW011", "{} triangles converted to quads.".format(count_tris), 2)

        if count_ngon > 0:
            logger.warning("IOBLBW012", "{} n-gons skipped.".format(count_ngon), 2)

    count_quads = sum([len(sec) for sec in quads])

    if count_quads < 1:
        # TODO: Test if an invisible brick works and remove this error.
        # RETURN ON ERROR
        return "IOBLBF005 No faces to export."
    else:
        logger.info("Brick quads: {}".format(count_quads), 1)

        return quads


def __format_blb_data(blb_data, forward_axis):
    """Formats the specified BLB data into the format required by the game and rotates the brick according to the specified forward axis.

    Args:
        blb_data (BLBData): A BLBData object containing the data to be written.
        forward_axis (Axis3D): A value of the Axis3D enum. The axis that will point forwards in-game.

    Returns:
        The formatted and rotated BLB data ready for writing.
    """
    # The exporter internally seems to work with +Y being forward because that makes the most sense to me.
    # The standard conversion from +Y forward (exporter) to +X forward (Blockland) is to swizzle X Y Z ("abc") to Y X Z ("bac").

    # Size

    # Swizzle the values according to the forward axis.
    if forward_axis is Axis3D.POS_Y or forward_axis is Axis3D.NEG_Y:
        blb_data.brick_size = common.swizzle(blb_data.brick_size, "bac")
    # Else: Do nothing.

    # Collision

    for index, (center, dimensions) in enumerate(blb_data.collision):
        # Swizzle and rotate the values according to the forward axis.
        # Collisions are defined by:
        #    - a center point coordinate in the coordinate space of the brick,
        #    - and the dimensions of the cuboid in plates.
        if forward_axis is Axis3D.POS_Y:
            # Still not entirely sure why I need to mirror the X coordinate here.
            blb_data.collision[index] = (common.swizzle(__mirror(center, forward_axis), "bac"), common.swizzle(dimensions, "bac"))
        elif forward_axis is Axis3D.NEG_Y:
            blb_data.collision[index] = (common.rotate(center, forward_axis), common.swizzle(dimensions, "bac"))
        elif forward_axis is Axis3D.POS_X:
            blb_data.collision[index] = (center, dimensions)
        else:
            blb_data.collision[index] = (common.rotate(center, forward_axis), dimensions)

    # Quads

    for section in blb_data.quads:
        for quad_data in section:
            # 0: positions
            # 1: normals
            # 2: uvs
            # 3: colors
            # 4: texture

            # Rotate the quads according to the defined forward axis to visually rotate the brick.
            for index, position in enumerate(quad_data[0]):
                quad_data[0][index] = common.rotate(position, forward_axis)

            # Normals also need to be rotated.
            for index, normal in enumerate(quad_data[1]):
                quad_data[1][index] = common.rotate(normal, forward_axis)

            # The texture name does not have to be all uppercase but it makes the output look more consistent.
            quad_data[4] = quad_data[4].upper()

    return blb_data


def process_blender_data(context, properties, objects):
    """Processes the specified Blender data into a format that can be written in a BLB file.

    Args:
        context (Blender context object): A Blender object containing scene data.
        properties (DerivateProperties): An object containing user properties.

    Returns:
        A BLBData object containing all the necessary information in the correct format for writing directly into a BLB file or an error message string to display to the user.
    """
    global __CALCULATION_FP_PRECISION_STR

    # Using a global variable for the sake of convenience and code readability.
    __CALCULATION_FP_PRECISION_STR = properties.precision

    if len(objects) > 0:
        logger.info("Processing definition objects.")

        # Process the definition objects (collision, brick grid, and bounds) first and separate the visible mesh_objects from the object sequence.
        # This is done in a single function because it is faster: no need to iterate over the same sequence twice.
        result = __process_definition_objects(properties, objects)

        if isinstance(result, str):
            # Something went wrong, return error message.
            return result
        else:
            blb_data = result[0]
            bounds_data = result[1]
            mesh_objects = result[2]

            # Calculate the coverage data based on the brick size.
            blb_data.coverage = __process_coverage(properties, blb_data)

            logger.info("Processing meshes.")

            # Processes the visible mesh data into the correct format for writing into a BLB file.
            quads = __process_mesh_data(context, properties, bounds_data, mesh_objects, properties.forward_axis)

            if isinstance(quads, str):
                # Something went wrong, we have an error message.
                return quads
            else:
                blb_data.quads = quads

            # Format and return the data for writing.
            return __format_blb_data(blb_data, properties.forward_axis)
    else:
        # RETURN ON ERROR
        return "IOBLBF006 No objects to export."
