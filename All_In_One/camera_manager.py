bl_info = {
    "name": "Camera Manager",
    "category": "Learnbgame",
    "location": "View3D > Tool Shelf > Camera Manager",
    "description": "Easily switch between different cameras",
    "author": "Isaac Weaver"
}

import bpy


class CameraManagerPanel(bpy.types.Panel):
    """UI for managing and switching between cameras."""
    bl_idname = "camera_manager"
    bl_label = "Camera Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "TOOLS"
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        
        layout.label('Camera:')
        
        layout.prop(context.scene, 'active_camera', text='', icon='CAMERA_DATA')
        
        layout.prop(context.scene.camera, 'name', text='')  # icon='OBJECT_DATAMODE'


def update(scene, context):
    scene.camera = bpy.data.objects[scene.active_camera]


def get_camera_list(scene, context):
    """Return a list of all cameras in the current scene."""
    items = []
    
    for obj in scene.objects:
        if obj.type == 'CAMERA':
            items.append((obj.name, obj.name, ""))
    
    return items


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.active_camera = bpy.props.EnumProperty(
        name='Cameras',
        description='All cameras in current scene.',
        items=get_camera_list,
        update=update
    )


def unregister():
    bpy.utils.unregister_module(__name__)
    
    del bpy.types.Scene.active_camera


if __name__ == "__main__":
    register()
