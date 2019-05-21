import bpy, bmesh
from mathutils import *
from math import *
import time, struct, ctypes, imp
from . import involute_gen, involute_gen_node
from . import myrandom
from . import myprops

from .myprops import getprop

def fract(f):
    return f - floor(f)

def tent(f):
  return 1.0 - abs(f - 0.5)*2.0

#utility function to try and avoid buggy triangle fill (blender's
#scanfill isn't always super-robust)
def safe_triangle_fill(bm, edges, profile):
    vset = set()
    
    for e in edges:
        vset.add(e.verts[0])
        vset.add(e.verts[1])
        
    vset = list(vset) #we need a defined order
    cos = [Vector(v.co) for v in vset]
    
    items = []
    steps = 5
    mintotf = None
    mini = None
    
    bm.edges.index_update()
    copyedges = set()
    for e in edges:
        copyedges.add(e.index)
        
    for i in range(steps):
        cos2 = [Vector(v.co) for v in vset]
        for j in range(len(cos2)):
            for k in range(2):
                cos2[j][k] += (myrandom.random()-0.5)*profile.twid*0.001
        
        copybm = bm.copy()
        copybm.edges.index_update()

        edges2 = []
        vset2 = set()
        for e in copybm.edges:
            vset2.add(e.verts[0])
            vset2.add(e.verts[1])
            
            if e.index in copyedges:
                edges2.append(e)
                
        vset2 = list(vset2)
        
        for j in range(5):
            bmesh.ops.smooth_vert(copybm, verts=vset2, factor=1.0)
        
        totf = len(copybm.faces)
        ret = bmesh.ops.triangle_fill(copybm, edges=list(edges2), use_beauty=True)
        totf = len(copybm.faces) - totf;
        
        for j, v in enumerate(vset):
            v.co = cos[j]
        
        items.append([cos2, totf])
        
        if mini is None or (totf > 0 and totf < mintotf):
            mini = i
            mintotf = totf
    
    for i, v in enumerate(vset):
        v.co = items[mini][0][i]

    ret = bmesh.ops.triangle_fill(bm, edges=list(edges), use_beauty=True)
    
    #"""
    for i, v in enumerate(vset):
        v.co = cos[i]
    #"""
    
    return ret
    
#SUCH AN EVIL IDEA
#SHAFT_MARGIN = 0.2
#make interior circle cutouts
def genCircleCutouts(bm, radius, numteeth, gear, mygear, shaftdiam, ob, scene):
    circles = []
        
    def circle(p, r):
        circles.append([p, r, False, 0.0])
        
    def keyedcircle(p, r, keydepth):
        circles.append([p, r, True, keydepth])
        
    def circle_isect(p, r, margin=0.0005):
        for c in circles:
            dis = (p-c[0]).length
            if dis < r+c[1]+margin:
                return True
        return False
    
    r3 = radius*0.2
    r2 = radius - 0.5*getprop(ob, scene, "depth") - r3*1.75

    def find_number_of_circles():
        def test(steps):
            circles[:] = []
            t = -pi

            dt = (2*pi)/steps
            
            circle(Vector(), shaftdiam*0.5)
            err = 0
            
            for i in range(steps):
                p = Vector()
                p[0] = sin(t)*r2
                p[1] = cos(t)*r2
                p[2] = 0
                
                circle(p, r3)
                
                if circle_isect(p, r3):
                    err += 1
                    
                t += dt
            
            circles[:] = []
            return err
        
        margin = r3*0.45
        minsteps = (r2*pi) / (r3 + margin)
        minsteps = max(int(minsteps), 1)
        return minsteps
        
        minerr = 1e17
        #minsteps = int(numteeth/2)
        #minsteps = max(minsteps, 3)
        
        for i in range(max(minsteps, 0), minsteps+3):
            err = test(i)
            
            if err <= minerr:
                minerr = err
                minsteps = i
        
        circles[:] = []
        return minsteps
    
    if getprop(ob, scene, "genshaft"):
        if getprop(ob, scene, "key_shaft"):
            keyedcircle(Vector(), shaftdiam*0.5, getprop(ob, scene, "key_depth"));
        else:
            circle(Vector(), shaftdiam*0.5)
    
    if not getprop(ob, scene, "no_cutouts"):
        steps = find_number_of_circles()
        t = -pi
        dt = (2*pi)/steps
        
        for i in range(steps):
            p = Vector()
            p[0] = sin(t)*r2
            p[1] = cos(t)*r2
            p[2] = 0
            
            if not circle_isect(p, r3):
                circle(p, r3)
            t += dt
            
    csteps = 64
    for p, r, dokey, keydepth in circles:
        t = -pi
        df = (2*pi) / csteps
        vs = []
        for i in range(csteps):
            x = sin(t)*r + p[0]
            y = cos(t)*r + p[1]
            z = p[2]
            
            if dokey and r-y < keydepth*r:
                y = r - keydepth*r;
            
            vs.append(bm.verts.new(Vector([x, y, z])))
            t += df
        
        for i in range(len(vs)):
            bm.edges.new([vs[i], vs[(i+1)%len(vs)]])

