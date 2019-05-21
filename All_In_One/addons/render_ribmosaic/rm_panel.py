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
#
# GUI module for all panels, menus and UI helper methods.
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
import bpy


# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
exec("from " + MODULE + " import rm_error")
exec("from " + MODULE + " import rm_context")
exec("import " + MODULE + " as rm")


DEBUG_PRINT = False

# #############################################################################
# MENU CLASSES AND FUNCTIONS
# #############################################################################


def ribmosaic_text_menu(self, context):
    """Text editor right click context menu responsible for displaying
    options relevent to the XML path of the text cursor in a pipeline document.
    """

    # Make sure RIB Mosaic is selected
    if context.scene.render.engine == rm.ENGINE:
        layout = self.layout
        text = context.space_data.text

        # Make sure there's a text datablock
        if text:
            # Get file extension (from filepath or text name)
            if text.filepath:
                ext = os.path.splitext(text.filepath)[1]
            else:
                ext = os.path.splitext(text.name)[1]

            # Show menu according to file type
            if ext == ".rmp":
                # Determine XML path from cursor position in text
                xmlpath = []
                attribute = ""
                basepath = ""
                abspath = ""
                relpath = ""

                try:
                    for l in text.lines:
                        line = l.body.strip()
                        current = (l == text.current_line)

                        # If line contains an element
                        # push it on path and get attrs
                        if (line.startswith("<") and
                            not line.startswith(("</", "<?"))):
                            element = line.strip("<> ").split(" ", 1)
                            xmlpath.append(element[0])

                            # If attrs determine which one is under cursor
                            if (current and len(element) > 1 and
                                '"' in element[1]):
                                pos = text.current_character
                                start = l.body.index(element[0]) + \
                                        len(element[0])
                                attrs = element[1].split('"')

                                for i in range(0, len(attrs) - 1, 2):
                                    end = start + len(attrs[i] + \
                                          attrs[i + 1]) + 2

                                    if pos >= start and pos <= end:
                                        attribute = attrs[i].strip(" =")
                                        break

                                    start = end

                        # If we reach current line then stop
                        if current:
                            break

                        # If last element closes pop it off path
                        if line.startswith("</") or line.endswith("/>"):
                            xmlpath.pop()

                    # Build path string
                    if xmlpath:
                        try:
                            xmlrel = list(xmlpath)
                            xmlrel[0] = ""
                            xmlrel[2] = ""
                        except:
                            pass

                        basepath = "/".join(xmlpath)
                        abspath = "/".join(xmlpath)
                        relpath = "/".join(xmlrel)

                        if attribute:
                            abspath += "." + attribute
                            relpath += "." + attribute
                except:
                    pass

                # Global Options
                layout.separator()
                layout.operator("wm.ribmosaic_pipeline_reload",
                                text="Reload Pipeline").pipeline = xmlpath[0]
                layout.operator("wm.ribmosaic_text_copypath",
                                text="Copy Relative Path").xmlpath = relpath
                layout.operator("wm.ribmosaic_text_copypath",
                                text="Copy Absolute Path").xmlpath = abspath
                layout.operator("wm.ribmosaic_text_escape",
                                text="Escape Selection")
                layout.operator("wm.ribmosaic_text_unescape",
                                text="Unescape Selection")

                # Element Options
                if basepath:
                    layout.separator()
                    layout.operator("wm.ribmosaic_text_comment",
                                    text="Element Comments").xmlpath = basepath

                    # TODO add dynamic menu for adding sub elements found in
                    #   PipelineManager._pipeline_elements[*]['user_elements']
                    # TODO add operator for loading shader source from file

                # Attribute Options
                if attribute:
                    layout.separator()
                    layout.operator("wm.ribmosaic_text_comment",
                                text="Attribute Comments").xmlpath = abspath

                    # TODO add dynamic menu for selecting attr options found in
                    # PipelineManager._pipeline_elements[*]
                    #   ['attributes'][*]['options']
            elif ext == ".sl":
                layout.separator()
                layout.operator("wm.ribmosaic_library_compile",
                                text="Build Shaders").pipeline = "Text_Editor"

                layout.operator("wm.ribmosaic_text_addshaderpanel",
                            icon='ZOOMIN',
                            text="Add Shader Panels")


class WM_MT_ribmosaic_pipeline_menu(bpy.types.Menu):
    """Pipeline options menu"""

    # ### Public attributes

    bl_label = "Pipeline editing"

    # ### Public methods

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        index = wm.ribmosaic_pipelines.active_index
        pipeline = wm.ribmosaic_pipelines.collection[index].xmlpath

        layout.operator("wm.ribmosaic_pipeline_help",
                        icon='QUESTION').pipeline = pipeline
        layout.separator()
        layout.operator("wm.ribmosaic_library_addpanel",
                        icon='ZOOMIN',
                        text="Add Shader Panels").pipeline = pipeline
        layout.operator("wm.ribmosaic_pipeline_purge",
                        text="Remove Shader Panels",
                        icon='X').pipeline = pipeline
        layout.operator("wm.ribmosaic_pipeline_update",
                        text="Update Shader Panels",
                        icon='TRIA_UP').pipeline = pipeline
        layout.separator()
        layout.operator("wm.ribmosaic_pipeline_register",
                        text="Register Shader Panels",
                        icon='LOCKVIEW_ON').pipeline = pipeline
        layout.operator("wm.ribmosaic_pipeline_unregister",
                        text="Unregister Shader Panels",
                        icon='LOCKVIEW_OFF').pipeline = pipeline


# #############################################################################
# GLOBAL UI PANEL CLASSES
# #############################################################################

