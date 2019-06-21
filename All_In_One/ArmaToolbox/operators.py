import bpy
from lists import safeAddTime
from . import properties
from ArmaProxy import CopyProxy, CreateProxyPos
import bmesh
import ArmaTools
import RVMatTools
from math import *
from mathutils import *
from ArmaToolbox import getLodsToFix

class ATBX_OT_add_frame_range(bpy.types.Operator):
    bl_idname = "armatoolbox.add_frame_range"
    bl_label = ""
    bl_description = "Add a range of keyframes"
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.keyFrames
        guiProps = context.window_manager.armaGUIProps
        start = guiProps.framePanelStart
        end = guiProps.framePanelEnd
        step = guiProps.framePanelStep
        
        for frame in range(start, end, step):
            safeAddTime(frame, prp)
            
        return {"FINISHED"}
        
class ATBX_OT_add_key_frame(bpy.types.Operator):
    bl_idname = "armatoolbox.add_key_frame"
    bl_label = ""
    bl_description = "Add a keyframe"
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.keyFrames
        frame = context.scene.frame_current
        safeAddTime(frame, prp)
        return {"FINISHED"}
  
class ATBX_OT_add_all_key_frames(bpy.types.Operator):
    bl_idname = "armatoolbox.add_all_key_frames"
    bl_label = ""
    bl_description = "Add a keyframe"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj.animation_data is not None and obj.animation_data.action is not None
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.keyFrames
        
        keyframes = [] 

        if obj.animation_data is not None and obj.animation_data.action is not None:
            fcurves = obj.animation_data.action.fcurves
            for curve in fcurves:
                for kp in curve.keyframe_points:
                    if kp.co.x not in keyframes:
                        keyframes.append(kp.co.x)
        
        keyframes.sort()
        
        for frame in keyframes:
            safeAddTime(frame, prp)
            
        return {"FINISHED"}  
  
class ATBX_OT_rem_key_frame(bpy.types.Operator):
    bl_idname = "armatoolbox.rem_key_frame"
    bl_label = ""
    bl_description = "Remove a keyframe"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        arma = obj.armaObjProps
        return arma.keyFramesIndex != -1
    

    def execute(self, context):
        obj = context.active_object
        arma = obj.armaObjProps
        if arma.keyFramesIndex != -1:
            arma.keyFrames.remove(arma.keyFramesIndex)
        return {"FINISHED"}        
        
class ATBX_OT_rem_all_key_frames(bpy.types.Operator):
    bl_idname = "armatoolbox.rem_all_key_frames"
    bl_label = ""
    bl_description = "Remove a keyframe"

    def execute(self, context):
        obj = context.active_object
        arma = obj.armaObjProps
        arma.keyFrames.clear()
        return {"FINISHED"}        
        
class ATBX_OT_add_prop(bpy.types.Operator):
    bl_idname = "armatoolbox.add_prop"
    bl_label = ""
    bl_description = "Add a named Property"
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.namedProps
        item = prp.add()
        item.name = "<new property>"
        return {"FINISHED"}

class ATBX_OT_rem_prop(bpy.types.Operator):
    bl_idname = "armatoolbox.rem_prop"
    bl_label = ""
    bl_description = "Remove named property"
    
    def execute(self, context):
        obj = context.active_object
        arma = obj.armaObjProps
        if arma.namedPropIndex != -1:
            arma.namedProps.remove(arma.namedPropIndex)
        return {"FINISHED"}
    
###
##   Enable Operator
#

class ATBX_OT_enable(bpy.types.Operator):
    bl_idname = "armatoolbox.enable"
    bl_label = "Enable for Arma Toolbox"
    
    def execute(self, context):
        obj = context.active_object
        if (obj.armaObjProps.isArmaObject == False):
            obj.armaObjProps.isArmaObject = True
        return{'FINISHED'}

###
##   Proxy Operators
#


