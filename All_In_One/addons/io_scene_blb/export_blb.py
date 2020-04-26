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
A module for exporting Blender data into the BLB format.

@author: Demian Wright
"""
from decimal import Decimal
import bpy

from . import const, logger, blb_processor, blb_writer, common


# The export mediator module.

# ======================
# DefinitionTokens Class
# ======================
class DefinitionTokens(object):
    """A class storing all definition tokens, except brick grid and quad sort, in upper case strings.
    Brick grid and quad sort definitions are stored separately in the DerivativeProperties class.
    """

    def __init__(self, properties):
        self.bounds = properties.deftoken_bounds.upper()
        self.collision = properties.deftoken_collision.upper()

        self.color = properties.deftoken_color.upper()
        self.color_blank = properties.deftoken_color_blank.upper()
        self.color_add = properties.deftoken_color_add.upper()
        self.color_sub = properties.deftoken_color_sub.upper()

# ==========================
# DerivativeProperties Class
# ==========================


class DerivativeProperties(object):
    """A class for storing various properties derived from the user-defined Blender properties to guide the export process.

    Stores the following data:
        blendprop (Blender properties object): The original Blender properties object containing more properties that have not been processed further.
        forward_axis (Axis3D): The axis that will point forwards in-game.
        deftokens (DefinitionTokens): A class storing all definition tokens, except brick grid and quad sort, in upper case strings.
        grid_def_obj_token_priority (sequence): A sequence containing the user-defined brick grid definitions in reverse priority order.
        grid_definitions_priority (sequence): A sequence containing the brick grid symbols in the same order as grid_def_obj_token_priority.
        quad_sort_definitions (sequence): A sequence containing the user-defined definitions for quad sorting.
        scale (Decimal): The scale to export the brick at. Value is in range [0.0,1.0].
        plate_height (Decimal): The height of one Blockland plate in Blender units.
        human_brick_grid_error (Decimal): Error allowed for manually created definition objects, because they must lie exactly on the brick grid.
        precision (String): The precision to round floating point numbers to when performing calculations.
        decimal_digits (int): The number of decimal digits in precision.
    """

    def __init__(self, properties):
        """Creates the DerivativeProperties object from the specified Blender properties.

        Args:
            properties (Blender properties object): A Blender object containing user preferences.
        """
        logger.info("Export Properties:")

        # ==========
        # Properties
        # ==========
        self.blendprop = properties
        self.error_message = None

        # ============
        # Forward Axis
        # ============
        self.forward_axis = const.Axis3D.from_property_name(properties.axis_blb_forward)

        # =================
        # Definition Tokens
        # =================
        self.deftokens = DefinitionTokens(properties)

        # ==========
        # Brick Grid
        # ==========
        # Build the brick grid definition tokens and symbol priority tuple.
        # Contains the brick grid definition object name tokens in reverse priority order.
        result = self.__build_grid_priority_tuples(properties)

        if isinstance(result, str):
            self.error_message = result
        else:
            self.grid_def_obj_token_priority = result[0]
            self.grid_definitions_priority = result[1]

            # ============
            # Quad Sorting
            # ============
            self.quad_sort_definitions = self.__build_quad_sort_definitions(properties)

            # =====
            # Scale
            # =====
            # export_scale is a percentage value.
            self.scale = Decimal("{0:.{1}f}".format(properties.export_scale, const.MAX_FP_DECIMALS_TO_WRITE)) * Decimal("0.01")
            logger.info("Scale: {}".format(self.scale.normalize()), 1)

            # ==========================
            # Plate Height & Human Error
            # ==========================
            # Used for rounding vertex positions to the brick grid.
            self.human_brick_grid_error = const.HUMAN_BRICK_GRID_ERROR
            # A 1x1 Blockland plate is equal to 1.0 x 1.0 x 0.4 Blender units (X,Y,Z)
            self.plate_height = const.DEFAULT_PLATE_HEIGHT

            if self.scale != const.DECIMAL_ONE:
                self.plate_height = self.plate_height * self.scale

            # =========
            # Precision
            # =========
            prec = common.to_float_or_none(properties.float_precision)

            if prec is None:
                self.error_message = "IOBLBF010 Invalid floating point value given for floating point precision property."
            else:
                min_prec = "0.{}1".format("0" * (const.MAX_FP_DECIMALS_TO_WRITE - 1))
                dot_idx = properties.float_precision.find(".")

                if dot_idx < 0:
                    self.decimal_digits = 0
                else:
                    self.decimal_digits = len(properties.float_precision) - (dot_idx + 1)

                if properties.float_precision == "0" or Decimal(properties.float_precision) < Decimal(min_prec):
                    logger.info("Setting floating point precision to minimum.", 1)
                    self.precision = min_prec
                    self.decimal_digits = const.MAX_FP_DECIMALS_TO_WRITE
                elif self.decimal_digits > const.MAX_FP_DECIMALS_TO_WRITE:
                    logger.warning("IOBLBW013", "Precision has too many decimal digits, using {} instead.".format(const.MAX_FP_DECIMALS_TO_WRITE), 1)
                    self.decimal_digits = const.MAX_FP_DECIMALS_TO_WRITE
                    self.precision = properties.float_precision[:dot_idx] + "." + \
                        properties.float_precision[dot_idx + 1:dot_idx + 1 + const.MAX_FP_DECIMALS_TO_WRITE]
                else:
                    self.precision = properties.float_precision

            logger.info("Floating point precision: {}".format(self.precision), 1)

    @classmethod
    def __build_grid_priority_tuples(cls, properties):
        """Sorts the grid definition object name tokens into reverse priority order according the user properties.
        Definitions earlier in the sequence are overwritten by tokens later in the sequence.

        Args:
            properties (Blender properties object): A Blender object containing user preferences.

        Returns:
            A tuple containing the grid definition object tokens in the first element and the grid symbols in the same order in the second element or None if one or more definition had the same priority which leads to undefined behavior and is disallowed.
        """
        # There are exactly 5 tokens.
        tokens = [None] * 5

        # Go through every priority individually.
        tokens[properties.deftoken_gridx_priority] = properties.deftoken_gridx.upper()
        tokens[properties.deftoken_griddash_priority] = properties.deftoken_griddash.upper()
        tokens[properties.deftoken_gridu_priority] = properties.deftoken_gridu.upper()
        tokens[properties.deftoken_gridd_priority] = properties.deftoken_gridd.upper()
        tokens[properties.deftoken_gridb_priority] = properties.deftoken_gridb.upper()

        if None in tokens:
            return "IOBLBF007 Two or more brick grid definitions had the same priority."
        else:
            symbols = [None] * 5

            symbols[properties.deftoken_gridx_priority] = const.GRID_INSIDE
            symbols[properties.deftoken_griddash_priority] = const.GRID_OUTSIDE
            symbols[properties.deftoken_gridu_priority] = const.GRID_UP
            symbols[properties.deftoken_gridd_priority] = const.GRID_DOWN
            symbols[properties.deftoken_gridb_priority] = const.GRID_BOTH

            return (tuple(tokens), tuple(symbols))

    @classmethod
    def __build_quad_sort_definitions(cls, properties):
        """Creates tuple of quad section definitions used to sort quads.

        Args:
            properties (Blender properties object): A Blender object containing user preferences.

        Returns:
            A tuple containing the definitions for manual quad section sorting in the correct order.
        """
        # The definitions must be in the same order as const.QUAD_SECTION_ORDER
        return (properties.deftoken_quad_sort_top.upper(),
                properties.deftoken_quad_sort_bottom.upper(),
                properties.deftoken_quad_sort_north.upper(),
                properties.deftoken_quad_sort_east.upper(),
                properties.deftoken_quad_sort_south.upper(),
                properties.deftoken_quad_sort_west.upper(),
                properties.deftoken_quad_sort_omni.upper())


def __has_object_in_visible_layer(context, objects):
    """Check if the specified sequence of Blender objects contains at least one object that is in a visible layer in thecurrent scene.

    Args:
        context (Blender context object): A Blender object containing scene data.
        objects (sequence of Blender objects): Objects to the checked.

    Returns:
        True if at least one object is in a visible layer.
    """
    # Is there anything to check?
    if len(objects) > 0:
        # For all layers in the scene.
        for index, layer in enumerate(context.scene.layers):
            # List's first object is in current layer.
            # Current layer is visible.
            # TODO: Clarify condition.
            if True is objects[0].layers[index] == layer:
                # List has at least one object in visible layer.
                return True
    # No objects in visible layers.
    return False


def export(context, properties, export_dir, export_file, file_name):
    """Processes the data from the scene and writes it to a BLB file.

    Args:
        context (Blender context object): A Blender object containing scene data.
        properties (Blender properties object): A Blender object containing user preferences.
        export_dir (string): The absolute path to the directory where to write the BLB file.
        export_file (string): The name of the file to be written with the extension or None if brick name is to be retrieved from the bounds definition object.
        file_name (string): The name of the .blend file with the BLB extension to be used as a fall back option.

    Returns:
        None if everything went OK or a string containing an error message to display to the user if the file was not written
    """

    def get_objects(context, properties):
        """Determines the sequence of Blender objects to be processed.

        Args:
            context (Blender context object): A Blender object containing scene data.
            properties (DerivateProperties): An object containing user properties.

        Returns:
            The sequence of Blender objects from the specified Blender context to be exported according to the specified user preferences.
        """
        objects = []

        # Use selected objects?
        if properties.blendprop.export_objects == "SELECTION":
            logger.info("Exporting selected objects to BLB.")
            objects = context.selected_objects
            logger.info(logger.build_countable_message("Found ", len(objects), (" object.", " objects."), "", "No objects selected."), 1)

        # Use objects in visible layers?
        if properties.blendprop.export_objects == "LAYERS":
            logger.info("Exporting objects in visible layers to BLB.")
            # For every object in the scene.
            for obj in context.scene.objects:
                # For every layer in the scene.
                for index in range(len(context.scene.layers)):
                    # If this layer is visible.
                    # And this object is in the layer.
                    # TODO: Clarify this funky condition.
                    if True is obj.layers[index] == context.scene.layers[index]:
                        # Append to the list of objects.
                        objects.append(obj)

            logger.info(logger.build_countable_message("Found ", len(objects), (" object.", " objects."), "", "No objects in visible layers."), 1)

        # Use the whole scene?
        if properties.blendprop.export_objects == "SCENE":
            logger.info("Exporting scene to BLB.")
            objects = context.scene.objects
            logger.info(logger.build_countable_message("Found ", len(objects), (" object.", " objects."), "", "Scene has no objects."), 1)

        return objects

    def export_brick(context, properties, export_dir, export_file, file_name, objects):
        """Helper function for exporting a single brick.

        Args:
            context (Blender context object): A Blender object containing scene data.
            properties (DerivateProperties): An object containing user properties.
            export_dir (string): The absolute path to the directory where to write the BLB file.
            export_file (string): The name of the file to be written with the extension or None if brick name is to be retrieved from the bounds definition object.
            file_name (string): The name of the .blend file with the BLB extension to be used as a fall back option.
            objects (sequence of Blender objects): Objects to be exported

        Returns:
            None if everything went OK or a string containing an error message to display to the user if the file was not written
        """
        # Process Blender data into a writable format.
        data = blb_processor.process_blender_data(context, properties, objects)

        # Got the BLBData we need.
        if isinstance(data, blb_processor.BLBData):
            # Name was sourced from the bounds object.
            if export_file is None:
                # No name was actually found?
                if data.brick_name is None:
                    # Fall back to file name.
                    export_file = file_name
                else:
                    # Use the found name.
                    export_file = "{}{}".format(data.brick_name, const.BLB_EXT)

            export_path = "{}{}".format(export_dir, export_file)

            logger.info("Writing to file.")
            # Write the data to a file.
            blb_writer.write_file(deriv_properties, export_path, data)

            logger.info("Output file: {}".format(export_path), 1)

            # Remove the .BLB extension and change it to the log extension.
            logname = bpy.path.ensure_ext(export_file[:-4], const.LOG_EXT)

            # Build the full path and write the log.
            logger.write_log("{}{}".format(export_dir, logname))

            logger.clear_log()

            return None
        else:
            # Something went wrong, pass on the message.
            return data

    logger.configure(properties.write_log, properties.write_log_warnings)

    # Process the user properties further.
    deriv_properties = DerivativeProperties(properties)

    if deriv_properties.error_message is not None:
        # RETURN ON ERROR
        return deriv_properties.error_message
    else:
        # Determine how many bricks to export from this file and the objects in every brick.
        if deriv_properties.blendprop.export_count == "SINGLE":
            # Standard single brick export.
            return export_brick(context, deriv_properties, export_dir, export_file, file_name, get_objects(context, deriv_properties))
        else:
            # Export multiple.
            logger.info("Exporting multiple bricks.")
            # Bricks in groups.
            if deriv_properties.blendprop.brick_definition == "GROUPS":
                if len(bpy.data.groups) < 1:
                    # RETURN ON ERROR
                    return "IOBLBF008 No groups to export in the current scene."
                else:
                    # For all groups in the scene.
                    for group in bpy.data.groups:
                        group_objects = group.objects

                        if deriv_properties.blendprop.export_objects_multi == "LAYERS":
                            if not __has_object_in_visible_layer(context, group_objects):
                                # This group didn't have objects in visible layers.
                                # Skip the rest of the loop.
                                continue
                            # Group has at least one object in a visible layer, export group.
                        # Else: Export all groups in the scene, no need to check anything.

                        # TODO: Add the same header to all logs, not just the first.
                        logger.info("\nExporting group '{}'.".format(group.name))

                        # Objects in multiple groups will be exported more than once.
                        if deriv_properties.blendprop.brick_name_source_multi == "GROUPS":
                            export_file = "{}{}".format(group.name, const.BLB_EXT)
                            message = export_brick(context, deriv_properties, export_dir, export_file, file_name, group_objects)
                        else:
                            # Get brick name from bounds.
                            message = export_brick(context, deriv_properties, export_dir, None, file_name, group_objects)

                        # If something went wrong stop export and return the error message.
                        if message is not None:
                            return message

            else:
                # Bricks in layers.
                exported = 0
                # Check all layers in the current scene.
                for layer_idx in range(0, const.BLENDER_MAX_LAYER_IDX):
                    # Add to list if object is in the layer.
                    # Objects on multiple layers will be exported more than once.
                    layer_objects = [ob for ob in bpy.context.scene.objects if ob.layers[layer_idx]]

                    if deriv_properties.blendprop.export_objects_multi == "LAYERS":
                        if not __has_object_in_visible_layer(context, layer_objects):
                            # This visible layer did not have any objects.
                            # Skip the rest of the loop.
                            continue
                        # Else: Layer has at least one object in a visible layer, export layer objects.

                    if len(layer_objects) > 0:
                        # TODO: Add the same header to all logs, not just the first.
                        logger.info("\nExporting layer {}.".format(layer_idx + 1))
                        # Get brick name from bounds.
                        message = export_brick(context, deriv_properties, export_dir, None, file_name, layer_objects)
                        exported += 1

                        # TODO: Do not fail if one export fails.
                        # If something went wrong stop export and return the error message.
                        if message is not None:
                            return message

                if exported < 1:
                    # RETURN ON ERROR
                    return "IOBLBF009 Nothing to export in the visible layers of the current scene."
