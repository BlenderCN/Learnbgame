bl_info = {
    "name": "vtools Snapshot Mesh",
    "author": "Antonio Mendoza",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "Properties > object data",
    "warning": "",
    "description": "save a mesh data status in order to be reused if needed",
    "wiki_url": "http://blenderaddonlist.blogspot.com/2015/03/addon-non-destructive-modelling.html",
    "category": "Mesh",
}


import bpy


def findSnapshotMeshListChild(p_obj):
    
    ssMeshList = None 
    
    for o in p_obj.children:
        finder = findSnapShotData(o,"snapshotMeshList")
        if finder >= 0:
            ssMeshList = o
            break
        
    return ssMeshList
    
def findSnapShotData(p_obj,p_string):
    
    isSnapShot = -1
    upp_name = p_obj.name.upper()
    upp_string = p_string.upper()
    isSnapShot= upp_name.find(upp_string)
       
    return isSnapShot

def createSnapshotMesh(p_obj):
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    obj = p_obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.context.scene.objects.active = obj
    
    snapShotName = obj.name + "_snapshotMesh.000"
    snapShotMesh = bpy.data.meshes.new("snapshotMeshData")
    snapShot = bpy.data.objects.new(snapShotName, snapShotMesh)
    snapShot.data = obj.data.copy()
    bpy.context.scene.objects.link(snapShot)
    
    #If snapshot list is empty
    ssMeshList = findSnapshotMeshListChild(obj)
           
    if ssMeshList == None:
        bpy.ops.object.empty_add(type='ARROWS', location =(0,0,0))
        emptySnapShotList = bpy.context.scene.objects.active
        emptySnapShotList.name = "snapshotMeshList.000"
        
        emptySnapShotList.location = obj.location

        
        emptySnapShotList.parent = obj
        snapShot.parent = emptySnapShotList
        
        ssMeshList = emptySnapShotList
        
          
    else:
        snapShot.parent = ssMeshList
        

    
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    
    bpy.ops.object.select_all(action='DESELECT')
    
    ssMeshList.select = False
    ssMeshList.hide = True
    ssMeshList.hide_select = True
    ssMeshList.hide_render = True
        
    snapShot.select = False
    snapShot.hide = True
    snapShot.hide_select = True
    snapShot.hide_render = True
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.context.scene.objects.active = obj
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    
    return snapShot

def deleteSnapshotMesh(p_obj, p_snapshotMeshName):
   
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    
    snapShot = bpy.data.objects[p_snapshotMeshName]
    
    print(p_obj)
    print(snapShot) 
    
    snapShot.hide = False
    snapShot.hide_select = False
    
    bpy.ops.object.select_all(action='DESELECT')
    snapShot.select = True
    bpy.context.scene.objects.active = snapShot
    
    bpy.ops.object.delete()
    
    bpy.ops.object.select_all(action='DESELECT')
    p_obj.select = True
    bpy.context.scene.objects.active = p_obj
        
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    
    return p_obj

def deleteAllSnapshotMesh(p_obj):
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    
    ssMeshList = findSnapshotMeshListChild(p_obj)
    
    if ssMeshList != None:    
        for c in ssMeshList.children:
            finder = findSnapShotData(c,"_snapshotMesh")
            
            if finder >= 0:
                c.hide = False
                c.hide_select = False
                bpy.ops.object.select_all(action='DESELECT')
                c.select = True
                bpy.context.scene.objects.active = c
                bpy.ops.object.delete()
        
        ssMeshList.hide = False
        ssMeshList.hide_select = False    
        bpy.ops.object.select_all(action='DESELECT')
        ssMeshList.select = True
        bpy.context.scene.objects.active = ssMeshList
        bpy.ops.object.delete()
                        
    bpy.ops.object.select_all(action='DESELECT')
    p_obj.select = True
    bpy.context.scene.objects.active = p_obj
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
            
    return {'FINISHED'}

def useSnapShot(p_obj, p_snapShot):
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    bpy.ops.object.select_linked(type='OBDATA')
    p_obj.data = p_snapShot.data.copy()
    p_obj.select = False

    for o in bpy.context.selected_objects:
        if o.type == 'MESH':
            o.data = p_obj.data
    
    bpy.ops.object.select_all(action='DESELECT')
    p_obj.select = True 
    bpy.context.scene.objects.active = p_obj
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    
def collectSnapShotMeshes(p_obj):
    
    ssMeshes = []
    
    ssMeshList = findSnapshotMeshListChild(p_obj)
    
    if ssMeshList != None:    
        for c in ssMeshList.children:
            finder = findSnapShotData(c,"_snapshotMesh")
            if finder >= 0:
                ssMeshes.append(c)
    
    return ssMeshes
          