class ATBX_OT_add_new_proxy(bpy.types.Operator):
    bl_idname = "armatoolbox.add_new_proxy"
    bl_label = ""
    bl_description = "Add a proxy"
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode="EDIT")
        obj = context.active_object
        mesh = obj.data
        
        cursor_location = bpy.context.scene.cursor_location
        cursor_location = cursor_location - obj.location

        bm = bmesh.from_edit_mesh(mesh)

        i = len(bm.verts)
        v1 = bm.verts.new(cursor_location + Vector((0,0,0)))
        v2 = bm.verts.new(cursor_location + Vector((0,0,2)))
        v3 = bm.verts.new(cursor_location + Vector((0,1,0)))
        
        f = bm.faces.new((v1,v2,v3))
        print (v1.index)  
        bpy.ops.object.mode_set(mode="OBJECT")

        #bm.to_mesh(mesh)
        #mesh.update()
              
        vgrp = obj.vertex_groups.new(name = "@@armaproxy")
        vgrp.add([i+0],1,'ADD')
        vgrp.add([i+1],1,'ADD')
        vgrp.add([i+2],1,'ADD')
            
        bpy.ops.object.mode_set(mode="EDIT")
        
        p = obj.armaObjProps.proxyArray.add()
        p.name = vgrp.name
        
        
        return {"FINISHED"}    

# This does two things. First, it goes through the model checking if the
# proxies in the list are still in the model, and delete all that arent.
#
# Secondly, it looks for "standard" proxy definition like "proxy:xxxx.001" and
# converts them into new proxies.
class ATBX_OT_add_sync_proxies(bpy.types.Operator):
    bl_idname = "armatoolbox.sync_proxies"
    bl_label = ""
    bl_description = "Synchronize the proxy list with the model"
    
    def execute(self, context):
        obj = context.active_object
        prp = obj.armaObjProps.proxyArray

        # Gp through our proxy list
        delList = []
        max = prp.values().__len__()
        for i in range(0,max):
            if prp[i].name not in obj.vertex_groups.keys():
                delList.append(i)
        if len(delList) > 0:
            delList.reverse()
            for item in delList:
                prp.remove(item)
        
        # Go through the vertex groups
        for grp in obj.vertex_groups:
            if len(grp.name) > 5:
                if grp.name[:6] == "proxy:":
                    prx = grp.name.split(":")[1]
                    if prx.find(".") != -1:
                        a = prx.split(".")
                        prx = a[0]
                        idx = a[1]
                    else:
                        idx = "1"
                    n = prp.add()
                    n.name = grp.name
                    n.index = int(idx)
                    n.path = "P:" + prx
                    
                
        return {"FINISHED"}         

class ATBX_OT_add_toggle_proxies(bpy.types.Operator):
    bl_idname = "armatoolbox.toggle_proxies"
    bl_label = ""
    bl_description = "Toggle GUI visibilityl"
    
    prop : bpy.props.StringProperty()
    
    def execute(self, context):
        obj = context.active_object
        prop = obj.armaObjProps.proxyArray[self.prop]
        if prop.open == True:
            prop.open = False
        else:
            prop.open = True  
        return {"FINISHED"}     

class ATBX_OT_copy_proxy(bpy.types.Operator):
    bl_idname = "armatoolbox.copy_proxy"
    bl_label = ""
    bl_description = "Copy proxy to other LOD's"    

    objectArray : bpy.props.CollectionProperty(type=properties.ArmaToolboxCopyHelper)
    copyProxyName : bpy.props.StringProperty()
    encloseInto : bpy.props.StringProperty(description="Enclose the proxy in a selection. Leave blank to not create any extra selection")

    def execute(self, context):
        sObj = context.active_object
        for obj in self.objectArray:
            if obj.doCopy:
                enclose = self.encloseInto
                enclose = enclose.strip()
                if len(enclose) == 0:
                    enclose = None
                
                CopyProxy(sObj, bpy.data.objects[obj.name], self.copyProxyName, enclose)

        self.objectArray.clear()
        return {"FINISHED"}
   
    def invoke(self, context, event):
        
        for obj in bpy.data.objects.values():
            if obj.armaObjProps.isArmaObject == True and obj != context.active_object:
                prop = self.objectArray.add()
                prop.name  = obj.name
                prop.doCopy = True
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Copy Proxy!")
        for s in self.objectArray:
            row = layout.row()
            row.prop(s, "doCopy", text=s.name)
        row = layout.row()
        row.prop(self, "encloseInto", text="Enclose in:")

