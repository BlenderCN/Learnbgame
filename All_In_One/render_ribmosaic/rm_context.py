# #############################################################################
# AUTHOR BLOCK:
# #############################################################################
#
# RIB Mosaic RenderMan(R) IDE, see <http://sourceforge.net/projects/ribmosaic>
# by Eric Nathen Back aka WHiTeRaBBiT, 01-24-2010
# This script is protected by the GPL: Gnu Public License
# GPL - http://www.gnu.org/copyleft/gpl.html
#
# #############################################################################
# GPL LICENSE BLOCK:
# #############################################################################
#
# Script Copyright (C) Eric Nathen Back
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
#
# #############################################################################
# COPYRIGHT BLOCK:
# #############################################################################
#
# The RenderMan(R) Interface Procedures and Protocol are:
# Copyright 1988, 1989, 2000, 2005 Pixar
# All Rights Reserved
# RenderMan(R) is a registered trademark of Pixar
#
# #############################################################################
# COMMENT BLOCK:
# #############################################################################
#
# Exporter context module
# (state info for all objects in pipeline and exporter),
# is inherited by all panels, operators, links and archive objects.
#
# This script is PEP 8 compliant
#
# Search TODO for incomplete code
# Search FIXME for improper code
# Search XXX for broken code
#
# #############################################################################
# END BLOCKS
# #############################################################################

import os
import sys
import bpy


# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
exec("from " + MODULE + " import rm_error")
exec("import " + MODULE + " as rm")


# #############################################################################
# EXPORT CONTEXT CLASS
# #############################################################################

# #### Maintains object location and state in pipeline system and exporter

