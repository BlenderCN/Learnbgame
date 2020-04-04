bl_info = {
    "name": "Mesh Extract",
    "author": "Ian Lloyd Dela Cruz, Roberto Roch Diago",
    "version": (1, 2),
    "blender": (2, 5, 5),
    "location": "3d View > Tool shelf",
    "description": "Simple Sculpting SubTool Operator",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
from bpy.props import *
import random

def edgemask():

    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.space_data.show_occlude_wire = True
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.select_more()
    bpy.ops.mesh.select_all(action = 'INVERT')
    bpy.ops.mesh.hide(unselected=False)
    bpy.ops.object.mode_set(mode='SCULPT')
    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=1)
    bpy.ops.paint.hide_show(action='SHOW', area='ALL')

def extractfaces():

    bpy.ops.paint.hide_show(area='MASKED')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.space_data.show_occlude_wire = True
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.mesh.separate()
    bpy.ops.mesh.reveal()
    bpy.ops.object.mode_set(mode='SCULPT')
    edgemask()

def weldfaces():
    
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.space_data.show_occlude_wire = True
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.select_more()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode='SCULPT')
    bpy.ops.paint.mask_flood_fill()
    
class MeshExtractOperator(bpy.types.Operator):
    '''Exracts Sculpt Mesh'''
    bl_idname = "mesh.extract"
    bl_label = "Mesh Exract"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    
    def execute(self, context):
        currobj = context.active_object
        if currobj.users_group == ():
            idcol = "%06x" % random.randint(0,0xFFFFFF)
            gflag = currobj.name + "_" + idcol + "_group"
            if bpy.data.groups.find(gflag) == -1:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.group.create(name=gflag)
                bpy.ops.object.mode_set(mode='SCULPT')
            else:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.group_link(group = gflag)
                bpy.ops.object.mode_set(mode='SCULPT')                   
             
        if context.active_object.mode == 'SCULPT':    
            if context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
                extractfaces()
                bpy.ops.sculpt.dynamic_topology_toggle()
            else:                           
                extractfaces()

        return {'FINISHED'}
    
class MeshExtractSolidifyOperator(bpy.types.Operator):
    '''Exracts New Sculpt Mesh And Solidify'''
    bl_idname = "mesh.solidfaces"
    bl_label = "Mesh Extract and Solidify"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    
    def draw(self, context): 
        if context.active_object.mode != 'SCULPT':   
            wm = context.window_manager
            layout = self.layout
            layout.prop(wm, "solidthickness", text="Thickness")
            layout.prop(wm, "smoothmesh", text="Smooth")
    
    def execute(self, context): 
        wn = context.window_manager
        currobj = context.active_object
        if context.active_object.mode == 'SCULPT':    
            if context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.duplicate()
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.hide_show(area='MASKED')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.space_data.show_occlude_wire = True
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.delete()
                bpy.ops.mesh.reveal()
                bpy.ops.transform.shrink_fatten(value=0.05)
                bpy.context.scene.objects.active.modifiers.new( 'solid', 'SOLIDIFY')
                bpy.context.scene.objects.active.modifiers['solid'].offset = 1
                bpy.context.scene.objects.active.modifiers['solid'].thickness = wn.solidthickness
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="solid")
                if currobj.users_group != ():
                   bpy.ops.group.objects_remove_all()
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.vertices_smooth(repeat=wn.smoothmesh)
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.mask_flood_fill()
                bpy.ops.sculpt.dynamic_topology_toggle()
            else:                           
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.duplicate()
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.hide_show(area='MASKED')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.space_data.show_occlude_wire = True
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.delete()
                bpy.ops.mesh.reveal()
                bpy.ops.transform.shrink_fatten(value=0.05)
                bpy.context.scene.objects.active.modifiers.new( 'solid', 'SOLIDIFY')
                bpy.context.scene.objects.active.modifiers['solid'].offset = 1
                bpy.context.scene.objects.active.modifiers['solid'].thickness = wn.solidthickness
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="solid")
                if currobj.users_group != ():
                    bpy.ops.group.objects_remove_all()
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.vertices_smooth(repeat=wn.smoothmesh)
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.mask_flood_fill()

        return {'FINISHED'}