class RibmosaicRender(bpy.types.RenderEngine):
    """The render engine class, used for scene and preview renders"""

    # ### Public attributes

    bl_use_preview = True
    bl_idname = rm.ENGINE
    bl_label = rm.ENGINE

    compile_library = ""  # Specify pipeline to compile library for (no render)
    preview_samples = 2  # Preview render xy samples
    preview_shading = 2.0  # Preview render shading rate
    preview_compile = True  # Compile shaders for preview
    preview_optimize = True  # Optimize textures for preview

    # ### Public methods

    def render(self, scene):
        rmv = rm.ENGINE + " " + rm.VERSION

        try:
            ### FIXME ###
            # can't write to scene datablock during render
            # so this has to be accomplished differently
            # Special setup for preview render
            # if scene.name == "preview":
            #
            #    scene.ribmosaic_purgeshd = self.preview_compile
            #    scene.ribmosaic_compileshd = self.preview_compile
            #    scene.ribmosaic_purgetex = self.preview_optimize
            #    scene.ribmosaic_optimizetex = self.preview_optimize

            c = scene.frame_current
            i = scene.frame_step
            s = scene.frame_start

            # Only prepare export if on start frame of not in a frame sequence
            if c == s or not ((c - i) == rm.export_manager.export_frame):
                self.update_stats("", rmv + ": Preparing export...")
                rm.export_manager.prepare_export(active_scene=scene,
                                        shader_library=self.compile_library)
                self.update_stats("", rmv + ": Processing shaders...")
                rm.export_manager.export_shaders(render_object=self,
                                        shader_library=self.compile_library)

                if not self.compile_library:
                    self.update_stats("", rmv + ": Processing textures...")
                    rm.export_manager.export_textures(render_object=self)

            # Special setup for preview render
            if scene.name == "preview" and rm.export_manager.active_pass:
                ap = rm.export_manager.active_pass
                ap.pass_shadingrate = self.preview_shading
                ap.pass_samples_x = self.preview_samples
                ap.pass_samples_y = self.preview_samples

            if not self.compile_library:
                self.update_stats("", rmv + ": Processing RIB...")
                rm.export_manager.export_rib(render_object=self)

            self.update_stats("", rmv + ": Executing commands...")
            rm.export_manager.execute_commands()

            if not self.compile_library:
                self.update_stats("", rmv + ": Post processing...")

                # Cycle through all beauty pass outputs
                x = rm.export_manager.display_output['x']
                y = rm.export_manager.display_output['y']

                result = self.begin_result(0, 0, x, y)

                for p in rm.export_manager.display_output['passes']:
                    if self.test_break():
                        raise rm_error.RibmosaicError(
                                "RibmosaicRender.render: Export canceled")

                    try:
                        # If multilayer exr
                        if p['multilayer']:
                            result.load_from_file(p['file'])
                        # Otherwise load per layer
                        else:
                            for l in result.layers:
                                # If no layer load in all otherwise match
                                if not p['layer'] or p['layer'] == l.name:
                                    l.load_from_file(p['file'])
                    except:
                        rm.RibmosaicInfo("RibmosaicRender.render:"
                                " Could not load " + p['file'] + " into layer")

                self.end_result(result)

            self.update_stats("", rmv + ": Process complete")
        except rm_error.RibmosaicError as err:
            self.update_stats("", rmv + ": Process terminated")
            err.ReportError()


class RibmosaicPropertiesPanel(rm_context.ExportContext):
    """Super class for all RIB Mosaic panels"""

    # ### Public attributes
    COMPAT_ENGINES = {rm.ENGINE}

    panel_context = ""  # Panel's context data type
    filter_type = ()  # Only show panels for object types in tuple as:
                     # 'EMPTY', 'MESH', 'CURVE', 'SURFACE', 'TEXT', 'META',
                     # 'LAMP', 'CAMERA', 'WAVE', 'LATTICE', 'ARMATURE'
    validate_context = ""  # Valid context object such as scene, object, ect
    validate_context_type = ""  # If validating context also validate its type
    invert_filter = False  # Only show panels that DONT match filter
    invert_context = False  # Only show panels that DONT match context
    # Only show panels that DONT match context type
    invert_context_type = False

    # ### Public methods

    @classmethod
    def poll(cls, context):
        scene = context.scene
        passes = scene.ribmosaic_passes

        rd = scene.render
        show_panel = True
        if DEBUG_PRINT:
            print("RibmosaicPropertiesPanel.poll()")

        if (rd.engine in cls.COMPAT_ENGINES):
            # Sync pipeline tree with current .rmp files
            #rm.pipeline_manager.sync()

            # If filter_type check object type against filter
            if cls.filter_type and context.object:
                show_panel = context.object.type in cls.filter_type

                if cls.invert_filter:
                    show_panel = not show_panel

            # If validate_context then check context actually exists
            if cls.validate_context:
                try:
                    valid_context = eval("context." + cls.validate_context)
                except:
                    valid_context = False

                if not valid_context:
                    show_panel = False

                    if cls.invert_context:
                        show_panel = not show_panel
                elif cls.validate_context_type:
                    context_type = valid_context.type
                    show_panel = context_type == cls.validate_context_type

                    if cls.invert_context_type and context_type != 'NONE':
                        show_panel = not show_panel

            # If panel is visible and a pipeline panel then check if enabled
            if show_panel and cls.panel_context:
                # Setup active pass for export context
                passes = scene.ribmosaic_passes

                if len(passes.collection):
                    cls.pointer_pass = passes.collection[passes.active_index]

                # Setup datablock for active context
                condat = cls._context_data(cls, context, cls.panel_context)
                cls.pointer_datablock = condat['data']
                cls.context_window = condat['window']

                show_panel = cls._panel_enabled(cls)

# TODO add hooks for realtime updating of scene content to exporter here

