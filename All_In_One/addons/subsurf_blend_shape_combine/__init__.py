if "bpy" in locals():
    import imp
    imp.reload(subsurf_blend_shape_combine)
else:
    from . import subsurf_blend_shape_combine

import bpy

bl_info = {
    "name" : "Subsurf Blend Shape Combine",
    "author" : "jujucub",
    "version" : (0,1), 
    "blender" : (2, 6, 5),
    "location" : "Object > Subsurf Blend Shape Combine",
    "description" : "Subsurf Blend Shape Combine",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category": "Learnbgame",
}

def menu_func(self, context):
    self.layout.operator(subsurf_blend_shape_combine.SubsurfBlendShapeCombine.bl_idname)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

# メイン関数
if __name__ == "__main__":
    register()