import bpy
import blf
import math
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Matrix
from bpy.props import (IntProperty,
                       FloatProperty,
                       BoolProperty,
                       StringProperty,
                       FloatVectorProperty)
from mathutils import Vector, Matrix
from ..iops import IOPS


# ----------------------------  UI  ---------------------------------------

def draw_line_cursor(self, context):
    coords = self.gpu_verts
    shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": coords})
    shader.bind()
    shader.uniform_float("color", (0.1, 0.6, 0.4, 1))
    batch.draw(shader)
    # pass


def draw_ui(self, context, _uidpi, _uifactor):

    def get_target():
        if self.target == context.scene.cursor:
            return "3D Cursor"
        elif self.target == context.view_layer.objects.active:
            return "Active object" 
    
    prefs = bpy.context.preferences.addons['InteractionOps'].preferences
    tColor = prefs.text_color
    tKColor = prefs.text_color_key
    tCSize = prefs.text_size
    tCPosX = prefs.text_pos_x
    tCPosY = prefs.text_pos_y
    tShadow = prefs.text_shadow_toggle           
    tSColor = prefs.text_shadow_color    
    tSBlur = prefs.text_shadow_blur
    tSPosX = prefs.text_shadow_pos_x
    tSPosY = prefs.text_shadow_pos_y  
    
    _target = get_target()
    iops_text = (
        ("Look at", str(_target)),
        ("Look at axis", str(self.look_axis[0])),
        ("Match cursor's rotation", str(self.rotate)),
        ("Align to cursor's pos", "F3"),
        ("Visual origin helper", "F4"),        
        )

    # FontID    
    font = 0
    blf.color(font, tColor[0], tColor[1], tColor[2], tColor[3]) 
    blf.size(font, tCSize, _uidpi)
    if tShadow:
        blf.enable(font, blf.SHADOW)
        blf.shadow(font, int(tSBlur), tSColor[0], tSColor[1], tSColor[2], tSColor[3])
        blf.shadow_offset(font, tSPosX, tSPosY)
    else:
        blf.disable(0, blf.SHADOW)

    textsize = tCSize    
    # get leftbottom corner
    offset = tCPosY
    columnoffs = (textsize * 15) * _uifactor 
    for line in reversed(iops_text):         
        blf.color(font, tColor[0], tColor[1], tColor[2], tColor[3])
        blf.position(font, tCPosX * _uifactor, offset, 0)
        blf.draw(font, line[0])

        blf.color(font, tKColor[0], tKColor[1], tKColor[2], tKColor[3])
        textdim = blf.dimensions(0, line[1])
        coloffset = columnoffs - textdim[0] + tCPosX     
        blf.position(0, coloffset, offset, 0)
        blf.draw(font, line[1])
        offset += (tCSize + 5) * _uifactor 


