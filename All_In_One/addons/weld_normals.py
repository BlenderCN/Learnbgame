bl_info = {
    "name": "Weld Object Normals",
    "author": "Some asshole",
    "version": ( 0, 1, 0 ),
    "blender": (2, 76, 0),
    "location": "Tool shelf",
    "description": "Weld the normals of two objects.",
    "show_expanded": True,
    "category": "Learnbgame"
}
	
import bpy
import bmesh
import os
import logging
import traceback
from mathutils import Color, Vector
from math import pi, exp
from bpy.types import Menu, Operator
from bpy.props import *
from bl_operators.presets import AddPresetBase
import shutil
import array


import os, sys, glob
import logging
from bpy.props import *
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty


class SparklesToolset(bpy.types.Operator):
    bl_idname = "sparkles.toolset_pro"
    bl_label  = "sparkles toolset pro"
    pass

class PanelSparklesTool(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Weld Object Normals"
    bl_idname = "sparkles.tools"
    bl_category    = "Tools"
        
        
    def draw(self, context):
        layout = self.layout
    
        if context.object:
            if context.object.type == 'MESH':
                box = layout.box()
                box.label("Normals Tools")
                WeldNormals.draw_generic(context, box)

template_paths=[]


def visualCopyMesh(context, target, apply_pose=True):

    dupobj      = target.copy()
    dupobj.data = target.data.copy()

    ctx                  = context.copy()
    ctx['active_object'] = dupobj
    ctx['object']        = dupobj

    context.scene.objects.link(dupobj)

    if dupobj.data.shape_keys:
        N = len(dupobj.data.shape_keys.key_blocks)
        if N > 0:
            sk = dupobj.shape_key_add("mix", from_mix=True)
            N += 1
            for ii in range (N-2, -1, -1):
                dupobj.active_shape_key_index = ii
                bpy.ops.object.shape_key_remove(ctx)

            dupobj.active_shape_key_index = 0
            bpy.ops.object.shape_key_remove(ctx)
            print("Baked Shape keys for %s" % dupobj.name)

    if apply_pose:

        try:
            for mod in dupobj.modifiers:
                if mod.type=="ARMATURE":
                    ctx['modifier'] = mod
                    bpy.ops.object.modifier_apply(ctx, apply_as='DATA', modifier=mod.name)
        except:
            print("Unexpected error while applying modifier:", sys.exc_info()[0])
            pass

    return dupobj


def getMesh(context, obj, exportRendertypeSelection, apply_mesh_rotscale = True):
    disabled_modifiers = []
    
    #
    #
    for m in obj.modifiers:
        if exportRendertypeSelection == 'NONE':
            if m.show_viewport == True:
                disabled_modifiers.append(m)
                m.show_viewport=False
        elif m.type == 'ARMATURE':
            if exportRendertypeSelection == 'PREVIEW' and m.show_viewport == True:
                m.show_viewport=False
                disabled_modifiers.append(m)
            elif exportRendertypeSelection == 'RENDER' and m.show_render == True:
                m.show_render=False
                disabled_modifiers.append(m)

    mesh_type = exportRendertypeSelection
    if mesh_type == 'NONE':
        mesh_data_copy = obj.to_mesh(context.scene, False, 'PREVIEW')
    else:
        mesh_data_copy = obj.to_mesh(context.scene, True, mesh_type)
    mesh_data_copy.name = mesh_data_copy.name + "_mdc"

    for m in disabled_modifiers:
        if exportRendertypeSelection == 'RENDER':
            m.show_render=True
        else:
            m.show_viewport=True

    if apply_mesh_rotscale:
        m = obj.matrix_world.copy()
        m[0][3] = m[1][3] = m[2][3] = 0
        mesh_data_copy.transform(m)
        mesh_data_copy.calc_normals()
    return mesh_data_copy

def get_boundary_verts(bmsrc, context, obj, exportRendertypeSelection="NONE", apply_mesh_rotscale = True):
    target_copy           = visualCopyMesh(context, obj)
    target_copy_data      = target_copy.data
    target_copy_data.name += "(frozen)"
    bmsrc.from_mesh(target_copy_data)    
    verts = [vert for vert in bmsrc.verts if vert.is_boundary]
    for vert in verts:
        co = obj.matrix_world*(vert.co)
        vert.co = co
    context.scene.objects.unlink(target_copy)
    bpy.data.objects.remove(target_copy)
    
    return verts
    
def get_nearest_vert_on_source(source_verts, target_vert):
    mindist   = None
    candidate = None
    for source_vert in source_verts:
        dist = (source_vert.co - target_vert.co).magnitude
        
        if dist < 0.001 and (not mindist or mindist < dist):
           mindist   = dist
           candidate = source_vert

    return candidate

def get_adjusted_vertex_normals(context, sources, exportRendertypeSelection, apply_mesh_rotscale):
    bm_source  = bmesh.new()
    bm_target  = bmesh.new()
    
    targets = sources.copy()
    source_normals    = {}

    active_object = bpy.context.object
    mesh_select_mode = context.scene.tool_settings.mesh_select_mode
    for obj in sources:
        bpy.context.scene.objects.active = obj
        omode = set_object_mode("EDIT")
        obj.data.calc_normals()
        set_object_mode(omode)
        
    context.scene.tool_settings.mesh_select_mode = mesh_select_mode
    bpy.context.scene.objects.active = active_object
    
    for obj in [obj for obj in sources if obj.select]:
    
        target_verts = get_boundary_verts(bm_target, context, obj, exportRendertypeSelection, apply_mesh_rotscale)
        bm_target.verts.ensure_lookup_table()
        bm_target.faces.ensure_lookup_table()
        targets.remove(obj)
        
        for otherobj in [ob for ob in sources if ob != obj]:

            source_verts = get_boundary_verts(bm_source, context, otherobj, exportRendertypeSelection, apply_mesh_rotscale)
            bm_source.verts.ensure_lookup_table()
            bm_source.faces.ensure_lookup_table()

            if not obj.name in source_normals:
                source_normals[obj.name]={}
            normals = source_normals[obj.name]
            
            for target_vert in [v for v in target_verts if any([e.smooth for e in v.link_edges])]:
                source_vert = get_nearest_vert_on_source(source_verts, target_vert)
                if source_vert:
                    avnor = Vector((0,0,0))
                    for face in [f for f in source_vert.link_faces if f.smooth]:
                        avnor += face.normal
                    for face in [f for f in target_vert.link_faces if f.smooth]:
                        avnor += face.normal
                    avnor.normalize()
                    for loop in [l for l in target_vert.link_loops if l.face.smooth]:
                        normals[loop.index] = avnor
            
            bm_source.clear()
        bm_target.clear()
        
    bm_source.free()        
    bm_target.free()
    return source_normals


class WeldNormals(bpy.types.Operator):
    bl_idname = "sparkles.weld_normals"
    bl_label  = "Weld Normals"
    bl_description = "Weld Normals to adjacent objects (only operates on boundary edges)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.active_object
        return ob and ob.type == 'MESH'
        
    @staticmethod
    def draw_generic(context, layout):
        col=layout.column(align=True)
        col.operator(WeldNormals.bl_idname, text="Weld Selected")

    def execute(self, context):
        mesh_select_mode = context.scene.tool_settings.mesh_select_mode
        context.scene.tool_settings.mesh_select_mode = (False,False,True)
        mobs = [ob for ob in context.visible_objects if ob.is_visible(context.scene) and ob.type=="MESH"]
        adjusted_normals = get_adjusted_vertex_normals(context, mobs, 'PREVIEW', True)
        
        if adjusted_normals:
            for tgt in [obj for obj in mobs if obj.select and obj.name in adjusted_normals]:
                welded_normals = adjusted_normals[tgt.name]
                mesh = tgt.data
                mesh.use_auto_smooth = True
                mesh.show_edge_sharp = True
                normals = [0.0] * len(mesh.loops) * 3
                for key, n in welded_normals.items():
                    vidx = tgt.data.loops[key].vertex_index
                    normals[3*key]   = n[0]
                    normals[3*key+1] = n[1]
                    normals[3*key+2] = n[2]
                original_mode = set_object_mode('OBJECT')
                tnormals = tuple(zip(*(iter(normals),) * 3))
                mesh.normals_split_custom_set(tnormals)

                set_object_mode(original_mode)
        context.scene.tool_settings.mesh_select_mode = mesh_select_mode
        return {'FINISHED'}

def set_object_mode(new_mode, def_mode=None, object=None):
    if new_mode is None:
        if def_mode is None:
            return None
        new_mode = def_mode
    
    try:
        if object == None:
            object = bpy.context.scene.objects.active
            
        if object == None:
            return None

        if object.mode == new_mode:
            return new_mode
    except:
        pass
        
    original_mode = object.mode
    try:
        context = bpy.context.copy()
        context['active_object'] = object
        bpy.ops.object.mode_set(context, mode=new_mode)
    except:
        print("Can't set object %s of type %s to mode %s" % (object.name, object.type, new_mode) )
        raise Exception("Wrong mode setting")
    return original_mode
    
def register():

        
    bpy.utils.register_module(__name__)
    sparkles_init    = __file__
    sparkles_home    = os.path.dirname(sparkles_init)

    
def unregister():
    
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    
    register()
