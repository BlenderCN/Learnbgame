bl_info = {
    "name": "BoolTool",
    "author": "Vitor Balbio",
    "version": (0, 2),
    "blender": (2, 70, 0),
    "location": "View3D > Object > BoolTool",
    "description": "Improve de Boolean Usability",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Object/BoolTool",
    "category": "Learnbgame",
}

import bpy
import time
from bpy.app.handlers import persistent
from bpy.types import Operator, AddonPreferences


#------------------- FUNCTIONS------------------------------
#Utils:

# Object is a Root Tool Bool
def isCanvas(_obj):
    try:
        if _obj["BoolToolRoot"]:
            return True
    except:
        return False

# Object is a Brush Tool Bool
def isBrush(_obj):
    try:
        if _obj["BoolToolBrush"]:
            return True
    except:
        return False
    
# Object is a Poly Brush Tool Bool
def isPolyBrush(_obj):
    try:
        if _obj["BoolToolPolyBrush"]:
            return True
    except:
        return False
    
def BT_ObjectByName(obj):
    for ob in bpy.context.scene.objects:
        if isCanvas(ob) or isBrush(ob):            
            if ob.name == obj:
                return ob

def FindCanvas(obj):
    for ob in bpy.context.scene.objects:
        if isCanvas(ob):
            for mod in ob.modifiers:
                if("BTool_" in mod.name):
                    if ( obj.name in mod.name ):
                        return ob
                    
def isFTransf():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[bl_info["name"]].preferences
    if addon_prefs.fast_transform:
        return True
    else:
        return False

"""
# EXPERIMENTAL FEATURES
def isMakeVertexGroup():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[bl_info["name"]].preferences
    if addon_prefs.make_vertex_groups:
        return True
    else:
        return False
    
def isMakeBoundary():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[bl_info["name"]].preferences
    if addon_prefs.make_boundary:
        return True
    else:
        return False
"""

def ConvertToMesh(obj):
    act = bpy.context.scene.objects.active
    bpy.context.scene.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    bpy.context.scene.objects.active = act
    

    
# Do the Union, Difference and Intersection Operations with a Brush
def Operation(context,_operation):
    for selObj in bpy.context.selected_objects:
        if selObj != context.active_object and (selObj.type == "MESH" or selObj.type == "CURVE"):
            if selObj.type == "CURVE":
                ConvertToMesh(selObj)  
            actObj = context.active_object
            selObj.hide_render = True
            cyclesVis = selObj.cycles_visibility
            #for obj in bpy.context.scene.objects:
             #   if isCanvas(obj):
              #      for mod in obj.modifiers:
               #         if(mod.name == "BTool_" + selObj.name):
                #            obj.modifiers.remove(mod)

            selObj.draw_type = "WIRE"
            cyclesVis.camera = False; cyclesVis.diffuse = False; cyclesVis.glossy = False; cyclesVis.shadow = False; cyclesVis.transmission = False;
            newMod = actObj.modifiers.new("BTool_"+ selObj.name,"BOOLEAN")
            newMod.object = selObj
            newMod.operation = _operation
            actObj["BoolToolRoot"] = True
            selObj["BoolToolBrush"] = _operation
            selObj["BoolTool_FTransform"] = "False"

# Do Direct Union, Difference and Intersection Operations
def Operation_Direct(context,_operation):
    actObj = context.active_object
    for selObj in bpy.context.selected_objects:
        if selObj != context.active_object and(selObj.type == "MESH" or selObj.type == "CURVE"):
            if selObj.type == "CURVE":
                ConvertToMesh(selObj)  
            actObj = context.active_object
            
            newMod = actObj.modifiers.new("BTool_"+ selObj.name,"BOOLEAN")
            newMod.operation = _operation
            newMod.object = selObj
            bpy.ops.object.modifier_apply (modifier=newMod.name)
            bpy.ops.object.select_all(action='DESELECT')
            selObj.select = True
            bpy.ops.object.delete()
            
