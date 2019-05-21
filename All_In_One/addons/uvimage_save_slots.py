
# from http://blender.stackexchange.com/questions/31312

bl_info = {
    "name": "Render slots",
    "author": "Chebhou",
    "version": (1, 0),
    "blender": (2, 74, 0),
    "location": "UV/Image editor > Image >Save render slots",
    "description": "Saves all render slots",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}


import bpy
from bpy.types import Operator

def save(self, context):

    scene = context.scene
    path = scene.render.filepath
    ext = scene.render.file_extension
    for img in bpy.data.images :
        i = 0
        if img.type == 'RENDER_RESULT' :
            print(img.name)
            for i in range(8):
                img.render_slots.active_index = i
                try :
                    img.save_render(path+img.name+"_slot_%d"%i+ext, scene)
                    print("slot %d saved"%i)
                except :
                    print("Slot %d is empty"%i)


class save_slots(Operator):
    """Save render slots"""
    bl_idname = "image.save_all_slots"
    bl_label = "save render slots"

    def execute(self, context):

        save(self, context)

        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        save_slots.bl_idname,
        text="Save render slots",
        icon='FILE_IMAGE')

def register():
    bpy.utils.register_class(save_slots)
    bpy.types.IMAGE_MT_image.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(save_slots)
    bpy.types.IMAGE_MT_image.remove(add_object_button)

if __name__ == "__main__":
    register()
