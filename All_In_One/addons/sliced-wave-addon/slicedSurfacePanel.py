import bpy


class SlicedSurfacePanel(bpy.types.Panel):
    bl_idname = "panel.sliced_surface_panel"
    bl_label = 'SlicedSurface'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Sliced Surface'
    bl_options = set()

    @classmethod
    def poll(self, context):
        return (context.mode == 'OBJECT'
                and (context.active_object is not None)
                and (context.active_object.sliced_surface is not None)
                and context.active_object.sliced_surface.sliced_surface)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object.sliced_surface

        layout.label('Surface Settings')

        col = layout.column(align=True)
        col.prop(obj, 'nSlices')
        col.prop(obj, 'nRes')
        col.prop(obj, 'slice')

        col = layout.column(align=True)
        col.prop(obj, 'seed')
        col.prop(obj, 'amplitude')
        col.prop(obj, 'maxFreq')
        col.prop(obj, 'numWaves')
        col.prop(obj, 'offset')

        layout.label('Export SVG')
        col = layout.column(align=True)
        col.prop(obj, 'height')
        col.prop(obj, 'width')
        col.prop(obj, 'depth')
        col.prop(obj, 'sliceDepth')

        col = layout.column(align=True)
        col.prop(obj, 'canvasWidth')
        col.prop(obj, 'canvasHeight')

        layout.operator('mesh.export_sliced_surface')

def register():
    bpy.utils.register_class(SlicedSurfacePanel)
    print('slicedSurfacePanel.py registered')

def unregister():
    bpy.utils.unregister_class(SlicedSurfacePanel)
    print('slicedSurfacePanel.py unregistered')
