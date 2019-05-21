# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3 of the license.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# import/reload all source files
if "bpy" in locals():
    import importlib
    importlib.reload(au)
else:
    from . import amb_utils as au

import bpy

import numpy as np
import bpy
import bmesh
import random
import cProfile, pstats, io
from collections import defaultdict, OrderedDict
import mathutils as mu

#import numba


def op_fraggle(mesh, thres, n):
    verts = read_verts(mesh)
    edges = read_edges(mesh)
    edge_a, edge_b = edges[:,0], edges[:,1]
    #for i in range(len(edge_a)):
    #    fastverts[edge_a[i]] += tvec[i]*thres 
    #    fastverts[edge_b[i]] -= tvec[i]*thres  
    for _ in range(n):
        tvec = verts[edge_b] - verts[edge_a]
        #tvlen = np.linalg.norm(tvec, axis=1)
        #tvec = (tvec.T / tvlen).T 
        verts[edge_a] += tvec * thres 
        verts[edge_b] -= tvec * thres 
    write_verts(mesh, verts)


def op_smooth_mask(verts, edges, mask, n):
    #for e in edges:
    #    edge_c[e[0]] += 1
    #    edge_c[e[1]] += 1
    edge_c = np.zeros(len(verts), dtype=np.int32)
    e0_u, e0_c = np.unique(edges[:,0], return_counts=True)
    e1_u, e1_c = np.unique(edges[:,1], return_counts=True)
    edge_c[e0_u] += e0_c
    edge_c[e1_u] += e1_c
    edge_c = edge_c.T

    new_verts = np.copy(verts)
    new_verts = new_verts.T
    mt1 = (1.0-mask).T
    mt0 = mask.T
    for xc in range(n):
        # <new vert location> = sum(<connected locations>) / <number of connected locations>
        locs = np.zeros((len(verts), 3), dtype=np.float64)
        np.add.at(locs, edges[:,0], verts[edges[:,1]])
        np.add.at(locs, edges[:,1], verts[edges[:,0]])

        locs = locs.T
        locs /= edge_c
        locs *= mt1

        new_verts *= mt0
        new_verts += locs 

    return new_verts.T


class Mesh_Operator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    my_props = []
    prefix = ""
    parent_name = ""

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def payload(self, mesh, context):
        pass

    def invoke(self, context, event):
        self.pr = au.profiling_start()

        # copy property values from panel to operator
        print(self.prefix, self.my_props)
        if self.prefix != "":
            for p in self.my_props:
                opname = self.parent_name + "_" + self.prefix + "_" + p
                setattr(self, p, getattr(context.scene, opname)) 
                print(opname, getattr(context.scene, opname))

        return self.execute(context)

    def execute(self, context):
        # apply modifiers for the active object before mesh actions
        for mod in context.active_object.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError as ex:
                b_print(ex)    

        # run mesh operation
        mesh = context.active_object.data
        self.payload(mesh, context)
        #mesh.update(calc_edges=True)

        au.profiling_end(self.pr)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        
        for p in self.my_props:
            row = col.row()
            row.prop(self, p, expand=True)


def mesh_operator_factory(props, prefix, payload, name, parent_name):
    return type('name', (Mesh_Operator,), 
        {**{'bl_idname' : "object." + parent_name + "_" + prefix,
        'bl_label' : " ".join(prefix.split("_")).capitalize(),
        'my_props' : props.keys(),
        'prefix' : prefix,
        'parent_name' : parent_name,
        'payload' : payload
        }, ** props})


