
import bpy

from . import operators
from . import panels
from . import properties


class OopsSchematicNodeTree(bpy.types.NodeTree):
    bl_idname = 'OopsSchematic'
    bl_label = 'OOPS Schematic'
    bl_icon = 'OOPS'


def draw_operator(self, context):
    if context.area.spaces[0].tree_type == 'OopsSchematic':
        self.layout.operator('node.oops_schematic_show')


def register_nodes_properties():
    bpy.utils.register_class(properties.OopsSchematicNodePropertyGroup)

    bpy.types.Scene.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Object.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Mesh.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Library.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Camera.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Lamp.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Material.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Texture.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.Image.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)
    bpy.types.World.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicNodePropertyGroup)


def unregister_nodes_properties():
    del bpy.types.Scene.oops_schematic
    del bpy.types.Object.oops_schematic
    del bpy.types.Mesh.oops_schematic
    del bpy.types.Library.oops_schematic
    del bpy.types.Camera.oops_schematic
    del bpy.types.Lamp.oops_schematic
    del bpy.types.Material.oops_schematic
    del bpy.types.Texture.oops_schematic
    del bpy.types.Image.oops_schematic
    del bpy.types.World.oops_schematic

    bpy.utils.unregister_class(properties.OopsSchematicNodePropertyGroup)


def register():
    register_nodes_properties()
    bpy.utils.register_class(properties.OopsSchematicClick)
    bpy.utils.register_class(properties.OopsSchematicPropertyGroup)
    bpy.types.WindowManager.oops_schematic = bpy.props.PointerProperty(type=properties.OopsSchematicPropertyGroup)
    bpy.utils.register_class(OopsSchematicNodeTree)
    bpy.utils.register_class(operators.OopsSchematicShow)
    bpy.utils.register_class(panels.OopsSchematicDisplayOptionsPanel)
    bpy.utils.register_class(panels.OopsSchematicUsedNodesPanel)
    bpy.utils.register_class(panels.OopsSchematicNodesColorsPanel)
    bpy.types.NODE_HT_header.append(draw_operator)


def unregister():
    bpy.types.NODE_HT_header.remove(draw_operator)
    bpy.utils.unregister_class(panels.OopsSchematicDisplayOptionsPanel)
    bpy.utils.unregister_class(panels.OopsSchematicUsedNodesPanel)
    bpy.utils.unregister_class(panels.OopsSchematicNodesColorsPanel)
    bpy.utils.unregister_class(operators.OopsSchematicShow)
    bpy.utils.unregister_class(OopsSchematicNodeTree)
    del bpy.types.WindowManager.oops_schematic
    bpy.utils.unregister_class(properties.OopsSchematicPropertyGroup)
    bpy.utils.unregister_class(properties.OopsSchematicClick)
    unregister_nodes_properties()
