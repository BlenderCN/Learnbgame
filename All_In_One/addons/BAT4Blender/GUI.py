from .Enums import *
from .Rig import *
from .LOD import *


class MainPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "BAT4Blender"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        # Create a simple row.
        layout.label(text="Rotation:")
        rot = layout.row()
        rot.prop(context.window_manager.interface_vars, 'rotation', expand=True)
        layout.label(text="Zoom:")
        zoom = layout.row()
        zoom.prop(context.window_manager.interface_vars, 'zoom', expand=True)

        self.layout.operator(Operators.PREVIEW.value[0], text="Preview")

        layout.label(text="LOD")
        lod = layout.row(align=True)
        lod.operator(Operators.LOD_FIT.value[0], text="Fit")
        lod.operator(Operators.LOD_DELETE.value[0], text="Delete")
        lod.operator(Operators.LOD_EXPORT.value[0], text="Export .3DS")

        layout.label(text="Camera")
        cam = layout.row(align=True)
        cam.operator(Operators.CAM_ADD.value[0], text="Add")
        cam.operator(Operators.CAM_DELETE.value[0], text="Delete")

        layout.label(text="Sun")
        sun = layout.row(align=True)
        sun.operator(Operators.SUN_ADD.value[0], text="Add")
        sun.operator(Operators.SUN_DELETE.value[0], text="Delete")

        layout.label(text="Render")
        render = layout.row()
        render.prop(context.scene, "group_id")
        self.layout.operator(Operators.RENDER.value[0], text="Render all zooms & rotations")


class InterfaceVars(bpy.types.PropertyGroup):
    # (unique identifier, property name, property description, icon identifier, number)
    rotation = bpy.props.EnumProperty(
        items=[
            (Rotation.NORTH.name, 'N', 'North view', '', Rotation.NORTH.value),
            (Rotation.EAST.name, 'E', 'East view', '', Rotation.EAST.value),
            (Rotation.SOUTH.name, 'S', 'South view', '', Rotation.SOUTH.value),
            (Rotation.WEST.name, 'W', 'West view', '', Rotation.WEST.value)
        ],
        default=Rotation.NORTH.name
    )

    zoom = bpy.props.EnumProperty(
        items=[
            (Zoom.ONE.name, '1', 'zoom 1', '', Zoom.ONE.value),
            (Zoom.TWO.name, '2', 'zoom 2', '', Zoom.TWO.value),
            (Zoom.THREE.name, '3', 'zoom 3', '', Zoom.THREE.value),
            (Zoom.FOUR.name, '4', 'zoom 4', '', Zoom.FOUR.value),
            (Zoom.FIVE.name, '5', 'zoom 5', '', Zoom.FIVE.value),
        ],
        default=Zoom.FIVE.name
    )