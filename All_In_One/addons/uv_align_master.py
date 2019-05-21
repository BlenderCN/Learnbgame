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

bl_info = {
    'name': "Aligning UV-coords",
    'author': "Mathias Weitz",
    'version': (1, 0, 4),
    'blender': (2, 6, 5),
    'api': 52859,
    'location': "IMAGE_EDITOR > UI",
    'description': "straightening UV-meshes",
    'category': 'UV'}
    
import bpy 
from bpy.props import *
import bmesh
import math 
import mathutils 
import itertools
from math import pi 
from mathutils import Vector, Matrix

def debug_del():
	for w in bpy.context.scene.objects:
		if w.name[0:9] == "textdebug":
			bpy.context.scene.objects.unlink(w)
			bpy.data.objects.remove(w)
	
def debug_show(origin,text):
	ft = bpy.data.curves.new('mytext','FONT')
	ft.body = text
	ft.size = 0.1
	ft.shear = 0
	ft.align = 'CENTER'
	ft.resolution_u = 2
	gr = bpy.data.objects.new("textdebug",ft)
	gr.location = Vector(origin)
	target = bpy.data.objects["Camera"]
	cns = gr.constraints.new("TRACK_TO")
	cns.name = "MTrack"
	cns.target = target
	cns.track_axis = 'TRACK_Z'
	cns.up_axis = 'UP_Y'
	cns.owner_space = 'LOCAL'
	cns.target_space = 'WORLD'
	bpy.context.scene.objects.link(gr)    


class thickface(object):
    __slots__= "v", "uv", "no", "area", "edge_keys"
    def __init__(self, face, uv_layer, mesh_verts):
        self.v = [mesh_verts[i] for i in face.vertices]
        self.uv = [uv_layer[i].uv for i in face.loop_indices]

        self.no = face.normal
        self.area = face.area
        self.edge_keys = face.edge_keys
        
class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)
 
    def draw(self, context):
        self.layout.label("Notice")
        row = self.layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(self, "message")
        #row = self.layout.split(0.80)
        #row.label("press ok and leave dialog") 
        #row.operator("error.ok")
        
class OkOperator(bpy.types.Operator):
    bl_idname = "error.ok"
    bl_label = "OK"
    def execute(self, context):
        return {'FINISHED'}

