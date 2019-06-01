# coding: utf-8

"""
group remover - Operator to remove groups faster
pre-select empty groups
"""
import bpy

def object_invoke_func(self, context, event):
    wm = context.window_manager
    wm.invoke_props_dialog(self)
    return {'RUNNING_MODAL'}

class Group_remover(bpy.types.Operator):
    '''Pop a menu to choose Groups to delete'''
    bl_idname = "utils.group_remover"
    bl_label = "Remove chosen groups"

    groups_selection = bpy.props.BoolVectorProperty(size=32, options={'SKIP_SAVE'})

    # poll = object_poll_func
    invoke = object_invoke_func

    def draw(self, context):
        layout = self.layout

        self.grpList = [grp for grp in bpy.data.groups]#grp.name

        #pre-fill the selection propertie (True if group if empty) -> + fill with bool statement until to assign 32 slots
        self.groups_selection = [len(bpy.data.groups[i].objects) == 0 for i in range(len(bpy.data.groups))] + [False for i in range(32) if i >= len(bpy.data.groups)]
        # self.groups_selection = [False for i in range(32)]

        #error message if no groups:
        if not self.grpList:
            layout.label('No groups available !')

        #create the list to display in popup
        if self.grpList:
            layout.label('select groups to remove (group containing no objects are pre-selected):')
            for idx, grp in enumerate(self.grpList):
                name = grp.name
                layout.prop(self, 'groups_selection', index=idx, text=name, toggle=True)


    def execute(self, context):
        groupToDelete = []
        for idx, flag in enumerate(self.groups_selection):
            if flag:
                groupToDelete.append(self.grpList[idx])

        if groupToDelete:
            for group in groupToDelete:
                print ('deleting group', group.name)
                bpy.data.groups.remove(group)

            #eventually print info
            ##mess = str(len(groupToDelete)) + ' group deleted'
            ##self.report({'INFO'}, mess)

        else:
            ##nothing selected
            pass

        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
