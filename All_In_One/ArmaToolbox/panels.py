import bpy
import os.path as Path
import RVMatTools
from math import *
from mathutils import *

class ATBX_PT_properties_panel(bpy.types.Panel):
    bl_idname = "ATBX_PT_properties_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Arma 3"
    bl_label = "Arma Object Properties"
    #bl_options = {'DEFAULT_CLOSED'}
    
    #@classmethod
    #def poll(cls, context):
        ## Visible when there is a selected object, it is a mesh
    #    obj = context.active_object
    #   
    #    return (obj 
    #        and obj.select_get() == True
    #        and (obj.type == "MESH" or obj.type == "ARMATURE") )

    def draw_header(self, context):
        obj = context.active_object
        if obj != None:
            arma = obj.armaObjProps
            self.layout.prop(arma, "isArmaObject", text="")
            
    def draw(self, context):
        obj = context.active_object
        layout = self.layout

        if obj != None:
            self.enable = obj.select_get()
            
            arma = obj.armaObjProps
            layout.active = arma.isArmaObject
            if obj.type == "MESH":
                #--- Add a button to enable this object for Arma
                #if (arma.isArmaObject == False):
                #    row = layout.row();
                #    row.operator("armatoolbox.enable", text="Make Arma Object")
                #else:
                #--- The LOD selection
                row = layout.row()
                if arma.lod == '-1.0':
                    box = row.box()
                    newrow = box.row()
                    newrow.prop(arma, "lod", text = "LOD Preset")
                    newrow = box.row()
                    newrow.prop(arma, "lodDistance", text = "Resolution")
                elif arma.lod == "1.000e+4" or arma.lod == "1.001e+4" or arma.lod == "1.100e+4" or arma.lod == "1.101e+4" or arma.lod == "2.000e+4":
                    box = row.box();
                    newrow = box.row()
                    newrow.prop(arma, "lod", text = "LOD Preset")
                    if arma.lod == "1.001e+4" or arma.lod == "1.101e+4":
                        newrow = box.row()
                        newrow.label(icon="ERROR", text="That LOD is deprecated")
                    newrow = box.row()
                    newrow.prop(arma, "lodDistance", text = "Resolution")
                else:
                    row.prop(arma,  "lod", text = "LOD Preset")

                #--- Named Props
                row = layout.row()
                row.label(text = "Named Properties")
                row = layout.row()
                
                row = layout.row()
                row.template_list(listtype_name = "ATBX_UL_named_prop_list", 
                                dataptr = arma,
                                propname = "namedProps",
                                active_dataptr = arma,
                                active_propname="namedPropIndex",
                                list_id="ATBX_namedProps");
                col = row.column(align=True)
                col.operator("armatoolbox.add_prop", icon="ADD")
                col.operator("armatoolbox.rem_prop", icon="REMOVE")    
                
                if arma.namedPropIndex > -1 and arma.namedProps.__len__() > arma.namedPropIndex:
                    nprop = arma.namedProps[arma.namedPropIndex]
                    box = layout.box()
                    row = box.row()
                    row.prop(nprop, "name", text = "Name")
                    row = box.row()
                    row.prop(nprop, "value", text = "Value")
                else:
                    box = layout.box()
                    row = box.row()
                    row.label(text = "Name")
                    row = box.row()
                    row.label(text = "Value")
            elif obj.type == "ARMATURE":
                #if (arma.isArmaObject == False):
                #    row = layout.row();
                #    row.operator("armatoolbox.enable", text="Make Arma RTM Armature")
                #else:
                guiProps = context.window_manager.armaGUIProps
                row = layout.row()
                row.label(text = "RTM Keyframes")
                row = layout.row()
                row.template_list(listtype_name="ATBX_UL_key_frame_list",
                    dataptr = arma,
                    propname = "keyFrames",
                    active_dataptr = arma,
                    active_propname="keyFramesIndex",
                    list_id = "ATBX_keyFrames"
                    )
                row = layout.row()
                row.operator("armatoolbox.add_key_frame", text="Add This Frame", icon="ADD")
                row = layout.row()
                row.operator("armatoolbox.rem_key_frame", text="Remove Frame", icon="REMOVE")
                row = layout.row()
                row.operator("armatoolbox.rem_all_key_frames", text="Clear", icon="CANCEL")
                row = layout.row()
                row.operator("armatoolbox.add_all_key_frames", text="Add Armature Timeline Keys", icon="NDOF_TRANS")
                col = layout.column(align=True)
                split = col.split(factor=0.15)
                if guiProps.framePanelOpen:
                    split.prop(guiProps, "framePanelOpen", text="", icon='DOWNARROW_HLT')
                else:
                    split.prop(guiProps, "framePanelOpen", text="", icon='RIGHTARROW')
                    
                split.operator("armatoolbox.add_frame_range", text="Add Frame Range", icon="ARROW_LEFTRIGHT")
                if guiProps.framePanelOpen:
                    box = layout.box()
                    sub = box.column(align=True)
                    if guiProps.framePanelStart == -1:
                        guiProps.framePanelStart = context.scene.frame_start
                    if guiProps.framePanelEnd == -1:
                        guiProps.framePanelEnd = context.scene.frame_end
                    sub.label(text = "Frame Range")    
                    sub.prop(guiProps, "framePanelStart", text="Start")
                    sub.prop(guiProps, "framePanelEnd", text="End")
                    sub.prop(guiProps, "framePanelStep", text="Step")
                
                box = layout.box()
                row = box.row()
                row.label(text = "RTM Motion Vector")
                if len(arma.centerBone) == 0:
                    row = box.row()
                    row.prop(arma, "motionVector", text="")
                row = box.row()
                row.prop_search(arma, "centerBone", obj.data, "bones",  text="")
        else:
            layout.label(text = "Selection not applicable")

