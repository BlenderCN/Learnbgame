bl_info = {
    "name": "HP Boolean Pie",
    "description": "",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }
import bpy
from bpy.types import Menu
#bpy.context.view_layer.objects.active
# Boolean Pie
class VIEW3D_MT_HP_Boolean(Menu):
    bl_idname = "HP_MT_boolean"
    bl_label = "HP Boolean"
    def draw(self, context):

        layout = self.layout
        pie = layout.menu_pie()
        split = pie.split()
        col = split.column(align=True)
        #Plain ol Booleans
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Add")
        prop.bool_operation = 'UNION'
        prop.cutline = 'NO'
        prop.insetted = 'NO'
        prop.live = 'NO'
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Intersect")
        prop.bool_operation = 'INTERSECT'
        prop.cutline = 'NO'
        prop.insetted = 'NO'
        prop.live = 'NO'        
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Subtract")
        prop.bool_operation = 'DIFFERENCE'
        prop.cutline = 'NO'
        prop.insetted = 'NO'
        prop.live = 'NO'
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("view3d.hp_boolean_slice", text="Slice")
        #Live Booleans
        split = pie.split()
        col = split.column(align=True)
        
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Live Add")
        prop.bool_operation = 'UNION'
        prop.live = 'YES'
        prop.cutline = 'NO'
        prop.insetted = 'NO'
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Live Intersect")
        prop.bool_operation = 'INTERSECT'
        prop.cutline = 'NO'
        prop.insetted = 'NO'
        prop.live = 'YES'       
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Live Subtract")
        prop.bool_operation = 'DIFFERENCE'
        prop.live = 'YES'
        prop.cutline = 'NO'
        prop.insetted = 'NO'
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Live Subtract Inset")
        prop.bool_operation = 'DIFFERENCE'
        prop.live = 'YES'
        prop.cutline = 'NO'
        prop.insetted = 'YES'
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.hp_boolean_live", text="Live Cutline")
        prop.bool_operation = 'DIFFERENCE'
        prop.live = 'YES'
        prop.cutline = 'YES'
        prop.insetted = 'NO'        
        
        split = pie.split()
        col = split.column(align=True)
        
        row = col.row(align=True)
        row.scale_y=1.5  
        row.operator("view3d.hp_boolean_apply", text="Apply and Copy").dup = 'YES'
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("view3d.hp_boolean_apply", text="Apply").dup = 'NO'
        row = col.row(align=True)
        row.scale_y=1.5
        #row.operator("view3d.hp_boolean_toggle_bool_solver", text="Toggle Solver")
        pie.operator("view3d.hp_boolean_toggle_cutters", text="Toggle Cutters")

        
        
class HP_Boolean_Toggle_Cutters(bpy.types.Operator):
    bl_idname = "view3d.hp_boolean_toggle_cutters"
    bl_label = "hp_boolean_toggle_cutters"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if bpy.data.collections['Cutters'].hide_viewport:
            bpy.data.collections['Cutters'].hide_viewport = False
        
        else:
           bpy.data.collections['Cutters'].hide_viewport = True
        return {'FINISHED'}