class PanelBuilder:
    def __init__(self, master_name, master_panel, mesh_ops):
        self.panel = {i.prefix : bpy.props.BoolProperty(
                name=i.prefix.capitalize() + " settings",
                description="Display settings of the tool",
                default=False) for i in mesh_ops}      

        self.master_name = master_name
        self.master_panel = master_panel
        self.mesh_ops = mesh_ops

    def create_panel(this):
        class _pt(bpy.types.Panel):
            bl_label = " ".join([i.capitalize() for i in this.master_name.split("_")])
            bl_idname = this.master_panel

            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = "Tools"

            def draw(self, context):
                layout = self.layout
                col = layout.column(align=True)

                for mop in this.mesh_ops:
                    split = col.split(percentage=0.15, align=True)
                    opname = this.master_panel + "_" + mop.prefix
                    
                    if len(mop.props) == 0:
                        split.prop(context.scene, opname, text="", icon='LINK')
                    else:
                        if getattr(context.scene, opname):
                            split.prop(context.scene, opname, text="", icon='DOWNARROW_HLT')
                        else:
                            split.prop(context.scene, opname, text="", icon='RIGHTARROW')

                    opr = split.operator(mop.op.bl_idname, text = " ".join(mop.prefix.split("_")).capitalize())

                    if getattr(context.scene, opname):
                        box = col.column(align=True).box().column()
                        for i, p in enumerate(mop.props):
                            if i%2==0:
                                row = box.row(align=True)
                            row.prop(context.scene, this.master_name+"_"+mop.prefix + "_" + p)
        return _pt

    def register_params(self):
        for mesh_op in self.mesh_ops:
            bpy.utils.register_class(mesh_op.op)
            for k, v in mesh_op.props.items():
                setattr(bpy.types.Scene, mesh_op.parent_name+"_"+mesh_op.prefix+"_"+k, v)

        for k, v in self.panel.items():
            setattr(bpy.types.Scene, self.master_panel+"_"+k, v)

    def unregister_params(self):
        for mesh_op in self.mesh_ops:
            bpy.utils.unregister_class(mesh_op.op)
            for k, v in mesh_op.props.items():
                delattr(bpy.types.Scene, mesh_op.parent_name+"_"+mesh_op.prefix+"_"+k)

        for k, v in self.panel.items():
            delattr(bpy.types.Scene, self.master_panel+"_"+k)


class Master_OP:
    def generate(self):
        pass

    def __init__(self):
        self.props = OrderedDict()
        self.parent_name = "mesh_refine_toolbox"

        self.generate()

        if hasattr(self, 'start_mode'):
            def _wrap(this, mesh, context):
                mode = context.object.mode
                bpy.ops.object.mode_set(mode = self.start_mode)
                self.payload(this, mesh, context)
                bpy.ops.object.mode_set(mode = mode)

            self.op = mesh_operator_factory(self.props, self.prefix, _wrap, self.name, self.parent_name)
        else:
            self.op = mesh_operator_factory(self.props, self.prefix, self.payload, self.name, self.parent_name)

class Masked_Smooth_OP(Master_OP):
    def generate(self):
        self.props['power']  = bpy.props.FloatProperty(name="Power", default=0.7, min=0.0, max=10.0)
        self.props['iter']   = bpy.props.IntProperty(name="Iterations", default=2, min=1, max=10)
        self.props['border'] = bpy.props.BoolProperty(name="Exclude border", default=True)

        self.prefix = "masked_smooth"
        self.name = "OBJECT_OT_Maskedsmooth"
        self.start_mode = 'OBJECT'

        def _pl(self, mesh, context):
            verts = au.read_verts(mesh)
            edges = au.read_edges(mesh)
            norms = au.read_norms(mesh)

            curve = np.abs(au.calc_curvature(verts, edges, norms)-0.5)
            curve = au.mesh_smooth_filter_variable(curve, verts, edges, 1)
            
            curve -= np.min(curve)
            curve /= np.max(curve)
            curve *= 8.0 * self.power
            curve = np.where(curve>1.0, 1.0, curve)

            # don't move border
            if self.border:
                curve = np.where(au.get_nonmanifold_verts(mesh), 1.0, curve)

            new_verts = op_smooth_mask(verts, edges, curve, self.iter)

            au.write_verts(mesh, new_verts)

            mesh.update(calc_edges=True)

        self.payload = _pl

class CropToLarge_OP(Master_OP):
    def generate(self):
        self.props['shells'] = bpy.props.IntProperty(name="Shells", default=1, min=1, max=100)

        self.prefix = "crop_to_large"
        self.name = "OBJECT_OT_CropToLarge"
        self.start_mode = 'EDIT'

        def _pl(self, mesh, context):
            with au.Bmesh_from_edit(mesh) as bm:
                shells = au.mesh_get_edge_connection_shells(bm)
                print(len(shells), "shells")

                for i in range(len(bm.faces)):
                    bm.faces[i].select = True

                delete_this = list(sorted(shells, key=lambda x: -len(x)))[:self.shells]
                for s in delete_this:
                    for f in s:
                        bm.faces[f.index].select = False

            bpy.ops.mesh.delete(type='FACE')

        self.payload = _pl

