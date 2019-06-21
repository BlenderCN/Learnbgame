from math import *
import bpy, bmesh
from mathutils import *
#from random import random, seed
from mathutils.geometry import *
import json
from .myrandom import seed, random
from .involute_gen import Profile
import os, sys, os.path, stat, subprocess

def normpath(path):
    return os.path.abspath(os.path.normpath(path))

def find_addon_path():
    list = []
    for path in sys.path:
        path = normpath(path)
        if "scripts" + os.path.sep + "addons" in path:
            list.append(path)
    
    for path in list:
        print(path + os.path.sep + "GearGen")
        if os.path.exists(path + os.path.sep + "GearGen") and os.path.exists(path + os.path.sep + "GearGen" + os.path.sep + "implicitgear"):
            return path + os.path.sep + "GearGen"
    
print("ADDON PATH:", find_addon_path())

implicitgearjs_path = find_addon_path() + os.path.sep + "implicitgear"; #"c:\\dev\\implicitgear"

def readJSON(path):
    file = open(path, "r")
    buf = file.read()
    file.close()
    
    return json.loads(buf)
    
def check_gearcache_validity():
    #see if gearcache needs to be purged
    path = implicitgearjs_path + os.path.sep + "package.json"
    j1 = readJSON(path)

    path = implicitgearjs_path + os.path.sep + "gearcache.json"
    if not os.path.exists(path):
        return
        
    j2 = readJSON(path)
    
    if j1["gearcache_version"] != j2["VERSION"]:
        print("Outdated gear cache version; deleting cache. . .")
        os.remove(path)

check_gearcache_validity()
        
def find_nodejs():
    windows = "win" in sys.platform.lower()
    
    splitchar = ";" if windows else ":"
    paths = os.environ["PATH"].split(splitchar)
    
    node_bin = "node.exe" if windows else "node"
    
    for path in paths:
        path = normpath(path)
        testpath = path + os.path.sep + node_bin
        ok = False
        
        try:
            if os.path.exists(testpath) and not stat.S_ISDIR(os.stat(testpath).st_mode): #make sure we're not a directory
                ok = True
        except:
            #file access error, presumably
            #annoyingly, python isn't consistent with file access exceptions across versions
            continue
        
        if ok:
            return testpath
            
    return None

def cachedGear(profile):
    #stupid node.js spawn delay
    #read implicitgear cache directly
    
    path = implicitgearjs_path + os.path.sep + "gearcache.json"
    if not os.path.exists(path):
        return None
    
    phash = "%.5f,%.5f,%.5f,%i,%.5f" % (profile.tdepth, profile.pressureth/180*pi, profile.twid, profile.numteeth, profile.backlash);
    phash += "," + ("true" if profile.inner_gear_mode else "false");
        
    file = open(path, "r")
    buf = file.read();
    file.close()
    
    obj = json.loads(buf)
    if phash in obj:
        rec = obj[phash]
        bm = bmesh.new()
        profile.radius = rec["radius"]
        lastv = None
        firstv = None
        
        for v in rec["verts"]:
            v = bm.verts.new(Vector([v[0], v[1], 0]))
            if lastv != None:
                bm.edges.new([lastv, v])
            else:
                startv = v
            lastv = v
        
        bm.edges.new([lastv, startv])
        return bm
        
    print("phash", phash, phash in obj, list((obj)));
    
def genGear(profile):
    bm = cachedGear(profile)
    if bm is not None:
        print("loaded gear from cache")
        return bm
        
    nodepath = find_nodejs()
    
    if nodepath is None:
        raise RuntimeError("Need node.js installed")
        
    curdir = os.getcwd()
    os.chdir(implicitgearjs_path)
    
    args = [
        nodepath,
        implicitgearjs_path + os.path.sep + "nodemain.js",
        
        "numteeth="+str(profile.numteeth),
        "modulus="+str(profile.twid),
        "depth="+str(profile.tdepth),
        "backlash="+str(profile.backlash),
        "inner_gear_mode="+str(profile.inner_gear_mode),
        "pressureth="+str(profile.pressureth / 180.0 * pi)
    ]
    
    bm = bmesh.new()
    
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
    stdout, stderr = proc.stdout, proc.stderr #proc.communicate()
    
    os.chdir(curdir)
    
    if type(stdout) == bytes:
        stdout = str(stdout, "latin-1")
    if type(stderr) == bytes:
        stderr = str(stderr, "latin-1")
        
    sys.stderr.write(stderr);
    
    stdout = stdout.replace("\r", "")
    
    profile.radius = -1
    
    vs = []
    lines = stdout.split("\n")
    for l in lines:
        l = l.strip()
        if l == "": continue
        if l.startswith("#"): 
            print(l)
            continue
        
        if l.startswith("pitch:"):
            print("Found pitch radius:", l)
            profile.radius = float(l[6:].strip())
        else:
            x, y = [float(f) for f in l.split(" ")]
            v = bm.verts.new(Vector([x, y, 0]))

            if len(vs) > 0:
                bm.edges.new([vs[-1], v])
                
            vs.append(v)
    
    if len(vs) > 1:
        bm.edges.new([vs[-1], vs[0]])
    return bm
    
print(find_nodejs())
