bl_info = {
    "name": "iOps",
    "author": "Titus, Cyrill, Aleksey",
    "version": (1, 5, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Toolbar and View3D",
    "description": "Interaction operators (iOps) = workflow speedup",
    "warning": "",
    "wiki_url": "https://blenderartists.org/t/interactionops-iops/",
    "tracker_url": "https://github.com/TitusLVR/InteractionOps",
    "category": "Learnbgame",
}

import bpy
from .operators.iops import IOPS
from .operators.modes import (IOPS_OT_MODE_F1,
                              IOPS_OT_MODE_F2,
                              IOPS_OT_MODE_F3,
                              IOPS_OT_MODE_F4)
from .operators.cursor_origin.curve import (IOPS_OT_CursorOrigin_Curve,
                                            IOPS_OT_CursorOrigin_Curve_Edit)
from .operators.cursor_origin.empty import IOPS_OT_CursorOrigin_Empty
from .operators.cursor_origin.gpen import (IOPS_OT_CursorOrigin_Gpen,
                                           IOPS_OT_CursorOrigin_Gpen_Edit)
from .operators.cursor_origin.mesh import IOPS_OT_CursorOrigin_Mesh
from .operators.cursor_origin.mesh_edit import IOPS_OT_CursorOrigin_Mesh_Edit
from .operators.align_object_to_face import AlignObjectToFace
from .operators.object_visual_origin import *
from .operators.object_visual_origin import IOPS_OP_VisualOrigin
from .operators.curve_subdivide import IOPS_OT_CurveSubdivide
from .operators.mesh_convert_selection import (IOPS_OP_ToFaces,
                                               IOPS_OP_ToEdges,
                                               IOPS_OP_ToVerts)
from .prefs.addon_preferences import IOPS_AddonPreferences


# WarningMessage
def ShowMessageBox(text="", title="WARNING", icon="ERROR"):
    def draw(self, context):
        self.layout.label(text=text)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def register_keymaps():
    keys = [
        ('iops.mode_f1',                   'F1', 'PRESS', False, False, False),
        ('iops.mode_f2',                   'F2', 'PRESS', False, False, False),
        ('iops.mode_f3',                   'F3', 'PRESS', False, False, False),
        ('iops.mode_f4',                   'F4', 'PRESS', False, False, False),
        ('iops.curve_subdivide',           'F2', 'PRESS', False, False, False),
        ('iops.cursor_origin_mesh',        'F4', 'PRESS', False, False, False),
        ('iops.cursor_origin_mesh_edit',   'F4', 'PRESS', False, False, False),
        ('iops.cursor_origin_curve',       'F4', 'PRESS', False, False, False),
        ('iops.cursor_origin_curve_edit',  'F4', 'PRESS', False, False, False),
        ('iops.cursor_origin_empty',       'F4', 'PRESS', False, False, False),
        ('iops.cursor_origin_gpen',        'F4', 'PRESS', False, False, False),
        ('iops.cursor_origin_gpen_edit',   'F4', 'PRESS', False, False, False),
        ('iops.align_object_to_face',      'F5', 'PRESS', False, False, False),
        ('iops.to_verts',                  'F1', 'PRESS', False, True,  False),
        ('iops.to_edges',                  'F2', 'PRESS', False, True,  False),
        ('iops.to_faces',                  'F3', 'PRESS', False, True,  False)
    ]

    keyconfigs = bpy.context.window_manager.keyconfigs
    keymapItems = (bpy.context.window_manager.keyconfigs.addon.keymaps.new("Window").keymap_items)
    for k in keys:
        found = False
        for kc in keyconfigs:
            keymap = kc.keymaps.get("Window")
            if keymap:
                kmi = keymap.keymap_items
                for item in kmi:
                    if item.idname.startswith('iops.') and item.idname == str(k[0]):
                        found = True
                    else:
                        found = False
        if not found:
            kmi = keymapItems.new(k[0], k[1], k[2], ctrl=k[3], alt=k[4], shift=k[5])
            kmi.active = True


def unregister_keymaps():
    keyconfigs = bpy.context.window_manager.keyconfigs
    for kc in keyconfigs:
        keymap = kc.keymaps.get("Window")
        if keymap:
            keymapItems = keymap.keymap_items
            toDelete = tuple(
                item for item in keymapItems if item.idname.startswith('iops.'))
            for item in toDelete:
                keymapItems.remove(item)

# Classes for reg and unreg
classes = (IOPS,
           IOPS_AddonPreferences,
           IOPS_OT_MODE_F1,
           IOPS_OT_MODE_F2,
           IOPS_OT_MODE_F3,
           IOPS_OT_MODE_F4,
           IOPS_OT_CursorOrigin_Curve,
           IOPS_OT_CursorOrigin_Curve_Edit,
           IOPS_OT_CursorOrigin_Empty,
           IOPS_OT_CursorOrigin_Gpen,
           IOPS_OT_CursorOrigin_Gpen_Edit,
           IOPS_OT_CursorOrigin_Mesh,
           IOPS_OT_CursorOrigin_Mesh_Edit,
           IOPS_OT_CurveSubdivide,
           IOPS_OP_ToFaces,
           IOPS_OP_ToEdges,
           IOPS_OP_ToVerts,
           AlignObjectToFace,
           IOPS_OP_VisualOrigin
           )

reg_cls, unreg_cls = bpy.utils.register_classes_factory(classes)


def register():
    reg_cls()
    register_keymaps()
    print("IOPS Registered!")


def unregister():
    unreg_cls()
    unregister_keymaps()
    print("IOPS Unregistered!")


if __name__ == "__main__":
    register()
