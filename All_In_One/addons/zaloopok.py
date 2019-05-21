bl_info = {
    "name": "Zaloopok",
    "author": "nemyax",
    "version": (0, 6, 20170206),
    "blender": (2, 7, 6),
    "location": "",
    "description": "Adaptations of a few tools from Wings3D",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
from bpy.props import FloatProperty, EnumProperty
import bmesh, math, mathutils as mu

### UV tools

def get_any(someset):
    for i in someset:
        return i

def reset_uvs(context, coords):
    bm = bmesh.from_edit_mesh(context.active_object.data)
    uv = bm.loops.layers.uv.verify()
    for l in coords:
        l[uv].uv = coords[l]
    context.active_object.data.update()

def initial_uvs(frags, bm):
    uv = bm.loops.layers.uv.verify()
    coords = {}
    for frag in frags:
        for l in frag:
            coords[l] = l[uv].uv.copy()
    return coords

def same_uv(l, uv):
    return set([a for a in l.vert.link_loops if a[uv].uv == l[uv].uv])

def uv_gather_sync(bm):
    hes = set()
    if bpy.context.scene.tool_settings.mesh_select_mode[2]:
        for f in bm.faces:
            if f.select:
                for l in f.loops:
                    hes.add(l)
    else:
        for e in bm.edges:
            if e.select:
                for l in e.link_loops:
                    if l.edge == e:
                        hes.add(l)
    return hes

def uv_gather_nonsync(bm):
    uv = bm.loops.layers.uv.verify()
    hes = set()
    for f in bm.faces:
        for l in f.loops:
            if l[uv].select and l.link_loop_next[uv].select:
                hes.add(l)
    return hes

def cache_uvs(ls, uv):
    lookup = {}
    for l in ls:
        lookup[l] = same_uv(l, uv)
    return lookup

def extract_frag(ls, lookup, n_lookup):
    done = set()
    todo = set()
    todo.add(get_any(ls))
    while todo:
        a = todo.pop()
        done.add(a)
        ls.discard(a)
        for b in lookup[a]:
            pb = b.link_loop_prev
            if pb in ls:
                todo.add(pb)
                ls.discard(pb)
            if b in lookup:
                done.add(b)
                ls.discard(b)
                nb = b.link_loop_next
                for d in n_lookup[nb]:
                    if d in lookup and not (d in done):
                        todo.add(d)
                        ls.discard(d)
                    pd = d.link_loop_prev
                    if pd in lookup and not (pd in done):
                        todo.add(pd)
                        ls.discard(pd)
    return done
            
def partial_frags(bm, uv):
    if bpy.context.scene.tool_settings.use_uv_select_sync:
        hes = uv_gather_sync(bm)
    else:
        hes = uv_gather_nonsync(bm)
    lookup = cache_uvs(hes, uv)
    n_lookup = cache_uvs([o.link_loop_next for o in hes], uv)
    frags = []
    done = set()
    while hes:
        frag = extract_frag(hes, lookup, n_lookup)
        vs = set()
        for a in frag:
            vs |= set(a.edge.verts)
            if len(vs) > 1:
                frags.append(frag)
                break
    return frags

def detect_uv_frags(bm):
    uv = bm.loops.layers.uv.verify()
    frags = partial_frags(bm, uv)
    for frag in frags:
        more = set()
        for a in frag:
            more |= same_uv(a, uv)
            more |= same_uv(a.link_loop_next, uv)
        frag |= more
    return frags

def erase_dupes(m1, m2, frag, uv):
    dupes = set()
    test = (m1.vert,m1[uv].uv[:],m2.vert,m2[uv].uv[:])
    for c in frag:
        d   = c.link_loop_next
        cv  = c.vert
        dv  = d.vert
        cco = c[uv].uv[:]
        dco = d[uv].uv[:]
        if test == (cv,cco,dv,dco) or test == (dv,dco,cv,cco):
            dupes.add(c)
    frag -= dupes

def extend_chain(item, frag, uv, right_way):
    l1, l2, fwd = item
    test1 = (l1.vert,l1[uv].uv[:])
    test2 = (l2.vert,l2[uv].uv[:])
    match = None
    for a in frag:
        b = a.link_loop_next
        conn_a = (a.vert,a[uv].uv[:])
        conn_b = (b.vert,b[uv].uv[:])
        if right_way:
            if fwd:
                if test2 == conn_a:
                    match = (a,b,True)
                    break
                elif test2 == conn_b:
                    match = (a,b,False)
                    break
            else:
                if test1 == conn_a:
                    match = (a,b,True)
                    break
                elif test1 == conn_b:
                    match = (a,b,False)
                    break
        else:
            if fwd:
                if test1 == conn_b:
                    match = (a,b,True)
                    break
                elif test1 == conn_a:
                    match = (a,b,False)
                    break
            else:
                if test2 == conn_b:
                    match = (a,b,True)
                    break
                elif test2 == conn_a:
                    match = (a,b,False)
                    break
    if not match:
        return
    erase_dupes(match[0], match[1], frag, uv)
    return match

def start_chain(frag, uv):
    l1 = frag.pop()
    l2 = l1.link_loop_next
    erase_dupes(l1, l2, frag, uv)
    return[(l1,l2,True)]

def prep_chain(chain, uv):
    order = [list(same_uv(lnk[not lnk[2]], uv)) for lnk in chain]
    ch_e = chain[-1]
    which_uv = int(ch_e[2])
    order.append(list(same_uv(ch_e[which_uv], uv)))
    is_closed = False
    if order[0] == order[-1]:
        is_closed = True
    return is_closed, order

def order_links(frag, uv):
    chain = start_chain(frag, uv)
    start_found = end_found = False
    while frag and not end_found:
        lst = extend_chain(chain[-1], frag, uv, True)
        if lst:
            chain.append(lst)
        else:
            end_found = True
    while frag and not start_found:
        fst = extend_chain(chain[0], frag, uv, False)
        if fst:
            chain.insert(0, fst)
        else:
            start_found = True
    return prep_chain(chain, uv)

def has_fork(frag, uv):
    for a in frag:
        same = same_uv(a, uv)
        conn = set()
        for b in same & frag:
            conn.add(b.link_loop_next)
        for c in same:
            prv = c.link_loop_prev
            if prv in frag:
                conn.add(prv)
        uvs = set([(c.vert,c[uv].uv[:]) for c in conn])
        if len(uvs) > 2:
            return True
    return False

def frag_to_chain(frag, uv):
    if has_fork(frag, uv):
        return None, None
    return order_links(frag, uv)

def frags_to_chains(frags, uv):
    result = []
    for a in frags:
        is_closed, ch = frag_to_chain(a, uv)
        if ch:
            result.append((is_closed,ch))
    return result

def arrange_uv_chain(ch, uv, equalize):
    is_closed, order = ch
    if is_closed:
        circ_uv_chain(order, uv, equalize)
    else:
        distrib_uv_chain(order, uv, equalize)

def arrange_uv_chains(bm, equalize):
    uv = bm.loops.layers.uv.active
    chains = frags_to_chains(partial_frags(bm, uv), uv)
    for ch in chains:
        arrange_uv_chain(ch, uv, equalize)

def circ_uv_chain(order, uv, equalize):
    coords = [b[0][uv].uv for b in order]
    n = len(coords)
    c = mu.Vector((
        sum([v[0] for v in coords]) / n,
        sum([v[1] for v in coords]) / n))
    r = sum([(v-c).magnitude for v in coords]) / n
    s = (order[0][0][uv].uv - c).normalized()
    if equalize:
        avg = math.radians(360) / (n - 1)
        if s.angle_signed(coords[1] - c) >= 0:
            avg *= -1
        angles = [avg*i for i in range(len(coords))]
    else:
        angles = []
        for co in coords:
            angles.append(-s.angle_signed(co - c))
    for a, ls in zip(angles, order):
        co = ((mu.Matrix.Rotation(a, 2)) * s) * r + c
        for l in ls:
            l[uv].uv = co

def distrib_uv_chain(order, uv, equalize):
    n = len(order)
    s = order[0][0][uv].uv.copy()
    d = order[-1][0][uv].uv - s
    avg = d.copy() / (n - 1)
    if equalize:
        vecs = [avg] * (n - 1)
    else:
        dist = d.magnitude
        if not dist:
            vecs = [mu.Vector((0.0,0.0))] * (n - 1)
        else:
            vecs = []
            for i in range(n - 1):
                vecs.append(order[i+1][0][uv].uv - order[i][0][uv].uv)
            total = sum([a.magnitude for a in vecs])
            for i in range(len(vecs)):
                vecs[i] = d * (vecs[i].magnitude / total)
    for ls, vec in zip(order, vecs):
        for a in ls:
            a[uv].uv = s
        s += vec

def xform_uv_frags(mtx, geom, bm):
    uv = bm.loops.layers.uv.verify()
    for center, frag in geom:
        for l in frag:
            l[uv].uv = center + mtx * (l[uv].uv - center)
    return bm

def prep_frags(frags, bm):
    result = []
    uv = bm.loops.layers.uv.verify()
    for frag in frags:
        uvs = [l[uv].uv[:] for l in frag]
        min_u = min([a[0] for a in uvs])
        max_u = max([a[0] for a in uvs])
        min_v = min([a[1] for a in uvs])
        max_v = max([a[1] for a in uvs])
        center = mu.Vector(((min_u + max_u) * 0.5, (min_v + max_v) * 0.5))
        result.append((center,frag))
    return result

def scale_uv_frags(factor_x, factor_y, frags, bm):
    mtx = mu.Matrix.Scale(factor_x, 2) * mu.Matrix.Scale(factor_y, 2)
    return xform_uv_frags(mtx, frags, bm)

### Mesh editing tools

def mirror(bm):
    copy_lookup = {}
    orig_faces = bm.faces[:]
    for f in orig_faces:
        if f.select:
            bmcp = bmesh.ops.duplicate(bm, geom=orig_faces)
            for fcp in bmcp['geom']:
                if type(fcp) == bmesh.types.BMFace:
                    fcp.normal_flip()
            copy_lookup[f] = bmcp
    for f in copy_lookup:
        tm = mu.Matrix.Translation(f.calc_center_median())
        sm = mu.Matrix.Scale(-1.0, 4, f.normal)
        cp = copy_lookup[f]
        bmesh.ops.transform(bm,
            matrix=tm * sm * tm.inverted(),
            verts=[v for v in cp['geom'] if type(v) == bmesh.types.BMVert])
        weld_map = {}
        for v in f.verts:
            vc = cp['vert_map'][v]
            weld_map[vc] = v
        bm.faces.remove(cp['face_map'][f])
        bm.faces.remove(f)
        bmesh.ops.weld_verts(bm, targetmap=weld_map)

def put_on(to, at, bm, turn):
    to_xyz = to.calc_center_median_weighted()
    at_xyz = at.calc_center_median_weighted()
    turn_mtx = mu.Matrix.Rotation(math.radians(turn), 4, 'Z')
    src_mtx = at.normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    trg_mtx = to.normal.to_track_quat('-Z', 'Y').to_matrix().to_4x4()
    mtx =  mu.Matrix.Translation(to_xyz) * \
        trg_mtx * turn_mtx * \
        src_mtx.inverted() * \
        mu.Matrix.Translation(-at_xyz)
    piece = extend_region(at, bm)
    bmesh.ops.transform(bm,
        matrix=mtx, space=mu.Matrix.Identity(4), verts=piece)
    return bm

def extend_region(f, bm):
    inside = set()
    es = set(f.edges[:])
    while es:
        e = es.pop()
        inside.add(e)
        les = set(e.verts[0].link_edges[:] + e.verts[1].link_edges[:])
        les.difference_update(inside)
        es.update(les)
    vs = set()
    for e in inside:
        vs.update(set(e.verts[:]))
    return list(vs)

def connect(bm):
    sel = set([a for a in bm.edges if a.select])
    es = set()
    for e in sel:
        e.select = False
        fs = set()
        for lf in e.link_faces:
            if len(set(lf.edges[:]).intersection(sel)) > 1:
                fs.add(lf)
        if fs:
            es.add(e)
    r1 = bmesh.ops.bisect_edges(bm, edges=list(es), cuts=1)['geom_split']
    vs = [a for a in r1 if type(a) == bmesh.types.BMVert]
    r2 = bmesh.ops.connect_verts(bm, verts=vs, check_degenerate=True)['edges']
    for e in r2:
        e.select = True
    return bm

def loop_extension(edge, vert):
    candidates = vert.link_edges[:]
    if len(vert.link_loops) == 4 and vert.is_manifold:
        cruft = [edge]
        for l in edge.link_loops:
            cruft.extend([l.link_loop_next.edge, l.link_loop_prev.edge])
        return [e for e in candidates if e not in cruft][0]
    else:
        return

def loop_end(edge):
    v1, v2 = edge.verts[:]
    return not loop_extension(edge, v1) \
        or not loop_extension(edge, v2)

def ring_extension(edge, face):
    if len(face.verts) == 4:
        target_verts = [v for v in face.verts if v not in edge.verts]
        return [e for e in face.edges if
            target_verts[0] in e.verts and
            target_verts[1] in e.verts][0]
    else:
        return

def ring_end(edge):
    faces = edge.link_faces[:]
    border = len(faces) == 1
    non_manifold = len(faces) > 2
    dead_ends = map(lambda x: len(x.verts) != 4, faces)
    return border or non_manifold or any(dead_ends)

def unselected_loop_extensions(edge):
    v1, v2 = edge.verts
    ext1, ext2 = loop_extension(edge, v1), loop_extension(edge, v2)
    return [e for e in [ext1, ext2] if e and not e.select]

def unselected_ring_extensions(edge):
    return [e for e in 
        [ring_extension(edge, f) for f in edge.link_faces]
        if e and not e.select]

def entire_loop(edge):
    e = edge
    v = edge.verts[0]
    loop = [edge]
    going_forward = True
    while True:
        ext = loop_extension(e, v)
        if ext:
            if going_forward:
                if ext == edge: # infinite
                    return [edge] + loop + [edge]
                else: # continue forward
                    loop.append(ext)
            else: # continue backward
                loop.insert(0, ext)
            v = ext.other_vert(v)
            e = ext
        else: # finite and we've reached an end
            if going_forward: # the first end
                going_forward = False
                e = edge
                v = edge.verts[1]
            else: # the other end
                return loop

def partial_ring(edge, face):
    part_ring = []
    e, f = edge, face
    while True:
        ext = ring_extension(e, f)
        if not ext:
            break
        part_ring.append(ext)
        if ext == edge:
            break
        if ring_end(ext):
            break
        else:
            f = [x for x in ext.link_faces if x != f][0]
            e = ext
    return part_ring

def entire_ring(edge):
    fs = edge.link_faces
    ring = [edge]
    if len(fs) and len(fs) < 3:
        dirs = [ne for ne in [partial_ring(edge, f) for f in fs] if ne]
        if dirs:
            if len(dirs) == 2 and set(dirs[0]) != set(dirs[1]):
                [ring.insert(0, e) for e in dirs[1]]
            ring.extend(dirs[0])
    return ring

def complete_associated_loops(edges):
    loops = []
    for e in edges:
        if not any([e in l for l in loops]):
            loops.append(entire_loop(e))
    return loops

def complete_associated_rings(edges):
    rings = []
    for e in edges:
        if not any([e in r for r in rings]):
            rings.append(entire_ring(e))
    return rings

def grow_loop(context):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    selected_edges = [e for e in bm.edges if e.select]
    loop_exts = []
    for se in selected_edges:
        loop_exts.extend(unselected_loop_extensions(se))
    for le in loop_exts:
        le.select = True
    mesh.update()
    return {'FINISHED'}

def grow_ring(context):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    selected_edges = [e for e in bm.edges if e.select]
    ring_exts = []
    for se in selected_edges:
        ring_exts.extend(unselected_ring_extensions(se))
    for re in ring_exts:
        re.select = True
    mesh.update()
    return {'FINISHED'}

def group_selected(edges):
    chains = [[]]
    for e in edges:
        if e.select:
            chains[-1].extend([e])
        else:
            chains.append([])
    return [c for c in chains if c]

def group_unselected(edges):
    gaps = [[]]
    for e in edges:
        if not e.select:
            gaps[-1].extend([e])
        else:
            gaps.append([])
    return [g for g in gaps if g != []]

def shrink_loop(context):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    selected_edges = [e for e in bm.edges if e.select]
    loop_ends = []
    for se in selected_edges:
        for v in [se.verts[0], se.verts[1]]:
            le = loop_extension(se, v)
            if not le or not le.select:
                loop_ends.append(se)
    loop_ends_unique = list(set(loop_ends))
    if len(loop_ends_unique):
        for e in loop_ends_unique:
            e.select = False
    mesh.update()
    return {'FINISHED'}

def shrink_ring(context):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    selected_edges = [e for e in bm.edges if e.select]
    ring_ends = []
    for r in complete_associated_rings(selected_edges):
        chains = group_selected(r)
        for c in chains:
            ring_ends.append(c[0])
            ring_ends.append(c[-1])
    for e in list((set(ring_ends))):
        e.select = False
    mesh.update()
    return {'FINISHED'}

def select_bounded_loop(context):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    selected_edges = [e for e in bm.edges if e.select]
    for l in complete_associated_loops(selected_edges):
        gaps = group_unselected(l)
        new_sel = []
        if l[0] == l[-1]: # loop is infinite
            sg = sorted(gaps,
                key = lambda x: len(x),
                reverse = True)
            if len(sg) > 1 and len(sg[0]) > len(sg[1]): # single longest gap
                final_gaps = sg[1:]
            else:
                final_gaps = sg
        else: # loop is finite
            tails = [g for g in gaps
                if any(map(lambda x: loop_end(x), g))]
            nontails = [g for g in gaps if g not in tails]
            if nontails:
                final_gaps = nontails
            else:
                final_gaps = gaps
        for g in final_gaps:
            new_sel.extend(g)
        for e in new_sel:
            e.select = True
    mesh.update()
    return {'FINISHED'}

def select_bounded_ring(context):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    selected_edges = [e for e in bm.edges if e.select]
    for r in complete_associated_rings(selected_edges):
        gaps = group_unselected(r)
        new_sel = []
        if r[0] == r[-1]: # ring is infinite
            sg = sorted(gaps,
                key = lambda x: len(x),
                reverse = True)
            if len(sg) > 1 and len(sg[0]) > len(sg[1]): # single longest gap
                final_gaps = sg[1:]
            else:
                final_gaps = sg
        else: # ring is finite
            tails = [g for g in gaps
                if any(map(lambda x: ring_end(x), g))]
            nontails = [g for g in gaps if g not in tails]
            if nontails:
                final_gaps = nontails
            else:
                final_gaps = gaps
        for g in final_gaps:
            new_sel.extend(g)
        for e in new_sel:
            e.select = True
    mesh.update()
    return {'FINISHED'}

def extract_mesh_frag(es):
    frag = set()
    todo = set()
    todo.add(es.pop())
    while todo:
        e = todo.pop()
        frag.add(e)
        v1, v2 = e.verts
        more = [a for a in v1.link_edges[:]+v2.link_edges[:] if a.select]
        todo |= (set(more) - frag)
    return frag

def mesh_frags(bm):
    todo = set([e for e in bm.edges if e.select])
    frags = []
    while todo:
        frag = extract_mesh_frag(todo)
        frags.append(frag)
        todo -= frag
    return frags

def vert_chain(frag):
    fst = get_any(frag)
    e_chain = [fst]
    v_chain = fst.verts[:]
    fwd = True
    while True:
        end_e = e_chain[-1]
        end_v = v_chain[-1]
        ways = [a for a in end_v.link_edges if a in frag]
        if len(ways) > 2:
            return None, None
        elif len(ways) == 1:
            if fwd:
                e_chain.reverse()
                v_chain.reverse()
                fwd = False
            else:
                return False, v_chain
        else:
            if end_v == v_chain[0]:
                return True, v_chain
            e1, e2 = ways
            if e1 == end_e:
                nxt_e = e2
            else:
                nxt_e = e1
            e_chain.append(nxt_e)
            v_chain.append(nxt_e.other_vert(end_v))

def vert_chains(frags):
    chains = []
    for frag in frags:
        is_closed, chain = vert_chain(frag)
        if chain:
            chains.append((is_closed, chain))
    return chains

def arrange_edges(context, equalize):
    mesh = context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    frags = mesh_frags(bm)
    for is_closed, chain in vert_chains(frags):
        if is_closed:
            circularize(chain, equalize)
        else:
            string_along(chain, equalize)
    context.active_object.data.update()
    return {'FINISHED'}

def circularize(ovs, equalize):
    n = len(ovs)
    center = mu.Vector((
        sum([v.co[0] for v in ovs]) / n,
        sum([v.co[1] for v in ovs]) / n,
        sum([v.co[2] for v in ovs]) / n))
    dists = [(v.co - center).magnitude for v in ovs]
    avg_d = (max(dists) + min(dists)) * 0.5
    crosses = []
    for v in ovs:
        pv = ovs[ovs.index(v)-1]
        crosses.append((pv.co - center).cross(v.co - center))
    nrm = mu.Vector((
        sum([a[0] for a in crosses]) / n,
        sum([a[1] for a in crosses]) / n,
        sum([a[2] for a in crosses]) / n)).normalized()
    nrm2 = nrm.cross(ovs[0].co - center)
    offset = -nrm.cross(nrm2)
    offset.magnitude = avg_d
    doublepi = 6.283185307179586
    if equalize:
        quats = [mu.Quaternion(nrm, doublepi / (n - 1))] * n
    else:
        if not avg_d:
            quats = [mu.Quaternion((1.0, 0.0, 0.0, 0.0))] * n
        else:
            vecs = [ovs[i+1].co - ovs[i].co for i in range(n - 1)]
            total = sum([vec.magnitude for vec in vecs])
            quats = []
            for vec in vecs:
                a = doublepi * (vec.magnitude / total)
                quats.append(mu.Quaternion(nrm, a))
    for v, quat in zip(ovs, quats):
        v.co = center + offset
        offset.rotate(quat)

def string_along(ovs, equalize):
    n = len(ovs)
    s = ovs[0].co.copy()
    d = ovs[-1].co - s
    avg = d / (n - 1)
    if equalize:
        vecs = [avg] * n
    else:
        dist = d.magnitude
        if not dist:
            vecs = [mu.Vector((0.0,0.0,0.0))] * (n - 1)
        else:
            vecs = []
            for i in range(n - 1):
                vecs.append(ovs[i+1].co - ovs[i].co)
            total = sum([a.magnitude for a in vecs])
            for i in range(len(vecs)):
                vecs[i] = d * (vecs[i].magnitude / total)
    for v, vec in zip(ovs, vecs):
        v.co = s
        s += vec

class GrowLoop(bpy.types.Operator):
    bl_idname = "mesh.z_grow_loop"
    bl_label = "Grow Loop"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return grow_loop(context)

class ShrinkLoop(bpy.types.Operator):
    bl_idname = "mesh.z_shrink_loop"
    bl_label = "Shrink Loop"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return shrink_loop(context)

class GrowRing(bpy.types.Operator):
    bl_idname = "mesh.z_grow_ring"
    bl_label = "Grow Ring"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return grow_ring(context)

class ShrinkRing(bpy.types.Operator):
    bl_idname = "mesh.z_shrink_ring"
    bl_label = "Shrink Ring"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return shrink_ring(context)

class SelectBoundedLoop(bpy.types.Operator):
    bl_idname = "mesh.z_select_bounded_loop"
    bl_label = "Select Bounded Loop"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return select_bounded_loop(context)

class SelectBoundedRing(bpy.types.Operator):
    bl_idname = "mesh.z_select_bounded_ring"
    bl_label = "Select Bounded Ring"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        return select_bounded_ring(context)

class ToFaces(bpy.types.Operator):
    bl_idname = "mesh.z_to_faces"
    bl_label = "Convert vertex or edge selection to face selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH'
            and (sm == (True, False, False)
                or sm == (False, True, False)))

    def execute(self, context):
        bpy.ops.mesh.select_mode(use_expand=True, type='FACE')
        context.tool_settings.mesh_select_mode = (False, False, True)
        context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        return {'FINISHED'}

