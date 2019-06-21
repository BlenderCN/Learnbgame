import bpy
from bpy.utils.toolsystem import ToolDef

@ToolDef.from_fn
def hardops_mirror_tool():
    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        layout.prop(props, "radius")
    return dict(
        idname="Hardops",
        label="Hardops",
        description=(
            "This is a tooltip\n"
            "with multiple lines"
        ),
        icon="ops.transform.transform",
        widget=None,
        keymap=None,
        draw_settings=draw_settings,
    )

def hardops_tool_register():
    bpy.utils.register_tool('VIEW_3D', 'OBJECT', hardops_mirror_tool)


def hardops_tool_unregister():
    bpy.utils.unregister_tool('VIEW_3D', 'OBJECT', hardops_mirror_tool)

