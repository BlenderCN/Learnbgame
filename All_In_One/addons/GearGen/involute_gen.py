from math import *
import bpy, bmesh
from mathutils import *
#from random import random, seed
from mathutils.geometry import *

from .myrandom import seed, random

"""
print("RAND TEST")
for i in range(32):
    print("%.3f" % (random()*2.0 - 1.0))
#"""

#####################################################
# based on http://lcamtuf.coredump.cx/gcnc/ch6/#6.2 #
#####################################################

weld_threshold = 0.0001

def cutedge(e, totcuts):
    vs = [e.verts[0], e.verts[1]]
    
    v = e.verts[0]
    ds = 1.0 / totcuts
    s = 0
    
    for i in range(totcuts):
        fac = 1 / (totcuts-i+1)
        e, v = bmesh.utils.edge_split(e, v, 1.0-fac);
        vs.append(v)
    
    return vs
    

class Profile:
    def __init__(self, twid, pressureth, numteeth, backlash, depthscale=1.0, inner_gear_mode=False):
        th = pi*pressureth/180 #20 degrees
        
        twid_scale = 1 / (numteeth)
        twid_scale = 1.0 - twid_scale*twid_scale
        
        #twid *= twid_scale
        
        self.inner_gear_mode = inner_gear_mode
        self.backlash = backlash
        self.twid = twid #teeth width
        self.numteeth = numteeth
        self.pressureth = pressureth

        self.tdepth = (twid * 2 / pi) * 1.0 * depthscale
        self.radius = ((twid * 2) * numteeth) / pi / 2
        
        #used by trap() function
        self._dx = sin(th)*self.tdepth
        self._dy = cos(th)*self.tdepth
        
        self.centv = None
        self.edges = None
        self.verts = None
        self.minvx = None
        self.maxvy = None
        
        self.geom = None
    
def vrnd():
    rx = random()*2.0 - 1.0
    ry = random()*2.0 - 1.0
    rz = 0#random()*2.0 - 1.0
    
    return Vector([rx, ry, rz])

def trap(profile, bm, s):
    dx = profile._dx
    dy = profile._dy
    bl = profile.backlash
    
    offy = 0#abs(dy)*0.125
    
    twid2 = profile.twid/2# + bl
    v1 = bm.verts.new([-twid2+dx, -dy+offy, 0])
    v2 = bm.verts.new([twid2-dx, -dy+offy, 0])

    v3 = bm.verts.new([-twid2-dx*2, dy*2+offy, 0])
    v4 = bm.verts.new([twid2+dx*2, dy*2+offy, 0])
    
    """
    rfac = 0.0000001
    v1.co += vrnd()*rfac
    v2.co += vrnd()*rfac
    v3.co += vrnd()*rfac
    v4.co += vrnd()*rfac
    
    #"""
    
    return bm.faces.new([v1, v2, v4, v3])

def rot(f, th):
    for v in f.verts:
        x = v.co[0]*cos(th) + v.co[1]*sin(th)
        y = v.co[1]*cos(th) - v.co[0]*sin(th)
        v.co[0] = x
        v.co[1] = y

def trans(f, x, y):
    for v in f.verts:
        v.co[0] += x
        v.co[1] += y

class funcsort_i:
    def __init__(self, func, item):
        self.item = item
        self.func = func
        
    def __eq__(self, b):
        return self.func(self.item, b.item) == 0
    def __lt__(self, b):
        return self.func(self.item, b.item) < 0
    def __gt__(self, b):
        return self.func(self.item, b.item) > 0

def funcsort(lst, func):
    lst2 = []
    
    for item in lst:
        lst2.append(funcsort_i(func, item))
        
    lst2.sort()
    
    for i, item in enumerate(lst2):
        lst[i] = item.item