class MergeTiny_OP(Master_OP):
    def generate(self):
        self.props['threshold'] = bpy.props.FloatProperty(name="Threshold", default=0.02, min=0.0, max=1.0)

        self.prefix = "merge_tiny_faces"
        self.name = "OBJECT_OT_MergeTinyFaces"
        self.start_mode = 'EDIT'

        def _pl(self, mesh, context):
            with au.Bmesh_from_edit(mesh) as bm:
                # thin faces
                collapse_these = []
                avg = sum(f.calc_perimeter() for f in bm.faces)/len(bm.faces)
                for f in bm.faces:
                    if f.calc_perimeter() < avg * self.threshold:
                        collapse_these.extend(f.edges)

                bmesh.ops.collapse(bm, edges=list(set(collapse_these)))
                bmesh.ops.connect_verts_concave(bm, faces=bm.faces)

        self.payload = _pl

class SurfaceSmooth_OP(Master_OP):
    def generate(self):
        self.props['border'] = bpy.props.BoolProperty(name="Exclude border", default=True)
        self.props['iter']   = bpy.props.IntProperty(name="Iterations", default=2, min=1, max=10)

        self.prefix = "surface_smooth"
        self.name = "OBJECT_OT_SurfaceSmooth"
        self.start_mode = 'EDIT'

        def _pl(self, mesh, context):
            with au.Bmesh_from_edit(mesh) as bm:
                limit_verts = set([])
                if self.border:
                    for e in bm.edges:
                        if len(e.link_faces) < 2:
                            limit_verts.add(e.verts[0].index)
                            limit_verts.add(e.verts[1].index)

                for _ in range(self.iter):
                    for v in bm.verts:
                        if v.index in limit_verts:
                            continue

                        ring1 = au.vert_vert(v)
                        projected = []
                        for rv in ring1:
                            nv = rv.co - v.co
                            dist = nv.dot(v.normal)
                            projected.append(rv.co-dist*v.normal)

                        new_loc = mu.Vector([0.0, 0.0, 0.0])
                        for p in projected:
                            new_loc += p
                        new_loc /= len(projected)

                        v.co = new_loc

        self.payload = _pl

