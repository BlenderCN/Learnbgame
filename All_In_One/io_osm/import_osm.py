import bpy
from xml.dom.minidom import parse,parseString
from collections import OrderedDict
from io_osm.helpers import Debugger
# TODO: support levels and multilevels.
# TODO: collision detection must be more precise, objects have to much offset.

profiler = False
debug = True
log = False

debugger = Debugger()

def load_osm(filepath, operator, context):
    from io_osm.osm_types import OSM
    if debug:
        debugger.start(log)
    if debug:
        debugger.debug("OSM import started: %r..." % filepath)
        debugger.debug("parsing xml to dom ...")

    # deactive undo for better performance and less memory usage
    global_undo = context.user_preferences.edit.use_global_undo
    context.user_preferences.edit.use_global_undo = False

    xml = parse(filepath)

    root = xml.documentElement

    # quit edit mode if enabled and deselect all objects
    editMode(context.scene,False)
    deselectObjects(context.scene)
    
    osm = OSM(root)
    if profiler:
        import profile
        import time
        profile.runctx('osm.generate(False)',{'debug':debug,'debugger':debugger,'log':log},{'osm':osm},'profile_results_'+time.strftime("%y-%m-%d-%H-%M-%S"))
    else:
        osm.generate(False)

    # everything went fine, so store filename
    bpy.context.scene.osm.file = filepath

    xml.unlink()

    if operator.create_tag_list:
        tag_list = ''
        tags = {}

        # get tags in nodes
        for id in osm.nodes:
            node = osm.nodes[id]
            for tag in node.tags:
                v = 'NODE:\t'+tag+' = '+node.tags[tag].value
                if v not in tags:
                    tags[v] = 1
                else:
                    tags[v]+=1

        # get tags in ways
        for id in osm.ways['by_id']:
            way = osm.ways['by_id'][id]
            for tag in way.tags:
                v = 'WAY:\t'+tag+' = '+way.tags[tag].value
                if v not in tags:
                    tags[v] = 1
                else:
                    tags[v]+=1

        for tag in OrderedDict(sorted(tags.items(),key=lambda t: t[1], reverse=True)):
            tag_list+="%s (%dx)\n" % (tag,tags[tag])
                    

        if "tags.txt" not in bpy.data.texts:
            bpy.data.texts.new('tags.txt')
        bpy.data.texts['tags.txt'].from_string(tag_list)

    # reset undo preference
    context.user_preferences.edit.use_global_undo = global_undo

def rebuild_osm(filepath,context):
    from io_osm.osm_types import OSM
    if debug:
        debugger.start(log)
    if debug:
        debugger.debug("OSM import started: %r..." % filepath)
        debugger.debug("parsing xml to dom ...")

    # deactive undo for better performance and less memory usage
    global_undo = context.user_preferences.edit.use_global_undo
    context.user_preferences.edit.use_global_undo = False

    xml = parse(filepath)

    root = xml.documentElement

    # quit edit mode if enabled and deselect all objects
    editMode(context.scene,False)
    deselectObjects(context.scene)

    osm = OSM(root)
    if profiler:
        import profile
        import time
        profile.runctx('osm.generate(True)',{'debug':debug,'debugger':debugger,'log':log},{'osm':osm},'profile_results_'+time.strftime("%y-%m-%d-%H-%M-%S"))
    else:
        osm.generate(True)
        
    xml.unlink()

    # reset undo preference
    context.user_preferences.edit.use_global_undo = global_undo

def remove_osm(context):
    for object in context.scene.objects:
        if object.osm.id!='':
            context.scene.objects.unlink(object)
            if object.data:
                mesh = object.data
            else:
                mesh = None
            bpy.data.objects.remove(object)

            if mesh:
                bpy.data.meshes.remove(mesh)
            

def load(operator, context, filepath=""):
    load_osm(filepath, operator, context)
    return {'FINISHED'}

def selectObject(scene,obj):
    obj.select = True
    scene.objects.active = obj #set the mesh object to current

def setOnLayer(obj,layer):
    for i in range(0,20):
        if i == layer:
            obj.layers[i] = True
        else:
            obj.layers[i] = False

def editMode(scene,mode=True):
    if mode:
        if scene.objects.active:
            bpy.ops.object.mode_set(mode='EDIT') #Operators
    else:
        if scene.objects.active:
            bpy.ops.object.mode_set(mode='OBJECT') #Operators

def selectMesh(mode=True):
    bpy.ops.object.mode_set(mode='EDIT') #Operators
    if mode:
        action = 'SELECT'
    else:
        action = 'DESELECT'
    bpy.ops.mesh.select_all(action=action)#select all the face/vertex/edge

def selectCurve():
    bpy.ops.object.mode_set(mode='EDIT') #Operators
    bpy.ops.curve.select_all(action='SELECT')#select all the face/vertex/edge

def deselectCurve():
    deselectMesh()

def deselectMesh():
    bpy.ops.object.mode_set(mode='OBJECT') # set it in object

def deselectObjects(scene):
    for i in scene.objects: i.select = False #deselect all objects

def deselectObject(obj):
    obj.select = False

def updateScene(scene):
    scene.update()

def getMandatoryTags(source):
    mandatory = []
    for tag in source.osm.tags:
        if tag.mandatory:
            mandatory.append(tag)
    return mandatory