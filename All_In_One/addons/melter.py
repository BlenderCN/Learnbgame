import bpy
import bgl
import math
import bmesh
from bpy.props import IntProperty, BoolProperty, StringProperty, EnumProperty
import rna_keymap_ui


######################
# CODE STRUCTURE
######################
# Misc Operations
#---------------------
# Core Operations
#---------------------
# Body Section
#---------------------
# Pie Menu Section
#---------------------
# Keymap Section
#---------------------
# Register and Unregister
######################


bl_info = {
    "name" : "Melter",
    "description" : "Vertex Melter",
    "author" : "Kozo Oeda",
    "version" : (0, 9),
    "location" : "",
    "warning" : "",
    "support" : "COMMUNITY",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}


###################
# Misc Operations #
###################


class SetAtFirst(bpy.types.Operator):
    bl_idname = "view3d.set_at_first"
    bl_label = "Set At First"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.mlt_merge_type = 'FIRST'
        return {'FINISHED'}


class SetAtLast(bpy.types.Operator):
    bl_idname = "view3d.set_at_last"
    bl_label = "Set At Last"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.mlt_merge_type = 'LAST'
        return {'FINISHED'}
        

class SetAtCenter(bpy.types.Operator):
    bl_idname = "view3d.set_at_center"
    bl_label = "Set At Center"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.mlt_merge_type = 'CENTER'
        return {'FINISHED'}


class SetAtCursor(bpy.types.Operator):
    bl_idname = "view3d.set_at_cursor"
    bl_label = "Set At Cursor"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.mlt_merge_type = 'CURSOR'
        return {'FINISHED'}


class SetCollapse(bpy.types.Operator):
    bl_idname = "view3d.set_collapse"
    bl_label = "Set Collapse"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.mlt_merge_type = 'COLLAPSE'
        return {'FINISHED'}


class CircleSizeUp(bpy.types.Operator):
    bl_idname = "view3d.mlt_circle_radius_up"
    bl_label = "Circle Size Up"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.mlt_circle_radius += 2
        context.scene.mlt_circle_updated = True
        return {'FINISHED'}


class CircleSizeDown(bpy.types.Operator):
    bl_idname = "view3d.mlt_circle_radius_down"
    bl_label = "Circle Size Down"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        context.scene.mlt_circle_radius -= 2
        context.scene.mlt_circle_updated = True
        return {'FINISHED'}


##################
# Core Operation #
##################


