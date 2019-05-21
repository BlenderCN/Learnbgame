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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import *
import os
import random
from mathutils import *


def create_cutter(context, crack_type, scale, roughness, materialname):
    ncuts = 12
    if crack_type == 'FLAT' or crack_type == 'FLAT_ROUGH':
        bpy.ops.mesh.primitive_cube_add(
            view_align=False,
            enter_editmode=False,
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            layers=context.scene.layers)

        for v in context.active_object.data.vertices:
            v.co[0] += 1.0
            v.co *= scale

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.uv.reset()

        if crack_type == 'FLAT_ROUGH':
            bpy.ops.mesh.subdivide(
                number_cuts=ncuts,
                fractal=0.0,
                smoothness=0)#roughness *  scale

            bpy.ops.mesh.vertices_smooth(repeat=1)

        bpy.ops.object.editmode_toggle()

    if crack_type == 'SPHERE' or crack_type == 'SPHERE_ROUGH':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4,
            size=1,
            view_align=False,
            enter_editmode=False,
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            layers=context.scene.layers)

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)

        bpy.ops.object.editmode_toggle()
        for v in context.active_object.data.vertices:
            v.co[0] += 1.0
            v.co *= scale

    if crack_type == 'SPHERE_ROUGH' or crack_type =='FLAT_ROUGH':
        for v in context.scene.objects.active.data.vertices:
            v.co[0] += roughness * scale * 0.2 * (random.random() - 0.5)
            v.co[1] += roughness * scale * 0.1 * (random.random() - 0.5)
            v.co[2] += roughness * scale * 0.1 * (random.random() - 0.5)
    
    #assign inner material to cutter
    #print("CUTTERMAT", materialname)
    if materialname != "" and materialname != None and \
    materialname in bpy.data.materials:
        ctx = bpy.context.copy()
        ctx["object"] = bpy.context.active_object
        bpy.ops.object.material_slot_add(ctx)
        material = bpy.data.materials[materialname]
        bpy.context.active_object.material_slots[0].material = material
    
    bpy.context.active_object.select = True
#    bpy.context.scene.objects.active.select = True


#UNWRAP
def getsizefrommesh(ob):
    bb = ob.bound_box
    return (
        bb[5][0] - bb[0][0],
        bb[3][1] - bb[0][1],
        bb[1][2] - bb[0][2])


def getIslands(shard):
    sm = shard.data
    vgroups = []
    fgroups = []

    vgi = []
    for v in sm.vertices:
        vgi.append(-1)

    gindex = 0
    for i in range(len(vgi)):
        if vgi[i] == -1:
            gproc = [i]
            vgroups.append([i])
            fgroups.append([])

            while len(gproc) > 0:
                i = gproc.pop(0)
                for f in sm.polygons:
                    for v in f.vertices:
                        if v == i:
                            for v1 in f.vertices:
                                if vgi[v1] == -1:
                                    vgi[v1] = gindex
                                    vgroups[gindex].append(v1)
                                    gproc.append(v1)

                            fgroups[gindex].append(f.index)

            gindex += 1

    if gindex == 1:
        shards = [shard]

    else:
        shards = []
        for gi in range(0, gindex):
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = shard
            shard.select = True
            bpy.ops.object.duplicate(linked=False, mode='DUMMY')
            a = bpy.context.scene.objects.active
            sm = a.data
            print (a.name)

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()

            for x in range(len(sm.vertices) - 1, -1, -1):
                if vgi[x] != gi:
                    a.data.vertices[x].select = True

            print(bpy.context.scene.objects.active.name)

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.delete()
            bpy.ops.object.editmode_toggle()

            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

            shards.append(a)

        bpy.context.scene.objects.unlink(shard)

    return shards


