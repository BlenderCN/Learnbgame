##\file
# class_main.py
# contains the main collection classes :
# the elements class that stores every city element
# the outlines class that store each outline element
# methods used by builders classes are also inherited from here
print('class_main.py')
import bpy
import mathutils
from mathutils import *
from blended_cities.utils.meshes_io import *
from blended_cities.utils import library
from blended_cities.utils.geo import *
from blended_cities.core.common import *

##\brief the main city elements collection
#
# store any element of the city, including outlines. allows 'real' object / element lookups
# @param name used internally as key for parenting and element lookup ! shouldn't be modified !
# @param type used for lookup between the element as element and the same element as builder or outline. I don't think it's useful anymore, since the name gives the info about the class of the element.
# @param pointer is the pointer to the real object. set to -1 if the object is missing. i fact it correspond to the obj.as_pointer() function. it allows to change the name of the real object without breaking the relation-ship between the element and the object.
class BC_elements(bpy.types.PropertyGroup) :
    bc_label = 'Element'
    bc_description = 'any city object'
    bc_collection = 'elements'
    bc_element = 'element'

    name  = bpy.props.StringProperty()
    collection  = bpy.props.StringProperty() # a builder collection name / the 'outlines' collection name
    #group  = bpy.props.StringProperty() # the group name  actually the name of its blender group...
    pointer = bpy.props.StringProperty(default='-1') # data pointer to get the object

    ###############################
    ## LOOKUPS METHODS
    ###############################

    ## given the element name, returns its id in its collection
    #
    # warning : indexes of the same element in elements, in outlines, or in builders can differs, so be sure of the className() of the element.
    def index(self) :
        return int(self.path_from_id().split('[')[1].split(']')[0])


    ## returns the class of the element as string : 'elements', 'outlines', 'groups', or builder name
    # @param True default. if False, returns the builder class name the element or the group belongs to.
    def className(self,itself=True) :
        if itself : return self.bc_collection
        return self.collection if self.bc_collection in ['elements'] else self.bc_collection
        #return self.collection if self.bc_collection in ['elements','groups'] else self.bc_collection
        

    ## returns the class of the element itself. 
    # @param True default. if False, returns the builder class the element or the group belongs to.
    def Class(self,itself=True) :
        city = bpy.context.scene.city
        clname = self.className(itself)
        #print(clname)
        if clname in ['outlines', 'elements','groups'] :
            return eval('city.%s'%clname)
        else :
            return eval('city.builders.%s'%clname)


    ## returns the element in its class (otl, bld or grp) 
    # @param True default. if False, returns the builder class the element or the group belongs to.
    def inClass(self,itself=True) :
        elmClass = self.Class(itself)
        return elmClass[self.name]


    ## given any kind of element, returns it as member of the main elements collection
    def asElement(self) :
        return bpy.context.scene.city.elements[self.name]


    ## given any kind of element, returns the outline of it
    def asOutline(self) :
        city = bpy.context.scene.city
        if self.className() == 'groups' :
            return self.Parent()

        if self.className() == 'elements' :
            self = self.inClass(False)

        if self.className() == 'outlines' :
            return self
        else :
            return self.Parent().Parent()


    ## given any kind of element, returns the group it belongs to
    def asGroup(self) :
        city = bpy.context.scene.city
        if self.className() == 'groups' :
            return self
        self = self.inClass(False)
        if self.className() == 'outlines' :
            return self.Childs(0)
        #if self.parent :
        return city.groups[self.parent]
        #return None


    ## given any kind of element, returns the element in its builder class
    def asBuilder(self) :
        city = bpy.context.scene.city
        #self = 
        if self.className() == 'outlines' :
            return self.Childs(0).Childs(0)
        if self.className() == 'groups' :
            return self.Childs(0)
        return self.inClass(False)


    ## given an outline, returns the builder
    ## given an builder,  returns the outline
    def peer(self) :
        city = bpy.context.scene.city
        if self.className() == 'elements' :
            elmclass = self.Class(False)
            self = elmclass[self.name]
        if self.className() == 'outlines' :
            self = city.elements[self.attached]
            elmclass = self.Class(False)
            return elmclass[self.name]
        else :
            self = city.elements[self.attached]
            return city.outlines[self.name]


    ## from an element, returns the object or the list of objects
    def object(self) :
        elm = self.asElement()
        if elm.pointer == '-1' : return False
        pointer = int(elm.pointer)
        for ob in bpy.context.scene.objects :
            if ob.as_pointer() == pointer :
                return ob
        elm.pointer = '-1'
        print('object data missing, removed pointer')
        return False


    ## from an element, returns the object name / the object names in a list
    def objectName(self) :
        ob = self.object()
        if ob :
            return ob.name
        else : return 'not built'


    ## change the object and the mesh names of the element object to the element name 
    # @return new name as string if done, else False (object missing or a group of objects is attached, not a single object)
    def objectNameSet(self,name=False) :
        ob = self.object()
        if name == False : name = self.name
        if ob : 
            if type(ob) == bpy.types.Object :
                ob.name = name
                ob.data.name = name
                return name
            return False
        else : return False


    ## name a new element in the element class.
    def nameNew(self,tag=False,id=0) :
        if tag == False :
            tag = self.bc_element
        if '.' in tag : name = '%s.%1.3d'%(tag,id)
        else : name = '%s.%1.5d'%(tag,id)

        if self.className() == 'groups' :
            collection = bpy.context.scene.city.groups
        else :
            collection = bpy.context.scene.city.elements

        while name in collection :
            id += 1
            if '.' in tag : name = '%s.%1.3d'%(tag,id)
            else : name = '%s.%1.5d'%(tag,id)
        self.name = name
        return name


    ## returns the name of the root element in a family of element
    # not sure about this one : should really the name of child elements have two numeric fields ?
    # internally almost useless.
    def nameMain(self) :
        n = self.name.split('.')
        if len(n) > 2 : 
            return n[0]+'.'+n[1]
        else :
            return self.name


    ## rename an outline, rewrite relationships, update element
    # not sure that's a good idea.. though it could be used by elementRemove(), wait and see
    #def rename(self,name) :
    #    city = bpy.context.scene.city
    #    oldname = self.name
    #    self.name = name
    #    if self.parent != '' :
    #        city.outlines[self.parent].childRemove(oldname)
    #        city.outlines[self.parent].childsAddName(name)
    #    for child in self.childslist() :
    #        city.outlines[child].parent = name
    #    self.asElement().name = name


    ## returns a list of childs name
    def ChildsName(self) :
        return self.childs.split(',')


    ## returns a child or a list of childs as element
    # @param id -1 (default) the child index. -1 for last. id > len(childs) returns last child
    # @return the element, all the elements in a list, or [] ( can be iterated directly even if None)
    def Childs(self,id=-1) :
        if self.childs :
            city = bpy.context.scene.city
            childnames = self.ChildsName()
            if id == -1 :
                childList = []
                for childname in childnames :
                    if self.className() == 'groups' :
                        childList.append(city.elements[childname].asBuilder())
                    else :
                        childList.append(city.groups[childname])
                return childList
            else :
                if id  >= len(childnames) : id = -1
                if self.className() == 'groups' :
                    return city.elements[childnames[id]].asBuilder()
                else :
                    return city.groups[childnames[id]]
        return []


    ## returns the parent element of an outline, a builder or a group
    # @return the element or None
    def Parent(self) :
        if self.parent :
            city = bpy.context.scene.city
            if self.className() == 'groups' :
                return city.outlines[self.parent]
            else :
                return city.groups[self.parent]
        return None


    ## returns the next sibling
    # @return the element or None
    def Next(self,attached=False) :
        outlines = bpy.context.scene.city.outlines
        self = self.inClass(False)
        if self.parent :
            siblings = self.Parent().Childs()
            if len(siblings) > 1 :
                si = siblings.index(self.name)
                try : sibling = outlines[siblings[si+1]]
                except : return None
                return sibling.peer() if attached else sibling
        return None


    ## returns the previous sibling
    # @param attached False (default) returns the outline parent. True returns the builder attached
    # @return the element or None
    def Previous(self,attached=False) :
        outlines = bpy.context.scene.city.outlines
        if self.asOutline().parent :
            siblings = self.Parent().Childs()
            if len(siblings) > 1 :
                si = siblings.index(self.name)
                if si > 0 : sibling = outlines[siblings[si-1]]
                else : return None
                return sibling.peer() if attached else sibling
        return None


    ## from an element, returns and select the object
    def select(self,attached=False) :
        #print('select %s %s %s'%(self.name,self.className(),attached))
        if attached :
            ob = self.peer().object()
        else :
            ob = self.object()
        if ob :
            bpy.ops.object.select_all(action='DESELECT')
            if type(ob) == bpy.types.Object : ob = [ob]
            for o in ob :
                o.select = True
            bpy.context.scene.objects.active = o
        else : return False


    ## selects the parent object of the current element
    # @param attached (default False) if True returns always the builder object and not the outline
    def selectParent(self,attached=False) :
        if self.className() == 'elements' : self = self.asBuilder()
        if self.className() != 'outlines' :
            self = self.peer()
            attached = True
        outlines = bpy.context.scene.city.outlines
        if self.parent != '' :
            self = outlines[self.parent]
        self.select(attached)


    ## selects the first child object of the current element
    # @param attached (default False) if True returns always the builder object and not the outline
    def selectChild(self,attached=False) :
        child = self.Childs(0)
        if child : child.select(attached)


    ## selects the next sibling object of the current element
    # @param attached (default False) if True returns always the builder object and not the outline
    def selectNext(self,attached=False) :
        if self.className() == 'elements' : self = self.asBuilder()
        if self.className() != 'outlines' :
            self = self.peer()
            attached = True
        outlines = bpy.context.scene.city.outlines
        if self.parent != '' :
            siblings = outlines[self.parent].Childs()
            if len(siblings) > 1 :
                si = siblings.index(self.name)
                sibling = outlines[siblings[(si+1)%len(siblings)]]
                sibling.select(attached)


    ## selects the previous sibling object of the current element
    # @param attached (default False) if True returns always the builder object and not the outline
    def selectPrevious(self,attached=False) :
        if self.className() == 'elements' : self = self.asBuilder()
        if self.className() != 'outlines' :
            self = self.peer()
            attached = True
        outlines = bpy.context.scene.city.outlines
        if self.parent != '' :
            siblings = outlines[self.parent].Childs()
            if len(siblings) > 1 :
                si = siblings.index(self.name)
                sibling = outlines[siblings[(si-1)%len(siblings)]]
                sibling.select(attached)


    # OTL and GRP
    ## add a child to an outline or a group.
    # @param childname the outline name (string)
    def childsAddName(self,childname) :
        #self = self.asOutline()
        if self.childs == '' :
            self.childs = childname
        elif childname not in self.childs :
            self.childs += ',%s'%childname


    # OTL and GRP
    ## delete a child outline reference of this outline.
    # @param childname the outline name (string)
    def childsRemoveName(self,childname) :
        childnames = self.ChildsName()
        #print('removing %s from %s : %s'%(childname,self.name,childnames))
        if childname in childnames :
            del childnames[childnames.index(childname)]
            newchilds = ''
            for child in childnames : newchilds += child+','
            self.childs = newchilds[:-1]
        if self.childs == '' : dprint('  %s childs : none'%self.name)
        else : dprint('  %s childs : %s'%(self.name,self.childs))


    ## attach an existing object to an outline
    def objectAttach(self,object) :
        otl = self.asOutline()
        city = bpy.context.scene.city
        ob = returnObject(object)
        if ob != [] : ob = ob[0]
        else : return False

        test = city.elementGet(ob)
        if  test == False :
            otl.objectRemove()
            otl.asElement().pointer = str(ob.as_pointer())
            otl.dataRead()
            otl.build()
            return True
        else :
            print('object %s already attached to %s'%(ob.name,test.name))
        return False

    ## detach the object of its element
    def objectDetach(self) :
        self = self.asElement()
        if self.pointer != '-1' :
            ob = self.object()
            if ob.name == self.name :
                ob.name = ob.name.split('.')[0] + '_free.' + ob.name.split('.')[1]
            if type(ob.data) != None : ob.data.name = ob.name
            objectLock(ob,False)
            mat = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = mat
            self.pointer = '-1'


    ###############################
    ## OUTLINES / BUILDERS OPERATION
    ###############################

    ## move a builder to another outline by moving the outline pointer to another object  
    # @param object an object or its name
    # @return True if the object has been attached
    def _objectAttach(self,object) :
        city = bpy.context.scene.city
        ob = returnObject(object)
        if ob != [] : ob = ob[0]
        else : return False
        test = city.elementGet(ob)
        if  test == False :
            otl_elm = self.asOutline().asElement()
            if otl_elm.pointer != '-1' :
                otl_elm.objectDetach()
            otl_elm.pointer = str(ob.as_pointer())
            otl_elm.asOutline().dataRead()
            #otl_elm.asBuilder().build()
            city.builders.build(otl_elm.asBuilder())
            return True
        else :
            print('object %s already attached to %s'%(ob.name,test.name))
        return False


    ## Delete  an outline/builder object
    def objectRemove(self) :
        elm = self.asElement()
        ob = elm.object()
        if ob :
            wipeOutObject(ob)
            elm.pointer = '-1'


    ## add a new elm in Elements, used when creating a new otl or bld. its name is the caller name
    # @return the new element in Elements 
    def _add(self) :
        city = bpy.context.scene.city
        if self.className() != 'elements' and self.name not in city.elements :
            elm = city.elements.add()
            elm.name = self.name
            elm.collection = self.className()
            if self.parent :
                self.Parent().childsAddName(self.name)
            return elm
        print('_add : elm %s already there'%self.name)


    ## remove an elm from Elements and the corresponding elm or bld
    ## or grp from groups
    def _rem(self) :
        self = self.inClass(False)
        selfclass = self.Class()
        if self.parent :
            self.Parent().childsRemoveName(self.name)
        if self.className() != 'groups' :
            ielm  = self.asElement().index()
            bpy.context.scene.city.elements.remove(ielm)
        iclass = self.index()
        selfclass.remove(iclass)