class MeshEdgeMaskOperator(bpy.types.Operator):
    '''Edge Masks Sculpt Mesh'''
    bl_idname = "mesh.edgemask"
    bl_label = "Mesh Edge Mask"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    
    def execute(self, context): 
        if context.active_object.mode == 'SCULPT':    
            if context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
                edgemask()
                bpy.ops.sculpt.dynamic_topology_toggle()
            else:                           
                edgemask()

        return {'FINISHED'}

class MeshWeldOperator(bpy.types.Operator):
    '''Unifies previously extracted or joins sculpt meshes'''
    bl_idname = "mesh.weld"
    bl_label = "Mesh Weld"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)>1

    def execute(self, context):
        # add a union boolean modifier
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
            if SelectedObject != activeObj :
                if context.active_object.mode == 'OBJECT':
                    weldfaces()
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                if context.active_object.mode == 'SCULPT':
                    if context.sculpt_object.use_dynamic_topology_sculpting:
                        bpy.ops.sculpt.dynamic_topology_toggle()
                        weldfaces()
                        bpy.ops.sculpt.dynamic_topology_toggle()
                    else:
                        weldfaces()
                        bpy.ops.object.mode_set(mode='SCULPT')

                bpy.context.scene.objects.active = activeObj
        
        return {'FINISHED'}
    
class AdjustValues(bpy.types.Operator):
    bl_idname = "adjust.values"
    bl_label = "Adjust Values for Solid and Offset"

    def execute(self, context):
        bpy.ops.sculpt.val('INVOKE_DEFAULT')
        return {'FINISHED'}

