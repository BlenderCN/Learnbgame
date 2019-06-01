# -*- coding: utf-8 -*-
"""LDR Importer GPLv2 license.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""


import os
import math
import mathutils
import traceback

import bpy

from bpy_extras.io_utils import ImportHelper

from .src.ldcolors import Colors
from .src.ldconsole import Console
from .src.ldmaterials import Materials
from .src.ldprefs import Preferences
from .src.extras import cleanup as Extra_Cleanup
from .src.extras import gaps as Extra_Part_Gaps
from .src.extras import linked_parts as Extra_Part_Linked

# Global variables
objects = []
paths = []


class LDrawFile(object):
    """Scans LDraw files."""

    # FIXME: rewrite - Rewrite entire class (#35)
    def __init__(self, context, filename, level, mat,
                 colour=None, orientation=None):

        self.level = level
        self.points = []
        self.faces = []
        self.material_index = []
        self.subparts = []
        self.submodels = []
        self.part_count = 0

        # Orientation matrix to handle orientation separately
        # (top-level part only)
        self.orientation = orientation
        self.mat = mat
        self.colour = colour
        self.parse(filename)

        # Deselect all objects before import.
        # This prevents them from receiving any cleanup (if applicable).
        bpy.ops.object.select_all(action='DESELECT')

        if len(self.points) > 0 and len(self.faces) > 0:
            mesh = bpy.data.meshes.new("LDrawMesh")
            mesh.from_pydata(self.points, [], self.faces)
            mesh.validate()
            mesh.update()

            for i, f in enumerate(mesh.polygons):
                n = self.material_index[i]

                # Get the material depending on the current render engine
                material = ldMaterials.make(n)

                if material is not None:
                    if mesh.materials.get(material.name) is None:
                        mesh.materials.append(material)

                    f.material_index = mesh.materials.find(material.name)

            # Naming of objects: filename of .dat-file, without extension
            self.ob = bpy.data.objects.new("LDrawObj", mesh)
            self.ob.name = os.path.basename(filename)[:-4]

            if LinkParts:  # noqa
                # Set top-level part orientation using Blender's 'matrix_world'
                self.ob.matrix_world = self.orientation.normalized()
            else:
                self.ob.location = (0, 0, 0)

            objects.append(self.ob)

            # Link object to scene
            bpy.context.scene.objects.link(self.ob)

        for i in self.subparts:
            self.submodels.append(LDrawFile(context, i[0], i[1], i[2],
                                            i[3], i[4]))

    def parse_line(self, line):
        """Harvest the information from each line."""
        verts = []
        color = line[1]

        if color == '16':
            color = self.colour

        num_points = int((len(line) - 2) / 3)
        for i in range(num_points):
                self.points.append(
                    (self.mat * mathutils.Vector((float(line[i * 3 + 2]),
                     float(line[i * 3 + 3]), float(line[i * 3 + 4])))).
                    to_tuple())
                verts.append(len(self.points) - 1)
        self.faces.append(verts)
        self.material_index.append(color)

    def parse_quad(self, line):
        """Properly construct quads in each brick."""
        color = line[1]
        verts = []
        num_points = 4
        v = []

        if color == '16':
            color = self.colour

        v.append(self.mat * mathutils.Vector((float(line[0 * 3 + 2]),
                 float(line[0 * 3 + 3]), float(line[0 * 3 + 4]))))
        v.append(self.mat * mathutils.Vector((float(line[1 * 3 + 2]),
                 float(line[1 * 3 + 3]), float(line[1 * 3 + 4]))))
        v.append(self.mat * mathutils.Vector((float(line[2 * 3 + 2]),
                 float(line[2 * 3 + 3]), float(line[2 * 3 + 4]))))
        v.append(self.mat * mathutils.Vector((float(line[3 * 3 + 2]),
                 float(line[3 * 3 + 3]), float(line[3 * 3 + 4]))))

        nA = (v[1] - v[0]).cross(v[2] - v[0])
        nB = (v[2] - v[1]).cross(v[3] - v[1])

        for i in range(num_points):
            verts.append(len(self.points) + i)

        if nA.dot(nB) < 0:
            self.points.extend([v[0].to_tuple(), v[1].to_tuple(),
                                v[3].to_tuple(), v[2].to_tuple()])
        else:
            self.points.extend([v[0].to_tuple(), v[1].to_tuple(),
                                v[2].to_tuple(), v[3].to_tuple()])

        self.faces.append(verts)
        self.material_index.append(color)

    def parse(self, filename):
        """Construct tri's in each brick."""
        # FIXME: rewrite - Rework function (#35)
        subfiles = []

        while True:
            # Get the path to the part
            filename = (filename if os.path.exists(filename)
                        else locatePart(filename))

            # The part does not exist
            # TODO Do not halt on this condition (#11)
            if filename is None:
                return False

            # Read the located part
            with open(filename, "rt", encoding="utf_8") as f:
                lines = f.readlines()

            # Some models may not have headers or enough lines
            # to support a header. Handle this case to avoid
            # hitting an IndexError trying to extract the header line.
            partTypeLine = ("" if len(lines) <= 3 else lines[3])

            # Check the part header for top-level part status
            is_top_part = is_top_level_part(partTypeLine)

            # Linked parts relies on the flawed is_top_part logic (#112)
            # TODO Correct linked parts to use proper logic
            # and remove this kludge
            if LinkParts:  # noqa
                is_top_part = filename == fileName  # noqa

            self.part_count += 1
            if self.part_count > 1 and self.level == 0:
                self.subparts.append([filename, self.level + 1, self.mat,
                                      self.colour, self.orientation])
            else:
                for retval in lines:
                    tmpdate = retval.strip()
                    if tmpdate != "":
                        tmpdate = tmpdate.split()

                        # Part content
                        if tmpdate[0] == "1":
                            new_file = tmpdate[14]
                            (
                                x, y, z, a, b, c,
                                d, e, f, g, h, i
                            ) = map(float, tmpdate[2:14])

                            # Reset orientation of top-level part,
                            # track original orientation
                            # TODO Use corrected isPart logic
                            if self.part_count == 1 and is_top_part and LinkParts:  # noqa
                                mat_new = self.mat * mathutils.Matrix((
                                    (1, 0, 0, 0),
                                    (0, 1, 0, 0),
                                    (0, 0, 1, 0),
                                    (0, 0, 0, 1)
                                ))
                                orientation = self.mat * mathutils.Matrix((
                                    (a, b, c, x),
                                    (d, e, f, y),
                                    (g, h, i, z),
                                    (0, 0, 0, 1)
                                )) * mathutils.Matrix.Rotation(
                                    math.radians(90), 4, 'X')
                            else:
                                mat_new = self.mat * mathutils.Matrix((
                                    (a, b, c, x),
                                    (d, e, f, y),
                                    (g, h, i, z),
                                    (0, 0, 0, 1)
                                ))
                                orientation = None
                            color = tmpdate[1]
                            if color == '16':
                                color = self.colour
                            subfiles.append([new_file, mat_new, color])

                            # When top-level part, save orientation separately
                            # TODO Use corrected is_top_part logic
                            if self.part_count == 1 and is_top_part:
                                subfiles.append(['orientation',
                                                 orientation, ''])

                        # Triangle (tri)
                        if tmpdate[0] == "3":
                            self.parse_line(tmpdate)

                        # Quadrilateral (quad)
                        if tmpdate[0] == "4":
                            self.parse_quad(tmpdate)

            if len(subfiles) > 0:
                subfile = subfiles.pop()
                filename = subfile[0]
                # When top-level brick orientation information found,
                # save it in self.orientation
                if filename == 'orientation':
                    self.orientation = subfile[1]
                    subfile = subfiles.pop()
                    filename = subfile[0]
                self.mat = subfile[1]
                self.colour = subfile[2]
            else:
                break


