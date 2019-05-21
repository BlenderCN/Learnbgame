import bpy

class Baebequeue_Panel(bpy.types.Panel):

    """ Panel for batch rendering"""

    bl_label = 'Render+ Batch'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
