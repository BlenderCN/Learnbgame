# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/blender-color-matching


import bpy
from .color_matching import ColorMatching
from .color_matching import ColorMatchingStatic
from .b3d_lib_int.rgb import RGB


class ColorMatchAddNode(bpy.types.Operator):
    bl_idname = 'colormatch.colormatch_addnode'
    bl_label = 'Add RGB Node'
    bl_options = {'REGISTER', 'INTERNAL'}

    add_node_id = bpy.props.IntProperty(
        name='NodeId',
        min=0,
        subtype='UNSIGNED',
        default=0
    )

    def execute(self, context):
        # add RGB node to active object - active material
        if context.selected_objects:
            added = []
            for object in context.selected_objects:
                if object.active_material and object.active_material not in added:
                    if not object.active_material.use_nodes:
                        object.active_material.use_nodes = True
                    rgb_node = object.active_material.node_tree.nodes.new(type='ShaderNodeRGB')
                    rgb_node.location = (0, 0)
                    match_color = ColorMatching.matches()[self.add_node_id][0]
                    rgb_match_color = RGB.fromlist(match_color).as_linear()
                    rgb_node.outputs[0].default_value = (rgb_match_color[0], rgb_match_color[1], rgb_match_color[2], 1.0)
                    added.append(object.active_material)
        return {'FINISHED'}


class ColorMatchCopyMatchesToClipboard(bpy.types.Operator):
    bl_idname = 'colormatch.colormatch_toclipboard'
    bl_label = 'To Clipboard'
    bl_description = 'Copy search results to clipboard'
    bl_options = {'REGISTER', 'INTERNAL'}

    db = bpy.props.StringProperty(
        name='Db',
        default=''
    )
    def execute(self, context):
        matches_str = ColorMatching.matches_str(context, self.db)
        if matches_str:
            context.window_manager.clipboard = matches_str
        return {'FINISHED'}


class ColorMatch(bpy.types.Operator):
    bl_idname = 'colormatch.colormatch'
    bl_label = 'Search for closest colors:'
    bl_options = {'REGISTER', 'INTERNAL'}

    db = bpy.props.StringProperty(
        name='Db',
        default=''
    )

    def execute(self, context):
        ColorMatching.clear(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.db:
            return '{CANCELLED}'
        ColorMatching.search_by_rgb(context, self.db, RGB.fromlist(context.window_manager.colormatching_vars.source_color), ColorMatchingStatic.matching_count)
        matches = ColorMatching.matches()
        for i, match in enumerate(matches):
            context.window_manager.colormatching_colors.add()
            matchcolor = RGB.fromlist(match[0]).as_linear()
            context.window_manager.colormatching_colors[i].dest_color[0] = matchcolor[0]
            context.window_manager.colormatching_colors[i].dest_color[1] = matchcolor[1]
            context.window_manager.colormatching_colors[i].dest_color[2] = matchcolor[2]
        # show window
        return context.window_manager.invoke_popup(self, width=700)

    def draw(self, context):
        matches = ColorMatching.matches()
        row = self.layout.split(0.92)
        row.label(self.bl_label)
        row.operator('colormatch.colormatch_toclipboard', text='', icon='COPYDOWN').db = self.db
        row = self.layout.row().separator()
        row = self.layout.row()
        for i, match in enumerate(matches):
            col = row.column()
            col.label('{:<7.2%}'.format(match[2]))
            col.prop(context.window_manager.colormatching_colors[i], 'dest_color', text='')
            col.label(match[1][0])
            col.label('CMYK ' + match[1][1])
            col.operator('colormatch.colormatch_addnode').add_node_id = i

    def check(self, context):
        return True

    def cancel(self, context):
        self.execute(context)


def register():
    bpy.utils.register_class(ColorMatch)
    bpy.utils.register_class(ColorMatchAddNode)
    bpy.utils.register_class(ColorMatchCopyMatchesToClipboard)


def unregister():
    bpy.utils.unregister_class(ColorMatchCopyMatchesToClipboard)
    bpy.utils.unregister_class(ColorMatchAddNode)
    bpy.utils.unregister_class(ColorMatch)
