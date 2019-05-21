"""
 RexExportModule: Export to tundra format
"""
import math
import os
import uuid

from .base import SyncModule

import b2rexpkg.tools.rexio.export
from b2rexpkg.tools import rexio
from b2rexpkg.tools.rexio.library import library
from b2rexpkg.tools import runexternal

from b2rexpkg.b25 import logic
from b2rexpkg.b25.material import RexMaterialIO

#from .props.rexlogic import RexLogicProps

import bpy
import subprocess

class RexExportModule(SyncModule):
    """
    b2rex module taking care of exporting to tundra
    """
    def export(self, context):
        """
        Export and pack the scene to rex logic format.
        """
        editor = self._parent
        editor.exportSettings = context.scene.b2rex_props
        editor.exportSettings.loc = [0,0,0]
        dest = editor.ensureDestinationDir(delete=True)

        # export materials
        for ob in bpy.context.scene.objects:
            if ob.type == 'MESH':
                self.export_materials(ob, dest)

        # export ogre data
        editor.onExport(context, delete=False)

        # export rex data
        dest_tundra = os.path.join(dest, editor.exportSettings.pack + '.txml')
        e = rexio.export.RexSceneExporter()
        e.export(context.scene, dest_tundra)
        return dest_tundra

    def run(self, context):
        """
        Export to tundra format and run the server on the given file.
        """
        dest_tundra = self.export(context)
        editor = self._parent

        # run tundra
        props = editor.exportSettings
        paths = []
        if props.tundra_path:
            paths.append(props.tundra_path)
        app_path = runexternal.find_application('server', paths)
        prevdir = os.curdir
        os.chdir(os.path.dirname(app_path))

        subprocess.call([app_path,
                          '--file',
                          dest_tundra])
        os.chdir(prevdir)


    def export_materials(self, obj, dest):
        """
        Export materials for the given file.
        """
        editor = self._parent
        mesh = obj.data
        faces = editor._getFaceRepresentatives(mesh)
        f = open(os.path.join(dest, mesh.name + '.material'), 'w')
        for face in faces:
            bmat = editor._getFaceMaterial(mesh, face)
            if not bmat.opensim.uuid:
                bmat.opensim.uuid = str(uuid.uuid4())
                bmat.name = bmat.opensim.uuid
            matio = RexMaterialIO(editor, mesh, face, bmat)
            matio.write(f)
        f.write('\n\n')
        f.close()

    def draw(self, layout, session, props):
        if not self.expand(layout, title='Rex logic'):
            return False
        col = layout.column_flow(0)
        col.operator("b2rex.rexexport", text="Export").action = 'export'
        if runexternal.find_application('server', [props.tundra_path]):
            col.operator("b2rex.rexexport", text="Export and run").action = 'run'
        components = library.get_components('jsscript')
        box = layout.box()
        for component_name in components:
            component = components[component_name]
            box.label(component.name)
            if component.dependencies:
                deps = map(lambda s: s.replace('EC_', ''), component.dependencies)
                box.label("    "+", ".join(deps), icon='RNA')
            if component.attributes:
                box.label("    "+", ".join(component.attributes), icon='SETTINGS')


