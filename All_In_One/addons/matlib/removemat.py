import bpy
mat = bpy.data.materials["MatNode"]
mat.use_fake_user=False
mat.user_clear()
bpy.ops.wm.save_mainfile(filepath="D:\\Blender258\\2.58\\scripts\\addons\\matlib\\materials.blend", check_existing=False, compress=True)