# Remove Obejcts form the BoolTool System    
def Remove(context,thisObj_name,Prop):
    
    # Find the Brush pointed in the Tree View and Restore it, active is the Canvas
    actObj = context.active_object
    
    #Restore the Brush
    def RemoveThis(_thisObj_name):
        for obj in bpy.context.scene.objects:
            #if it's the brush object
            if obj.name == _thisObj_name:
                cyclesVis = obj.cycles_visibility
                obj.draw_type = "TEXTURED"
                del obj["BoolToolBrush"]
                del obj["BoolTool_FTransform"]
                cyclesVis.camera = True; cyclesVis.diffuse = True; cyclesVis.glossy = True; cyclesVis.shadow = True; cyclesVis.transmission = True;
        
                #Remove it from the Canvas
                for mod in actObj.modifiers:
                    if("BTool_"in mod.name):
                        if(_thisObj_name in mod.name):
                            actObj.modifiers.remove(mod)
 
    if Prop == "THIS":
        RemoveThis(thisObj_name)
    
    #If the remove was called from the Properties:
    else:
        # Remove the Brush Property
        if Prop == "BRUSH":
            Canvas = FindCanvas(actObj)
            for mod in Canvas.modifiers:
                if("BTool_"in mod.name):
                    if(actObj.name in mod.name):
                        Canvas.modifiers.remove(mod)
                        cyclesVis = actObj.cycles_visibility
                        actObj.draw_type = "TEXTURED"
                        del actObj["BoolToolBrush"]
                        del actObj["BoolTool_FTransform"]
                        cyclesVis.camera = True; cyclesVis.diffuse = True; cyclesVis.glossy = True; cyclesVis.shadow = True; cyclesVis.transmission = True;
        
        if Prop == "CANVAS":
            for mod in actObj.modifiers:
                if("BTool_"in mod.name):
                    RemoveThis(mod.object.name)
        

# Tooble the Enable the Brush Object Propertie
def EnableBrush(context, objList, canvas):
    
    for obj in objList :
        for mod in canvas.modifiers:
            if("BTool_"in mod.name and mod.object.name == obj ):
                
                if(mod.show_viewport):
                    mod.show_viewport=False
                    mod.show_render=False
                else:
                    mod.show_viewport=True
                    mod.show_render=True

#Find the Canvas and Enable this Brush
def EnableThisBrush(context,set):
    canvas = None
    for obj in bpy.context.scene.objects:
        if obj != bpy.context.active_object:
            if isCanvas(obj):
                for mod in obj.modifiers:
                    if("BTool_"in mod.name):
                        if mod.object == bpy.context.active_object:
                            canvas = obj
                                
    for mod in canvas.modifiers:
        if("BTool_"in mod.name):
            if mod.object == bpy.context.active_object:
                if set == "None":
                    if(mod.show_viewport):
                        mod.show_viewport=False
                        mod.show_render=False
                    else:
                        mod.show_viewport=True
                        mod.show_render=True
                else:       
                    if (set == "True"):
                        mod.show_viewport = True
                    else:
                        mod.show_viewport = False
                return

# Tooble the Fast Transform Propertie of the Active Brush      
def EnableFTransf(context):
    actObj = bpy.context.active_object
    
    if actObj["BoolTool_FTransform"] == "True":
        actObj["BoolTool_FTransform"] = "False"
    else:
        actObj["BoolTool_FTransform"] = "True"
    return 
                                      
        
# Apply All Brushes to the Canvas
def ApplyAll(context, list):
    deleteList = []
    for selObj in list:
        if isCanvas(selObj) and selObj == context.active_object:
            for mod in selObj.modifiers:
                if("BTool_"in mod.name):
                    deleteList.append(mod.object)
                bpy.ops.object.modifier_apply (modifier=mod.name)
            
            bpy.ops.object.select_all(action='TOGGLE')  
            bpy.ops.object.select_all(action='DESELECT')
            for obj in deleteList:
                obj.select = True
            bpy.ops.object.delete()