class EdgeSmooth_OP(Master_OP):
    def generate(self):
        self.props['border'] = bpy.props.BoolProperty(name="Exclude border", default=True)
        self.props['iter']   = bpy.props.IntProperty(name="Iterations", default=2, min=1, max=10)
        self.props['thres']  = bpy.props.FloatProperty(name="Threshold", default=0.95, min=0.0, max=1.0)

        self.prefix = "edge_smooth"
        self.name = "OBJECT_OT_EdgeSmooth"
        self.start_mode = 'EDIT'

        def _pl(self, mesh, context):
            with au.Bmesh_from_edit(mesh) as bm:
                limit_verts = set([])
                if self.border:
                    for e in bm.edges:
                        if len(e.link_faces) < 2:
                            limit_verts.add(e.verts[0].index)
                            limit_verts.add(e.verts[1].index)

                # record initial normal field
                normals = []
                for v in bm.verts:
                    normals.append(v.normal)

                thr = self.thres

                for _ in range(self.iter):
                    # project surrounding verts to normal plane and move <v> to center
                    new_verts = []
                    for v in bm.verts:
                        new_verts.append(v.co)
                        if v.index in limit_verts:
                            continue

                        v_norm = normals[v.index]
                        ring1 = au.vert_vert(v)

                        # get projected points on plane defined by v_norm
                        projected = []
                        n_diff = []
                        for rv in ring1:
                            nv = rv.co-v.co
                            dist = nv.dot(v_norm)
                            projected.append(rv.co-dist*v_norm)
                            n_diff.append(rv.co-projected[-1])
                            
                        # get approximate co-planar verts
                        coplanar = []
                        discord = []
                        for i, rv in enumerate(ring1):
                            r_norm = normals[rv.index]
                            if r_norm.dot(v_norm) > thr:
                                coplanar.append((i,rv))
                            else:
                                discord.append((i,rv))

                        for i, rv in discord:
                            # project 2-plane intersection instead of location
                            # which direction is the point? (on the v.normal plane)
                            # make it a 1.0 length vector
                            p = projected[i]
                            p = (p-v.co).normalized()

                            # v + n*p = <the normal plane of rv>, find n
                            d = r_norm.dot(p)
                            # if abs(d) > 1e-6:
                            if d > 1e-6:
                                w = v.co - rv.co
                                fac = r_norm.dot(w)/d
                                u = p * fac

                                # sanity limit for movement length
                                # this doesn't actually prevent the explosion
                                # just makes it a little more pleasing to look at 
                                dist = v.co-rv.co
                                if u.length > dist.length:
                                    u = u*dist.length/u.length
                                
                                projected[i] = v.co + u
                                #projected = [v.co + u]
                                break
                            else:
                                projected[i] = v.co

                        final_norm = v_norm
                        for i, rv in coplanar:
                            final_norm += r_norm

                        normals[v.index] = final_norm.normalized()

                        if len(projected) > 0:
                            new_loc = mu.Vector([0.0, 0.0, 0.0])
                            for p in projected:
                                new_loc += p
                            new_verts[-1] = new_loc / len(projected)

                        # move towards average valid 1-ring plane
                        # TODO: this should project to new normal (from coplanar norms), not old v.normal
                        # new_verts[-1] = v.co
                        # if len(coplanar) > 0:
                        #     total = mu.Vector([0.0, 0.0, 0.0])
                        #     for i, rv in coplanar: 
                        #         total += n_diff[i]
                        #     total /= len(coplanar)
                        #     new_verts[-1] += total                     

                            

                    # finally set new values for verts
                    for i, v in enumerate(bm.verts):
                        v.co = new_verts[i]

                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

            #mesh.update(calc_edges=True)

        self.payload = _pl

class Mechanize_OP(Master_OP):
    def generate(self):
        self.props['border'] = bpy.props.BoolProperty(name="Exclude border", default=True)
        self.props['iter']   = bpy.props.IntProperty(name="Iterations", default=2, min=1, max=50)

        self.prefix = "mechanize"
        self.name = "OBJECT_OT_Mechanize"
        self.start_mode = 'EDIT'

        def _pl(self, mesh, context):
            with au.Bmesh_from_edit(mesh) as bm:
                limit_verts = set([])
                if self.border:
                    for e in bm.edges:
                        if len(e.link_faces) < 2:
                            limit_verts.add(e.verts[0].index)
                            limit_verts.add(e.verts[1].index)

                ok_verts = []
                for v in bm.verts:
                    if v.index not in limit_verts:
                        ok_verts.append(v)

                ring1s = []
                for v in bm.verts:
                    ring1s.append(au.vert_vert(v))

                for xx in range(self.iter):
                    print("iteration:", xx+1)
                    for v in ok_verts:
                        ring1 = ring1s[v.index]
                        projected = []
                        distances = []
                        for rv in ring1:
                            nv = rv.co - v.co
                            dist = nv.dot(v.normal)
                            distances.append(abs(dist)/nv.length)
                            projected.append(rv.co-dist*v.normal)

                        # dist_min = min(distances)
                        # for i in range(len(distances)):
                        #     distances[i] += dist_min

                        dist_sum = sum(distances)
                        new_loc = mu.Vector([0.0, 0.0, 0.0])

                        if dist_sum/len(projected) > 0.02:
                            for i, p in enumerate(projected):
                                new_loc += p*distances[i]/dist_sum
                        else:
                            for i, p in enumerate(projected):
                                new_loc += p
                            new_loc /= len(projected)

                        v.co = new_loc

        self.payload = _pl

