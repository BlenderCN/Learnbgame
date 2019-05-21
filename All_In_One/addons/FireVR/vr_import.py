# Import JanusVR from URL/filesystem
import os
import urllib.request as urlreq
import gzip
import bpy
from mathutils import Vector, Matrix
from math import radians
import re
import bs4

def s2v(s):
    return [float(c) for c in s.split(" ")]

def s2p(s):
    v = s2v(s)
    return [v[0], -v[2], v[1]]

def s2lp(s):
    v = s2v(s)
    return [v[0], v[2], v[1]]

def fromFwd(zdir):
    ydir = [0,1,0]
    xdir = Vector(zdir).cross(Vector(ydir))
    mtrx = Matrix([xdir, zdir, ydir])
    return mtrx

def neg(v):
    return [-e for e in v]

def rel2abs(base, path):
    if path.startswith("../"):
        parentdir = base[:-2 if base.endswith("/") else -1].rsplit("/", 1)[0]
        return os.path.join(parentdir, path[3:])

    return path

class AssetObjectObj:

    def __init__(self, basepath, workingpath, tag):
        self.downloaded_imgfiles = {}
        self.basepath = basepath
        self.workingpath = workingpath
        self.tag = tag
        self.id = tag["id"]
        self.src = tag["src"]
        self.sourcepath = os.path.dirname(self.src)
        self.mtl = tag.attrs.get("mtl", None)
        self.loaded = False
        self.imported = False
        self.objects = []

    def abs_source(self, base, path):
        base = rel2abs(self.basepath, base)
        if path.startswith("./"):
            path = path[2:]
        if path.startswith("/") or path.startswith("http://") or path.startswith("https://"):
            return path
        elif path.startswith("../"):
            return rel2abs(base, path)
        if base.startswith("http://") or base.startswith("https://"):
            return os.path.join(base, path).replace('\\','/')
        return os.path.join(base, path).replace('\\','/')

    def abs_target(self, path):
        return os.path.join(self.workingpath, os.path.basename(path))

    # Moves resources to the working directory
    def retrieve(self, path, base=None):
        if base is None:
            base = self.basepath
        source = self.abs_source(base, path)
        print('Retrieving '+source)
        target = self.abs_target(path)
        try:
            urlreq.urlretrieve(source, target)
        except:
            print('Error getting '+source)
        if path.endswith(".gz"):
            with gzip.open(target, 'rb') as infile:
                with open(target[:-3], 'wb') as outfile:
                    outfile.write(infile.read())

            return target[:-3]
        return target

    def load(self):

        if self.loaded:
            return

        if self.src is not None:
            self.src = self.retrieve(self.src)
            if self.mtl is None:
                with open(self.src,'r') as f:
                    contents = f.read()
                    mtllibs = re.findall(r"mtllib (.*?)", mtlfile.read())
                    for mtllib in mtllibs:
                        try:
                            self.mtl = abs_source( abs_source(self.basepath, self.tag["src"]), mtllib[0])
                        except Exception as e:
                            print(e)
                            self.mtl = None
                        print(self.mtl)
            if self.mtl is not None:
                #mtlpath = os.path.dirname(self.mtl)
                mtlpath = os.path.dirname(self.abs_source(self.basepath,self.mtl))
                self.mtl = self.retrieve(self.mtl)
                #print(self.mtl)
                imgfiles = []
                with open(self.mtl, "r") as mtlfile:
                    #imgfiles = re.findall(r"\b\w*\.(?:jpg|gif|png)", mtlfile.read())
                    imgfiles = re.findall(r"((\S*?)\.(?:jpg|jpeg|gif|png))", mtlfile.read())
                
                for imgfile in imgfiles:
                    if imgfile[0] not in self.downloaded_imgfiles:
                        self.downloaded_imgfiles[imgfile[0]] = self.retrieve(imgfile[0], mtlpath)

                # rewrite mtl to point to local file
                with open(self.abs_target(self.mtl), "r") as mtlfile:
                    file = mtlfile.read()
                for imgfile in imgfiles:
                    file = file.replace(self.downloaded_imgfiles[imgfile[0]], os.path.basename(imgfile[0]))
                with open(self.mtl, "w") as mtlfile:
                    mtlfile.write(file)
            self.loaded = True
            print('Loaded asset.')
    #An .obj can include multiple objects!
    def instantiate(self, tag):
        print(tag)
        self.load()
        if not self.imported:
            self.imported = True
            objects = list(bpy.data.objects)
            if self.mtl is not None:
                if self.mtl[:-4] != self.src[:-4]:
                    print('Rewriting obj')
                    # rewrite obj to use correct mtl
                    replaced = False
                    file = ""
                    with open(self.abs_target(self.src), "r") as mtlfile:
                        for line in mtlfile.read().split('\n'):
                            if line[:6] == 'mtllib':
                                file = file + 'mtllib ' + os.path.basename(self.mtl) + '\n'
                                replaced = True
                            else:
                                file = file + line + '\n'
                        if replaced == False:
                            file = 'mtllib ' + os.path.basename(self.mtl) + '\n' + file
                    with open(self.abs_target(self.src[:-4]+"_"+os.path.basename(self.mtl[:-4])+".obj"), "w") as mtlfile:
                        mtlfile.write(file)
                    bpy.ops.import_scene.obj(filepath=self.src[:-4]+"_"+os.path.basename(self.mtl[:-4])+".obj", axis_up="Y", axis_forward="Z")
                else:
                    bpy.ops.import_scene.obj(filepath=self.src, axis_up="Y", axis_forward="Z")
            else:
                bpy.ops.import_scene.obj(filepath=self.src, axis_up="Y", axis_forward="Z")
            self.objects = [o for o in list(bpy.data.objects) if o not in objects]
            obj = bpy.context.selected_objects[0]
            obj.name = self.id
        else:
            newobj = []
            for obj in self.objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_pattern(pattern=obj.name)
                bpy.ops.object.duplicate(linked=True)
                newobj.append(bpy.context.selected_objects[0])
            self.objects = newobj

        print(self.objects)
        for obj in self.objects:
            obj.scale = s2v(tag.attrs.get("scale", "1 1 1"))

            if "xdir" in tag.attrs or "ydir" in tag.attrs or "zdir" in tag.attrs:
                #obj.rotation_euler = (Matrix([s2v(tag.attrs.get("xdir", "1 0 0")), neg(s2v(tag.attrs.get("zdir", "0 0 1"))), s2v(tag.attrs.get("ydir", "0 1 0"))])).to_euler()
                xdir = s2v(tag.attrs.get("xdir", "1 0 0"))
                zdir = s2v(tag.attrs.get("zdir", "0 0 1"))
                if xdir[0] == zdir[2]:
                    zdir[2] = -zdir[2]
                if xdir[2] == zdir[0]:
                    zdir[0] = -zdir[0]
                obj.rotation_euler = (Matrix([xdir, zdir, s2v(tag.attrs.get("ydir", "0 1 0"))])).to_euler()
                
            else:
                obj.rotation_euler = fromFwd(neg(s2v(tag.attrs.get("fwd", "0 0 1")))).to_euler()

            obj.location = s2p(tag.attrs.get("pos", "0 0 0"))
        return list(self.objects)