# Apply This Brush to the Canvas   
def ApplyThisBrush(context, brush):
    for canvas in context.scene.objects:
        if isCanvas(canvas):
            for mod in canvas.modifiers:
                if("BTool_" + brush.name in mod.name):
                       
                    """
                    # EXPERIMENTAL
                    if isMakeVertexGroup():
                        # Turn all faces of the Brush selected
                        bpy.context.scene.objects.active = brush
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        
                        #Turn off al faces of the Canvas selected
                        bpy.context.scene.objects.active = canvas
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                    """
                    
                    # Apply This Brush
                    bpy.context.scene.objects.active = canvas
                    bpy.ops.object.modifier_apply (modifier=mod.name)
                    bpy.ops.object.select_all(action='TOGGLE')
                    bpy.ops.object.select_all(action='DESELECT')
                    brush.select = True
                    bpy.ops.object.delete()
                    
                    """
                    # EXPERIMENTAL
                    if isMakeVertexGroup():
                        # Make Vertex Group
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.object.vertex_group_assign_new()
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        
                        canvas.vertex_groups.active.name = "BTool_" + brush.name
                    """  

# Garbage Colletor
def GCollector(_obj):
    if isCanvas(_obj):
        BTRoot = False
        for mod in _obj.modifiers:
            if("BTool_" in mod.name):
                BTRoot = True
                if(mod.object == None):
                    _obj.modifiers.remove(mod)
        if not BTRoot:
            del _obj["BoolToolRoot"]
            
# Handle the callbacks when modifing things in the scene
@persistent
def HandleScene(scene):
    if bpy.data.objects.is_updated:
        for ob in bpy.data.objects:
            if ob.is_updated:
                GCollector(ob)

# ------------------ OPERATORS-----------------------------------------------------                
class BTool_DrawPolyBrush(bpy.types.Operator):
    """Draw a Polygonal Mask that can be applyied to a Canvas as a Brush or Directly"""
    bl_idname = "btool.draw_polybrush"
    bl_label = "Draw Poly Brush"
    
               
    count=0
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
      
    
    def modal(self,context,event):
        self.count +=1
        actObj = bpy.context.active_object
        if self.count == 1:
            actObj.select = True
            bpy.ops.gpencil.draw('INVOKE_DEFAULT',mode ="DRAW_POLY")
                 
        if event.type in {'RET', 'NUMPAD_ENTER'}:
            
            bpy.ops.gpencil.convert(type='POLY')
            for obj in context.selected_objects:
                if obj.type == "CURVE":
                    obj.name = "PolyDraw"
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select = True
                    bpy.ops.object.convert(target="MESH")
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.edge_face_add()
                    bpy.ops.mesh.flip_normals()
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
                    bpy.ops.object.modifier_add(type="SOLIDIFY")
                    for mod in obj.modifiers:
                        if mod.name == "Solidify":
                            mod.name = "BTool_PolyBrush"
                            mod.thickness = 1
                            mod.offset = 0
                    obj["BoolToolPolyBrush"] = True             
            
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = actObj
                    bpy.context.scene.update()
                    actObj.select = True
                    obj.select = True
                    #try:
                    actObj.grease_pencil.clear()
                    bpy.ops.gpencil.data_unlink()
                    
            
            return {'FINISHED'}

        if event.type in {'ESC'}:
            bpy.ops.ed.undo() # remove o Grease Pencil
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
        
    def invoke(self, context, event):
        if context.object:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        

                
# Fast Transform
class BTool_FastTransform(bpy.types.Operator):
    """Enable Fast Transform"""
    bl_idname = "btool.fast_transform"
    bl_label = "Fast Transform"
    
    operator = bpy.props.StringProperty("")

    count=0

    def modal(self,context,event):
        self.count +=1
        actObj = bpy.context.active_object
        if self.count ==1:
            
            if isBrush(actObj) and actObj["BoolTool_FTransform"] == "True":
                EnableThisBrush(bpy.context,"False")
                actObj.draw_type = "WIRE"
                
            if self.operator == "Translate":                
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            if self.operator == "Rotate":                
                bpy.ops.transform.rotate('INVOKE_DEFAULT')
            if self.operator == "Scale":                
                bpy.ops.transform.resize('INVOKE_DEFAULT')
            

        if event.type == 'LEFTMOUSE':
            if isBrush(actObj):
                EnableThisBrush(bpy.context,"True")
                actObj.draw_type = "WIRE"
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            if isBrush(actObj):
                EnableThisBrush(bpy.context,"True")
                actObj.draw_type = "WIRE"
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
        
    def invoke(self, context, event):
        if context.object:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

#------------------- OPERATOR CLASSES --------------------------------------------------------