#class HP_Boolean_Toggle_Solver(bpy.types.Operator):
#    bl_idname = "view3d.hp_boolean_toggle_bool_solver"
#    bl_label = "hp_boolean_toggle_cutters"
#    bl_options = {'REGISTER', 'UNDO'}
#    def execute(self, context):
#        sel = bpy.context.selected_objects
#        view_layer = bpy.context.view_layer
#        bases = [base for base in view_layer.objects if not base.name.startswith("Bool_Cutter") and base.type == 'MESH']
#        for ob in sel: 
#            #Get Cutters in Sel
#            if ob.name.startswith('Bool_Cutter'):
#                cutter = ob
#                for base in bases:
#                    for mod in base.modifiers: 
#                        if mod.name == cutter.name:
#                            if mod.solver == 'BMESH':
#                                mod.solver = 'CARVE'
#                            else:
#                                mod.solver = 'BMESH'
#            else:               
#                base = ob
#                for mod in base.modifiers: 
#                    if mod.name.startswith ('Bool_Cutter'):
#                        if mod.solver == 'BMESH':
#                            mod.solver = 'CARVE'
#                        else:
#                            mod.solver = 'BMESH'
#        return {'FINISHED'}
class HP_Boolean_Live(bpy.types.Operator):
    bl_idname = "view3d.hp_boolean_live"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    cutline: bpy.props.StringProperty(name='Cutline',default='NO')   
    live: bpy.props.StringProperty(name='Live',default='NO')   
    insetted: bpy.props.StringProperty(name='Insetted',default='NO')   
    displaytype: bpy.props.StringProperty(name="Display Type",default='WIRE')
    showbounds: bpy.props.BoolProperty(name="Display Type",default= False)
    bool_operation: bpy.props.StringProperty(name="Boolean Operation")
    bool_solver: bpy.props.StringProperty(name="Boolean Solver",default='BMESH')
    def execute(self, context):

        sel = bpy.context.selected_objects
        base = bpy.context.active_object
        view_layer = bpy.context.view_layer
        isedit = False
        mirror = False
        if len([m for m in bpy.context.object.modifiers if m.name == "Mirror Base"]) > 0:
            print('Base Mirrored')
            mirror = True
        if bpy.context.active_object.mode != 'OBJECT' and self.live == 'NO':
            bpy.ops.mesh.select_linked(delimit={'NORMAL'})
            bpy.ops.mesh.intersect_boolean(operation=self.bool_operation)
            return {'FINISHED'}
        def create_cutter(displaytype, insetted, showbounds):
            bpy.context.view_layer.objects.active = cutter
            cutter.name = "Bool_Cutter"
            if mirror == True:
                bpy.ops.view3d.mirror_toggle(type='Mirror Base')
                bpy.context.object.modifiers['Mirror Base'].show_viewport = True
                bpy.context.object.modifiers['Mirror Base'].show_render = True
                bpy.context.object.modifiers['Mirror Base'].use_clip = True
                bpy.context.object.modifiers['Mirror Base'].show_in_editmode = True
                bpy.context.object.modifiers['Mirror Base'].use_bisect_axis[0] = True
            view_layer_cutters = [obj for obj in view_layer.objects if obj.name.startswith("Bool_Cutter")]
            # for x in view_layer_cutters:
                # if x != cutter:
                    # bpy.ops.object.modifier_apply(apply_as='DATA', modifier=x.name)
            cutter.name = "Bool_Cutter_" + str(len(view_layer_cutters))
            if self.cutline == 'YES':
                cutter.modifiers.new('Cutline', "SOLIDIFY")
                bpy.context.object.modifiers['Cutline'].thickness = 0.02     
            if self.insetted == 'YES':
                base.select_set(state=False)
                cutter.select_set(state=True)
                for x in view_layer_cutters:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier = x.name)
                bpy.ops.object.duplicate()
                bpy.context.view_layer.objects.active.name = "Bool_Inset"
                inset = bpy.context.active_object
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                bpy.ops.transform.resize(value=(0.92, 0.92, 0.92), constraint_axis=(False, False, False), mirror=False, proportional='DISABLED')
                bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
                bpy.ops.object.editmode_toggle()      
                bpy.context.view_layer.objects.active = cutter
                bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
                bpy.context.object.constraints["Copy Transforms"].target = inset
                inset.select_set(state=True)
                bpy.context.view_layer.objects.active = inset
            cutter.display_type = self.displaytype
            cutter.show_bounds = self.showbounds
            cutter.select_set(state=False)
            
        def create_bool(bool_operation, live):
            Bool = base.modifiers.new(cutter.name, "BOOLEAN")
            Bool.object = cutter
            Bool.operation = bool_operation
            #Bool.solver = bool_solver
            base.select_set(state=True)
            bpy.context.view_layer.objects.active = base
            # for o in bpy.context.selected_objects:
                # bpy.context.view_layer.objects.active = o
                # if 0 == len([m for m in bpy.context.object.modifiers if m.type == "SUBSURF"]):
                    # bpy.ops.object.modifier_move_down(modifier="Mirror Base")
            if self.live == 'NO':
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.object.editmode_toggle()
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cutter.name)
                base.select_set(state=False)
                cutter.select_set(state=True)
                bpy.ops.object.delete(use_global=False)
                base.select_set(state=True)
                i = base.data.vertex_colors.active_index
                base.data.vertex_colors.active_index = i + 1
                bpy.ops.mesh.vertex_color_remove()

        if context.active_object.mode != 'OBJECT':
            isedit = True
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.editmode_toggle()
            sel = bpy.context.selected_objects                
        for cutter in sel:
            if cutter != base:
                create_cutter(self.displaytype, self.insetted, self.showbounds)
                create_bool(self.bool_operation, self.live)
        if isedit == True and self.live == 'NO':
            bpy.ops.object.editmode_toggle()
        if self.insetted == 'YES':
            base.select_set(state=False)  
            for x in bpy.context.selected_objects:
                bpy.context.view_layer.objects.active = x
                
        try:
            bpy.data.collections['Cutters']
        except:
            print('Creating Cutters Collection')
            Cutcol = bpy.data.collections.new("Cutters")
            bpy.context.scene.collection.children.link(Cutcol)
        cutters = [ob for ob in bpy.data.objects if ob.name.startswith("Bool_Cutter")]
        for cutter in cutters:
            try:
                bpy.data.collections['Cutters'].objects.link(cutter)
                try:
                    bpy.context.scene.collection.objects.unlink(cutter)
                except:
                    bpy.data.collections['Main'].objects.unlink(cutter)

            except:
                pass
        return {'FINISHED'}
