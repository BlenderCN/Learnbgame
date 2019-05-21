import bpy
mat = bpy.data.materials["PM007"]
mat.name = "tmp"
mat.user_clear()
with bpy.data.libraries.load("untitled.blend") as (data_from, data_to):
 data_to.materials = ["PM007"]
mat = bpy.data.materials["PM007"]
mat.use_fake_user=True
bpy.ops.wm.save_mainfile(filepath="C:\\Users\\Dad\\Downloads\\3321_blender-2.59-39740-contrib-add-ons-fastest\\2.59\\scripts\\addons_extern\\matlib\\materials.blend", check_existing=False, compress=True)
