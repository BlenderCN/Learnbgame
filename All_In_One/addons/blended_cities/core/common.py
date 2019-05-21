import bpy
# 2.6
try : from bpy.types import Mesh, PointLamp, SpotLamp, HemiLamp, AreaLamp, SunLamp, Camera, TextCurve, MetaBall, Lattice, Armature
# 2.59
except :
    Mesh = bpy.types.Mesh
    PointLamp = bpy.types.PointLamp
    SpotLamp = bpy.types.SpotLamp
    HemiLamp = bpy.types.HemiLamp
    AreaLamp = bpy.types.AreaLamp
    SunLamp = bpy.types.SunLamp
    Camera = bpy.types.Camera
    TextCurve = bpy.types.TextCurve
    MetaBall = bpy.types.MetaBall
    Lattice = bpy.types.Lattice
    Armature = bpy.types.Armature

## returns an object or a list of objects
# @param ob 'all', 'active', 'selected', <object>, 'objectname'
# @return list of objects, or None
def returnObject(ob) :
    if type(ob) == str :
        if ob == 'all' : return bpy.context.scene.objects
        elif ob == 'active' : return [bpy.context.active_object] if bpy.context.active_object != None else []
        elif ob == 'selected' : return bpy.context.selected_objects
        else :
            try : return [bpy.data.objects[ob]]
            except : return []
    return [ob]


def dprint(str,level=1) :
    city = bpy.context.scene.city
    city.log.prt(str,level)
    #if level <= city.debuglevel :
    #    print(str)

## 
def display(elm, arg = 'outline', detail = True) :
    detail = True
    if arg == 'outline' :
        otl = elm
        elements = elm.Childs()
    else :
        otl = elm.Parent()
        elements = [elm]
    print('{:^77}\n{:^25}|{:^25}|{:^25}'.format('-'*77,' OUTLINE : %s'%(otl.name),'object  : %s'%(otl.objectName()),'type  : %s'%(otl.type)))
    if otl.parent :
        print(' parent : %s'%(otl.parent))
    print('{:^77}\n'.format('-'*77))
    for grp in elements :
        for child in grp.Childs() :
            if child.className() == 'outlines' :
                otl_child = 'has child'
                break
        else : otl_child = ''
        print('{:38}{:30}{:9}'.format('    GROUP : %s'%(grp.name),'builder : %s'%(grp.collection),otl_child))
        if detail :
            #print('{:^77}\n{:^25}|{:^25}|{:^25}\n{:^77}'.format('-'*77,'element name','object name','collection','-'*77))
            print('\n{:^25}|{:^25}|{:^25}\n{:^77}'.format('element name','object name','collection','-'*77))
            for child in grp.Childs() :
                if child.className() == 'outlines' : childname = '* %s'%child.name
                else : childname = child.name
                print('{:^25}|{:^25}|{:^25}'.format(childname,child.objectName(),child.className()))
            print('{:^77}\n'.format('-'*77))
    if detail == False : print('{:^77}\n'.format('-'*77))


## remove an object from blender internal
def wipeOutObject(ob,and_data=True) :
    objs = returnObject(ob)
    if objs :
        if type(objs) == bpy.types.Object : objs = [objs]
        for ob in objs :
            data = bpy.data.objects[ob.name].data
            #and_data=False
            # never wipe data before unlink the ex-user object of the scene else crash (2.58 3 770 2)
            # so if there's more than one user for this data, never wipeOutData. will be done with the last user
            # if in the list
            try :
                if data.users > 1 :
                    and_data=False
            except :
                and_data=False # empties have no user
            # odd :
            ob=bpy.data.objects[ob.name]
            # if the ob (board) argument comes from bpy.data.groups['aGroup'].objects,
            #  bpy.data.groups['board'].objects['board'].users_scene

            for sc in ob.users_scene :
                ob.name = '_dead'#print(sc.name)
                #ob.location = [-1000,0,0]
                sc.objects.unlink(ob)

            try :
                print('  removing object %s...'%(ob.name)),
                bpy.data.objects.remove(ob)
                print('  done.')
            except : print('  failed. now named %s and unlinked'%ob.name)

            # never wipe data before unlink the ex-user object of the scene else crash (2.58 3 770 2)
            if and_data :
                wipeOutData(data)


## remove an object data from blender internal
def wipeOutData(data) :
    #print('%s has %s user(s) !'%(data.name,data.users))
    if data.users <= 0 :
        try :
            data.user_clear()
            print('  removing data %s...'%(data.name))
            # mesh
            if type(data) == Mesh :
                bpy.data.meshes.remove(data)
            # lamp
            elif type(data) in [ PointLamp, SpotLamp, HemiLamp, AreaLamp, SunLamp ] :
                bpy.data.lamps.remove(data)
            # camera
            elif type(data) == Camera :
                bpy.data.cameras.remove(data)
            # Text, Curve
            elif type(data) in [ Curve, TextCurve ] :
                bpy.data.curves.remove(data)
            # metaball
            elif type(data) == MetaBall :
                bpy.data.metaballs.remove(data)
            # lattice
            elif type(data) == Lattice :
                bpy.data.lattices.remove(data)
            # armature
            elif type(data) == Armature :
                bpy.data.armatures.remove(data)
            else :
                print('  data still here : forgot %s type'%type(data))
            print('  done.')
        except :
            # empty, field
            print('%s has no user_clear attribute.'%data.name)
    else :
        print('  not done, %s has %s user'%(data.name,data.users))