class ATBX_PT_proxy_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Proxies"
    bl_category =  "Arma 3"

    @classmethod
    def poll(cls, context):
        ## Visible when there is a selected object, it is a mesh
        obj = context.active_object
       
        return (obj 
            and obj.select_get() == True
            and obj.armaObjProps.isArmaObject == True
            and (obj.type == "MESH" or obj.type == "ARMATURE") )

    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        row = layout.row()
        row.operator("armatoolbox.add_new_proxy", text = "Add Proxy")
        row.operator("armatoolbox.sync_proxies", text = "Sync with model")
        
        for prox in obj.armaObjProps.proxyArray:
            box = layout.box()
            row = box.row()
            if prox.open == True:
                toggle = row.operator("armatoolbox.toggle_proxies", icon="TRIA_DOWN", emboss=False)
                toggle.prop = prox.name
                row.label(text = prox.name)
            else:
                toggle = row.operator("armatoolbox.toggle_proxies", icon="TRIA_RIGHT", emboss=False)
                name = Path.basename(prox.path)
                toggle.prop = prox.name
                iconName = "NONE"
                if name.upper() == "DRIVER" or name.upper() == "COMMANDER" or name.upper() == "GUNNER":
                    iconName="GHOST_ENABLED"
                if name[:5].upper() == "CARGO":
                    iconName="GHOST_ENABLED" 
                row.label(text = name, icon=iconName)
            
            
            if prox.open:
                # For later
                ##row.operator("armatoolbox.deleteproxy", "", icon="X")
                ##row.operator("armatoolbox.selectproxy", "", icon="VIEWZOOM")
                copyOp = row.operator("armatoolbox.copy_proxy", text = "", icon="PASTEDOWN", emboss=False)
                copyOp.copyProxyName = prox.name
                delOp = row.operator("armatoolbox.delete_proxy", text = "", icon="X", emboss=False)
                delOp.proxyName = prox.name
                row = box.row()
                row.prop(prox, "path", text = "Path")
                row = box.row()
                row.prop(prox, "index", text = "Index")
            else:
                delOp = row.operator("armatoolbox.delete_proxy", text = "", icon="X", emboss=False)
                delOp.proxyName = prox.name
                
        row = layout.row()
        row.operator("armatoolbox.add_new_proxy", text = "Add Proxy")
        row.operator("armatoolbox.sync_proxies", text = "Sync with model")

class ATBX_PT_weight_tool_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "objectmode"
    bl_label = "Arma Weight Tools"
    bl_category = "Arma 3 Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("armatoolbox.sel_weights", text = "Problematic Weighted Vertices")
        row = layout.row()
        row.operator("armatoolbox.prune_weights", text = "Prune weights to 4 bones max")