def collectListNames(p_UIList, p_IdList):
    
    listSnapShots = []
    cont = 0
    for o in p_UIList:
        if cont != p_IdList:
            listSnapShots.append(o)
        cont += 1
    
    return listSnapShots



def deleteUnusedSnapShotMeshes():
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    
    baseObj = bpy.context.scene.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    
    for o in bpy.data.objects:
        if o.parent == None: 
            finder = findSnapShotData(o,"snapshotMesh") 
            if finder >= 0:
                for c in o.children:
                    c.hide = False
                    c.hide_select = False
                    bpy.ops.object.select_all(action='DESELECT')
                    c.select = True
                    bpy.context.scene.objects.active = c
                    bpy.ops.object.delete()
                
                o.hide = False
                o.hide_select = False
                bpy.ops.object.select_all(action='DESELECT')
                o.select = True
                bpy.context.scene.objects.active = o
                bpy.ops.object.delete()
    
    bpy.ops.object.select_all(action='DESELECT')
    baseObj.select = True
    bpy.context.scene.objects.active = baseObj
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
    

def updateSnapshotMeshList(p_list, p_UIList, p_IdList, p_snapShot=None):
    

    
    cont = len(p_list)
    snapShots = collectListNames(p_UIList, p_IdList)

    longSnapShots =  len(p_UIList)
    longSnapShotsMesh = len(p_list)
   
    
    if longSnapShotsMesh > longSnapShots:
        #if is added a new one add to the UI List
        sMesh = p_UIList.add()
        sMesh.name = "snapshot_" + str(longSnapShotsMesh)
        sMesh.snapShotMeshName = p_snapShot.name
    else:
        #if delete the snapshot from de UI List
        p_UIList.remove(p_IdList)
   
    return {'FINISHED'}

def recalculateFromChildren(p_obj,p_UIList):
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
        
    ssMeshList = findSnapshotMeshListChild(p_obj)
    cont = 1
    p_UIList.clear()
    
    if ssMeshList != None:
        for c in ssMeshList.children:
            sMesh = p_UIList.add()
            sMesh.name = "snapshot_" + str(cont)
            sMesh.snapShotMeshName = c.name
            cont += 1
    
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle=True)
        
    return {'FINISHED'}                
    
class VTOOLS_OP_captureSnapShot(bpy.types.Operator):
    bl_idname = "vtools.capturesnapshot"
    bl_label = "Capture snapShot Mesh"
    bl_description = "captures and saves the current mesh data"
    
    def execute(self,context):
        snapShot = createSnapshotMesh(bpy.context.active_object)
        ssmList = collectSnapShotMeshes(bpy.context.active_object)

        updateSnapshotMeshList(ssmList, context.object.snapShotMeshes,bpy.context.object.snapShotMesh_ID_index, snapShot)
        
        bpy.context.object.snapShotMesh_ID_index = len(context.object.snapShotMeshes.items())-1
        
        return {'FINISHED'}
    

class VTOOLS_OP_deleteSnapShot(bpy.types.Operator):
    bl_idname = "vtools.deletesnapshot"
    bl_label = "Delete snapShot Mesh"
    bl_description = "Delete the selected mesh data"
    
    def execute(self,context):
        listId = bpy.context.object.snapShotMesh_ID_index
        if listId > -1:
            ssMeshObjectName = context.object.snapShotMeshes[listId].snapShotMeshName
            deleteSnapshotMesh(bpy.context.active_object, ssMeshObjectName)

            ssmList = collectSnapShotMeshes(bpy.context.active_object)
            updateSnapshotMeshList(ssmList, context.object.snapShotMeshes, bpy.context.object.snapShotMesh_ID_index)
            
            
            if listId > 0: 
                bpy.context.object.snapShotMesh_ID_index = listId - 1
            else:
                bpy.context.object.snapShotMesh_ID_index = 0
        
        return {'FINISHED'}
    
class VTOOLS_OP_deleteAllSnapShot(bpy.types.Operator):
    bl_idname = "vtools.deleteallsnapshot"
    bl_label = "Delete all snapShot Mesh"
    bl_description = "Delete all snapshot meshes "
    
    def execute(self,context):
        deleteAllSnapshotMesh(bpy.context.active_object)
        context.object.snapShotMeshes.clear()

        bpy.context.object.snapShotMesh_ID_index = -1
        
        return {'FINISHED'}
    
class VTOOLS_OP_useSnapShot(bpy.types.Operator):
    bl_idname = "vtools.usesnapshot"
    bl_label = "Use selected snapShot Mesh"
    bl_description = "Use the selected mesh data"
    
    def execute(self,context):
        
        listId = bpy.context.object.snapShotMesh_ID_index
        if listId > -1:
            ssMeshName = context.object.snapShotMeshes[listId].snapShotMeshName
            snapShotMesh = bpy.data.objects[ssMeshName]
            
           
            useSnapShot(bpy.context.active_object, snapShotMesh) 
        
        return {'FINISHED'}
    