def myintersect_line_line_2d(a1, a2, b1, b2):
    a1 = Vector(a1)
    a2 = Vector(a2)
    b1 = Vector(b1)
    b2 = Vector(b2)
    
    """
    fac = 1.0000001
    
    c1 = (a1+a2)*0.5
    c2 = (b1+b2)*0.5
    
    rfac = 0.0000000
    a1 = (a1 - c1)*fac + c1 #+ vrnd()*rfac
    a2 = (a2 - c1)*fac + c1 #+ vrnd()*rfac
    b1 = (b1 - c2)*fac + c2 #+ vrnd()*rfac
    b2 = (b2 - c2)*fac + c2 #+ vrnd()*rfac
    #"""
    
    return intersect_line_line_2d(a1, a2, b1, b2)

def isectline(netbm, a, b):
    def veq(a, b):
        return (a-b).length <= 0.0001
           
    isects = []
    for e in netbm.edges:
        shared = veq(a, e.verts[0].co) or veq(a, e.verts[1].co)
        shared = shared or veq(b, e.verts[0].co) or veq(b, e.verts[1].co)
        
        if shared:
            continue
            
        isect = myintersect_line_line_2d(a, b, e.verts[0].co, e.verts[1].co)
        if isect != None:
            isects.append([e, isect])
    
    def xydis(x1, y1, x2, y2):
        dx = x1-y1
        dy = x2-y2
        return dx*dx + dy*dy
    
    def cmp(i1, i2):
        d1 = xydis(i1[1][0], i1[1][1], a[0], a[1])
        d2 = xydis(i2[1][0], i2[1][1], a[0], a[1])
        
        return d1 - d2
    
    funcsort(isects, cmp)
    
    return isects

def addline(netbm, a, b):
    isects = isectline(netbm, a.co, b.co)
    if len(isects) == 0:
        netbm.edges.new([a, b])
        return
    
    firstv = a
    lastnewv = a
    
    limit = 0.000001
    for e, isect in isects:
        isect = Vector([isect[0], isect[1], 0])
        if (isect - a.co).length < limit or (isect - b.co).length < limit:
            continue
        
        newe, newv = bmesh.utils.edge_split(e, e.verts[0], 0.5)
        newv.co[0] = isect[0]
        newv.co[1] = isect[1] 
        
        if lastnewv is not None:
            netbm.edges.new([lastnewv, newv])
        lastnewv = newv
    
    newv = b
    netbm.edges.new([lastnewv, newv])
    
    return firstv, newv
def edge(bm, a, b):
    return bm.edges.new([bm.verts.new(a), bm.verts.new(b)])

def coincident(v1, v2, p, fac=0.0000012):
    p = Vector(p)
    v1 = Vector(v1)
    v2 = Vector(v2)
    
    p -= v1
    vec = v2 - v1
    
    vec.normalize()
    p.normalize()
    
    d = vec.dot(p)
    
    #return abs(d) <= fac or abs(d) >= 1.0 - fac
    return abs(d) >= 1.0-fac
 
def inside(es, p, radius):
    vec = Vector([0.6523, 0.5, 0.0])#+vrnd()*0.01
    vec.normalize()
    
    v1 = Vector(p) #- vec*0.0000123
    v2 = p + vec*100.0*radius
    
    #edge(visbm, v1, v2)        
    tot = 0
    for e in es:
        limit = 0.00001
        """
        if (e.verts[0].co - v1).length <= limit or \
            (e.verts[1].co - v1).length <= limit:
            continue
        #"""
        
        if coincident(e.verts[0].co, e.verts[1].co, v1):
            return False
        
        """
        if coincident(v1, v2, e.verts[0].co, 0.0001):
            tot += 1
            #asd()
            pass
        if coincident(v1, v2, e.verts[1].co, 0.0001):
            tot += 1
            #aet()
            pass
        #"""
        
        isect = myintersect_line_line_2d(e.verts[0].co, e.verts[1].co, v1, v2)
        
        if isect != None:
            tot += 1
    
    #print("tot", tot)
    return tot & 1 == 1