class ToEdges(bpy.types.Operator):
    bl_idname = "mesh.z_to_edges"
    bl_label = "Convert vertex or face selection to edge selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH'
            and (sm == (True, False, False)
                or sm == (False, False, True)))

    def execute(self, context):
        exp = False
        if context.tool_settings.mesh_select_mode[0]:
            exp = True
        bpy.ops.mesh.select_mode(use_expand=exp, type='EDGE')
        context.tool_settings.mesh_select_mode = (False, True, False)
        context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
        return {'FINISHED'}

class ToVerts(bpy.types.Operator):
    bl_idname = "mesh.z_to_verts"
    bl_label = "Convert edge or face selection to vertex selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH'
            and (sm == (False, True, False)
                or sm == (False, False, True)))

    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=True, type='VERT')
        context.tool_settings.mesh_select_mode = (True, False, False)
        context.space_data.pivot_point = 'MEDIAN_POINT'
        return {'FINISHED'}

class ContextDelete(bpy.types.Operator):
    bl_idname = "mesh.z_delete_mode"
    bl_label = "Delete Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        modes = []
        for a, b in zip(
            ['VERT','EDGE','FACE'],
            context.tool_settings.mesh_select_mode[:]):
            if b:
                modes.append(a)
        for m in reversed(modes):
            bpy.ops.mesh.delete(type=m)
        return {'FINISHED'}