class VTOOLS_OP_deleteUnusedSnapShotList(bpy.types.Operator):
    bl_idname = "vtools.deleteunusedsnapshotlist"
    bl_label = "Delete unused snapShot Mesh List"
    bl_description = "Deletes unused snapShot Mesh List"
    
    def execute(self,context):
        deleteUnusedSnapShotMeshes()
        return {'FINISHED'}

class VTOOLS_OP_recalculateFromChildren(bpy.types.Operator):
    bl_idname = "vtools.recalculatesnapshotfromchildren"
    bl_label = "Recalculate snapShot Meshes from object"
    bl_description = "recalculate snapshot meshes. Needed in somecase (ie:duplicated objects). You will loose the snapshot names"
    
    def execute(self,context):
        recalculateFromChildren(bpy.context.scene.objects.active ,context.object.snapShotMeshes) 
        bpy.context.object.snapShotMesh_ID_index = -1
        
        return {'FINISHED'}
               
class VTOOLS_CC_snapShotMeshCollection(bpy.types.PropertyGroup):
       
    name = bpy.props.StringProperty(default='')
    snapShotMeshName = bpy.props.StringProperty(default="")
    snapShotMesh_ID = bpy.props.StringProperty(default="bake",options={"HIDDEN"})
    
   
    
class VTOOLS_PN_snapShotMeshes(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Snapshot Meshes"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH'})
    
    
    def draw(self,context):
        
        layout = self.layout
        obj = context.object
       
        # Create using template_list UI
        
        box = layout.box()
        col = box.row()
        row = col.row()
        row.template_list('UI_UL_list', "snapShotMesh_ID", obj, "snapShotMeshes", obj, "snapShotMesh_ID_index", rows=2)
        
        # Add and delete buttons 
        
        col = row.column(align=True)
        subrow = col.row(align=True)
        subrow.operator(VTOOLS_OP_captureSnapShot.bl_idname, icon='ZOOMIN', text="")
        subrow.operator(VTOOLS_OP_deleteSnapShot.bl_idname, icon='ZOOMOUT', text="")
        
        subrow = col.row(align=True)
        subrow.operator(VTOOLS_OP_useSnapShot.bl_idname, icon='OUTLINER_OB_MESH', text="")    
        subrow.operator(VTOOLS_OP_recalculateFromChildren.bl_idname, icon='BORDERMOVE', text="")  
        
        col = col.column()
        col.separator()
        subrow = col.row(align=True)
        subrow.operator(VTOOLS_OP_deleteAllSnapShot.bl_idname, icon='X', text="") 
        subrow.operator(VTOOLS_OP_deleteUnusedSnapShotList.bl_idname, icon='CANCEL', text="") 

        
            
def register():
   

    bpy.utils.register_class(VTOOLS_OP_captureSnapShot)
    bpy.utils.register_class(VTOOLS_OP_deleteSnapShot)
    bpy.utils.register_class(VTOOLS_OP_deleteAllSnapShot) 
    bpy.utils.register_class(VTOOLS_PN_snapShotMeshes)
    bpy.utils.register_class(VTOOLS_OP_useSnapShot)
    bpy.utils.register_class(VTOOLS_OP_deleteUnusedSnapShotList)
    bpy.utils.register_class(VTOOLS_OP_recalculateFromChildren)
    
    
    bpy.utils.register_class(VTOOLS_CC_snapShotMeshCollection)
    bpy.types.Object.snapShotMesh_ID_index = bpy.props.IntProperty()
    bpy.types.Object.snapShotMeshes = bpy.props.CollectionProperty(type=VTOOLS_CC_snapShotMeshCollection)
    
                   
def unregister():
    
    del bpy.types.Object.snapShotMeshes
    del bpy.types.Object.snapShotMesh_ID_index
    
    bpy.utils.unregister_class(VTOOLS_OP_captureSnapShot)
    bpy.utils.unregister_class(VTOOLS_OP_deleteSnapShot)
    bpy.utils.unregister_class(VTOOLS_OP_deleteAllSnapShot) 
    bpy.utils.unregister_class(VTOOLS_PN_snapShotMeshes)
    bpy.utils.unregister_class(VTOOLS_OP_useSnapShot)
    bpy.utils.unregister_class(VTOOLS_OP_deleteUnusedSnapShotList)
    bpy.utils.unregister_class(VTOOLS_OP_recalculateFromChildren)
    
    
if __name__ == "__main__":
    register()

