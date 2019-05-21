def remesh(meshes):
    def vsi(vns, va, na, vn):
        i = vns.get(vn, None)
        if not i:
            vns[vn] = i = len(va)
            va.append(vn[0])
            na.append(vn[1])
        return i

    def mgs(m, rm, vn0, vn1, vn2):
        def cmb(m, vn, r):
            e = m.get(vn, None)
            if e is None:
                m[vn] = r
            elif e[4] != r[4]:
                vv, ff, nn, _, _ = e
                for (f0, f1, f2) in ff:
                    v0, v1, v2 = vv[f0], vv[f1], vv[f2]
                    n0, n1, n2 = nn[f0], nn[f1], nn[f2]
                    vn0, vn1, vn2 = (v0, n0), (v1, n1), (v2, n2)
                    vc, fc, nc, vns, _ = r
                    fc.append((vsi(vns, vc, nc, vn0), vsi(vns, vc, nc, vn1), vsi(vns, vc, nc, vn2)))
                for k in m.keys():
                    if m[k][4] == e[4]:
                        m[k] = r
                del rm[e[4]]

        r = m.get(vn0)
        if r:
            cmb(m, vn1, r)
            cmb(m, vn2, r)
            return r
        r = m.get(vn1)
        if r:
            cmb(m, vn0, r)
            cmb(m, vn2, r)
            return r
        r = m.get(vn2)
        if r:
            cmb(m, vn0, r)
            cmb(m, vn1, r)
            return r
        i = len(m)
        m[vn0] = m[vn1] = m[vn2] = r = ([], [], [], {}, i)
        rm[i] = (r[0], r[1], r[2])
        return r

    m, rm = {}, {}
    for vv, ff, nn in meshes:
        for (f0, f1, f2) in ff:
            v0, v1, v2 = vv[f0], vv[f1], vv[f2]
            n0, n1, n2 = nn[f0], nn[f1], nn[f2]
            vn0, vn1, vn2 = (v0, n0), (v1, n1), (v2, n2)
            vc, fc, nc, vns, _ = mgs(m, rm, vn0, vn1, vn2)
            fc.append((vsi(vns, vc, nc, vn0), vsi(vns, vc, nc, vn1), vsi(vns, vc, nc, vn2)))
    return rm.values()
