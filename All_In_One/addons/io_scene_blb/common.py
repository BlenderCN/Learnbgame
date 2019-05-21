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
Various functions and collections used in multiple classes.

@author: Demian Wright
"""
from math import isnan
from string import ascii_lowercase
from . import const


def swizzle(sequence, order):
    """Changes the order of the elements in the specified sequence. (Maximum of 26 elements.)

    Args:
        sequence (sequence): A sequence of objects.
        order (sequence or string): The new order of the sequence as string or a sequence of lowercase Latin letters.
                                    Sequence indices are represented using lowercase letters a-z of the Latin alphabet.
                                    I.e. "a" signifies the index 0 and "z" stands for index 25.
                                    Duplicating elements is possible by specifying the the same letter multiple times.
    Returns:
        A new list of objects shallowly copied from the specified sequence in the specified order.
        The new sequence will only contain the elements specified in the order, elements not specified in the new order are discarded.
    """
    # For every letter in the specified order.
    # Get the index of the letter in the ascii_lowercase string.
    # Get the value of that index in the specified sequence.
    # Add it to a new list.
    # Return the new list.
    return [sequence[ascii_lowercase.index(letter)] for letter in order]


def swizzle_by_index(sequence, order):
    """Changes the order of the elements in the specified sequence.

    Args:
        sequence (sequence): A sequence of objects.
        order (sequence of integers): The new order of the specified sequence as sequence of indices.
                                      Duplicating elements is possible by specifying the the same index multiple times.
    Returns:
        A new list of objects shallowly copied from the specified sequence in the specified order.
        The new sequence will only contain the elements specified in the order, elements not specified in the new order are discarded.
    """
    return [sequence[idx] for idx in order]


def offset_sequence(sequence, offset):
    """Moves every element in the sequence by the specified offset, looping the elements around when they are pushed off either end of the sequence.

    Args:
        sequence (sequence): A sequence of objects.
        offset (integer): The number of slots to move each element forwards (positive) or backwards (negative).

    Returns:
        A new list of objects shallowly copied from the specified sequence with each element's position offset by the specified amount.
    """
    length = len(sequence)

    return [sequence[(i - offset) % length] for i in range(0, length)]


def rotate(xyz, forward_axis):
    """Rotates the specified XYZ coordinate sequence according to the specified forward axis so the coordinates will be correctly represented in the game.
    By default Blockland assumes that coordinates are relative to +X axis being the brick forward axis pointing away from the player.

    Args:
        xyz (sequence of numbers): A sequence of XYZ coordinates. Only the first 3 values are taken into account even if more are specified.
        forward_axis (Axis3D): A value of the Axis3D enum. The axis that will point forwards in-game.

    Returns:
        A new list of XYZ coordinates.
    """
    rotated = []

    if forward_axis is const.Axis3D.POS_X:
        # Rotate: 0 degrees clockwise
        return xyz

    elif forward_axis is const.Axis3D.POS_Y:
        # Rotate: 90 degrees clockwise = X Y Z -> Y -X Z
        rotated.append(xyz[const.Y])
        rotated.append(-xyz[const.X])

    elif forward_axis is const.Axis3D.NEG_X:
        # Rotate: 180 degrees clockwise = X Y Z -> -X -Y Z
        rotated.append(-xyz[const.X])
        rotated.append(-xyz[const.Y])

    elif forward_axis is const.Axis3D.NEG_Y:
        # Rotate: 270 degrees clockwise = X Y Z -> -Y X Z
        rotated.append(-xyz[const.Y])
        rotated.append(xyz[const.X])

    # The Z axis is not yet taken into account.
    rotated.append(xyz[const.Z])

    return rotated


def to_float_or_none(value):
    """Converts the specified value to a float if it is numerical, or None if it is not.

    Args:
        value (object): Object to be converted to a float.

    Returns:
        A float representing the object or None if the object was not numerical.
    """
    try:
        num = float(value)

        if isnan(num):
            return None
        return num
    except ValueError:
        return None