# Material Properties Panel
class ATBX_PT_material_settings_panel(bpy.types.Panel):
    bl_label = "Arma Toolbox Material Settings"
    #bl_idname = "Arma2MaterialSettingsPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return (context.active_object
            and context.active_object.select_get() == True
            and context.active_object.type == 'MESH'
            and context.active_object.active_material
            and context.active_object.armaObjProps
            and context.active_object.armaObjProps.isArmaObject
            )

    def draw(self, context):
        obj = bpy.context.active_object
        layout = self.layout
        self.enable = obj.active_material
        
        if self.enable:
            arma = obj.active_material.armaMatProps
            box = layout.box()
            # - box
            row = box.row()
            row.prop(arma, "texType", text = "Procedural Texture", expand=True)
            row = box.row()
            matType = arma.texType
            if matType == 'Texture':
                row.prop(arma, "texture", text = "Face Texture")
            elif matType == 'Color':
                row.prop(arma, "colorValue", text = "Color Texture")
                row.prop(arma, "colorType", text = "Type")
            elif matType == 'Custom':
                row.prop(arma, "colorString", text = "Custom Procedural Texture")
            row = box.row()
                    
            # end of box
            layout.separator()
            row = layout.row()
            row.prop(arma, "rvMat", text = "RV Material file")

