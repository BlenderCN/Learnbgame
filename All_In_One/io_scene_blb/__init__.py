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
Handles registering the add-on into Blender and drawing properties to the UI.

@author: Demian Wright
"""

import bpy
import os
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty, FloatProperty
from bpy_extras.io_utils import ExportHelper

# Blender requires imports from "." for self-defined modules.
from . import export_blb, const, logger

bl_info = {
    "name": "Export: Blockland Brick (.blb)",
    "author": "Demian Wright & Nick Smith",
    "version": (2, 0, 0),
    "blender": (2, 67, 0),
    "location": "File > Export > Blockland Brick (.blb)",
    "description": "Export Blockland brick format",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

# TODO: Exporting DTS collision.
# TODO: Importing BLB files.
# TODO: Render brick preview.
# TODO: Check that all docstrings and comments are still up to date.
# TODO: Quad sorting is per object but BLBs support per-quad sorting: the exporter does not support quad sorting for smoothed objects.
# TODO: Serialize props to the start of the log?
# TODO: Add a section about brick grid to the readme.
# TODO: Make the capitalization consistent in the readme.
# TODO: Clarify brick grid and brick grid placement rules.


class ExportBLB(bpy.types.Operator, ExportHelper):
    """Export Blockland brick data."""
    bl_idname = "export_scene.blb"
    bl_label = "Export BLB"
    bl_options = {"REGISTER", "PRESET"}

    filename_ext = const.BLB_EXT
    logfile_ext = const.LOG_EXT
    filter_glob = StringProperty(default="*" + const.BLB_EXT, options={"HIDDEN"})

    # ==========
    # Properties
    # ==========

    # ==================
    # Blender Properties
    # ==================

    # ------------
    # Export Count
    # ------------
    export_count = EnumProperty(
        items=[("SINGLE", "Single", "Export a single brick"),
               ("MULTIPLE", "Multiple", "Export multiple bricks at once")],
        name="Bricks to Export",
        description="How many bricks to export from this file",
        default="SINGLE"
    )

    # ----------------
    # Brick Definition
    # ----------------
    brick_definition = EnumProperty(
        items=[("GROUPS", "Groups", "Bricks are in different groups"),
               ("LAYERS", "Layers", "Bricks are in different layers")],
        name="Bricks Defined by",
        description="The method for defining multiple bricks in a file",
        default="GROUPS"
    )

    # ----------
    # Brick Name
    # ----------
    brick_name_source = EnumProperty(
        items=[("BOUNDS", "Bounds", "Brick name is in the name of the bounds object, after the bounds definition, separated with a space (directory set in export file dialog)"),
               ("FILE", "File", "Brick name is the same as the .blend file name (can be changed manually in the file dialog)")],
        name="Brick Name from:",
        description="Where to get the name of the exported brick",
        default="BOUNDS"
    )

    # -------------------
    # Brick Name Multiple
    # -------------------
    brick_name_source_multi = EnumProperty(
        items=[("BOUNDS", "Bounds", "Brick name is in the name of the bounds object, after the bounds definition, separated with a space (directory set in export file dialog)"),
               ("GROUPS", "Groups", "Brick name is the group name (directory set in export file dialog)")],
        name="Brick Names from:",
        description="Where to get the name of the exported bricks",
        default="BOUNDS"
    )

    # -------
    # Objects
    # -------
    export_objects = EnumProperty(
        items=[("SELECTION", "Selection", "Export only selected objects"),
               ("LAYERS", "Layers", "Export all objects in the visible layers"),
               ("SCENE", "Scene", "Export all objects in the active scene")],
        name="Export Objects In:",
        description="Only export the specified objects",
        default="SELECTION"
    )

    # -------------
    # Objects Multi
    # -------------
    export_objects_multi = EnumProperty(
        items=[("LAYERS", "Layers", "Export all bricks in the visible layers"),
               ("SCENE", "Scene", "Export all bricks in the active scene")],
        name="Export Bricks in:",
        description="Only export the specified bricks",
        default="LAYERS"
    )

    # ------------
    # Forward Axis
    # ------------
    # For whatever reason BLB coordinates are rotated 90 degrees counter-clockwise to Blender coordinates.
    # I.e. -X is facing you when the brick is planted and +X is the brick north instead of +Y which makes more sense to me.
    # TODO: Support Z axis remapping.
    axis_blb_forward = EnumProperty(
        items=[("POSITIVE_X", "+X", "The positive X axis"),
               ("POSITIVE_Y", "+Y", "The positive Y axis"),
               ("NEGATIVE_X", "-X", "The negative X axis"),
               ("NEGATIVE_Y", "-Y", "The negative Y axis")],
        name="Brick Forward Axis",
        description="Set the Blender axis that will point forwards in the game",
        default="POSITIVE_Y"
    )

    # -----
    # Scale
    # -----
    export_scale = FloatProperty(
        name="Scale",
        description="The scale to export the brick at. A 1x1x1 brick at 100% scale is defined as being 1.0x1.0x1.2 Blender units in size on the XYZ axes.",
        subtype="PERCENTAGE",
        precision=3,
        step=1,
        default=100.0,
        min=0.001,
        soft_max=400.0,
    )

    # -------------
    # Use Modifiers
    # -------------
    use_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Take modifiers into account (at preview settings) when exporting objects, does not apply the modifiers in the interface",
        default=True,
    )

    # -----------
    # Definitions
    # -----------
    custom_definitions = BoolProperty(
        name="Custom Definition Tokens",
        description="Set custom definitions tokens (case insensitive) to use in definition object names",
        default=False,
    )

    deftoken_bounds = StringProperty(
        name="Brick Bounds",
        description="Token for objects that define brick bounds",
        default="bounds",
    )

    deftoken_collision = StringProperty(
        name="Collision Cuboid",
        description="Token for objects that define collision cuboids",
        default="collision",
    )

    # Sections

    deftoken_quad_sort_top = StringProperty(
        name="Top Quads",
        description="Token for specifying that the object's vertices belong to the top section of the brick (used in brick coverage for hiding faces to improve performance)",
        default="qt",
    )

    deftoken_quad_sort_bottom = StringProperty(
        name="Bottom Quads",
        description="Token for specifying that the object's vertices belong to the bottom section of the brick (used in brick coverage for hiding faces to improve performance)",
        default="qb",
    )

    deftoken_quad_sort_north = StringProperty(
        name="North Quads",
        description="Token for specifying that the object's vertices belong to the north section of the brick (used in brick coverage for hiding faces to improve performance)",
        default="qn",
    )

    deftoken_quad_sort_east = StringProperty(
        name="East Quads",
        description="Token for specifying that the object's vertices belong to the east section of the brick (used in brick coverage for hiding faces to improve performance)",
        default="qe",
    )

    deftoken_quad_sort_south = StringProperty(
        name="South Quads",
        description="Token for specifying that the object's vertices belong to the south section of the brick (used in brick coverage for hiding faces to improve performance)",
        default="qs",
    )

    deftoken_quad_sort_west = StringProperty(
        name="West Quads",
        description="Token for specifying that the object's vertices belong to the west section of the brick (used in brick coverage for hiding faces to improve performance)",
        default="qw",
    )

    deftoken_quad_sort_omni = StringProperty(
        name="Omni Quads",
        description="Token for specifying that the object's vertices belong to the omni section of the brick, these vertices will never be hidden",
        default="qo",
    )

    # Brick Grid

    deftoken_gridx = StringProperty(
        name="Brick Grid x",
        description="Token for objects that define a volume within the brick bounds that will be filled with the 'x' symbol in the brick grid signifying that other bricks cannot be placed there",
        default="gridx",
    )

    deftoken_griddash = StringProperty(
        name="Brick Grid -",
        description="Token for objects that define a volume within the brick bounds that will be filled with the '-' symbol in the brick grid signifying empty space",
        default="grid-",
    )

    deftoken_gridu = StringProperty(
        name="Brick Grid u",
        description="Token for objects that define a volume within the brick bounds that will be filled with the 'u' symbol in the brick grid signifying that other bricks may be planted above",
        default="gridu",
    )

    deftoken_gridd = StringProperty(
        name="Brick Grid d",
        description="Token for objects that define a volume within the brick bounds that will be filled with the 'd' symbol in the brick grid signifying that other bricks may be planted below",
        default="gridd",
    )

    deftoken_gridb = StringProperty(
        name="Brick Grid b",
        description="Token for objects that define a volume within the brick bounds that will be filled with the 'b' symbol in the brick grid signifying that other bricks may be planted above or below",
        default="gridb",
    )

    deftoken_gridx_priority = IntProperty(
        name="Grid X Symbol Priority",
        description="Priority of the 'x' symbol definition, higher priority definition override any overlapping definitions with lower priority (two or more symbols must not have the same priority)",
        default=0,
        min=0,
        max=4,
    )

    deftoken_griddash_priority = IntProperty(
        name="Grid - Symbol Priority",
        description="Priority of the '-' symbol definition, higher priority definition override any overlapping definitions with lower priority (two or more symbols must not have the same priority)",
        default=1,
        min=0,
        max=4,
    )

    deftoken_gridu_priority = IntProperty(
        name="Grid U Symbol Priority",
        description="Priority of the 'u' symbol definition, higher priority definition override any overlapping definitions with lower priority (two or more symbols must not have the same priority)",
        default=2,
        min=0,
        max=4,
    )

    deftoken_gridd_priority = IntProperty(
        name="Grid D Symbol Priority",
        description="Priority of the 'd' symbol definition, higher priority definition override any overlapping definitions with lower priority (two or more symbols must not have the same priority)",
        default=3,
        min=0,
        max=4,
    )

    deftoken_gridb_priority = IntProperty(
        name="Grid B Symbol Priority",
        description="Priority of the 'b' symbol definition, higher priority definition override any overlapping definitions with lower priority (two or more symbols must not have the same priority)",
        default=4,
        min=0,
        max=4,
    )

    # Colors

    deftoken_color = StringProperty(
        name="Object Color",
        description="Token for specifying a color for an object using its name. Token must be followed by 4 values (red green blue alpha) separated with spaces using a comma (,) as decimal separator. Integers 0-255 also supported.",
        default="c",
    )

    deftoken_color_blank = StringProperty(
        name="In-Game Color",
        description="No color is written for these faces: in-game spray color is used",
        default="blank",
    )

    deftoken_color_add = StringProperty(
        name="Additive Color",
        description="Blender material/vertex color is added to in-game spray color",
        default="cadd",
    )

    deftoken_color_sub = StringProperty(
        name="Subtractive Color",
        description="Blender material/vertex color is subtracted from in-game spray color",
        default="csub",
    )

    # ==============
    # BLB Properties
    # ==============

    # ---------
    # Collision
    # ---------
    custom_collision = BoolProperty(
        name="Custom Collision",
        description="Use custom collision definition objects (if any)",
        default=True,
    )

    fallback_collision = EnumProperty(
        items=[("BOUNDS", "Bounds", "Use brick bounds as collision"),
               ("AABB", "AABB", "Calculate axis-aligned bounding box collision from visible objects")],
        name="Fallback Collision",
        description="Collision type to use if no custom definitions exist",
        default="BOUNDS"
    )

    # --------
    # Coverage
    # --------
    calculate_coverage = BoolProperty(
        name="Coverage",
        description="Calculate brick coverage. Coverage relies on the quad section data to be of any use. The coverage system intelligently hides (non-omni) quads on the side of the brick when it is covered by other bricks.",
        default=False,
    )

    coverage_top_calculate = BoolProperty(
        name="Hide Own Top Faces",
        description="Hide the top faces of this brick when the entire top side of this brick is covered",
        default=False,
    )

    coverage_top_hide = BoolProperty(
        name="Hide Adjacent Top Faces",
        description="Hide the bottom faces of the adjacent brick(s) covering the top side of this brick",
        default=False,
    )

    coverage_bottom_calculate = BoolProperty(
        name="Hide Own Bottom Faces",
        description="Hide the bottom faces of this brick when the entire bottom side of this brick is covered",
        default=False,
    )

    coverage_bottom_hide = BoolProperty(
        name="Hide Adjacent Bottom Faces",
        description="Hide the top faces of the adjacent brick(s) covering the bottom side of this brick",
        default=False,
    )

    coverage_north_calculate = BoolProperty(
        name="Hide Own North Faces",
        description="Hide the north faces of this brick when the entire north side of this brick is covered",
        default=False,
    )

    coverage_north_hide = BoolProperty(
        name="Hide Adjacent North Faces",
        description="Hide the adjacent side faces of the adjacent brick(s) covering the north side of this brick",
        default=False,
    )

    coverage_east_calculate = BoolProperty(
        name="Hide Own East Faces",
        description="Hide the east faces of this brick when the entire east side of this brick is covered",
        default=False,
    )

    coverage_east_hide = BoolProperty(
        name="Hide Adjacent East Faces",
        description="Hide the adjacent side faces of the adjacent brick(s) covering the east side of this brick",
        default=False,
    )

    coverage_south_calculate = BoolProperty(
        name="Hide Own South Faces",
        description="Hide the south faces of this brick when the entire south side of this brick is covered",
        default=False,
    )

    coverage_south_hide = BoolProperty(
        name="Hide Adjacent South Faces",
        description="Hide the adjacent side faces of the adjacent brick(s) covering the south side of this brick",
        default=False,
    )

    coverage_west_calculate = BoolProperty(
        name="Hide Own West Faces",
        description="Hide the west faces of this brick when the entire west side of this brick is covered",
        default=False,
    )

    coverage_west_hide = BoolProperty(
        name="Hide Adjacent West Faces",
        description="Hide the adjacent side faces of the adjacent brick(s) covering the west side of this brick",
        default=False,
    )

    # -------
    # Sorting
    # -------
    auto_sort_quads = BoolProperty(
        name="Automatic Quad Sorting",
        description="Automatically sorts the quads of the meshes into the 7 sections. Coverage must be enabled for this to be of any use.",
        default=True,
    )

    # -------------
    # Use Materials
    # -------------
    use_materials = BoolProperty(
        name="Use Material Colors",
        description="Read quad colors from materials (recommended method, overrides object colors)",
        default=True,
    )

    # -----------------
    # Use Vertex Colors
    # -----------------
    use_vertex_colors = BoolProperty(
        name="Use Vertex Colors",
        description="Read quad colors from the first vertex color layer (overrides material colors)",
        default=False,
    )

    # -----------------
    # Use Object Colors
    # -----------------
    use_object_colors = BoolProperty(
        name="Parse Object Colors",
        description="Parse quad colors from object names using the definition token (intended as legacy support)",
        default=False,
    )

    # -------------
    # Calculate UVs
    # -------------
    calculate_uvs = BoolProperty(
        name="Calculate UVs",
        description="Calculate correct UV coordinates based on the brick texture name specified in the material name",
        default=True,
    )

    # ---------
    # Store UVs
    # ---------
    store_uvs = BoolProperty(
        name="Store UVs",
        description="Write calculated UVs into Blender objects (data in existing generated UV layers will be overwritten)",
        default=True,
    )

    # -------------
    # Round Normals
    # -------------
    round_normals = BoolProperty(
        name="Round Normals",
        description="Round vertex normal values to the precision defined below, if disabled normals will be written using up to 16 decimals whenever possible",
        default=True,
    )

    # ---------
    # Precision
    # ---------
    # Smaller values will increase floating point errors in the exported brick.
    # Larger values will decrease the quality of the visuals as vertex positions will become more deformed
    # Setting to 0 actually uses the minimum precision of 1e-16 since only 16 decimals are ever written to file.
    # Some floats (like UV coordinates) are not rounded.
    float_precision = StringProperty(
        name="Precision",
        description="The precision to round most floating point values (e.g. vertex coordinates) to. Changing this value is discouraged unless you know what you're doing. 16 decimal places supported. Use 0 to disable.",
        default="0.000001",
    )

    # =======
    # Writing
    # =======

    # ------------
    # Pretty Print
    # ------------
    pretty_print = BoolProperty(
        name="Pretty Print",
        description="Trim unnecessary zeros from the end of all numbers and if a number is an integer, do not write any decimal places. If false will write as many decimal places as set in the Precision property.",
        default=True,
    )

    # ---
    # Log
    # ---

    write_log = BoolProperty(
        name="Write Log",
        description="Write a log file after exporting",
        default=True,
    )

    write_log_warnings = BoolProperty(
        name="Only on Warnings",
        description="Only write a log file if warnings were generated",
        default=True,
    )

    # ----------
    # Terse Mode
    # ----------
    terse_mode = BoolProperty(
        name="Terse Mode",
        description="Exclude optional text from the BLB file making it slightly smaller and harder to read (not recommended, file size difference is negligible)",
        default=False,
    )

    # ===============
    # Export Function
    # ===============

    def execute(self, context):
        """Export the objects."""
        print("\n____STARTING BLB EXPORT____")

        props = self.properties

        # Get the current filepath which may or may not be the absolute path to the currently open .blend file.
        # Get only the name of the file from the filepath.
        # Add in the BLB extension.
        file_name = bpy.path.ensure_ext(bpy.path.display_name_from_filepath(self.filepath), self.filename_ext)

        # The absolute path to the directory user has specified in the export dialog.
        export_dir = os.path.split(self.filepath)[0] + os.sep

        if export_dir == "\\":
            # Export was probably initiated from a script, use the absolute path of the location where the script was executed.
            export_dir = bpy.path.abspath("//")

        # The name of the BLB file to export.
        if props.brick_name_source == "FILE":
            export_file = file_name
        else:
            export_file = None

        message = export_blb.export(context, props, export_dir, export_file, file_name)

        if isinstance(message, str):
            # Log the message in case the user missed it.
            logger.fatal(message)

            # Show an error popup in the UI.
            self.report({"ERROR"}, message)

            logger.clear_log()

            return {"CANCELLED"}
        else:
            # No error message, everything is OK.

            logger.clear_log()

            return {"FINISHED"}

    # ==============
    # User Interface
    # ==============

    def draw(self, context):
        """Draws the UI in the export menu."""
        layout = self.layout

        # ==================
        # Blender Properties
        # ==================
        row = layout.row()
        row.alignment = "CENTER"
        row.label("Blender Properties", icon="SCENE_DATA")

        # Property: Export Count
        row = layout.row()
        row.label("Bricks to Export:")

        row = layout.row()
        row.prop(self, "export_count", expand=True)

        multi_export = self.export_count == "MULTIPLE"

        # When doing multi-brick export, swap the brick name and objects properties and add in the brick definition property.
        if multi_export:
            bricks_in_groups = self.brick_definition == "GROUPS"

            # Property: Brick Name Multiple
            row = layout.row()
            row.enabled = multi_export
            row.label("Brick Names from:")

            row = layout.row()
            # Disable selecting values when bricks are in layers.
            row.enabled = multi_export and bricks_in_groups
            row.prop(self, "brick_name_source_multi", expand=True)

            if not bricks_in_groups:
                # If bricks are defined by layers, the brick names must come from bounds objects.
                # Otherwise you need to put all objects in every layer in their own group to define the name which defeats the purpose.
                self.brick_name_source_multi = "BOUNDS"

            # Property: Brick Definition
            row = layout.row()
            row.enabled = multi_export
            row.label("Bricks Defined by:")

            row = layout.row()
            row.enabled = multi_export
            row.prop(self, "brick_definition", expand=True)

            # Property: Export Objects Multi
            row = layout.row()
            row.label("Export Bricks in:")

            row = layout.row()
            row.enabled = multi_export
            row.prop(self, "export_objects_multi", expand=True)
        else:
            # Property: Brick Name
            row = layout.row()
            row.enabled = not multi_export
            row.label("Brick Name From:")

            row = layout.row()
            row.enabled = not multi_export
            row.prop(self, "brick_name_source", expand=True)

            # Property: Export Objects
            row = layout.row()
            row.label("Export Only:")

            row = layout.row()
            row.enabled = not multi_export
            row.prop(self, "export_objects", expand=True)

        # Property: BLB Forward Axis
        row = layout.row()
        row.label("Forward Axis:")

        row = layout.row()
        row.prop(self, "axis_blb_forward", expand=True)

        # Property: Export Scale
        layout.prop(self, "export_scale")

        # Property: Use Modifiers.
        layout.prop(self, "use_modifiers")

        # Properties: Custom Definition Tokens
        layout.prop(self, "custom_definitions", text="Custom Definition Tokens...")

        if self.custom_definitions:
            box = layout.box()
            box.label("Definition Tokens", icon="EDIT_VEC")
            box.enabled = self.custom_definitions

            def draw_definition_property(label_text, prop_name):
                """A helper function for drawing the definition properties."""
                row = box.row()

                split = row.split(percentage=0.6)
                col = split.column()
                col.label("{}:".format(label_text))

                split = split.split()
                col = split.column()
                col.prop(self, prop_name, "")

            def draw_grid_definition_property(symbol, prop_name):
                """A helper function for drawing the definition properties."""
                row = box.row()

                split = row.split(percentage=0.25)
                col = split.column()
                col.label("{}".format(symbol))

                split = split.split(percentage=0.7)
                col = split.column()
                col.prop(self, prop_name, "")

                split = split.split()
                col = split.column()
                col.prop(self, "{}_priority".format(prop_name), "")

            # This has duplicate data but I don't know how to access the property names defined earlier since self.deftoken_bounds.name doesn't seem to work.
            # For some reason self.deftoken_bounds = "deftoken_bounds" instead of an instance of StringProperty.
            row = box.row()
            row.alignment = "CENTER"
            row.label("Definition Objects", icon="OBJECT_DATA")
            row = box.row()
            row.alignment = "CENTER"
            row.label("Token In: Object Name")

            draw_definition_property("Brick Bounds", "deftoken_bounds")
            draw_definition_property("Collision Cuboids", "deftoken_collision")

            row = box.row()
            row.alignment = "CENTER"
            row.label("Brick Grid Definition Objects", icon="GRID")
            row = box.row()
            row.alignment = "CENTER"
            row.label("Token In: Object Name")

            row = box.row()
            split = row.split(percentage=0.25)
            col = split.column()
            col.label("Symbol")

            split = split.split(percentage=0.7)
            col = split.column()
            col.label("Token")

            split = split.split()
            col = split.column()
            col.label("Priority")

            draw_grid_definition_property("b", "deftoken_gridb")
            draw_grid_definition_property("d", "deftoken_gridd")
            draw_grid_definition_property("u", "deftoken_gridu")
            draw_grid_definition_property("-", "deftoken_griddash")
            draw_grid_definition_property("x", "deftoken_gridx")

            row = box.row()
            row.alignment = "CENTER"
            row.label("Quad Sorting Tokens", icon="FACESEL")
            row = box.row()
            row.alignment = "CENTER"
            row.label("Token In: Object Name")

            draw_definition_property("Top Quads", "deftoken_quad_sort_top")
            draw_definition_property("Bottom Quads", "deftoken_quad_sort_bottom")
            draw_definition_property("North Quads", "deftoken_quad_sort_north")
            draw_definition_property("East Quads", "deftoken_quad_sort_east")
            draw_definition_property("South Quads", "deftoken_quad_sort_south")
            draw_definition_property("West Quads", "deftoken_quad_sort_west")
            draw_definition_property("Omni Quads", "deftoken_quad_sort_omni")

            row = box.row()
            row.alignment = "CENTER"
            row.label("Color Tokens", icon="COLOR")
            row = box.row()
            row.alignment = "CENTER"
            row.label("Token In: Object/Material/Vertex Color Layer Name")

            draw_definition_property("Object Colors", "deftoken_color")
            draw_definition_property("In-Game Color", "deftoken_color_blank")
            draw_definition_property("Additive Color", "deftoken_color_add")
            draw_definition_property("Subtractive Color", "deftoken_color_sub")

        layout.separator()

        # ===
        # BLB
        # ===
        row = layout.row()
        row.alignment = "CENTER"
        row.label("BLB Properties", icon="MESH_CUBE")

        # Property: Custom Collision
        layout.prop(self, "custom_collision")

        # Property: Fallback Collision
        row = layout.row()
        row.label("Fallback Collision:")
        row = layout.row()
        row.prop(self, "fallback_collision", expand=True)

        # Properties: Coverage
        layout.prop(self, "calculate_coverage", text="Calculate Coverage...")

        if self.calculate_coverage:
            box = layout.box()
            box.label("Coverage Options", icon="GROUP")
            box.enabled = self.calculate_coverage

            def draw_coverage_property(label_text):
                """A helper function for drawing the coverage properties."""

                row = box.row()

                split = row.split(percentage=0.28)
                col = split.column()
                col.label(label_text)

                split = split.split(percentage=0.43)
                col = split.column()
                col.prop(self, "coverage_{}_hide".format(label_text.lower()), "")

                split = split.split()
                col = split.column()
                col.prop(self, "coverage_{}_calculate".format(label_text.lower()), "")

            row = box.row()
            split = row.split(percentage=0.27)
            col = split.column()
            col.label("")
            col.label("Side")

            split = split.split(percentage=0.42)
            col = split.column()
            col.label("Hide")
            col.label("Adjacent")

            split = split.split()
            col = split.column()
            col.label("Hide")
            col.label("Self")

            draw_coverage_property("Top")
            draw_coverage_property("Bottom")
            draw_coverage_property("North")
            draw_coverage_property("East")
            draw_coverage_property("South")
            draw_coverage_property("West")

        # Properties: Quad Sorting
        layout.prop(self, "auto_sort_quads")

        # Property: Use Material Colors
        layout.prop(self, "use_materials")

        # Property: Use Vertex Colors
        layout.prop(self, "use_vertex_colors")

        # Property: Use Object Colors
        layout.prop(self, "use_object_colors")

        # Property: UVs
        row = layout.row()
        split = row.split(percentage=0.53)
        col = split.column()
        col.prop(self, "calculate_uvs")

        # Property: Store UVs
        split = split.split()
        split.enabled = self.calculate_uvs

        if not self.calculate_uvs:
            self.store_uvs = False

        col = split.column()
        col.prop(self, "store_uvs")

        # Property: Round Normals
        layout.prop(self, "round_normals")

        # Property: Precision
        layout.prop(self, "float_precision")

        layout.separator()

        # =======
        # Writing
        # =======
        row = layout.row()
        row.alignment = "CENTER"
        row.label("File Properties", icon="TEXT")

        # Property: Pretty Print
        layout.prop(self, "pretty_print")

        # Property: Write Log
        row = layout.row()
        split = row.split(percentage=0.4)
        col = split.column()
        col.prop(self, "write_log")

        # Property: Write Log on Warnings
        # Only show when Write Log is checked.
        split = split.split()

        # The "Only on Warnings" option is grayed out when "Write Log" is not enabled.
        split.enabled = self.write_log

        if not self.write_log:
            self.write_log_warnings = False

        col = split.column()
        col.prop(self, "write_log_warnings")

        # Property: Terse Mode
        layout.prop(self, "terse_mode")

# =============
# Blender Stuff
# =============


def menu_export(self, context):
    """Adds the export option into the export menu."""
    self.layout.operator(ExportBLB.bl_idname, text="Blockland Brick (.blb)")


def register():
    """Registers this module into Blender."""
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    """Unregisters this module from Blender."""
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_export)


if __name__ == "__main__":
    register()
