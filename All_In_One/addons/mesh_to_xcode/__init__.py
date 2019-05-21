"""Defines toolbox layout and implements the logic.
"""

# import modules
if 'bpy' in locals():
    import importlib

    importlib.reload(imports)
    importlib.reload(modifiers)

    print('bpy in locals')
else:
    from .imports import ImportMeshButton
    from .modifiers import (
        DecimateMeshButton,
        ApplyModifiersButton,
        RemoveModifiersButton
    )

    print('relative import')

import os
import bpy
import bmesh

from bpy.types import (
    Panel,
    Operator,
    Scene
)


# addon configs
bl_info = {
    'name': 'Mesh to XCode',
    'description': 'Toolbox to modify meshes for XCode',
    'author': 'Osman Mesut Ozcan',
    'blender': (2, 8, 1),
    'version': (0, 0, 1),
    'category': 'Add Mesh',
    'location': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
}


class MeshToolboxPanel(Panel):
    """Main toolbox panel

    Defines layout properties of the toolbox.
    """
    bl_idname = 'mesh_to_xcode.toolbox'
    bl_label = 'Mesh to XCode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        obj = context.active_object

        ##############  IMPORT ######################
        row = layout.row()
        row.operator('mesh_to_xcode.import', icon='IMPORT')

        ##############  INFORMATION #################
        layout.separator()
        layout.label('Mesh Information')
        info_box = layout.box()
        mesh = obj.data

        bm = bmesh.new()
        bm.from_object(obj, scene)
        info_box.label('Total Vertices: {}'.format(
            len(bm.verts)))

        info_box.label('Total Faces:    {}'.format(
            len(bm.faces)))
        bm.free()

        ##############  MODIFIERS ###################
        layout.separator()
        layout.label('Mesh Modifiers')

        mod_box = layout.box()

        # reduce mesh polygon count
        row = mod_box.row(align=True)
        try:
            row.label('Decimate:')
            row.prop(obj.modifiers['Decimate'], "ratio")
        except KeyError:
            row.operator('mesh_to_xcode.decimate_button')

        # operation to all mods
        mod_box.separator()
        row = mod_box.row(align=True)
        row.operator('mesh_to_xcode.apply_modifiers')
        row.operator('mesh_to_xcode.remove_modifiers')

        ##############  TEXTURE #####################
        layout.separator()
        layout.label('Texture Modifiers')


classes = {
    # panels
    MeshToolboxPanel,

    # buttons
    ImportMeshButton,
    DecimateMeshButton,
    ApplyModifiersButton,
    RemoveModifiersButton,
}


def register():
    """Registers classes to Blender.
    """
    bpy.types.Scene.mesh_to_xcode_import_path = bpy.props.StringProperty (
        name='Import Path',
        default = '',
        description = 'Define the path where to import from',
        subtype = 'DIR_PATH'
    )
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregisters classes from Blender.
    """
    del bpy.types.Scene.mesh_to_xcode_import_path
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