def addtrap(profile, netbm, trap):
    delvs = set()
    vs = []
    netbm.verts.index_update()
    radius = profile.radius
    
    for v in trap.verts:
        v2 = netbm.verts.new(v.co)
        v2.index = -2
        vs.append(v2)
    
    for v in vs:
        if inside(netbm.edges, v.co, radius):
            delvs.add(v)
            pass
    
    for i in range(len(trap.edges)):
        v1 = vs[i]
        v2 = vs[(i+1) % len(trap.edges)]
        addline(netbm, v1, v2)
        
    for v in netbm.verts:
        if v.index == -2: continue
        
        if inside(trap.edges, v.co, radius):
            delvs.add(v)
            pass
        
    for v in delvs:
        netbm.verts.remove(v)
        pass
    
    for e in netbm.edges:
        v1 = e.verts[0]
        v2 = e.verts[1]
        l1 = len(list(v1.link_edges))
        l2 = len(list(v2.link_edges))
        
        if (l1 > 2) and (l2 > 2):
            netbm.edges.remove(e)
            pass    
    
#print("\n")

def cut_tooth(profile, bm, netbm):
    steps = 26
    bl = profile.backlash

    radius = profile.radius
    
    for i in range(-steps, 0):            
        f = trap(profile, bm, i/steps)
        
        offx = radius*i/steps
        trans(f, 0, radius)
        trans(f, offx, 0)
        rot(f, -offx/radius)
        
        #XXX delete this if block!
        if i != -1:
            #trans(f, -0.35, -1)
            pass
        addtrap(profile, netbm, f)

def smooth(bm, fac=1.0):
    cos = [Vector(v.co) for v in bm.verts]
    bm.verts.index_update()
    
    for i, v in enumerate(bm.verts):
        sum = Vector(v.co)
        tot = 1
        
        for e in v.link_edges:
            v2 = e.other_vert(v)
            sum += cos[v2.index]
            tot += 1
        
        sum /= tot
        v.co += (sum - v.co)*fac

def make_profile(profile, bm, netbm):
    cut_tooth(profile, bm, netbm)
    bmesh.ops.remove_doubles(netbm, verts=netbm.verts, dist=0.05)
    smooth(netbm, 0.1)

    minvx = None
    maxvy = None
    radius = profile.radius
    tdepth = profile.tdepth
    
    thres = 0.001
    cutoff_limit = radius + tdepth + thres #- profile.backlash*4
    
    def docutoff(v):
        return v.co[0]*v.co[0] + v.co[1]*v.co[1] > cutoff_limit*cutoff_limit
    
    def safesqrt(f):
        return sqrt(-f) if f < 0 else sqrt(f)
    
    def cut_at_radius(e, radius):
        """
        on factor
        off period;
        
        dx := x1 + (x2-x1)*t;
        dy := y1 + (y2-y1)*t;
        
        f1 := dx**2 + dy**2 - cutoff_limit**2;
        f := part(solve(f1, t), 1, 2);
        """
        cutoff_limit = radius;
        x1 = e.verts[0].co[0];
        y1 = e.verts[0].co[1];
        x2 = e.verts[1].co[0];
        y2 = e.verts[1].co[1];
        
        t = (sqrt(cutoff_limit**2*x1**2-2*cutoff_limit**2*x1*x2+
          cutoff_limit**2*x2**2+cutoff_limit**2*y1**2-2*cutoff_limit**2*
          y1*y2+cutoff_limit**2*y2**2-x1**2*y2**2+2*x1*x2*y1*y2-x2**2*y1**2)
          +x1**2-x1*x2+y1**2-y1*y2)/(x1**2-2*x1*x2+x2**2+y1**2-2*y1*
          y2+y2**2);

        
        t = abs(t);
        
        ne, nv = bmesh.utils.edge_split(e, e.verts[0], t);
        
    #cut edge spanning chop-off line
    for e in list(netbm.edges):
        if docutoff(e.verts[0]) == docutoff(e.verts[1]):
            continue
        
        """
        on factor
        off period;
        
        dx := x1 + (x2-x1)*t;
        dy := y1 + (y2-y1)*t;
        
        f1 := dx**2 + dy**2 - cutoff_limit**2;
        f := part(solve(f1, t), 1, 2);
        
        """
        
        cut_at_radius(e, cutoff_limit - 0.001);
        
        #cutedge(e, 3)
        continue
    
    for v in netbm.verts[:]:
        if v.co[0] < profile.twid*0.25:
            netbm.verts.remove(v)
            continue
            
    bmesh.ops.remove_doubles(netbm, verts=netbm.verts, dist=0.01)
    
    #chop off outer verts
    for v in netbm.verts:
        if v.co[0] < 0 or docutoff(v):
            netbm.verts.remove(v)
            continue
            pass
        
        if minvx is None or v.co[0] < minvx.co[0]: # or (v.co[0] == minvx.co[0] and v.co[1] < minvx.co[1]):
            minvx = v
        if maxvy is None or v.co[1] > maxvy.co[1]: # or (v.co[1] == maxvy.co[1] and v.co[0] > maxvy.co[0]):
            maxvy = v
                
    #cv = netbm.verts.new([0, radius-tdepth, 0])
    #netbm.edges.new([cv, minvx])
    
    #profile.centv = cv
    profile.edges = list(netbm.edges)
    profile.verts = list(netbm.verts)
    profile.minvx = minvx
    profile.maxvy = maxvy
    
    profile.geom = profile.verts + profile.edges

    return profile