def is_top_level_part(header_line):
    """Check if the given part is a top level part.

    @param {String} headerLine The header line stating the part level.
    @return {Boolean} True if a top level part, False otherwise
                      or the header does not specify.
    """
    # Make sure the file has the spec'd META command
    # If it does not, we cannot do easily determine the part type,
    # so we will simply say it is not top level
    header_line = header_line.lower().strip()
    if header_line == "":
        return False

    header_line = header_line.split()
    if header_line[0] != "0 !ldraw_org":
        return False

    # We can determine if this is top level or not
    return header_line[2] in ("part", "unofficial_part")


def locatePart(partName):
    """Find the given part in the defined search paths.

    @param {String} partName The part to find.
    @return {!String} The absolute path to the part if found.
    """
    # Use the OS's path separator to ensure the parts are found
    partName = partName.replace("\\", os.path.sep)

    for path in paths:
        # Find the part filename using the exact case in the file
        fname = os.path.join(path, partName)
        if os.path.exists(fname):
            return fname

        # Because case-sensitive file systems, if the first check fails
        # check again using a normalized part filename
        # See #112#issuecomment-136719763
        else:
            fname = os.path.join(path, partName.lower())
            if os.path.exists(fname):
                return fname

    Console.log("Could not find part {0}".format(fname))
    return None


