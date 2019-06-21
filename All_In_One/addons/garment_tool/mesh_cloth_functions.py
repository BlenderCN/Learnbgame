'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
import bmesh
import copy
import numpy as np


def three_d_bincount_add(out ,e_k, weights):
    out[:,0] += np.bincount(e_k, weights[:,0], out.shape[0])
    out[:,1] += np.bincount(e_k, weights[:,1], out.shape[0])
    out[:,2] += np.bincount(e_k, weights[:,2], out.shape[0])

def new_bincount(out, e_k, weights = None):
    out += np.bincount(e_k, weights, out.shape[0]) 


def close_bmesh(context,  bm, source):
    bm.normal_update()
    if context.object.mode == "EDIT":
        bmesh.update_edit_mesh(source, tessface=False, destructive=False)
    else:
        bm.to_mesh(source)
        bm.free()
        # source.update()

def get_bmesh(context, mesh):
    bm = bmesh.new()
    if context.active_object.mode == 'OBJECT':
        bm.from_mesh(mesh)
    elif context.active_object.mode == 'EDIT':
        bm =  bmesh.from_edit_mesh(mesh)            
    return bm

class GTOOL_OT_GarmentSmooth(bpy.types.Operator):
    bl_idname = 'object.cloth_smooth'
    bl_label = 'Cloth Smooth'
    bl_description = 'Smooth'
    bl_options = {'REGISTER', 'UNDO'}

    iteration_amount: IntProperty(name="Iterations", description="Number of times to repeat the smoothing", default=3, min=1, max=10, step=1)

    def inflate_numpy_smooth(self,context):
        bm = get_bmesh(context, context.active_object.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        o_co =  np.array([vert.co for vert in bm.verts])
        vert_count =  len(bm.verts)

        edge_keys = np.array([ [edge.verts[0].index, edge.verts[1].index] for edge in  bm.edges])
        freeze_verts = np.array([vert.is_boundary or not vert.is_manifold for vert in bm.verts]) #manifold for pocket sewing edges

        p_co = np.copy(o_co) #current new vertex position

        #sum edges that have vert X  and either end of edge (Va, Vb)
        v_connections = np.zeros(vert_count, dtype=np.float32)
        new_bincount(v_connections, edge_keys[:,1] ) 
        new_bincount(v_connections, edge_keys[:,0]) 

        for x in range(self.iteration_amount):
            q_co = np.copy(p_co) #prevoius iteration vert position
            p_co.fill(0)
            #calc average position weighted...
            three_d_bincount_add(p_co, edge_keys[:,1], q_co[edge_keys[:,0]])
            three_d_bincount_add(p_co, edge_keys[:,0], q_co[edge_keys[:,1]])

            p_co =p_co / v_connections[:,None]   #new aver posision

            p_co[freeze_verts] = q_co[freeze_verts] # not selected ver - reset to original pos o_co
        # source.vertices.foreach_set('co', p_co.ravel())
        for v in bm.verts:
            v.co = p_co[v.index]
        close_bmesh(context, bm, context.active_object.data)


    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'MESH')

    def execute(self, context):
        self.inflate_numpy_smooth(context)
        return {'FINISHED'}


class GTOOL_OT_BakeSimToShape(bpy.types.Operator):
    bl_idname = "cloth.save_to_shape"
    bl_label = "Save to shape key"
    bl_description = "Save sim to shape key"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        if garment.name in context.scene.objects.keys():
            shapeSourceObj = bpy.data.objects[garment.name]
        else:
            self.report({'INFO'}, 'Cannot find Garment mesh: ' + garment.name)
            return {'CANCELLED'}

        context.view_layer.objects.active = shapeSourceObj
        if not shapeSourceObj.data.shape_keys:
            bpy.ops.object.shape_key_add(from_mix=False)  # add  base key
        for i, sourceShape in enumerate(shapeSourceObj.data.shape_keys.key_blocks):
            sourceShape.value = 0
        bpy.context.scene.update()

        shapeSourceObj.shape_key_add(name=garment.name, from_mix=False)
        bpy.context.scene.update()
        target_shape= shapeSourceObj.data.shape_keys.key_blocks[-1]

        constructive_modifiers = ['SUBSURF', 'BEVEL', 'MIRROR', 'MASK', 'EDGE_SPLIT','SOLIDIFY']
        for mod in shapeSourceObj.modifiers: #disable constructive modifiers
            if mod.type in  constructive_modifiers:
                mod.show_viewport = False
        bpy.context.scene.update()
        modified_mesh = shapeSourceObj.to_mesh(depsgraph=context.depsgraph, apply_modifiers=True, calc_undeformed=True)
        for meshVert in modified_mesh.vertices:
            target_shape.data[meshVert.index].co = meshVert.co
        bpy.data.meshes.remove(modified_mesh)
        # shapeTargetObj.data.shape_keys.key_blocks[i].name = sourceShape.name
        sourceShape.value = 0
        shapeSourceObj.data.shape_keys.key_blocks[-1].value = 0

        for mod in shapeSourceObj.modifiers: #disable constructive modifiers
            if mod.type in constructive_modifiers:
                mod.show_viewport = True
        return {"FINISHED"}



