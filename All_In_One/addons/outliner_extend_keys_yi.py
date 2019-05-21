# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# outliner_extend_keys_yi.py

import bpy


bl_info = {
    'name' : "Outliner Extend Keys",
    'description' : "Outliner Extend Keys",
    'author' : "Yi Danyang",
    'version' : ( 0, 0, 3 ),
    'blender' : ( 2, 6, 9, 1 ),
    'api' : 61076,
    'location' : '[Outliner]Hotkey: up/down + [shift]; (alt + wheel up/down) + [shift]; shift + (double)LMB; shift v/s/r',
    'warning' : "Alpha",
    'category' : 'Outliner',
    "wiki_url" : "https://github.com/nirenyang/Blender_Addon_-_Outliner_Extend_Keys",
    "tracker_url" : "http://www.blenderartists.org/forum/showthread.php?303375-Addon-Outliner-Extend-Keys",
}


##
## Force VSR Begin
##
enum_vsr = [( 'V', 'v', 'hide' ),
            ( 'S', 's', 'hide_select' ),
            ( 'R', 'r', 'hide_render' ),]
class ObjectSetVSR(bpy.types.Operator):
    """Object Set VSR"""
    bl_idname = "object.set_vsr"
    bl_label = "Object Set VSR"
    bl_options = {'REGISTER', 'UNDO'}

    input_vsr = bpy.props.EnumProperty( name='arrows', description='Arrow Types', items=enum_vsr)

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return context.area.type == 'OUTLINER'

    def execute(self, context):
        if self.input_vsr == 'V':
            tmp = not context.active_object.hide
            for i in context.selected_objects:
                if i.hide != tmp:
                    i.hide = tmp
        elif self.input_vsr == 'S':
            tmp = not context.active_object.hide_select
            for i in context.selected_objects:
                if i.hide_select != tmp:
                    i.hide_select = tmp
        elif self.input_vsr == 'R':
            tmp = not context.active_object.hide_render
            for i in context.selected_objects:
                if i.hide_render != tmp:
                    i.hide_render = tmp
        return {'FINISHED'}

def registerObjectSetVSR():
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Outliner']
    if kc:
        for i in enum_vsr:
            kmi = kc.keymap_items.new('object.set_vsr', i[0], 'PRESS', shift = True)
            kmi.properties.input_vsr = i[0]
        kmi = kc.keymap_items.new('outliner.item_rename', 'F2', 'PRESS')
        
def unregisterObjectSetVSR():
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Outliner']
    if kc:
        for i in enum_vsr:
            if i[0] in kc.keymap_items.keys():
                kc.keymap_items.remove( kc.keymap_items[i[0]] )
##
## Force VSR End
##

##
## Queue Select Begin
##
class ObjectQueueSelect(bpy.types.Operator):
    """ObjectQueueSelect"""
    bl_idname = "object.object_queue_select"
    bl_label = "Object Queue Select"
    bl_options = {'REGISTER', 'UNDO'}
    
    ctrlOn = bpy.props.BoolProperty( name='ctrl', description='ctrl bool') #反选
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return context.area.type == 'OUTLINER' and space.display_mode in {'ALL_SCENES', }    #'CURRENT_SCENE'}
        
    def execute(self, context):
        # import locale
        # locale.setlocale(locale.LC_ALL, "") #亚洲语言支持for asian language sorting 但是bl的列表似乎是按西文的排列
        sorted_names = [i.name for i in context.scene.objects]
        # sorted_names.sort(key=locale.strxfrm)
        sorted_names.sort()
        
        select_ob = [i for i in context.selected_objects if i != context.active_object]
        if len(select_ob) < 1:
            self.report({'INFO'}, '2 objects need!')
            return {'CANCELLED'}
        select_id = sorted_names.index(select_ob[0].name)
        active_id = sorted_names.index(context.active_object.name)
        ids = [(select_id, active_id), (active_id, select_id)][(active_id-select_id) < 0]
        if abs(select_id-active_id) < 2:
            return {'FINISHED'}
        for i in range(ids[0], ids[1]):
            context.scene.objects[sorted_names[i]].select = True
        return {'FINISHED'}
        
def registerObjectQueueSelect():
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Outliner']
    if kc:
        kmi = kc.keymap_items.new('object.object_queue_select', 'LEFTMOUSE', 'DOUBLE_CLICK', shift = True)
        kmi.properties.ctrlOn = False
        # kmi = kc.keymap_items.new('object.object_alt_select', 'LEFTMOUSE', 'DOUBLE_CLICK', shift = True, ctrl = True)
        # kmi.properties.ctrlOn = True
        
def unregisterObjectQueueSelect():
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Outliner']
    if kc:
        if 'object.object_queue_select' in kc.keymap_items.keys():
            kc.keymap_items.remove( kc.keymap_items['object.object_queue_select'] )
##
## Queue Select End
##

##
## Arrow and Wheel Select Begin
##
enum_arrow = [( 'UP_ARROW', 'UP', 'up' ),
              ( 'DOWN_ARROW', 'DOWN', 'down' ),
              ( 'None', 'None', 'None' ),]
              # ( 'LEFT_ARROW', 'LEFT', 'left' ),
              # ( 'RIGHT_ARROW', 'RIGHT', 'right' ),]