class ATBX_PT_tool_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "objectmode"
    bl_label = "Arma Tools"
    bl_category = "Arma 3 Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    lastId = -1
    
    def safeAddRenamable(self, name, prop):
        if len(name) == 0: 
            return None
       
        for p in prop:
            if p.name == name:
                return None
        
        item = prop.add()
        item.name = name
        return item 
 
    def fillList(self, guiProps):
        # Fill the renamable list
        guiProps.renamableList.clear()
            
        mats = bpy.data.materials
            
        for mat in mats:
            self.safeAddRenamable(mat.armaMatProps.texture, guiProps.renamableList)
            self.safeAddRenamable(mat.armaMatProps.rvMat, guiProps.renamableList)
            self.safeAddRenamable(mat.armaMatProps.colorString, guiProps.renamableList)
 
    def draw(self, context):
        layout = self.layout
        guiProps = context.window_manager.armaGUIProps
        col = layout.column(align=True)
        
        # Bulk Renamer
        split = col.split(factor=0.15)
        if guiProps.bulkRenamePanelOpen:
            split.prop(guiProps, "bulkRenamePanelOpen", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(guiProps, "bulkRenamePanelOpen", text="", icon='RIGHTARROW')
        split.operator("armatoolbox.bulk_rename", text = "Path Rename")
        
        # Bulk Renamer Settings
        if guiProps.bulkRenamePanelOpen:
            box = col.column(align=True).box().column()
            row = box.row()
            
            self.fillList(guiProps)
             
            row.template_list(listtype_name = "ATBX_UL_named_prop_list", 
                              dataptr = guiProps,
                              propname = "renamableList",
                              active_dataptr = guiProps,
                              active_propname="renamableListIndex",
                              list_id = "renamableList")
            
            
            if guiProps.renamableListIndex > -1 and guiProps.renamableList.__len__() > guiProps.renamableListIndex:
                guiProps.renameFrom = guiProps.renamableList[guiProps.renamableListIndex].name
                row = box.row()
                row.prop(guiProps, "renameFrom", text = "Rename From")
                row = box.row()
                row.prop(guiProps, "renameTo", text = "To")
            else:
                row = box.row()
                row.label(text = "Rename From")
                row = box.row()
                row.label(text = "To")
        
        # Bulk Renamer
        row = layout.row()
        col = row.column(align=True)
        split = col.split(factor=0.15)
        if guiProps.bulkReparentPanelOpen:
            split.prop(guiProps, "bulkReparentPanelOpen", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(guiProps, "bulkReparentPanelOpen", text="", icon='RIGHTARROW')
        split.operator("armatoolbox.bulk_reparent", text = "Change File Parent")
      
        # Bulk Reparent Settings
        if guiProps.bulkReparentPanelOpen:
            box = col.column(align=True).box().column()
            row = box.row()
            row = box.row()
            row.prop(guiProps, "parentFrom", text = "Change Parent From")
            row = box.row()
            row.prop(guiProps, "parentTo", text = "To")
            
        # Selection Renamer
        row = layout.row()
        col = row.column(align=True)
        split = col.split(factor=0.15)
        if guiProps.selectionRenamePanelOpen:
            split.prop(guiProps, "selectionRenamePanelOpen", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(guiProps, "selectionRenamePanelOpen", text="", icon='RIGHTARROW')
        split.operator("armatoolbox.bulk_rename_selection", text = "Rename selections / vertex groups")
        
        # Selection Renamer settings    
        if guiProps.selectionRenamePanelOpen:
            box = col.column(align=True).box().column()
            row = box.row()
            row = box.row()
            row.prop(guiProps, "renameSelectionFrom", text = "Rename Selection From")
            row = box.row()
            row.prop(guiProps, "renameSelectionTo", text = "To")   
        
        # Hitpoint Creator
        row = layout.row()
        col = row.column(align=True)
        split = col.split(factor=0.15)
        if guiProps.hitpointCreatorPanelOpen:
            split.prop(guiProps, "hitpointCreatorPanelOpen", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(guiProps, "hitpointCreatorPanelOpen", text="", icon='RIGHTARROW')
        split.operator("armatoolbox.hitpoint_creator", text = "Create Hitpoint Cloud")
        
        # Hitpoint Creator Settings
        if guiProps.hitpointCreatorPanelOpen:
            box = col.column(align=True).box().column()
            row = box.row()
            row = box.row()
            row.prop(guiProps, "hpCreatorSelectionName", text = "Selection Name")
            row = box.row()
            row.prop(guiProps, "hpCreatorRadius", text = "Sphere Radius") 
          
        # Component Creator
        row = layout.row()
        row.operator("armatoolbox.create_components", text = "Create Geometry Components")

        # Tessalte non-quads
        row = layout.row()
        row.operator("armatoolbox.ensure_quads", text = "Tesselate all non-quads")

class ATBX_PT_relocation_tool_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "objectmode"
    bl_label = "Arma Relocation Tools"
    bl_category = "Arma 3 Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        guiProps = context.window_manager.armaGUIProps

        layout.operator("armatoolbox.rvmatrelocator", text = "Relocate external RVMat")
        layout.prop(guiProps, "rvmatRelocFile", text = "Relocate RVMat")
        layout.prop(guiProps, "rvmatOutputFolder", text = "Output Folder")
        layout.prop(guiProps, "matPrefixFolder", text = "Search Prefix")
        layout.separator()

class ATBX_PT_material_relocation_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Arma Material Relocation"
    bl_category = "Arma 3 Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        guiProps = context.window_manager.armaGUIProps
        layout.prop(guiProps, "matOutputFolder", text = "Output Folder")
        layout.prop(guiProps, "matPrefixFolder", text = "Search Prefix")
        layout.prop(guiProps, "matAutoHandleRV", text = "Automatically translate RVMat")
        data = bpy.data
        materials = data.materials
        
        texNames = []
        matNames = []
        
        for mat in materials:
            matName, texName = RVMatTools.mt_getMaterialInfo(mat)
            if len(texName) > 0 and texName not in texNames and texName[0] is not "#":
                texNames.append(texName)
            if len(matName)> 0 and matName not in matNames:
                matNames.append(matName)
            
        for tex in texNames:
            box = layout.box()
            row = box.row()
            row.label(text = tex)
            p = row.operator("armatoolbox.materialrelocator", text = "Relocate")
            p.texture = tex
            p.material = ""
            
        for mat in matNames:    
            box = layout.box()
            row = box.row()
            row.label(text = mat)
            p = row.operator("armatoolbox.materialrelocator", text = "Relocate")
            p.texture = ""
            p.material = mat

def createToggleBox(context, layout, propName, label, openOp = None):
    box = layout.box()
    row = box.row()
    guiProp = context.window_manager.armaGUIProps
    
    if guiProp.is_property_set(propName) == True and guiProp[propName] == True:
        toggle = row.operator("armatoolbox.toggleguiprop", icon="TRIA_DOWN", emboss=False)
        toggle.prop = propName
        if openOp == None:
            row.label(text = label)
        else:
            row.operator(openOp, text = label)
    else:
        toggle = row.operator("armatoolbox.toggleguiprop", icon="TRIA_RIGHT", emboss=False)
        toggle.prop = propName
        row.label(text = label)
        
    return box

class ATBX_PT_proxy_tools_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Proxy Tools"
    bl_category = "Arma 3 Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        obj = context.active_object
        guiProp = context.window_manager.armaGUIProps
        layout = self.layout
        row = layout.row()
        box = createToggleBox(context, row, "mapOpen", "Join as Proxy", "armatoolbox.joinasproxy")
        if guiProp.mapOpen == True:
            row = box.row()
            row.prop(guiProp, "mapProxyObject", text="Path")
            row = box.row()
            row.prop(guiProp, "mapProxyIndex",  text="Index")
            row = box.row()
            row.prop(guiProp, "mapProxyDelete", text="Delete source objects")
            row = box.row()
            bx = row.box()
            bx.label(text = "Enclose in selection")
            bx.prop(guiProp, "mapProxyEnclose", text="(Empty for none)")
        
        layout.separator()
        
        layout.operator("armatoolbox.proxypathchanger", text = "Proxy Path Change")
        layout.prop(guiProp, "proxyPathFrom", text = "Proxy path from")
        layout.prop(guiProp, "proxyPathTo", text = "Proxy path to")
        layout.separator()               

class ATBX_PT_hf_properties_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Arma 3"
    bl_label = "Arma Heightfield Properties"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        ## Visible when there is a selected object, it is a mesh
        obj = context.active_object
       
        return (obj 
            and obj.select_get() == True
            and (obj.type == "MESH" or obj.type == "ARMATURE") )
        
    def draw_header(self, context):
        obj = context.active_object
        hrp = obj.armaHFProps

        self.layout.prop(hrp, "isHeightfield", text="")
        
    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        self.enable = obj.select_get()
        
        hrp = obj.armaHFProps
        layout.active = hrp.isHeightfield
        if obj.type == "MESH" and hrp.isHeightfield:
            row = layout.row()
            row.prop(hrp, "cellSize", text = "Cell Size")
            
            row = layout.row()
            row.prop(hrp, "northing", text = "Northing")
            
            row = layout.row()
            row.prop(hrp, "easting", text = "Easting")
            
            row = layout.row()
            row.prop(hrp, "undefVal", text = "NODATA_value")
            
            verts = len(obj.data.vertices)
            verts = sqrt(verts)
            row = layout.row()
            row.label(text = "rows/cols: " + str(int(verts)))

### TODO
class ATBX_PT_selection_maker(bpy.types.Panel):
    bl_label = "Arma Toolbox: Hidden Selection Maker"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        obj = context.active_object
        arma = obj.armaObjProps
        
        return context.active_object.active_material!=None and arma.isArmaObject == True

    def draw(self, context):
        guiProps = context.window_manager.armaGUIProps
        obj = bpy.context.active_object
        layout = self.layout
        layout.prop(guiProps, "hiddenSelectionName", text="Hidden Selection")            

class ATBX_PT_nass_tools_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Mass Tools"
    bl_category = "Arma 3 Tools"
    
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
        
    def draw(self, context):
        obj = context.active_object
        guiProp = context.window_manager.armaGUIProps
        layout = self.layout
        row = layout.row()

        guiProps = context.window_manager.armaGUIProps
                
        row = layout.row()
        row.prop(guiProps, "vertexWeight", text = "Weight To Set")
        layout.operator("armatoolbox.setmass", text = "Set Mass on selected")
        layout.operator("armatoolbox.distmass", text = "Distribute Mass to selected")



panel_classes = (
    ATBX_PT_properties_panel,
    ATBX_PT_proxy_panel,
    ATBX_PT_material_settings_panel,
    ATBX_PT_weight_tool_panel,
    ATBX_PT_tool_panel,
    ATBX_PT_relocation_tool_panel,
    ATBX_PT_material_relocation_panel,
    ATBX_PT_proxy_tools_panel,
    ATBX_PT_hf_properties_panel,
    ATBX_PT_selection_maker,
    ATBX_PT_nass_tools_panel,
)


def register():
    from bpy.utils import register_class
    for c in panel_classes:
        register_class(c)

def unregister():
    from bpy.utils import unregister_class
    for c in panel_classes:
        unregister_class(c)