# Brush Operators --------------------------------------------
           
# Boolean Union Operator                
class BTool_Union(bpy.types.Operator):
    """This operator add a union brush to a canvas"""
    bl_idname = "btool.boolean_union"
    bl_label = "Brush Union"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        Operation(context,"UNION")
        return {'FINISHED'}

# Boolean Intersection Operator
class BTool_Inters(bpy.types.Operator):
    """This operator add a intersect brush to a canvas"""
    bl_idname = "btool.boolean_inters"
    bl_label = "Brush Intersection"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Operation(context,"INTERSECT")
        return {'FINISHED'}
        
# Boolean Difference Operator
class BTool_Diff(bpy.types.Operator):
    """This operator add a difference brush to a canvas"""
    bl_idname = "btool.boolean_diff"
    bl_label = "Brush Difference"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Operation(context,"DIFFERENCE")
        return {'FINISHED'}

# Direct Operators ---------------------------------------------------

# Boolean Union Direct Operator                
class BTool_Union_Direct(bpy.types.Operator):
    """Make the union between selected objects to the active"""
    bl_idname = "btool.boolean_union_direct"
    bl_label = "Direct Union"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        Operation_Direct(context,"UNION")
        return {'FINISHED'}

# Boolean Intersection Operator
class BTool_Inters_Direct(bpy.types.Operator):
    """Make the intersection between selected objects to the active"""
    bl_idname = "btool.boolean_inters_direct"
    bl_label = "Direct Intersection"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Operation_Direct(context,"INTERSECT")
        return {'FINISHED'}
        
# Boolean Difference Operator
class BTool_Diff_Direct(bpy.types.Operator):
    """Make the difference between selected objects to the active"""
    bl_idname = "btool.boolean_diff_direct"
    bl_label = "Direct Difference"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Operation_Direct(context,"DIFFERENCE")
        return {'FINISHED'}
    
# Utils Class ---------------------------------------------------------------

# Find the Brush Selected in Three View
class BTool_FindBrush(bpy.types.Operator):
    """Find the this brush"""
    bl_idname = "btool.find_brush"
    bl_label = ""
    obj = bpy.props.StringProperty("")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        for ob in bpy.context.scene.objects:
            if(ob.name == self.obj):
                bpy.ops.object.select_all(action='TOGGLE')  
                bpy.ops.object.select_all(action='DESELECT')  
                bpy.context.scene.objects.active = ob
                ob.select = True
        return {'FINISHED'}

# Mode The Modifier in The Stack Up or Down
class BTool_MoveStack(bpy.types.Operator):
    """Move this Brush Up/Down in the Stack"""
    bl_idname = "btool.move_stack"
    bl_label = ""
    modif = bpy.props.StringProperty("")
    direction = bpy.props.StringProperty("")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        if(self.direction == "UP"):
            bpy.ops.object.modifier_move_up(modifier=self.modif)
        if(self.direction == "DOWN"):
            bpy.ops.object.modifier_move_down(modifier=self.modif)
        return {'FINISHED'}

# Enable or Disable a Brush in th Three View    
class BTool_EnableBrush(bpy.types.Operator):
    """Removes all BoolTool config assigned to it"""
    bl_idname = "btool.enable_brush"
    bl_label = ""
    
    thisObj = bpy.props.StringProperty("")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # in this case is just one object but the function accept more than one at once
        EnableBrush(context,[self.thisObj],context.active_object)
        return {'FINISHED'}

# Enable or Disabel a Brush Directly
class BTool_EnableThisBrush(bpy.types.Operator):
    """ Toggles this brush"""
    bl_idname = "btool.enable_this_brush"
    bl_label = ""
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        EnableThisBrush(context,"None")
        return {'FINISHED'}

# Enable or Disabel a Brush Directly
class BTool_EnableFTransform(bpy.types.Operator):
    """Use Fast Transformations to improve speed"""
    bl_idname = "btool.enable_ftransf"
    bl_label = ""
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        EnableFTransf(context)
        return {'FINISHED'}


# Other Operations -------------------------------------------------------

