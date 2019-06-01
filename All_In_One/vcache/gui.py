import bpy

#Pie Menu
class VCachePieMenu(bpy.types.Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "VCache"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='VIEW_3D'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        pie.operator('vcache.playback_rangecache', text="Play Frame Range", icon='RIGHTARROW')
        pie.operator('vcache.opengl_range', text="Cache Range", icon='ARROW_LEFTRIGHT')
        #pie.operator('vcache.copy', text='Export Current Cache', icon='DISK_DRIVE')
        pie.operator('vcache.settings_menu', text='Scene Settings', icon='MODIFIER')
        pie.menu('VCache_cache_info_menu', text='Cache Menu', icon='COLLAPSEMENU')
        
#Pie Caller
class VCachePieMenuCaller(bpy.types.Operator):
    bl_idname = "vcache.piemenu_caller"
    bl_label = "VCache Pie Menu"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.area.type=='VIEW_3D'

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VCachePieMenu")
        return {'FINISHED'}
    
#Cache Menu
class VCacheCacheInfoMenu(bpy.types.Menu):
    bl_label = "Viewport Cache Info Menu"
    bl_idname = "VCache_cache_info_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("vcache.open_cache")
        layout.separator()
        layout.operator("vcache.purge_all_except_project", text="Purge All Cache except Current Project")
        layout.operator("vcache.purge_scene", text="Purge Current Scene Cache")
        layout.operator("vcache.purge_project", text="Purge Current Project Cache")
        layout.operator("vcache.purge_all", text="Purge All Cache")
        
#Settings Menu
class VCacheCacheSettingsMenu(bpy.types.Operator):
    bl_idname = "vcache.settings_menu"
    bl_label = "VCache Settings Menu"
    bl_description = "Set some scene settings"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300, height=100)
    
    def check(self, context):
        return True
    
    def draw(self, context):
        scn=bpy.context.scene

        layout = self.layout
        layout.prop(scn, 'vcache_draft')
        layout.prop(scn, 'vcache_only_render')
        layout.prop(scn, 'vcache_real_size')
        row=layout.row(align=True)

        #check cams
        chk=0
        for ob in bpy.context.scene.objects:
            if ob.type=='CAMERA':
                chk=1
        
        if chk==1:
            if scn.vcache_camera=='':
                row.menu('VCache_cam_menu')
            else:
                row.menu('VCache_cam_menu', text=scn.vcache_camera)
            row.separator()
            row.operator("vcache.get_active_cam", icon='EYEDROPPER', text='')
        else:
            if scn.vcache_camera!='':
                row.label(scn.vcache_camera+' missing - Clear it to Cache', icon='ERROR')
            else:
                row.label('No Camera')
        row.operator("vcache.clear_cam", icon='X', text='')

    def execute(self, context):
        return {"FINISHED"}
    
#cam menu
class VCacheCamMenu(bpy.types.Menu):
    bl_label = "Select Camera"
    bl_idname = "VCache_cam_menu"
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        scn=bpy.context.scene
        chk=0
        layout = self.layout
        for ob in bpy.context.scene.objects:
            if ob.type=='CAMERA':
                chk=1
                if ob.name==scn.vcache_camera:
                    op=layout.operator("vcache.change_cam", text=ob.name, icon='OUTLINER_OB_CAMERA')
                    op.cam=ob.name
                else:
                    op=layout.operator("vcache.change_cam", text=ob.name, icon='CAMERA_DATA')
                    op.cam=ob.name
