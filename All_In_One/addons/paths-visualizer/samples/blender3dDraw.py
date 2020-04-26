import bpy
import bgl
from bgl import *
import blf
import bmesh
from mathutils import *
from math import *

def draw_callback_px(self, context, displayListIndex):
        
    ob = context.object
    if ob is None:
        return

    # 50% alpha, 2 pixel width line
    glEnable(GL_BLEND)
    glColor4f(1.0, 1.0, 1.0, 0.5)
    glLineWidth(2)
    
    glPushMatrix()
    glTranslatef(*ob.location)
    glCallList(displayListIndex)
    glPopMatrix()

    # restore opengl defaults
    glLineWidth(1)
    glDisable(GL_BLEND)
    glColor4f(0.0, 0.0, 0.0, 1.0)

def createArrowDisplayList(context):
    ob = context.object
    if ob is None:
        return
    
    if bpy.context.active_object.mode != 'EDIT':
        return
        
    ob = context.edit_object
    me = ob.data
    
    bm = bmesh.from_edit_mesh(me)
    index = glGenLists(1)
    
    glNewList(index, GL_COMPILE)
    for e in bm.edges:
        vecFrom = e.verts[0].co
        vecTo = e.verts[1].co
        
        middle = (Vector(vecTo) + Vector(vecFrom)) / 2.0
        
        v = Vector(vecTo) - Vector(vecFrom)
        v.normalize()
        
        vPerp1 = Vector((-v.y, v.x, 0.0))
        vPerp2 = Vector((v.y, -v.x, 0.0))
        
        v1 = (vPerp1 - v).normalized()
        v2 = (vPerp2 - v).normalized()
        
        glBegin(GL_LINE_STRIP)
        glVertex3f(*(middle + v1))
        glVertex3f(*(middle))
        glVertex3f(*(middle + v2))
        glEnd()
    glEndList()
        
    return index
    
class ModalDrawOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            index = createArrowDisplayList(context)
            # the arguments we pass the the callback
            args = (self, context, index)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_VIEW')
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)

if __name__ == "__main__":
    register()

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            bpy.ops.view3d.modal_operator({'area': area}, 'INVOKE_DEFAULT')
            break