class EdgeEq(bpy.types.Operator):
    '''Equalize the selected contiguous edges.'''
    bl_idname = "mesh.eq_edges"
    bl_label = 'Equalize'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH'
            and (sm == (False, True, False)))

    def execute(self, context):
        return arrange_edges(context, equalize=True)

class EdgeLineUp(bpy.types.Operator):
    '''Line up the selected contiguous edges.'''
    bl_idname = "mesh.line_up_edges"
    bl_label = 'Line Up'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH'
            and (sm == (False, True, False)))

    def execute(self, context):
        return arrange_edges(context, equalize=False)

class EdgeConnect(bpy.types.Operator):
    '''Connect the selected edges.'''
    bl_idname = "mesh.z_connect"
    bl_label = 'Connect'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH'
            and (sm == (False, True, False)))

    def execute(self, context):
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        connect(bm)
        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}

class PutOn(bpy.types.Operator):
    bl_idname = "mesh.z_put_on"
    bl_label = "Put On"
    bl_options = {'REGISTER', 'UNDO'}
    turn = FloatProperty(
            name="Turn angle",
            description="Turn by this angle after placing",
            min=-180.0, max=180.0,
            default=0.0)

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        sel_fs = [f for f in bm.faces if f.select]
        where_to = bm.faces.active
        result = {'CANCELLED'}
        if len(sel_fs) == 2 and where_to in sel_fs:
            f1, f2 = sel_fs
            where_at = f1 if f2 == where_to else f2
            bm = put_on(where_to, where_at, bm, self.turn)
            bmesh.update_edit_mesh(mesh)
            result = {'FINISHED'}
        return result