#        # If using interactive rendering call render on panel update
#        if show_panel and scene.ribmosaic_interactive:
#            bpy.ops.render.render()

        return (rd.use_game_engine == False) and \
               (rd.engine in cls.COMPAT_ENGINES) and show_panel

    def lod_ui(self, scene, data, layout, data_search):
        """helper method to create LOD UI across several windows
           and data-blocks

        scene = current scene data-block
        layout = current panel layout
        data_search = data-block to perform prop_search on
        """

        col = layout.column(align=True)
        col.prop(data, "ribmosaic_lod")

        if data.ribmosaic_lod:
            # Force first LOD to use current data-block
            data.ribmosaic_lod_data_l1 = data.name

            for l in range(1, data.ribmosaic_lod + 1):
                col = layout.column(align=True)
                col.prop_search(data, "ribmosaic_lod_data_l" + str(l),
                                bpy.data, data_search, text="")
                sub = col.row(align=True)
                sub.prop(data, "ribmosaic_lod_range_l" + str(l))
                sub.prop(data, "ribmosaic_lod_trans_l" + str(l))

    def update_collection(self, group_property, xml_paths=[""],
                          attrs=[], window=""):
        """Populates group_property collections for the pipeline_manager with
        elements from xml path.

        group_property = group pointer property to collection to populate
        xml_paths = list of paths to elements to list in pipeline tree
        attrs = attributes in elements to include in collection
        window = window space this collection is filtered by
        """

        # Only update collections when a pipeline or window space changes
        if rm.pipeline_manager.revisions != group_property.revision or \
           group_property.window != window:
            group_property.revision = rm.pipeline_manager.revisions
            group_property.window = window
            old_collection = group_property.collection.keys()

            # Clear collection
            for i in group_property.collection:
                group_property.collection.remove(0)

            # Populate collection with elements from tree in each pipeline path
            for p in xml_paths:
                for e in rm.pipeline_manager.list_elements(p, True, attrs):
                    # Build collection attribute data
                    if attrs:
                        name = e[0]
                        element = e[1]
                    else:
                        name = e
                        element = e

                    if p:
                        path = p + "/" + element
                        pipeline = p.split("/")[0]
                    else:
                        path = element
                        pipeline = element

                    # Get element properties
                    windows = rm.pipeline_manager.get_attr(self, path,
                                                           "windows",
                                                           False, "NONE")

                    # Add item if not a panel or
                    # panel assigned to current window
                    if windows == 'NONE' or window == 'TEXT' or \
                       window in windows:
                        i = group_property.collection.add()
                        i.xmlpath = path
                        i.name = pipeline + name

            # Set collection index to item added to list
            new_collection = group_property.collection.keys()

            if new_collection != old_collection:
                for i, k in enumerate(new_collection):
                    if k not in old_collection:
                        group_property.active_index = i
                        break


class RibmosaicWarningPanel(RibmosaicPropertiesPanel):
    """Generic warning message panel"""

    # ### Public attributes

    bl_label = "RIBMOSAIC WARNING"

    warning_message = []

    # ### Public methods

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        for l in self.warning_message:
            col.label(text=l)


class RibmosaicPreviewPanel(RibmosaicPropertiesPanel):
    """Generic shader preview panel for material, lamp and world data-blocks"""

    # ### Public attributes

    bl_label = "Preview"

    # ### Public methods

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        data = self._context_data(context, self.bl_context)['data']

        if data:
            layout.template_preview(data)
            sub = layout.row()
            sub.prop(wm, "ribmosaic_preview_compile", toggle=True)
            sub.prop(wm, "ribmosaic_preview_optimize", toggle=True)
            sub = layout.row()
            sub.prop(wm, "ribmosaic_preview_samples")
            sub.prop(wm, "ribmosaic_preview_shading")

            RibmosaicRender.preview_samples = wm.ribmosaic_preview_samples
            RibmosaicRender.preview_shading = wm.ribmosaic_preview_shading
            RibmosaicRender.preview_compile = wm.ribmosaic_preview_compile
            RibmosaicRender.preview_optimize = wm.ribmosaic_preview_optimize


