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
A module for writing data into a BLB file.

@author: Demian Wright
"""

# Blender requires imports from ".".
from . import const


def __get_sequence_string(sequence, pretty_print, decimal_digits=const.MAX_FP_DECIMALS_TO_WRITE, new_line=True):
    """Writes the values of the specified sequence separated with spaces into the specified file.
    An optional new line character is added at the end of the line by default.

    Args:
        sequence (sequence): A sequence of data to be written.
        decimal_digits (int): The number of decimal digits to write if the sequence contains floating point values or None to ignore. (Default: const.MAX_FP_DECIMALS_TO_WRITE)
                              The default value prevents very small values from being written in scientific notation, which the game does not understand.
        new_line (bool): Add a newline character at the end of the line? (Default: True)
    """
    parts = []

    for index, value in enumerate(sequence):
        if index != 0:
            # Add a space before each value except the first one.
            parts.append(" ")

        # Format the value into string.
        if pretty_print and decimal_digits != 0:
            # Remove all zeros from the end (if any), then remove all periods from the end (if any).
            parts.append("{0:.{1}f}".format(value, decimal_digits).rstrip("0").rstrip("."))
        else:
            parts.append("{0:.{1}f}".format(value, decimal_digits))
    if new_line:
        # Add a new line after all values.
        parts.append("\n")

    return "".join(parts)


def write_file(properties, filepath, blb_data):
    """Writes the BLB file.

    Args:
        properties (DerivateProperties): An object containing user properties.
        filepath (string): Path to the BLB file to be written.
        blb_data (BLBData): A BLBData object containing the data to be written.
    """
    lines = []

    # ----------
    # Brick Size
    # ----------
    lines.append(__get_sequence_string(blb_data.brick_size, False, 0))

    # ----------
    # Brick Type
    # ----------
    lines.append("{}\n\n".format(const.BLB_BRICK_TYPE_SPECIAL))

    # ----------
    # Brick Grid
    # ----------
    for axis_slice in blb_data.brick_grid:
        for row in axis_slice:
            # Join each Y-axis of data without a separator.
            lines.append("".join(row) + "\n")

        # A new line after each axis slice.
        lines.append("\n")

    # ---------
    # Collision
    # ---------
    if len(blb_data.collision) < 1:
        # No collision.
        lines.append("0\n")
    else:
        # Write the number of collision cuboids.
        lines.append("{}\n".format(str(len(blb_data.collision))))

        # Write the defined collision cuboids.
        for (center, dimensions) in blb_data.collision:
            lines.append("\n")
            lines.append(__get_sequence_string(center, properties.blendprop.pretty_print, properties.decimal_digits))
            lines.append(__get_sequence_string(dimensions, properties.blendprop.pretty_print, properties.decimal_digits))

    # --------
    # Coverage
    # --------
    # Only skip writing coverage if terse mode is True and coverage is False.
    if not (properties.blendprop.terse_mode and not properties.blendprop.calculate_coverage):
        lines.append("{}\n".format(const.BLB_HEADER_COVERAGE))
        for (hide_adjacent, plate_count) in blb_data.coverage:
            lines.append("{} : {}\n".format(str(int(hide_adjacent)), str(plate_count)))

    # -----
    # Quads
    # -----
    for section_name, section in const.BLBQuadSection.__members__.items():
        # Write section name.
        lines.append("{}\n".format("" if properties.blendprop.terse_mode else const.BLB_SECTION_SEPARATOR.format(section_name)))

        # Write section length.
        lines.append("{}\n".format(str(len(blb_data.quads[section.value]))))

        for (positions, normals, uvs, colors, texture_name) in blb_data.quads[section.value]:
            # Face texture name.
            lines.append("\n{}{}\n".format(const.BLB_PREFIX_TEXTURE, texture_name))

            # Vertex positions.
            lines.append("{}\n".format("" if properties.blendprop.terse_mode else const.BLB_HEADER_POSITION))

            for position in positions:
                lines.append(__get_sequence_string(position, properties.blendprop.pretty_print, properties.decimal_digits))

            # Face UV coordinates.
            lines.append("{}\n".format("" if properties.blendprop.terse_mode else const.BLB_HEADER_UV))
            for uv_pair in uvs:
                lines.append(__get_sequence_string(uv_pair, properties.blendprop.pretty_print, properties.decimal_digits))

            # Vertex colors, if any.
            if colors is not None:
                lines.append("{}\n".format("" if properties.blendprop.terse_mode else const.BLB_HEADER_COLORS))
                for color in colors:
                    lines.append(__get_sequence_string(color, properties.blendprop.pretty_print, properties.decimal_digits))

            # Vertex normals.
            lines.append("{}\n".format("" if properties.blendprop.terse_mode else const.BLB_HEADER_NORMALS))
            for normal in normals:
                lines.append(__get_sequence_string(normal, properties.blendprop.pretty_print, properties.decimal_digits))

    with open(filepath, "w") as file:
        for line in lines:
            file.write(line)