class UVTest(bpy.types.Operator):
    '''uv align'''
    bl_idname = 'uv.linealign'
    bl_label = 'linealign'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def execute(self, context):
        #print ('***************')
        error = 0
        active = bpy.context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')
        me = active.data
        uv_select_sync = bpy.context.scene.tool_settings.use_uv_select_sync
        
        if not me.uv_textures: 
            me.uv_textures.new()
            
        # getting the edges of a mesh-face aligned to the edge of a uv-face
        # the results are in edge with (vertindex_0, vertindex_1, uv_0, uv_1)
        # there could be more than one entry for vertindex_0, vertindex_1
        uv_layer = me.uv_layers.active.data
        markedUV = {}
        edges = []
        verts2uv = {}
        vert2vert = {}
        #me_vertices = me.vertices 
        #me_edges = me.edges
        #edges = [e for e in me_edges if me.vertices[e.vertices[0]].select and me.vertices[e.vertices[1]].select]
        for i,face in enumerate(me.polygons):
            for ii in range(len(face.loop_indices)):
                iip = (ii + 1) % len(face.loop_indices);
                iv0 = face.vertices[ii]
                iv1 = face.vertices[iip]
                uvi0 = ii
                uvi1 = iip
                if iv1 < iv0:
                    iv0 = face.vertices[iip]
                    iv1 = face.vertices[ii]
                    uvi0 = iip
                    uvi1 = ii
                
                if face.loop_indices[uvi0] not in verts2uv:
                    verts2uv[face.loop_indices[uvi0]] = [iv0, uv_layer[face.loop_indices[uvi0]].uv.copy()]   
                if face.loop_indices[uvi1] not in verts2uv:
                    verts2uv[face.loop_indices[uvi1]] = [iv1, uv_layer[face.loop_indices[uvi1]].uv.copy()]
                    
                v0 = me.vertices[iv0]
                v1 = me.vertices[iv1]
                select0 = False
                select1 = False
                if uv_select_sync:
                    select0 = v0.select
                    select1 = v1.select
                else:
                    select0 = uv_layer[face.loop_indices[uvi0]].select
                    select1 = uv_layer[face.loop_indices[uvi1]].select
                    
                if select0:
                    markedUV[face.loop_indices[uvi0]] = iv0
                if select1:
                    markedUV[face.loop_indices[uvi1]] = iv1
                if select0 and select1:
                    k = (iv0,iv1,face.loop_indices[uvi0],face.loop_indices[uvi1])
                    edges.append(k)
                    if iv0 not in vert2vert:
                        vert2vert[iv0] = []
                    if iv1 not in vert2vert:
                        vert2vert[iv1] = []
                    if iv0 not in vert2vert[iv1]:
                        vert2vert[iv1].append(iv0)
                    if iv1 not in vert2vert[iv0]:
                        vert2vert[iv0].append(iv1)
            
        #print (markedUV)
        #print (edges)
        #print ("verts2uv", verts2uv)
        #print ("len(verts2uv)", len(verts2uv))
        #print (vert2vert)
        
        # sorting the verts along the edges
        # start
        vertsOrder = []
        for vi, vin in vert2vert.items():
            if len(vin) == 1:
                vertsOrder.append(vi)
                vertsOrder.append(vin[0])
                break
        # TODO: if there is no start in the loop of the mesh
        # try to find a start in the verts of the UV-Mesh
        if 0 < len(vertsOrder):
            b = True
            maxc = 10000
            while b and 0 < maxc:
                b = False
                maxc -= 1
                v = vert2vert[vertsOrder[-1]]
                vn = v[0]
                if vn == vertsOrder[-2]:
                    if 1 < len(v):
                        vn = v[1]
                    else:
                        vn = None
                if vn != None:
                    vertsOrder.append(vn)
                    b = True
            
            # sorting the UV-Edges
            uvEdgeOrder = [[],[]]
            dist = 0.0
            if 1 < len(vertsOrder):
                for i in range(len(vertsOrder) - 1):
                    dist += (me.vertices[vertsOrder[i]].co - me.vertices[vertsOrder[i+1]].co).length
                    # the second uv-line can remain zero in the case of an open edge
                    if (len(uvEdgeOrder[0]) == i + 1 and (len(uvEdgeOrder[1]) == i + 1 or len(uvEdgeOrder[1]) == 0)) \
                        or i == 0:
                        vi0 = vertsOrder[i]
                        vi1 = vertsOrder[i+1]
                        for e in edges:
                            found = False
                            if e[0] == vi0 and e[1] == vi1:
                                #print ('->', e);
                                uv0, uv1 = e[2], e[3]
                                found = True
                            if e[0] == vi1 and e[1] == vi0:
                                #print ('-<', e);
                                uv0, uv1 = e[3], e[2]
                                found = True
                            if found:
                                if i == 0:
                                    if len(uvEdgeOrder[0]) == 0:
                                        uvEdgeOrder[0] = [uv0, uv1]
                                    else:
                                        uvEdgeOrder[1] = [uv0, uv1]
                                else:
                                    d0 = (uv_layer[uv0].uv - uv_layer[uvEdgeOrder[0][i]].uv).length
                                    d1 = 100.0
                                    if 0 < len(uvEdgeOrder[1]):
                                        d1 = (uv_layer[uv0].uv - uv_layer[uvEdgeOrder[1][i]].uv).length
                                    #print ("add",e, d0, d1, uvEdgeOrder)
                                    if abs(d0 - d1) < 1e-8:
                                        if len(uvEdgeOrder[1]) < len(uvEdgeOrder[0]):
                                            uvEdgeOrder[1].append(uv1)
                                        else:
                                            uvEdgeOrder[0].append(uv1)
                                    else:
                                        if d0 < d1:
                                            uvEdgeOrder[0].append(uv1)
                                        else:
                                            uvEdgeOrder[1].append(uv1)
                                
                            #print (i,uv0.uv, uv1.uv)
                    else:
                        error = 1
            else:
                error = 2    
            #print (uvEdgeOrder)
        else:
            error = 3
            
        #print ('error', error)
        #for uv in markedUV:
        #    print ("uv", uv, markedUV[uv],uv_layer[uv].uv)
        if 0 < error:
            if error == 1:
                bpy.ops.error.message('INVOKE_DEFAULT', message = "Something wrong, maybe different Manifolds")   
            else:
                bpy.ops.error.message('INVOKE_DEFAULT', message = "Something wrong, maybe single line couldn't found")   
        else:
            # ein nonManifold bedeutet, das die Linie nicht an der Kante sitzt
            nonManifold = (0 < len(uvEdgeOrder[1]))
            uv = [0,0]
            uv_old = [0,0]
            w0 = uv_layer[uvEdgeOrder[0][-1]].uv - uv_layer[uvEdgeOrder[0][0]].uv
            if nonManifold:
                w1 = uv_layer[uvEdgeOrder[1][-1]].uv - uv_layer[uvEdgeOrder[1][0]].uv
            d = (me.vertices[vertsOrder[0]].co - me.vertices[vertsOrder[1]].co).length
            for i in range(1,len(vertsOrder) - 1):
                #print ("---" , i, uvEdgeOrder[0][i], uvEdgeOrder[1][i])
                ratiod = d / dist
                d += (me.vertices[vertsOrder[i]].co - me.vertices[vertsOrder[i+1]].co).length
                uv_old[0] = verts2uv[uvEdgeOrder[0][i]][1]
                uv[0] = uv_layer[uvEdgeOrder[0][0]].uv + w0*ratiod
                c = 1
                if nonManifold:
                    uv_old[1] = verts2uv[uvEdgeOrder[1][i]][1]
                    uv[1] = uv_layer[uvEdgeOrder[1][0]].uv + w1*ratiod
                    c = 2
                for j in range(c):
                    for uvi in markedUV:
                        #print ('+',uvi, verts2uv[uvi][0], verts2uv[uvEdgeOrder[j][i]][0], verts2uv[uvi][1], uv_old[j])
                        if verts2uv[uvEdgeOrder[j][i]] == verts2uv[uvi] and (verts2uv[uvi][1] - uv_old[j]).length < 1e-7:
                            #print (uvi, uv_layer[uvi].uv)
                            uv_layer[uvi].uv = uv[j]
        #print ("len(markedUV)", len(markedUV))
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}
    
