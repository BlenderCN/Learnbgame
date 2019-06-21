# -*- coding: utf-8 -*-
"""LDR Importer GPLv2 license.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""


import os
import re
import struct

from .ldconsole import Console


class Colors:
    """Parse and manage LDraw color definitions."""

    def __init__(self, ldPath, useAltColors):
        """Instance the class.

        @param {String} ldPath An absolute path to the LDraw library.
        @param {Boolean} useAltColors True if alternative color definitions
                                      should be used, False for
                                      standard color definitions.
        """
        self.__ldPath = ldPath
        self.__colorFile = ("LDCfgalt.ldr" if useAltColors else "LDConfig.ldr")
        self.__colors = {
            "filename": self.__colorFile
        }

    def hexToRgb(self, color):
        """Convert a Hex color value to the RGB format Blender requires.

        @param {String} color - The hex color value to convert.
                                Can be prefixed with "#".
        @return {!Tuple.<number>} A three-index tuple containing
                                  the converted RGB value.
                                  Otherwise None if the color
                                  could not be converted.
        """
        color = color.lstrip("#")
        rgbColor = struct.unpack("BBB", bytes.fromhex(color))
        return tuple([val / 255 for val in rgbColor])

    def __hasColorValue(self, line, value):
        """Check if the color tag has a specific attribute.

        @param {List} line - The color line to search.
        @param {String} value - The attribute to find.
        @return {Boolean} True if attribute is present, False otherwise.
        """
        return value in line

    def __getColorValue(self, line, value):
        """Get a specific attribute for a given color tag.

        @param {List} line - The color line to search.
        @param {String} value - The value to find.
        @return {!String} The color value is present, None otherwise.
        """
        if value in line:
            return line[line.index(value) + 1]
        return None

    def __set(self, code, color):
        """Store an LDraw color.

        @param {String} code - The code identifying the color.
        @param {*} color - The structure describing the color.
        """
        self.__colors[code] = color

    def makeDirectColor(self, color):
        """Convert a direct color to RGB values.

        @link {http://www.ldraw.org/article/218.html#colours}
        @param {String} color - An LDraw direct color in the format 0x2RRGGBB.
        @return {Dictionary} "valid" key is a boolean value indicating
                             if a direct color was found or not.
                             "value" key is the color converted into
                             a three-index RGB color tuple or None if
                             "valid" if False.
        """
        results = {
            "valid": False,
            "value": None
        }

        # There is no color data
        if color is None:
            return results

        # This is not a direct color
        if re.fullmatch(r"^0x2(?:[A-F0-9]{2}){3}$", color) is None:
            return results

        # This is a valid direct color
        results["valid"] = True
        results["value"] = self.hexToRgb(color[3:])
        return results

    def get(self, code):
        """Get an individual LDraw color object.

        @param {String} code - The code identifying the color.
        @return {!Dictionary} The color definition if available,
                              None otherwise.
        """
        return self.__colors.get(code)

    def contains(self, code):
        """Check if a color exists in the color dictionary.

        @param {String} code - The code for the corresponding color.
        @return {Boolean} True if the color was found, False otherwise.
        """
        return code in self.__colors.keys()

    def load(self):
        """Parse the LDraw color definitions file.

        @return {Dictionary} The complete LDraw color dictionary
                             with color codes as the keys.
        """
        # Read the color definition file
        Console.log("Parsing {0} color definitions".format(self.__colorFile))
        with open(os.path.join(self.__ldPath, self.__colorFile),
                  "rt", encoding="utf_8") as f:
            lines = f.readlines()

        for line in lines:
            # Normalize the lines
            line = line.lstrip("0").strip().lower()

            # Make sure this is a color
            if line.startswith("!colour"):
                line = line.split()
                code = line[3]

                # Create the color
                color = {
                    "alpha": 1.0,
                    "code": code,
                    "edge": self.hexToRgb(self.__getColorValue(line, "edge")),
                    "luminance": 0.0,
                    "material": "basic",
                    "name": self.__getColorValue(line, "!colour"),
                    "value": self.hexToRgb(self.__getColorValue(line, "value"))
                }

                # Extract the alpha value
                if self.__hasColorValue(line, "alpha"):
                    color["alpha"] = int(
                        self.__getColorValue(line, "alpha")) / 256

                # Extract the luminance value
                if self.__hasColorValue(line, "luminance"):
                    color["luminance"] = int(
                        self.__getColorValue(line, "luminance"))

                # Extract the valueless attributes
                if self.__hasColorValue(line, "chrome"):
                    color["material"] = "chrome"
                if self.__hasColorValue(line, "pearlescent"):
                    color["material"] = "pearlescent"
                if self.__hasColorValue(line, "rubber"):
                    color["material"] = "rubber"
                if self.__hasColorValue(line, "metal"):
                    color["material"] = "metal"

                # Extract extra material values if present
                if self.__hasColorValue(line, "material"):
                    subLine = line[line.index("material"):]
                    color["material"] = self.__getColorValue(subLine,
                                                             "material")
                    color["secondary_color"] = self.__getColorValue(
                        subLine, "value")[1:]
                    color["fraction"] = self.__getColorValue(subLine,
                                                             "fraction")
                    color["vfraction"] = self.__getColorValue(subLine,
                                                              "vfraction")
                    color["size"] = self.__getColorValue(subLine, "size")
                    color["minsize"] = self.__getColorValue(subLine, "minsize")
                    color["maxsize"] = self.__getColorValue(subLine, "maxsize")

                self.__set(code, color)
