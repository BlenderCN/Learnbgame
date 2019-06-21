import bpy

from .func_bgl import draw_callback_px
from .func_bgl import select_bone
from .func_picker import *
from .utils import is_over_region


class FunctionExecute(bpy.types.Operator) :
    bl_idname = "rigui.function_execute"
    bl_label = 'Function Execute'

    shape_index = bpy.props.IntProperty()

    def execute(self,context) :
        event = self.event
        ob = context.object
        shape = ob.data.UI['shapes'][self.shape_index]

        function = shape['function']
        if shape.get('variables') :
            variables=shape['variables'].to_dict()


        else :
            variables={}

        variables['event']=event
        globals()[function](variables)

        return {'FINISHED'}

    def invoke(self,context,event) :
        self.event = event
        return self.execute(context)


class UIDraw(bpy.types.Operator):
    bl_idname = "rigui.ui_draw"
    bl_label = "Rig UI Draw"

    _handle = None
    tmp_ob = None
    tmp_bones = []
    start = (0,0)
    end = (0,0)
    border = ((0,0),(0,0),(0,0),(0,0))
    is_border = False
    press = False
    scale = 1
    offset = 0
    outside_point = (-1,-1)
    addon_keymaps = []

    def set_shorcut(self,context) :
        ob = context.object
        addon = bpy.context.window_manager.keyconfigs.addon

        if ob and ob.type =='ARMATURE' and ob.data.UI and addon:
            for i,shape in [(i,s) for i,s in enumerate(ob.data.UI['shapes']) if s.get('function') and s.get('shortcut')] :
                km = addon.keymaps.new(name = 'Image Generic', space_type = 'IMAGE_EDITOR',region_type = 'WINDOW')

                split = shape["shortcut"].split(' ')
                if len(split)==1 :
                    shortcut = shape["shortcut"].upper()
                    modifier = None
                else :
                    shortcut = split[1].upper()
                    modifier = split[0].lower()

                kmi = km.keymap_items.new("rigui.function_execute", type = shortcut, value = "CLICK")
                kmi.properties.shape_index = i

                if modifier :
                    setattr(kmi,modifier,True)

                self.addon_keymaps.append(km)

    def remove_shorcut(self,context) :
        # Remove Shortcut
        wm = bpy.context.window_manager
        for km in self.addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

        self.addon_keymaps.clear()

    def modal(self, context, event):
        inside = is_over_region(self,context,event)

        if context.object and context.object.type == 'ARMATURE' and context.area :
            if not context.screen.is_animation_playing :
                if self.tmp_ob != context.object :
                    context.area.tag_redraw()
                    self.remove_shorcut(context)
                    self.set_shorcut(context)
                    self.tmp_ob = context.object

                if self.tmp_bones != context.selected_pose_bones :
                    context.area.tag_redraw()
                    self.tmp_bones = context.selected_pose_bones

                if inside :
                    context.area.tag_redraw()

            if event.type == 'LEFTMOUSE' :
                if event.value == 'PRESS': # start selection
                    if inside:
                        self.start = (event.mouse_region_x,event.mouse_region_y)
                        self.press = True

                elif event.value == 'RELEASE'  and self.press:
                    self.end = (event.mouse_region_x,event.mouse_region_y)

                    select_bone(self,context,event)
                    bpy.ops.ed.undo_push()

                    self.is_border= False
                    self.press = False

            if event.type == 'MOUSEMOVE' :
                self.end = (event.mouse_region_x,event.mouse_region_y)

                if self.press :
                    b_x = (min(self.start[0],self.end[0]),max(self.start[0],self.end[0]))
                    b_y = (min(self.start[1],self.end[1]),max(self.start[1],self.end[1]))
                    self.border = ((b_x[0],b_y[1]),(b_x[1],b_y[1]),(b_x[1],b_y[0]),(b_x[0],b_y[0]))
                    self.is_border= True if (b_x[1]-b_x[0])+(b_y[1]-b_y[0]) > 4 else False

                if self.is_border :
                    select_bone(self,context,event)

            elif event.type in {'ESC',} and inside:
                bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
                self.remove_shorcut(context)


                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        #shortcut Creation



        context.space_data.image = None
        self.adress = context.area.as_pointer()
        args = (self, context)

        self._handle = bpy.types.SpaceImageEditor.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')


        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