class SculptValues(bpy.types.Operator):
    bl_idname = "sculpt.val"
    bl_label = "Adjust Values for Solid & Offset"

    my_float = bpy.props.FloatProperty(name="Solid Thickness", min = -1, max = 1)
    my_int = bpy.props.IntProperty(name="Solid Smooth", min = 0, max = 20)
    my_float1 = bpy.props.FloatProperty(name="Offset Thickness", min = -1, max = 1,)
    my_int1 = bpy.props.IntProperty(name="Offset Smooth", min = 0, max = 20,)

    def execute(self, context):
        wm = context.window_manager
        message = "Popup Values: %f, %d, %e, %g" % \
            (self.my_float, self.my_int, self.my_float1, self.my_int1)
        #
        wm.offsetthickness = self.my_float1
        wm.smoothoffset = self.my_int1
        wm.solidthickness = self.my_float
        wm.smoothmesh = self.my_int
        self.report({'INFO'}, message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        self.my_float1 = wm.offsetthickness
        self.my_int1 = wm.smoothoffset
        self.my_float = wm.solidthickness
        self.my_int = wm.smoothmesh
        return wm.invoke_props_dialog(self)

class MeshOffsetFacesOperator(bpy.types.Operator):
    '''Offsets masked area in or out'''
    bl_idname = "mesh.offsetfaces"
    bl_label = "Mesh Offset Faces"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    
    def draw(self, context): 
        if context.active_object.mode != 'SCULPT':   
            wm = context.window_manager
            layout = self.layout
            layout.prop(wm, "offsetthickness", text="Thickness")
            layout.prop(wm, "smoothoffset", text="Smooth")
    
    def execute(self, context): 
        wn = context.window_manager
        #bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        if context.active_object.mode == 'SCULPT':    
            if context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
                bpy.ops.paint.mask_flood_fill(mode='INVERT')
                bpy.ops.paint.hide_show(area='MASKED')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.space_data.show_occlude_wire = True
                bpy.ops.mesh.select_mode(type='EDGE')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.select_more()
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.normals_make_consistent(inside=True)
                bpy.ops.transform.shrink_fatten(value=wn.offsetthickness)
                bpy.ops.mesh.vertices_smooth(repeat=wn.smoothoffset)
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.hide_show(action='SHOW', area='ALL')
                bpy.ops.paint.mask_flood_fill()
                bpy.ops.sculpt.dynamic_topology_toggle()
            else:                           
                bpy.ops.paint.mask_flood_fill(mode='INVERT')
                bpy.ops.paint.hide_show(area='MASKED')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.space_data.show_occlude_wire = True
                bpy.ops.mesh.select_mode(type='EDGE')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.select_more()
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.normals_make_consistent(inside=True)                
                bpy.ops.transform.shrink_fatten(value=wn.offsetthickness)
                bpy.ops.mesh.vertices_smooth(repeat=wn.smoothoffset)
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.hide_show(action='SHOW', area='ALL')
                bpy.ops.paint.mask_flood_fill()
        return {'FINISHED'}
    
class MeshExtractPanel(bpy.types.Panel):
    """UI panel for Mesh Extraction Buttons"""
    bl_label = "Mesh Extract"
    bl_idname = "OBJECT_PT_extract"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Sculpt"

    def draw(self, context):
        layout = self.layout

        wm = context.window_manager
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'

        try:
            row.operator("mesh.extract", text='Extract')
        except:
            pass
        
        row2 = layout.row(align=True)
        row2.alignment = 'EXPAND'
        row2.operator("mesh.solidfaces", text="Extract New & Solidify")
        row2.prop(wm, 'solidthickness', text="Thickness")
        row2.prop(wm, 'smoothmesh', text="Smooth")        
        row3 = layout.row(align=True)
        row3.alignment = 'EXPAND'
        row3.operator("mesh.edgemask", text="Edge Mask")
        row4 = layout.row(align=True)
        row4.alignment = 'EXPAND'
        row4.operator("mesh.weld", text="Weld")
        row5 = layout.row(align=True)
        row5.alignment = 'EXPAND'
        row5.operator("mesh.offsetfaces", text="Offset Masked")
        row5.prop(wm, 'offsetthickness', text="Thickness")
        row5.prop(wm, 'smoothoffset', text="Smooth")
        
#Select Object
class MeshListToggle(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "data.call"
    bl_label = "Mesh List Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    mesh_name = bpy.props.StringProperty(name = "Sculpt Object")
    autozoom = bpy.props.BoolProperty(name = "Autozoom", description = "Autozoom: center object in view when selected", default = False)
    show_all = bpy.props.BoolProperty(name = "Show All Hidden", description = "Show All Hidden", default = False)
    stay_iso = bpy.props.BoolProperty(name = "Isolate New Select", description = "Localize new selection in view", default = False)
    multi_select = bpy.props.BoolProperty(name = "Multiselection", description = "Toggle Object Multiselection", default = False)
    x_ray = bpy.props.BoolProperty(name = "X-Ray Active", description = "X-Ray Current Selection", default = False)

    layerN = bpy.props.IntProperty(name = "Active Layer")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        layerN = self.layerN
        wm = context.window_manager
                        
        bpy.data.objects[bpy.context.active_object.name].show_x_ray = False
        if bpy.context.active_object.layers_local_view[layerN] == True:
            bpy.ops.view3d.localview()
        if bpy.data.objects[self.mesh_name].hide == True:
            bpy.data.objects[self.mesh_name].hide = False

        bpy.ops.object.mode_set(mode='OBJECT')
        if self.show_all == True:
            bpy.ops.object.hide_view_clear()

        if self.multi_select == False:
            bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects[self.mesh_name].select = True
        bpy.context.scene.objects.active = bpy.context.scene.objects[self.mesh_name]
        if self.x_ray == True:
            bpy.data.objects[bpy.context.active_object.name].show_x_ray = True
        if self.autozoom == True:
            bpy.ops.view3d.view_selected()
        if self.stay_iso == True:
            bpy.ops.view3d.localview()
        bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}
    
#Ninja Function
class IsolateMeshToggle(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "ninja.mesh"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    ninja_fade = bpy.props.BoolProperty(name = "Hide/Show", description = "Toggle Visibility ON/OFF", default = False)
    ninja_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.data.objects[self.ninja_name].hide = self.ninja_fade 
        return {'FINISHED'}
    
#Weld from Selection Function
class WeldSelOther(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weldsel.other"
    bl_label = "Weld Select Another Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    mesh_name = bpy.props.StringProperty()
    layerN = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        layerN = self.layerN
        toglview = False
        
        if bpy.context.active_object.layers_local_view[layerN] == True:
            bpy.ops.view3d.localview()
            toglview = True
        for oldsel in bpy.context.selected_objects:
            if bpy.context.active_object.name != oldsel.name:
                bpy.context.scene.objects[oldsel.name].select = False
        
        bpy.context.scene.objects[self.mesh_name].select = True
        if bpy.data.objects[self.mesh_name].hide == True:
            bpy.data.objects[self.mesh_name].hide = False
        bpy.ops.mesh.weld()
        if toglview == True:
            bpy.ops.view3d.localview()
        bpy.ops.mesh.edgemask()
        return {'FINISHED'}
    
#Mesh List Menu(Main)
class MeshListMenu(bpy.types.Menu):
    bl_label = ""
    bl_idname = "OBJECT_MT_meshlist_menu"
    
    def draw(self, context):
               
        layout = self.layout
        view_3d = context.area.spaces.active
        scene = context.scene
        active = scene.active_layer
        wm = context.window_manager
        
        currobj = context.active_object
        activel = 0
        
        split = layout.split(align=True)
        
        col1 = split.column(align=True)
        col1.alignment = 'EXPAND'
        col1.label("Mesh Object List:")
        for obj in bpy.context.scene.objects:
            for i in range(0,19):
                if bpy.context.scene.objects[currobj.name].layers[i] == True:
                    activel = i
            if context.scene.objects[obj.name].layers[activel]:
                if bpy.data.objects[obj.name].type == "MESH":
                    if bpy.context.active_object.name != obj.name:
                        #group query
                        if currobj.users_group != ():
                            gsearch = currobj.users_group[0].name
                            if obj.users_group != ():
                                if obj.users_group[0].name != gsearch:
                                    myicon = 'MESH_DATA'
                                else:
                                    myicon = "LINKED"
                            else:
                                myicon = 'MESH_DATA'
                        else:
                            myicon = 'MESH_DATA'
                    else:
                        myicon = 'OUTLINER_OB_MESH'
                    if obj.select == True:
                        selc = " *"
                    else:
                        selc = ""     
                    col1.operator("data.call", text = obj.name + selc, icon = myicon).mesh_name = obj.name
        col1.label("List Options")
        col1.prop(wm, "menu_type", text="")
                            
        if bpy.context.window_manager.menu_type == "Active":
            col2 = split.column(align=True)
            col2.alignment = 'LEFT'
            col2.label(text = "Active Mesh Functions:")
            actobj = context.active_object
            col2.prop(actobj, "name", text = "", icon = "OBJECT_DATA")
            col2.prop(wm, 'tricount', text="Show Tri Count") 
            if bpy.context.window_manager.tricount == True:
                info_str = ""
                tris = 0
    
                for p in currobj.data.polygons:
                    count = p.loop_total
                    if count == 3:
                        tris += 1

                info_str = "%i" % (tris)
                col2.label("Tri Count: " + " " + info_str)
            col2.prop(bpy.data.objects[currobj.name], "show_x_ray", text = "X-Ray")
            col2.operator("view3d.localview", text = "Local View")
        #ninja functions, margins how!!!?
        if bpy.context.window_manager.menu_type == "Ninja":
            col3 = split.column(align=True)
            col3.alignment = 'LEFT'
            col3.label("Ninja Functions:")
            for obj in bpy.context.scene.objects:
               if context.scene.objects[obj.name].layers[activel]:
                    if bpy.data.objects[obj.name].type == "MESH":
                        if bpy.context.active_object.name != obj.name:
                            if obj.hide == True:
                                props = col3.operator("ninja.mesh", text = "Show", icon = 'VISIBLE_IPO_OFF')
                                props.ninja_fade = False
                                props.ninja_name = obj.name
                            else:
                                props = col3.operator("ninja.mesh", text = "Hide", icon = 'VISIBLE_IPO_ON')
                                props.ninja_fade = True
                                props.ninja_name = obj.name
                        else:
                            col3.label("")
            col3.label("")
        # weldto list 
        if bpy.context.window_manager.menu_type == "Weld":
            col4 = split.column(align=True)
            col4.alignment = 'LEFT'
            col4.label("Weld to Options:")
            for obj in bpy.context.scene.objects:
                if context.scene.objects[obj.name].layers[activel]:
                    if bpy.data.objects[obj.name].type == "MESH":
                        if bpy.context.active_object.name != obj.name:
                            if currobj.users_group != ():
                                gsearch = currobj.users_group[0].name
                                if obj.users_group != ():
                                    if obj.users_group[0].name != gsearch:
                                        myicon = 'UNLINKED'
                                    else:
                                        myicon = "LINKED"
                                else:
                                    myicon = 'UNLINKED'
                            else:
                                myicon = 'UNLINKED'
                            col4.operator("weldsel.other", text = obj.name, icon=myicon).mesh_name = obj.name
                        else:
                            col4.label("")
            col4.label("")
        #Mask Function
        if bpy.context.window_manager.menu_type == "Mask":
            col5 = split.column(align=True)
            col5.alignment = 'LEFT'
            col5.label(text = "Mask Functions:")
            col5.operator("mesh.extract", text="Sculpt Extract Mask")
            col5.operator("mesh.edgemask", text="Edge Mask")
            col5.operator("mesh.solidfaces", text="Extract New & Solidify")
            col5.operator("mesh.offsetfaces", text="Offset Masked")
            col5.separator()
            col5.operator("adjust.values", text = "Values for Solid & Offset")
            col5.separator()
            col5.operator("paint.mask_flood_fill", text="Clear Mask").value=0
             
    #def draw_item(self, context):
    #    layout = self.layout
    #    layout.menu(CustomMenu.bl_idname)
        
addon_keymaps = []
              
def register():
    bpy.utils.register_module(__name__)
    
    # add keymap entry
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(\
        name='Sculpt', space_type='EMPTY')
    kmi = km.keymap_items.new("wm.call_menu", 'Q', 'PRESS')
    kmi.properties.name = 'OBJECT_MT_meshlist_menu' 
    addon_keymaps.append(km)   
    
    
    bpy.types.WindowManager.menu_type = EnumProperty(name="Select Menu:",
                             items = (("Ninja","Ninja","Show/Hide Options","VISIBLE_IPO_ON",1),
                                      ("Weld","Weld to","Weld to Mesh List","LINKED",2),
                                      ("Active","Active Mesh","Show Active Mesh Options","OBJECT_DATA",3),
                                      ("Mask","Mask","Show Active Mesh Options","MOD_MASK",4),
                                      ("None","Only List","Show Only Mesh List","MESH_DATA",5)),                                      
                             default = "None")
    
    bpy.types.WindowManager.smokebomb= BoolProperty(default=False)
    bpy.types.WindowManager.weldto= BoolProperty(default=False)
    
    bpy.types.WindowManager.tricount= BoolProperty(default=False)
    
    #bpy.types.WindowManager.unibools = BoolProperty(default=False)
    
    bpy.types.WindowManager.solidthickness= FloatProperty(
    min = -1, max = 1,
    default = 0.1)
    
    bpy.types.WindowManager.smoothmesh= IntProperty(
    min = 0, max = 20,
    default = 1)
    
    bpy.types.WindowManager.offsetthickness= FloatProperty(
    min = -1, max = 1,
    default = 0.1)
    
    bpy.types.WindowManager.smoothoffset= IntProperty(
    min = 0, max = 20,
    default = 1)    
   
def unregister():
    bpy.utils.unregister_module(__name__)
    
    # remove keymap entry
    for km in addon_keymaps:
        bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()