class MelterOperation(bpy.types.Operator):
    bl_idname = "view3d.melter_operation"
    bl_label = "Merge Verts"
    bl_options = {'INTERNAL'}

    def __init__(self):
        self._origin_3d_cursor = None
        self._at_first = None
        self._at_last = None
        self._at_last_index = None
        self._verts_indexes = []
        self.mat = bpy.context.object.matrix_world

    def select_joined_vert(self):
        bpy.context.object.update_from_editmode()
        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        bm.verts[bpy.context.scene.mlt_joined_vert_index].select = True

    def update_joined_vert(self):
        bpy.context.object.update_from_editmode()
        bm = bmesh.from_edit_mesh(bpy.context.object.data)

        selected_verts = [vert for vert in bm.verts if vert.select]

        if len(selected_verts) > 1:
            return None, None

        elif len(selected_verts) == 1:
            return selected_verts[0].co, selected_verts[0].index

        else:
            return None, None

    def select_circle(self, origin, radius):
        bpy.ops.view3d.select_circle(x = origin[0], y = origin[1], radius = radius, gesture_mode = 3)

    def melt_at_first(self, origin, radius): 
        bpy.context.object.update_from_editmode()

        def update_3d_curosr():
            if self._origin_3d_cursor is None:
                #self._origin_3d_cursor = bpy.context.scene.cursor_location changes values dynamically in 2.78
                x, y, z = bpy.context.scene.cursor_location
                self._origin_3d_cursor = (x, y, z)

            if self._at_first:
                bpy.context.scene.cursor_location = self.mat * self._at_first

        if self._at_first:
            self.select_circle(origin, radius)
            bpy.ops.mesh.merge(type = 'CURSOR')

        else:
            self.select_circle(origin, radius)

            try:
                bpy.ops.mesh.merge(type = 'FIRST')
                self._at_first, _ = self.update_joined_vert()
                update_3d_curosr()
            except TypeError:
                self._at_first, _ = self.update_joined_vert()
                update_3d_curosr()

    def melt_at_last(self, origin, radius): 
        bpy.context.object.update_from_editmode()

        def update_3d_curosr():
            if self._origin_3d_cursor is None:
                #self._origin_3d_cursor = bpy.context.scene.cursor_location changes values dynamically in 2.78
                x, y, z = bpy.context.scene.cursor_location
                self._origin_3d_cursor = (x, y, z)
            bpy.context.scene.cursor_location = self.mat * self._at_last

        def backup_verts():
            bm = bmesh.from_edit_mesh(bpy.context.object.data)

            for index in self._verts_indexes:
                bm.verts[index].select_set(True)

        bpy.ops.mesh.select_all(action = 'DESELECT') 
        self.select_circle(origin, radius)

        self._at_last, self._at_last_index = self.update_joined_vert()

        if self._at_last_index:
            self._verts_indexes.append(self._at_last_index)

        if len(self._verts_indexes) and self._at_last:
            backup_verts()

            if self._at_last:
                update_3d_curosr()

            bpy.ops.mesh.merge(type = 'CURSOR')
            self._verts_indexes.clear()

            self._at_last, self._at_last_index = self.update_joined_vert()
            self._verts_indexes.append(self._at_last_index)

    def melt(self, origin, radius, mlt_merge_type):
       
        self.select_circle(origin, radius)
        bpy.ops.mesh.merge(type = mlt_merge_type)

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            bpy.ops.mesh.select_all(action = 'DESELECT') #TODO
            return {'RUNNING_MODAL'}

        else:
            return {'CANCELLED'}

    def modal(self, context, event):
        if event.value in {'RELEASE'}:
            self._at_first = None
            self._at_last =  None
            self._at_last_index = None
            self._verts_indexes = []

            if self._origin_3d_cursor:
                bpy.context.scene.cursor_location = self._origin_3d_cursor

            self._origin_3d_cursor = None
            bpy.ops.mesh.select_all(action = 'DESELECT')
            return {'CANCELLED'}

        if event.type in {'MOUSEMOVE'}:
            origin = (event.mouse_region_x, event.mouse_region_y)
            radius = bpy.context.scene.mlt_circle_radius
            merge_type = bpy.context.scene.mlt_merge_type

            if merge_type == 'FIRST':
                self.melt_at_first(origin, radius)

            elif merge_type == 'LAST':
                self.melt_at_last(origin, radius)

            else:
                self.melt(origin, radius, merge_type)

        return {'PASS_THROUGH'}


#################
# Body  Section #
#################


def get_keymap_item(km, kmi_idname):
    for keymap_item in km.keymap_items:

        if keymap_item.idname == kmi_idname:
            return keymap_item

    return None


