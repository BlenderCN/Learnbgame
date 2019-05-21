import bpy

#Panel
class VIEW3D_PT_jet_step6(bpy.types.Panel):
    bl_label = "6. Bake Sets Creation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "bake_sets_creation", text="", icon="INFO")

    def draw_list(self, list_prop, list_name, layout, tuple_buttons=(True, True, True, True)):
        box = layout.box()
        row = box.row()

        split = row.split(percentage=0.6)
        split.label(text=list_name + ' contents')
        split = split.split()
        split.prop(list_prop, "obj_list")

        row = box.row()
        row.template_list("DATA_UL_jet_list_" + list_name, "",
                          list_prop, 'obj_list',
                          list_prop, 'obj_list_index',
                          rows=1, maxrows=5)

        has_objs = len(list_prop.obj_list)>0

        col = box.column(align=True)
        row = col.row(align=True)
        if tuple_buttons[0]:
            col_assign = row.column(align=True)
            col_assign.operator(list_name + "_obj_list_add.btn", text="Assign")
            col_remove = row.column(align=True)
            col_remove.enabled = has_objs
            col_remove.operator(list_name + "_obj_list_remove.btn", text="Remove")

        if tuple_buttons[1]:
            row = col.row(align=True)
            row.enabled = has_objs
            row.operator(list_name + "_obj_list_clear.btn", text="Clear")

        if tuple_buttons[2]:
            row = col.row(align=True)
            row.enabled = has_objs
            row.operator(list_name + "_obj_list_select.btn", text="Select All").select = True
            row.operator(list_name + "_obj_list_select.btn", text="Deselect All").select = False

        if tuple_buttons[3]:
            row = col.row(align=True)
            row.enabled = has_objs
            row.operator(list_name + "_obj_list_hide.btn", text="Show All").hide = False
            row.operator(list_name + "_obj_list_hide.btn", text="Hide All").hide = True


    def draw(self, context):
        layout = self.layout

        low_res = context.scene.Jet.list_low_res
        self.draw_list(low_res, "low_res", layout, tuple_buttons=(True, False, True, True))

        items = len(low_res.obj_list)
        idx = low_res.obj_list_index
        if items > 0:
            layout.prop(low_res, "select_hi_rest_list", "Select Hi-Res automatically", icon="TRIA_DOWN")
            idx = idx if idx < items else 0

            hi_res = low_res.obj_list[idx].list_high_res
            self.draw_list(hi_res, "hi_res", layout, tuple_buttons=(True, False, True, True))


#Operators

#col.operator("jet_add_sufix.btn", text="Add Sufix '_Low'").sufix = "_Low"
#col.operator("jet_add_sufix.btn", text="Add Sufix '_High'").sufix = "_High"
#class VIEW3D_OT_jet_add_sufix(bpy.types.Operator):
#    bl_idname = "jet_add_sufix.btn"
#    bl_label = "Add sufix"
#    bl_description = "Add sufix to the selected objects"
#
#    sufix = bpy.props.StringProperty(name="sufix",default="_Low")
#
#    def execute(self, context):
#        for obj in context.selected_objects:
#            if self.sufix in obj.name: continue
#            obj.name = obj.name + self.sufix
#        return {'FINISHED'}

