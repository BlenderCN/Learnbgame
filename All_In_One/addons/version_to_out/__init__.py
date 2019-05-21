bl_info = {
    "name": "Output from VERSION.txt",
    "author": "gabriel montagné láscaris-comneno, gabriel@tibas.london",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "description": "Sets render output from VERSION.txt file if found",
    "category": "Learnbgame",
    }

from bpy.app.handlers import persistent
from bpy.types import Panel, Scene
from bpy.props import BoolProperty
from os import path
import bpy

version_map = {}
version_file = 'VERSION.txt'

@persistent
def update_out_from_version(scene):
    global version_map

    filepath = bpy.data.filepath
    base_dir = path.dirname(filepath)

    version_path = path.join(base_dir, version_file)
    if not path.isfile(path.join(base_dir, version_path)):
        return

    base = path.basename(filepath)
    name, ext = path.splitext(base)

    basename = path.basename(scene.render.filepath)

    version = version_map.get(version_path)
    if not version:
        version_map[version_path] = version = open(version_path, 'r').read().strip()

    if scene.subfolder_per_mark:
        markers = [m for m in sorted(list(scene.timeline_markers), key=lambda m: m.frame) if m.frame <= scene.frame_current]
        if len(markers):
            last_marker = markers[-1]
            scene.render.filepath = '//target/{}/{}/{}/{}'.format(version, name, last_marker.name, basename)
        else:
            scene.render.filepath = '//target/{}/{}/{}'.format(version, name, basename)
    else:
        scene.render.filepath = '//target/{}/{}/{}'.format(version, name, basename)

class VERSION_TO_OUT_PT_config(Panel):
    bl_label = 'Version to out'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        layout = self.layout
        rd = context.scene.render
        row = layout.row()
        row.label(text='Create subfolders per mark')
        row.prop(context.scene, "subfolder_per_mark", text="")
        row = layout.row()
        row.prop(rd, "filepath", text="")

def register():
    Scene.subfolder_per_mark = BoolProperty(
        name='Nest in subfolders per mark',
        default=False)

    bpy.utils.register_class(VERSION_TO_OUT_PT_config)

    bpy.app.handlers.frame_change_pre.append(update_out_from_version)
    bpy.app.handlers.load_post.append(update_out_from_version)

def unregister():
    del Scene.subfolder_per_mark 
    bpy.app.handlers.frame_change_pre.remove(update_out_from_version)
    bpy.app.handlers.load_post.remove(update_out_from_version)
    bpy.utils.unregister_class(VERSION_TO_OUT_PT_config)

if __name__ == "__main__":
    register()