def create_model(self, context, scale):
    """Create the actual model."""
    # FIXME: rewrite - Rewrite entire function (#35)
    global objects
    global ldColors
    global ldMaterials
    global fileName

    fileName = self.filepath
    # Attempt to get the directory the file came from
    # and add it to the `paths` list
    paths[0] = os.path.dirname(fileName)
    Console.log("Attempting to import {0}".format(fileName))

    # The file format as hinted to by
    # conventional file extensions is not supported.
    # Recommended: http://ghost.kirk.by/file-extensions-are-only-hints
    if fileName[-4:].lower() not in (".ldr", ".dat"):

        Console.log('''ERROR: Reason: Invalid File Type
Must be a .ldr or .dat''')
        self.report({'ERROR'}, '''Error: Invalid File Type
Must be a .ldr or .dat''')
        return {'ERROR'}

    # It has the proper file extension, continue with the import
    try:
        # Rotate and scale the parts
        # Scale factor is divided by 25 so we can use whole number
        # scale factors in the UI. For reference,
        # the default scale 1 = 0.04 to Blender
        trix = mathutils.Matrix((
            (1.0,  0.0, 0.0, 0.0),  # noqa
            (0.0,  0.0, 1.0, 0.0),  # noqa
            (0.0, -1.0, 0.0, 0.0),
            (0.0,  0.0, 0.0, 1.0)  # noqa
        )) * (scale / 25)

        # If LDrawDir does not exist, stop the import
        if not os.path.isdir(LDrawDir):  # noqa
            Console.log(''''ERROR: Cannot find LDraw installation at
{0}'''.format(LDrawDir))  # noqa
            self.report({'ERROR'}, '''Cannot find LDraw installation at
{0}'''.format(LDrawDir))  # noqa
            return {'CANCELLED'}

        # Instance the colors module and
        # load the LDraw-defined color definitions
        ldColors = Colors(LDrawDir, AltColorsOpt)  # noqa
        ldColors.load()
        ldMaterials = Materials(ldColors, context.scene.render.engine)

        LDrawFile(context, fileName, 0, trix)

        for cur_obj in objects:
            # The CleanUp import option was selected
            if CleanUpOpt:  # noqa
                Extra_Cleanup.main(cur_obj, LinkParts)  # noqa

            if GapsOpt:  # noqa
                Extra_Part_Gaps.main(cur_obj, scale)

        # The link identical parts import option was selected
        if LinkParts:  # noqa
            Extra_Part_Linked.main(objects)

        # Select all the mesh now that import is complete
        for cur_obj in objects:
            cur_obj.select = True

        # Update the scene with the changes
        context.scene.update()
        objects = []

        # Always reset 3D cursor to <0,0,0> after import
        bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)

        # Display success message
        Console.log("{0} successfully imported!".format(fileName))
        return {'FINISHED'}

    except Exception as e:
        Console.log("ERROR: {0}\n{1}\n".format(
            type(e).__name__, traceback.format_exc()))

        Console.log("ERROR: Reason: {0}.".format(
            type(e).__name__))

        self.report({'ERROR'}, '''File not imported ("{0}").
Check the console logs for more information.'''.format(type(e).__name__))
        return {'CANCELLED'}


# ------------ Operator ------------ #