class ATBX_OT_delete_proxy(bpy.types.Operator):
    bl_idname = "armatoolbox.delete_proxy"
    bl_label = ""
    bl_description = "Delete given proxy"  
    
    proxyName : bpy.props.StringProperty()
    
    @classmethod
    def poll(self, context):
        if context.active_object.mode == 'OBJECT':
            return True
        else:
            return False
    
    def execute(self, context):
        sObj = context.active_object
        mesh = sObj.data

        idxList = []

        grp = sObj.vertex_groups[self.proxyName]
        for v in mesh.vertices:
            for g in v.groups:
                if g.group == grp.index:
                    if g.weight > 0:
                        idxList.append(v.index)
                        
        if len(idxList) > 0:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            if hasattr(bm.verts, "ensure_lookup_table"): 
                bm.verts.ensure_lookup_table()
            
            vList = []
            for i in idxList:
                vList.append(bm.verts[i])
            
            for v in vList:
                bm.verts.remove(v)
        
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            
        sObj.vertex_groups.remove(grp)
        prp = sObj.armaObjProps.proxyArray
        for i,pa in enumerate(prp):
            if pa.name == self.proxyName:
                prp.remove(i)
            
            
        return {"FINISHED"}
    
###
##  Weight Tools
#

class ATBX_OT_select_weight_vertex(bpy.types.Operator):
    bl_idname = "armatoolbox.sel_weights"
    bl_label = "Select vertices with more than 4 bones weights"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'  
    
    def execute(self, context):
        ArmaTools.selectOverweightVertices()
        return {'FINISHED'}

class ATBX_OT_prune_weight_vertex(bpy.types.Operator):
    bl_idname = "armatoolbox.prune_weights"
    bl_label = "Prune vertices with more than 4 bones weights"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'  
    
    def execute(self, context):
        ArmaTools.pruneOverweightVertices()
        return {'FINISHED'}

class ATBX_OT_bulk_rename(bpy.types.Operator):
    bl_idname = "armatoolbox.bulk_rename"
    bl_label = "Bulk Rename Arma material paths"
    
    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps
        if guiProps.renamableListIndex > -1 and guiProps.renamableList.__len__() > guiProps.renamableListIndex:
            frm = guiProps.renamableList[guiProps.renamableListIndex].name
            t   = guiProps.renameTo 
            ArmaTools.bulkRename(context, frm, t)
        return {'FINISHED'}
    
class ATBX_OT_create_components(bpy.types.Operator):
    bl_idname = "armatoolbox.create_components"
    bl_label = "Create Geometry Components"
    
    def execute(self, context):
        ArmaTools.createComponents(context)
        return {'FINISHED'}

class ATBX_OT_bulk_reparent(bpy.types.Operator):
    bl_idname = "armatoolbox.bulk_reparent"
    bl_label = "Bulk Re-parent Arma material paths"

    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps
        frm = guiProps.parentFrom
        t   = guiProps.parentTo
        ArmaTools.bulkReparent(context, frm, t)
        return {'FINISHED'}

class ATBX_OT_selection_rename(bpy.types.Operator):
    bl_idname = "armatoolbox.bulk_rename_selection"
    bl_label = "Bulk Re-parent Arma material paths"

    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps
        frm = guiProps.renameSelectionFrom
        t   = guiProps.renameSelectionTo
        ArmaTools.bulkRenameSelections(context, frm, t)
        return {'FINISHED'}      

class ATBX_OT_hitpoint_creator(bpy.types.Operator):
    bl_idname = "armatoolbox.hitpoint_creator"
    bl_label = "Create Hitpoint Volume"
    
    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps
        selection = guiProps.hpCreatorSelectionName
        radius = guiProps.hpCreatorRadius
        ArmaTools.hitpointCreator(context, selection, radius)
        return {'FINISHED'}

# Make sure all ArmaObjects do not have n-gons with more than four vertices
class ATBX_OT_ensure_quads(bpy.types.Operator):
    '''Make sure all ArmaObjects do not have n-gons with more than four vertices'''
    bl_idname = "armatoolbox.ensure_quads"
    bl_label = "Tesselate all n-gons > 4 in all objects flagged as Arma Objects"

    def execute(self, context):
        ArmaTools.tessNonQuads(context)
        return {'FINISHED'}

class ATBX_OT_rvmat_relocator(bpy.types.Operator):
    '''Relocate a single RVMat to a different directory'''
    bl_idname = "armatoolbox.rvmatrelocator"
    bl_label = "Relocate RVMat"
    
    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps
        rvfile = guiProps.rvmatRelocFile
        rvout  = guiProps.rvmatOutputFolder
        prefixPath = guiProps.matPrefixFolder
        RVMatTools.rt_CopyRVMat(rvfile, rvout, prefixPath)
        return {'FINISHED'}