class Mirror(bpy.types.Operator):
    bl_idname = "mesh.z_mirror"
    bl_label = "Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        mirror(bm)
        bmesh.update_edit_mesh(mesh)
        return {'FINISHED'}

### UV ops

class RotateUVFragments(bpy.types.Operator):
    bl_idname = "uv.z_rotate_fragments"
    bl_label = "Rotate Fragments"
    bl_options = {'GRAB_CURSOR', 'BLOCKING', 'REGISTER', 'UNDO'}
    angle = FloatProperty(
        name="Angle",
        description="Angle to rotate fragments by",
        min=-100000.0,
        max=100000.0,
        default=0.0)

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            reset_uvs(context, self.initial_uvs)
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE':
            mult = math.radians(1)
            if event.ctrl:
                mult = math.radians(5)
            elif event.shift:
                mult = math.radians(0.1)
            self.angle = math.degrees(
                (event.mouse_y - self.initial_pos) * mult)
            self.execute(context)
        elif event.type in {'RET', 'LEFTMOUSE'}:
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'IMAGE_EDITOR':
            self.initial_pos = event.mouse_y
            bm = bmesh.from_edit_mesh(context.active_object.data)
            frags = detect_uv_frags(bm)
            self.initial_uvs = initial_uvs(frags, bm)
            if frags:
                self.bm = bm
                self.geom = prep_frags(frags, bm)
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
        return {'CANCELLED'}

    def execute(self, context):
        reset_uvs(context, self.initial_uvs)
        mtx = mu.Matrix.Rotation(math.radians(self.angle), 2)
        xform_uv_frags(mtx, self.geom, self.bm)
        bmesh.update_edit_mesh(context.active_object.data)
        # context.active_object.data.update()
        return {'FINISHED'}