class ExportContext():
    """Superclass for nearly every subclass in RIB Mosaic. This provides public
    exporter and pipeline attributes to access the current export context from
    pipeline links. This context is maintained by the following objects:
    - export objects
    - command objects
    - link objects
    - panel objects
    - operator objects

    The public members of this interface are exposed to the pipeline
    editor's UI and link system. This facilitates the creation of very
    complex pipelines. The private members of this interface are to aid
    each respective object in accessing and maintaining their own export
    context.
    """

    # #### Public attributes

    # Addon info
    addon_name = ""  # Path safe name of addon module

    # Data pointers
    pointer_parent = None  # Parent export object
    pointer_datablock = None  # Current datablock
    pointer_pass = None  # Current render pass object
    pointer_render = None  # Current render engine object

    # Pipeline context
    context_pipeline = ""  # Current pipeline
    context_category = ""  # Current pipeline sub element
    context_panel = ""  # Current pipeline panel element
    context_window = ""  # Assigned Blender properties window
    context_enabled = True  # Current "enabled" state of panel

    # File context
    root_path = "."  # Root export directory
    archive_path = ""  # Relative path to archive file
    archive_name = ""  # Name of archive file
    target_path = ""  # Path to target file/s
    target_name = ""  # Name of target file
    blend_path = ""  # Path of current blend file
    blend_name = ""  # Name of current blend file
    blend_ext = ""  # Extension of current blend file

    # Exporter state counters
    current_pass = 0  # Current pass index
    current_subpass = 0  # Current sub pass index
    current_frame = 0  # Current Blender frame
    current_rmframe = 0  # Current RenderMan frame
    current_subframe = 0  # Current blur subframe
    current_dupli = 0  # Current dupli index
    current_command = 0  # Current command (shell script) index
    current_library = 0  # Current shader library index
    current_lightid = 0  # Current RenderMan light ID
    current_indent = 0  # Current indentation level for RIB text ouput

    # Output dimensions
    dims_resx = 0  # X output resolution
    dims_resy = 0  # Y output resolution
    dims_cropx = 0  # X cropping resolution
    dims_cropy = 0  # Y cropping resolution

    # Pass context
    pass_type = ""  # Current pass's type
    pass_tile = 0  # Tile index number
    pass_sequence = 0  # Sequence index number
    pass_userid = 0  # User defined pass id
    pass_output = ""  # Display output string
    pass_layer = ""  # Assigned Blender layer
    pass_multilayer = False  # Multilayer output pass
    pass_ribstr = ""  # User defined rib string

    # Datablock context
    data_name = ""  # Active datablock name
    data_type = ""  # Active datablock type

    # #### Private methods

    def __init__(self, export_object=None, pointer_datablock=None,
                 pointer_pass=None):
        """Initialize export context using a subclass export_object.

        export_object = Any object subclassed from ExportContext
        pointer_datablock = Pointer to any Blender datablock
        pointer_pass = Pointer to any RIB Mosaic pass
        """

        if export_object:  # Construct parameters from export object
            self.addon_name = export_object.addon_name

            self.pointer_parent = export_object
            self.pointer_datablock = export_object.pointer_datablock
            self.pointer_pass = export_object.pointer_pass
            self.pointer_render = export_object.pointer_render

            self.context_pipeline = export_object.context_pipeline
            self.context_category = export_object.context_category
            self.context_panel = export_object.context_panel
            self.context_window = export_object.context_window
            self.context_enabled = export_object.context_enabled

            self.root_path = export_object.root_path
            self.archive_path = export_object.archive_path
            self.archive_name = export_object.archive_name
            self.target_path = export_object.target_path
            self.target_name = export_object.target_name
            self.blend_path = export_object.blend_path
            self.blend_name = export_object.blend_name
            self.blend_ext = export_object.blend_ext

            self.current_pass = export_object.current_pass
            self.current_subpass = export_object.current_subpass
            self.current_frame = export_object.current_frame
            self.current_rmframe = export_object.current_rmframe
            self.current_subframe = export_object.current_subframe
            self.current_dupli = export_object.current_dupli
            self.current_command = export_object.current_command
            self.current_library = export_object.current_library
            self.current_lightid = export_object.current_lightid
            self.current_indent = export_object.current_indent

            self.dims_resx = export_object.dims_resx
            self.dims_resy = export_object.dims_resy
            self.dims_cropx = export_object.dims_cropx
            self.dims_cropy = export_object.dims_cropy

            self.pass_type = export_object.pass_type
            self.pass_tile = export_object.pass_tile
            self.pass_sequence = export_object.pass_sequence
            self.pass_userid = export_object.pass_userid
            self.pass_output = export_object.pass_output
            self.pass_layer = export_object.pass_layer
            self.pass_multilayer = export_object.pass_multilayer
            self.pass_ribstr = export_object.pass_ribstr

            self.data_name = export_object.data_name
            self.data_type = export_object.data_type
        else:  # If no export object initialize data based parameters
            filepath = os.path.split(bpy.data.filepath)
            nameext = os.path.splitext(filepath[1])

            self.addon_name = MODULE.replace("render_", "")
            self.blend_path = filepath[0] + os.sep
            self.blend_name = nameext[0]
            self.blend_ext = nameext[1]

        # Construct pointer based parameters if set
        if pointer_pass:
            p = pointer_pass
            self.pointer_pass = p
            self.pass_type = getattr(p, "pass_type",
                                        self.pass_type)
            self.pass_tile = getattr(p, "pass_tile_index",
                                        self.pass_tile)
            self.pass_sequence = getattr(p, "pass_seq_index",
                                         self.pass_sequence)
            self.pass_userid = getattr(p, "pass_passid",
                                        self.pass_userid)
            self.pass_output = getattr(p, "pass_display_file",
                                        self.pass_output)
            self.pass_layer = getattr(p, "pass_layerfilter",
                                        self.pass_layer)
            self.pass_multilayer = getattr(p, "pass_multilayer",
                                        self.pass_multilayer)
            self.pass_ribstr = getattr(p, "pass_rib_string",
                                        self.pass_ribstr)

        self._set_pointer_datablock(pointer_datablock)

    def _set_pointer_datablock(self, pointer_datablock=None):
        if pointer_datablock:
            self.pointer_datablock = pointer_datablock
            self.data_name = getattr(pointer_datablock, "name", "")
            self.data_type = getattr(pointer_datablock, "type", self.data_type)

    def _public_attrs(self, *include):
        """Returns list of public attributes plus any defined in include"""

        return [a for a in dir(ExportContext) if \
                (type(getattr(self, a)).__name__ != 'method' \
                and not a.startswith('_')) or a in include]

    def _public_methods(self, *include):
        """Returns list of public methods plus any defined in include"""

        return [a for a in dir(ExportContext) if \
                (type(getattr(self, a)).__name__ == 'method' \
                and not a.startswith('_')) or a in include]

    def _test_break(self):
        """Use self.pointer_render to test for break in export process. If
        break occurred throw error for export handlers to catch.
        """

        # Test for break if in render object
        if self.pointer_render and self.pointer_render.test_break():
            raise rm_error.RibmosaicError("Process canceled by user")

    def _resolve_links(self, text, textpath=""):
        """Separate and resolve all links in text returning combined result

        text = String containing links to resolve
        textpath = path where text came from (for error reporting)
        """

        local = {'rm_link': None}
        exec("from " + MODULE + " import rm_link", globals(), local)
        rm_link = local['rm_link']

        def walk_links(link_list):
            """walk through multidimensional list of strings with each branch
            representing a link. Start from deepest elements of list resolving
            the links in each and collapsing the list with resolved strings.
            """

            try:
                for i, l in enumerate(link_list):
                    if type(l) == list:
                        link = walk_links(l)

                        pl = rm_link.PipelineLink(self, link)
                        link_list[i] = pl.resolve_link()
                        del pl

                string = "".join(link_list)
            except rm_error.RibmosaicError as err:
                err.ReportError()
                raise rm_error.RibmosaicError('Link errors from "' +
                                              textpath + '"')

            return string

        # Convert start/end tokens into multidimensional list
        t = repr(text)
        q = t[0]
        links = eval("[" + q + t[1:-1]
                     .replace("@[", q + ", [" + q)
                     .replace("]@", q + "], " + q) +
                     q + "]")

        return walk_links(links)

    def _panel_enabled(self, do_filter=True):
        """Determines if a panel should be enabled or disabled according to
        the ContextExport attributes and panel properties. This is used by both
        the panel classes during draw and export objects during validation.

        do_filter = If enabled render pass filter will be processed for enabled
        return = returns final True/False panel enabled state
        """

        # Be sure we have an XML path to get panel attributes
        if self.context_pipeline and \
           self.context_category and \
           self.context_panel:
            catpath = self.context_pipeline + "/" + \
                      self.context_category
            panpath = self.context_pipeline + "/" + \
                      self.context_category + "/" + \
                      self.context_panel
            enabled = rm.pipeline_manager.get_attr(self,
                                                 self.context_pipeline,
                                                 "enabled",
                                                 False,
                                                 "True")
            register = rm.pipeline_manager.get_attr(self,
                                                 panpath,
                                                 "register",
                                                 False,
                                                 "True")

            # Be sure current panel is registered and its pipeline is enabled
            if eval(enabled) and eval(register):
                # We need a datablock to check properties
                if self.pointer_datablock:
                    enabled_name = rm.PropertyHash(self.context_pipeline +
                                                   self.context_category +
                                                   self.context_panel +
                                                   "enabled")

                    try:
                        enabled_prop = eval("self.pointer_datablock." +
                                            enabled_name)
                    except:
                        enabled_prop = True

                    # Check if there's an active pass
                    if self.pointer_pass and do_filter:
                        panel_filter = self.pointer_pass.pass_panelfilter

                        # If pass has a filter run it
                        if panel_filter:
                            #Setup export context for any links in filter
                            self.context_enabled = enabled_prop

                            try:
                                enabled = eval(self._resolve_links(self,
                                               panel_filter))
                            except:
                                raise rm_error.RibmosaicError(
                                        "Filter expression error",
                                        sys.exc_info())
                        else:
                            enabled = enabled_prop
                    else:
                        enabled = enabled_prop
                else:
                    enabled = True
            else:
                enabled = False
        else:
            enabled = True

        return enabled

    def _context_data(self, context, context_type):
        """Use panel's context and self.context_type to find active data-block.

        context = context from Blender's Panel class draw method
        context_type = type of context to get data from (can pass bl_context)
        return = dictionary with data-block, search type and window type
        """

        context_type = context_type.upper()

        try:
            if context:
                if context_type == 'TEXT':
                    data = context.window_manager
                    search = ""
                    window = ""
                elif context_type == 'DATA':
                    if context.mesh:
                        data = context.mesh
                        search = "meshes"
                        window = 'MESH'
                    elif context.curve:
                        data = context.curve
                        search = "curves"
                        window = context.object.type
                    elif context.meta_ball:
                        data = context.meta_ball
                        search = "metaballs"
                        window = 'META'
                    elif context.lamp:
                        data = context.lamp
                        search = "lamps"
                        window = 'LAMP'
                    elif context.camera:
                        data = context.camera
                        search = "cameras"
                        window = 'CAMERA'
                elif context_type == 'RENDER':
                    data = context.scene
                    search = "renders"
                    window = context_type
                elif context_type == 'SCENE':
                    data = context.scene
                    search = "scenes"
                    window = context_type
                elif context_type == 'WORLD':
                    data = context.world
                    search = "worlds"
                    window = context_type
                elif context_type == 'OBJECT':
                    data = context.object
                    search = "objects"
                    window = context_type
                elif context_type == 'MATERIAL':
                    data = context.material
                    search = "materials"
                    window = context_type
                elif context_type == 'PARTICLE':
                    data = context.particle_system.settings
                    search = "particles"
                    window = context_type
                elif context_type == 'TEXTURE':
                    data = context.texture
                    search = "textures"
                    window = context_type
                else:
                    data = context.scene
                    search = "scenes"
                    window = "SCENE"
            else:
                data = None
                search = ""
                window = ""
        except:
                data = None
                search = ""
                window = ""

        return {'data': data, 'search': search, 'window': window}

    # #### Public methods

    def inc_indent(self):
        """ Increment the current indent by one. """
        self.current_indent += 1

    def dec_indent(self):
        """ Decrement the current indent by one.  Does not allow the indent to
            go below zero.
        """
        self.current_indent -= 1
        if self.current_indent < 0:
            self.current_indent = 0

    # TODO begin writing handy public export methods for links here!
    # TODO methods and docstrings to show in pipeline editor link builder
    # TODO the following are just pseudo examples of handy methods

    def pass_add(self, name=""):
        """Add RenderMan pass"""

        print("Test public export context method")

    def pass_remove(self, name=""):
        """Remove RenderMan pass"""

        print("Test public export context method")

    def pass_is(self, name=""):
        """Does specified RenderMan pass already exist?"""

        print("Test public export context method")

    def rib_comment(self, prop="", string=""):
        """Returns string with leading RIB comment value of prop is false"""

        print("Test public export context method")

    def ribify_primvar(self, datablock=None, data=None, rmname="",
                        rmtype="", rmclass=""):
        """Export data in geometry datablock to
           current RIB archive as primvar"""

        print("Test public export context method")