class RibmosaicPipelinePanels(RibmosaicPropertiesPanel):
    """Generic base class for pipeline panel control"""

    # ### Public attributes

    bl_label = "Pipeline Manager"

    # UI for text pipeline editor
    pipeline_editor = False

    # Show these pipeline element collections
    python_scripts = False
    shader_sources = False
    shader_panels = False
    utility_panels = False
    command_panels = False

    # ### Public methods
    def draw(self, context):
        wm = context.window_manager
        layout = self.layout

        # Update pipeline collection data
        self.update_collection(wm.ribmosaic_pipelines,
                               attrs=[(" - ",
                                        "'Enabled' if e.attrib['enabled'] "
                                             "== 'True' else 'Disabled'", ""),
                                      (", ",
                                        "'Library' if e.attrib['library'] "
                                             " else ''", "")])

        pipeline_len = len(wm.ribmosaic_pipelines.collection)
        index = wm.ribmosaic_pipelines.active_index

        # Clamp list index to number of items in collection
        if index > pipeline_len - 1:
            wm.ribmosaic_pipelines.active_index = pipeline_len - 1
            index = pipeline_len - 1

        # Setup number of rows based on content
        if pipeline_len:
            rows = 4
        else:
            rows = 2

        row = layout.row()
        row.operator("wm.ribmosaic_modal_sync")
        row = layout.row()
        row.template_list(wm.ribmosaic_pipelines, "collection",
                          wm.ribmosaic_pipelines, "active_index", rows=rows)
        col = row.column()
        sub = col.column(align=True)
        pan = sub.column()
        pan.operator("wm.ribmosaic_pipeline_load",
                    icon='FILE_FOLDER', text="").filepath = "//*.rmp"
        pan.operator("wm.ribmosaic_pipeline_new",
                    icon='ZOOMIN', text="").name = "New_Pipeline"

        # Only show entire UI if there's a loaded pipeline
        if pipeline_len:
            xmlpath = wm.ribmosaic_pipelines.collection[index].xmlpath

            # Get context datablock
            context_data = self._context_data(context, self.bl_context)
            window = context_data['window']
            data = context_data['data']

            # Only show prop search and operators on active datablock
            if data:
                enabled = eval(rm.pipeline_manager.get_attr(self, xmlpath,
                                                            "enabled",
                                                            False, "True"))
                library = "\"" + rm.pipeline_manager.get_attr(self, xmlpath,
                                                            "library",
                                                            False) + "\""
                build = rm.pipeline_manager.get_attr(self, xmlpath,
                                                            "build",
                                                            False)
                compile = rm.pipeline_manager.get_attr(self, xmlpath,
                                                            "compile",
                                                            False)
                pan.operator("wm.ribmosaic_pipeline_remove",
                             icon='PANEL_CLOSE', text="").pipeline = xmlpath
                pan.operator("wm.ribmosaic_pipeline_reload",
                             icon='FILE_REFRESH',
                             text="").pipeline = xmlpath
                pan.menu("WM_MT_ribmosaic_pipeline_menu",
                             icon='DOWNARROW_HLT', text="")

                row = layout.row()
                row.operator("wm.ribmosaic_library_set",
                             icon='PACKAGE',
                             text="Setup Library").pipeline = xmlpath
                row.operator("wm.ribmosaic_library_compile",
                             icon='URL',
                             text="Build Library").pipeline = xmlpath
                if enabled:
                    row.operator("wm.ribmosaic_pipeline_disable",
                             icon='CHECKBOX_HLT',
                             text="").xmlpath = xmlpath
                else:
                    row.operator("wm.ribmosaic_pipeline_enable",
                             icon='CHECKBOX_DEHLT',
                             text="").xmlpath = xmlpath

                layout.separator()
                grp = layout.column()
                grp.enabled = enabled if not self.pipeline_editor else True

                if self.pipeline_editor:
                    row = grp.row()
                    spl = row.split(percentage=0.2)
                    spl.label(text="Path:")
                    sub = spl.row(align=True)
                    sub.prop(wm, "ribmosaic_pipeline_search",
                             text="")
                    op = sub.operator("wm.ribmosaic_pipeline_search",
                                      text="",
                                      icon='VIEWZOOM')
                    op.xmlpath = wm.ribmosaic_pipeline_search
                    grp.separator()

                # Setup which collections will show
                panels = []

                if self.python_scripts:
                    panels.append(("Scripts:",
                                   'SCRIPT',
                                   "python_scripts",
                                   wm.ribmosaic_scripts,
                                   "ribmosaic_active_script",
                                   [(" - ", "e.tag", "")]))
                if self.shader_sources:
                    panels.append(("Sources:",
                                   'URL',
                                   "shader_sources",
                                   wm.ribmosaic_sources,
                                   "ribmosaic_active_source",
                                   [(" - ", "e.tag", "")]))
                if self.shader_panels:
                    panels.append(("Shaders:",
                                   'MATERIAL',
                                   "shader_panels",
                                   wm.ribmosaic_shaders,
                                   "ribmosaic_active_shader",
                                   [(" - ", "e.tag", " ")]))
                if self.utility_panels:
                    panels.append(("Utilities:",
                                   'SCRIPTWIN',
                                   "utility_panels",
                                   wm.ribmosaic_utilities,
                                   "ribmosaic_active_utility",
                                   [(" - ", "e.tag", "")]))
                if self.command_panels:
                    panels.append(("Commands:",
                                   'CONSOLE',
                                   "command_panels",
                                   wm.ribmosaic_commands,
                                   "ribmosaic_active_command",
                                   [(" - ", "e.tag", "")]))

                # Draw each collection with same basic options
                for panel in panels:
                    # Update collection for each
                    # panel category in all pipelines
                    panel_paths = [p.xmlpath + "/" + panel[2] for p in \
                                   wm.ribmosaic_pipelines.collection]
                    self.update_collection(panel[3],
                                           panel_paths,
                                           attrs=panel[5],
                                           window=window)

                    row = grp.row()
                    spl = row.split(percentage=0.2)
                    spl.label(text=panel[0])
                    sub = spl.row(align=True)
                    sub.prop_search(data, panel[4], panel[3], "collection",
                                    text="", icon=panel[1])

                    # Show UI search result otherwise show error operator
                    try:
                        search = eval("data." + panel[4])

                        # Search collection
                        path = panel[3].collection.get(search).xmlpath

                        # Change UI based on which space panel is in
                        if not self.pipeline_editor:
                            register = rm.pipeline_manager.get_attr(self,
                                                                    path,
                                                                    "register",
                                                                    False,
                                                                    "True")

                            # Change UI based on registered state
                            if eval(register):
                                e = rm.PropertyHash(path.replace("/", "") + \
                                                    "enabled")

                                # Select operator based on enabled state
                                if eval("data." + e):
                                    op = "wm.ribmosaic_panel_disable"
                                    icon = 'PINNED'
                                else:
                                    op = "wm.ribmosaic_panel_enable"
                                    icon = 'UNPINNED'

                                op = sub.operator(op, text="", icon=icon)
                                op.popup = False
                                op.xmlpath = path
                                op.context = self.bl_context
                                sub.operator("wm.ribmosaic_panel_unregister",
                                             text="",
                                             icon='LOCKVIEW_ON').xmlpath = path
                            else:
                                sub.operator("wm.ribmosaic_panel_register",
                                             text="",
                                            icon='LOCKVIEW_OFF').xmlpath = path

                            if panel[2] == "shader_panels":
                                sub.operator("wm.ribmosaic_panel_update",
                                             text="",
                                           icon='SCRIPTPLUGINS').xmlpath = path

                            op = sub.operator("wm.ribmosaic_xml_info",
                                              text="",
                                              icon='INFO')
                            op.xmlpath = path
                            op.context = self.bl_context
                            op.event = "@[ATTR:" + path + ".description:]@"
                        else:
                            op = sub.operator("wm.ribmosaic_pipeline_search",
                                              text="",
                                              icon='VIEWZOOM')
                            op.xmlpath = path
                    except:
                        op = sub.operator("wm.ribmosaic_xml_info",
                                          text="",
                                          icon='ERROR')
                        op.xmlpath = ""
                        op.context = self.bl_context
                        op.event = "Cannot find \"" + search + "\"" \
                                   " in \"" + panel[2] + "\" collection!"


# #############################################################################
# RENDER SPACE CLASSES
# #############################################################################

