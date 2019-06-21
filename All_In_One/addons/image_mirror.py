import bpy
import numpy

bl_info = {
    'name': 'Image Mirror',
    "category": "Learnbgame",
    'author': 'Taremin',
    'location': 'UV > UI > Taremin',
    'description': "Image mirroring",
    'version': [0, 0, 1],
    'blender': (2, 80, 0),
    'wiki_url': '',
    'tracker_url': '',
    'warning': '',
}

IS_LEGACY = (bpy.app.version < (2, 80, 0))
REGION = "TOOLS" if IS_LEGACY else "UI"


class UV_OT_ImageMirrorOperator(bpy.types.Operator):
    bl_idname = "uv.imagemirror"
    bl_label = '画像のミラーを行う'
    bl_description = '画像のミラーを行う'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_image = context.space_data.image
        if active_image is None:
            return {'FINISHED'}

        width, height = active_image.size
        pixels = numpy.array(active_image.pixels[:])

        print("method: {}".format(bpy.context.scene.image_mirror_method))
        method = bpy.context.scene.image_mirror_method
        mirror_func = {
            'RIGHT_TO_LEFT': [
                lambda width, height, x, y: x <= width // 2,
                lambda width, height, x, y: y * width + (width - (x + 1))
            ],
            'LEFT_TO_RIGHT': [
                lambda width, height, x, y: x >= width // 2,
                lambda width, height, x, y: y * width + (width - (x + 1))
            ],
            'TOP_TO_BOTTOM': [
                lambda width, height, x, y: y <= height // 2,
                lambda width, height, x, y: (height - (y + 1)) * width + x
            ],
            'BOTTOM_TO_TOP': [
                lambda width, height, x, y: y >= height // 2,
                lambda width, height, x, y: (height - (y + 1)) * width + x
            ],
        }
        cond, get_index = mirror_func[method]

        for idx in range(width * height):
            x = idx % width
            y = idx // width

            # mirror
            if cond(width, height, x, y):
                src_idx = get_index(width, height, x, y)
                pixels[idx * 4 + 0] = pixels[src_idx * 4 + 0]
                pixels[idx * 4 + 1] = pixels[src_idx * 4 + 1]
                pixels[idx * 4 + 2] = pixels[src_idx * 4 + 2]
                pixels[idx * 4 + 3] = pixels[src_idx * 4 + 3]

        active_image.pixels = pixels
        return {'FINISHED'}


class UV_PT_ImageMirrorPanel(bpy.types.Panel):
    bl_label = "Image Mirror"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS' if IS_LEGACY else 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, 'image_mirror_method')
        row = layout.row()
        split = layout.split()
        col = split.column(align=True)
        col.operator(UV_OT_ImageMirrorOperator.bl_idname, text="Mirror")

classes = [
    UV_OT_ImageMirrorOperator,
    UV_PT_ImageMirrorPanel
]

bpy.types.Scene.image_mirror_method = bpy.props.EnumProperty(
    items=[
        ("RIGHT_TO_LEFT", "Right To Left", "", 0),
        ("LEFT_TO_RIGHT", "Left To Right", "", 1),
        ("TOP_TO_BOTTOM", "Top To Bottom", "", 2),
        ("BOTTOM_TO_TOP", "Bottom To Top", "", 3),
    ]
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