class ScaleUVFragments(bpy.types.Operator):
    bl_idname = "uv.z_scale_fragments"
    bl_label = "Scale Fragments"
    bl_options = {'GRAB_CURSOR', 'BLOCKING', 'REGISTER', 'UNDO'}
    factor = FloatProperty(
        name="Angle",
        description="Scale factor for fragments",
        min=-100000.0,
        max=100000.0,
        default=0.0)
    axis = EnumProperty(
        name = "Axis",
        description="Axis to rotate about",
        items = [
            ('U', "U", ""),
            ('V', "V", ""),
            ('UV', "Uniform", "")],
        default = 'UV')

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            reset_uvs(context, self.initial_uvs)
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE':
            mult = 0.1
            if event.ctrl:
                mult = 0.5
            elif event.shift:
                mult = 0.01
            self.factor = 1.0 + (event.mouse_y - self.initial_pos) * mult
            self.execute(context)
        elif event.type in {'X','U'} and event.value == 'RELEASE':
            self.axis = 'UV' if self.axis == 'U' else 'U'
            reset_uvs(context, self.initial_uvs)
            self.initial_pos = event.mouse_y
        elif event.type in {'Y','V'} and event.value == 'RELEASE':
            self.axis = 'UV' if self.axis == 'V' else 'V'
            reset_uvs(context, self.initial_uvs)
            self.initial_pos = event.mouse_y
        elif event.type in {'RET', 'LEFTMOUSE'}:
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'IMAGE_EDITOR':
            self.initial_pos = event.mouse_y
            bm = bmesh.from_edit_mesh(context.active_object.data)
            frags = detect_uv_frags(bm)
            self.initial_uvs = initial_uvs(frags, bm)
            if frags:
                self.bm = bm
                self.geom = prep_frags(frags, bm)
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
        return {'CANCELLED'}

    def execute(self, context):
        reset_uvs(context, self.initial_uvs)
        if self.axis == 'U':
            mtx = mu.Matrix.Scale(self.factor, 2, mu.Vector((1.0,0.0)))
        elif self.axis == 'V':
            mtx = mu.Matrix.Scale(self.factor, 2, mu.Vector((0.0,1.0)))
        else:
            mtx = mu.Matrix.Scale(self.factor, 2)
        xform_uv_frags(mtx, self.geom, self.bm)
        bmesh.update_edit_mesh(context.active_object.data)
        return {'FINISHED'}

