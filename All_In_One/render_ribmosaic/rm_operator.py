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
# Operator module for both pipeline link and GUI operators.
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
import blf


# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
exec("from " + MODULE + " import rm_error")
exec("from " + MODULE + " import rm_context")
exec("from " + MODULE + " import rm_property")
exec("from " + MODULE + " import rm_panel")
exec("import " + MODULE + " as rm")


# #############################################################################
# GLOBAL OPERATORS
# #############################################################################

class WM_OT_ribmosaic_modal_sync(bpy.types.Operator):
    '''Allow user to demand the pipeline manager to execute
       its sync method.  This operator is temporary until
       background callbacks are supported
    '''
    bl_idname = "wm.ribmosaic_modal_sync"
    bl_label = "sync pipelines"

    def execute(self, context):
        print("wm.ribmosaic_modal_sync()")

        # Sync pipeline tree with current .rmp files
        rm.pipeline_manager.sync()

        return {'FINISHED'}


class RibmosaicOperator():
    """Super class for all RIB Mosaic operators providing helper methods"""

    # #### Private methods

    def _dialog_width(self, message, minimum=50):
        """Returns a pixel width large enough to encompass longest line in
        message at current fonts (this is not always the line with most
        characters depending on font and characters used!).

        message = list of lines
        minimum = smallest allowed width
        return = pixel width useful for dialog pop ups
        """

        width = 0
        dialog_width = minimum

        # Find the longest line in message
        for i, l in enumerate(message):
            # Get the pixel width of line for dialog width
            width = int(blf.dimensions(0, l)[0]) + 18

            if width > dialog_width:
                dialog_width = width

        return dialog_width

    def _dialog_message(self, layout, message):
        """Generic message dialog for displaying long lines of text in a pop up
        dialog. Can be called from operators, menus or panels.

        layout = layout from calling class draw method
        message = list of lines to display
        """

        if layout and message:
            col = layout.column(align=True)

            for l in message:
                col.label(text=l)

            layout.separator()

    def _refresh_panels(self):
        """Refreshes UI panels by simply toggling Blender's render engine"""

        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.context.scene.render.engine = rm.ENGINE

    def _unique_name(self, name, names):
        """Checks name against names list to build a unique name by appending
        a number to name if necessary. Also cleans name to be file and XML
        element safe.

        name = name string to check
        names = list of name string to check against
        """

        if "_" in name:
            segs = name.split("_")
            ext = segs.pop()

            if ext.isdigit():
                name = "_".join(segs)

        if name in names:
            for i in range(1, 100):
                new_name = name + "_" + "000"[:-len(str(i))] + str(i)

                if new_name not in names:
                    name = new_name
                    break

        return bpy.path.clean_name(name)

    def _path_info(self, xmlpath):
        """Pop last element off XML path and return new path, target element
        and list all elements also on same path.
        """

        segs = xmlpath.split("/")
        element = segs.pop()
        path = "/".join(segs)
        elements = rm.pipeline_manager.list_elements(path)

        return {'xmlpath': path, 'element': element, 'elements': elements}

# #############################################################################
# TEXT EDITOR OPERATORS
# #############################################################################


