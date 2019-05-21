bl_info = {
    "name": "Pie Specials",
    "description": "Specials Modes",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

import bpy
from bpy.types import Menu

# Specials Pie
class VIEW3D_PIE_SPECIALS(Menu):
    bl_idname = "pie.specials"
    bl_label = "Specials"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
#Left
        prop=pie.operator("mesh.spin", text="Duplicate Radial")
        prop.dupli=True
        prop.angle=6.28319
#Right

#Bottom
        pie.operator("mesh.subdivide_cylinder", text='Subdivide Cylinder')
        pie.operator("transform.tosphere", text="Make Round").value=1
#Top
        pie.operator("object.quickpipe", text="Quick Pipe")
        pie.operator("transform.vertex_random", text="Randomize")

#TopLeft
        split = pie.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("mesh.subdivide", text="Subdivide Smooth").smoothness=1
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("mesh.subdivide", text="Subdivide Flat").smoothness=0
        row = col.row(align=True)
        row.operator("transform.edge_crease", text="SUBD Crease ").value=1
        row.operator("transform.edge_crease", text="SUBD Un Crease").value=-1
        col.operator("object.scv_ot_draw_operator", text="Keys Viewer")
        
        
#TopRight
        pie.operator("mesh.remove_doubles", text="Remove Doubles")
        pie.operator("mesh.bridge_edge_loops", text = "Bridge Smooth").number_cuts=12
#BottomLeft
        split = pie.split()

#BottomRight

class HP_OT_subdivide_cylinder(bpy.types.Operator):
    bl_idname = "mesh.subdivide_cylinder"        # unique identifier for buttons and menu items to reference.
    bl_label = "Push And Slide"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):
        bpy.ops.mesh.edgering_select('INVOKE_DEFAULT')
        bpy.ops.mesh.loop_multi_select()
        bpy.ops.mesh.bevel(offset_type='PERCENT', offset=25, vertex_only=False)
        return {'FINISHED'}


classes = (
    VIEW3D_PIE_SPECIALS,
    HP_OT_subdivide_cylinder,
)
register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