def read_html(operator, scene, filepath, path_mode, workingpath):
    #FEATURE import from ipfs://
    if filepath.startswith("http://") or filepath.startswith("https://"):
        splitindex = filepath.rfind("/")
        basepath = filepath[:splitindex+1]
        basename = filepath[splitindex+1:]
    else:
        basepath = "file:///" + os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        filepath = "file:///" + filepath

    source = urlreq.urlopen(filepath.replace('\\','/'))
    html = source.read()
    fireboxrooms = bs4.BeautifulSoup(html, "html.parser").findAll("fireboxroom")
    if len(fireboxrooms) == 0:
        # no fireboxroom, remove comments and try again
        html = re.sub("(<!--)", "", html.decode('utf-8'), flags=re.DOTALL).encode('utf-8')
        html = re.sub("(-->)", "", html.decode('utf-8'), flags=re.DOTALL).encode('utf-8')
    soup = bs4.BeautifulSoup(html, "html.parser")
    fireboxrooms = soup.findAll("fireboxroom")
    print(str(len(fireboxrooms)))

    if len(fireboxrooms) == 0:
        operator.report({"ERROR"}, "Could not find the FireBoxRoom tag")
        return

    fireboxroom = fireboxrooms[0]

    rooms = fireboxroom.findAll("room")
    if rooms is None:
        operator.report({"ERROR"}, "Could not find the Room tag")
        return

    room = rooms[0]

    # Reset all changes in case of later error? Undo operator?
    # Prevent having to specify defaults twice? (on external load and addon startup)
    scene.janus_room_gravity = float(room.attrs.get("gravity", 9.8))
    scene.janus_room_walkspeed = float(room.attrs.get("walk_speed", 1.8))
    scene.janus_room_runspeed = float(room.attrs.get("run_speed", 5.4))
    scene.janus_room_jump = float(room.attrs.get("jump_velocity", 5))
    scene.janus_room_clipplane[0] = float(room.attrs.get("near_dist", 0.0025))
    scene.janus_room_clipplane[1] = float(room.attrs.get("far_dist", 500))
    scene.janus_room_teleport[0] = float(room.attrs.get("teleport_min_dist", 5))
    scene.janus_room_teleport[1] = float(room.attrs.get("teleport_min_dist", 100))
    scene.janus_room_defaultsounds = bool(room.attrs.get("default_sounds", True))
    scene.janus_room_cursorvisible = bool(room.attrs.get("cursor_visible", True))
    scene.janus_room_fog = bool(room.attrs.get("fog", False))
    scene.janus_room_fog_density = float(room.attrs.get("fog_density", 500))
    scene.janus_room_fog_start = float(room.attrs.get("fog_start", 500))
    scene.janus_room_fog_end = float(room.attrs.get("fog_end", 500))
    scene.janus_room_fog_col = s2v(room.attrs.get("fog_col", "100 100 100"))
    scene.janus_room_locked = bool(room.attrs.get("locked", False))

    jassets = {}

    assets = fireboxroom.findAll("assets")
    if assets is None:
        operator.report({"INFO"}, "No assets found")
        return

    for asset in assets[0].findAll("assetobject"):
        #dae might be different!
        #assets with same basename will conflict (e.g. from different domains)
        print(asset)
        
        if asset.attrs.get("src", None) is not None:
            print(asset['src'])
            if asset["src"].endswith(".obj") or asset["src"].endswith(".obj.gz"):
                jassets[asset["id"]] = AssetObjectObj(basepath, workingpath, asset)
            elif asset["src"].endswith(".dae") or asset["src"].endswith(".dae.gz"):
                jassets[asset["id"]] = AssetObjectDae(basepath, workingpath, asset)
            else:
                continue
        else:
            print('no src')
            continue

    objects = room.findAll("object")
    if objects is None:
        operator.report({"INFO"}, "No objects found")
        return

    for obj in objects:
        try:
            asset = jassets.get(obj["id"])
            if asset:
                asset.instantiate(obj)
        except:
            pass

