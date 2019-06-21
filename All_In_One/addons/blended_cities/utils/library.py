import bpy
from blended_cities.utils.geo import *

## load a group of object from an external blend
# wip : only dig in /library/default_props_v0.2.blend
# library methods should be handled by a dedicated addon/module
def libraryGet(request) :

    # define request
    city = bpy.context.scene.city
    path = city.path_library
    file = '/default_props_v0.2.blend'
    groupname = request

    if groupname not in bpy.data.groups :
        # retrieve
        pth = '//%s/Group/%s'%(file,groupname)
        dir = '%s%s/Group/'%(path,file)
        bpy.ops.wm.link_append(filepath=pth, directory=dir, filename=groupname, link=True, instance_groups=False)

        # IF GROUP INSTANCIED  original objects in layer 19
        #g=bpy.data.groups[groupname]
        #for ob in g.objects :
        #    ob.name = '_'+ob.name
        #    for li,l in enumerate(ob.layers) :
        #        l=False if li != 19 else True

    return bpy.data.groups[groupname]

def objectAppend(otl,request,c) :
    otl = otl.asOutline()
    #bld = otl.asBuilder()
    city = bpy.context.scene.city
    scale = bpy.context.scene.unit_settings.scale_length
    otlscale = otl.object().scale
    group = libraryGet(request)

    # WHEN GROUP IS APPENDED AND NOT LINKED. parent should be seek. only apply transfs on them
    '''
    #for ob in group.objects :
    #    # define 3d object
    #    obnew = ob.copy()
    #    obnew.name = bld.name + '.' + ob.name[1:]
    #    obnew.location = metersToBu([c])[0]
    #    obnew.scale[0] = obnew.scale[0] / scale / otlscale[0]
    #    obnew.scale[1] = obnew.scale[1] / scale / otlscale[1]
    #    obnew.scale[2] = obnew.scale[2] / scale / otlscale[2]
    #    # todo rotation
    #    obnew.parent = otl.object()
    #    bpy.context.scene.objects.link(obnew)

        # define as element
    #    bld.objectAdd(obnew)
    # twice for the last, to force parenting update else it won't move (2.58a)
    #obnew.parent = otl.object()
    '''

    # WHEN GROUP IS LINKED (the group itself is an ob)
    bpy.ops.object.group_instance_add(group = group.name)
    obnew = bpy.context.active_object
    #obnew.name = bld.name + '.' + obnew.name.split('.')[0]
    obnew.location = metersToBu([c])[0]
    obnew.scale[0] = obnew.scale[0] / scale / otlscale[0]
    obnew.scale[1] = obnew.scale[1] / scale / otlscale[1]
    obnew.scale[2] = obnew.scale[2] / scale / otlscale[2]
    #obnew.parent = otl.object()
    #bld.objectAdd(obnew)
    return obnew
