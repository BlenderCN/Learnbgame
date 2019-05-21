import time
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty
from mathutils import Vector

bl_info = {
    "name": "Japan Road Generator", 
    "author": "Densyakun", 
    "version": (0, 0, 1, 'alpha'), 
    "blender": (2, 75, 0), 
    "location": "Mesh", 
    "description": "日本の規格で道路を簡単に生成するアドオンです。", 
    "warning": "", 
    "support": "TESTING", 
    "wiki_url": "", 
    "tracker_url": "", 
    "category": "Mesh"
}

if "bpy" in locals():
    import imp
    imp.reload(road_generator)
else:
    from . import road_generator

import bpy

addon_keymaps = []

class VIEW3D_PT_RoadGenMenu(bpy.types.Panel):
    bl_label = "JpnRoadGen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "JpnRoadGen"
    bl_context = "mesh_edit"

    @classmethod
    def poll(cls, context):
        return True
        #for o in bpy.data.objects:
        #    if o.select:
        #        return True
        #return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.operator(LanesGen.bl_idname)
        layout.operator(RoadGen.bl_idname)

class RoadGenMenu(bpy.types.Menu):
    bl_idname = "mesh.roadgen_menu"
    bl_label = "Densyakun Road Generator"
    bl_description = ""

    def draw(self, context):
        self.layout.operator(LanesGen.bl_idname)
        self.layout.operator(RoadGen.bl_idname)

def road_type_list_func(scene, context):
    return [(str(k), road_generator.road_type[k], "") for k in sorted(road_generator.road_type)]

class LanesGen(bpy.types.Operator):
    bl_idname = "mesh.lanesgen"
    bl_label = "車線を生成"
    bl_description = "選択中の辺に沿って辺を移動したり、辺を複製します。"
    bl_options = {'REGISTER', 'UNDO'}

    road_type = EnumProperty(
        name = "道路の種類",
        description = "道路の種類を設定します。他の設定に関係します",
        items = road_type_list_func
    )

    left_lanes = IntProperty(
        name = "複製する左側の車線数",
        description = "複製する左側の車線数を設定します",
        default = 1,
        min = 0
    )

    right_lanes = IntProperty(
        name = "複製する右側の車線数",
        description = "複製する右側の車線数を設定します",
        default = 1,
        min = 0
    )

    road_width = FloatProperty(
        name = "道路幅員",
        description = "道路の幅員を設定します",
        default = 3.0,
        min = 2.75,
        max = 3.75
    )

    offset = FloatProperty(
        name = "オフセット",
        description = "辺を左右に移動します",
        default = 0.0
    )

    invert = BoolProperty(
        name = "向きを反転",
        description = "道路の向きを反転します",
        default = False
    )

    def execute(self, context):
        LanesGen.road_type = self.road_type
        time_start = time.time()
        rw = road_generator.road_width.get(int(self.road_type))
        rwe = road_generator.road_width_exception.get(int(self.road_type))
        if rwe == None:
            rwe = self.road_width
        self.road_width = min(max(self.road_width, min((rw, rwe))), max((rw, rwe)))

        result = road_generator.lanes_generate(self, self.left_lanes, self.right_lanes, self.road_width, self.offset, self.invert)
        if result:
            self.report({'INFO'}, "Road Generator Finished: " + str(time.time() - time_start)[: 3] + "sec")
            return {'FINISHED'}
        return {'CANCELLED'}

class RoadGen(bpy.types.Operator):
    bl_idname = "mesh.roadgen"
    bl_label = "道路を生成"
    bl_description = "選択中の辺から道路を生成します。"
    bl_options = {'REGISTER', 'UNDO'}

    road_type = EnumProperty(
        name = "道路の種類",
        description = "道路の種類を設定します。他の設定に関係します",
        items = road_type_list_func
    )

    road_width = FloatProperty(
        name = "道路幅員",
        description = "道路の幅員を設定します",
        default = 3.0,
        min = 2.75,
        max = 3.75
    )

    '''
    left_lanes = IntProperty(
        name = "左側の車線数",
        description = "左側の車線数を設定します",
        default = 2,
        min = 1
    )

    right_lanes = IntProperty(
        name = "右側の車線数",
        description = "右側の車線数を設定します",
        default = 2,
        min = 1
    )
    '''

    invert = BoolProperty(
        name = "向きを反転",
        description = "道路の向きを反転します",
        default = False
    )

    def execute(self, context):
        RoadGen.road_type = self.road_type
        time_start = time.time()
        rw = road_generator.road_width.get(int(self.road_type))
        rwe = road_generator.road_width_exception.get(int(self.road_type))
        if rwe == None:
            rwe = self.road_width
        self.road_width = min(max(self.road_width, min((rw, rwe))), max((rw, rwe)))

        result = road_generator.road_generate(self, self.road_width, self.invert)
        if result:
            self.report({'INFO'}, "Road Generator Finished: " + str(time.time() - time_start)[: 3] + "sec")
            return {'FINISHED'}
        return {'CANCELLED'}

def menu_func(self, context):
    self.layout.separator()
    self.layout.menu(RoadGenMenu.bl_idname)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(RoadGenMenu.bl_idname, 'R', 'PRESS', ctrl=True, shift=True, alt=True)

def unregister():
    for km in addon_keymaps:
        bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
