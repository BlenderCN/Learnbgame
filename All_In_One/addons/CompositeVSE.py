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


# todo: automatically show composites before rendering, but store value of bool_show_compositions to revert after render

# TODO: Correctly handle image sequences which start at a frame number >0. The correct offset has to be set.

bl_info = {
    "name": "Edit Strip With Compositor REMAKE f",
    "description": "Send one or more Sequencer strips to the Compositor, gently",
    "author": "Carlos Padial, TMW, Björn Sonnenschein",
    "version": (0, 14),
    "blender": (2, 78),
    "location": "Sequencer > UI panel, Node Editor > UI panel",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Learnbgame"
}

import bpy, os

from bpy.props import (IntProperty,
                       FloatProperty,
                       EnumProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty,
                       )


# common functions

def switch_screen(context, eswc_screen):
    # get the name of the desired composite screen
    for index, screen in enumerate(bpy.data.screens):
        if index == int(eswc_screen):
            screen_name = screen.name
            break

    # change current screen to the composite screen
    for screen in bpy.data.screens:
        bpy.ops.screen.screen_set(delta=1)
        if context.screen.name == screen_name:
            break


def select_only_strip(strip):
    # deselect all strips and select only the composite strip
    # todo: more elegant way to do this?
    bpy.ops.sequencer.select_all(action='SELECT')
    for i in bpy.context.selected_editable_sequences:
        if i.name != strip.name:
            i.select = False
    bpy.context.scene.sequence_editor.active_strip = strip
    bpy.context.scene.update()


def create_strip_for_composition(strip_composition):
    eswc_info_composite = strip_composition.scene.eswc_info
    path_input = eswc_info_composite.path_input

    # deselect all other strips
    bpy.ops.sequencer.select_all(action='DESELECT')

    new_strip = None
    if eswc_info_composite.type_original_strip == 'MOVIE':
        bpy.ops.sequencer.movie_strip_add(filepath=path_input, replace_sel=True, sound=False)
        bpy.context.scene.update()
        new_strip = bpy.context.scene.sequence_editor.active_strip
    elif eswc_info_composite.type_original_strip == 'IMAGE':
        # todo: respect files. For this, a new string prop collection holding all files
        # of the source image strip must be added to composition scene.
        # also, the check if a scene already corresponds to an image strip then also has to compare
        # this list of files because if other files are used, it is not the same source albeit
        # it referes to the same directory.
        bpy.ops.sequencer.image_strip_add(directory=path_input, replace_sel=True)
        bpy.context.scene.update()
        new_strip = bpy.context.scene.sequence_editor.active_strip

    if new_strip is not None:
        new_strip.composite_scene = strip_composition.scene.name
        S_CompOperator.replace_strip(strip_composition, new_strip, bpy.context)
    else:
        print({'ERROR_INVALID_INPUT'}, 'The following composite strip refers to an invalid strip type:'
                                       ' {}'.format(strip_composition.name))

    return new_strip


# function to toggle showing the compositions
def toggle_composition_visibility(self, context):
    # store strips first because direct iteration doesn't work when modifying strips
    strips = [strip for strip in bpy.context.scene.sequence_editor.sequences_all]

    for strip in strips:
        # if show compositions, replace the movie and image strips with their compositions
        if bpy.context.scene.eswc_info.bool_show_compositions:
            if strip.type in ['MOVIE', 'IMAGE']:
                if strip.composite_scene != "":
                    composite_scene = bpy.data.scenes[strip.composite_scene]
                    S_CompOperator.insert_scene_timeline(composite_scene, strip, bpy.context)
        # if not show compositions, the compositions are to be replaced by the movie strips
        elif strip.type == 'SCENE' and strip.scene.eswc_info.path_input != "":
            new_strip = create_strip_for_composition(strip)


# ----------------------------------------------------------------------------
# Persistent Scene Data Types for Edit Strip With Compositor addon (eswc_info)