# Remove a Brush or a Canvas
class BTool_Remove(bpy.types.Operator):
    """Removes all BoolTool config assigned to it"""
    bl_idname = "btool.remove"
    bl_label = ""
    bl_options = {'UNDO'}
    thisObj = bpy.props.StringProperty("")
    Prop = bpy.props.StringProperty("")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Remove(context,self.thisObj,self.Prop)
        return {'FINISHED'}

# Apply All to Canvas
class BTool_AllBrushToMesh(bpy.types.Operator):
    """Apply all brushes of this canvas"""
    bl_idname = "btool.to_mesh"
    bl_label = "Apply All Canvas"
    bl_options = {'UNDO'}   
    

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        list = bpy.context.selected_objects
        ApplyAll(context,list)
        return {'FINISHED'}
    
# Apply This Brush to the Canvas
class BTool_BrushToMesh(bpy.types.Operator):
    """Apply this brush to the canvas"""
    bl_idname = "btool.brush_to_mesh"
    bl_label = "Apply this Brush to Canvas"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if isBrush(context.active_object):
            return True
        else:
            return False

    def execute(self, context):
        ApplyThisBrush(context,bpy.context.active_object)
        return {'FINISHED'}

#TODO
#Apply This Brush To Mesh
        

#------------------- MENU CLASSES ------------------------------  
# 3Dview Header Menu
class BoolTool_Menu(bpy.types.Menu):
    bl_label = "BoolTool Operators"
    bl_idname = "OBJECT_MT_BoolTool_Menu"

    def draw(self, context):
        layout = self.layout

        self.layout.operator(BTool_Union.bl_idname,icon = "ROTATECOLLECTION")
        self.layout.operator(BTool_Diff.bl_idname,icon = "ROTACTIVE")
        self.layout.operator(BTool_Inters.bl_idname, icon = "ROTATECENTER")
        self.layout.separator()
        
        self.layout.operator(BTool_Union_Direct.bl_idname, text = "Union",icon = "ROTATECOLLECTION")
        self.layout.operator(BTool_Inters_Direct.bl_idname, text ="Intersection",icon = "ROTATECENTER")
        self.layout.operator(BTool_Diff_Direct.bl_idname, text ="Difference",icon = "ROTACTIVE")
        
        self.layout.separator()
        
        self.layout.operator(BTool_DrawPolyBrush.bl_idname,icon = "LINE_DATA")
        self.layout.separator()   
        
        if(isCanvas(context.active_object)):
            self.layout.operator(BTool_AllBrushToMesh.bl_idname,icon = "MOD_LATTICE", text = "Apply All")
            Rem = self.layout.operator(BTool_Remove.bl_idname,icon = "CANCEL", text="Remove All")
            Rem.thisObj = ""
            Rem.Prop = "CANVAS"
            self.layout.separator()
        
        if(isBrush(context.active_object)):
            self.layout.operator(BTool_BrushToMesh.bl_idname,icon = "MOD_LATTICE", text = "Apply Brush")
            Rem = self.layout.operator(BTool_Remove.bl_idname,icon = "CANCEL", text = "Remove Brush")
            Rem.thisObj = ""
            Rem.Prop = "BRUSH"

def VIEW3D_BoolTool_Menu(self, context):
    self.layout.menu(BoolTool_Menu.bl_idname)

#---------------- Bool Tools ---------------------
class BoolTool_Tools(bpy.types.Panel):
    bl_label = "Operators"
    bl_idname = "BoolTool_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BoolTool"
    bl_context = "objectmode"
    
    def draw(self,context):

        #self.layout.label("Operators:",icon = "MODIFIER")
        row = self.layout.row(True)
        col = row.column(True)
        col.label(" Brush:",icon = "MODIFIER")
        col.separator() 
        col.operator(BTool_Union.bl_idname, text = "Union",icon = "ROTATECOLLECTION")
        col.operator(BTool_Inters.bl_idname, text ="Intersection",icon = "ROTATECENTER")
        col.operator(BTool_Diff.bl_idname, text ="Difference",icon = "ROTACTIVE")
        
        self.layout.separator() 
        row = self.layout.row(True)
        col = row.column(True)
        col.label("Direct:",icon = "MOD_LATTICE")
        col.separator()
        col.operator(BTool_Union_Direct.bl_idname, text = "Union",icon = "ROTATECOLLECTION")
        col.operator(BTool_Inters_Direct.bl_idname, text ="Intersection",icon = "ROTATECENTER")
        col.operator(BTool_Diff_Direct.bl_idname, text ="Difference",icon = "ROTACTIVE")
        
        self.layout.separator() 
        row = self.layout.row(True)
        col = row.column(True)
        col.label("Draw:",icon = "MESH_CUBE")
        col.separator()
        col.operator(BTool_DrawPolyBrush.bl_idname,icon = "LINE_DATA")
        col.separator()
    