class Melter(bpy.types.Operator):
    bl_idname = "view3d.start_melter"
    bl_label = "Start Melter"
        
    def keymap_on(self, context):
        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Mesh']
        idnames = [MelterOperation.bl_idname, SetMelterSettingPieTrigger.bl_idname, CircleSizeUp.bl_idname, CircleSizeDown.bl_idname]

        for idname in idnames:
            kmi = get_keymap_item(km, idname)
            kmi.active = True
        
    def keymap_off(self, context):
        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Mesh']
        idnames = [MelterOperation.bl_idname, SetMelterSettingPieTrigger.bl_idname, CircleSizeUp.bl_idname, CircleSizeDown.bl_idname]

        for idname in idnames:
            kmi = get_keymap_item(km, idname)
            kmi.active = False

    def draw_circle(self, origin, points, point_list):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBegin(bgl.GL_LINES)

        bgl.glLineWidth(1)
        bgl.glColor4f(0, 255, 150, 1)

        for n in range(points - 1):
            bgl.glVertex2f(origin[0] + point_list[n][0], origin[1] + point_list[n][1])
            bgl.glVertex2f(origin[0] + point_list[n + 1][0], origin[1] + point_list[n + 1][1])

        bgl.glVertex2f(origin[0] + point_list[-1][0], origin[1] + point_list[-1][1])
        bgl.glVertex2f(origin[0] + point_list[0][0], origin[1] + point_list[0][1])

        bgl.glEnd()
        bgl.glDisable(bgl.GL_BLEND)

    def __init__(self):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        if bpy.context.scene.mlt_is_first_init:
            bpy.context.scene.mlt_circle_radius = addon_prefs.radius
            bpy.context.scene.mlt_merge_type = addon_prefs.mlt_merge_type
            bpy.context.scene.mlt_is_first_init = False

        self._handle_draw = None
        self.radius = bpy.context.scene.mlt_circle_radius
        self.points = 30
        self.degrees = float(360.0/self.points)
        self.point_list = [(self.radius * math.cos(math.radians(n * self.degrees)), self.radius * math.sin(math.radians(n * self.degrees))) for n in range(self.points)]

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            #bpy.ops.mesh.select_all(action = 'DESELECT') #TODO

            self.keymap_on(context)
            context.window_manager.modal_handler_add(self)

            origin = (event.mouse_region_x, event.mouse_region_y)
            args = (origin, self.points, self.point_list)
            self._handle_draw = bpy.types.SpaceView3D.draw_handler_add(self.draw_circle, args, 'WINDOW', 'POST_PIXEL')
            return {'RUNNING_MODAL'}

        else:
            return {'CANCELLED'}

    def modal(self, context, event):
        try:
            bpy.context.area.tag_redraw()
        except AttributeError:
            pass

        if bpy.context.scene.mlt_circle_updated:
            self.radius = bpy.context.scene.mlt_circle_radius
            self.point_list = [(self.radius * math.cos(math.radians(n * self.degrees)), self.radius * math.sin(math.radians(n * self.degrees))) for n in range(self.points)]
            bpy.context.scene.mlt_circle_updated = False

            if self._handle_draw:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw, 'WINDOW')

            origin = (event.mouse_region_x, event.mouse_region_y)
            args = (origin, self.points, self.point_list)
            self._handle_draw = bpy.types.SpaceView3D.draw_handler_add(self.draw_circle, args, 'WINDOW', 'POST_PIXEL')
            
        if event.type in {'MOUSEMOVE'}:
            if self._handle_draw:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw, 'WINDOW')

            origin = (event.mouse_region_x, event.mouse_region_y)
            args = (origin, self.points, self.point_list)
            self._handle_draw = bpy.types.SpaceView3D.draw_handler_add(self.draw_circle, args, 'WINDOW', 'POST_PIXEL')

        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw, "WINDOW")
            self.keymap_off(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


####################
# Pie Menu Section #
####################


class MelterSettingPie(bpy.types.Menu):
    bl_idname = "MelterSettingPie"
    bl_label = "Melter Setting"

    def is_first(self):
        if bpy.context.scene.mlt_merge_type == 'FIRST':
            return 'CHECKBOX_HLT'

        else:
            return 'CHECKBOX_DEHLT'

    def is_last(self):
        if bpy.context.scene.mlt_merge_type == 'LAST':
            return 'CHECKBOX_HLT'

        else:
            return 'CHECKBOX_DEHLT'

    def is_center(self):
        if bpy.context.scene.mlt_merge_type == 'CENTER':
            return 'CHECKBOX_HLT'

        else:
            return 'CHECKBOX_DEHLT'

    def is_cursor(self):
        if bpy.context.scene.mlt_merge_type == 'CURSOR':
            return 'CHECKBOX_HLT'

        else:
            return 'CHECKBOX_DEHLT'

    def is_collapse(self):
        if bpy.context.scene.mlt_merge_type == 'COLLAPSE':
            return 'CHECKBOX_HLT'

        else:
            return 'CHECKBOX_DEHLT'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator(SetAtFirst.bl_idname, text = "At First", icon = self.is_first())
        pie.operator(SetCollapse.bl_idname, text = "Collapse", icon = self.is_collapse())
        pie.operator(SetAtCursor.bl_idname, text = "At Cursor", icon = self.is_cursor())
        pie.operator(SetAtCenter.bl_idname, text = "At Center", icon = self.is_center())
        pie.operator(SetAtLast.bl_idname, text = "At Last", icon = self.is_last())

        
class SetMelterSettingPieTrigger(bpy.types.Operator):
    bl_idname = 'wm.set_melter_setting_pie'
    bl_label = "Melter Pie Menu"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name = "MelterSettingPie")
        return {'FINISHED'}


