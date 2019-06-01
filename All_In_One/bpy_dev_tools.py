bl_info = {
    'name': 'Development tools for Blender',
    'description': 'Registers operators, panels, menus etc to abet development and introspection',
    "category": "Learnbgame",
}

"""Registers operators, panels, menus etc to abet development and introspection"""

import bpy

import bpy.props

from rna_info import get_direct_properties


class BlenderTypes(object):
    base = bpy.types

    @classmethod
    def _get(cls, bclass):
        classes = []
        for typestr in dir(cls.base):
            typ = getattr(cls.base, typestr)
            if (issubclass(typ, bclass) and typ is not bclass):
                classes.append(typ)
        return classes

    @classmethod
    def headers(cls):
        base = bpy.types.Header
        return cls._get(base)

    @classmethod
    def panels(cls):
        base = bpy.types.Panel
        return cls._get(base)

    @staticmethod
    def properties():
        base = bpy.types.Property
        return base.__subclasses__()    

    @staticmethod
    def property_tags():
        properties = BlenderTypes.properties()
        return tuple([property.bl_rna.name.split()[0].upper() for property in properties])


class DebugPropTypeNoOp(bpy.types.Operator):
    bl_idname = 'debug.prop_type'
    bl_label = ''
    bl_description = ''
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        return {'FINISHED'}


def property_types_enum(self, context):
    enum_items = []
    enum_items.append(('ALL', 'All Property Definitions', ''))

    for property_type in BlenderTypes.properties():
        bl_rna = property_type.bl_rna
        name = bl_rna.name+'s'
        identifier = name.split()[0].upper()
        description = ''
        enum_items.append((identifier, name, description))

    return enum_items


class ContextSpaceData(bpy.types.Operator):
    bl_idname = 'debug.context_space_data'
    bl_label = 'Context Space Data Properties'
    bl_description = 'View the properties of the active space data'
    bl_options = {'REGISTER'}

    prop_type = bpy.props.EnumProperty(items=property_types_enum)

    def draw(self, context):
        layout = self.layout
        
        split = layout.split(percentage=0.3)
        col1 = split.column()
        col2 = split.column()
        col1.label("rna_type")
        col2.label(context.space_data.rna_type.description)
        col2.prop(context.space_data, 'rna_type')
        
        column = layout.column()
        
        prop_map = {}
        
        space_data_properties = context.space_data.rna_type.properties
        
        PropertyIdentifier = lambda prop: prop.identifier
        
        props = filter(lambda prop: prop.identifier != 'rna_type', space_data_properties)
        
        if self.prop_type != 'ALL':
            props = filter(lambda prop: prop.type == self.prop_type, props)
            prop_map[self.prop_type] = sorted(props, key=PropertyIdentifier)
        else:
            criterion = lambda prop: prop.type
        
            import itertools
            for key, group in itertools.groupby(sorted(props, key=criterion), criterion):
                prop_map[key] = sorted(group, key=PropertyIdentifier)
            
            default_prop_tags = set(BlenderTypes.property_tags())
            avail_prop_tags = set(prop_map.keys())
            missing_prop_tags = default_prop_tags - avail_prop_tags
            if missing_prop_tags:
                column.operator('debug.prop_type', text='Unavailable Property Types')
                missing_prop_tags_string = ' '.join(missing_prop_tags)
                column.label(missing_prop_tags_string)

        for key in prop_map:
            row = column.row()
            row.alert = True
            row.operator('debug.prop_type', text=key)
            if not prop_map[key]:
                column.label("No definitions available of this type")
                continue
            for prop in prop_map[key]:
                split = column.split(percentage=0.3)
                col1 = split.column()
                col2 = split.column()
                opprops = col1.operator('debug.panel_id_copy', text=prop.identifier)
                opprops.idname = prop.identifier
                col2.label(prop.description)
                col1.label('')
                col2.box().prop(context.space_data, prop.identifier)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
      
    def execute(self, context):
        return {'FINISHED'}


def ALL_HT_debug_context_draw(self, context):
    space_data = context.space_data
    space_type = space_data.type
    space_icon = space_data.bl_rna.properties['type'].enum_items[space_type].icon
    
    layout = self.layout
    row = layout.row()
    row.alert = True
    row.operator("wm.search_menu")
    row.operator_menu_enum('debug.context_space_data', 'prop_type', text="Properties", icon=space_icon)


class PanelDebugIDCopy(bpy.types.Operator):
    bl_idname = 'debug.panel_id_copy'
    bl_description = 'Copy the idname of panel to clipboard'
    bl_label = 'Copy idname'
    bl_options = {'INTERNAL'}
    
    idname = bpy.props.StringProperty(name='idname')
    
    def execute(self, context):
        context.window_manager.clipboard = self.idname
        return {'FINISHED'}


def ALL_PT_debug_identifier_draw(self, context):
    if not bpy.app.debug:
        return

    layout = self.layout
    box = layout.box()
    box.alert = True
    idname = self.bl_idname
    props = box.operator('debug.panel_id_copy', text=idname)
    props.idname = 'bpy.types.' + self.bl_idname


_operators = (
    ContextSpaceData,
    PanelDebugIDCopy,
    DebugPropTypeNoOp
)


def register():
    for operator in _operators:
        bpy.utils.register_class(operator)

    for header in BlenderTypes.headers():
        header.append(ALL_HT_debug_context_draw)
        
    for panel in BlenderTypes.panels():
        panel.prepend(ALL_PT_debug_identifier_draw)


def unregister():
    for operator in _operators:
        bpy.utils.unregister_class(operator)

    for header in BlenderTypes.headers():
        header.remove(ALL_HT_debug_context_draw)

    for panel in BlenderTypes.panels():
        panel.remove(ALL_PT_debug_identifier_draw)


if __name__ == '__main__':
    register()