class UVRound(bpy.types.Operator):
    '''uv round'''
    bl_idname = 'uv.round'
    bl_label = 'uvround'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print ("****")
        #debug_show((0,0,0), 'Textc')
        active = bpy.context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')
        interval = int(context.scene.uv_interval)
        me = active.data
        uv_layer = me.uv_layers.active.data
        uv_select_sync = bpy.context.scene.tool_settings.use_uv_select_sync
        for face in me.polygons:
            for i in range(len(face.loop_indices)):
                iv = face.vertices[i]
                v = me.vertices[iv]
                vselect = v.select
                if not uv_select_sync:
                    vselect = uv_layer[face.loop_indices[i]].select    
                if vselect:
                    #print (face.index, iv, face.loop_indices[i])
                    uv = uv_layer[face.loop_indices[i]].uv
                    #print (i,iv, face.loop_indices[i], uv.x, uv.y)
                    uv.x = round(interval * uv.x) / interval
                    uv.y = round(interval * uv.y) / interval
            
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class UVTessellate(bpy.types.Operator):
    '''uv tessellate'''
    bl_idname = 'uv.tessellate'
    bl_label = 'uvtessellate'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print ("****")
        #debug_show((0,0,0), 'Textc')
        active = bpy.context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')
        interval = int(context.scene.uv_interval)
        hideFaces = context.scene.hideFaces
        me = active.data
        uv_layer = me.uv_layers.active.data
        # tri_elem contains a list of all triangles
        # struct like [[vert_0,vert_1,vert_2],[uv_0,uv_1,uv_2]]
        tri_elem = []
        for face in me.polygons:
            if face.select:
                face.hide=hideFaces
                #print ()
                #print (face.index, len(face.vertices), len(face.loop_indices))
                vectors=[]
                for uvi in face.loop_indices:
                    vectors.append(Vector((uv_layer[uvi].uv.x,uv_layer[uvi].uv.y,0.0)))
                tri_tess_list = mathutils.geometry.tessellate_polygon([vectors]) 
                for tri in tri_tess_list:
                    #print (tri, uv_layer[tri[0]].uv, uv_layer[tri[1]].uv, uv_layer[tri[2]].uv)
                    tri_verts = []
                    tri_uv = []
                    for i in tri:
                        tri_verts.append(face.vertices[i])
                        tri_uv.append(face.loop_indices[i])
                    tri_elem.append([tri_verts,tri_uv])
        #print ("Tris", tri_elem)
        
        k = int(context.scene.uv_tessellate)
        count = 0
        acc = 5e-6
        vertices = {}
        for i1 in range(k+1):
            #self.report({"INFO"}, str(i1))
            for i2 in range(k+1):
                x = i1 / k
                y = i2 / k
                #print ('********** ',x,y)
                p = False
                for tri in tri_elem:
                    v0 = uv_layer[tri[1][0]].uv
                    v1 = uv_layer[tri[1][1]].uv
                    v2 = uv_layer[tri[1][2]].uv
                    w1 = v1-v0
                    w2 = v2-v0
                    w0 = Vector((x,y)) - v0
                    det = w1.x*w2.y - w1.y*w2.x
                    detx = w0.x*w2.y - w0.y*w2.x
                    dety = w1.x*w0.y - w1.y*w0.x
                    if det != 0:
                        solu_x = detx / det
                        solu_y = dety / det
                        if -acc <= solu_x and -acc <= solu_y and solu_x+solu_y <= 1.0+acc:
                            #bm = mathutils.geometry.intersect_point_tri_2d(Vector((x,y)),v0,v1,v2)
                            #print (solu_x,solu_y,' = ',v0.x,v0.y,',',v1.x,v1.y,',',v2.x,v2.y,',')
                            ve0 = me.vertices[tri[0][0]].co
                            ve1 = me.vertices[tri[0][1]].co
                            ve2 = me.vertices[tri[0][2]].co
                            we1 = ve1-ve0
                            we2 = ve2-ve0
                            p = ve0 + solu_x * we1 + solu_y * we2
                if p != False:
                    if i1 not in vertices:
                        vertices[i1] = {}
                    vertices[i1][i2]=p
                    count += 1
        
        print ("count",count)
        start = len(me.vertices)
        me.vertices.add(count)
        c = 0
        for i1 in vertices:
            for i2 in vertices[i1]:
                ve = me.vertices[start+c]
                ve.co = vertices[i1][i2]
                vertices[i1][i2] = ve
                c += 1
        
        bm = bmesh.new() 
        bm.from_mesh(me) 
        for i1 in vertices.keys():
            if 0 < len(vertices[i1]):
                for i2 in vertices[i1].keys():
                    verts = []
                    if i1 in vertices and i2 in vertices[i1]:
                        verts.append(bm.verts[vertices[i1][i2].index])
                    if i1 in vertices and i2+1 in vertices[i1]:
                        verts.append(bm.verts[vertices[i1][i2+1].index])
                    if i1+1 in vertices and i2+1 in vertices[i1+1]:
                        verts.append(bm.verts[vertices[i1+1][i2+1].index])
                    if i1+1 in vertices and i2 in vertices[i1+1]:
                        verts.append(bm.verts[vertices[i1+1][i2].index])
                    if 2 < len(verts):
                        #print (verts)
                        bm.faces.new(verts)
        bm.to_mesh(me)
        bm.free()

        me.update()    
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}        
        
