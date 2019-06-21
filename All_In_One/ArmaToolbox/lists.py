import bpy

class ATBX_UL_named_prop_list(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        prop = item
        layout.label(text = prop.name)

class ATBX_UL_key_frame_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        prop = item
    
        startFrame = context.scene.frame_start
        endFrame = context.scene.frame_end
        frameIdx = prop.timeIndex - startFrame
        timeIdx = frameIdx / (endFrame - startFrame)

        layout.label(text = "%d (time: %f)" %  (prop.timeIndex, timeIdx))
    
    def filter_items(self, context, data, propname):
        helper_funcs = bpy.types.UI_UL_list
        keyFrames = getattr(data, propname)
        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Reorder by name or average weight.
        _sort = [(idx, frame) for idx, frame in enumerate(keyFrames)]
        flt_neworder = helper_funcs.sort_items_helper(_sort, lambda e: e[1].timeIndex, False)

        return flt_flags, flt_neworder

class ATBX_UL_renameable_prop_list(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        prop = item
        layout.label(text = prop.renameable)
        
###
##  Update the component list for the mass distribution
#
class ATBX_UL_update_list(bpy.types.Operator):
    bl_idname = "armatoolbox.updatelist"
    bl_label = ""
    bl_description = "Update List of components"
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.massArray

        for grp in obj.vertex_groups:
            if grp.name in prp.keys():
                pass
            else:
                n = prp.add()
                n.name = grp.name
                n.weight = 0.0

        # Is there really no better way to do this? Bummer!
        delList = []
        max = prp.values().__len__()
        for i in range(0,max):
            if prp[i].name not in obj.vertex_groups.keys():
                delList.append(i)
        if len(delList) > 0:
            delList.reverse()
            for item in delList:
                prp.remove(item)

        return {"FINISHED"}

class ATBX_UL_convert_list(bpy.types.Operator):
    bl_idname = "armatoolbox.convertlist"
    bl_label = ""
    bl_description = "Convert Single mass to component mass"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        prp = obj.armaObjProps
        return (prp.mass > 0)
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.massArray
        num = len(obj.vertex_groups)
        perComponent = obj.armaObjProps.mass / num
        obj.armaObjProps.mass = 0

        for grp in obj.vertex_groups:
            if grp.name in prp.keys():
                pass
            else:
                n = prp.add()
                n.name = grp.name
                n.weight = perComponent

        return {"FINISHED"}

list_classes = (
    ATBX_UL_named_prop_list,
    ATBX_UL_key_frame_list,
    ATBX_UL_renameable_prop_list,
    ATBX_UL_update_list,
    ATBX_UL_convert_list
)

def safeAddTime(frame, prop):
    for k in prop:
        if k.timeIndex == frame:
            return
        
    item = prop.add()
    item.timeIndex = frame
    item.name = str(frame)
    return item

def register():
    from bpy.utils import register_class
    for c in list_classes:
        register_class(c)

def unregister():
    from bpy.utils import unregister_class
    for c in list_classes:
        unregister_class(c)
        