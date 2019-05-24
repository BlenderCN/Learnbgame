bl_info = {
    "name": "Fractals",
    "author": "corrodedHash",
    "version": (0, 3),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > Fractal",
    "description": "Adds a new fractal",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

import bpy  # NOQA

# import dragon  # NOQA
from .fractal import Fractal_add_object  # NOQA
from .dragon import DragonCurve_add_object # NOQA

# Registration


def add_dragon_button(self, context):
    self.layout.operator(
        DragonCurve_add_object.bl_idname,
        text="Dragon Curve",
        icon='PLUGIN')


def add_fractal_button(self, context):
    self.layout.operator(
        Fractal_add_object.bl_idname,
        text="Fractal",
        icon='PLUGIN')


# This allows you to right click on a button and link to the manual
def add_dragon_manual_map():
    url_manual_prefix = "http://wiki.blender.org/index.php/Doc:2.6/Manual/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "Modeling/Objects"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    # bpy.utils.register_class(dragon.DragonCurve_add_object)
    # bpy.utils.register_manual_map(add_object_manual_map)
    # bpy.types.INFO_MT_mesh_add.append(add_dragon_button)

    bpy.utils.register_class(Fractal_add_object)
    # bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.append(add_fractal_button)


def unregister():
    # bpy.utils.unregister_class(dragon.DragonCurve_add_object)
    # bpy.utils.unregister_manual_map(add_object_manual_map)
    # bpy.types.INFO_MT_mesh_add.remove(add_dragon_button)

    bpy.utils.unregister_class(Fractal_add_object)
    # bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.remove(add_fractal_button)


if __name__ == "__main__":
    register()