class RENDER_MT_ribmosaic_pass_menu(bpy.types.Menu):
    """Render pass options menu"""

    # ### Public attributes

    bl_label = "Render Pass editing"

    # ### Public methods

    def draw(self, context):
        layout = self.layout

        layout.operator("scene.ribmosaic_passes_sort", icon='FILE_REFRESH')
        layout.separator()
        layout.operator("scene.ribmosaic_passes_copy", icon='COPYDOWN')
        layout.operator("scene.ribmosaic_passes_paste", icon='PASTEDOWN')
        layout.operator("scene.ribmosaic_passes_duplicate", icon='COPY_ID')
        layout.separator()
        layout.operator("scene.ribmosaic_passes_tiles_add", icon='MESH_GRID')
        layout.operator("scene.ribmosaic_passes_tiles_del", icon='MESH_PLANE')
        layout.separator()
        layout.operator("scene.ribmosaic_passes_seq_add", icon='RENDERLAYERS')
        layout.operator("scene.ribmosaic_passes_seq_del", icon='RENDER_RESULT')


class RENDER_PT_ribmosaic_passes(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline passes control panel for render"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "RenderMan Passes"
    bl_context = "render"
    bl_options = 'DEFAULT_CLOSED'

    pass_clipboard = {}

    # ### Public methods

    def draw(self, context):
        scene = self._context_data(context, self.bl_context)['data']
        wm = context.window_manager
        ribmosaic_passes = scene.ribmosaic_passes

        active_index = ribmosaic_passes.active_index
        if len(ribmosaic_passes.collection) and (active_index >= 0):
            active_pass = ribmosaic_passes.collection[active_index]
        else:
            active_pass = None

        layout = self.layout
        row = layout.row()
        row.template_list(ribmosaic_passes, "collection", ribmosaic_passes,
                        "active_index", rows=5)

        col = row.column()
        sub = col.column(align=True)
        sub.operator("scene.ribmosaic_passes_add", icon='ZOOMIN', text="")
        sub.operator("scene.ribmosaic_passes_del", icon='ZOOMOUT', text="")
        sub.menu("RENDER_MT_ribmosaic_pass_menu",
                 icon='DOWNARROW_HLT', text="")
        col.separator()
        sub = col.column(align=True)
        sub.operator("scene.ribmosaic_passes_up", icon='TRIA_UP', text="")
        sub.operator("scene.ribmosaic_passes_down", icon='TRIA_DOWN', text="")

        row = layout.row()
        sub = row.split(percentage=0.8, align=True)

        if active_pass:
            sub.prop(active_pass, "name", text="Name")
            sub.prop(active_pass, "pass_type", text="")
            # TODO This should be moved into template_list when possible
            row.prop(active_pass, "pass_enabled", text="")

            grp = layout.column()
            grp.active = active_pass.pass_enabled

            split = grp.split()
            sub = split.column()
            sub.label(text="Output:")
            row = sub.row(align=True)
            row.prop(active_pass, "pass_display_file", text="")
            row.prop(active_pass, "pass_multilayer",
                     text="", icon='RENDERLAYERS')
            sub.separator()
            col = sub.column(align=True)
            col.prop(active_pass, "pass_shadingrate")
            col.prop(active_pass, "pass_eyesplits")
            col.prop(active_pass, "pass_gridsize")
            col.prop(active_pass, "pass_bucketsize_width")
            col.prop(active_pass, "pass_bucketsize_height")
            col.prop(active_pass, "pass_texturemem")
            sub = split.column()
            sub.label(text="Camera:")
            row = sub.row(align=True)
            if active_pass.pass_camera_group:
                row.prop_search(active_pass, "pass_camera", bpy.data, "groups")
            else:
                row.prop_search(active_pass, "pass_camera", scene, "objects")
            row.prop(active_pass, "pass_camera_group",
                     toggle=True, icon='OOPS')
            sub.separator()
            col = sub.column(align=True)
            col.prop(active_pass, "pass_camera_persp", text="")
            col.prop(active_pass, "pass_camera_lensadj")
            col.prop(active_pass, "pass_camera_nearclip")
            col.prop(active_pass, "pass_camera_farclip")

            grp.separator()
            split = grp.split()
            sub = split.column()
            sub.label(text="Samples:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_samples_x")
            col.prop(active_pass, "pass_samples_y")
            sub.label(text="Pixel Filtering:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_filter", text="", icon='FILTER')
            row = col.row(align=True)
            row.prop(active_pass, "pass_width_x")
            row.prop(active_pass, "pass_width_y")
            sub.label(text="Tile Passes:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_tile_x")
            col.prop(active_pass, "pass_tile_y")
            col.prop(active_pass, "pass_tile_index")
            sub.label(text="Sequence Passes:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_seq_width")
            col.prop(active_pass, "pass_seq_index")
            sub = split.column()
            if active_pass.pass_type != 'BEAUTY':
                sub.label(text="Resolution:")
                col = sub.column(align=True)
                col.prop(active_pass, "pass_res_x")
                col.prop(active_pass, "pass_res_y")
            sub.label(text="Aspect Ratio:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_aspect_x")
            col.prop(active_pass, "pass_aspect_y")
            sub.label(text="Frame Range:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_range_start")
            col.prop(active_pass, "pass_range_end")
            col.prop(active_pass, "pass_range_step")
            sub.label(text="Pass Control:")
            col = sub.column(align=True)
            col.prop(active_pass, "pass_subpasses")
            col.prop(active_pass, "pass_passid")

            grp.separator()
            grp.prop_search(active_pass, "pass_layerfilter",
                            scene.render, "layers")
            grp.prop(active_pass, "pass_panelfilter", icon='FILTER')
            grp.prop(active_pass, "pass_rib_string", icon='SCRIPT')


class RENDER_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for render"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "render"
    bl_options = 'DEFAULT_CLOSED'

    # ### Public methods

    def draw(self, context):
        scene = self._context_data(context, self.bl_context)['data']
        layout = self.layout

        row = layout.row()
        row.operator("scene.ribmosaic_purgerenders")
        row.operator("scene.ribmosaic_purgemaps")

        layout.prop(scene, "ribmosaic_interactive", toggle=True)

        sub = layout.column()
        sub.enabled = not scene.ribmosaic_interactive

        row = sub.row()
        row.prop(scene, "ribmosaic_activepass")
        row.prop(scene, "ribmosaic_activeobj")

        sub.separator()

        row = sub.row()
        row.prop(scene, "ribmosaic_purgeshd")
        row.prop(scene, "ribmosaic_compileshd")

        row = sub.row()
        row.prop(scene, "ribmosaic_purgetex")
        row.prop(scene, "ribmosaic_optimizetex")

        row = sub.row()
        row.prop(scene, "ribmosaic_purgerib")
        row.prop(scene, "ribmosaic_renderrib")

        row = sub.row()
        row.prop(scene, "ribmosaic_exportrib")


class RENDER_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline utility control panel for render"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    utility_panels = True

    pass


# #############################################################################
# SCENE SPACE CLASSES
# #############################################################################

class SCENE_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for scenes"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "scene"
    bl_options = 'DEFAULT_CLOSED'

    # ### Public methods

    def draw(self, context):
        scene = self._context_data(context, self.bl_context)['data']
        layout = self.layout

        row = layout.row(align=True)
        row.prop(scene, "ribmosaic_export_path")
        op = row.operator("scene.ribmosaic_exportpath",
                           icon='FILESEL', text="")
        op.filepath = "//"
        op.exportpath = "bpy.context.scene.ribmosaic_export_path"
        layout.separator()

        layout.label(text="Search Path Options")
        col = layout.box().column()
        row = col.row(align=True)
        row.prop(scene, "ribmosaic_shader_searchpath")
        op = row.operator("scene.ribmosaic_searchpath",
                          icon='FILESEL', text="")
        op.filepath = "//"
        op.searchpath = "bpy.context.scene.ribmosaic_shader_searchpath"
        row = col.row(align=True)
        row.prop(scene, "ribmosaic_texture_searchpath")
        op = row.operator("scene.ribmosaic_searchpath",
                          icon='FILESEL', text="")
        op.filepath = "//"
        op.searchpath = "bpy.context.scene.ribmosaic_texture_searchpath"
        row = col.row(align=True)
        row.prop(scene, "ribmosaic_display_searchpath")
        op = row.operator("scene.ribmosaic_searchpath",
                          icon='FILESEL', text="")
        op.filepath = "//"
        op.searchpath = "bpy.context.scene.ribmosaic_display_searchpath"
        row = col.row(align=True)
        row.prop(scene, "ribmosaic_archive_searchpath")
        op = row.operator("scene.ribmosaic_searchpath",
                          icon='FILESEL', text="")
        op.filepath = "//"
        op.searchpath = "bpy.context.scene.ribmosaic_archive_searchpath"
        row = col.row(align=True)
        row.prop(scene, "ribmosaic_procedural_searchpath")
        op = row.operator("scene.ribmosaic_searchpath",
                          icon='FILESEL', text="")
        op.filepath = "//"
        op.searchpath = "bpy.context.scene.ribmosaic_procedural_searchpath"
        row = col.row(align=True)
        row.prop(scene, "ribmosaic_resource_searchpath")
        op = row.operator("scene.ribmosaic_searchpath",
                           icon='FILESEL', text="")
        op.filepath = "//"
        op.searchpath = "bpy.context.scene.ribmosaic_resource_searchpath"
        layout.separator()

        layout.label(text="RIB Archive Options")
        col = layout.box().column()
        row = col.row()
        row.prop(scene, "ribmosaic_compressrib")
        row.prop(scene, "ribmosaic_export_threads")
        col.separator()
        row = col.row()
        row.prop(scene, "ribmosaic_object_archives")
        row = col.row()
        row.prop(scene, "ribmosaic_data_archives")
        row = col.row()
        row.prop(scene, "ribmosaic_material_archives")
        layout.separator()

        layout.label(text="Compatibility Options")
        col = layout.box().column()
        row = col.row()
        row.prop(scene, "ribmosaic_use_frame")
        row.prop(scene, "ribmosaic_use_world")
        row = col.row()
        row.prop(scene, "ribmosaic_use_screenwindow")
        row.prop(scene, "ribmosaic_use_projection")
        row = col.row()
        row.prop(scene, "ribmosaic_use_clipping")
        row.prop(scene, "ribmosaic_use_sides")
        row = col.row()
        row.prop(scene, "ribmosaic_use_bound")
        row.prop(scene, "ribmosaic_use_attribute")


class SCENE_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline utility and command control panel for scenes"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    utility_panels = True
    command_panels = True

    pass


# #############################################################################
# WORLD SPACE CLASSES
# #############################################################################

class WORLD_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for worlds"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "world"
    bl_options = 'DEFAULT_CLOSED'

    # ### Public methods

    def draw(self, context):
        ob = self._context_data(context, self.bl_context)['data']

        layout = self.layout

        sub = layout.row()

        if ob.ribmosaic_rib_archive != 'NOEXPORT':
            col = sub.column()
            col.prop(ob, "ribmosaic_mblur")
            col = col.column(align=True)
            col.active = ob.ribmosaic_mblur
            col.prop(ob, "ribmosaic_mblur_steps")
            col.prop(ob, "ribmosaic_mblur_start")
            col.prop(ob, "ribmosaic_mblur_end")

        col = sub.column()
        col.label(text="RIB Archive:")
        col.prop(ob, "ribmosaic_rib_archive", text="")


class WORLD_PT_ribmosaic_preview(RibmosaicPreviewPanel, bpy.types.Panel):
    """Pipeline shader control panel for worlds"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    validate_context = "world"

    pass


class WORLD_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline shader and utility control panel for worlds"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    validate_context = "world"
    shader_panels = True
    utility_panels = True

    pass


# #############################################################################
# OBJECT SPACE CLASSES
# #############################################################################

class OBJECT_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for objects"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "object"
    bl_options = 'DEFAULT_CLOSED'

    filter_type = ('MESH', 'CURVE', 'SURFACE', 'META', 'EMPTY', 'LAMP')
    validate_context = "object"

    # ### Public methods

    def draw(self, context):
        scene = context.scene
        ob = self._context_data(context, self.bl_context)['data']
        layout = self.layout

        if ob.type != 'LAMP' and ob.ribmosaic_rib_archive != 'NOEXPORT':
            if ob.type != 'EMPTY':
                layout.prop(ob, "ribmosaic_csg", expand=True)
                layout.separator()

        sub = layout.row()

        if ob.type != 'LAMP' and ob.ribmosaic_rib_archive != 'NOEXPORT':
            col = sub.column()
            col.prop(ob, "ribmosaic_mblur")
            col = col.column(align=True)
            col.active = ob.ribmosaic_mblur
            col.prop(ob, "ribmosaic_mblur_steps")
            col.prop(ob, "ribmosaic_mblur_start")
            col.prop(ob, "ribmosaic_mblur_end")

        col = sub.column()
        col.label(text="RIB Archive:")
        col.prop(ob, "ribmosaic_rib_archive", text="")


class OBJECT_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline shader and utility control panel for objects"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    filter_type = ('MESH', 'CURVE', 'SURFACE', 'META', 'EMPTY')
    validate_context = "object"
    shader_panels = True
    utility_panels = True

    pass


class OBJECT_PT_ribmosaic_warning1(RibmosaicWarningPanel, bpy.types.Panel):
    """Warning message for non exportable object types"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    filter_type = ('MESH', 'CURVE', 'SURFACE', 'META', 'EMPTY',
                   'LAMP', 'CAMERA')
    invert_filter = True
    validate_context = "object"
    warning_message = ["This object is ignored by exporter"]