class WM_OT_ribmosaic_text_copypath(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Copy XML path to clipboard"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_text_copypath"
    bl_label = "Copy XML path to clipboard"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def invoke(self, context, event):
        wm = context.window_manager
        wm.clipboard = self.xmlpath

        return {'FINISHED'}


class WM_OT_ribmosaic_text_escape(rm_context.ExportContext,
                                  RibmosaicOperator,
                                  bpy.types.Operator):
    """Convert XML control characters in selected text to XML escape
        sequences"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_text_escape"
    bl_label = "Escape Selected Text"

    # ### Public methods

    def invoke(self, context, event):
        wm = context.window_manager

        bpy.ops.text.copy()
        wm.clipboard = wm.clipboard.replace("<", "&lt;") \
                                   .replace(">", "&gt;") \
                                   .replace("&", "&amp;") \
                                   .replace("'", "&apos;") \
                                   .replace('"', "&quot;")
        bpy.ops.text.paste()

        return {'FINISHED'}


class WM_OT_ribmosaic_text_unescape(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Convert XML escape sequences in selected text to standard characters"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_text_unescape"
    bl_label = "Unescape Selected Text"

    # ### Public methods

    def invoke(self, context, event):
        wm = context.window_manager

        bpy.ops.text.copy()
        wm.clipboard = wm.clipboard.replace("&lt;", "<") \
                                   .replace("&gt;", ">") \
                                   .replace("&amp;", "&") \
                                   .replace("&apos;", "'") \
                                   .replace("&quot;", '"')
        bpy.ops.text.paste()

        return {'FINISHED'}


class WM_OT_ribmosaic_text_comment(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Show comments for selected XML element or attribute"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_text_comment"
    bl_label = "Show Comment Dialog"

    xmlpath = bpy.props.StringProperty(name="xmlpath")
    comment = bpy.props.StringProperty(name="comment")

    # ### Public methods

    def draw(self, context):
        self._dialog_message(self.layout, self.comment.splitlines())

    def execute(self, context):
        try:
            wm = context.window_manager
            segs = self.xmlpath.split(".")

            if len(segs) > 1:
                path = segs[0]
                attr = segs[1]
            else:
                path = segs[0]
                attr = None

            comment = rm.pipeline_manager.get_element_info(path, attr,
                                                            "comment")

            if not comment:
                comment = "No comment available"

            self.comment = comment
            dialog_width = self._dialog_width(comment.splitlines())

            wm.invoke_popup(self, width=dialog_width)
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}


class WM_OT_ribmosaic_text_addshaderpanel(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):

    """
      Compile shader in text editor, Build slmeta, and add shader panel
      to selected pipeline.
    """

    # ### Public attributes

    bl_idname = "wm.ribmosaic_text_addshaderpanel"
    bl_label = "Compile and generate shader panel for selected pipeline"

    def execute(self, context):
        try:
            text = context.space_data.text
            # make sure text is saved, compiled, and slmeta is built
            bpy.ops.wm.ribmosaic_library_compile('EXEC_DEFAULT',
                pipeline="Text_Editor")

            wm = context.window_manager
            # get the index of the active pipeline
            index = wm.ribmosaic_pipelines.active_index
            # determine the path to the slmeta file for the shader in the text
            # editor
            slmetapath = (rm.export_manager.export_directory +
                    rm.export_manager.make_shader_export_path() +
                    text.name[:-2] + "slmeta")
            # only try to add the shader panel if a pipeline is selected
            # and the slmeta file exists
            if index >= 0 and os.path.isfile(slmetapath):
                bpy.ops.wm.ribmosaic_library_addpanel('INVOKE_DEFAULT',
                    filepath=slmetapath,
                    pipeline=wm.ribmosaic_pipelines.collection[index].xmlpath)

        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

# #############################################################################
# XML OPERATORS
# #############################################################################

# Operator for the <type=INFO> XML layout element
class WM_OT_ribmosaic_xml_info(rm_context.ExportContext,
                               RibmosaicOperator,
                               bpy.types.Operator):
    """Display information on current selection"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_xml_info"
    bl_label = "Description"

    xmlpath = bpy.props.StringProperty(name="xmlpath")
    event = bpy.props.StringProperty(name="event")
    context = bpy.props.StringProperty(name="context")

    # ### Public methods

    def draw(self, context):
        self._dialog_message(self.layout, self.event.splitlines())

    def execute(self, context):
        wm = context.window_manager

        if self.context:
            condat = self._context_data(context, self.context)
            self.pointer_datablock = condat['data']
            self.context_window = condat['window']

        if self.xmlpath:
            segs = self.xmlpath.split("/")

            try:
                self.context_pipeline = segs[0]
                self.context_category = segs[1]
                self.context_panel = segs[2]
            except:
                pass

            self.event = self._resolve_links(self.event)

        # Force default message if none
        if not self.event:
            self.event = "No description specified"

        # Convert string returns and split lines for dialog width
        self.event = self.event.replace("\\n", "\n")
        dialog_width = self._dialog_width(self.event.splitlines())

        wm.invoke_popup(self, width=dialog_width)
        return {'FINISHED'}


# Operator for the <type=BUTTON> XML layout element
class WM_OT_ribmosaic_xml_button(rm_context.ExportContext,
                                 RibmosaicOperator,
                                 bpy.types.Operator):
    """This operator handles panel button event attribute tokens"""

    bl_idname = "wm.ribmosaic_xml_button"
    bl_label = "Triggers panel button down script"

    context = bpy.props.StringProperty(name="context")
    xmlpath = bpy.props.StringProperty(name="xmlpath")
    event = bpy.props.StringProperty(name="event")

    def draw(self, context):
        self._dialog_message(self.layout, self.event.splitlines())

    def execute(self, context):
        wm = context.window_manager

        if self.context:
            condat = self._context_data(context, self.context)
            self.pointer_datablock = condat['data']
            self.context_window = condat['window']

        if self.xmlpath:
            segs = self.xmlpath.split("/")

            try:
                self.context_pipeline = segs[0]
                self.context_category = segs[1]
                self.context_panel = segs[2]
            except:
                pass

            self.event = self._resolve_links(self.event)

        if self.event:
            # Convert string returns and split lines for dialog width
            self.event = self.event.replace("\\n", "\n")
            dialog_width = self._dialog_width(self.event.splitlines())

            wm.invoke_popup(self, width=dialog_width)

        self._refresh_panels()
        return {'FINISHED'}


# Operator for the <type=LINK> XML layout element
class WM_OT_ribmosaic_xml_link(rm_context.ExportContext,
                               RibmosaicOperator,
                               bpy.types.Operator):
    """Link to another control property using a RNA data path"""

    bl_idname = "wm.ribmosaic_xml_link"
    bl_label = "Link to another control property..."

    context = bpy.props.StringProperty(name="context")
    xmlpath = bpy.props.StringProperty(name="xmlpath")
    event = bpy.props.StringProperty(name="event")
    link = bpy.props.StringProperty(name="RNA Data Path",
        description="Paste the RNA data path of any property on the same"\
                    "data-block (can also append mathematics)")

    def draw(self, context):
        layout = self.layout
        layout.prop(self.properties, "link")

    def execute(self, context):
        wm = context.window_manager

        if self.event:
            rm.pipeline_manager.set_attrs(self.event, True, link=self.link)

        self._refresh_panels()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.context:
            condat = self._context_data(context, self.context)
            self.pointer_datablock = condat['data']
            self.context_window = condat['window']

        if self.xmlpath:
            segs = self.xmlpath.split("/")

            try:
                self.context_pipeline = segs[0]
                self.context_category = segs[1]
                self.context_panel = segs[2]
            except:
                pass

            path = self._resolve_links(self.event)

        if path:
            link = rm.pipeline_manager.get_attr(self, path, "link", False)
            self.link = link
            self.event = path

        return wm.invoke_props_dialog(self, width=300)


# Operator for the <type=FILE> XML layout element
class WM_OT_ribmosaic_xml_file(rm_context.ExportContext,
                               RibmosaicOperator,
                               bpy.types.Operator):
    """Open file browser"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_xml_file"
    bl_label = "Select file"

    xmlpath = bpy.props.StringProperty(name="xmlpath")
    event = bpy.props.StringProperty(name="event")
    context = bpy.props.StringProperty(name="context")
    filepath = bpy.props.StringProperty(name="Search Path", default="//")
    filename = bpy.props.StringProperty(name="Pipeline Name")
    directory = bpy.props.StringProperty(name="Pipeline Directory")
    relativepath = bpy.props.BoolProperty(name="Use relative path",
                    description="Return path relative to export directory",
                    default=True)
    ribpath = bpy.props.BoolProperty(name="Return RIB Safe Path",
                    description="Return path safe for RIB format",
                    default=True)
    usename = bpy.props.BoolProperty(name="Include File In Path",
                    description="Return both path and file selection",
                    default=True)

    # ### Public methods

    def draw(self, context):
        layout = self.layout

        layout.prop(self.properties, "relativepath")
        layout.prop(self.properties, "ribpath")
        layout.prop(self.properties, "usename")

    def execute(self, context):
        try:
            path = self.directory

            if self.relativepath:
                if bpy.data.is_saved:
                    rm.export_manager._update_directory()
                    export = rm.export_manager.export_directory
                    path = os.path.relpath(path, export) + os.sep
                else:
                    raise rm_error.RibmosaicError("Blend must be saved for "
                                                  "relative paths to work")

            if self.ribpath:
                path = rm.RibPath(path)

            if self.usename:
                path += self.filename

            if self.pointer_datablock:
                try:
                    exec("self.pointer_datablock." + self.event + " = path")
                except:
                    raise rm_error.RibmosaicError("Cant find property \"" +
                                                  self.event + \
                                                  "\" on datablock \"" +
                                                  str(data) + "\"",
                                                  sys.exc_info())
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.context:
            condat = self._context_data(context, self.context)
            self.pointer_datablock = condat['data']
            self.context_window = condat['window']

        if self.xmlpath:
            segs = self.xmlpath.split("/")

            try:
                self.context_pipeline = segs[0]
                self.context_category = segs[1]
                self.context_panel = segs[2]
            except:
                pass

            path = self._resolve_links(self.event)

        if path:
            self.event = path

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}


# #############################################################################
# PANEL OPERATORS
# #############################################################################

class WM_OT_ribmosaic_panel_duplicate(rm_context.ExportContext,
                                      RibmosaicOperator,
                                      bpy.types.Operator):
    """Duplicate this panel (copies panel in host pipeline with new name)"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_duplicate"
    bl_label = "Duplicate Panel?"

    context = bpy.props.StringProperty(name="context")
    xmlpath = bpy.props.StringProperty(name="xmlpath")
    panel = bpy.props.StringProperty(name="Panel Name",
                                     description="Name of new panel")

    # ### Public methods

    def draw(self, context):
        layout = self.layout
        layout.prop(self.properties, "panel")

    def execute(self, context):
        p = self._path_info(self.xmlpath)
        name = self._unique_name(self.panel, p['elements'])

        try:
            rm.pipeline_manager.duplicate_panel(self.xmlpath, name)

            attr = rm.PropertyHash(p['xmlpath'].replace("/", "") +
                    name + "enabled")

            exec("self.pointer_datablock." + attr + " = True")
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        condat = self._context_data(context, self.context)
        self.pointer_datablock = condat['data']
        self.context_window = condat['window']

        p = self._path_info(self.xmlpath)
        self.panel = self._unique_name(p['element'], p['elements'])

        return context.window_manager.invoke_props_dialog(self, width=300)


class WM_OT_ribmosaic_panel_delete(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Delete this panel (completely removes this panel from host pipeline)"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_delete"
    bl_label = "Delete this panel from pipeline?"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            rm.pipeline_manager.remove_panel(self.xmlpath)
            self._refresh_panels()

            rm.RibmosaicInfo("WM_OT_ribmosaic_panel_delete.execute: Panel " +
                             self.xmlpath + " removed")
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        width = self._dialog_width([self.bl_label])
        return context.window_manager.invoke_props_dialog(self, width)


class WM_OT_ribmosaic_panel_enable(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Pin or Unpin this panel from the current datablock"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_enable"
    bl_label = "Pin this panel to the current datablock?"

    context = bpy.props.StringProperty(name="context")
    xmlpath = bpy.props.StringProperty(name="xmlpath")
    popup = bpy.props.BoolProperty(name="popup", default=True)

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            if self.context and self.xmlpath:
                d = self._context_data(context, self.context)['data']
                e = rm.PropertyHash(self.xmlpath.replace("/", "") + 'enabled')

                exec("d." + e + " = True")
                self._refresh_panels()
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        width = self._dialog_width([self.bl_label])

        if self.popup:
            return context.window_manager.invoke_props_dialog(self, width)
        else:
            self.execute(context)
            return {'FINISHED'}


class WM_OT_ribmosaic_panel_disable(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Pin or Unpin this panel from the current datablock"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_disable"
    bl_label = "Unpin this panel from the current datablock?"

    context = bpy.props.StringProperty(name="context")
    xmlpath = bpy.props.StringProperty(name="xmlpath")
    popup = bpy.props.BoolProperty(name="popup", default=True)

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            if self.context and self.xmlpath:
                # Get data
                d = self._context_data(context, self.context)['data']
                e = rm.PropertyHash(self.xmlpath.replace("/", "") + 'enabled')

                # Set active item of collection to disabled panel
                if "shader_panels" in self.xmlpath:
                    collection = context.window_manager.ribmosaic_shaders
                    selection = "d.ribmosaic_active_shader"
                elif "utility_panels" in self.xmlpath:
                    collection = context.window_manager.ribmosaic_utilities
                    selection = "d.ribmosaic_active_utility"
                elif "command_panels" in self.xmlpath:
                    collection = context.window_manager.ribmosaic_commands
                    selection = "d.ribmosaic_active_command"

                for p in collection.collection:
                    if p.xmlpath == self.xmlpath:
                        exec(selection + " = '" + p.name + "'")
                        break

                # Disable panel
                exec("d." + e + " = False")
                self._refresh_panels()
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        width = self._dialog_width([self.bl_label])

        if self.popup:
            return context.window_manager.invoke_props_dialog(self, width)
        else:
            self.execute(context)
            return {'FINISHED'}


class WM_OT_ribmosaic_panel_register(rm_context.ExportContext,
                                     RibmosaicOperator,
                                     bpy.types.Operator):
    """Register or Unregister panel from Blender's GUI"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_register"
    bl_label = "Register this panel to Blender's UI?"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        rm.pipeline_manager.set_attrs(self.xmlpath, True, register="True")
        self._refresh_panels()
        return {'FINISHED'}

    def invoke(self, context, event):
        width = self._dialog_width([self.bl_label])
        return context.window_manager.invoke_props_dialog(self, width)


class WM_OT_ribmosaic_panel_unregister(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Register or Unregister panel from Blender's GUI"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_unregister"
    bl_label = "Unregister this panel from Blender's UI?"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        rm.pipeline_manager.set_attrs(self.xmlpath, True, register="False")
        self._refresh_panels()
        return {'FINISHED'}

    def invoke(self, context, event):
        width = self._dialog_width([self.bl_label])
        return context.window_manager.invoke_props_dialog(self, width)


class WM_OT_ribmosaic_panel_update(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Update shader panel from shader source (uses slmeta file)"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_panel_update"
    bl_label = "Update shader panel from source?"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        pipeline = self.xmlpath.split("/")[0]
        rm_context = {'context_pipeline': pipeline,
                      'context_category': "shader_panels",
                      'context_panel': ""}

        try:
            slmeta = rm.pipeline_manager.get_attr(rm_context, self.xmlpath,
                                                  "slmeta", False)

            if slmeta:
                rm.pipeline_manager.slmeta_to_panel(slmeta, "", pipeline,
                                                    "", False)
            rm.pipeline_manager._write_xml(pipeline)
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            rm.pipeline_manager._write_xml(pipeline)
            self._refresh_panels()
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        try:
            if bpy.data.is_saved:
                if self.xmlpath:
                    return wm.invoke_props_dialog(self)
                else:
                    return {'CANCELLED'}
            else:
                raise rm_error.RibmosaicError("Blend must be saved before "
                                              "shader panel can be rebuilt")
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}


# #############################################################################
# LIBRARY OPERATORS
# #############################################################################

class WM_OT_ribmosaic_library_set(rm_context.ExportContext,
                                  RibmosaicOperator,
                                  bpy.types.Operator):
    """Path and build options for this pipeline's shader source library"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_library_set"
    bl_label = "Set Shader Library"

    pipeline = bpy.props.StringProperty(name="Pipeline")
    filepath = bpy.props.StringProperty(name="Search Path")
    filename = bpy.props.StringProperty(name="Pipeline Name")
    directory = bpy.props.StringProperty(name="Pipeline Directory")
    compile = bpy.props.BoolProperty(name="Compile shaders",
                    description="Compile all shader sources when building"
                                "library",
                    default=True)
    build = bpy.props.BoolProperty(name="Build slmeta",
                    description="Create slmeta for all shaders when building"
                                "library",
                    default=True)
    relativepath = bpy.props.BoolProperty(name="Use relative path",
                    description="Return path relative to saved blend file",
                    default=True)

    # ### Public methods

    def draw(self, context):
        layout = self.layout
        params = context.space_data.params
        params.use_filter = True
        params.use_filter_folder = True

        layout.label(text="Select directory containing shaders...")
        layout.prop(self.properties, "relativepath")
        layout.prop(self.properties, "compile")
        layout.prop(self.properties, "build")
        layout.separator()
        layout.operator("wm.ribmosaic_library_clear").pipeline = self.pipeline

    def execute(self, context):
        try:
            if self.relativepath:
                self.directory = bpy.path.relpath(self.directory) + os.sep

            rm.pipeline_manager.set_attrs(self.pipeline,
                                       library=self.directory,
                                       compile=str(self.compile),
                                       build=str(self.build))
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        p = self.pipeline

        try:
            if bpy.data.is_saved:
                lib = rm.pipeline_manager.get_attr(self, p, "library", False)
                compile = rm.pipeline_manager.get_attr(self, p, "compile",
                                                       False)
                build = rm.pipeline_manager.get_attr(self, p, "build", False)

                if lib:
                    lib = os.path.realpath(bpy.path.abspath(lib)) + os.sep
                    self.filepath = lib
                else:
                    self.filepath = "//"
                if compile:
                    self.compile = eval(compile)
                if build:
                    self.build = eval(build)
            else:
                raise rm_error.RibmosaicError("Blend must be saved before "
                                              "library can be set")
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}


class WM_OT_ribmosaic_library_clear(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Clear pipeline's shader library path and close file manager"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_library_clear"
    bl_label = "Clear Shader Library"

    pipeline = bpy.props.StringProperty(name="Pipeline")

    # ### Public methods

    def invoke(self, context, event):
        try:
            rm.pipeline_manager.set_attrs(self.pipeline, library="")
            bpy.ops.file.cancel()
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}


class WM_OT_ribmosaic_library_compile(rm_context.ExportContext,
                                      RibmosaicOperator,
                                      bpy.types.Operator):
    """Compiles and generates slmeta for shaders in specified shader library"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_library_compile"
    bl_label = "Build shaders for this library? (ESC to cancel once started)"

    pipeline = bpy.props.StringProperty(name="Pipeline")

    # ### Public methods
    def draw(self, context):
        pass

    def execute(self, context):
        rm_panel.RibmosaicRender.compile_library = self.pipeline

        bpy.ops.render.render()

        rm_panel.RibmosaicRender.compile_library = ""
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.pipeline:
            return wm.invoke_props_dialog(self)
        else:
            return {'CANCELLED'}


class WM_OT_ribmosaic_library_addpanel(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Add shader panels from pipeline's shader library
       (generated from slmeta)"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_library_addpanel"
    bl_label = "Shader Panels"

    files = bpy.props.CollectionProperty(name="Pipeline List",
                    type=rm_property.RibmosaicFiles)
    filepath = bpy.props.StringProperty(name="Search Path")
    filename = bpy.props.StringProperty(name="Pipeline Name")
    directory = bpy.props.StringProperty(name="Pipeline Directory")
    pipeline = bpy.props.StringProperty(name="Pipeline")
    library = bpy.props.StringProperty(name="Shader Library")
    autoprops = bpy.props.BoolProperty(name="Auto Assign Properties",
                    description="Automatically assign shader panel to"
                                " properties window based on shader type",
                    default=True)
    worldprops = bpy.props.BoolProperty(name="World Properties",
                    description="Use shader in world properties window",
                    default=True)
    objprops = bpy.props.BoolProperty(name="Object Properties",
                    description="Use shader in object properties window",
                    default=False)
    camprops = bpy.props.BoolProperty(name="Camera Properties",
                    description="Use shader in camera properties window",
                    default=True)
    curveprops = bpy.props.BoolProperty(name="Curve Properties",
                    description="Use shader in curve properties window",
                    default=False)
    surfprops = bpy.props.BoolProperty(name="Surface Properties",
                    description="Use shader in surface properties window",
                    default=False)
    lampprops = bpy.props.BoolProperty(name="Lamp Properties",
                    description="Use shader in lamp properties window",
                    default=True)
    meshprops = bpy.props.BoolProperty(name="Mesh Properties",
                    description="Use shader in mesh properties window",
                    default=False)
    metaprops = bpy.props.BoolProperty(name="Metaball Properties",
                    description="Use shader in metaball properties window",
                    default=False)
    matprops = bpy.props.BoolProperty(name="Material Properties",
                    description="Use shader in material properties window",
                    default=True)
    panelregister = bpy.props.BoolProperty(name="Panel Register",
                    description="Is panel registered on load or manually?",
                    default=True)
    enabled = bpy.props.BoolProperty(name="Panel Enable",
                    description="Is panel initially enabled or disabled?",
                    default=False)
    delete = bpy.props.BoolProperty(name="Panel Delete",
                    description="Can panel be deleted by user?",
                    default=True)
    duplicate = bpy.props.BoolProperty(name="Panel Duplicate",
                    description="Can panel be duplicated by user?",
                    default=True)
    relativepath = bpy.props.BoolProperty(name="Use relative path",
                    description="Return path relative to saved blend file",
                    default=True)

    # ### Public methods

    def draw(self, context):
        layout = self.layout

        layout.label(text="Select slmeta to convert to panel...")
        layout.separator()
        layout.prop(self.properties, "relativepath", toggle=True)
        layout.separator()
        layout.label(text="Panel state and permissions:")
        box = layout.box()
        box.prop(self.properties, "panelregister")
        box.prop(self.properties, "enabled")
        box.prop(self.properties, "duplicate")
        box.prop(self.properties, "delete")
        layout.separator()
        layout.label(text="Panel properties associations:")
        box = layout.box()
        box.prop(self.properties, "autoprops")
        col = box.column()
        col.enabled = not self.autoprops
        col.prop(self.properties, "worldprops")
        col.prop(self.properties, "objprops")
        col.prop(self.properties, "camprops")
        col.prop(self.properties, "curveprops")
        col.prop(self.properties, "surfprops")
        col.prop(self.properties, "lampprops")
        col.prop(self.properties, "meshprops")
        col.prop(self.properties, "metaprops")
        col.prop(self.properties, "matprops")

    def execute(self, context):
        try:
            # Be sure to update export directory
            rm.export_manager._update_directory(context.scene)

            # Setup shaders path reference based on where it came from
            if self.library == self.directory:
                shader_path = "@[SLIB::]@"
                library_path = "@[SLIB::RIB]@"
            elif self.directory.endswith("Text_Editor" + os.sep):
                shader_path = "@[STXT::]@"
                library_path = "@[STXT::RIB]@"
            elif self.directory.endswith(self.pipeline + os.sep):
                shader_path = "@[SXML::]@"
                library_path = "@[SXML::RIB]@"
            else:
                if self.relativepath:
                    shader_path = bpy.path.relpath(self.directory) + os.sep
                else:
                    shader_path = self.directory

                library_path = rm.RibPath(os.path.relpath(self.directory,
                                          rm.export_manager.export_directory) +
                                          os.sep)

            # If no selections and *.slmeta then collect all meta in directory
            if not len(self.files) and self.filename == "*.slmeta":
                for f in os.listdir(self.directory):
                    if os.path.splitext(f)[1].lower() == ".slmeta":
                        self.files.add().name = f

            for filename in self.files:
                if os.path.splitext(filename.name)[1].lower() != ".slmeta":
                    raise rm_error.RibmosaicError(filename.name +
                                                  " not a .slmeta file")

                props = []

                if not self.autoprops:
                    if self.worldprops:
                        props.append('WORLD')
                    if self.objprops:
                        props.append('OBJECT')
                    if self.camprops:
                        props.append('CAMERA')
                    if self.curveprops:
                        props.append('CURVE')
                    if self.surfprops:
                        props.append('SURFACE')
                    if self.lampprops:
                        props.append('LAMP')
                    if self.meshprops:
                        props.append('MESH')
                    if self.metaprops:
                        props.append('META')
                    if self.matprops:
                        props.append('MATERIAL')

                rm.pipeline_manager.slmeta_to_panel(shader_path +
                                        filename.name,
                                        library_path, self.pipeline, "", False,
                                        windows=",".join(props),
                                        register=str(self.panelregister),
                                        enabled=str(self.enabled),
                                        duplicate=str(self.duplicate),
                                        delete=str(self.delete))

            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        try:
            if bpy.data.is_saved:
                lib = rm.pipeline_manager.get_attr(self, self.pipeline,
                                                   "library", False)

                if lib:
                    lib = os.path.realpath(bpy.path.abspath(lib)) + os.sep
                    self.library = lib
                    self.filepath = lib + "*.slmeta"
                else:
                    self.library = ""
                    #self.filepath = "//*.slmeta"
            else:
                raise rm_error.RibmosaicError("Blend must be saved before "
                                              "shaders can be added")
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}



# #############################################################################
# PIPELINE OPERATORS
# #############################################################################

class WM_OT_ribmosaic_pipeline_enable(rm_context.ExportContext,
                                      RibmosaicOperator,
                                      bpy.types.Operator):
    """Enable pipeline"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_enable"
    bl_label = "Enable Pipeline"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def invoke(self, context, event):
        rm.pipeline_manager.set_attrs(self.xmlpath, False, enabled="True")
        self._refresh_panels()
        return {'FINISHED'}


class WM_OT_ribmosaic_pipeline_disable(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Disable pipeline"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_disable"
    bl_label = "Disable Pipeline"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def invoke(self, context, event):
        rm.pipeline_manager.set_attrs(self.xmlpath, False, enabled="False")
        self._refresh_panels()
        return {'FINISHED'}


class WM_OT_ribmosaic_pipeline_new(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Create a new empty pipeline (useful for custom shader pipelines)"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_new"
    bl_label = "New Pipeline..."

    name = bpy.props.StringProperty(name="Pipeline Name",
                        description="Name of the pipeline and .rmp text file")
    help = bpy.props.StringProperty(name="Pipeline Help",
                        description="Help message to display in help dialog")

    # ### Public methods

    def draw(self, context):
        layout = self.layout
        layout.prop(self.properties, "name")
        layout.prop(self.properties, "help")

    def execute(self, context):
        try:
            wm = context.window_manager
            name = self.properties.name
            help = "\n" + self.help + "\n"

            if name:
                pipelines = rm.pipeline_manager.list_pipelines()
                name = self._unique_name(name, pipelines)

                rm.pipeline_manager.new_pipeline(name, help)
                self._refresh_panels()
            else:
                raise rm_error.RibmosaicError("Pipeline name cannot be blank")
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        name = self.properties.name
        wm = context.window_manager

        if name:
            pipelines = rm.pipeline_manager.list_pipelines()
            self.properties.name = self._unique_name(name, pipelines)

        return wm.invoke_props_dialog(self, width=300)


class WM_OT_ribmosaic_pipeline_load(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Load pipeline from file system"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_load"
    bl_label = "Load Pipeline..."

    files = bpy.props.CollectionProperty(name="Pipeline List",
                    type=rm_property.RibmosaicFiles)
    filepath = bpy.props.StringProperty(name="Pipeline Path")
    filename = bpy.props.StringProperty(name="Pipeline Name")
    directory = bpy.props.StringProperty(name="Pipeline Directory")
    pipeline = bpy.props.StringProperty(name="Pipeline Element Name")

    # ### Public methods

    def draw(self, context):
        message = rm.pipeline_manager.list_help(self.pipeline)

        if message:
            self._dialog_message(self.layout, message)
        else:
            self.layout.label(text="Load RIB Mosaic pipelines...")

    def execute(self, context):
        wm = context.window_manager

        # If no selections and *.rmp then collect all pipelines in directory
        if not len(self.files) and self.filename == "*.rmp":
            for f in os.listdir(self.directory):
                if os.path.splitext(f)[1].lower() == ".rmp":
                    self.files.add().name = f

        for filename in self.files:
            path = self.directory + filename.name

            try:
                self.pipeline = rm.pipeline_manager.load_pipeline(path)
                message = rm.pipeline_manager.list_help(self.pipeline)

                if message:
                    dialog_width = self._dialog_width(message)

                    wm.invoke_popup(self, width=dialog_width)
                self._refresh_panels()
            except rm_error.RibmosaicError as err:
                err.ReportError(self)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


class WM_OT_ribmosaic_pipeline_remove(rm_context.ExportContext,
                                      RibmosaicOperator,
                                      bpy.types.Operator):
    """Remove selected pipeline"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_remove"
    bl_label = "Remove selected pipeline?"

    pipeline = bpy.props.StringProperty(name="Pipeline")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        wm = context.window_manager

        try:
            rm.pipeline_manager.remove_pipeline(self.pipeline)

            rm.RibmosaicInfo("WM_OT_ribmosaic_pipeline_remove.execute:"
                             "Pipeline " + self.pipeline + " removed")
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.pipeline:
            return wm.invoke_props_dialog(self)
        else:
            return {'CANCELLED'}


class WM_OT_ribmosaic_pipeline_reload(rm_context.ExportContext,
                                      RibmosaicOperator,
                                      bpy.types.Operator):
    """Reload and re-register all panels for selected pipeline"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_reload"
    bl_label = "Reload Pipeline"

    pipeline = bpy.props.StringProperty(name="Pipeline",
                    description="Name of pipeline")

    # ### Public methods
    def draw(self, context):
        pass

    def execute(self, context):
        wm = context.window_manager

        try:
            rm.pipeline_manager.update_pipeline(self.pipeline)

            rm.RibmosaicInfo("WM_OT_ribmosaic_pipeline_reload.execute:"
                             "Pipeline " + self.pipeline + " reloaded")
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.pipeline:
            return wm.invoke_props_dialog(self)
        else:
            return {'CANCELLED'}


class WM_OT_ribmosaic_pipeline_help(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Display help dialog for selected pipeline"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_help"
    bl_label = "Pipeline Help Dialog"

    pipeline = bpy.props.StringProperty(name="Pipeline")

    # ### Public methods

    def draw(self, context):
        message = rm.pipeline_manager.list_help(self.pipeline)

        if not message:
            message = ["No help available"]

        self._dialog_message(self.layout, message)

    def execute(self, context):
        try:
            wm = context.window_manager
            message = rm.pipeline_manager.list_help(self.pipeline)

            if not message:
                message = ["No help available"]

            dialog_width = self._dialog_width(message)

            wm.invoke_popup(self, width=dialog_width)
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}


class WM_OT_ribmosaic_pipeline_update(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Update ALL shader panels from sources in shader library
       (updates using slmeta)"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_update"
    bl_label = "Update ALL shader panels in pipeline?"

    pipeline = bpy.props.StringProperty(name="pipeline")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        category = self.pipeline + "/shader_panels"
        rm_context = {'context_pipeline': self.pipeline,
                      'context_category': "shader_panels",
                      'context_panel': ""}

        try:
            for panel in rm.pipeline_manager.list_elements(category):
                rm_context['context_panel'] = panel
                xmlpath = category + "/" + panel
                slmeta = rm.pipeline_manager.get_attr(rm_context, xmlpath,
                                                      "slmeta", False)

                if slmeta:
                    rm.pipeline_manager.slmeta_to_panel(slmeta, "",
                                                        self.pipeline, "",
                                                        False)
            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        try:
            if bpy.data.is_saved:
                if self.pipeline:
                    return wm.invoke_props_dialog(self)
                else:
                    return {'CANCELLED'}
            else:
                raise rm_error.RibmosaicError("Blend must be saved before "
                                              "shader panels can be rebuilt")
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}


class WM_OT_ribmosaic_pipeline_register(rm_context.ExportContext,
                                        RibmosaicOperator,
                                        bpy.types.Operator):
    """Register ALL shader panels in pipeline to Blender's UI"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_register"
    bl_label = "Register ALL shaders in pipeline?"

    pipeline = bpy.props.StringProperty(name="pipeline")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        category = self.pipeline + "/shader_panels"

        try:
            for panel in rm.pipeline_manager.list_elements(category):
                xmlpath = category + "/" + panel
                rm.RibmosaicInfo("WM_OT_ribmosaic_pipeline_register.execute:"
                                "Registering panel " + panel + "...")
                rm.pipeline_manager.set_attrs(xmlpath, True, False,
                                              register="True")

            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.pipeline:
            return wm.invoke_props_dialog(self)
        else:
            return {'CANCELLED'}


class WM_OT_ribmosaic_pipeline_unregister(rm_context.ExportContext,
                                          RibmosaicOperator,
                                          bpy.types.Operator):
    """Unregister ALL shader panels in pipeline from Blender's UI"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_unregister"
    bl_label = "Unregister ALL shader panels in pipeline?"

    pipeline = bpy.props.StringProperty(name="pipeline")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        category = self.pipeline + "/shader_panels"

        try:
            for panel in rm.pipeline_manager.list_elements(category):
                xmlpath = category + "/" + panel
                rm.RibmosaicInfo("WM_OT_ribmosaic_pipeline_unregister.execute:"
                                 "Unregistering panel " + panel + "...")
                rm.pipeline_manager.set_attrs(xmlpath, True, False,
                                              register="False")

            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.pipeline:
            return wm.invoke_props_dialog(self)
        else:
            return {'CANCELLED'}


class WM_OT_ribmosaic_pipeline_purge(rm_context.ExportContext,
                                     RibmosaicOperator,
                                     bpy.types.Operator):
    """Completely removes ALL shader panels from pipeline"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_purge"
    bl_label = "Remove ALL shader panels from pipeline?"

    pipeline = bpy.props.StringProperty(name="pipeline")

    # ### Public methods

    def draw(self, context):
        pass

    def execute(self, context):
        category = self.pipeline + "/shader_panels"

        try:
            for panel in rm.pipeline_manager.list_elements(category):
                xmlpath = category + "/" + panel
                rm.RibmosaicInfo("WM_OT_ribmosaic_pipeline_purge.execute:"
                                 "Purging shader panel " + panel + "...")
                rm.pipeline_manager.remove_panel(xmlpath)

            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
        except rm_error.RibmosaicError as err:
            rm.pipeline_manager._write_xml(self.pipeline)
            self._refresh_panels()
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if self.pipeline:
            return wm.invoke_props_dialog(self)
        else:
            return {'CANCELLED'}


class WM_OT_ribmosaic_pipeline_search(rm_context.ExportContext,
                                      RibmosaicOperator,
                                      bpy.types.Operator):
    """Search for and select XML element in pipeline text"""

    # ### Public attributes

    bl_idname = "wm.ribmosaic_pipeline_search"
    bl_label = "Search Pipeline"

    xmlpath = bpy.props.StringProperty(name="xmlpath")

    # ### Public methods

    def _select_element(self, textdata, xmlpath):
        """Searches textdata for specified xmlpath and highlights element in
        editor and making it focused.

        textdata = Text datablock to select and search
        xmlpath = Pipeline path to element to highlight
        """

        try:
            segs = xmlpath.split("/")
            segl = len(segs)
            segi = 0
            highlight = False

            for i, l in enumerate(textdata.lines):
                line = l.body.strip()

                if segi < segl and line.startswith("<" + segs[segi]):
                    segi += 1

                    if segi == segl:
                        bpy.ops.text.jump(line=i + 1)
                        highlight = True

                        if line.endswith("/>"):
                            bpy.ops.text.move_select(type='NEXT_LINE')
                            break

                if highlight:
                    bpy.ops.text.move_select(type='NEXT_LINE')

                if segi > 0 and line.startswith("</" + segs[segi - 1]):
                    segi -= 1

                    if segi + 1 == segl:
                        break

            if not highlight:
                raise
        except:
            raise rm_error.RibmosaicError("XML path \"" + xmlpath +
                                          "\" not found!")

    def invoke(self, context, event):
        if self.xmlpath:
            try:
                segs = self.xmlpath.split("/")
                text = rm.pipeline_manager.get_attr(None, segs[0],
                                                    "filepath", False)

                textdata = bpy.data.texts[text]
                context.space_data.text = textdata

                self._select_element(textdata, self.xmlpath)
                context.window_manager.ribmosaic_pipeline_search = self.xmlpath

                return {'FINISHED'}
            except rm_error.RibmosaicError as err:
                err.ReportError(self)
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}


# #############################################################################
# RENDER SPACE OPERATORS
# #############################################################################

class RENDER_OT_ribmosaic_pass_add(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Add a new render pass"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_add"
    bl_label = "Add a new render pass"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        ribmosaic_passes.collection.add().name = "Beauty Pass"
        ribmosaic_passes.collection.move(len(ribmosaic_passes.collection) - 1,
                                         0)
        ribmosaic_passes.active_index = 0

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_del(rm_context.ExportContext,
                                   RibmosaicOperator,
                                   bpy.types.Operator):
    """Remove the selected render pass"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_del"
    bl_label = "Remove selected render pass"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        len_passes = len(ribmosaic_passes.collection) - 1

        if len_passes:
            ribmosaic_passes.collection.remove(active_index)

            if active_index == len_passes:
                ribmosaic_passes.active_index -= 1

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_copy(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Copy settings from selected render pass into clipboard"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_copy"
    bl_label = "Copy pass settings"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        active_pass = ribmosaic_passes.collection[active_index]
        pass_clipboard = rm_panel.RENDER_PT_ribmosaic_passes.pass_clipboard
        pass_clipboard.clear()

        for p in dir(active_pass):
            if p.startswith("pass_"):
                if "bpy_" in eval("str(type(active_pass." + p + "))"):
                    pass_clipboard[p] = eval("list(active_pass." + p + ")")
                else:
                    pass_clipboard[p] = eval("active_pass." + p)

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_paste(rm_context.ExportContext,
                                     RibmosaicOperator,
                                     bpy.types.Operator):
    """Paste settings from clipboard to selected render pass"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_paste"
    bl_label = "Paste pass settings"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        active_pass = ribmosaic_passes.collection[active_index]
        pass_clipboard = rm_panel.RENDER_PT_ribmosaic_passes.pass_clipboard

        for p in pass_clipboard.items():
            v = p[1]
            if type(v) == str:
                exec("active_pass." + p[0] + " = '" + str(p[1]) + "'")
            else:
                exec("active_pass." + p[0] + " = " + str(p[1]))

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_duplicate(rm_context.ExportContext,
                                         RibmosaicOperator,
                                         bpy.types.Operator):
    """Duplicate selected render pass"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_duplicate"
    bl_label = "Duplicate pass"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        active_pass = ribmosaic_passes.collection[active_index]
        len_passes = len(ribmosaic_passes.collection)

        bpy.ops.scene.ribmosaic_passes_copy()
        ribmosaic_passes.collection.add().name = active_pass.name
        ribmosaic_passes.collection.move(len_passes, active_index + 1)
        ribmosaic_passes.active_index += 1
        bpy.ops.scene.ribmosaic_passes_paste()

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_tiles_add(rm_context.ExportContext,
                                         RibmosaicOperator,
                                         bpy.types.Operator):
    """Use tile setup of active pass to generate a pass per tile"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_tiles_add"
    bl_label = "Generate tile passes"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        active_pass = ribmosaic_passes.collection[active_index]
        name = active_pass.name

        if active_pass.pass_tile_x and active_pass.pass_tile_y:
            tile = 0

            for x in range(active_pass.pass_tile_x):
                for y in range(active_pass.pass_tile_y):
                    bpy.ops.scene.ribmosaic_passes_duplicate()
                    active_index = ribmosaic_passes.active_index
                    active_pass = ribmosaic_passes.collection[active_index]
                    active_pass.name = name + "-Tile_" + str(x) + "_" + str(y)
                    active_pass.pass_tile_index = tile
                    tile += 1

            ribmosaic_passes.active_index = active_index - tile

            active_index = ribmosaic_passes.active_index
            ribmosaic_passes.collection[active_index].pass_enabled = False

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_tiles_del(rm_context.ExportContext,
                                         RibmosaicOperator,
                                         bpy.types.Operator):
    """Removes all tile passes generated from active pass"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_tiles_del"
    bl_label = "Remove tile passes"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        name = ribmosaic_passes.collection[active_index].name
        len_passes = len(ribmosaic_passes.collection)
        index = 0

        while index < len(ribmosaic_passes.collection):
            if name + "-Tile" in ribmosaic_passes.collection[index].name:
                ribmosaic_passes.collection.remove(index)
            else:
                index += 1

        if ribmosaic_passes.active_index >= index:
            ribmosaic_passes.active_index = index - 1

        active_index = ribmosaic_passes.active_index
        ribmosaic_passes.collection[active_index].pass_enabled = True

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_seq_add(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Use sequence setup of active pass to generate a pass
       per frame sequence"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_seq_add"
    bl_label = "Generate sequence passes"

    # ### Public methods

    def execute(self, context):
        scene = bpy.context.scene
        ribmosaic_passes = scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        active_pass = ribmosaic_passes.collection[active_index]
        start = active_pass.pass_range_start
        end = active_pass.pass_range_end
        step = active_pass.pass_range_step
        width = active_pass.pass_seq_width
        name = active_pass.name

        if not start:
            start = scene.frame_start
        if not end:
            end = scene.frame_end
        if not step:
            step = scene.frame_step

        if active_pass.pass_seq_width:
            sequence = 0
            frames = range(start, end + 1, step)

            for seq in range(0, len(frames), width):
                s = frames[seq]
                w = seq + (width - 1)
                if w >= len(frames):
                    e = frames[-1]
                else:
                    e = frames[w]
                bpy.ops.scene.ribmosaic_passes_duplicate()
                active_index = ribmosaic_passes.active_index
                active_pass = ribmosaic_passes.collection[active_index]
                active_pass.name = name + "-Seq_" + str(s) + "-" + str(e)
                active_pass.pass_seq_index = sequence
                active_pass.pass_range_start = s
                active_pass.pass_range_end = e
                sequence += 1

            ribmosaic_passes.active_index = active_index - sequence

            active_index = ribmosaic_passes.active_index
            ribmosaic_passes.collection[active_index].pass_enabled = False

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_seq_del(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Removes all sequence passes generated from active pass"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_seq_del"
    bl_label = "Remove sequence passes"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        name = ribmosaic_passes.collection[active_index].name
        len_passes = len(ribmosaic_passes.collection)
        index = 0

        while index < len(ribmosaic_passes.collection):
            if name + "-Seq" in ribmosaic_passes.collection[index].name:
                ribmosaic_passes.collection.remove(index)
            else:
                index += 1

        if ribmosaic_passes.active_index >= index:
            ribmosaic_passes.active_index = index - 1

        active_index = ribmosaic_passes.active_index
        ribmosaic_passes.collection[active_index].pass_enabled = True

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_up(rm_context.ExportContext,
                                  RibmosaicOperator,
                                  bpy.types.Operator):
    """Move selected render pass up list"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_up"
    bl_label = "Move render pass up"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        to_index = active_index - 1

        if active_index > 0:
            ribmosaic_passes.collection.move(active_index, to_index)
            ribmosaic_passes.active_index = to_index

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_down(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Move selected render pass down list"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_down"
    bl_label = "Move render pass down"

    # ### Public methods

    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        active_index = ribmosaic_passes.active_index
        to_index = active_index + 1
        len_passes = len(ribmosaic_passes.collection) - 1

        if active_index < len_passes:
            ribmosaic_passes.collection.move(active_index, to_index)
            ribmosaic_passes.active_index = to_index

        return {'FINISHED'}


class RENDER_OT_ribmosaic_pass_sort(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Sort selected render pass by its type"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_passes_sort"
    bl_label = "Sort render pass"

    # ### Public methods

    # move active pass to slot after a pass with matching or higher group
    def execute(self, context):
        ribmosaic_passes = bpy.context.scene.ribmosaic_passes
        len_passes = len(ribmosaic_passes.collection) - 1
        passes = ribmosaic_passes.collection
        active_index = ribmosaic_passes.active_index
        active_pass = passes[active_index]
        group_order = [g[0] for g in pass_types]
        active_group = group_order.index(active_pass.pass_type)
        to_index = -1

        # Cycle through passes in reverse order to keep beauty passes last
        for i in list(range(len_passes, -1, -1)) + [-1]:
            # Add a bogus pass and group above all to force sorting order
            if i > -1:
                g = group_order.index(passes[i].pass_type)
            else:
                g = len(pass_types)

            # Find pass with higher or matching group that's
            # not the active pass
            if g >= active_group and i != active_index:
                to_index = i

                # If moving down the list add one to keep reverse order
                if active_index > i:
                    to_index += 1

                # If match is one slot before active do nothing
                if i + 1 == active_index:
                    to_index = -1

                break

        if to_index > -1:
            passes.move(active_index, to_index)
            ribmosaic_passes.active_index = to_index

        return {'FINISHED'}


class RENDER_OT_ribmosaic_purgemaps(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Purge maps output folder (./Maps/)"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_purgemaps"
    bl_label = "Purge Maps"

    # ### Public methods

    def execute(self, context):
        try:
            rm.export_manager.prepare_export(clean_paths=[],
                                          purge_paths=['MAP'])
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}


class RENDER_OT_ribmosaic_purgerenders(rm_context.ExportContext,
                                       RibmosaicOperator,
                                       bpy.types.Operator):
    """Purge render output folder (./Renders/)"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_purgerenders"
    bl_label = "Purge Renders"

    # ### Public methods

    def execute(self, context):
        try:
            rm.export_manager.prepare_export(clean_paths=[],
                                          purge_paths=['RND'])
        except rm_error.RibmosaicError as err:
            err.ReportError(self)
            return {'CANCELLED'}

        return {'FINISHED'}


# #############################################################################
# SCENE SPACE OPERATORS
# #############################################################################

class SCENE_OT_ribmosaic_searchpath(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Append a directory to this seach path"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_searchpath"
    bl_label = "Append Directory"

    filepath = bpy.props.StringProperty(name="Search Path")
    filename = bpy.props.StringProperty(name="Pipeline Name")
    directory = bpy.props.StringProperty(name="Pipeline Directory")
    searchpath = bpy.props.StringProperty(name="Searchpath Property")
    ribpath = bpy.props.BoolProperty(name="Return RIB Safe Path",
                    description="Returns path safe for RIB format",
                    default=True)

    # ### Public methods

    def draw(self, context):
        params = context.space_data.params
        params.use_filter = True
        params.use_filter_folder = True
        layout = self.layout

        layout.label(text="Append directory to search path...")
        layout.prop(self.properties, "ribpath")

    def execute(self, context):
        path = self.directory

        if self.ribpath:
            path = rm.RibPath(path)

        if eval(self.searchpath):
            sep = ":"
        else:
            sep = ""

        exec(self.searchpath + " += \"" + sep + path + "\"")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}


class SCENE_OT_ribmosaic_exportpath(rm_context.ExportContext,
                                    RibmosaicOperator,
                                    bpy.types.Operator):
    """Select path to export and render scene"""

    # ### Public attributes

    bl_idname = "scene.ribmosaic_exportpath"
    bl_label = "Export Directory"

    filepath = bpy.props.StringProperty(name="Export Path")
    filename = bpy.props.StringProperty(name="Pipeline Name")
    directory = bpy.props.StringProperty(name="Pipeline Directory")
    exportpath = bpy.props.StringProperty(name="Export Property")
    relativepath = bpy.props.BoolProperty(name="Use relative path",
                    description="Use relative path from blend",
                    default=True)

    # ### Public methods

    def draw(self, context):
        params = context.space_data.params
        params.use_filter = True
        params.use_filter_folder = True
        layout = self.layout

        layout.label(text="Select export directory...")
        layout.prop(self.properties, "relativepath")

    def execute(self, context):
        if self.relativepath:
            self.directory = bpy.path.relpath(self.directory) + os.sep

        exec(self.exportpath + " = \"" + self.directory + "\"")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}
