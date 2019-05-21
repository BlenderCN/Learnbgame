import bpy
from bpy.props import StringProperty  # noqa pylint: disable=import-error, no-name-in-module

from .ModelImporter.import_scene import ImportScene


class ImportSceneOperator(bpy.types.Operator):
    """ Import an entire scene into the current blender context."""
    bl_idname = "nmsdk.import_scene"
    bl_label = "Import NMS Scene file"

    path = StringProperty(default="")

    def execute(self, context):
        importer = ImportScene(self.path, parent_obj=None, ref_scenes=dict())
        importer.render_scene()
        return importer.state


class ImportMeshOperator(bpy.types.Operator):
    """ Import one or more individual meshes from a single scene into the
    current blender context. """
    bl_idname = "nmsdk.import_mesh"
    bl_label = "Import NMS meshes"

    path = StringProperty(default="")
    mesh_id = StringProperty(default="")

    def execute(self, context):
        importer = ImportScene(self.path, parent_obj=None, ref_scenes=dict())
        importer.render_mesh(str(self.mesh_id))
        return importer.state