class HP_Boolean_Slice(bpy.types.Operator):
    """slice"""
    bl_idname = "view3d.hp_boolean_slice"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def invoke(self, context, event):
        if bpy.context.mode=='OBJECT':
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()                 
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.join()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.vertex_group_select() 
            bpy.ops.mesh.select_all(action='INVERT')      
            bpy.ops.object.vertex_group_remove()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_assign()
        bpy.ops.mesh.intersect()
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_assign() 
        i = bpy.context.active_object.vertex_groups.active_index
        i = i-1
        bpy.context.active_object.vertex_groups.active_index = i
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_select()        
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.vertex_group_remove()
        bpy.ops.object.vertex_group_select()       
        bpy.ops.object.vertex_group_remove()
        return {'FINISHED'}

class HP_Boolean_Apply(bpy.types.Operator):
    bl_idname = "view3d.hp_boolean_apply" 
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    dup: bpy.props.StringProperty(name='Duplicate')
    def execute(self, context):
        def apply(dup):
            sel = bpy.context.selected_objects
            view_layer = bpy.context.view_layer
            view_layer_cutters = [obj for obj in view_layer.objects if obj.name.startswith("Bool_Cutter")]
            for ob in sel:
                if ob.name.startswith('Bool_Cutter'):
                    iscutter = True
                    cutter = ob
                    for base in view_layer.objects:
                        for mod in base.modifiers:
                            bpy.context.view_layer.objects.active = base
                            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cutter.name)
                    cutter.select_set(state=True)
                else:
                    base = ob
                    if self.dup == 'YES':
                        bpy.ops.object.duplicate()
                        clone = bpy.context.active_object
                        base.hide_render = True
                    for mod in base.modifiers:
                        cutter = bpy.context.view_layer.objects[mod.name]
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cutter.name)
                        if self.dup == 'YES':
                            cutter.hide_render = True
                            continue
                        cutter.select_set(state=True)
                        base.select_set(state=False)
                        bpy.ops.object.delete()
                        base.select_set(state=True)
            try:
                if iscutter == True:
                    bpy.ops.object.delete() 
                    bpy.context.active_object.select_set(state=True)
                    sel = bpy.context.selected_objects  
            except:
                pass  
        apply(self.dup)
        return {'FINISHED'}  

classes = (
    VIEW3D_MT_HP_Boolean,
    HP_Boolean_Toggle_Cutters,
    HP_Boolean_Live,
    HP_Boolean_Slice,
    HP_Boolean_Apply,
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass

if __name__ == "__main__":
    register() 
