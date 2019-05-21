import bpy

from ..functions import store_ui_data
from ..functions import draw_callback_px
from ..functions import select_bone

class StoreUIData(bpy.types.Operator):
    bl_label = "Store UI Data"
    bl_idname = "rigui.store_ui_data"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        canevas=None
        objects = bpy.context.selected_objects
        rig = bpy.context.object

        for ob in objects :
            if ob.name.endswith('canevas.display') :
                canevas = ob

        if rig.type == 'ARMATURE' and canevas:
            objects.remove(rig)
            store_ui_data(objects,canevas,rig)

        else :
            self.report({'INFO'},'active object not rig or canevas not found')

        return {'FINISHED'}

class UIDraw(bpy.types.Operator):
    bl_idname = "rigui.ui_draw"
    bl_label = "Rig UI Draw"

    _handle = None
    adress = bpy.props.IntProperty()

    start_x = bpy.props.IntProperty(default = 0)
    start_y = bpy.props.IntProperty(default = 0)
    end_x = bpy.props.IntProperty()
    end_y = bpy.props.IntProperty()
    border = bpy.props.BoolProperty()
    #selecting = BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type=='ARMATURE')

    def modal(self, context, event):
        context.area.tag_redraw()
        in_x = 2 < event.mouse_region_x < context.region.width-2
        in_y = 2 < event.mouse_region_y < context.region.height-2

        if in_x and in_y:

            if event.type == 'MOUSEMOVE':
                self.end_x = event.mouse_region_x
                self.end_y = event.mouse_region_y


                if self.border :
                    select_bone(self,context,event)

            elif event.type == 'LEFTMOUSE':
                if event.value == 'PRESS': # start selection
                    #self.selecting = True
                    self.start_x = event.mouse_region_x
                    self.start_y = event.mouse_region_y


                    self.border= True


                if event.value == 'RELEASE': # end of selection
                    self.end_x = event.mouse_region_x
                    self.end_y = event.mouse_region_y
                    #print(self.start_x,self.end_x ,self.start_y,self.end_y)
                    self.border= False


                    select_bone(self,context,event)

            elif event.type in {'ESC',}:
                #bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                context.space_data.draw_handler_remove(self._handle, 'WINDOW')
                #self._finish(context)
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        #if context.area.type == 'VIEW_3D':
        #self.adress = context.space_data.as_pointer()
        #context.window_manager.modal_handler_add(self)
        args = (self, context)

        # Add the region OpenGL drawing callback
        # draw in view space with 'POST_VIEW' and 'PRE_VIEW'

        self._handle = context.space_data.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        self.mouse = (0,0)

        context.window.cursor_modal_set('DEFAULT')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        #else:
            #self.report({'WARNING'}, "View3D not found, cannot run operator")
            #return {'CANCELLED'}
