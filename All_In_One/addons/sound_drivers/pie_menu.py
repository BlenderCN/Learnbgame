import bpy
from bpy.types import Menu
from bpy.types import UILayout, Operator 
from bpy.utils import register_class, unregister_class
from sound_drivers.icons import icon_value, enum_item_icon
from sound_drivers.sounddriver import DriverManager_DriverOp

def get_var_dic(self):
    ''' driver var by target dictionary '''
    var_dic = {}
    for var in self.fcurve.driver.variables:
        target = var.targets[0]
        name = "None" if not target.id else target.id.name
        icon = 0 if not target.id else icon_value(target.id)
        target_dic = var_dic.setdefault(name, {})
        if icon:
            icon = target_dic.setdefault("icon", icon)
        variables = target_dic.setdefault("variables", {})
        
        type_dic = variables.setdefault(var.type, [])
        
        type_dic.append(var.name)
        type_dic.sort(key=lambda r: (r[0], (r[1] if len(r) > 1 else r[0], len(r), r)))
    rubbish_vars = var_dic.get("None")
    if rubbish_vars:
        rubbish_vars = var_dic.pop("None")    
    return var_dic, rubbish_vars
        
def draw_variable(self, var, layout):
    #var = self.variables.get(name)
    row = layout.row(align=True)
    row.scale_y = 0.5
    target = var.targets[0]

    row.label(var.name.ljust(6), icon='BLANK1')
    op = row.operator("dm.edit_driver_var", text="edit", emboss=True)
    op.varname = var.name
    op.dindex = self.index
    
    if target.id:
        if var.type == 'SINGLE_PROP':
            if hasattr(target.id, target.data_path):
                row.prop(target.id, target.data_path, slider=True, text="")
            else:
                row.label("invalid dp")
        else:
            row.label("XXX")
    else:
        row.label("invalid")
    op = row.operator("dm.remove_driver_var", text="", icon="X")
    op.varname = var.name
    op.dindex = self.index
    row = layout.row()
    locs =  getattr(self, "locs", {})
    if var.name not in locs:
        op = row.operator("driver.edit")
        op.dindex = self.index
        op.update = True


class PieMenuDriverPopup(bpy.types.Operator, DriverManager_DriverOp):
    """Edit Driver Details"""
    bl_idname = "driver.popup_driver"
    bl_label = "Driver Manager"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        '''
        if wm is None:

            # try and start the b***
            bpy.ops.wm.drivermanager_update('INVOKE_DEFAULT')
            wm = context.window_manager
        '''
        wm.update_dm = not wm.update_dm
        d = self.get_driver()
        print("************", get_var_dic(d))
        if d:         
            bpy.ops.driver.edit('INVOKE_DEFAULT', dindex=d.index, toggle=True)
        return(wm.invoke_props_dialog(self))
        
    def draw_header(self, context):
        self.layout.draw("FUCK")
    def draw(self, context):
        d = self.get_driver()
        v0 = d.fcurve.driver.variables[0]
        layout = self.layout
        if d:        
            scene = context.scene    
            gui = d.driver_gui(scene)
            '''
            if gui is not None:
                self.layout.prop(gui, "gui_types",
                             text="",
                             expand=True,
                             icon_only=True)
            '''
            d.draw_slider(self.layout)
            #d.edit(self.layout, context)
            print("VARIABLE DIC", d.vd)
            target_dic, rubbish_vars = get_var_dic(d)
            row = layout.row(align=True)
            row.label("Variables")
            op = row.operator("driver.new_var_popup", text="", icon='ZOOMIN')
            op.dindex = d.index
            if target_dic:                
                for targetname, data in target_dic.items():
                    if targetname == "None":
                        continue
                    variables = data["variables"]
                    layout.label(targetname, icon_value=data.get("icon"))
                    col = layout.column()
                    #col.scale_y = 0.4
                    
                    for type, varnames in variables.items():
                        #print(name)
                        col.label(type)
                        for name in varnames:
                            var = d.fcurve.driver.variables.get(name)
                            draw_variable(d, var, col)
                        #var = variables.get(key)

            if rubbish_vars:
                col = layout.column()
                col.alert = True
                col.label("No Targets")
                types = rubbish_vars.get("variables")
                for type, vars in types.items():
                    col.label(UILayout.enum_item_name(v0, "type", type), icon_value=enum_item_icon(v0, "type", type))
                    for var in vars:
                        var = d.fcurve.driver.variables.get(var)
                        draw_variable(d, var, col)
                
            self.check(context)
        
    def execute(self, context):
        print("DRIVER PIE EXEC")
        return {'FINISHED'}

class AddDriverVarPopup(DriverManager_DriverOp, Operator):
    """Add Driver Variable"""
    bl_idname = "driver.new_var_popup"
    bl_label = "Add Driver Variable"

    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        return True
    
    def draw(self, context):
        d = self.driver
        gui = d.driver_gui(context.scene)
        self.layout.label(gui.varname)
        var = d.fcurve.driver.variables.get(gui.varname)
        d.draw_edit_driver_var(self.layout, var)
        
    def invoke(self, context, event):
        wm = context.window_manager
        d = self.driver
        if not d:
            return {'CANCELLED'}
        # check if var is in variables
        name = "var"
        i = 1
        if d:
            while name in d.fcurve.driver.variables.keys():
                name = "var%d" % i
                i += 1
        v = d.fcurve.driver.variables.new()
        v.name = name
        gui = d.driver_gui(context.scene)
        gui.varname = v.name
        gui.var_index = d.fcurve.driver.variables.find(v.name)    
        return(wm.invoke_props_dialog(self))
    
    def execute(self, context):

        return {'FINISHED'}


class VIEW3D_PIE_drivers(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Select Mode"

    @classmethod
    def poll(self, context):
        dm = context.driver_manager
        print("PM POLL", dm is not None, hasattr(context, "driver_manager"))
        return True
        return dm is not None

    def draw(self, context):
        layout = self.layout
        layout.label("WHERE")
        obj = context.object
        dm = context.driver_manager
        if dm is None:
            layout.operator("drivermanager.update")
            return None
        
        pie = layout.menu_pie()
        dm.draw_pie_menu(obj, pie)
        dm.draw_pie_menu(obj.active_material, pie)
        #pie = pie.box()
        dm.draw_pie_menu(obj.data.shape_keys, pie)
        #pie = pie.box()
        #dm.draw_pie_menu(obj, pie)

        return None

addon_keymaps = []
def register():
    register_class(VIEW3D_PIE_drivers)
    register_class(PieMenuDriverPopup)
    register_class(AddDriverVarPopup)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu_pie", type='D', value='PRESS', ctrl=True)
        kmi.properties.name = "VIEW3D_PIE_drivers"
        addon_keymaps.append((km, kmi))

def unregister():
    unregister_class(VIEW3D_PIE_drivers)
    bpy.utils.unregister_class(PieMenuDriverPopup)
    unregister_class(AddDriverVarPopup)
if __name__ == "__main__":
    register()

    bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_drivers")
