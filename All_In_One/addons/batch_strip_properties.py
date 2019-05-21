"""
Addon to easily copy properties of currently active strip over
to all selected strips (of same type).

Copyright (c) 2017 Krzysztof Trzcinski
"""

from bpy import types
from bpy import props
import bpy

bl_info = {
    "name": "VSE batch strip properties",
    "category": "VSE"
}

# TODO: Can I get that from somewhere instead of hardcoding?
PROXY_SIZES = (25, 50, 75, 100)
TRIBOOL = (
    ('SET', 'Set', ''),
    ('UNSET', 'Unset', ''),
    ('NO_CHANGE', 'No change', ''),
)

class ProxySettingsProperty(bpy.types.PropertyGroup):
    action = bpy.props.EnumProperty(
        items = TRIBOOL,
        description = "Proxy size",
        default = 'NO_CHANGE',
    )

class BatchStripPropertyCopy(types.Operator):
    """Batch Strip Property Copy"""
    bl_idname = "sequencer.batch_strip_property_copy"
    bl_label = "Batch Set Strip Properties"
    bl_options = {'REGISTER', 'UNDO'}
    
    set_proxy = props.EnumProperty(
        items = TRIBOOL,
        default = 'NO_CHANGE',
    )
    proxy_sizes = props.CollectionProperty(
        name='Set proxy',
        type=ProxySettingsProperty,
        description='Select properties to copy from active strip to all selected',
    )

    def check(self, event):
        return True

    def _selected_strips(self, context):
        editor = context.scene.sequence_editor
        return [
            seq
            for seq in editor.sequences_all
            if seq.select
        ]

    def _selected_move_strips(self, context):
        return [
            seq
            for seq in self._selected_strips(context)
            if seq.type == 'MOVIE'
        ]
    
    def draw(self, context):
        layout = self.layout

        enabled = str(self.set_proxy) == 'SET'

        self.selected_all = self._selected_strips(context)
        self.selected_movie_strips = self._selected_move_strips(context)

        layout.label(
            'Slected movie strips: {}/{}'.format(
                len(self.selected_movie_strips),
                len(self.selected_all)
            )
        )
        row = layout.row()
        row.label('Set Proxy')
        row.prop(self, 'set_proxy', expand=True)

        proxy_counts = {size: 0 for size in PROXY_SIZES}
        for seq in self.selected_movie_strips:
            if seq.use_proxy:
                for size in PROXY_SIZES:
                    if getattr(seq.proxy, 'build_{}'.format(size)):
                        proxy_counts[size] += 1

        for size, prop in zip(PROXY_SIZES, self.proxy_sizes):
            row = layout.row()
            row.enabled = enabled
            row.separator()
            row.label('{}%'.format(size))
            row.prop(prop, 'action', expand=True)
            row.label('{}/{}'.format(proxy_counts[size], len(self.selected_movie_strips)))

    def execute(self, context):
        if self.set_proxy == 'SET':
            for seq in self.selected_movie_strips:
                seq.use_proxy = True
                for size, prop in zip(PROXY_SIZES, self.proxy_sizes):
                    if prop.action == 'SET':
                        setattr(seq.proxy, 'build_{}'.format(size), True)
                    elif prop.action == 'UNSET':
                        setattr(seq.proxy, 'build_{}'.format(size), False)
        elif self.set_proxy == 'UNSET':
            for seq in self.selected_movie_strips:
                seq.use_proxy = False
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        for size in PROXY_SIZES:
            self.proxy_sizes.add()

        editor = context.scene.sequence_editor
        if not editor:
            return {'FINISHED'}

        return wm.invoke_props_dialog(self)

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