class SelectShortest(bpy.types.Operator):
    '''uv select shortest'''
    bl_idname = 'uv.selectshortest'
    bl_label = 'selectshortest'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print ("****")
        #debug_show((0,0,0), 'Textc')
        active = bpy.context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')
        interval = int(context.scene.uv_interval)
        hideFaces = context.scene.hideFaces
        uv_select_sync = bpy.context.scene.tool_settings.use_uv_select_sync
        print ('uv_select_sync',uv_select_sync)
        me = active.data
        uv_layer = me.uv_layers.active.data
        vert2vert = {}
        vert2uv = {}
        # determine length from one vert to its neighbours
        for i in range(len(me.edges)):
            edge = me.edges[i]
            edge_visible = False
            if uv_select_sync:
                edge_visible = not edge.hide
            else:
                edge_visible = active.data.vertices[edge.vertices[0]].select and active.data.vertices[edge.vertices[1]].select
            if edge_visible:
                #print (edge.vertices[0])
                v0 = active.data.vertices[edge.vertices[0]]
                v1 = active.data.vertices[edge.vertices[1]]
                d = (v0.co - v1.co).length
            
                if v0.index not in vert2vert:
                    vert2vert[v0.index] = {}
                if v1.index not in vert2vert[v0.index]:
                    vert2vert[v0.index][v1.index] = d           
                if v1.index not in vert2vert:
                    vert2vert[v1.index] = {}
                if v0.index not in vert2vert[v1.index]:
                    vert2vert[v1.index][v0.index] = d
                
        verts = {}
        start=0
        second=0
        selected = []
        for face in me.polygons:
            for i in range(len(face.loop_indices)):
                iv = face.vertices[i]
                vert = me.vertices[iv]
                vertSelect = vert.select
                if not uv_select_sync:
                   vertSelect = uv_layer[face.loop_indices[i]].select   
                if vertSelect:
                    if iv not in selected:
                        selected.append(iv)
                if iv not in vert2uv:
                    vert2uv[iv] = []
                vert2uv[iv].append(face.loop_indices[i])    
        print ('selected', selected)
        perm = itertools.permutations(selected)
        shortest = {}
        
        if 1 < len(selected) and len(selected) < 9:
            for iv in selected:
                for i in range(len(me.vertices)):
                    vert = me.vertices[i]
                    if not vert.hide:
                        verts[vert.index] = {'d': 10000.0, 'path':[]}
                verts[iv]['d'] = 0.0
                search = [iv]
                c = 1500000
                while 0 < len(search) and 0<c:
                    c -= 1
                    next = search.pop(0)
                    d = verts[next]['d']
                    #print ('***', next)
                    for nvert in vert2vert[next].keys():
                        dp=vert2vert[next][nvert]
                        if d + dp < verts[nvert]['d']:
                            search.append(nvert)
                            verts[nvert]['d'] = d + dp
                            verts[nvert]['path'] = [next] + verts[next]['path']
                for iv2 in selected:
                    if iv != iv2:
                        shortest[str(iv) + '-' + str(iv2)] = verts[iv2]
            bestp = () 
            bestd = 100000.0
            for p in perm:
                d = 0.0
                for i in range(len(p)-1):
                    d += shortest[str(p[i]) + '-' + str(p[i+1])]['d']
                #print (p,d)
                if d < bestd:
                    bestd = d
                    bestp = p[:]
            print ('best', bestp, bestd)
            
            for i in range(len(bestp)-1):
                pp = shortest[str(bestp[i]) + '-' + str(bestp[i+1])]['path']
                for iv in pp:
                    if uv_select_sync:
                        me.vertices[iv].select = True
                    else:
                        for iuv in vert2uv[iv]:
                            uv_layer[iuv].select = True
                            
                
        
                    
                
            
        #for i in range(len(me.vertices)):
        #    vert = me.vertices[i]
        #    if not vert.hide:
        #        verts[vert.index] = {'d': 10000.0, 'path':[]}  
        #        if vert.select:
        #            second = start
        #            start = i
        #if 0 < start and 0 < second:
        #    search = [start]
        #    c = 500000
        #    verts[start]['d'] = 0.0
        #    while 0 < len(search) and 0<c:
        #        c -= 1
        #        next = search.pop(0)
        #        d = verts[next]['d']
        #        #print ('***', next)
        #        for nvert in vert2vert[next].keys():
        #            dp=vert2vert[next][nvert]
        #            if d + dp < verts[nvert]['d']:
        #                search.append(nvert)
        #                verts[nvert]['d'] = d + dp
        #                verts[nvert]['path'] = [next] + verts[next]['path']
        #        #print (search)
        #    for v in verts[second]['path']:
        #        #print (v)
        #        me.vertices[v].select = True
            
        #print (vert2vert)
        #print (verts)
        me.update()    
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}          