class OBJECT_PT_ribmosaic_warning2(RibmosaicWarningPanel, bpy.types.Panel):
    """Warning message for camera object types"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    filter_type = ('CAMERA')
    validate_context = "object"
    warning_message = ["Not exported as object, use Object Data instead"]


# #############################################################################
# OBJECT DATA SPACE CLASSES
# #############################################################################

class DATA_PT_ribmosaic_preview(RibmosaicPreviewPanel, bpy.types.Panel):
    """Pipeline preview control panel for object data"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    filter_type = ('LAMP')

    pass


class DATA_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for object data"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "data"
    bl_options = 'DEFAULT_CLOSED'

    filter_type = ('MESH', 'CURVE', 'SURFACE', 'META', 'LAMP', 'CAMERA')

    # ### Public methods

    def draw(self, context):
        scene = context.scene
        ob = context.object
        layout = self.layout
        context_data = self._context_data(context, self.bl_context)
        data = context_data['data']
        search = context_data['search']

        if  data.ribmosaic_rib_archive != 'NOEXPORT':
            if ob.type != 'CAMERA' and ob.type != 'LAMP':
                layout.prop(data, "ribmosaic_primitive")

            if ob.type == 'MESH':
                sub = layout.split()
                sub.prop(data, "ribmosaic_n_export")
                row = sub.row()
                row.active = data.ribmosaic_n_export
                row.prop(data, "ribmosaic_n_class", text="")
                sub = layout.split()
                sub.prop(data, "ribmosaic_st_export")
                row = sub.row()
                row.active = data.ribmosaic_st_export
                row.prop(data, "ribmosaic_st_class", text="")
                sub = layout.split()
                sub.prop(data, "ribmosaic_cs_export")
                row = sub.row()
                row.active = data.ribmosaic_cs_export
                row.prop(data, "ribmosaic_cs_class", text="")
            elif ob.type == 'CAMERA':
                sub = layout.split()
                col = sub.column()
                col.prop(data, "ribmosaic_dof")
                col = col.column(align=True)
                col.active = data.ribmosaic_dof
                col.prop(data, "ribmosaic_f_stop")
                col.prop(data, "ribmosaic_focal_length")
                col = sub.column(align=True)
                col.label(text="Shutter:")
                col.prop(data, "ribmosaic_shutter_min")
                col.prop(data, "ribmosaic_shutter_max")
                layout.prop(data, "ribmosaic_relative_detail")

        if ob.type == 'LAMP':
            layout.prop(data, "type", expand=True)
            sub = layout.row()
            col = sub.column()
            col.prop(data, "energy")
            col.prop(data, "distance")
            col = sub.column()
            col.prop(data, "color", text="")

            if data.type == 'POINT' or data.type == 'SPOT':
                col.prop(data, "use_sphere")

            if data.type == 'SPOT':
                # Force shadow as buffer so clipping shows in view port
                #FIXME: can't write to blender data when refreshing panel
                #if data.shadow_method != 'BUFFER_SHADOW':
                #    data.shadow_method = 'BUFFER_SHADOW'

                sub = layout.split()
                col = sub.column()
                col.prop(data, "spot_size")
                col.prop(data, "spot_blend", slider=True)
                col = sub.column()
                col.prop(data, "shadow_buffer_clip_start", text="Clip Start")
                col.prop(data, "shadow_buffer_clip_end", text="Clip End")

            if data.type == 'AREA':
                layout.prop(data, "shape", expand=True)
                sub = layout.column(align=True)
                if data.shape == 'SQUARE':
                    sub.prop(data, "size", text="Size")
                elif data.shape == 'RECTANGLE':
                    sub.prop(data, "size", text="Size X")
                    sub.prop(data, "size_y", text="Size Y")

        if ob.type != 'CAMERA' and ob.type != 'LAMP':
            self.lod_ui(scene, data, layout, search)
            layout.separator()

        elif ob.type == 'LAMP' or data.ribmosaic_rib_archive != 'NOEXPORT':
            layout.separator()

        sub = layout.row()
        col = sub.column()
        col.prop(data, "ribmosaic_mblur")
        col = col.column(align=True)
        col.active = data.ribmosaic_mblur
        col.prop(data, "ribmosaic_mblur_steps")
        col.prop(data, "ribmosaic_mblur_start")
        col.prop(data, "ribmosaic_mblur_end")

        col = sub.column()
        col.label(text="RIB Archive:")
        col.prop(data, "ribmosaic_rib_archive", text="")