class IOPS_OT_CursorOrigin_Mesh(IOPS):
    bl_idname = "iops.cursor_origin_mesh"
    bl_label = "MESH: Object mode - Align to cursor"
    orig_mxs = []
    rotate = False
    flip = False
    target = None
    look_axis = []
    gpu_verts = []

    @classmethod
    def poll(self, context):
        return (context.area.type == "VIEW_3D" and
                context.mode == "OBJECT" and
                context.view_layer.objects.active.type == "MESH"
                and len(context.view_layer.objects.selected) != 0)

    def move_to_cursor(self, rotate):
        scene = bpy.context.scene
        objs = bpy.context.selected_objects
        for ob in objs:
            ob.location = scene.cursor.location
            if rotate:
                ob.rotation_euler = scene.cursor.rotation_euler

    def look_at(self, context, target, axis, flip):
        objs = bpy.context.selected_objects
        self.gpu_verts = []

        for o in objs:
            # Reset matrix
            q = o.matrix_world.to_quaternion()
            m = q.to_matrix()
            m = m.to_4x4()
            o.matrix_world @= m.inverted()
           
            self.gpu_verts.append(o.location)
            self.gpu_verts.append(target.location)

            v = Vector(o.location - target.location)
            if flip:
                rot_mx = v.to_track_quat("-" + axis[0], axis[1]).to_matrix().to_4x4()
            else:
                rot_mx = v.to_track_quat(axis[0], axis[1]).to_matrix().to_4x4()
            o.matrix_world @= rot_mx
    
    def modal(self, context, event):
            context.area.tag_redraw()
            objs = context.selected_objects

            if event.type in {'MIDDLEMOUSE'}:
                # Allow navigation
                return {'PASS_THROUGH'}

            elif event.type == "F4" and event.value == "PRESS":
                    bpy.ops.iops.visual_origin('INVOKE_DEFAULT')                          
                    bpy.types.SpaceView3D.draw_handler_remove(self._handle_cursor, "WINDOW")
                    bpy.types.SpaceView3D.draw_handler_remove(self._handle_ui, "WINDOW")
                    return {'FINISHED'}

            elif event.type == "F1" and event.value == "PRESS":
                    self.flip = not self.flip
                    self.target = context.scene.cursor
                    self.look_at(context, self.target, self.look_axis, self.flip)
                    self.report({"INFO"}, event.type)

            elif event.type == "F2" and event.value == "PRESS":
                    self.flip = not self.flip
                    self.target = context.view_layer.objects.active
                    self.look_at(context, self.target, self.look_axis, self.flip)
                    self.report({"INFO"}, event.type)

            elif event.type == "X" and event.value == "PRESS":
                    self.flip = not self.flip
                    self.look_axis = [("X"), ("Z")]
                    self.look_at(context, self.target, self.look_axis, self.flip)
                    self.report({"INFO"}, event.type)

            elif event.type == "Y" and event.value == "PRESS":
                    self.flip = not self.flip
                    self.look_axis = [("Y"), ("X")]
                    self.look_at(context, self.target, self.look_axis, self.flip)
                    self.report({"INFO"}, event.type)

            elif event.type == "Z" and event.value == "PRESS":
                    self.flip = not self.flip
                    self.look_axis = [("Z"), ("Y")]
                    self.look_at(context, self.target, self.look_axis, self.flip)
                    self.report({"INFO"}, event.type)
            
            elif event.type == "F3" and event.value == "PRESS":
                    for o, m in zip(objs, self.orig_mxs):
                        o.matrix_world = m
                    self.rotate = not self.rotate
                    self.move_to_cursor(self.rotate)
                    self.report({"INFO"}, event.type)

            elif event.type in {"LEFTMOUSE", "SPACE"} and event.value == "PRESS":
                # self.execute(context)
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_cursor, "WINDOW")
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_ui, "WINDOW")
                return {"FINISHED"}

            elif event.type in {"RIGHTMOUSE", "ESC"}:
                for o, m in zip(objs, self.orig_mxs):
                    o.matrix_world = m
                # clean up
                self.orig_mxs = []

                bpy.types.SpaceView3D.draw_handler_remove(self._handle_cursor, "WINDOW")
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_ui, "WINDOW")
                return {"CANCELLED"}

            return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        self.orig_mxs = []
        self.gpu_verts = []
        self.look_axis = [("Z"), ("Y")]
        self.target = context.scene.cursor
        objs = context.selected_objects
        preferences = context.preferences
        # Store matricies for undo
        for o in objs:
            self.orig_mxs.append(o.matrix_world.copy())

        if context.object and context.area.type == "VIEW_3D":
            # Add drawing handler for text overlay rendering         
            uidpi = int((72 * preferences.system.ui_scale))
            args = (self, context, uidpi, preferences.system.ui_scale)
            self._handle_ui = bpy.types.SpaceView3D.draw_handler_add(
                            draw_ui,
                            args,
                            'WINDOW',
                            'POST_PIXEL')
            args_line = (self, context)
            self._handle_cursor = bpy.types.SpaceView3D.draw_handler_add(
                            draw_line_cursor,
                            args_line,
                            'WINDOW',
                            'POST_VIEW')

            # Add modal handler to enter modal mode
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "No active object, could not finish")
            return {"CANCELLED"}