class LDRImporterOps(bpy.types.Operator, ImportHelper):
    """LDR Importer Import Operator."""

    bl_idname = "import_scene.ldraw"
    bl_description = "Import an LDraw model (.ldr/.dat)"
    bl_label = "Import LDraw Model"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    # Instance the preferences system
    prefs = Preferences()

    # File type filter in file browser
    filename_ext = ".ldr"
    filter_glob = bpy.props.StringProperty(
        default="*.ldr;*.dat",
        options={'HIDDEN'}
    )

    ldrawPath = bpy.props.StringProperty(
        name="",
        description="Path to the LDraw Parts Library",
        default=prefs.getLDraw()
    )

    importScale = bpy.props.FloatProperty(
        name="Scale",
        description="Use a specific scale for each part",
        default=prefs.get("importScale", 1.00)
    )

    resPrims = bpy.props.EnumProperty(
        name="Resolution of part primitives",
        description="Resolution of part primitives",
        default=prefs.get("resPrims", "StandardRes"),
        items=(
            ("HighRes", "High-Res Primitives",
             "Import using high resolution primitives. "
             "NOTE: This feature may create mesh errors"),
            ("StandardRes", "Standard Primitives",
             "Import using standard resolution primitives"),
            ("LowRes", "Low-Res Primitives",
             "Import using low resolution primitives. "
             "NOTE: This feature may create mesh errors")
        )
    )

    cleanUpParts = bpy.props.BoolProperty(
        name="Model Cleanup",
        description="Perform some basic model cleanup",
        default=prefs.get("cleanUpParts", True)
    )

    altColors = bpy.props.BoolProperty(
        name="Use Alternate Colors",
        description="Use LDCfgalt.ldr for color definitions",
        default=prefs.get("altColors", False)
    )

    addGaps = bpy.props.BoolProperty(
        name="Spaces Between Parts",
        description="Add small spaces between each part",
        default=prefs.get("addGaps", False)
    )

    lsynthParts = bpy.props.BoolProperty(
        name="Use LSynth Parts",
        description="Use LSynth parts during import",
        default=prefs.get("lsynthParts", False)
    )

    linkParts = bpy.props.BoolProperty(
        name="Link Identical Parts",
        description="Link identical parts by type and color (experimental)",
        default=prefs.get("linkParts", False)
    )

    def draw(self, context):
        """Display import options."""
        layout = self.layout
        box = layout.box()
        box.label("Import Options", icon="SCRIPTWIN")
        box.label("LDraw Parts Library", icon="FILESEL")
        box.prop(self, "ldrawPath")
        box.prop(self, "importScale")
        box.label("Primitives", icon="MOD_BUILD")
        box.prop(self, "resPrims", expand=True)
        box.label("Additional Options", icon="PREFERENCES")
        box.prop(self, "linkParts")
        box.prop(self, "cleanUpParts", expand=True)
        box.prop(self, "addGaps")
        box.prop(self, "altColors")
        box.prop(self, "lsynthParts")

    def execute(self, context):
        """Set import options and start the import process."""
        global LDrawDir, CleanUpOpt, AltColorsOpt, GapsOpt, LinkParts
        LDrawDir = str(self.ldrawPath)
        CleanUpOpt = bool(self.cleanUpParts)
        AltColorsOpt = bool(self.altColors)
        GapsOpt = bool(self.addGaps)
        LinkParts = bool(self.linkParts)

        # Clear array before adding data if it contains data already
        # Not doing so duplicates the indexes
        if paths:
            del paths[:]

        # Create placeholder for index 0.
        # It will be filled with the location of the model later.
        paths.append("")

        # Always search for parts in the `models` folder
        paths.append(os.path.join(self.ldrawPath, "models"))

        # The unofficial folder exists, search the standard folders
        if os.path.exists(os.path.join(self.ldrawPath, "unofficial")):
            paths.append(os.path.join(self.ldrawPath, "unofficial", "parts"))

            # The user wants to use high-res unofficial primitives
            if self.resPrims == "HighRes":
                paths.append(os.path.join(self.ldrawPath,
                                          "unofficial", "p", "48"))
            # The user wants to use low-res unofficial primitives
            elif self.resPrims == "LowRes":
                paths.append(os.path.join(self.ldrawPath,
                                          "unofficial", "p", "8"))

            # Search in the `unofficial/p` folder
            paths.append(os.path.join(self.ldrawPath, "unofficial", "p"))

            # The user wants to use LSynth parts
            if self.lsynthParts:
                if os.path.exists(os.path.join(self.ldrawPath, "unofficial",
                                               "lsynth")):
                    paths.append(os.path.join(self.ldrawPath, "unofficial",
                                              "lsynth"))
                    Console.log("Use LSynth Parts selected")

        # Always search for parts in the `parts` folder
        paths.append(os.path.join(self.ldrawPath, "parts"))

        # The user wants to use high-res primitives
        if self.resPrims == "HighRes":
            paths.append(os.path.join(self.ldrawPath, "p", "48"))
            Console.log("High-res primitives substitution selected")

        # The user wants to use low-res primitives
        elif self.resPrims == "LowRes":
            paths.append(os.path.join(self.ldrawPath, "p", "8"))
            Console.log("Low-res primitives substitution selected")

        # The user wants to use normal-res primitives
        else:
            Console.log("Standard-res primitives substitution selected")

        # Finally, search in the `p` folder
        paths.append(os.path.join(self.ldrawPath, "p"))

        # Create the preferences dictionary
        importOpts = {
            "addGaps": self.addGaps,
            "altColors": self.altColors,
            "cleanUpParts": self.cleanUpParts,
            "importScale": self.importScale,
            "linkParts": self.linkParts,
            "lsynthParts": self.lsynthParts,
            "resPrims": self.resPrims
        }

        # Save the preferences and import the model
        self.prefs.setLDraw(self.ldrawPath)
        self.prefs.save(importOpts)
        create_model(self, context, self.importScale)
        return {'FINISHED'}
