import bpy

#subdir list
class NDUIList(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, flt_flag):
        layout.label(item.name)

class NDFileBrowserUI(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOLS'
    bl_category = "Notre-Dame"
    bl_label = "Notre-Dame"
    
    @classmethod
    def poll(cls, context):
        winman=bpy.data.window_managers['WinMan']
        chk=0
        try:
            prop=winman.nd_props[0]
        except IndexError:
            chk=1
        return chk==0
    
    def draw(self, context):
        layout = self.layout
        
        winman=bpy.data.window_managers['WinMan']
        prop=winman.nd_props[0]
        
        layout.prop(prop, 'shot_index')
        
        if len(prop.dirpath_coll)>0:
            layout.template_list("NDUIList", "", prop, "dirpath_coll", prop, "path_index", rows=20)
            
        row=layout.row(align=True)
        row.operator("nd.reload_custom_path", text='Reload', icon='FILE_REFRESH')
        row.operator("nd.open_custom_path_folder", text='Open', icon='FILE_FOLDER')