##################
# Keymap Section #
##################


class ManageMelterKeymap(bpy.types.AddonPreferences):
    bl_idname = __name__

    items = [('FIRST', 'At First', '', 0),
             ('LAST', 'At Last', '', 1),
             ('CENTER', 'At Center', '', 2),
             ('CURSOR', 'At Cursor', '', 3),
             ('COLLAPSE', 'Collapse', '', 4),
    ]

    radius = IntProperty(name = "Circle Radius", default = 10, min = 0)
    mlt_merge_type = EnumProperty(name = "Merge Types", items = items)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radius")
        layout.prop(self, "mlt_merge_type")
        wm = context.window_manager
        kc = wm.keyconfigs.user
        box = layout.box()
        box.label("You don't need to check boxes of Merge Verts, Melter Pie Menu, Circle Size Up and Circle Size Down.")

        idnames = [Melter.bl_idname, MelterOperation.bl_idname, SetMelterSettingPieTrigger.bl_idname, CircleSizeUp.bl_idname, CircleSizeDown.bl_idname]
        km = kc.keymaps['Mesh']

        for n, idname in enumerate(idnames):
            split = box.split()
            col = split.column()
            kmi = get_keymap_item(km, idname)

            if kmi:
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

            else:
                register_keymap()


###########################
# Register and Unregister #
###########################


addon_keymaps = []


def register_keymap():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh', space_type = 'EMPTY')

    kmi = km.keymap_items.new(Melter.bl_idname, 'NONE', 'PRESS', head = True)
    kmi.active = True

    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(MelterOperation.bl_idname, 'LEFTMOUSE', 'PRESS', head = True)
    kmi.active = False

    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(SetMelterSettingPieTrigger.bl_idname, 'RIGHTMOUSE', 'PRESS', head = True)
    kmi.active = False

    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CircleSizeUp.bl_idname, 'WHEELUPMOUSE', 'ANY', shift = True, head = True)
    kmi.active = False

    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(CircleSizeDown.bl_idname, 'WHEELDOWNMOUSE', 'ANY', shift = True, head = True)
    kmi.active = False

    addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.mlt_circle_radius = IntProperty(default = 10)
    bpy.types.Scene.mlt_circle_updated = BoolProperty(default = False)
    bpy.types.Scene.mlt_merge_type = StringProperty(default = 'CENTER')
    bpy.types.Scene.mlt_joined_vert_index = IntProperty(default = -1)
    bpy.types.Scene.mlt_joined_vert_id = StringProperty(default = '')
    bpy.types.Scene.mlt_is_first_init = BoolProperty(default = True)
    register_keymap()


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.mlt_circle_radius
    del bpy.types.Scene.mlt_circle_updated
    del bpy.types.Scene.mlt_merge_type
    del bpy.types.Scene.mlt_joined_vert_index
    del bpy.types.Scene.mlt_joined_vert_id
    del bpy.types.Scene.mlt_is_first_init
    unregister_keymap()


if __name__ == '__main__':
    register()
