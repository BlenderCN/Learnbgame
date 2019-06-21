import bpy


def get_all_cameras(context):
    return list(filter(
        lambda x: x.type == 'CAMERA',
        bpy.data.scenes[context.scene.name].objects
        )
    )