class EqualizeUVChains(bpy.types.Operator):
    bl_idname = "uv.equalize"
    bl_label = "Equalize UV Chains"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        arrange_uv_chains(bm, equalize=True)
        bmesh.update_edit_mesh(context.active_object.data)
        return {'FINISHED'}

class LineUpUVChains(bpy.types.Operator):
    bl_idname = "uv.line_up"
    bl_label = "Line Up UV Chains"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        # eq_uv_chains(bm)
        arrange_uv_chains(bm, equalize=False)
        bmesh.update_edit_mesh(context.active_object.data)
        return {'FINISHED'}

### UI

class ZaloopokView3DPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = "VIEW3D_PT_Zaloopok"
    bl_label = "Zaloopok"

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def draw(self, context):
        col = self.layout.column()
        subcol1 = col.column(align = True)
        subcol1.label("Select More:")
        subcol1.operator("mesh.z_grow_loop", text="Grow Loop")
        subcol1.operator("mesh.z_grow_ring", text="Grow Ring")
        subcol2 = col.column(align = True)
        subcol2.separator()
        subcol2.label("Select Less:")
        subcol2.operator("mesh.z_shrink_loop", text="Shrink Loop")
        subcol2.operator("mesh.z_shrink_ring", text="Shrink Ring")
        subcol3 = col.column(align = True)
        subcol3.separator()
        subcol3.label("Select Bounded:")
        subcol3.operator("mesh.z_select_bounded_loop", text="Select Loop")
        subcol3.operator("mesh.z_select_bounded_ring", text="Select Ring")
        comp_sel = context.tool_settings.mesh_select_mode[:]
        if len(list(filter(lambda x: x, comp_sel))) == 1:
                subcol4 = col.column(align = True)
                subcol4.separator()
                subcol4.label("Convert Selection to:")
                if not comp_sel[0]:
                    subcol4.operator("mesh.z_to_verts", text="Vertices")
                if not comp_sel[1]:
                    subcol4.operator("mesh.z_to_edges", text="Edges")
                if not comp_sel[2]:
                    subcol4.operator("mesh.z_to_faces", text="Faces")
        subcol5 = col.column(align = True)
        subcol5.separator()
        subcol5.label("Modify:")
        subcol5.operator("mesh.z_delete_mode")
        subcol5.operator("mesh.eq_edges")
        subcol5.operator("mesh.line_up_edges")
        subcol5.operator("mesh.z_connect")
        subcol5.operator("mesh.z_put_on")
        subcol5.operator("mesh.z_mirror")