class DATA_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline shader and utility control panel for object data"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    filter_type = ('MESH', 'CURVE', 'SURFACE', 'META', 'LAMP', 'CAMERA')
    shader_panels = True
    utility_panels = True

    pass


class DATA_PT_ribmosaic_message(RibmosaicWarningPanel, bpy.types.Panel):
    """Warning message for non exportable data types"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    filter_type = ('MESH', 'CURVE', 'SURFACE', 'META', 'LAMP', 'CAMERA')
    invert_filter = True
    warning_message = ["This object data type is ignored by exporter"]


# #############################################################################
# MATERIAL SPACE CLASSES
# #############################################################################

class MATERIAL_PT_ribmosaic_preview(RibmosaicPreviewPanel, bpy.types.Panel):
    """Pipeline preview control panel for materials"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    validate_context = "material"

    pass


class MATERIAL_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for materials"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "material"
    bl_options = 'DEFAULT_CLOSED'

    validate_context = "material"

    # ### Public methods

    def draw(self, context):
        scene = context.scene
        mat = self._context_data(context, self.bl_context)['data']
        strand = mat.strand
        halo = mat.halo
        layout = self.layout

        if mat.ribmosaic_rib_archive != 'NOEXPORT':
            if mat.type == 'HALO':
                layout.prop(halo, "size", text="Point Size")
            elif mat.type == 'WIRE':
                layout.prop(mat, "ribmosaic_wire_size")

            sub = layout.row()
            sub.prop(mat, "ribmosaic_disp_pad")
            row = sub.row()
            row.active = mat.ribmosaic_disp_pad > 0
            row.prop(mat, "ribmosaic_disp_coor", text="")
            layout.separator()

            split = layout.split()
            sub = split.column()
            sub.prop(mat, "ribmosaic_ri_color")
            row = sub.row()
            row.active = mat.ribmosaic_ri_color
            row.prop(mat, "diffuse_color", text="")
            sub = split.column()
            sub.prop(mat, "ribmosaic_ri_opacity")
            row = sub.row()
            row.active = mat.ribmosaic_ri_opacity
            row.prop(mat, "alpha", text="Opacity")

            ### FIXME ###
            # can't modify material data block during draw call
            #if not strand.use_blender_units:
            #    strand.use_blender_units = True
            split = layout.split()
            sub = split.column(align=True)
            sub.label(text="Strand Options")
            sub.prop(strand, "shape", text="Shape")
            sub.prop(strand, "width_fade", text="Tip Fade")
            sub.label(text="Light Group:")
            sub.prop(mat, "light_group", text="")
            sub = split.column(align=True)
            sub.label(text="Strand Size")
            sub.prop(strand, "root_size", text="Root")
            sub.prop(strand, "tip_size", text="Tip")
            sub.prop(strand, "size_min", text="Minimum")
            sub.prop(mat, "use_light_group_exclusive", text="Exclusive")

        if mat.ribmosaic_rib_archive != 'NOEXPORT':
            layout.separator()

        sub = layout.row()

        col = sub.column()
        col.prop(mat, "ribmosaic_mblur")
        col = col.column(align=True)
        col.active = mat.ribmosaic_mblur
        col.prop(mat, "ribmosaic_mblur_steps")
        col.prop(mat, "ribmosaic_mblur_start")
        col.prop(mat, "ribmosaic_mblur_end")

        col = sub.column()
        col.label(text="RIB Archive:")
        col.prop(mat, "ribmosaic_rib_archive", text="")