class ATBX_OT_material_relocator(bpy.types.Operator):
    ''' Relocate RVMATs'''
    bl_idname = "armatoolbox.materialrelocator"
    bl_label = "Relocate Material"
    
    material : bpy.props.StringProperty()
    texture : bpy.props.StringProperty()
    
    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps

        outputPath = guiProps.matOutputFolder
        if len(outputPath) is 0:
            self.report({'ERROR_INVALID_INPUT'}, "Output folder name missing")
        
        prefixPath = guiProps.matPrefixFolder
        if len(prefixPath) == 0:
            prefixPath = "P:\\"
        
        materialName = self.material
        textureName = self.texture
        RVMatTools.mt_RelocateMaterial(textureName, materialName, outputPath, guiProps.matAutoHandleRV, prefixPath)

        return {'FINISHED'}

class ATBX_OT_toggle_gui_prop(bpy.types.Operator):
    bl_idname = "armatoolbox.toggleguiprop"
    bl_label = ""
    bl_description = "Toggle GUI visibilityl"
    
    prop : bpy.props.StringProperty()
        
    def execute(self, context):
        prop = context.window_manager.armaGUIProps
        if prop.is_property_set(self.prop) == True and prop[self.prop] == True:
            prop[self.prop] = False
        else:
            prop[self.prop] = True  
        return {"FINISHED"}   


class ATBX_OT_join_as_proxy(bpy.types.Operator):
    bl_idname = "armatoolbox.joinasproxy"
    bl_label = ""
    bl_description = "Join as Proxy"
    
    @classmethod
    def poll(cls, context):
        ## Visible when there is a selected object, it is a mesh
        obj = context.active_object
       
        return (obj 
            and obj.select_get() == True
            and obj.armaObjProps.isArmaObject == True
            and obj.type == "MESH" 
            and len(bpy.context.selected_objects) > 1
            )
        
    def execute(self, context):
        obj = context.active_object
        selected = context.selected_objects
        
        path =  context.window_manager.armaGUIProps.mapProxyObject
        index = context.window_manager.armaGUIProps.mapProxyIndex
        doDel = context.window_manager.armaGUIProps.mapProxyDelete
        
        enclose = context.window_manager.armaGUIProps.mapProxyEnclose
        if len(enclose) == 0:
            enclose = None
        
        for sel in selected:
            if sel == obj:
                pass
            else:
                if enclose == None:
                    e = None
                else:
                    e = enclose + str(index)
                pos = sel.location - obj.location 
                CreateProxyPos(obj, pos, path, index, e)
                index = index + 1
        
        if doDel == True:
            obj.select_set(False)
            bpy.ops.object.delete();      
        
        return {"FINISHED"}   

###
##  Proxy Path Changer
#
#   Code contributed by Cowcancry

class ATBX_OT_proxy_path_changer(bpy.types.Operator):
    bl_idname = "armatoolbox.proxypathchanger"
    bl_label = "Proxy Path Change"
    
    def execute(self, context):
        guiProps = context.window_manager.armaGUIProps
        pathFrom = guiProps.proxyPathFrom
        pathTo = guiProps.proxyPathTo

        for obj in bpy.data.objects.values():
            if (obj 
            and obj.armaObjProps.isArmaObject == True
            and obj.type == "MESH"):
                for proxy in obj.armaObjProps.proxyArray:
                    proxy.path = proxy.path.replace(pathFrom, pathTo)
        return {'FINISHED'}

class ATBX_OT_selection_translator(bpy.types.Operator):
    bl_idname = "armatoolbox.autotranslate"
    bl_label = "Attempt to automatically translate Czech selection names"

    def execute(self, context):
        ArmaTools.autotranslateSelections()
        return {'FINISHED'}
 

class ATBX_OT_set_mass(bpy.types.Operator):
    bl_idname = "armatoolbox.setmass"
    bl_label = ""
    bl_description = "Set the same mass for all selected vertices"
    
    @classmethod
    def poll(cls, context):
        ## Visible when there is a selected object, it is a mesh
        obj = context.active_object
        return (obj
            and obj.select_get() == True
            and obj.armaObjProps.isArmaObject == True
            and obj.type == "MESH" 
            and (obj.armaObjProps.lod == '1.000e+13' or obj.armaObjProps.lod == '4.000e+13')
            and obj.mode == 'EDIT'
            ) 
        
    def execute(self, context):
        obj = context.active_object
        selected = context.selected_objects
               
        mass = context.window_manager.armaGUIProps.vertexWeight

        ArmaTools.setVertexMass(obj, mass)
        return {"FINISHED"}   