enum_wheel = [( 'WHEELINMOUSE', 'UP', 'up' ),
              ( 'WHEELOUTMOUSE', 'DOWN', 'down' ),
              ( 'None', 'None', 'None' ),]
class ObjectArrowAndWheelSelect(bpy.types.Operator):
    """ObjectArrowAndWheelSelect"""
    bl_idname = "object.arrow_and_wheel_select"
    bl_label = "Object Arrow and Wheel Select "
    bl_options = {'REGISTER', 'UNDO'}
    
    shiftOn     = bpy.props.BoolProperty(name='shift', description='Shift Bool')
    input_arrow = bpy.props.EnumProperty(name='arrows', description='Arrow Types', items=enum_arrow)
    input_wheel = bpy.props.EnumProperty(name='wheels', description='Wheel Types', items=enum_wheel)
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return context.area.type == 'OUTLINER' and space.display_mode in {'ALL_SCENES', }    #'CURRENT_SCENE'}

    def execute(self, context):
        # import locale
        # locale.setlocale(locale.LC_ALL, "") #亚洲语言支持for asian language sorting 但是bl的列表似乎是按西文的排列
        sorted_names = [i.name for i in context.scene.objects]
        # sorted_names.sort(key=locale.strxfrm)
        sorted_names.sort()
        
        while context:
            if self.input_arrow == 'LEFT_ARROW':
                pass
                # print('close? how to get outliner active object?')
            elif self.input_arrow == 'RIGHT_ARROW':
                pass
                # print('open? how to get outliner active object?')
            else:
                if not self.shiftOn:
                    bpy.ops.object.select_all( action='DESELECT' )
                if not context.active_object:
                    next_id = 0
                else:
                    curr_id = sorted_names.index(context.active_object.name)
                    if self.input_arrow == 'UP_ARROW' or self.input_wheel == 'WHEELINMOUSE':
                        if curr_id == 0:
                            next_id = len(sorted_names)-1
                        else:
                            next_id = curr_id-1
                    elif self.input_arrow == 'DOWN_ARROW' or self.input_wheel == 'WHEELOUTMOUSE':
                        if curr_id == len(sorted_names)-1:
                            next_id = 0
                        else:
                            next_id = curr_id+1
                        
                context.scene.objects.active = context.scene.objects[sorted_names[next_id]]
                context.active_object.select = True
            break
        return {'FINISHED'}
        
def registerObjectArrowAndWheelSelect():
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Outliner']
    if kc:
        for i in enum_arrow:
            if not i[0] == 'None':
                #arrow
                kmi = kc.keymap_items.new('object.arrow_and_wheel_select', i[0], 'PRESS', shift = True)
                kmi.properties.input_arrow = i[0]
                kmi.properties.input_wheel = 'None'
                kmi.properties.shiftOn = True
                kmi = kc.keymap_items.new('object.arrow_and_wheel_select', i[0], 'PRESS', shift = False)
                kmi.properties.input_arrow = i[0]
                kmi.properties.input_wheel = 'None'
                kmi.properties.shiftOn = False
        for i in enum_wheel:
            if not i[0] == 'None':
                #wheel
                kmi = kc.keymap_items.new('object.arrow_and_wheel_select', i[0], 'PRESS', shift = True, alt = True)
                kmi.properties.input_arrow = 'None'
                kmi.properties.input_wheel = i[0]
                kmi.properties.shiftOn = True
                kmi = kc.keymap_items.new('object.arrow_and_wheel_select', i[0], 'PRESS', shift = False, alt = True)
                kmi.properties.input_arrow = 'None'
                kmi.properties.input_wheel = i[0]
                kmi.properties.shiftOn = False
            
def unregisterObjectArrowAndWheelSelect():
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Outliner']
    if kc:
        for i in enum_arrow:
            if not i[0] == 'None':
                if i[0] in kc.keymap_items.keys():
                    kc.keymap_items.remove( kc.keymap_items[i[0]] )
                    kc.keymap_items.remove( kc.keymap_items[i[0]] )
        for i in enum_wheel:
            if not i[0] == 'None':
                if i[0] in kc.keymap_items.keys():
                    kc.keymap_items.remove( kc.keymap_items[i[0]] )
                    kc.keymap_items.remove( kc.keymap_items[i[0]] )    
##
## Arrow and Wheel Select End
##


def register():
    bpy.utils.register_class(ObjectSetVSR)
    bpy.utils.register_class(ObjectQueueSelect)
    bpy.utils.register_class(ObjectArrowAndWheelSelect)
    registerObjectSetVSR()
    registerObjectQueueSelect()
    registerObjectArrowAndWheelSelect()

def unregister():
    bpy.utils.unregister_class(ObjectSetVSR)
    bpy.utils.unregister_class(ObjectQueueSelect)
    bpy.utils.unregister_class(ObjectArrowAndWheelSelect)
    unregisterObjectSetVSR()
    unregisterObjectQueueSelect()
    unregisterObjectArrowAndWheelSelect()


if __name__ == "__main__":
    register()