class CleanupThinFace_OP(Master_OP):
    def generate(self):
        self.props['threshold'] = bpy.props.FloatProperty(name="Threshold", default=0.95, min=0.0, max=1.0)
        self.props['repeat'] = bpy.props.IntProperty(name="Repeat", default=2, min=0, max=10)

        self.prefix = "cleanup_thin_faces"
        self.name = "OBJECT_OT_CleanupThinFace"
        self.start_mode = 'EDIT'

        
        def _pl(self, mesh, context):
            bm = bmesh.from_edit_mesh(mesh)
            thr = self.threshold

            for _ in range(self.repeat):
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

                collapse_these = []
                for f in bm.faces:
                    s = 0.0
                    for e in f.edges:
                        s += e.calc_length()
                    s=s/2*thr
                    for e in f.edges:
                        if e.calc_length() > s:
                            mval = 100000.0
                            sed = None
                            for e in f.edges:
                                cl = e.calc_length()
                                if cl<mval:
                                    mval=cl
                                    sed=e
                            collapse_these.append(sed)
                            break

                #cthese = [bm.faces[i].edges[j] for i, j in res]
                cthese = list(set(collapse_these))
                print(len(cthese), "collapsed edges")
                
                bmesh.ops.collapse(bm, edges=cthese)
                bmesh.ops.connect_verts_concave(bm, faces=bm.faces)
            
            bmesh.update_edit_mesh(mesh)
            mesh.update(calc_edges=True)

        self.payload = _pl

class Cleanup_OP(Master_OP):
    def generate(self):
        #self.props['trifaces'] = bpy.props.BoolProperty(name="Only trifaces", default=False)
        self.props['fillface'] = bpy.props.BoolProperty(name="Fill faces", default=True)
        self.prefix = "cleanup_triface"
        self.name = "OBJECT_OT_CleanupTriface"
        self.start_mode = 'EDIT'
        
        def _pl(self, mesh, context):
            with au.Bmesh_from_edit(mesh) as bm:
                # deselect all
                for v in bm.verts:
                    v.select = False

                # some preprocessing
                #e_len = np.empty((len(bm.edges)), dtype=np.float32)
                #for e in bm.edges:
                #    e_len[e.index] = (e.verts[0].co - e.verts[1].co).length
                #print(np.min(e_len), np.mean(e_len))
                #bmesh.ops.dissolve_degenerate(bm) #, dist=np.min(e_len))

                # find nonmanifold edges
                nm_edges = np.zeros((len(bm.edges)), dtype=np.bool)
                c3_edges = np.zeros((len(bm.edges)), dtype=np.bool)
                for e in bm.edges:
                    facecount = len(e.link_faces)
                    if facecount < 2:
                        nm_edges[e.index] = True
                    elif facecount > 2:
                        c3_edges[e.index] = True

                # A

                # remove all faces, connected to 3+ connection edge, that have nonmanifold edges
                delete_this = []
                for f in bm.faces:
                    nm = False
                    c3 = False
                    for e in f.edges:
                        if nm_edges[e.index]:
                            nm = True
                        if c3_edges[e.index]:
                            c3 = True
                    if nm and c3:
                        delete_this.append(f)               

                bmesh.ops.delete(bm, geom=delete_this, context=5)

                #if self.trifaces == False:
                bm.edges.ensure_lookup_table()
                bm.verts.ensure_lookup_table()

                c3_edges = np.zeros((len(bm.edges)), dtype=np.bool)
                for e in bm.edges:
                    if len(e.link_faces) > 2:
                        c3_edges[e.index] = True

                # B

                # mark non manifold verts (3-face-edge)
                # delete verts, select edges around the deleted vertices
                nonm_verts = set([])
                nonm_edges_idx = np.nonzero(c3_edges)[0]
                nonm_edges = [bm.edges[e] for e in nonm_edges_idx]

                for e in nonm_edges:
                    e.select = True
                    nonm_verts.add(e.verts[0].index)
                    nonm_verts.add(e.verts[1].index)

                for v in nonm_verts:
                    for v in au.vert_vert(bm.verts[v]):
                        v.select = True

                # enum {
                # DEL_VERTS = 1,
                # DEL_EDGES,
                # DEL_ONLYFACES,
                # DEL_EDGESFACES,
                # DEL_FACES,
                # DEL_ALL,
                # DEL_ONLYTAGGED
                # };

                delete_this = [bm.verts[v] for v in nonm_verts]
                bmesh.ops.delete(bm, geom=delete_this, context=1)

                # delete loose edges
                bm.edges.ensure_lookup_table()
                loose_edges = []
                for e in bm.edges:
                    if len(e.link_faces) == 0:
                        loose_edges.append(e)
                bmesh.ops.delete(bm, geom=loose_edges, context=2)

                bm.edges.ensure_lookup_table()
                bm.verts.ensure_lookup_table()

                for e in bm.edges:
                    if len(e.link_faces) > 1 or len(e.link_faces) == 0:
                        e.select = False

                # C

                # fill faces for each loop
                # triangulate
                if self.fillface:
                    all_faces = []
                    for _ in range(2):
                        bm.edges.ensure_lookup_table()
                        loops = au.bmesh_get_boundary_edgeloops_from_selected(bm)
                        new_faces, leftover_loops = au.bmesh_fill_from_loops(bm, loops)

                        all_faces.extend(new_faces)
                        au.bmesh_deselect_all(bm)

                        for l in leftover_loops:
                            for e in l:
                                e.select = True

                        # TODO: loops with 4 edge connections (one vert) could be 
                        #       split into 2 verts which makes the loops simple

                        print(len(leftover_loops))
                        if len(leftover_loops) == 0:
                            break

                    for f in all_faces:
                        f.select = True

                    bmesh.ops.recalc_face_normals(bm, faces=all_faces)
                    res = bmesh.ops.triangulate(bm, faces=all_faces)
                    smooth_verts = []
                    for f in res['faces']:
                        for v in f.verts:
                            smooth_verts.append(v)
                    smooth_verts = list(set(smooth_verts))
                    print(len(smooth_verts), "smoothed verts")
                    bmesh.ops.smooth_vert(bm, verts=smooth_verts, factor=1.0, use_axis_x=True, use_axis_y=True, use_axis_z=True)

                    # cleanup faces with no other face connections
                    bm.faces.ensure_lookup_table()
                    delete_this = []
                    for f in bm.faces:
                        no_conn = True
                        for e in f.edges:
                            if e.is_manifold:
                                no_conn = False
                        if no_conn:
                            delete_this.append(f)     

                    print(len(delete_this), "faces deleted after triface cleanup")
                    bmesh.ops.delete(bm, geom=delete_this, context=5)


        self.payload = _pl

