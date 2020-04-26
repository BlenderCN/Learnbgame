import bpy
import uuid
from bpy.types import Menu, Panel, UIList,UILayout,Operator

def findLod(obj,lodLevel,set=None,replace=True):
    lod=None
    collection=None
    if obj.data!=None and "_f3b_Lod" in obj.data:
        lodGroup=obj.data["_f3b_Lod"]
        lodName="LOD"+str(lodLevel)+"_"
        if lodGroup in bpy.context.scene.collection.children:
            collection=bpy.context.scene.collection.children[lodGroup]
        for llod in collection.objects:
            if llod.name.startswith(lodName):
                lod=llod

                break
        
        if set:
            if not lod:
                lod= bpy.data.objects.new(lodName+str(uuid.uuid1()),set)
                collection.objects.link(lod)
            elif replace:
                lod.data=set
            lod.data["_f3b_Lod"]=lodGroup            
    return [lod,collection]

def removeLod(lodData):
    if not lodData[0]: return
    lodData[1].objects.unlink(lodData[0])
    bpy.data.objects.remove(lodData[0], do_unlink=True)   
            

def selectLod(obj,lodLevel):
    found=False
    lodZero=None
    if lodLevel != 0:
        lodZero=findLod(obj,0,set=obj.data,replace=False)[0]
        

    lod=findLod(obj,lodLevel)[0]
    if lod !=None:
        obj.data=lod.data
        if lodLevel!=0:
            obj.data.materials.clear()

            for i in range(0,len(lodZero.data.materials)):
                obj.data.materials.append(lodZero.data.materials[i])
        found=True

    if lodLevel==0:
        lodData=findLod(obj,0)
        linked=False
        for obj in bpy.context.scene.objects:
            if obj.data != None and  lodData[0]!=None and obj.data==lodData[0].data:
                linked=True
                break
        if not linked: removeLod(lodData)
        found=True
    
    return found
    

def initLods(obj):
    lodGroupName=""
    if not "_f3b_Lod" in obj.data:
        lodGroupName="LOD_"+str(uuid.uuid1())
        obj.data["_f3b_Lod"]=lodGroupName
    else:
        lodGroupName=obj.data["_f3b_Lod"]
    if not lodGroupName in bpy.context.scene.collection.children:
        col=bpy.data.collections.new(lodGroupName)  
        bpy.context.scene.collection.children.link(col)
        bpy.context.window.view_layer.layer_collection.children[col.name].exclude=True  
    selectLod(obj,0)
    
def setAsLodLevel(obj,lodLevel,lodObj):
    if lodObj == None:
        lodData=findLod(obj,lodLevel)
        removeLod(lodData)
        selectLod(obj,0)
    else:
        lod=findLod(obj,lodLevel,set=lodObj.data)[0]
        bpy.data.objects.remove(lodObj, do_unlink=True)   


class F3B_TOOLS_lod_show(Operator):
    bl_idname = "f3btools.lod_show"
    bl_label = "Show lod level"
    filename_ext = ""

    lodLevel=bpy.props.IntProperty()
    target=None

    def execute(self, context):
        tg=self.target if self.target!=None else bpy.context.active_object
        initLods(tg)
        selectLod(tg,self.lodLevel)
        return {"FINISHED"}
        
class F3B_TOOLS_lod_remove(Operator):
    bl_idname = "f3btools.lod_remove"
    bl_label = "Remove lod"
    filename_ext = ""

    lodLevel=bpy.props.IntProperty()
    target=None

    def execute(self, context):
        tg=self.target if self.target!=None else bpy.context.active_object
        setAsLodLevel(tg,self.lodLevel,None)
        return {"FINISHED"}
        
class F3B_TOOLS_lod_assign(Operator):
    bl_idname = "f3btools.lod_assign"
    bl_label = "Assign lod level"
    filename_ext = ""

    lodLevel=bpy.props.IntProperty()
    target=None
    selected=None

    def execute(self, context):
        tg=self.target if self.target!=None else bpy.context.active_object
        sl=self.selected
        if not sl:
            for o in bpy.context.scene.objects:
                if o.select_get() and o != tg:
                    sl=o
                    break
        if sl:
            initLods(tg)
            setAsLodLevel(tg,self.lodLevel,sl)
        return {"FINISHED"}
        
           
class F3B_TOOLS_PT_lod_data_panel(Panel):
    bl_label = "Lod"
    bl_idname = "F3B_TOOLS_PT_lod_data_panel"
    bl_context = "data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id="F3B_TOOLS_PT_data_panel"
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw(self, context):
        # Lod [0]  SHOW
        self.layout.use_property_split = True

        hasPrevious=False
        for i in range(0,4):
            col = self.layout.column()
            row = col.row()
            split = row.split(factor=0.3)


            hasNext=False
            hasCurrent=False
            m="unset"
            if i==0:
                m="Mesh"
                hasCurrent=True
            else:
                lod=findLod(bpy.context.active_object,i)[0]
                if i < 3:
                    hasNext=findLod(bpy.context.active_object,i+1)[0] != None
                if lod:
                    m=lod.data.name
                    hasCurrent=True

            split.column().label(text="Lod["+str(i)+"] ("+m+")")
            split=split.split(factor=0.3)

            c=split.column()
            showbtn=c.operator("f3btools.lod_show",text="Show")
            showbtn.lodLevel=i
            c.enabled=hasCurrent

            split=split.split(factor=0.5)
           
            c=split.column()
            assignbtn=c.operator("f3btools.lod_assign",text="Assign Selected")
            assignbtn.lodLevel=i
            c.enabled=hasPrevious

            split=split.split()
            
            c=split.column()           
            rembtn=c.operator("f3btools.lod_remove",text="Remove")
            rembtn.lodLevel=i
            c.enabled=not hasNext and hasCurrent and hasPrevious

            hasPrevious=hasCurrent

def register():
    bpy.utils.register_class(F3B_TOOLS_PT_lod_data_panel)
    bpy.utils.register_class(F3B_TOOLS_lod_show)
    bpy.utils.register_class(F3B_TOOLS_lod_assign)
    bpy.utils.register_class(F3B_TOOLS_lod_remove)

def unregister():
    bpy.utils.unregister_class(F3B_TOOLS_PT_lod_data_panel)
    bpy.utils.unregister_class(F3B_TOOLS_lod_show)
    bpy.utils.unregister_class(F3B_TOOLS_lod_assign)
    bpy.utils.unregister_class(F3B_TOOLS_lod_remove)
    