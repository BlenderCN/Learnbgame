import bpy


def change_active_action(self, context):
    action = bpy.data.actions.get(self.actions[self.active_index].name)
    context.object.animation_data.action = action


# define some types
bpy.types.Armature.active_index = bpy.props.IntProperty(description="ACTIVE", update=change_active_action)

class UL_rig_actions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            if ob:
                ac = bpy.data.actions.get(item.name)
                if ac is None:
                    layout.prop(item, "description", text="", emboss=False, icon='IMPORT') 
                    
                else:
                    layout.prop(item, "description", text="", emboss=False, icon='ACTION')
                    layout.prop(ac, "use_fake_user", text="")
            else:
                layout.label(text="xxxx", translate=False, icon_value=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class RigActionListPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Rig Actions"
    bl_idname = "OBJECT_PT_ui_list_example"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "BVH"

    def draw(self, context):
        layout = self.layout

        obj = context.object.data

        layout.template_list("UL_rig_actions", "", obj, "actions", obj, "active_index")

        '''
        layout.template_list("UL_rig_actions", "compact", obj, "actions",
                             obj, "active_index", type='COMPACT')
        '''

def register():
    bpy.utils.register_class(UL_rig_actions)
    bpy.utils.register_class(RigActionListPanel)


def unregister():
    bpy.utils.unregister_class(UL_rig_actions)
    bpy.utils.unregister_class(RigActionListPanel)


if __name__ == "__main__":
    register()