def genShaftSpacer(ob, bm, gear, radius, side, thickness, scene):
  print("generating shaft spacer")
  
  sw = getprop(ob, scene, "spacer_width");
  st = getprop(ob, scene, "spacer_thick");
  
  r1 = getprop(ob, scene, "shaft_diameter")*sw - getprop(ob, scene, "spacer_thick")*0.5#min(ob.geargen.shaft_diameter*sw, (radius - st*2.0))
  r2 = r1 + st
  
  steps = 64
  
  th = -pi
  dth = (2*pi) / steps
  
  lastv1 = None
  lastv2 = None
  firstv1 = None
  firstv2 = None
  
  faces = []
  
  zoff = side * 0.5*thickness
  
  for i in range(steps):
    x1 = sin(th) * r1
    y1 = cos(th) * r1
    
    x2 = sin(th) * r2
    y2 = cos(th) * r2
    
    v1 = bm.verts.new([x1, y1, zoff+side*0.0002])
    v2 = bm.verts.new([x2, y2, zoff+side*0.0002])
    
    if i > 0:
      vs = [lastv1, v1, v2, lastv2]
      if side < 0:
        vs.reverse()
        
      faces.append(bm.faces.new(vs))
    else:
      firstv1 = v1
      firstv2 = v2
      
    lastv1 = v1
    lastv2 = v2
    
    th += dth
  
  bm.verts.index_update()
  
  vs = [lastv1, firstv1, firstv2, lastv2]
  if side < 0:
    vs.reverse()
  
  faces.append(bm.faces.new(vs))
  geom = faces[:]
  vset = set()
  
  for f in faces:
    for v in f.verts:
      if v.index not in vset:
        vset.add(v.index)
        geom.append(v)
        
  geom = bmesh.ops.extrude_face_region(bm, geom=geom)['geom']
  extrude = side * ob.geargen.spacer_height
  
  for v in geom:
      if not isinstance(v, bmesh.types.BMVert):
          continue
          
      v.co[2] += extrude
  
