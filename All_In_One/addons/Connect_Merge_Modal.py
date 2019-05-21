import bpy
import bgl

bl_info = {
    "name": "Connect-Merge-Modal",
    "category": "User",
    "author": "Andreas Strømberg",
}


def draw_callback_px(self, context):
    # 50% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    bgl.glLineWidth(4)

    bgl.glBegin(bgl.GL_LINES)
    if self.started:
        bgl.glVertex2i(self.start_vertex[0], self.start_vertex[1])
        bgl.glVertex2i(self.end_vertex[0], self.end_vertex[1])

    bgl.glEnd()

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def main(context, event, started):
    """Run this function on left mouse, execute the ray cast"""
    coord = event.mouse_region_x, event.mouse_region_y

    if started:
        result = bpy.ops.view3d.select(extend=True, location=coord)
    else:
        result = bpy.ops.view3d.select(extend=False, location=coord)

    if result == {'PASS_THROUGH'}:
        bpy.ops.mesh.select_all(action='DESELECT')


#Connect modal
class RMB_Smart_Connect_Tool_Raycast(bpy.types.Operator):
    """Modal object selection with a ray cast"""
    bl_idname = "object.smart_connect_tool_raycast"
    bl_label = "Connect-Merge Tool"
    bl_options = {'REGISTER'}

    def __init__(self):
        self.started = None
        self.start_vertex = None
        self.end_vertex = None
        self._handle = None

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        elif event.type == 'MOUSEMOVE':
            if self.started:
                self.end_vertex = (event.mouse_region_x, event.mouse_region_y)

        elif event.type == 'LEFTMOUSE':
            main(context, event, self.started)
            if not self.started:
                if context.object.data.total_vert_sel == 1:
                    self.start_vertex = (event.mouse_region_x, event.mouse_region_y)
                    self.end_vertex = (event.mouse_region_x, event.mouse_region_y)
                    self.started = True
            elif context.object.data.total_vert_sel == 2:
                
                if event.shift:
                    bpy.ops.mesh.merge(type='CENTER')
                else:
                    bpy.ops.mesh.vert_connect_path()
                if event.ctrl:
                    bpy.ops.mesh.merge(type='LAST')
                    
                bpy.ops.ed.undo_push(message="Add an undo step *function may be moved*")
                self.started = False
            
            return {'RUNNING_MODAL'}
        
        elif event.type == 'SPACE':
            self.started = False
        
        elif event.ctrl and event.type == 'Z' and event.value == 'PRESS':
            bpy.ops.ed.undo()   
            
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            args = (self, context)

            self.start_vertex = (0, 0)
            self.end_vertex = (0, 0)
            
            context.window_manager.modal_handler_add(self)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            context.area.header_text_set("Click: Continuous Connect, Drag+Click: Connect, Shift+Click: merge at Center, Ctrl+Click: Merge at Last, Space: Restart Auto Connect, RMB/ESC: Exit") 
            self.started = False
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(RMB_Smart_Connect_Tool_Raycast)


def unregister():
    bpy.utils.unregister_class(RMB_Smart_Connect_Tool_Raycast)

if __name__ == "__main__":
    register()