class MATERIAL_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline shader and utility control panel for materials"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    validate_context = "material"
    shader_panels = True
    utility_panels = True

    pass


# #############################################################################
# TEXTURE SPACE CLASSES
# #############################################################################

class TEXTURE_PT_ribmosaic_preview(RibmosaicPreviewPanel, bpy.types.Panel):
    """Pipeline preview control panel for textures"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    validate_context = "texture"
    validate_context_type = 'IMAGE'

    pass


class TEXTURE_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline command control panel for textures"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    validate_context = "texture"
    validate_context_type = 'IMAGE'
    command_panels = True

    pass


class TEXTURE_PT_ribmosaic_message(RibmosaicWarningPanel, bpy.types.Panel):
    """Warning message for non Image type textures"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    validate_context = "texture"
    validate_context_type = 'IMAGE'
    invert_context_type = True
    warning_message = ["Only Image texture type supported by exporter",
                       "Use material shaders for procedural texturing"]


# #############################################################################
# PARTICLE SPACE CLASSES
# #############################################################################

class PARTICLE_PT_ribmosaic_export(RibmosaicPropertiesPanel, bpy.types.Panel):
    """Pipeline export control panel for particles"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Export Options"
    bl_context = "particle"
    bl_options = 'DEFAULT_CLOSED'

    validate_context = "particle_system"

    # ### Public methods

    def draw(self, context):
        scene = context.scene
        part = self._context_data(context, self.bl_context)['data']
        layout = self.layout

        if part.ribmosaic_rib_archive != 'NOEXPORT':
            layout.prop(part, "ribmosaic_primitive")

        self.lod_ui(scene, part, layout, "particles")
        layout.separator()

        sub = layout.row()

        col = sub.column()
        col.prop(part, "ribmosaic_mblur")
        col = col.column(align=True)
        col.active = part.ribmosaic_mblur
        col.prop(part, "ribmosaic_mblur_steps")
        col.prop(part, "ribmosaic_mblur_start")
        col.prop(part, "ribmosaic_mblur_end")

        col = sub.column()
        col.label(text="RIB Archive:")
        col.prop(part, "ribmosaic_rib_archive", text="")


class PARTICLE_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline utility control panel for particles"""

    # ### Public attributes

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"

    validate_context = "particle_system"
    utility_panels = True

    pass


# #############################################################################
# TEXT EDITOR CLASSES
# #############################################################################

class TEXT_PT_ribmosaic_panels(RibmosaicPipelinePanels, bpy.types.Panel):
    """Pipeline command control panel for texts"""

    # ### Public attributes

    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_context = "text"

    pipeline_editor = True
    python_scripts = True
    shader_sources = True
    shader_panels = True
    utility_panels = True
    command_panels = True

    pass