class ESWC_Info(bpy.types.PropertyGroup):
    bool_show_options = BoolProperty(
        name="Show options",
        description="Show options",
        default=False)

    bool_add_scale = BoolProperty(
        name="Add Scale node",
        description="Add Scale node",
        default=False)

    # todo: implement update function
    bool_show_compositions = BoolProperty(
        name="Show composite strips",
        description="If activated, the composite are shown in the timeline. Otherwise, the source videos are visible.",
        default=True,
        update=toggle_composition_visibility)

    bool_reuse_compositions = BoolProperty(
        name="Reuse compositions",
        description="When creating compositions for strips, reuse existing compositions that use the same source",
        default=True)

    bool_add_viewer = BoolProperty(
        name="Add Viewer",
        description="You can add a viewer node to the new compositions \
        automatically",
        default=True)

    bool_add_group = BoolProperty(
        name="Add Nodegroup",
        description="You can add a custom node group to the new compositions \
        automatically",
        default=False)

    # the input path of the movie file the composition was created from
    # if it is empty, the operators infer that the current scene
    # is not a composition.
    path_input = StringProperty(
        name="Movie strip input",
        default="",
        description="the input path of the movie file the composition was \
            created from")

    # store original strip type so that a strip can be created from the composition
    type_original_strip = StringProperty(
        name="Original strip type",
        default="",
        description="Type of the strip associated with this composition")

    bool_auto_proxy = BoolProperty(
        name="Automatic proxy settings",
        description="The new scene will automatically create and use a proxy \
        custom directory in the project directory, 100% proxy will be \
        generated by default. ",
        default=False)

    selections = [("All", "All", "Copy all settings"),
                  # ( "Select", "Select", "Copy selected settings" ),
                  ("None", "None", "Copy none of the settings")]
    settings = EnumProperty(
        name="Settings Type",
        items=selections,
        default="All",
        description="Choose which settings to copy from the source clip to the created composition")

    proxy_qualities = [("1", "25%", ""), ("2", "50%", ""),
                       ("3", "75%", ""), ("4", "100%", "")]
    pq = EnumProperty(
        name="Proxy Quality", items=proxy_qualities,
        default="1",
        description="Quality setting for auto proxies")

    master_scene = StringProperty(
        name="Master Scene",
        description="This is the name of the Scene's Master Scene",
        default="Scene")

    scene_init_comp = BoolProperty(name="",
                                   description="",
                                   default=False)

    # col_node_groups = CollectionProperty(type=StringColl)

    def avail_nodegroups(self, context):
        items = []
        for i, node_group in enumerate(bpy.data.node_groups):
            items.append((str(i), node_group.name, node_group.name))
        return items

    enum_node_groups = EnumProperty(items=avail_nodegroups,
                                    name="Node Group")

    def avail_screens(self, context):
        items = []
        for i, elem in enumerate(bpy.data.screens):
            items.append((str(i), elem.name, elem.name))
        return items

    enum_edit_screen = EnumProperty(items=avail_screens,
                                    name="Editing Screen")

    enum_comp_screen = EnumProperty(items=avail_screens,
                                    name="Compositing Screen")


class CompPanel(bpy.types.Panel):
    bl_label = "Edit strip with Compositor"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.sequence_editor is not None

    def draw(self, context):
        scn = context.scene
        activestrip = scn.sequence_editor.active_strip
        layout = self.layout
        # try:
        eswc_info = scn.eswc_info
        if activestrip is not None:
            if activestrip.type == "SCENE":
                layout.operator("sequencer.eswc_switch_to_composite")
            if activestrip.type in {"MOVIE", "IMAGE"}:
                layout.operator("sequencer.eswc_single_comp")

        layout.prop(eswc_info, "bool_show_options")
        if eswc_info.bool_show_options:
            box = layout.box()
            col = box.column(align=True)
            col.prop(eswc_info, "settings")
            col.prop(eswc_info, "bool_show_compositions")
            col.prop(eswc_info, "bool_reuse_compositions")
            col.prop(eswc_info, "bool_add_viewer")
            col.prop(eswc_info, "bool_add_scale")

            col.prop(eswc_info, "bool_auto_proxy")
            if eswc_info.bool_auto_proxy:
                col.prop(eswc_info, "pq")

            if len(bpy.data.node_groups) != 0:
                col.prop(eswc_info, "bool_add_group")
                if eswc_info.bool_add_group:
                    # node group selector
                    col.prop(eswc_info, "enum_node_groups")

            box = layout.box()
            col = box.column(align=True)

            # comp screen selector
            col.prop(eswc_info, "enum_comp_screen")

            # editing screen selector
            col.prop(eswc_info, "enum_edit_screen")


class NodePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Edit strip with Compositor"

    def draw(self, context):
        scn = context.scene
        try:
            layout = self.layout
            row = layout.row()
            col = row.column()
            try:
                col.operator("node.eswc_switch_back_to_timeline")
                col.operator("node.eswc_switch_to_composite_nodepanel")
            except KeyError:
                pass
        except AttributeError:
            pass


class Switch_to_Composite_Operator(bpy.types.Operator):
    bl_idname = "sequencer.eswc_switch_to_composite"
    bl_label = "Edit Composition"

    def invoke(self, context, event):
        if context.scene.sequence_editor.active_strip.type == 'SCENE':
            stripscene = context.scene.sequence_editor.active_strip.scene
            scn = context.scene

            eswc_info = scn.eswc_info
            switch_screen(context, eswc_info.enum_comp_screen)
            context.screen.scene = stripscene

            try:
                viewer = context.scene.node_tree.nodes['Viewer']
                context.scene.node_tree.nodes.active = viewer
            except KeyError:
                pass
            context.scene.frame_current = context.scene.frame_start

        return {'FINISHED'}


class Switch_to_Composite_Nodepanel_Operator(bpy.types.Operator):
    bl_idname = "node.eswc_switch_to_composite_nodepanel"
    bl_label = "Edit Composition"

    def invoke(self, context, event):
        master_scene = bpy.data.scenes[context.scene.eswc_info.master_scene]

        if master_scene.sequence_editor.active_strip.type == 'SCENE':
            target_scene = master_scene.sequence_editor.active_strip.scene
            eswc_info = master_scene.eswc_info

            switch_screen(context, eswc_info.enum_comp_screen)
            context.screen.scene = target_scene

            try:
                viewer = context.scene.node_tree.nodes['Viewer']
                context.scene.node_tree.nodes.active = viewer
            except KeyError:
                pass
            context.scene.frame_current = context.scene.frame_start

        return {'FINISHED'}


class Switch_back_to_Timeline_Operator(bpy.types.Operator):
    bl_idname = "node.eswc_switch_back_to_timeline"
    bl_label = "Get Back"

    def invoke(self, context, event):
        scn = bpy.data.scenes[context.scene.eswc_info.master_scene]

        # this is to avoid errors when changing percentage for preview render...
        context.scene.render.resolution_percentage = 100

        eswc_info = scn.eswc_info
        switch_screen(context, eswc_info.enum_edit_screen)
        context.screen.scene = scn

        return {'FINISHED'}

        # ---------------------------------------------------------------------


