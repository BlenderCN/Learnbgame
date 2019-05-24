bl_info = {
    "name": "vtools Rename objects Tool",
    "author": "Antonio Mendoza",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D > Panel Tools > Object Utils Tab",
    "warning": "",
    "description": "Batch renaming objects keeping selection order",
    "category": "Learnbgame",
}


import bpy
import math 
import threading
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, FloatProperty, EnumProperty

    
def setName(p_objects, p_newName, p_startIn=0, p_numDigits=3, p_numbered=False):
    id = p_startIn
    cont = 1
    numberDigits = p_numDigits
    replacingName = p_newName
    
    if p_numbered == True:
         replacingName += ".000"    
 
    for obj in p_objects:
        
        if p_startIn == 0 or p_numbered == False:
            obj.name = replacingName
        else:
            addZero = 0    
            for i in range(1,numberDigits):
                mod = int(id / (pow(10,i)))
                if mod == 0:
                    addZero += 1
 
            newNameId = str(id)
            for i in range(0,addZero):
                newNameId = '0' + newNameId
               
            oldName = obj.name
            obj.name = ''
            newName = p_newName + '.' + newNameId
            obj.name = newName
            id += 1
            
 
def replace(p_objects, p_findString, p_replaceString=''):
    exist = 0
    if p_findString != '':
        for obj in p_objects:
            obj.name = obj.name.replace(p_findString, p_replaceString)
            
def hasId (p_name):
    
    
    idFound = False
    i = len(p_name) - 1
    str = p_name[i]
    str_res = ""
    
    while p_name[i].isnumeric() and i >= 0:
        str_res = p_name[i] + str_res
        i = i - 1
        
    #print("string ", str_res)  
    
    if i < 0 or not str_res.isnumeric():
        idFound = False
        i = - 1
        
    return i

def addPrefixSubfix(p_objects,p_prefix='',p_subfix='',p_keepId=True):
    
    for obj in p_objects:
        obj.name = p_prefix + obj.name
        if p_keepId == True:
            id = hasId(obj.name)
            if id >= 0:
                obj.name = obj.name[:id] + p_subfix + obj.name[id:]
            else:
                obj.name = obj.name + p_subfix
        else:
            obj.name = obj.name + p_subfix   

"""    
    
#setName(bpy.context.selected_objects, "esfera")
replace(bpy.context.selected_objects, "hola_",'')
replace(bpy.context.selected_objects, "_adios",'')
#addPrefixSubfix(bpy.context.selected_objects, "hola_", "_adios", False)

"""

class RNO_OP_setName(bpy.types.Operator):
    bl_idname = "object.rno_setname"
    bl_label = "Set new name"

    selection_list = []
    
       
    def execute(self,context):
        newName = context.scene.rno_str_new_name
        numbered = context.scene.rno_bool_numbered
        startIn = 1
        numDigits = 3
        
        if context.scene.rno_str_numFrom != '':
            startIn = int(context.scene.rno_str_numFrom)
            numDigits = len(context.scene.rno_str_numFrom)
            
        if context.scene.rno_bool_keepOrder == True:
            setName(self.selection_list,newName, p_startIn=startIn,p_numDigits=numDigits, p_numbered=numbered)
        else:
            setName(bpy.context.selected_objects, newName, p_startIn=startIn,p_numDigits=numDigits, p_numbered=numbered)
        
        return{'FINISHED'}

class RNO_OP_replaceInName(bpy.types.Operator):
    bl_idname = "object.rno_replace_in_name"
    bl_label = "replace"
        

    def execute(self,context):
        oldName = context.scene.rno_str_old_string
        newName = context.scene.rno_str_new_string
        
        replace(bpy.context.selected_objects,oldName, newName)
        
        return{'FINISHED'}
      
      
class RNO_OP_addSubfixPrefix(bpy.types.Operator):
    bl_idname = "object.rno_add_subfix_prefix"
    bl_label = "Add subfix / Prefix"
        

    def execute(self,context):
        prefix = context.scene.rno_str_prefix
        subfix = context.scene.rno_str_subfix
        keepIndex = context.scene.rno_bool_keepIndex 
        
        
        addPrefixSubfix(bpy.context.selected_objects,p_prefix=prefix,p_subfix=subfix,p_keepId=keepIndex)
        
        return{'FINISHED'}
      

class RNO_PN_EndSelectionOrder(bpy.types.Operator):
    bl_idname = "object.rno_end_selection_order"
    bl_label = "leave selection order"
    
    def execute(self,context):
        context.scene.rno_bool_keepOrder = False
        return {'FINISHED'}

