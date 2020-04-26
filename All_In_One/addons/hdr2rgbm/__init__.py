bl_info = {
    "name": "HDR 2 RGBM",
    "author": "Yusuf Umar, Henrik Melsom",
    "version": (0, 0, 0),
    "blender": (2, 80, 0),
    "location": "Anywhere",
    "description": "Encode (and decode) HDR image into RGBM format",
    "wiki_url": "http://twitter.com/ucupumar",
    "category": "Learnbgame",
}

import bpy, math, os
from bpy.app.handlers import persistent

# function to clamp float
def saturate(num, floats=True):
    if num < 0:
        num = 0
    elif num > (1 if floats else 255):
        num = (1 if floats else 255)
    return num 

class EncodeToRGBM(bpy.types.Operator):
    """Encodes the currently viewed HDR image to RGBM format"""
    bl_idname = "image.encode_to_rgbm"
    bl_label = "Encode HDR to RGBM"
    bl_description = "Encode HDR/float image to RGBM format. Create new image with '_RGBM.png' prefix"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.type == 'IMAGE_EDITOR' and sima.image and sima.image.is_float

    def execute(self, context):
        sima = context.space_data
        # Image
        ima = sima.image
        ima_name = ima.name

        if ima.colorspace_settings.name != 'Linear':
            ima.colorspace_settings.name = 'Linear'

        # Removing .exr or .hdr prefix
        if ima_name[-4:] == '.exr' or ima_name[-4:] == '.hdr':
            ima_name = ima_name[:-4]

        target_ima = bpy.data.images.get(ima_name + '_RGBM.png')
        if not target_ima:
            target_ima = bpy.data.images.new(
                    name = ima_name + '_RGBM.png',
                    width = ima.size[0],
                    height = ima.size[1],
                    alpha = True,
                    float_buffer = False
                    )
        
        num_pixels = len(ima.pixels)
        result_pixel = list(ima.pixels)
        
        # Encode to RGBM
        for i in range(0,num_pixels,4):
            for j in range(3):
                result_pixel[i+j] *= 1.0 / 8.0
            result_pixel[i+3] = saturate(max(result_pixel[i], result_pixel[i+1], result_pixel[i+2], 1e-6))
            result_pixel[i+3] = math.ceil(result_pixel[i+3] * 255.0) / 255.0;
            for j in range(3):
                result_pixel[i+j] /= result_pixel[i+3]
        
        target_ima.pixels = result_pixel
        
        sima.image = target_ima

        return {'FINISHED'}

def draw(self, context):
    row = self.layout.row()
    row.label(text="Convert:")
    row = self.layout.row()
    row.operator("image.encode_to_rgbm")

def register():
    bpy.utils.register_class(EncodeToRGBM)
    bpy.types.IMAGE_PT_image_properties.append(draw)

def unregister():
    bpy.types.IMAGE_PT_image_properties.remove(draw)
    bpy.utils.unregister_class(EncodeToRGBM)


@persistent
def load_node_groups(scene):
    root = bpy.utils.script_path_user()
    sep = os.sep

    # get addons folder
    filepath = root + sep + "addons"

    # Dealing with two possible name for addon folder
    dirs = next(os.walk(filepath))[1]
    folder = [x for x in dirs if x == 'hdr-2-rgbm' or x == 'hdr-2-rgbm-master'][0]

    # Node groups necessary are in nodegroups_lib.blend
    filepath = filepath + sep + folder + sep + "nodegroups_lib.blend"

    # Load node groups
    with bpy.data.libraries.load(filepath) as (data_from, data_to):

        exist_groups = [ng.name for ng in bpy.data.node_groups]
        for ng in data_from.node_groups:
            if ng not in exist_groups:
                data_to.node_groups.append(ng)

# Load decode rgbm node groups after loading blend file
bpy.app.handlers.load_post.append(load_node_groups)

if __name__ == "__main__":
    register()