class S_CompOperator(bpy.types.Operator):
    bl_idname = "sequencer.eswc_single_comp"
    bl_label = "Create Comp from strips"

    def copy_render_settings(self, scene_a, scene_b):
        '''
        Copy render settings for scene A to match original scene B
        '''
        scene_a.render.resolution_x = scene_b.render.resolution_x
        scene_a.render.resolution_y = scene_b.render.resolution_y
        # scene_a.render.resolution_percentage = scene_b.render.resolution_percentage
        scene_a.render.fps = scene_b.render.fps
        path = bpy.path.abspath(os.path.join("//Comp", scene_a.name + "/" + scene_a.name))
        scene_a.render.filepath = bpy.path.relpath(path)

    def copy_comp_render_settings(self, scene_a, scene_b):
        # copy compositor render settings
        scene_a.node_tree.use_opencl = scene_b.node_tree.use_opencl
        scene_a.node_tree.two_pass = scene_b.node_tree.two_pass
        scene_a.node_tree.render_quality = scene_b.node_tree.render_quality
        scene_a.node_tree.edit_quality = scene_b.node_tree.edit_quality
        scene_a.node_tree.chunk_size = scene_b.node_tree.chunk_size

    @staticmethod
    def copy_all_settings(scene_a, scene_b):
        '''
        Copy all listed settings for scene strip A scene_a.node_tree.use_opencl
        to match original scene strip B
        '''
        # scene_a.use_translation =  scene_b.use_translation
        scene_a.use_reverse_frames = scene_b.use_reverse_frames
        scene_a.use_float = scene_b.use_float
        scene_a.use_flip_y = scene_b.use_flip_y
        scene_a.use_deinterlace = scene_b.use_deinterlace
        scene_a.use_default_fade = scene_b.use_default_fade
        scene_a.strobe = scene_b.strobe
        scene_a.speed_factor = scene_b.speed_factor
        scene_a.mute = scene_b.mute
        scene_a.lock = scene_b.lock
        scene_a.effect_fader = scene_b.effect_fader
        scene_a.color_saturation = scene_b.color_saturation
        scene_a.color_multiply = scene_b.color_multiply
        scene_a.blend_type = scene_b.blend_type
        scene_a.blend_alpha = scene_b.blend_alpha
        scene_a.use_flip_x = scene_b.use_flip_x

    @staticmethod
    def setup_proxy(strip, eswc_info, new_name):
        strip.use_proxy = True
        if (eswc_info.pq == "1"):
            strip.proxy.build_25 = True
        else:
            strip.proxy.build_25 = False
        if (eswc_info.pq == "2"):
            strip.proxy.build_50 = True
        else:
            strip.proxy.build_50 = False
        if (eswc_info.pq == "3"):
            strip.proxy.build_75 = True
        else:
            strip.proxy.build_75 = False
        if (eswc_info.pq == "4"):
            strip.proxy.build_100 = True
        else:
            strip.proxy.build_100 = False
        strip.use_proxy_custom_directory = True
        name = new_name
        proxy_folder = bpy.path.abspath("//.proxy")
        new_folder = os.path.join(proxy_folder, name)
        rel_folder = bpy.path.relpath(new_folder)
        strip.proxy.directory = rel_folder
        strip.proxy.quality = 90

    def create_composition_for_strip(self, original_strip, context):
        # Creates new scene but doesn't set it as active.
        # attention: new_scene_name may be != new_scene.name, if scene of same name already exists.
        new_scene_name = '{}{}'.format('Comp_', original_strip.name)
        new_scene = bpy.data.scenes.new(new_scene_name)

        editing_scene = context.scene
        eswc_info_editing = editing_scene.eswc_info

        # Change render settings for new scene to match original scene
        self.copy_render_settings(new_scene, editing_scene)

        # set render resolution to full so that scaling is done in sequencer
        new_scene.render.resolution_percentage = 100

        # Setup new scene EndFrame to match original_strip length
        new_scene.frame_end = original_strip.frame_final_duration + original_strip.frame_offset_start + original_strip.frame_offset_end

        # Setup nodes
        new_scene.use_nodes = True

        self.create_node_tree_for_strip(new_scene, original_strip, eswc_info_editing)

        new_scene.eswc_info.master_scene = editing_scene.name
        new_scene.eswc_info.type_original_strip = original_strip.type
        new_scene.eswc_info.path_input = self.get_filepath_strip(original_strip)

        context.screen.scene.update()

        return new_scene

    @classmethod
    def insert_scene_timeline(cls, new_scene, original_strip, context):

        # deselect all other strips
        bpy.ops.sequencer.select_all(action='DESELECT')
        context.scene.sequence_editor.active_strip = None

        # Add newly created scene to the timeline
        # if view comps mode, replace the movie strip with the scene strip.
        # else, assign the composition name to the movie strip
        bpy.ops.sequencer.scene_strip_add(
            frame_start=original_strip.frame_start,
            replace_sel=True, scene=new_scene.name)

        context.scene.update()

        # make composite strip  active
        # todo: is this really the correct way to get the newly created strip?
        composite_strip = context.scene.sequence_editor.active_strip

        cls.replace_strip(original_strip, composite_strip, context)

    @classmethod
    def replace_strip(cls, strip_to_replace, strip_replacement, context):
        eswc_info = context.scene.eswc_info

        name_strip = strip_to_replace.name

        # Update scene
        context.scene.update()

        # # Camera override
        # todo: this in insert_scene_timeline?
        # strip_replacement.scene_camera = editing_scene.camera

        context.scene.update()

        # Copy Settings
        if eswc_info.settings == "All":
            cls.copy_all_settings(strip_replacement, strip_to_replace)

        if eswc_info.bool_auto_proxy:
            a = strip_replacement
            cls.setup_proxy(a, eswc_info, strip_replacement.name)

        # if any strips use the strip to replace as input, set input to new strip
        for sequence in context.scene.sequence_editor.sequences_all:
            if hasattr(sequence, 'input_1') and sequence.input_1 == strip_to_replace:
                sequence.input_1 = strip_replacement
            if hasattr(sequence, 'input_2') and sequence.input_2 == strip_to_replace:
                sequence.input_2 = strip_replacement

        channel = strip_to_replace.channel
        frame_start = strip_to_replace.frame_start
        offset_start = strip_to_replace.frame_offset_start
        offset_end = strip_to_replace.frame_offset_end

        # delete the strip
        select_only_strip(strip_to_replace)
        bpy.ops.sequencer.delete()

        # set the correct channel and name
        strip_replacement.name = name_strip

        strip_replacement.frame_offset_start = offset_start
        strip_replacement.frame_offset_end = offset_end
        strip_replacement.frame_start = frame_start

        strip_replacement.channel = channel

    def create_node_tree_for_strip(self, new_scene, strip, eswc_info):
        # copy_comp_render_settings(new_scene, cur_scene)
        node_tree = new_scene.node_tree

        # Clear default nodes
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        # Create input node
        image_node = node_tree.nodes.new('CompositorNodeImage')
        image_node.location = 0, 0

        if strip.type == 'IMAGE':
            # Find extension
            full_name = strip.elements[0].filename
            extension = os.path.splitext(full_name)[1]

            # Get source of strip and add strip path
            clean_path = bpy.path.abspath(strip.directory)
            files = []
            for file in os.listdir(clean_path):
                if file.endswith(extension):
                    files.append(file)
            path = os.path.join(clean_path, full_name)
            # Check for existing image datablocks for this item
            bool_create_new = True
            for image in bpy.data.images:
                if image.name == full_name:
                    strip_source = bpy.data.images[full_name]
                    bool_create_new = False

            # or create a new one
            if bool_create_new:
                strip_path = bpy.path.resolve_ncase(path)
                strip_source = bpy.data.images.load(strip_path)
                strip_source.source = 'SEQUENCE'
            image_node.image = strip_source

            image_node.image.source = 'SEQUENCE'
            image_node.frame_duration = len(files)

        elif strip.type == 'MOVIE':
            # Get source of strip and add strip path
            strip_path = strip.filepath

            # Check for existing image datablocks for this item
            bool_create_new = True
            D = bpy.data
            for file in D.images:
                if file.filepath == strip_path:
                    strip_source = bpy.data.images[file.name]
                    bool_create_new = False
            # or create a new one
            if bool_create_new:
                strip_source = bpy.data.images.load(strip_path)
                strip_source.source = 'MOVIE'
            image_node.image = strip_source

        # Other input settings
        # length shall be original movie length.
        # todo: is this necessary? Doesn't the strip have the duration by default?
        # todo: why set frame offset?
        image_node.frame_duration = strip.frame_final_duration + \
                                    strip.frame_offset_start + strip.frame_offset_end + \
                                    strip.animation_offset_end
        image_node.frame_offset = strip.animation_offset_start

        image_node.use_cyclic = False
        image_node.use_auto_refresh = True

        # Update scene
        new_scene.update()

        new_scene.frame_current = 2

        # create scale node
        if eswc_info.bool_add_scale:
            scale = node_tree.nodes.new('CompositorNodeScale')
            scale.space = "RENDER_SIZE"
            scale.location = 180, 0

        # create group node
        if eswc_info.bool_add_group:
            group_exists = False
            nodegroup = ""

            for file, elem in enumerate(bpy.data.node_groups):
                if file == int(eswc_info.enum_node_groups):
                    group_exists = True
                    nodegroup = elem
                    break

            if group_exists == True:
                group = node_tree.nodes.new('CompositorNodeGroup')
                group.node_tree = nodegroup
                group.location = 350, 0

        # create comp and viewer output node
        comp = node_tree.nodes.new('CompositorNodeComposite')
        if eswc_info.bool_add_group and group_exists:
            comp.location = 600, 0
        else:
            comp.location = 400, 0
        if eswc_info.bool_add_viewer:
            viewer = node_tree.nodes.new('CompositorNodeViewer')
            reroute = node_tree.nodes.new('NodeReroute')
            if eswc_info.bool_add_group and group_exists:
                reroute.location = 550, -150
                viewer.location = 600, -200
            else:
                reroute.location = 350, -150
                viewer.location = 400, -200

        # Link nodes
        links = node_tree.links
        if not eswc_info.bool_add_viewer:
            if eswc_info.bool_add_group and group_exists:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], comp.inputs[0])
                else:
                    link = links.new(image_node.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], comp.inputs[0])
            else:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], comp.inputs[0])
                else:
                    link = links.new(image_node.outputs[0], comp.inputs[0])
        else:
            link = links.new(reroute.outputs[0], viewer.inputs[0])
            link = links.new(reroute.outputs[0], comp.inputs[0])
            if eswc_info.bool_add_group == True and group_exists == True:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], reroute.inputs[0])

                else:
                    link = links.new(image_node.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], reroute.inputs[0])
            else:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], reroute.inputs[0])
                else:
                    link = links.new(image_node.outputs[0], reroute.inputs[0])

    @classmethod
    def find_matching_compositions(cls, strip):
        result = []
        for scene in bpy.data.scenes:
            if scene.eswc_info.path_input == cls.get_filepath_strip(strip):
                result.append(scene)

        return result

    @staticmethod
    def get_filepath_strip(strip):
        if strip.type == 'IMAGE':
            return strip.directory

        elif strip.type == 'MOVIE':
            # Get source of strip and add strip path
            return strip.filepath

    def invoke(self, context, event):
        eswc_info = context.scene.eswc_info

        selected_strips = context.selected_sequences

        # Loop selected strips
        names_strips_failed = []
        for strip in selected_strips:

            # Check if strip is a movie
            if strip.type in ['MOVIE', 'IMAGE']:

                # create a new composition if no composition exists or if one or more compositions exist and
                # option to create new compositions is activated.
                # generate the composition
                reuse_compositions = eswc_info.bool_reuse_compositions
                matching_compositions = self.find_matching_compositions(strip)
                if len(matching_compositions) == 0 or not reuse_compositions:
                    comp_scene = self.create_composition_for_strip(strip, context)
                elif len(matching_compositions) == 1 and reuse_compositions:
                    # If only one compostion exists for the source, it can be reused
                    comp_scene = matching_compositions[0]
                else:
                    names_strips_failed.append(strip.name)
                    continue

                # insert the strip into the scene in place of the original if composite strips are to be shown.
                # else, set the name of the scene
                if eswc_info.bool_show_compositions:
                    self.insert_scene_timeline(new_scene=comp_scene, original_strip=strip, context=context)
                else:
                    strip.composite_scene = comp_scene.name

            else:
                print("Active Strip is not a movie or an image sequence.")

        if len(names_strips_failed) > 0:
            self.report({'ERROR_INVALID_INPUT'}, 'The following strips could not be converted because more than one'
                                                 'composite scenen with the same source exists and \"Reuse Composition\"'
                                                 'is activated: {}'.format(str(names_strips_failed)))
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

    # eswc_info
    bpy.types.Scene.eswc_info = PointerProperty(type=ESWC_Info)

    # strip composite scene name; used to interchange movies and composites
    bpy.types.ImageSequence.composite_scene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )
    bpy.types.MovieSequence.composite_scene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )
    # todo: MovieClip sequences are not supported yet.
    bpy.types.MovieClipSequence.composite_scene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )


def unregister():
    bpy.utils.unregister_module(__name__)

    # eswc_info
    del bpy.types.Scene.eswc_info


if __name__ == "__main__":
    register()