class VIEW3D_PT_tools_UVTest(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_idname = 'uv_even'

    bl_label = "uv align raster"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object
        layout = self.layout

        colm = layout.column(align=True)
        row = colm.split(0.25)
        #row.split = 0.15
        w = row.prop(context.scene, "uv_interval")
        #row.split(percentage=0.15)
        #w.alignment = 'RIGHT'
        row.operator("uv.round", text="Round")
        
        colm = layout.column(align=True)
        col = colm.column(align=True)
        col.operator("uv.selectshortest", text="Select Shortest")

        colm = layout.column(align=True)
        col = colm.column(align=True)
        col.operator("uv.linealign", text="Line align")
        
        #col = colm.column(align=True)
        #col.operator("uv.linealign", text="Round")
        
        colm1 = layout.column(align=True)
        colm2 = colm1.column(align=True)
        row2 = colm2.split(0.25)
        w = row2.prop(context.scene, "uv_tessellate")
        row2.operator("uv.tessellate", text="remesh from UV")
        
        colm3 = colm1.column(align=True)
        row3 = colm3.row(align=True)
        row3.prop(context.scene, "hideFaces")
        

classes = [MessageOperator, OkOperator,
    UVTest,
    UVRound,
    UVTessellate,
    SelectShortest,
    VIEW3D_PT_tools_UVTest]   
                    
def register():
    #bpy.utils.register_module(__name__)
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.uv_tessellate = EnumProperty(
		name="",
		description="mesh size on UV-Editor",
		items=[("256","1","1"),
			   ("128","2","2"),
			   ("64","4","4"),
			   ("32","8","8"),
			   ("16","16","16"),
			   ("8","32","32"),
			  ],
		default='32')
    bpy.types.Scene.uv_interval = EnumProperty(
		name="",
		description="uv rounding factor",
		items=[("256","1","1"),
			   ("128","2","2"),
			   ("64","4","4"),
			   ("32","8","8"),
			   ("16","16","16"),
			   ("8","32","32"),
			  ],
		default="8")
    bpy.types.Scene.hideFaces = BoolProperty(
            name="Hide Faces",
            description="Hide the selected Faces",
            default=True,
            )
   
def unregister():
    #bpy.utils.unregister_module(__name__)
    for c in classes:
        bpy.utils.unregister_class(c)
   
if __name__ == "__main__":
    register()   
