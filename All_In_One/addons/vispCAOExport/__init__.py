
bl_info = {
    "name": "ViSP CAO",
    "author": "Vikas Thamizharasan",
    "blender": (2, 7, 6),
    "location": "File > Export",
    "description": "Export CAO",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
from bpy.props import *
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )
_modules = [
    "property_panel",
    "treeview_faces",
    "treeview_lines",
    "treeview_cylinders",
    "treeview_circles"
]

__import__(name=__name__, fromlist=_modules)
_namespace = globals()
_modules_loaded = [_namespace[name] for name in _modules]
del _namespace

if "bpy" in locals():
    import imp
    if "export_cao" in locals():
        imp.reload(export_cao)
    from importlib import reload
    _modules_loaded[:] = [reload(val) for val in _modules_loaded]
    del reload

# #########################################
# ExportCAO
# #########################################

class ExportCAO(bpy.types.Operator, ExportHelper):

    bl_idname = "export_scene.cao"
    bl_label = 'Export .cao'
    bl_options = {'PRESET'}

    filename_ext = ".cao"
    filter_glob = StringProperty(
            default="*.cao",
            options={'HIDDEN'},
            )

    # context group
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    # object group
    use_mesh_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Apply modifiers (preview resolution)",
            default=True,
            )

    # extra data group
    use_edges = BoolProperty(
            name="Include Edges",
            description="",
            default=True,
            )

    use_normals = BoolProperty(
            name="Include Normals",
            description="",
            default=False,
            )

    use_triangles = BoolProperty(
            name="Triangulate Faces",
            description="Convert all faces to triangles",
            default=False,
            )

    axis_forward = EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='-Z',
            )
    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
            )
    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )


    check_extension = True

    def execute(self, context):
        from . import export_cao
        scn = context.scene
        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())
        keywords["global_matrix"] = global_matrix

        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
        except:
            pass

        print("Exporting Objects:")#TODO: hierarchical model export
        for mlist in scn.custom_faces, scn.custom_lines, scn.custom_cylinder, scn.custom_circle:
            for item in mlist: 
                if item.enabled:
                    bpy.data.objects[item.name].select = True
                    print(item.name)
        return export_cao.save(self, context, **keywords)

# #########################################
# Register
# #########################################

def menu_func_export(self, context):
    self.layout.operator(ExportCAO.bl_idname, text="ViSP .cao")

def register():
    from bpy.utils import register_class
    for mod in _modules_loaded:
        for cls in mod.classes:
            register_class(cls)
        
    bpy.types.Scene.ignit_panel = bpy.props.PointerProperty(type=_modules_loaded[0].classes[0])
    bpy.types.Scene.custom_vertices = CollectionProperty(type=_modules_loaded[0].classes[1])
    bpy.types.Scene.custom_vertices_index = IntProperty()

    bpy.types.Scene.custom_faces = CollectionProperty(type=_modules_loaded[1].classes[0])
    bpy.types.Scene.custom_faces_index = IntProperty()

    bpy.types.Scene.custom_lines = CollectionProperty(type=_modules_loaded[2].classes[0])
    bpy.types.Scene.custom_lines_index = IntProperty()

    bpy.types.Scene.custom_cylinder = CollectionProperty(type=_modules_loaded[3].classes[0])
    bpy.types.Scene.custom_cylinder_index = IntProperty()

    bpy.types.Scene.custom_circle = CollectionProperty(type=_modules_loaded[4].classes[0])
    bpy.types.Scene.custom_circle_index = IntProperty()

    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    from bpy.utils import unregister_class
    for mod in reversed(_modules_loaded):
        for cls in reversed(mod.classes):
            if cls.is_registered:
                unregister_class(cls)
    del bpy.types.Scene.custom_circle
    del bpy.types.Scene.custom_circle_index
    del bpy.types.Scene.custom_cylinder
    del bpy.types.Scene.custom_cylinder_index

    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    del bpy.types.Scene.ignit_panel

# if __name__ == "__main__":
#     register()