#---------- Properties --------------------------------------------------------
class BoolTool_Config(bpy.types.Panel):
    bl_label = "Properties"
    bl_idname = "BoolTool_BConfig"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BoolTool"
    bl_context = "objectmode"
    
    @classmethod
    def poll(cls, context):
        
        result = False
        actObj = bpy.context.active_object
        if(isCanvas(actObj) or isBrush(actObj) or isPolyBrush(actObj)):
            result = True
        return result
    
    def draw(self,context):
        actObj = bpy.context.active_object
        icon = ""
                
        row = self.layout.row(True)
        
        # CANVAS ---------------------------------------------------
        if isCanvas(actObj):
            row.label("CANVAS", icon = "MESH_GRID")
            self.layout.separator()
            row = self.layout.row(True)
            row.operator(BTool_AllBrushToMesh.bl_idname,icon = "MOD_LATTICE", text="Apply All")
            
            row = self.layout.row(True)
            Rem = row.operator(BTool_Remove.bl_idname,icon = "CANCEL", text="Remove All")
            Rem.thisObj = ""
            Rem.Prop = "CANVAS"
            
            if isBrush(actObj):
                self.layout.separator()
            
        # BRUSH ------------------------------------------------------    
        if isBrush(actObj):
            
            if(actObj["BoolToolBrush"] == "UNION"):
               icon ="ROTATECOLLECTION"
            if(actObj["BoolToolBrush"] == "DIFFERENCE"):
                icon ="ROTACTIVE"
            if(actObj["BoolToolBrush"] == "INTERSECT"):
                icon ="ROTATECENTER"
            
            row = self.layout.row(True)
            row.label("BRUSH" ,icon = icon)
            #self.layout.separator()            
            
            icon = ""
            if actObj["BoolTool_FTransform"] == "True":
                icon ="PMARKER_ACT"
            else:
                icon ="PMARKER"
            if isFTransf():
                pass
            
            if isFTransf():
                row = self.layout.row(True)
                row.operator(BTool_EnableFTransform.bl_idname,text = "Fast Vis", icon = icon)
                Enable = row.operator(BTool_EnableThisBrush.bl_idname, text = "Enable", icon = "VISIBLE_IPO_ON")
                row = self.layout.row(True)
            else:
                Enable = row.operator(BTool_EnableThisBrush.bl_idname, icon = "VISIBLE_IPO_ON")
                row = self.layout.row(True)
            
        if isPolyBrush(actObj):
            row = self.layout.row(False)
            row.label("POLY BRUSH" ,icon = "LINE_DATA")
            mod = actObj.modifiers["BTool_PolyBrush"]
            row = self.layout.row(False)
            row.prop(mod,"thickness",text = "Size")
            self.layout.separator()
        
        if isBrush(actObj):    
            row = self.layout.row(True)
            row.operator(BTool_BrushToMesh.bl_idname,icon = "MOD_LATTICE", text = "Apply Brush")
            row = self.layout.row(True)
            Rem = row.operator(BTool_Remove.bl_idname,icon = "CANCEL", text = "Remove Brush")
            Rem.thisObj = ""
            Rem.Prop = "BRUSH"
            
        self.layout.separator()
                    
