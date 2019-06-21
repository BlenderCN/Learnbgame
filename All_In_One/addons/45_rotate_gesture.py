# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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


import bpy



bl_info = {'name':'45 rotate gesture',
            'author':'bookyakuno',
            'version':(0,1),
            "category": "Learnbgame",
            'location':'View3D > cmd + D , Ctrl + Shift + D',
            'description':'45 rotate Gesture'}



class rotate_gesture(bpy.types.Operator):
    bl_idname = "object.rotate_gesture"
    bl_label = "45 rotate gesture"
    bl_options = {'REGISTER', 'UNDO'}



#     first_mouse_x = IntProperty()
#     first_mouse_y = IntProperty()
#     first_mouse_z = IntProperty()
#     first_valuex = FloatProperty()
#     first_valuey = FloatProperty()
#     first_valuez = FloatProperty()
#     axis = StringProperty()
#     value_fix_x = 0
#     value_fix_y = 0
#     value_fix_z = 0
#     nd = 0
    def vdist(self):
      area=bpy.context.window.screen.areas[0]
      for x in bpy.context.window.screen.areas:
          if x.type=='VIEW_3D': area=x

      area.spaces[0].region_3d.view_distance
      return area.spaces[0].region_3d.view_distance

    def modal(self, context, event):

# 説明
        context.area.header_text_set('Mouse wheel Up/Down or + - key = 45, Shift +wheel = -45, ZXCY = & AXIS,  Shift + ZXCY = -45 & AXIS')


################################################################

################################################################
# # # # # # # #

        if event.type == 'D' and event.value=='PRESS':
            bpy.ops.transform.rotate(value=0.785398, constraint_orientation='GLOBAL') #編集


        elif event.type == 'WHEELUPMOUSE' and event.shift  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(True, False, False), constraint_orientation='GLOBAL') #編集
        elif event.type == 'WHEELDOWNMOUSE' and event.shift  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(True, False, False), constraint_orientation='GLOBAL') #編集

        elif event.type == 'WHEELUPMOUSE' and event.alt  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集
        elif event.type == 'WHEELDOWNMOUSE' and event.alt  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集

        elif event.type == 'WHEELUPMOUSE' and event.alt  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集
        elif event.type == 'WHEELDOWNMOUSE' and event.alt  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集


        elif event.type == 'WHEELUPMOUSE' and event.oskey  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(False, False, True), constraint_orientation='GLOBAL') #編集
        elif event.type == 'WHEELDOWNMOUSE' and event.oskey  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(False, False, True), constraint_orientation='GLOBAL') #編集




        elif event.type == 'WHEELUPMOUSE':

            bpy.ops.transform.rotate(value=0.785398, constraint_orientation='GLOBAL') #編集
        elif event.type == 'WHEELDOWNMOUSE':

            bpy.ops.transform.rotate(value=-0.785398, constraint_orientation='GLOBAL') #編集


        elif event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398, constraint_orientation='GLOBAL') #編集

        elif event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398, constraint_orientation='GLOBAL') #編集



        elif event.type == 'X' and event.shift  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(True, False, False), constraint_orientation='GLOBAL') #編集
        elif event.type == 'X'  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(True, False, False), constraint_orientation='GLOBAL') #編集

        elif event.type == 'Y' and event.shift  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集
        elif event.type == 'Y'  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集

        elif event.type == 'C' and event.shift  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集
        elif event.type == 'C'  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(False, True, False), constraint_orientation='GLOBAL') #編集

        elif event.type == 'Z' and event.shift  and event.value=='PRESS':
            bpy.ops.transform.rotate(value=-0.785398,constraint_axis=(False, False, True), constraint_orientation='GLOBAL') #編集
        elif event.type == 'Z'  and event.value=='PRESS':

            bpy.ops.transform.rotate(value=0.785398,constraint_axis=(False, False, True), constraint_orientation='GLOBAL') #編集






        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()
            return {'FINISHED'}

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()
            return {'FINISHED'}


        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set()
#            return {'CANCELLED'}
            return {'FINISHED'}


# # # # # # # #
################################################################

################################################################


        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:


            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.location.x
            args = (self, context)



            cArrID=-1
            n=-1
            nrf=False




            args = (self, context)

            self.id=int(cArrID)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}







addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)

#addon_keymaps = [] #put on out of register()
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)

    # kmi = km.keymap_items.new(rotate_gesture.bl_idname, 'D', 'PRESS', shift=True, ctrl=True)
    kmi = km.keymap_items.new(rotate_gesture.bl_idname, 'D', 'PRESS', oskey=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(rotate_gesture.bl_idname, 'D', 'PRESS', shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