class ZaloopokUVPanel(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_idname = "IMGEDIT_PT_Zaloopok"
    bl_label = "Zaloopok"

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def draw(self, context):
        col = self.layout.column()
        subcol1 = col.column(align = True)
        subcol1.label("Transform fragments:")
        subcol1.operator("uv.z_rotate_fragments", text="Rotate")
        subcol1.operator("uv.z_scale_fragments", text="Scale")
        subcol1.separator()
        subcol2 = col.column(align = True)
        subcol2.operator("uv.equalize", text="Equalize")
        subcol2.operator("uv.line_up", text="Line Up")

def register():
    bpy.utils.register_class(ZaloopokView3DPanel)
    bpy.utils.register_class(ZaloopokUVPanel)
    bpy.utils.register_class(GrowLoop)
    bpy.utils.register_class(ShrinkLoop)
    bpy.utils.register_class(GrowRing)
    bpy.utils.register_class(ShrinkRing)
    bpy.utils.register_class(SelectBoundedLoop)
    bpy.utils.register_class(SelectBoundedRing)
    bpy.utils.register_class(ToFaces)
    bpy.utils.register_class(ToEdges)
    bpy.utils.register_class(ToVerts)
    bpy.utils.register_class(EdgeEq)
    bpy.utils.register_class(EdgeLineUp)
    bpy.utils.register_class(ContextDelete)
    bpy.utils.register_class(PutOn)
    bpy.utils.register_class(Mirror)
    bpy.utils.register_class(EdgeConnect)
    bpy.utils.register_class(RotateUVFragments)
    bpy.utils.register_class(ScaleUVFragments)
    bpy.utils.register_class(EqualizeUVChains)
    bpy.utils.register_class(LineUpUVChains)

def unregister():
    bpy.utils.unregister_class(ZaloopokView3DPanel)
    bpy.utils.unregister_class(ZaloopokUVPanel)
    bpy.utils.unregister_class(GrowLoop)
    bpy.utils.unregister_class(ShrinkLoop)
    bpy.utils.unregister_class(GrowRing)
    bpy.utils.unregister_class(ShrinkRing)
    bpy.utils.unregister_class(SelectBoundedLoop)
    bpy.utils.unregister_class(SelectBoundedRing)
    bpy.utils.unregister_class(ToFaces)
    bpy.utils.unregister_class(ToEdges)
    bpy.utils.unregister_class(ToVerts)
    bpy.utils.unregister_class(EdgeEq)
    bpy.utils.unregister_class(EdgeLineUp)
    bpy.utils.unregister_class(ContextDelete)
    bpy.utils.unregister_class(PutOn)
    bpy.utils.unregister_class(Mirror)
    bpy.utils.unregister_class(EdgeConnect)
    bpy.utils.unregister_class(RotateUVFragments)
    bpy.utils.unregister_class(ScaleUVFragments)
    bpy.utils.unregister_class(EqualizeUVChains)
    bpy.utils.unregister_class(LineUpUVChains)

if __name__ == "__main__":
    register()