def boolop(ob, cutter, op):
    sce = bpy.context.scene

    fault = 0
    new_shards = []

    sizex, sizey, sizez = getsizefrommesh(ob)
    gsize = sizex + sizey + sizez

    bpy.ops.object.select_all()
    ob.select = True
    sce.objects.active = ob
    cutter.select = False

    if sce.objects.active == None: #error case, sometimes setting the active object doesnt work....
        return 0, [ob] #ob is the only shard
    
    bpy.ops.object.duplicate(linked=False, mode='DUMMY')
    a = sce.objects.active
    mod = a.modifiers.new("Boolean", 'BOOLEAN')
    mod.object = cutter
    mod.operation = op
    
    ctx = bpy.context.copy()
    ctx["object"] = a
    ctx["modifier"] = mod 
    bpy.ops.object.modifier_apply(ctx, apply_as='DATA', modifier=mod.name)
    nmesh=a.data

    if len(nmesh.vertices) > 0:
        #a.modifiers.remove(mod)

        new_shard = sce.objects.active
        new_shard.location = a.location
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        sizex, sizey, sizez = getsizefrommesh(new_shard)
        gsize2 = sizex + sizey + sizez

        if gsize2 > gsize * 1.01:               # Size check
            print (gsize2, gsize, ob.name, cutter.name)
            fault = 1
            #print ('boolop: sizeerror')

         # This checks whether returned shards are non-manifold.
         # Problem is, if org mesh is non-manifold, it will always fail (e.g. with Suzanne).
         # And disabling it does not seem to cause any problem...
#        elif min(mesh_utils.edge_face_count(nmesh)) < 2:    # Manifold check
#            fault = 1

        if not fault:
            new_shards = getIslands(new_shard)

        else:
            sce.objects.unlink(new_shard)

    else:
        sce.objects.unlink(a)
        fault = 2

    return fault, new_shards


def splitobject(context, ob, crack_type, roughness, materialname):
    scene = context.scene

    size = getsizefrommesh(ob)
    shards = []
    scale = max(size) * 1.3

    create_cutter(context, crack_type, scale, roughness, materialname)
    cutter = context.active_object
    cutter.location = ob.location

    cutter.location[0] += random.random() * size[0] * 0.1
    cutter.location[1] += random.random() * size[1] * 0.1
    cutter.location[2] += random.random() * size[2] * 0.1
    cutter.rotation_euler = [
        random.random() * 5000.0,
        random.random() * 5000.0,
        random.random() * 5000.0]

    scene.objects.active = ob
    operations = ['INTERSECT', 'DIFFERENCE']

    for op in operations:
        fault, newshards = boolop(ob, cutter, op)
        
        if ob.destruction.use_debug_redraw:
            scene.update()
            ob.destruction._redraw_yasiamevil()

        shards.extend(newshards)
        if fault > 0:
            # Delete all shards in case of fault from previous operation.
            for s in shards:
                scene.objects.unlink(s)

            scene.objects.unlink(cutter)
            #print('splitobject: fault')

            return [ob]

    if shards[0] != ob:
        bpy.context.scene.objects.unlink(ob)

    bpy.context.scene.objects.unlink(cutter)

    return shards


def fracture_basic(context, objects, nshards, crack_type, roughness, materialname):
    tobesplit = []
    shards = []

 #   for ob in context.scene.objects:
 #       if ob.select:
 #           tobesplit.append(ob)
    tobesplit.extend(objects)

    i = 1     # I counts shards, starts with 1 - the original object
    iter = 0  # counts iterations, to prevent eternal loops in case
              # of boolean faults

    maxshards = nshards * len(tobesplit)

    while i < maxshards and len(tobesplit) > 0 and iter < maxshards * 10:
        ob = tobesplit.pop(0)

        newshards = splitobject(context, ob, crack_type, roughness, materialname)
        tobesplit.extend(newshards)

        if len(newshards) > 1:
            shards.extend(newshards)
            #shards.remove(ob)

            i += (len(newshards) - 1)

            #print('fracture_basic: ' + str(i))
            #print('fracture_basic: lenobs', len(context.scene.objects))

        iter += 1
        
    #    prog = str(round(float(i) / float(maxshards), 2) * 100)
     #   ob.destruction.fracture_progress(prog)
        
    return shards