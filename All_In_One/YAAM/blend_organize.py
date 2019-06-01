import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]

if len(argv) < 2:
    exit(-1)

blender_path = argv[0]
png_render_filepath = argv[1]

created_camera = False

if not bpy.context.scene.camera:
    bpy.ops.object.camera_add(location=(0.040998, -24.2937, 6.0491),
                              rotation=(1.1, 0, 0))
    created_camera = True
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj

print(bpy.context.scene.camera)

# store original values
res_x = bpy.context.scene.render.resolution_x
res_y = bpy.context.scene.render.resolution_y
percentage = bpy.context.scene.render.resolution_percentage
engine = bpy.context.scene.render.engine
output = bpy.context.scene.render.filepath

# set to EEVEE
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
# change the output to 128x128 100% resolution
bpy.context.scene.render.resolution_x = 128
bpy.context.scene.render.resolution_y = 128
bpy.context.scene.render.resolution_percentage = 100

bpy.context.scene.render.filepath = png_render_filepath
# Save the image and the file in the blend asset directory
bpy.ops.render.render(write_still=True)

# restore original settings
bpy.context.scene.render.resolution_x = res_x
bpy.context.scene.render.resolution_y = res_y
bpy.context.scene.render.resolution_percentage = percentage
bpy.context.scene.render.engine = engine
bpy.context.scene.render.filepath = output

if created_camera:
    for obj in bpy.context.scene.objects:
        if obj.type != 'CAMERA':
            obj.select_set(False)
        else:
            obj.select_set(True)
        bpy.ops.object.delete()
