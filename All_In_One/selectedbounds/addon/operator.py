import bpy

from bpy.types import Operator

from bgl import glEnable, GL_BLEND, GL_DEPTH_TEST, glColor4f, glLineWidth, glBegin, GL_LINES, glVertex3f, glEnd, glDisable

from mathutils import Vector

class selected_bounds(Operator):
    bl_idname = 'view3d.selected_bounds'
    bl_label = 'Initialize Bounds'
    bl_description = 'Initialize bound indicator drawing. (Persistent)'
    bl_options = {'INTERNAL'}


    def execute(self, context):

        context.window_manager.is_selected_bounds_drawn = True

        bpy.types.SpaceView3D.draw_handler_add(draw_bounds, (self, context), 'WINDOW', 'PRE_VIEW')

        return {'FINISHED'}

def draw_bounds(self, context):

    try: addon = context.user_preferences.addons[__name__.partition('.')[0]]
    except: pass

    if context.window_manager.selected_bounds:

        if context.active_object and not context.active_object.hide:
            option = context.scene.selected_bounds if addon.preferences.scene_independent else addon.preferences

            if context.object and option.mode != 'NONE' and context.object.mode in {'OBJECT', 'EDIT'} and context.space_data.viewport_shade in {'SOLID', 'WIREFRAME'} and not context.space_data.show_only_render:

                glEnable(GL_BLEND)
                glEnable(GL_DEPTH_TEST)

                glLineWidth(option.width)

                length = float(option.length) * 0.01

                if option.mode == 'ACTIVE':

                    if context.object.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE'}:

                        color = option.color if not option.use_object_color else context.object.color
                        glColor4f(color[0], color[1], color[2], color[3])

                        matrix = context.object.matrix_world
                        bounds = context.object.bound_box

                        draw_corners(length, matrix, bounds)

                elif option.mode == 'SELECTED':

                    for object in context.selected_objects:

                        if object.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LATTICE'}:

                            color = option.color if not option.use_object_color else object.color
                            glColor4f(color[0], color[1], color[2], color[3])

                            matrix = object.matrix_world
                            bounds = object.bound_box

                            draw_corners(length, matrix, bounds)

                glDisable(GL_DEPTH_TEST)
                glDisable(GL_BLEND)

def draw_corners(length, matrix, bounds):

    for index in range(0, 8):

        pointer_x = index + 4 if index < 4 else index - 4

        pointer_y = 3 - index if index < 4 else 10 - (index - 1)

        pointer_z = index + 1 if index % 2 == 0 else index - 1

        draw_lines(length, matrix, bounds[index], bounds[pointer_x], bounds[pointer_y], bounds[pointer_z])


def draw_lines(length, matrix, origin, x, y, z):

    x = (origin[0] - (origin[0] - x[0])*length, x[1], x[2])
    y = (y[0], origin[1] - (origin[1] - y[1])*length, y[2])
    z = (z[0], z[1], origin[2] - (origin[2] - z[2])*length)

    origin = matrix * Vector(origin)
    x = matrix * Vector(x)
    y = matrix * Vector(y)
    z = matrix * Vector(z)

    glBegin(GL_LINES)

    glVertex3f(origin[0], origin[1], origin[2])
    glVertex3f(x[0], x[1], x[2])
    glVertex3f(origin[0], origin[1], origin[2])
    glVertex3f(y[0], y[1], y[2])
    glVertex3f(origin[0], origin[1], origin[2])
    glVertex3f(z[0], z[1], z[2])

    glEnd()
