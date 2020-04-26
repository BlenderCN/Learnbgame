import bpy
from ..common import *
from .. import tools

class RevoltHullPanel(bpy.types.Panel):
    bl_label = "Hulls"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"
    bl_options = {"DEFAULT_CLOSED"}

    # @classmethod
    # def poll(self, context):
    #     return context.object and len(context.selected_objects) >= 1 and context.object.type == "MESH"

    def draw_header(self, context):
        self.layout.label("", icon="BBOX")

    def draw(self, context):
        view = context.space_data
        obj = context.object
        props = context.scene.revolt
        layout = self.layout

        layout.operator("hull.generate", icon="BBOX")
        layout.operator("object.add_hull_sphere", icon="MATSPHERE", text="Create Hull Sphere")

    
class ButtonHullGenerate(bpy.types.Operator):
    bl_idname = "hull.generate"
    bl_label = "Generate Convex Hull"
    bl_description = (
        "Generates a convex hull from the selected object"
    )

    def execute(self, context):
        tools.generate_chull(context)
        return{"FINISHED"}


class OBJECT_OT_add_revolt_hull_sphere(bpy.types.Operator):
    bl_idname = "object.add_hull_sphere"
    bl_label = "Hull Sphere"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        from ..hul_in import create_sphere
        obj = create_sphere(context.scene, (0, 0, 0), to_revolt_scale(0.1), "Hull Sphere")
        obj.location = bpy.context.scene.cursor_location
        obj.select = True
        bpy.context.scene.objects.active = obj

        return {'FINISHED'}