def setup_keyframes(context, garment):
    if garment.name not in bpy.data.objects:
        return
    sim_time = garment.sim_time #use for gravity ? or as bake cache time?
    garment_obj = bpy.data.objects[garment.name]
    garment_obj.animation_data_clear() #maybe jutt delete cloth mod actions keyfremes
    if garment_obj.modifiers["Cloth"].settings.vertex_group_shrink != '':
        garment_obj.modifiers["Cloth"].settings.shrink_max = 0.0
        garment_obj.keyframe_insert(data_path='modifiers["Cloth"].settings.shrink_max', frame=0)
        garment_obj.modifiers["Cloth"].settings.shrink_max = 0.2
        garment_obj.keyframe_insert(data_path='modifiers["Cloth"].settings.shrink_max', frame=int(sim_time*0.5))

    if garment_obj.modifiers["Cloth"].settings.quality <= 10:
        garment_obj.modifiers["Cloth"].settings.quality = 22
    # context.scene.animation_data_clear()
    if context.scene.animation_data:
        if context.scene.animation_data.action is None:
            context.scene.animation_data.action = bpy.data.actions.new('SceneAction')
        for fcurv in context.scene.animation_data.action.fcurves:
            if fcurv.data_path == 'gravity':
                context.scene.animation_data.action.fcurves.remove(fcurv)
    context.scene.gravity[2] = -0.8
    context.scene.keyframe_insert(data_path='gravity', frame=0)
    context.scene.gravity[2] = -9.8
    context.scene.keyframe_insert(data_path='gravity', frame=sim_time)
    
    garment_obj.modifiers["Cloth"].settings.sewing_force_max = 0
    garment_obj.keyframe_insert(data_path='modifiers["Cloth"].settings.sewing_force_max', frame=0)
    garment_obj.modifiers["Cloth"].settings.sewing_force_max = 2.0
    garment_obj.keyframe_insert(data_path='modifiers["Cloth"].settings.sewing_force_max', frame=int(sim_time*0.5))

    garment_obj.modifiers['Cloth'].point_cache.frame_end = int(sim_time*1.2)

    
class GTOOL_OT_SetupKeyframes(bpy.types.Operator):
    bl_idname = "garment.setup_keyframes"
    bl_label = "Initialize Simulation"
    bl_description = 'Initialize simulation variables (like gravity, sewing strenth) by animating their slow increase over time\n\
This helps to avoid cloth falling too fast on floor'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        setup_keyframes(context,garment)
        return {'FINISHED'}


class GTOOL_OT_BakeCloth(bpy.types.Operator):
    bl_idname = "garment.simulate_cloth"
    bl_label = "Simulate"
    bl_description = 'Bake simulation for Garment mesh'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        if garment.name not in bpy.data.objects:
            self.report({'INFO'}, 'Cannot find Garment object: ' + garment.name)
            return {'CANCELLED'}
        garment_obj = bpy.data.objects[garment.name]
        for modifier in garment_obj.modifiers:
            if modifier.type == 'CLOTH':
                override = {'scene': context.scene, 'active_object': garment_obj, 'point_cache': modifier.point_cache}
                bpy.ops.ptcache.free_bake(override)
                bpy.ops.ptcache.bake(override, bake=True)
                break
        return {'FINISHED'}