##\brief the outlines collection
#
# this collection stores retionship between elements, and the geometry data of the outline. an outline is always attached to a builder element, and reciproquely.
#
# @param type not sure it's useful anymore... 
# @param attached (string) the name of the builder object attached to it
# @param data (dictionnary as string)stores the geometry, outline oriented, of the outline object
# @param childs (list as string) store outlines parented to the outline element "child1,child2,.."
# @param parent  the parent outline name if any (else '')
class BC_outlines(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Outline'
    bc_description = 'an outline object'
    bc_collection = 'outlines'
    bc_element = 'outline'
    type   = bpy.props.StringProperty() # generated, user, stacked.....
    #attached = bpy.props.StringProperty() # its attached builder
    data = bpy.props.StringProperty(default="{'perimeters':[], 'lines':[], 'dots':[], 'matrix':Matrix() }") # global. if the outline object is missing, create from this
    childs = bpy.props.StringProperty(default='') # several group names separated by commas
    parent = bpy.props.StringProperty(default='') # a group name or ''
    #generated = bpy.props.BoolProperty(default=False)

    ## given an outline, retrieves its geometry in meters as a dictionnary from the otl.data string field :
    # @param what 'perimeters', 'lines', 'dots', 'matrix', or 'all' default is 'perimeters'
    # @return a nested lists of vertices, or the world matrix, or all fields in a dict.
    def dataGet(self,what='perimeters',meters=True) :
        data = eval(self.data)
        if meters :
            print('dataGet returns %s %s datas in Meters'%(self.name,what))
            data['perimeters'] = buToMeters(data['perimeters'])
            data['lines'] = buToMeters(data['lines'])
            data['dots'] = buToMeters(data['dots'])
        #else : print('dataGet returns %s %s datas in B.U.'%(self.name,what))          
        data['matrix'] = Matrix(data['matrix'])
        if what == 'all' : return data
        return data[what]


    ## set or modify the geometry of an outline
    # @param what 'perimeters', 'lines', 'dots', 'matrix', or 'all' default is 'perimeters'
    # @param data a list with nested list of vertices or a complete dictionnary conaining the four keys
    def dataSet(self,data,what='perimeters',meters=True) :
        if what == 'all' : pdata = data
        else :
            pdata = self.dataGet('all',meters)
            pdata[what] = data
        if meters :
            print('dataSet received %s %s datas in meters :'%(self.name,what)) 
            pdata['perimeters'] = metersToBu(pdata['perimeters'])
            pdata['lines'] = metersToBu(pdata['lines'])
            pdata['dots'] = metersToBu(pdata['dots'])
        #else : print('dataSet received %s %s datas in BU :'%(self.name,what))
        self.data = '{ "perimeters": ' + str(pdata['perimeters']) + ', "lines":' + str(pdata['lines']) + ', "dots":' + str(pdata['dots']) + ', "matrix":' + matToString(pdata['matrix']) +'}'


    ## read the geometry of the outline object and sets its data (dataSet call)
    # @return False if object does not exists
    def dataRead(self) :
        print('dataRead outline object of %s'%self.name)
        obsource=self.object()
        if obsource :
            # data extracted are in BU no meter so dataSet boolean is False
            mat, perims, lines,dots = outlineRead(obsource)
            data = {'perimeters':perims, 'lines':lines, 'dots':dots, 'matrix':mat }
            self.dataSet(data,'all',False)
            return True
        else :
            print('no object ! regenerate')
            self.dataWrite()
            print('done regenerate')
            return False
        print('dataReaddone')


    ## write the geometry in the outline object from its data field (dataGet call)
    # inputs and outputs are in meters
    def dataWrite(self) :
        print('dataWrite outline ob for %s'%self.name)
        data = self.dataGet('all')
        verts = []
        edges = []
        ofs = 0
        for perimeter in data['perimeters'] :
            verts.extend(perimeter)
            edges.extend( edgesLoop(ofs, len(perimeter)) )
            ofs += len(perimeter)
        for line in data['lines'] :
            verts.extend(line)
            edges.extend( edgesLoop(ofs, len(line),True) )
            ofs += len(line)
        for dot in data['dots'] :
            verts.append(dot)
        #print('>',verts,edges)
        #print(len(verts),len(edges))
        ob = objectBuild(self,verts,edges)
        self.asElement().pointer = str(ob.as_pointer())
        ob.matrix_local = Matrix()#data['matrix']
        print('dataWrite done')


    ## remove an Outline and its childs
    # cares about relationship
    # @param del_object (default True) delete the attached object
    def remove(self, rem_self=False, rem_elements=False, rem_objects=True, rem_childs=False) :
        dprint('* outline.remove')
        city = bpy.context.scene.city
        '''
        # rebuild relationship
        parent = otl.parent
        childs = otl.Childs()
        for child in childs :
            city.outlines[child].parent = parent
        if parent != '' :
            otl.Parent().childsRemoveName(otl.name)
            for child in childs :
                otl.Parent().childsAddName(child)
            #otl.Parent().asBuilder().build(True) # this to update the childs
            city.builders.build(otl.Parent().asBuilder())
        '''
        groupsname = list(self.ChildsName())
        for groupname in groupsname :
            group = city.groups[groupname]
            group.remove(rem_self, rem_elements, rem_objects, rem_childs, False)
        if rem_objects and self.type != 'user' :
            self.objectRemove()
        if rem_self :
            if rem_objects == False : self.objectDetach()
            self._rem()

    ## add a new group to an outline
    def groupAdd(self,builder='',update=True) :
        if builder == '' : builder = 'nones'
        city = bpy.context.scene.city
        elmclass = city.Class(builder)
        if elmclass == False : return False

        # remove default none group of the outline if exists
        no = self.Childs(0)
        dprint('existing group %s'%no)
        if no and no.collection == 'nones' :
            dprint('removing nones')
            no.remove()
        # add the builder group
        grp = city.groups.add()
        grp.nameNew(builder)
        grp.collection = builder
        grp.parent  = self.name
        self.childsAddName(grp.name)
        gr = bpy.data.groups.new(grp.name)

        # add a default group member in its builder class, member/group link
        bld  = elmclass.add()
        bld.nameNew()
        bld.parent = grp.name
        bld._add()
        dprint('otl.groupAdd : main element of %s group is %s'%(grp.name,bld.name))
        if update : grp.build()
        return grp

    ## outline build() method
    def build(self) :
        if self.type == 'stacked' :
            grp = self.Parent()
            otl = grp.Parent()
            mat_ori = otl.object().matrix_world.copy()
            loc, rot, otl_scale = mat_ori.decompose()
            print('parent outline is : %s'%otl.name)
            z = grp.height()
            world_scale = bpy.context.scene.unit_settings.scale_length
            z /= world_scale * otl_scale[2]
            self.object().location = [0, 0, z]
        for grp in self.Childs() :
            grp.build()


##\brief the groups collection
# handles the build() requests
class BC_groups(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Groups'
    bc_description = 'group of object(s) generated by a builder'
    bc_collection = 'groups'
    bc_element = 'group'
    collection = bpy.props.StringProperty(default='') # the builder used to create this group of ob/elm
    childs = bpy.props.StringProperty(default='') # member of the group (element names separated by commas)...
    parent = bpy.props.StringProperty(default='') # an outline name. mandatory


    ## build or update a builder group
    def build(grp,refreshData=True) :
        city = bpy.context.scene.city
        #if self.className() != 'groups' : grp = self.Parent()
        #else : grp = self
        #grp = self
        print('** build %s'%grp.name)
        display(grp,'group')
        otl = grp.Parent()
        bld = grp.Childs(0)

        if refreshData :
            print('ask for data read')
            otl.dataRead()
    
        data = otl.dataGet('all')

        mat_ori = data['matrix'].copy()
        mat_ori.invert()
        loc, rot, scale = mat_ori.decompose()
        mat = Matrix()
        mat[0][0] *= scale[0]
        mat[1][1] *= scale[1]
        mat[2][2] *= scale[2]
        mat *= rot.to_matrix().to_4x4()

        materialsCheck(bld)
        print(bld.name,bld.className())
        objs = bld.build(data)
        print('  received %s objects :'%len(objs))
        if len(objs) > 0 :
            generated=[]
            # build returned objects
            for idx,ob in enumerate(objs) :
                # object/element name
                if idx == 0 : name = bld.name
                else : name = '%s.%1.3d'%(bld.name,idx)
                print('    %s'%(name))
                # a generated mesh
                if type(ob[0]) == list :
                    datas = [ [] for i in range(0,5) ]
                    for i, data in enumerate(ob) : 
                        datas[i] = data
                    for vi,v in enumerate(datas[0]) :  datas[0][vi] = mat *  datas[0][vi]
                    matslots = bld.materialslots
                    ## verts, edges, faces, matslots, mats, uvs
                    ob = objectBuild(name, datas[0], datas[1], datas[2], matslots, datas[3], datas[4])
                    ob.name = name
                    builder = grp.collection
                    '''
                    verts, edges, faces, mats, uvs = ob
                    uvs = []
                    for vi,v in enumerate(verts) : verts[vi] = mat * verts[vi]
                    matslots = bld.materialslots
                    ## verts, edges, faces, matslots, mats, uvs
                    ob = objectBuild(name, verts, edges, faces, matslots, mats, uvs)
                    ob.name = name
                    builder = grp.collection
                    '''
                # a generated outline
                elif type(ob[0]) == str and ob[0] == 'outline' :
                    dummy, verts, edges, faces, mats = ob
                    for vi,v in enumerate(verts) : verts[vi] = mat * verts[vi]
                    matslots = bld.materialslots
                    ob = objectBuild(name, verts, edges, faces, matslots, mats)
                    builder = 'outlines'
                # an object from the library
                elif type(ob[0]) == str :
                    request, coord = ob
                    ob = library.objectAppend(otl, request, coord*mat)
                    elm = city.elementGet(name)
                    if elm : elm.objectRemove()
                    ob.name = name
                    builder = 'objects'
                objectLock(ob)
                elm = grp.objectAdd(ob,builder)
                generated.append(ob)
                if builder == 'outlines' :
                    elm = elm.asOutline()
                    elm.type = 'generated'
            # remove previous generated and non updated objects from scene and collections
            objs = bpy.data.groups[grp.name].objects
            print('** removing ? %s %s'%(len(objs), len(generated)))
            if len(objs) != len(generated) :
                print('   group : %s\n   generated : %s'%(objs, generated))
                for ob in objs :
                    if ob not in generated :
                        elm = city.elementGet(ob)
                        dprint('stack test : %s %s %s'%(elm.name,elm.className(False),elm.asOutline().type))
                        # don't remove outlines added by the user, like stacked outlines
                        if elm.className(False) == 'outlines' and elm.asOutline().type != 'generated' :
                            continue
                        grp.remove(False,True,ob,True)

            # child outlines update
            for child in grp.Childs() :
                if child.className() == 'outlines' :
                    child.build()

        print('** end build %s'%bld.name)


    ## Remove this group and its childs
    def remove(self, rem_self=True, rem_elements=True, rem_objects=True, rem_childs=True, keepNones=True) :
        dprint('* group.remove')
        city = bpy.context.scene.city
        if  type(rem_objects) == bpy.types.Object :
            rem_objects = returnObject(rem_objects)
            all = False
        else : all = True
        childs = list(self.ChildsName())
        for child in childs :
                child = city.elements[child].asBuilder()
                if all or child.object() in rem_objects :
                    dprint('  removing %s %s :'%(child.className(),child.name))
                    if child.className() == 'outlines' :
                        if rem_childs == False :
                            if self.parent : newparent = self.parent
                            else : newparent = ''
                            child.parent = newparent
                            print(child.parent,newparent,self.parent)
                        else: #if rem_childs :
                            child.remove(rem_elements, rem_elements, rem_objects, rem_childs)
                    else :
                        if rem_objects :
                            child.objectRemove()
                        if rem_elements :
                            if rem_objects == False : child.objectDetach()
                            child._rem()
                    dprint('  done')

        # remove group element
        if rem_self :
            dprint('  removing group %s'%self.name)

            gr = bpy.data.groups[self.name]
            bpy.data.groups.remove(gr)

            # removing a 'nones' group means adding a new group to an empty otl. forces keepNones to False
            otl = self.Parent()
            if self.collection == 'nones' : keepNones = False
            print('*%s %s %s'%(self.collection,keepNones,otl.childs))
            # it otl has no childs anymore, add a none group child to it.
            if keepNones and otl.childs == self.name :
                dprint('  adding a none group to %s'%otl.name)
                otl.groupAdd()
            self._rem()
        dprint('end group.remove')


    ## replace this builder group by a new one
    def replace(self,builder) :
        dprint('* group.replace')
        if self.collection == builder : return False
        city = bpy.context.scene.city
        elmclass = city.Class(builder)
        if elmclass == False : return False

        # remove group
        self.remove(False,True,True,True,False)

        # redefine group
        self.Parent().childsRemoveName(self.name)
        self.nameNew(builder)
        self.Parent().childsAddName(self.name)
        self.collection = builder
        gr = bpy.data.groups.new(self.name)

        # add a default group member in its builder class, member/group link
        bld  = elmclass.add()
        bld.nameNew()
        bld.parent = self.name
        bld._add()
        dprint('grp.replace() : main element of %s group is %s'%(self.name,bld.name))
        self.build()
        return self


    ## stack a new or existing group over this group
    def stack(self,what='',builder='',update=True) :
        dprint('* group.stack')
        city = bpy.context.scene.city
        # stack a new outline
        if what == '' :
            dprint('  creating new outline')
            otl = city.outlines.add()
            otl.nameNew()
            otl._add()
            otl.data = self.Parent().data
            otl.dataWrite()
            ob = otl.object()
        # stack an existing object. TODO not really tested yet
        else :
            dprint('  use given object as outline')
            ob = returnObject(what)
            if ob != [] :
                ob = ob[0]
                elm = city.elementGet(ob)
                if elm :
                    if elm.className(False) != 'outlines' or elm.asOutline().type == 'generated' :
                        dprint("grp.stack : only non-generated outlines are stackable (%s %s)"%(elm.name,elm.className(False)))
                        return False
                    otl = elm.asOutline()
                else :
                    otl = city.outlines.add()
                    otl.nameNew()
                    otl._add()
                    otl.objectAttach(ob)
        otl.type = 'stacked'
        self.objectAdd(ob,'outlines')
        grp = otl.groupAdd(builder,False)
        if update : otl.build()
        dprint('otl parent : %s'%otl.parent)
        return grp


    ## add/update the builder object of a group
    def objectAdd(self,what='active',builder='objects') :
        dprint('* group.objectAdd')
        city = bpy.context.scene.city
        grp = self
        #self = self.asElement()
        otl = grp.asOutline()
        ob = returnObject(what)
        elmClass = city.Class(builder)

        if ob != [] :
            ob = ob[0]
            # check if the object already exists in collections
            # if not defined, add it in a collection
            elm = city.elementGet(ob)
            print(elm)
            if elm == False :
                # reuse the element with the same name
                if ob.name in city.elements and city.elements[ob.name].pointer == '-1' :
                    elm = city.elements[ob.name].inClass(False)
                    print('  found %s element with no objects attached, used it'%(elm.name))
                else :
                    # create a new element
                    elm = elmClass.add()
                    elm.name = ob.name # named by group build()
                    elm._add()
                    print('  added object %s as %s in the %s collection'%(ob.name,elm.name,builder))
                elm.asElement().pointer = str(ob.as_pointer())
            else :
                elm = elm.inClass(False)
                print('  object %s <-> elm %s'%(ob.name,elm.name))
            elm.parent = grp.name
            dprint('  otl parent : %s'%elm.parent)
            # update the blender group
            objs = bpy.data.groups[grp.name].objects
            if ob not in objs.values() :
                objs.link(ob)

            # updtate the group childs list
            grp.childsAddName(elm.name)
            dprint('  group %s :\n    blender group members : %s'%(grp.name,bpy.data.groups[grp.name].objects.keys()))
            dprint('    childs : %s'%(grp.childs))

            # parent the object
            ob.parent = otl.object()
            
            if builder == 'outlines' :
                otl = elm.asOutline()
                if otl.Childs() == [] : otl.groupAdd()
            return elm
                
        else :
            print('grp.objectAdd : object %s not found'%(what))


    def height(self) :
        return self.asBuilder().height()


##\brief the nones collection
# used by empty outilnes with no builder attached. length of the collection gives the free outlines number.
# the none elm of an empty otl is removed when it's attached to a real builder
class BC_nones(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Nones'
    bc_description = 'a null object. used to add a single outline'
    bc_collection = 'nones'
    bc_element = 'none'

    parent = bpy.props.StringProperty() #  name of the group it belongs to

    def build(self,data) :
        return []
    def height(self) :
        return 0


##\brief the objects collection
# used to store elements that come from the library, when library calls are used by a builder
class BC_objects(BC_elements,bpy.types.PropertyGroup) :
    bc_label = 'Objects'
    bc_description = 'a null object. used to add a single outline'
    bc_collection = 'objects'
    bc_element = 'obj'

    parent = bpy.props.StringProperty() #  name of the group it belongs to

    def build(self,data) :
        return []
    def height(self) :
        return 0


bpy.utils.register_class(BC_nones)
bpy.utils.register_class(BC_objects)

##\brief the builder bpy pointer. builders are hooked here
# this will be populated with builder collections
class BC_builders(bpy.types.PropertyGroup):
    nones = bpy.props.CollectionProperty(type=BC_nones)
    objects = bpy.props.CollectionProperty(type=BC_objects)
    #  for reference :
    # BC_builders = type("BC_builders", (bpy.types.PropertyGroup, ), {})