class ATBX_OT_distribute_mass(bpy.types.Operator):
    bl_idname = "armatoolbox.distmass"
    bl_label = ""
    bl_description = "Distribute the given mass equally to all selected vertices"
    
    @classmethod
    def poll(cls, context):
        ## Visible when there is a selected object, it is a mesh
        obj = context.active_object
        return (obj
            and obj.select_get() == True
            and obj.armaObjProps.isArmaObject == True
            and obj.type == "MESH" 
            and (obj.armaObjProps.lod == '1.000e+13' or obj.armaObjProps.lod == '4.000e+13')
            and obj.mode == 'EDIT'
            ) 
        
    def execute(self, context):
        obj = context.active_object
        selected = context.selected_objects
               
        mass = context.window_manager.armaGUIProps.vertexWeight

        ArmaTools.distributeVertexMass(obj, mass)
        return {"FINISHED"} 


# Fix shadow volumes
class ATBX_OT_fix_shadows(bpy.types.Operator):
    bl_idname = "armatoolbox.fixshadows"
    bl_label = "Items to fix"
    bl_description = "Fix Shadow volumes resolutions"
    
    objectArray : bpy.props.CollectionProperty(type=properties.ArmaToolboxFixShadowsHelper)
    
    def execute(self, context):
        for prop in self.objectArray:
            obj = bpy.data.objects[prop.name]

            lod = obj.armaObjProps.lod
            res = obj.armaObjProps.lodDistance
            
            print (obj.name, " " , lod , " " , res)
            
            if lod == "1.000e+4":
                if res == 0:
                    obj.armaObjProps.lodDistance = 1.0
            elif lod == "1.001e+4":
                print("Stencil 2")
                obj.armaObjProps.lod = "1.000e+4"
                obj.armaObjProps.lodDistance = 10.0
            elif lod == "1.100e+4":
                if res == 0:
                    obj.armaObjProps.lodDistance = 1.0
            elif lod == "1.101e+4":
                obj.armaObjProps.lod = "1.100e+4"
                obj.armaObjProps.lodDistance = 10.0
            
        self.objectArray.clear()
        return {"FINISHED"}

    def invoke(self, context, event):
        self.objectArray.clear()
        objs = getLodsToFix()
        for o in objs:
            prop = self.objectArray.add()
            prop.name = o.name
            prop.fixThis = True
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(icon="MODIFIER", text="The following objects have shadow volume issues")
        col = layout.column()

        for s in self.objectArray:
            row = layout.row()
            row.prop(s, "fixThis", text=s.name)
        
        row = layout.row()
        row.label (text  = "Click 'OK' to fix")


op_classes = (
    ATBX_OT_add_frame_range,
    ATBX_OT_add_key_frame,
    ATBX_OT_add_all_key_frames,
    ATBX_OT_rem_key_frame,
    ATBX_OT_rem_all_key_frames,
    ATBX_OT_add_prop,
    ATBX_OT_rem_prop,
    ATBX_OT_enable,
    ATBX_OT_add_new_proxy,
    ATBX_OT_add_sync_proxies,
    ATBX_OT_add_toggle_proxies,
    ATBX_OT_copy_proxy,
    ATBX_OT_delete_proxy,
    ATBX_OT_select_weight_vertex,
    ATBX_OT_prune_weight_vertex,
    ATBX_OT_bulk_rename,
    ATBX_OT_create_components,
    ATBX_OT_bulk_reparent,
    ATBX_OT_selection_rename,
    ATBX_OT_hitpoint_creator,
    ATBX_OT_ensure_quads,
    ATBX_OT_rvmat_relocator,
    ATBX_OT_material_relocator,
    ATBX_OT_toggle_gui_prop,
    ATBX_OT_join_as_proxy,
    ATBX_OT_proxy_path_changer,
    ATBX_OT_selection_translator,
    ATBX_OT_set_mass,
    ATBX_OT_distribute_mass,
    ATBX_OT_fix_shadows,
)


def register():
    from bpy.utils import register_class
    for c in op_classes:
        register_class(c)

def unregister():
    from bpy.utils import unregister_class
    for c in op_classes:
        unregister_class(c)
        