class RNO_PN_KeepSelectionOrder(bpy.types.Operator):
    bl_idname = "object.rno_keep_selection_order"
    bl_label = "respect selection order Start / Finish"
    
    num_selected = 0
    selection_list = []    
  
    def getSelectionList(self):
        return self.selection_list
    
    def findObject(self, p_object, p_list):
        
        found = False
        for obj in p_list:
            if obj.name == p_object.name:
                found = True
                break            
        return found
    
    def removeUnselecteds(self, p_oldList, p_newList):
        
        for obj in p_oldList:
            found = self.findObject(obj, p_newList)
            if found == False:
                p_oldList.remove(obj)
                
        return p_oldList
              
            
    def sortList(self):
        #print("sorting")
        
        objects = bpy.context.selected_objects
        num_sel = len(objects)
        num_sortElements = len(self.selection_list)
        
        if num_sel < num_sortElements:
            self.removeUnselecteds(self.selection_list,objects)
            
        else:
            for obj in objects:
                found = self.findObject(obj,self.selection_list)
                
                if found == False:
                    #print("not found, add")
                    self.selection_list.append(obj)
        
        return True
        
    def execute(self,context):
        
        if context.scene.rno_bool_keepOrder == False:
            bpy.ops.object.select_all(action='DESELECT')
            context.scene.rno_bool_keepOrder = True
            self.active = False
            
            #print("------------------ INICIO -----------------------")
            
        else:
            context.scene.rno_bool_keepOrder = False
            #print("------------------ FIN -----------------------")
            

        context.window_manager.modal_handler_add(self)            
        return {'RUNNING_MODAL'}
    
    
         
    def modal(self, context, event):
       
        active = context.scene.rno_bool_keepOrder 
        if active == True:
            self.sortList()
            return {'PASS_THROUGH'}
        else:
            return {'FINISHED'} 
              
        return {'PASS_THROUGH'}
 
    
class RNO_PN_RenamePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Rename Objects"
    bl_context = "objectmode"
    bl_category = 'Relations'
    bl_options = {'DEFAULT_CLOSED'}       
    
       
    def draw(self,context):
        
        layout = self.layout
        split = layout.split()
        col = split.column()
        col.alignment = 'EXPAND'
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        
        # ----------- RESPECT ORDER ------------------ #
        row.separator()
        row = col.row()
        row.prop(context.scene,'rno_bool_keepOrder',text='respect selection order active')
        row.enabled = False
        row = col.row()
        op_SelectionOrder = row.operator(RNO_PN_KeepSelectionOrder.bl_idname,RNO_PN_KeepSelectionOrder.bl_label)
        row = col.row()
        row.separator()
        
        # ----------- NEW NAME ------------------ #
        
        row = col.row()
        box = row.box()
        rbox = box.row(align=True)
        rbox.prop(context.scene,"rno_str_new_name")
        rbox = box.row() 
        rbox.prop(context.scene,"rno_bool_numbered")
        rbox.prop(context.scene,"rno_str_numFrom")
        rbox = box.row()
        op_SetName = rbox.operator(RNO_OP_setName.bl_idname, RNO_OP_setName.bl_label)
        RNO_OP_setName.selection_list = RNO_PN_KeepSelectionOrder.selection_list
        
        # ----------- REPLACE NAME ------------------ #
        
        row=col.row()
        row.separator()
        
        row = col.row()
        box = row.box()
        rbox = box.row()
        box.prop(context.scene, "rno_str_old_string")
        box.prop(context.scene, "rno_str_new_string")
        box.operator(RNO_OP_replaceInName.bl_idname, RNO_OP_replaceInName.bl_label)

        # ----------- ADD SUBFIX / PREFIX NAME ------------------ #
        
        row=col.row()
        row.separator()
        
        row = col.row()
        box = row.box()
        rbox = box.row()
        
        box.prop(context.scene,'rno_bool_keepIndex',text='keep object Index')
        rbox.prop(context.scene, "rno_str_prefix")
        rbox.prop(context.scene, "rno_str_subfix")
        
        
        box.operator(RNO_OP_addSubfixPrefix.bl_idname, RNO_OP_addSubfixPrefix.bl_label)
        
        
def menu_func(self, context):
    self.layout.separator()
    self.layout.menu('VIEW3D_MT_objectsRenaming')
    
def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.rno_list_selection_ordered = bpy.props.EnumProperty(name="selection orderer", items=[])
    
    bpy.types.Scene.rno_str_new_name = bpy.props.StringProperty(name="New name", default='')
    bpy.types.Scene.rno_str_old_string = bpy.props.StringProperty(name="Old string", default='')
    bpy.types.Scene.rno_str_new_string = bpy.props.StringProperty(name="New string", default='')
    bpy.types.Scene.rno_str_numFrom = bpy.props.StringProperty(name="from", default='')
    bpy.types.Scene.rno_str_prefix = bpy.props.StringProperty(name="Prefix", default='')
    bpy.types.Scene.rno_str_subfix = bpy.props.StringProperty(name="Subfix", default='')
    
 
    bpy.types.Scene.rno_bool_numbered = bpy.props.BoolProperty(name='numbered', default=True)
    bpy.types.Scene.rno_bool_keepOrder = bpy.props.BoolProperty(name='keep selection order')
    bpy.types.Scene.rno_bool_keepIndex = bpy.props.BoolProperty(name='keep object Index', default=True)


        
    bpy.types.VIEW3D_MT_object_specials.append(menu_func)
          
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_object_specials.remove(menu_func)
    
    del bpy.types.Scene.rno_str_new_name
    del bpy.types.Scene.rno_str_old_string
    del bpy.types.Scene.rno_str_new_string
    del bpy.types.Scene.rno_bool_keepOrder
    del bpy.types.Scene.rno_bool_numbered
    del bpy.types.Scene.rno_list_selection_ordered
    del bpy.types.Scene.rno_str_prefix
    del bpy.types.Scene.rno_str_subfix
    del bpy.types.Scene.rno_bool_keepIndex 
    
if __name__ == "__main__":
    register()
    