def genGear(ob, scene):
    shaftdiam = getprop(ob, scene, "shaft_diameter") / getprop(ob, scene, "xy_scale")
    
    myprops.handleVersioning(scene, ob)
    
    print("generating gear");
    
    gear = scene.geargen #global settings
    #local settings live in ob.geargen
    
    gearwid = getprop(ob, scene, "modulus")*2
    teethsize = gearwid
    
    numteeth = int(ob.geargen.numteeth)
    perim = numteeth * teethsize
    radius = 0.5 * perim/pi
        
    print("radius:", radius)
    print("number of gear teeth:", numteeth)
    
    profile = involute_gen.Profile(teethsize*0.5, getprop(ob, scene, "pressure_angle"), numteeth, getprop(ob, scene, "backlash"), 
                                   getprop(ob, scene, "depth"), inner_gear_mode=ob.geargen.inner_gear_mode)
    bm = involute_gen_node.genGear(profile)
    radius = profile.radius
    
    #involute_gen made a face for us; delete it
    f = None
    for f in bm.faces:
        break
    
    if f is not None:
        bm.faces.remove(f)
    else:
        pass #print("Error generating gear!")
    
    if ob.geargen.inner_gear_mode:
        outer_radius = radius + getprop(ob, scene, "depth") + ob.geargen.inner_gear_depth
        steps = max(int(2*outer_radius*pi / 0.5), 12);
        inner_race_set = set()
        
        dt = 2*pi / steps
        t = -pi
        vs = []
        for i in range(steps):
            x = sin(t)*outer_radius
            y = cos(t)*outer_radius
            vs.append(bm.verts.new([x, y, 0]))
            t += dt
            
        for i in range(len(vs)):
            v1 = vs[i]
            v2 = vs[(i+1)%len(vs)]
            
            bm.edges.new([v1, v2])
            inner_race_set.add(v1)
            
    else: #make circle relief cuts
        genCircleCutouts(bm, radius, numteeth, gear, ob.geargen, shaftdiam, ob, scene)
        inner_race_set = None
    
    ob.geargen.pitch_out = radius*ob.geargen.xy_scale
        
    #get rid of any stupidly dense geometry
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.06)
    
    #final gear thickness
    thickness = getprop(ob, scene, "thickness")
 
    zmin = -thickness*0.5
    zmax = thickness*0.5
    
    layer  = []
    layers = [layer]
    elayers = [list(bm.edges)]
    
    shaftverts = set();
    edgemap = {}
    
    for v in bm.verts:
        v.co[2] = zmin
        layer.append(v)
            
    bm.verts.index_update()
    bm.edges.index_update()
    
    if getprop(ob, scene, "double_helical") or getprop(ob, scene, "helical_on") or getprop(ob, scene, "taper_on"):
        steps = getprop(ob, scene, "subdivisions")*2
    else:
        steps = 1
        
    shape = getprop(ob, scene, "herring_shape")
    dochannel = getprop(ob, scene, "double_helical") and getprop(ob, scene, "herringchannel_on")
    chanwid = getprop(ob, scene, "herringchannel_width")
    chanblend = getprop(ob, scene, "herringchannel_blend")
    
    dz = (zmax - zmin) / steps
    z = zmin + dz
    
    #create subdivisions
    
    geom = bm.faces
    for i in range(steps):
        layer = []
        elayer = []
        layers.append(layer)
        elayers.append(elayer)
        vmap = {}
        
        for v in layers[0]:
            v2 = bm.verts.new(v.co)
            v2.co[2] = z
            layer.append(v2)
            v2.index = v.index
            
            vmap[v.index] = v2
                
        for e in elayers[0]:
            try:
                newe = bm.edges.new([vmap[e.verts[0].index], vmap[e.verts[1].index]])
                edgemap[newe] = e
                elayer.append(newe)
            except ValueError: #edge exists
                pass
                
        
        #flatted middle where channel is?
        
        absz = abs(z)
        if dochannel and absz <= (chanwid+chanblend)*0.5:
            #calc channel blend factor
            if absz > chanwid*0.5:                
                sz = 1.0 - 2.0*(absz - chanwid*0.5) / chanblend;
            else:
                sz = 1
            
            sz *= getprop(ob, scene, "herringchannel_depth");

            signsz = 1 if ob.geargen.inner_gear_mode else -1
            szradius = radius + signsz*getprop(ob, scene, "depth") + getprop(ob, scene, "backlash")*4*signsz
            
            #if ob.geargen.inner_gear_mode:
            #    szradius += getprop(ob, scene, "depth")*0.5
                
            #walk around teeth boundary
            startv = layer[0]
            v = startv
            e = list(v.link_edges)[0]
            _i = 0
            while _i < 10000000: #infinite loop safeguard
                co2 = Vector(v.co)
                co2.normalize()
                co2 *= szradius
                
                v.co += (co2 - v.co)*sz
                
                for e2 in v.link_edges:
                    if e2 != e:
                        e = e2
                        break
                
                v = e.other_vert(v)
                
                if v == startv: break
                _i += 1
            
            if _i == 10000000:
                print("error: infinite loop in gear gen code")
                
        z += dz
    
    #remove shaft vertices if we have them
    if getprop(ob, scene, "genshaft"):
        for layer in layers:
            rem = []
            for v in layer:
                if sqrt(v.co[0]*v.co[0] + v.co[1]*v.co[1]) <= shaftdiam*0.5001:
                    shaftverts.add(v)
    
    if ob.geargen.inner_gear_mode:
        bm.verts.index_update()
        
        for v in bm.verts:
            if abs(sqrt(v.co[0]*v.co[0] + v.co[1]*v.co[1]) - outer_radius) < 0.01:
                inner_race_set.add(v)
                
    dth = 2*pi / numteeth
    if getprop(ob, scene, "double_helical") or getprop(ob, scene, "helical_on"):
        th3 = (2.0 / gearwid) * dth*getprop(ob, scene, "helical_angle")*0.25*thickness / 4
    else:
        th3 = 0
        
    ds = 1.0 / steps
    s = 0
    
    if ob.geargen.invert_helical:
        th3 = -th3
    
    def herringshape(s):
        s2 = 1.0 - abs(s-0.5)*2.0
        
        if shape == "SMOOTHSTEP":
            s2 = s2*s2*(3.0 - 2.0*s2)
        elif shape == "WIDE":
            s2 = 1.0 - pow(1.0 - s2, 2.0)
        elif shape == "PINCHED":
            s2 *= s2
            
        return s2
    
    def identshape(s):
        return 1.0 - s
    
    def helicalshape(s):
        return 1.0 - s
    
    if getprop(ob, scene, "double_helical"):
        shapef = herringshape
    elif getprop(ob, scene, "helical_on"):
        shapef = helicalshape
    else:
        shapef = identshape
        
    for i in range(steps):
        layer = layers[i]
            
        s2 = shapef(s)    
        th4 = th3*s2;
        
        costh4 = cos(th4)
        sinth4 = sin(th4)
        
        for v in layer:
            if v in shaftverts: continue
            
            try:
            #if 1:
                x, y = v.co[0], v.co[1]
            except ReferenceError:
                print("bmesh error, dead vert")
                layer.remove(v)
                continue
                
            """
            if s > 0.5:
                s2 = 1.0 - s*2
            else:
                s2 = s*2
            """
            
            v.co[0] = costh4*x + sinth4*y
            v.co[1] = costh4*y - sinth4*x
        
        s += ds
        
    if getprop(ob, scene, "taper_on"):
        if not ob.geargen.inner_gear_mode:
            scale = (radius - getprop(ob, scene, "taper_amount")) / radius
        else:
            scale = (radius + getprop(ob, scene, "taper_amount")) / radius
        
        taperh = getprop(ob, scene, "taper_height")
        
        tapersteps = 1
        for i, layer in enumerate(layers):
            z = layer[0].co[2]
            
            if z >= zmin + taperh:
                tapersteps = i
                break
        
        if not ob.geargen.inner_gear_mode:
            dscale = (1.0 - scale) / tapersteps
        else:
            dscale = (1.0 + scale) / tapersteps
        
        scale2 = scale
        dt = 1.0 / tapersteps
        t = 0
        
        for i, layer in enumerate(layers):
            z = layer[0].co[2]
            
            if z >= zmin + taperh and z <= zmax - taperh:
                continue
                
            for v in layer:
                if v in shaftverts: continue
                if ob.geargen.inner_gear_mode and v in inner_race_set:
                    continue;
                    
                v.co[0] *= scale2
                v.co[1] *= scale2
            
            if i < tapersteps:
                t += dt
                t2 = 1.0 - (1.0-t)*(1.0-t)
             
                scale2 = scale + (1 - scale)*t2
            elif i >= len(layers) -  tapersteps:
                t -= dt
                t2 = 1.0 - (1.0-t)*(1.0-t)
                scale2 = scale + (1 - scale)*t2
            
    """
        
    middle = []
    for v in geom:
        if not isinstance(v, bmesh.types.BMVert):
            continue
            
        v.co[2] = 0 
        middle.append(v)
    
    geom = bmesh.ops.extrude_face_region(bm, geom=geom)['geom']
    for v in geom:
        if not isinstance(v, bmesh.types.BMVert):
            continue
            
        v.co[2] = 0.5*thickness
    
    for v in middle:
        x, y, z = v.co
        th = dth*getprop(ob, scene, "helical_angle")*0.25*thickness
        
        v.co[0] = cos(th)*x + sin(th)*y
        v.co[1] = cos(th)*y - sin(th)*x
/        """

    for i, elayer in enumerate(elayers):
        if i == 0: continue
        last = elayers[i-1]
        
        for j, e2 in enumerate(elayer):
            e1 = last[j]
            
            try:
                pass
                bm.faces.new([e1.verts[0], e2.verts[0], e2.verts[1], e1.verts[1]])
            except:
                pass
           
    safe_triangle_fill(bm, elayers[0], profile)
    safe_triangle_fill(bm, elayers[-1], profile)
    
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    print("  ZOFF:", ob.geargen.zoff)
    for v in bm.verts:
      v.co[2] += ob.geargen.zoff
      
    #why do I have to do this twice?
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    #deal with shaft spacer ring
    if getprop(ob, scene, "spacer_on") and not getprop(ob, scene, "inner_gear_mode"):
      genShaftSpacer(ob, bm, gear, radius, 1, thickness, scene)
      genShaftSpacer(ob, bm, gear, radius, -1, thickness, scene)
      
    #do final scale in xy plane
    for v in bm.verts:
        v.co[0] *= ob.geargen.xy_scale
        v.co[1] *= ob.geargen.xy_scale
		
    #final load into ob.data
    bm.to_mesh(ob.data)
    ob.data.update()
