import bpy
with bpy.data.libraries.load("G:\\untitled1.blend") as (data_from, data_to):
 data_to.materials = ["Material.002"]
mat = bpy.data.materials["Material.002"]
mat.use_fake_user=True
bpy.ops.wm.save_mainfile(filepath="C:\\Users\\Dad\\Downloads\\_blender-2.58.1---39104---scripts\\2.58\\scripts\\addons_extern\\matlib\\materials.blend", check_existing=False, compress=True)