#---------- Tree Viewer-------------------------------------------------------
class BoolTool_BViwer(bpy.types.Panel):
    bl_label = "Brush Viewer"
    bl_idname = "BoolTool_BViwer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BoolTool"
    bl_context = "objectmode"
    
    @classmethod
    def poll(cls, context):
        actObj = bpy.context.active_object
        
        if isCanvas(actObj):
            return True
        else:
            return False
    
    def draw(self,context):
    
        actObj = bpy.context.active_object
        icon = ""

        if isCanvas(actObj):
            
            for mod in actObj.modifiers:
                container = self.layout.box()
                row = container.row(True)
                icon = ""
                if("BTool_" in mod.name):
                    if(mod.operation == "UNION"):
                        icon ="ROTATECOLLECTION"
                    if(mod.operation == "DIFFERENCE"):
                        icon ="ROTACTIVE"
                    if(mod.operation == "INTERSECT"):
                        icon ="ROTATECENTER"

                    objSelect = row.operator("btool.find_brush",text=mod.object.name, icon = icon, emboss = False)
                    objSelect.obj = mod.object.name
                    
                    EnableIcon = "RESTRICT_VIEW_ON"
                    if (mod.show_viewport):
                        EnableIcon = "RESTRICT_VIEW_OFF"
                    Enable = row.operator(BTool_EnableBrush.bl_idname, icon=EnableIcon,emboss = False)
                    Enable.thisObj = mod.object.name
                    
                    Remove = row.operator("btool.remove", icon="CANCEL",emboss = False)
                    Remove.thisObj = mod.object.name
                    Remove.Prop = "THIS"
                    
                    #Stack Changer
                    Up = row.operator("btool.move_stack",icon ="TRIA_UP",emboss = False)
                    Up.modif = mod.name
                    Up.direction = "UP"
                    
                    Dw = row.operator("btool.move_stack",icon ="TRIA_DOWN",emboss = False)
                    Dw.modif = mod.name
                    Dw.direction = "DOWN"

                else:
                    row.label(mod.name)
                    #Stack Changer
                    Up = row.operator("btool.move_stack",icon ="TRIA_UP",emboss = False)
                    Up.modif = mod.name
                    Up.direction = "UP"
                    
                    Dw = row.operator("btool.move_stack",icon ="TRIA_DOWN",emboss = False)
                    Dw.modif = mod.name
                    Dw.direction = "DOWN"
        

# ------------------ BOOL TOOL ADD-ON PREFERENCES ----------------------------

def UpdateBoolTool_Pref(self,context):
    if self.fast_transform:
        RegisterFastT()
    else:
        UnRegisterFastT()

class BoolTool_Pref(AddonPreferences):
    bl_idname = __name__
    
    fast_transform = bpy.props.BoolProperty(name="Fast Transformations", default=False, update=UpdateBoolTool_Pref, description="Replace the Transform HotKeys (G,R,S) for a custom version that can optimize the visualization of Brushes")
    make_vertex_groups = bpy.props.BoolProperty(name="Make Vertex Groups", default=False, description="When Apply a Brush to de Object it will create a new vertex group of the new faces")
    make_boundary = bpy.props.BoolProperty(name="Make Boundary", default=False, description = "When Apply a Brush to de Object it will create a new vertex group of the bondary boolean area")
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Experimental Features:")
        layout.prop(self, "fast_transform")
        """
        # EXPERIMENTAL
        layout.prop(self, "make_vertex_groups")
        layout.prop(self, "make_boundary")
        """
        
#------------------- REGISTER ------------------------------------------------
addon_keymaps = []
addon_keymapsFastT = []

#Fast Transform HotKeys Register
def RegisterFastT():    
    
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    kmi = km.keymap_items.new(BTool_FastTransform.bl_idname, 'G', 'PRESS')
    kmi.properties.operator = "Translate"
    addon_keymapsFastT.append((km, kmi))
    
    kmi = km.keymap_items.new(BTool_FastTransform.bl_idname, 'R', 'PRESS')
    kmi.properties.operator = "Rotate"
    addon_keymapsFastT.append((km, kmi))
    
    kmi = km.keymap_items.new(BTool_FastTransform.bl_idname, 'S', 'PRESS')
    kmi.properties.operator = "Scale"
    addon_keymapsFastT.append((km, kmi))

#Fast Transform HotKeys UnRegister
def UnRegisterFastT():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    for km, kmi in addon_keymapsFastT:
        km.keymap_items.remove(kmi)
    addon_keymapsFastT.clear()
            
