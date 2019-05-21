# <pep8 compliant>


bl_info = {
    "name": "Control positioning of Area Headers",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "Operator Search Menu -> Make Area Headers Consistent",
    "description": "Move all headers to the top/or bottom in all areas of the current screen",
    "warning": "",
    "category": "Learnbgame"
}


"""Display Area Spaces in Header"""


import bpy


def main(self, context):
    window = context.window
    screen = window.screen

    where_is_header = lambda area: 'BOTTOM' if area.y == area.regions[0].y else 'TOP'

    for area in screen.areas:
        if self.header_to != where_is_header(area):
            if bpy.app.debug:
                print("Flipping header for {0}".format(area.spaces.active.type))

            overrides = {
                'window':window,
                'screen':screen,
                'area': area,
                'region':area.regions[0]
            }

            bpy.ops.screen.header_flip(overrides)


class AreaHeadersConsistentOperator(bpy.types.Operator):
    """Position the Area Headers consistently"""
    bl_idname = "screen.area_headers_consistent"
    bl_label = "Make Area Headers Consistent"
    bl_options = {'REGISTER', 'UNDO'}

    items = [('TOP', 'Top', 'Header on top'), ('BOTTOM', 'Bottom', 'Header at Bottom')]

    header_to = bpy.props.EnumProperty(items=items, default='TOP', name="Header Location")

    def invoke(self, context, event):
        main(self, context)
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AreaHeadersConsistentOperator)


def unregister():
    bpy.utils.unregister_class(AreaHeadersConsistentOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.screen.area_headers_consistent()
