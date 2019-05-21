# wahooney_uv_quad_unwrap.py Copyright (C) 2015, Keith "Wahooney" Boshoff
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

'''
HISTORY:

1.0:
 * Initial implementation

1.1:
 * Blender 2.76 compatibility

'''

bl_info = {
    'name': 'Quad Unwrap',
    'author': 'Keith (Wahooney) Boshoff',
    'version': (1, 0, 1),
    'blender': (2, 7, 6),
    #'location': 'UVs > Normalize UVs',
    'url': 'http://wahooney.net',
    'category': 'UV'}

import bpy
import bmesh
from mathutils import Vector

def main(self, context):

    use_linked = self.properties.use_linked

    obj = context.active_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()

    f = bm.faces.active

    if f is None:
        self.report ({'INFO'}, "Active face required.")
        return

    if len (f.loops) != 4:
        self.report ({'INFO'}, "Active face must be exactly 4 vertices.")
        return

    #get uvs and average edge lengths
    luv1 = f.loops[0][uv_layer]
    luv2 = f.loops[1][uv_layer]
    luv3 = f.loops[2][uv_layer]
    luv4 = f.loops[3][uv_layer]

    l1 = ((f.verts[0].co - f.verts[1].co).length + (f.verts[2].co - f.verts[3].co).length) / 2
    l2 = ((f.verts[1].co - f.verts[2].co).length + (f.verts[3].co - f.verts[0].co).length) / 2

    # Try to fit into old coords
    u = ((luv1.uv - luv2.uv).length + (luv3.uv - luv4.uv).length) / 2
    v = ((luv2.uv - luv3.uv).length + (luv4.uv - luv1.uv).length) / 2

    c = (luv1.uv + luv2.uv + luv3.uv + luv4.uv) / 4

    #u = 1
    #v = 1

    if l1 < l2:
        u = v*(l1/l2)
    else:
        v = u*(l2/l1)

    #try to fit into old coords
    luv1.uv = c + Vector ((-u, -v)) / 2
    luv2.uv = c + Vector ((u, -v)) / 2
    luv3.uv = c + Vector ((u, v)) / 2
    luv4.uv = c + Vector ((-u, v)) / 2
    
    bmesh.update_edit_mesh(me)

    # store selection
    selection = []
    for f in bm.faces:
        if f.select:
            selection.append (f)

    # select linked
    if use_linked:
        bpy.ops.mesh.select_linked(delimit={'SEAM'})

    # follow active quads
    bpy.ops.uv.follow_active_quads (mode='LENGTH_AVERAGE')

    # restore selection
    for f in bm.faces:
        f.select = False

    for f in selection:
        f.select = True

from bpy.props import *

class QuadUnwrap (bpy.types.Operator):
    """Unwrap selection from to contiguous uniform quad layout"""
    bl_idname = "uv.quad_unwrap"
    bl_label = "Quad Unwrap"
    bl_options = {'UNDO', 'REGISTER'}

    use_linked = BoolProperty(name="Quad Linked Faces", description="Apply Quad Unwrap to linked faces",
            default=False)

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}

addon_keymaps = []

def register_keymaps():

    kc = bpy.context.window_manager.keyconfigs.addon

    if kc:
        kmuv = kc.keymaps.new(name="UV Editor", space_type='EMPTY', region_type='WINDOW', modal=False)
        km3d = kc.keymaps.new(name="Mesh")

        # Quad unwrap
        kmi = kmuv.keymap_items.new("uv.quad_unwrap", 'Q', 'PRESS', ctrl=False, shift=True, alt=False)
        kmi.properties.use_linked = False

        kmi = kmuv.keymap_items.new("uv.quad_unwrap", 'Q', 'PRESS', ctrl=True, shift=True, alt=False)
        kmi.properties.use_linked = True

        kmi = km3d.keymap_items.new("uv.quad_unwrap", 'Q', 'PRESS', ctrl=False, shift=True, alt=False)
        kmi.properties.use_linked = False

        kmi = km3d.keymap_items.new("uv.quad_unwrap", 'Q', 'PRESS', ctrl=True, shift=True, alt=False)
        kmi.properties.use_linked = True

        addon_keymaps.append (kmuv)
        addon_keymaps.append (km3d)


def unregister_keymaps():

    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)

    # clear the list
    del addon_keymaps[:]

def register():
    bpy.utils.register_class(QuadUnwrap)
    register_keymaps ()

def unregister():
    bpy.utils.unregister_class(QuadUnwrap)
    unregister_keymaps ()

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.uv.quad_unwrap()
