bl_info = {
    "name": "ShapeKey Helpers",
    "author": "Ott, Jan",
    "version": (1, 0, 0),
    "blender": (2, 76, 0),
    "description": "Adds three operators: 'Split Shapekeys', 'Apply Modifiers and Keep Shapekeys' and 'Apply Selected Shapekey as Basis'",
    "warning": "",
    "wiki_url": "",
    "category": "",
}


import bpy

#__________________________________________________________________________
#__________________________________________________________________________


def SetActiveShapeKey (name):
    bpy.context.object.active_shape_key_index = bpy.context.object.data.shape_keys.key_blocks.keys().index(name)
    
#__________________________________________________________________________
#__________________________________________________________________________

O = bpy.ops

class ShapeKeySplitter(bpy.types.Operator):
    """Creates a new object with the shapekeys split based on two vertex groups, named 'left' and 'right', that you must create manually"""
    bl_idname = "object.shape_key_splitter"
    bl_label = "Split Shapekeys"

    def execute(self, context):
        
        O.object.select_all(action='DESELECT')
        bpy.context.object.select = True

        #____________________________
        #Generate copy of object
        #____________________________
        originalName = bpy.context.object.name
        O.object.duplicate_move()
        bpy.context.object.name = originalName + "_SplitShapeKeys"


        listOfKeys = []

        index = 0

        #__________________________________________________

        for s_key in bpy.context.object.data.shape_keys.key_blocks:
            
            if(index == 0):
                index = index + 1
                continue 
            
            if s_key.name.endswith('.L') or s_key.name.endswith('.R') or s_key.name.endswith('.B'):
                continue
            
            
            listOfKeys.append(s_key.name)

        #__________________________________________________

        for name in listOfKeys:
            
            SetActiveShapeKey(name)
            
            savedName = name
            savedShapeKey = bpy.context.object.active_shape_key
            
            
            #Create left version
            
            O.object.shape_key_clear()
            
            SetActiveShapeKey(savedName)
            savedShapeKey.vertex_group = 'left'
            savedShapeKey.value = 1.0
            
            O.object.shape_key_add(from_mix=True)
            bpy.context.object.active_shape_key.name = savedName + ".L"

            
            #Create right version
            
            O.object.shape_key_clear()
            
            SetActiveShapeKey(savedName)
            savedShapeKey.vertex_group = 'right'
            savedShapeKey.value = 1.0
            
            O.object.shape_key_add(from_mix=True)
            bpy.context.object.active_shape_key.name = savedName + ".R"
            
            
        for name in listOfKeys:
            
            #Set index to target shapekey
            SetActiveShapeKey(name)
            #Remove
            O.object.shape_key_remove(all=False)
                
                
        return {'FINISHED'}
    

class ShapeKeyPreserver(bpy.types.Operator):
    """Creates a new object with all modifiers applied and all shape keys preserved"""
    """NOTE: Blender can only combine objects with a matching number of vertices. """ 
    """As a result, you need to make sure that your shape keys don't change the number of vertices of the mesh. """
    """Modifiers like 'Subdivision Surface' can always be applied without any problems, other modifiers like 'Bevel' or 'Edgesplit' may not."""

    bl_idname = "object.shape_key_preserver"
    bl_label = "Apply Modifiers and Keep Shapekeys"
    
    def execute(self, context):
    
        oldName = bpy.context.active_object.name
        
        #Change context to 'VIEW_3D' and store old context
        oldContext = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'

        #selection setup
        originalObject = bpy.context.active_object

        originalObject.select = True

        listOfShapeInstances = []
        listOfShapeKeyValues = []

        #_______________________________________________________________

        #Deactivate any armature modifiers
        for mod in originalObject.modifiers:
            if mod.type == 'ARMATURE':
                originalObject.modifiers[mod.name].show_viewport = False

        index = 0
        for shapekey in originalObject.data.shape_keys.key_blocks:
            if(index == 0):
                index = index + 1
                continue
            listOfShapeKeyValues.append(shapekey.value)

        index = 0
        for shapekey in originalObject.data.shape_keys.key_blocks:
            
            if(index == 0):
                index = index + 1
                continue
            
            bpy.ops.object.select_all(action='DESELECT')
            originalObject.select = True
            bpy.context.scene.objects.active = originalObject
            
            bpy.ops.object.shape_key_clear()
            
            shapekey.value = 1.0
            
            #save name
            #____________________________
            shapekeyname = shapekey.name
            
            #create new object from shapekey and add it to list
            #____________________________
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            bpy.ops.object.convert(target='MESH')
            listOfShapeInstances.append(bpy.context.active_object)
            
            #rename new object
            #____________________________
            bpy.context.object.name = shapekeyname
            
            bpy.ops.object.select_all(action='DESELECT')
            originalObject.select = True
            bpy.context.scene.objects.active = originalObject

        #_____________________________________________________________
        #Prepare final empty container model for all those shape keys:
        #_____________________________________________________________

        bpy.context.scene.objects.active = originalObject
        bpy.ops.object.shape_key_clear()

        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        newObject = bpy.context.active_object

        bpy.ops.object.shape_key_clear()
        bpy.ops.object.shape_key_remove(all=True)

        newObject.name = oldName + "_Applied"

        for mod in newObject.modifiers:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

        errorDuringShapeJoining = False
            
        for object in listOfShapeInstances:
            
            bpy.ops.object.select_all(action='DESELECT')
            newObject.select = True
            object.select = True
            bpy.context.scene.objects.active = newObject
            
            print("Trying to join shapes.")
            
            result = bpy.ops.object.join_shapes()
            
            if(result != {'FINISHED'}):
                print ("Could not add " + object.name + " as shape key.")
                errorDuringShapeJoining = True

        if(errorDuringShapeJoining == False):
            print("Success!")
                
        if(errorDuringShapeJoining == False):
            #Reset old shape key values on new object
            index = 0
            for shapekey in newObject.data.shape_keys.key_blocks:
                if(index == 0):
                    index = index + 1
                    continue
                shapekey.value = listOfShapeKeyValues[index-1]
                index = index + 1

        #Reset old shape key values on original object
        index = 0
        for shapekey in originalObject.data.shape_keys.key_blocks:
            if(index == 0):
                index = index + 1
                continue
            shapekey.value = listOfShapeKeyValues[index-1]
            index = index + 1
            
            
        #Select and delete all temporal shapekey objects       
        bpy.ops.object.select_all(action='DESELECT')

        for object in listOfShapeInstances:
            object.select = True
            
        bpy.ops.object.delete(use_global=False)
        
        
        #Reactivate armature modifiers on old and new object
    
        for mod in originalObject.modifiers:
            if mod.type == 'ARMATURE':
                originalObject.modifiers[mod.name].show_viewport = True

        for mod in newObject.modifiers:
            if mod.type == 'ARMATURE':
                newObject.modifiers[mod.name].show_viewport = True
                
        bpy.context.area.type = oldContext
        
        return {'FINISHED'}
    
    
    
