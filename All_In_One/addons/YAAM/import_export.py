import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]

if len(argv) < 3:
    exit(-1)

filepath = argv[0]
file_type = argv[1]
png_render_filepath = argv[2]

camera_obj = None

for obj in bpy.context.scene.objects:
    if obj.type != 'CAMERA':
        obj.select_set(True)
    else:
        camera_obj = obj
    bpy.ops.object.delete()

if file_type.lower() == 'obj':
    bpy.ops.import_scene.obj(filepath=filepath)
elif file_type.lower() == 'fbx':
    bpy.ops.import_scene.fbx(filepath=filepath)

if camera_obj == None:
    bpy.ops.object.camera_add(location=(0.040998, -12.2937, 6.0491),
                              rotation=(1.1, 0, 0))

# set to EEVEE
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
# change the output to 128x128 100% resolution
bpy.context.scene.render.resolution_x = 128
bpy.context.scene.render.resolution_y = 128
bpy.context.scene.render.resolution_percentage = 100


bpy.context.scene.render.filepath = png_render_filepath
# Save the image and the file in the blend asset directory
bpy.ops.render.render(write_still=True)


