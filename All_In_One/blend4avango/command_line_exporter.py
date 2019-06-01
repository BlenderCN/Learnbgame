import bpy, sys

bpy.ops.export_scene.b4a_json(do_autosave = False, override_filepath=sys.argv[6])