class ShapeKeyApplier(bpy.types.Operator):
    """Replace the 'Basis' shape key with the currently selected shape key"""
    bl_idname = "object.shape_key_applier"
    bl_label = "Apply Selected Shapekey as Basis"
    
    def execute(self, context):
        
        O.object.select_all(action='DESELECT')
        bpy.context.object.select = True

        #____________________________
        #Generate copy of object
        #____________________________
        originalName = bpy.context.object.name
        O.object.duplicate_move()
        bpy.context.object.name = originalName + "_Applied_Shape_Key"

        shapeKeyToBeApplied_name = bpy.context.object.active_shape_key.name

        listOfKeys = []

        #__________________________________________________
        #Store all shape keys in a list 
        #__________________________________________________

        for s_key in bpy.context.object.data.shape_keys.key_blocks:
            
            if s_key.name == shapeKeyToBeApplied_name:
                continue
            
            listOfKeys.append(s_key.name)

        #__________________________________________________

        for name in listOfKeys:
            
            SetActiveShapeKey(name)
            currentShapeKey = bpy.context.object.active_shape_key
            
            SetActiveShapeKey(shapeKeyToBeApplied_name)
            applyShapeKey = bpy.context.object.active_shape_key
            
            #Add new shapekey from mix
            O.object.shape_key_clear()
            
            currentShapeKey.value = 1.0
            applyShapeKey.value = 1.0
            
            O.object.shape_key_add(from_mix=True)
            bpy.context.object.active_shape_key.name = currentShapeKey.name + "_"
            
            
        for name in listOfKeys:
            
            #Set index to target shapekey
            SetActiveShapeKey(name)
            #Remove
            O.object.shape_key_remove(all=False)
            
            
        SetActiveShapeKey(shapeKeyToBeApplied_name)
        O.object.shape_key_remove(all=False)

        #Remove the "_" at the end of each shapeKey
        for s_key in bpy.context.object.data.shape_keys.key_blocks:
            
            s_key.name = s_key.name[:-1]
            
            
        return {'FINISHED'}




def shapeKeyHelpers_menu_func(self, context):
    self.layout.separator()
    self.layout.operator(ShapeKeySplitter.bl_idname, text="Split Shapekeys", icon="FULLSCREEN_ENTER")
    self.layout.operator(ShapeKeyPreserver.bl_idname, text="Apply Modifiers and Keep Shapekeys", icon="MODIFIER")
    self.layout.operator(ShapeKeyApplier.bl_idname, text="Apply Selected Shapekey as Basis", icon="KEY_HLT")


def register():
    bpy.utils.register_class(ShapeKeySplitter)
    bpy.utils.register_class(ShapeKeyPreserver)
    bpy.utils.register_class(ShapeKeyApplier)
    bpy.types.MESH_MT_shape_key_specials.append(shapeKeyHelpers_menu_func)


def unregister():
    bpy.utils.unregister_class(ShapeKeySplitter)
    bpy.utils.unregister_class(ShapeKeyPreserver)
    bpy.utils.unregister_class(ShapeKeyApplier)
    bpy.types.MESH_MT_shape_key_specials.remove(shapeKeyHelpers_menu_func)

if __name__ == "__main__":
    register()
    
    