def finalgen(netbm, profile):
    steps = profile.numteeth-1
    dth = 2*pi/steps
    th = dth
    
    def rot(v, costh, sinth):
        x = v.co[0]*costh + v.co[1]*sinth
        y = v.co[1]*costh - v.co[0]*sinth
        
        v.co[0] = x
        v.co[1] = y
    
    def rotvs(vs, th):
        costh = cos(th)
        sinth = sin(th)
        
        for v in vs:
            if not isinstance(v, bmesh.types.BMVert):
                continue
            rot(v, costh, sinth)
    
    rotvs(profile.verts, -0.5*pi*2/profile.numteeth)
    
    lastbase1 = None#profile.minvx
    lastbase2 = None#profile.minvx
    firstbase1 = None
    firstbase2 = None
    
    #for making undercut
    def roundbase(e):
        vs = []
        steps = 16
        
        ds = 1.0 / steps
        s = 0
        
        v = e.verts[0]
        #print("\n")
        #vs = [e.verts[0], e.verts[1]]
        
        vs = cutedge(e, steps)
        
        s = 0
        ds = 1.0 / len(vs)
        for v in vs:
            vec = Vector(v.co)
            vec.normalize()
            
            s2 = 1.0 - s
            fac = 1.0 - s2*s2
            v.co -= vec*profile.tdepth*fac*0.2
            s += ds
                
    bases = []
    base2 = None
    
    for i in range(steps):
        netbm.verts.index_update()
        #print("yay")

        geom = bmesh.ops.duplicate(netbm, geom=profile.geom)
        
        if profile.minvx not in geom["vert_map"]:
            print("Error, no minvx mapping!")
            continue
        if profile.maxvy not in geom["vert_map"]:
            print("Error, no maxvy mapping!")
            continue
            
        tip1 = geom["vert_map"][profile.maxvy]
        base1 = geom["vert_map"][profile.minvx]
        
        netbm.verts.index_update()
        geom = geom["geom"]
        
        geom2 = bmesh.ops.duplicate(netbm, geom=profile.geom)
        tip2 = geom2["vert_map"][profile.maxvy]
        base2 = geom2["vert_map"][profile.minvx]
        
        geom2 = geom2["geom"]
        
        netbm.edges.new([tip1, tip2])
        
        if firstbase1 is None:
            firstbase1 = base1
            firstbase2 = base2
                    
        if lastbase1 is not None:
            e = netbm.edges.new([lastbase2, base1])
            bases.append(e)
            
        lastbase1 = base1
        lastbase2 = base2        
        rotvs(geom, th)
        for v in geom2:
            if not isinstance(v, bmesh.types.BMVert):
                continue
            v.co[0] = -v.co[0]
                        
        rotvs(geom2, th)
        
        th += dth
    
    if base2 != None:
        bases.append(netbm.edges.new([firstbase1, base2]))
    
    #undercut base a bit
    #"""
    for e in bases:
        roundbase(e)
    #"""
    
    def smooth_profile():
        #smooth mesh
       
        #subdivide edges
        tesswid = 0.025
      
        #merge any really small geometry
        bmesh.ops.remove_doubles(netbm, verts=netbm.verts, dist=tesswid*0.95)
        
        for e in list(netbm.edges):
            l = (e.verts[1].co - e.verts[0].co).length
            if l < tesswid*2: continue
            
            cutedge(e, int(l / tesswid))
        bmesh.ops.remove_doubles(netbm, verts=netbm.verts, dist=tesswid*4)
        
        for i in range(20):
            bmesh.ops.smooth_vert(netbm, verts=netbm.verts);
    
    #smooth_profile()
    
    #backup vertex locations
    vcos = [Vector(v.co) for v in netbm.verts]
    
    #add some randomness
    #"""
    for v in netbm.verts:
        v.co += vrnd()*0.005;
    #"""
    
    bmesh.ops.remove_doubles(netbm, verts=netbm.verts, dist=0.01)
    bmesh.ops.triangle_fill(netbm, edges=netbm.edges, use_beauty=True)
    
    #for i, v in enumerate(netbm.verts):
    #    v.co = vcos[i]
        
    ok = True
    try:
        ret = bmesh.ops.dissolve_faces(netbm, faces=netbm.faces)
        ok = len(list(ret["region"])) == 1
    except:
        ok = False
        
    if not ok:
        print("Error generating involute shape!")
        return netbm
        
    face = ret["region"][0]
        
    netbm.normal_update()
    if face.normal[2] < 0:
        bmesh.ops.reverse_faces(netbm, faces=netbm.faces)
        netbm.normal_update()
    
    #offset profile for anti-backlash
    vs = list(face.verts)
    vcos = [Vector(v.co) for v in netbm.verts]
    
    netbm.verts.index_update()
    
    for e in netbm.edges:
        if len(list(e.link_faces)) == 0:
            netbm.edges.remove(e)
    for v in netbm.verts:
        if len(list(v.link_edges)) == 0:
            netbm.verts.remove(v)
            
    for i in range(len(vs)):
        v1 = vs[i]
        v2 = vs[(i+1)%len(vs)]
        v3 = vs[(i+2)%len(vs)]
        
        vec1 = vcos[v2.index] - vcos[v1.index]
        vec2 = vcos[v3.index] - vcos[v2.index]
        
        vec1.normalize()
        vec2.normalize()
        
        vec = vec1+vec2
        vec.normalize()
        
        t = vec[0]; vec[0] = vec[1]; vec[1] = -t
        
        #XXX 
        v2.co -= vec*profile.backlash
    
    
    #netbm.faces.remove(face)
    
    if profile.inner_gear_mode: #radially mirror the teeth
        maxdot = 0
        for v in netbm.verts:
            maxdot = max(maxdot, v.co.dot(v.co))
        
        if maxdot != 0:
            maxr = sqrt(maxdot)
            for v in netbm.verts:
                r = v.co.length
                v.co.normalize()
                r = profile.radius + (maxr - r)
                
                v.co *= r
                
    return netbm

def genGear(profile):
    seed(0)
    
    netbm = bmesh.new()
    bm = bmesh.new()
    
    make_profile(profile, bm, netbm)
    finalgen(netbm, profile)
    
    return netbm

def test():
    profile = Profile(2.0, 17.5, 8, 0.0)
    netbm = genGear(profile)

    ob2 = bpy.data.objects["netmesh"]
    netbm.to_mesh(ob2.data)    
    ob2.data.update()

    bm.to_mesh(ob.data)
    ob.data.update()

    #visob = bpy.data.objects["vis"]
    #visbm.to_mesh(visob.data)
    #visob.data.update()
