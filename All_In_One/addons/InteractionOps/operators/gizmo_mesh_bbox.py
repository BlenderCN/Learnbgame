# Example of a group that edits a single property
# using the predefined gizmo arrow.
#
# Usage: Select a light in the 3D view and drag the arrow at it's rear
# to change it's energy value.
#
import bpy
from bpy.types import (
    GizmoGroup,
)


class IOPS_GIZMO(GizmoGroup):
    bl_idname = "OBJECT_GGT_mesh_test"
    bl_label = "Test Mesh BBOX Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'MESH')

    def setup(self, context):
        # Arrow gizmo has one 'offset' property we can assign to the light energy.
        ob = context.object
        mpr = self.gizmos.new("GIZMO_GT_cage_3d")
      
        #mpr.target_set_prop("dimensions", ob.data,'BBox')
        mpr.matrix_basis = ob.matrix_local
        #mpr.location = ob.location 
        mpr.scale_basis = 25.0
        #mpr.draw_style = 'BOX'
        
        mpr.select = True
        mpr.use_draw_hover = True
        mpr.use_draw_modal = True
        mpr.use_draw_offset_scale = True
        use_draw_scale = True
        use_grab_cursor = True
        use_operator_tool_properties = True
        use_select_background = True
        
        draw_select(context, select_id=0)
        #mpr.is_highlight = False
        mpr.color = 0.9, 0.9, 0.9
        mpr.alpha = 0.0

        mpr.color_highlight = 1.0, 0.0, 0.0
        mpr.alpha_highlight = 0.5
        #mpr.line_width = 2.0d
        self.bbox_widget = mpr

    def refresh(self, context):
        ob = context.object
        mpr = self.bbox_widget
        mpr.matrix_basis = ob.matrix_local
#        mpr.location = ob.location


bpy.utils.register_class(IOPS_GIZMO)