def register():
    
    #Handlers
    bpy.app.handlers.scene_update_post.append(HandleScene)
    
    
    # Operators
    bpy.utils.register_class(BTool_Union)
    bpy.utils.register_class(BTool_Diff)
    bpy.utils.register_class(BTool_Inters)
    
    bpy.utils.register_class(BTool_Union_Direct)
    bpy.utils.register_class(BTool_Diff_Direct)
    bpy.utils.register_class(BTool_Inters_Direct)
    
    bpy.utils.register_class(BTool_DrawPolyBrush)
   
    
    # Others
    bpy.utils.register_class(BTool_Remove)
    bpy.utils.register_class(BTool_AllBrushToMesh)
    bpy.utils.register_class(BTool_BrushToMesh)
    
    #Utils
    bpy.utils.register_class(BTool_FindBrush)
    bpy.utils.register_class(BTool_MoveStack)
    bpy.utils.register_class(BTool_EnableBrush)
    bpy.utils.register_class(BTool_EnableThisBrush)
    bpy.utils.register_class(BTool_EnableFTransform)
    
    
    #Append 3DVIEW Menu
    bpy.utils.register_class(BoolTool_Menu)
    bpy.types.VIEW3D_MT_object.append(VIEW3D_BoolTool_Menu)
    
    # Append 3DVIEW Tab
    bpy.utils.register_class(BoolTool_Tools)
    bpy.utils.register_class(BoolTool_Config)
    bpy.utils.register_class(BoolTool_BViwer)
    
    #Fast Transform
    bpy.utils.register_class(BTool_FastTransform)
        
    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    # Brush Operators
    kmi = km.keymap_items.new(BTool_Union.bl_idname, 'NUMPAD_PLUS', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTool_Diff.bl_idname, 'NUMPAD_MINUS', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTool_Inters.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    
    # Direct Operators
    kmi = km.keymap_items.new(BTool_Union_Direct.bl_idname, 'NUMPAD_PLUS', 'PRESS', ctrl=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTool_Diff_Direct.bl_idname, 'NUMPAD_MINUS', 'PRESS', ctrl=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTool_Inters_Direct.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTool_BrushToMesh.bl_idname, 'NUMPAD_ENTER', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTool_AllBrushToMesh.bl_idname, 'NUMPAD_ENTER', 'PRESS', ctrl=True, shift=True)
    addon_keymaps.append((km, kmi))
    
    # Bool Tool Global User Preferences
    bpy.utils.register_class(BoolTool_Pref)

def unregister():
    
    bpy.utils.unregister_class(BoolTool_Menu)
    bpy.utils.unregister_class(BoolTool_Tools)
    bpy.utils.unregister_class(BoolTool_Config)
    bpy.utils.unregister_class(BoolTool_BViwer)
    bpy.types.VIEW3D_MT_object.remove(VIEW3D_BoolTool_Menu)
        
    #Operators
    bpy.utils.unregister_class(BTool_Union)
    bpy.utils.unregister_class(BTool_Diff)
    bpy.utils.unregister_class(BTool_Inters)
    
    bpy.utils.unregister_class(BTool_Union_Direct)
    bpy.utils.unregister_class(BTool_Diff_Direct)
    bpy.utils.unregister_class(BTool_Inters_Direct)
    
    bpy.utils.register_class(BTool_DrawPolyBrush)
    
    #Othes
    bpy.utils.unregister_class(BTool_AllBrushToMesh)
    bpy.utils.unregister_class(BTool_BrushToMesh)
    bpy.utils.unregister_class(BTool_Remove)
    
    #Utils
    bpy.utils.unregister_class(BTool_FindBrush)
    bpy.utils.unregister_class(BTool_MoveStack)
    bpy.utils.unregister_class(BTool_EnableBrush)
    bpy.utils.unregister_class(BTool_EnableThisBrush)
    bpy.utils.unregister_class(BTool_EnableFTransform)
    
    #Fast Transform
    bpy.utils.unregister_class(BTool_FastTransform)
    
    #Add Handlers    
    bpy.app.handlers.scene_update_post.remove(HandleScene)

    # Keymapping
    # handle the keymap ( NEED TO FIX BUG YET )
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    # Bool Tool Global User Preferences
    bpy.utils.unregister_class(BoolTool_Pref)
    

if __name__ == "__main__":
    register()