class AssetObjectDae(AssetObjectObj):
    #An .obj can include multiple objects!
    def instantiate(self, tag):
        print(tag)
        self.load()
        if not self.imported:
            self.imported = True
            objects = list(bpy.data.objects)
            bpy.ops.wm.collada_import(filepath=self.src)
            self.objects = [bpy.data.objects[0]]
        else:
            newobj = []
            for obj in self.objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_pattern(pattern=obj.name)
                bpy.ops.object.duplicate(linked=True)
                newobj.append(bpy.context.selected_objects[0])
            self.objects = newobj

        print(self.objects)
        for obj in self.objects:
            obj.scale = s2v(tag.attrs.get("scale", "1 1 1"))

            if "xdir" in tag.attrs or "ydir" in tag.attrs or "zdir" in tag.attrs:
                xdir = s2v(tag.attrs.get("xdir", "1 0 0"))
                zdir = s2v(tag.attrs.get("zdir", "0 0 1"))
                if xdir[0] == zdir[2]:
                    zdir[2] = -zdir[2]
                if xdir[2] == zdir[0]:
                    zdir[0] = -zdir[0]
                obj.rotation_euler = (Matrix([xdir, zdir, s2v(tag.attrs.get("ydir", "0 1 0"))])).to_euler()
                
            else:
                obj.rotation_euler = fromFwd(neg(s2v(tag.attrs.get("fwd", "0 0 1")))).to_euler()
            obj.location = s2p(tag.attrs.get("pos", "0 0 0"))

    def load(self):

        if self.loaded:
            return

        if self.src is not None:
            src_orig = self.abs_source(os.path.dirname(self.basepath+"0"), self.src)
            print(src_orig)
            self.src = self.retrieve(self.src)
            self.parse_dae(self.src,src_orig)
            self.loaded = True

    def parse_dae(self, path, dae_url):
        f = open(path,'r')
        line = ''
        output = ''
        line = f.readline()
        while line != '':
            m = re.search('<init_from>(.*?)\.(jpg|png|gif|bmp)</init_from>', line)
            if m is not None:
                img = self.abs_source(os.path.dirname(dae_url), m.group(1)+'.'+m.group(2))
                print(img)
                img = self.retrieve(img, os.path.dirname(self.abs_source(self.basepath, self.src)))
                img = img[img.rfind(os.path.sep)+1:].replace('\\','/')
                line = re.sub('<init_from>(.*?)</init_from>', '<init_from>'+img+'</init_from>', line)
                print(line)
                output += line
            else:
                output += line
            line = f.readline()
        f.close()
        f = open(path,'w')
        f.write(output)
        f.close()
        
def load(operator, context, filepath, path_mode="AUTO", relpath="", workingpath="FireVR/tmp"):
    read_html(operator, context.scene, filepath, path_mode, workingpath)
