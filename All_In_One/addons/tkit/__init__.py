# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
        "name":        "tkit",
        "description": "edgemode select ops w/ configurable hotkeys",
        "author":      "Shams Kitz <dustractor@gmail.com>",
        "version":     (5,3),
        "blender":     (2,78,0),
        "location":    "Mesh Tools, Edge Menu, and hotkeys in edge-select mode",
        "warning":     "",
        "tracker_url": "https://github.com/dustractor/tkit",
        "wiki_url":    "",
        "category":    "Mesh"
        }

import bpy
import bmesh

selected = lambda _: _.select
notselected = lambda _: not _.select
tagged = lambda _: _.tag
nottagged = lambda _: not _.tag

class EdgeSelectMode:
    @classmethod
    def poll(self,context):
        return (context.active_object and
                context.active_object.type == 'MESH' and
                context.active_object.mode == 'EDIT' and
                context.scene.tool_settings.mesh_select_mode[1])

class TKIT:
    mapdata = []
    ops = []
    maps = []

    def __init__(self):
        def draw(s,c):
            if EdgeSelectMode.poll(c):
                for op in self.ops:
                    s.layout.operator(op.bl_idname)
        self.menu = type("TKIT_MT_menu",(bpy.types.Menu,),
                dict(
                    bl_label="tkit",
                    bl_idname="tkit.menu",
                    draw=draw))

    @property
    def classes(self):
        return [self.menu] + self.ops

    @classmethod
    def op(cls,f):
        n = f.__name__.lower()
        lbl,ign,mapx = f.__doc__.partition(":")
        ncls = type(
                "TKIT_OT_"+n,
                (EdgeSelectMode,bpy.types.Operator),
                dict(
                    bl_idname="tkit."+n,
                    bl_label=lbl,
                    bl_options={"REGISTER","UNDO"},
                    execute=f))
        cls.ops.append(ncls)
        if mapx:
            cls.maps.append((ncls.bl_idname,mapx))
        return ncls

    @staticmethod
    def menudraw(self,context):
        self.layout.menu("tkit.menu")

tkit = TKIT()

@tkit.op
def ie(self,context):
    '''Inner edges : QUOTE '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in bm.edges:
        e.tag = len(list(filter(selected,e.link_faces))) == 1
    for e in filter(tagged,bm.edges):
        e.select_set(0)
        e.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def oe(self,context):
    '''Outer Edges : S+QUOTE '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in bm.edges:
        e.tag = len(list(filter(selected,e.link_faces))) == 2
    for e in filter(tagged,bm.edges):
        e.select_set(0)
        e.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def lon(self,context):
    ''' lon : RIGHT_BRACKET '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for v in e.verts:
            v.tag ^= 1
        for f in e.link_faces:
            f.tag = 1
    efs = {f.index for f in filter(tagged,bm.faces)}
    for v in filter(tagged,bm.verts):
        v.tag = 0
        for e in filter(notselected,v.link_edges):
            e.tag = {f.index for f in e.link_faces}.isdisjoint(efs)
    for e in filter(tagged,bm.edges):
        e.tag = 0
        e.select_set(1)
    for f in bm.faces:
        f.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def lun(self,context):
    ''' lun (un-lon) : LEFT_BRACKET '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for v in e.verts:
            v.tag ^= 1
    for v in filter(tagged,bm.verts):
        v.tag = 0
        for e in filter(selected,v.link_edges):
            e.select_set(0)
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def epz(self,context):
    ''' epz : CSA+END '''

    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for v in e.verts:
            v.tag ^= 1
    for v in filter(tagged,bm.verts):
        for e in v.link_edges:
            e.select ^=1
    for e in bm.edges:
        e.select_set(e.select)
    for v in bm.verts:
        v.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def ef1n(self,context):
    ''' ef1n : BACK_SLASH '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for f in filter(notselected,e.link_faces):
            for fe in filter(notselected,f.edges):
                fe.tag = len(list(filter(selected,fe.verts))) == 1
    for e in bm.edges:
        e.select_set(e.tag)
        e.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def ef2n(self,context):
    ''' ef2n : S+BACK_SLASH '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for f in filter(notselected,e.link_faces):
            for fe in filter(notselected,f.edges):
                fe.tag = len(list(filter(notselected,fe.verts))) == 2
    for e in bm.edges:
        e.select_set(e.tag)
        e.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def ef2np(self,context):
    ''' ef2np : CS+BACK_SLASH '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for f in filter(notselected,e.link_faces):
            for fe in filter(notselected,f.edges):
                fe.tag ^= len(list(filter(notselected,fe.verts))) == 2
    for e in bm.edges:
        e.select_set(e.tag)
        e.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

@tkit.op
def ef2nx(self,context):
    ''' ef2nx : CSA+BACK_SLASH '''
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for e in filter(selected,bm.edges):
        for f in filter(notselected,e.link_faces):
            for fe in filter(notselected,f.edges):
                fe.tag = 1
    for e in bm.edges:
        e.select_set(e.tag)
        e.tag = 0
    bm.select_flush_mode()
    context.area.tag_redraw()
    return {'FINISHED'}

class tkitPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    def draw(self,context):
        layout = self.layout
        for op in tkit.ops:
            opn = op.bl_idname
            t = opn.partition(".")[2]
            layout.prop(self,t)

for opn,mapx in tkit.maps:
    t = opn.partition(".")[2]
    setattr(
            tkitPrefs,
            t,
            bpy.props.StringProperty(default=mapx))

def register():
    list(map(bpy.utils.register_class,tkit.classes))
    bpy.utils.register_class(tkitPrefs)

    prefs = bpy.context.user_preferences.addons[__name__].preferences
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new("Mesh",space_type="EMPTY")
        for op in tkit.ops:
            opn = op.bl_idname
            t = opn.partition(".")[2]
            mapx = getattr(prefs,t)
            modx = ""
            if "+" in mapx:
                modx,ign,mapt = mapx.partition("+")
            else:
                mapt = mapx
            ctrl,shift,alt,oskey = map(lambda _:_ in modx.upper(),"CSAO")
            mapt = mapt.strip()
            kmi = km.keymap_items.new(
                    opn, type=mapt, value="PRESS",
                    shift=shift, ctrl=ctrl, alt=alt, oskey=oskey)
            tkit.mapdata.append((km,kmi))
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(tkit.menudraw)
    bpy.types.VIEW3D_PT_tools_meshedit.append(tkit.menu.draw)

def unregister():
    for km,kmi in tkit.mapdata:
        km.keymap_items.remove(kmi)
    tkit.mapdata.clear()
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(tkit.menudraw)
    bpy.types.VIEW3D_PT_tools_meshedit.remove(tkit.menu.draw)
    bpy.utils.unregister_class(tkitPrefs)
    list(map(bpy.utils.unregister_class,tkit.classes))