class Test_OP(Master_OP):
    def generate(self):
        self.props['test'] = bpy.props.FloatProperty(name="Test", default=0.02, min=0.0, max=1.0)

        self.prefix = "test"
        self.name = "OBJECT_OT_Test"

        #@numba.jit
        def _pl(self, mesh, context):
            print("hello")
            
            # def sum2(two_dimensional_array):    
            #     result = 0.0
            #     J, I = two_dimensional_array.shape    
            #     for i in range(J):
            #         for j in range(I):
            #             result += two_dimensional_array[i,j]    
            #     return result
            # print(sum2(np.array([[1,2],[3,4]])))
            
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.verts.ensure_lookup_table()

            for v in bm.verts:
                bm.verts[v.index].co += mu.Vector([0.1,0.0,0.0])

            bm.to_mesh(mesh)

            bm.free()

            mesh.update(calc_edges=True)

        self.payload = _pl


bl_info = {
    "name": "Mesh Refine Toolbox",
    "category": "Mesh",
    "description": "Various tools for mesh processing",
    "author": "ambi",
    "location": "3D view > Tools",
    "version": (1, 1, 0),
    "blender": (2, 79, 0)
}


pbuild = PanelBuilder("mesh_refine_toolbox", "mesh_refine_toolbox_panel", \
    #[Mechanize_OP(), SurfaceSmooth_OP(), EdgeSmooth_OP(), MergeTiny_OP(), CleanupThinFace_OP(), Cleanup_OP(), CropToLarge_OP()])
    [Mechanize_OP(), SurfaceSmooth_OP(), Masked_Smooth_OP(), MergeTiny_OP(), CleanupThinFace_OP(), Cleanup_OP(), CropToLarge_OP()])
OBJECT_PT_ToolsAMB = pbuild.create_panel()

def register():
    pbuild.register_params()
    bpy.utils.register_class(OBJECT_PT_ToolsAMB)

def unregister():
    pbuild.unregister_params()
    bpy.utils.unregister_class(OBJECT_PT_ToolsAMB)
    

