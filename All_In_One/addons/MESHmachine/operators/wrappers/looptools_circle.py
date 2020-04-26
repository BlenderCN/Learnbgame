import bpy
import bmesh
from bpy.props import BoolProperty, FloatProperty, EnumProperty
from ... utils.developer import output_traceback
from ... utils.ui import draw_init, draw_end, draw_title, draw_prop, wrap_mouse, step_enum
from ... utils import MACHIN3 as m3



methoditems = [("best", "Best fit", "Non-linear least squares"),
               ("inside", "Fit inside", "Only move vertices towards the center")]


class CircleSettings:
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'allowmodalradius', 'allowmodalinfluence']:
                continue
            try:
                self.__class__._settings[d] = self.properties[d]
            except KeyError:
                # catches __doc__ etc.
                continue

    def load_settings(self):
        # what exception could occur here??
        for d in self.__class__._settings:
            self.properties[d] = self.__class__._settings[d]


class LoopToolsCircle(bpy.types.Operator, CircleSettings):
    bl_idname = "machin3.looptools_circle"
    bl_label = "MACHIN3: LoopTools Circle"
    bl_options = {'REGISTER', 'UNDO'}

    method = EnumProperty(name="Method", items=methoditems, default='best')

    influence = FloatProperty(name="Influence", description="Force of the tool", default=100.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE')

    flatten = BoolProperty(name="Flatten", description="Flatten the circle, instead of projecting it on the mesh", default=True)
    regular = BoolProperty(name="Regular", description="Distribute vertices at constant distances along the circle", default=False)

    custom_radius = BoolProperty(name="Radius", description="Force a custom radius", default=False)
    radius = FloatProperty(name="Radius", description="Custom radius for circle", default=1.0, min=0.0, soft_max=1000.0)

    lock_x = BoolProperty(name="Lock X", description="Lock editing of the x-coordinate", default=False)
    lock_y = BoolProperty(name="Lock Y", description="Lock editing of the y-coordinate", default=False)
    lock_z = BoolProperty(name="Lock Z", description="Lock editing of the z-coordinate", default=False)

    # modal
    allowmodalradius = BoolProperty(default=False)
    allowmodalinfluence = BoolProperty(default=False)

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Circle", subtitle="LoopTools")

        draw_prop(self, "Method", self.method, key="scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "Flatten", self.flatten, offset=18, key="toggle F")
        draw_prop(self, "Regular", self.regular, offset=18, key="toggle R")
        self.offset += 10

        draw_prop(self, "Custom Radius", self.custom_radius, offset=18, key="toggle C")
        draw_prop(self, "Radius", self.radius, offset=18, active=self.allowmodalradius, key="move LEFT/RIGHT, toggle W, reset ALT + W")
        draw_prop(self, "Influence", self.influence, offset=18, active=self.allowmodalinfluence, key="move UP/DOWN, toggle I, reset ALT + I")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO', 'C', 'W', 'I', 'F', 'R']

        # only consider MOUSEMOVE as a trigger for main(), when modalradius or modalinfluence are actually active
        if any([self.allowmodalradius, self.allowmodalinfluence]):
            events.append('MOUSEMOVE')

        if event.type in events:
            if event.type == 'MOUSEMOVE':
                delta_x = self.mouse_x - self.init_mouse_x   # bigger if going to the right
                delta_y = self.mouse_y - self.init_mouse_y   # bigger if going to the right

                if self.allowmodalradius:
                    wrap_mouse(self, context, event, x=True)
                    self.radius = delta_x * 0.001 + 0.5

                if self.allowmodalinfluence:
                    wrap_mouse(self, context, event, y=True)
                    self.influence = delta_y * 0.1 + 100

            elif event.type in {'WHEELUPMOUSE', 'ONE'} and event.value == 'PRESS':
                self.method = step_enum(self.method, methoditems, 1)

            elif event.type in {'WHEELDOWNMOUSE', 'TWO'} and event.value == 'PRESS':
                self.method = step_enum(self.method, methoditems, -1)


            elif event.type == 'C' and event.value == "PRESS":
                self.custom_radius = not self.custom_radius

            elif event.type == 'W' and event.value == "PRESS":
                if event.alt:
                    self.allowmodalradius = False
                    self.radius = 1
                else:
                    self.allowmodalradius = not self.allowmodalradius
                    if not self.custom_radius:
                        self.custom_radius = True

            elif event.type == 'I' and event.value == "PRESS":
                if event.alt:
                    self.allowmodalinfluence = False
                    self.influence = 100
                else:
                    self.allowmodalinfluence = not self.allowmodalinfluence

            elif event.type == 'F' and event.value == "PRESS":
                self.flatten = not self.flatten

            elif event.type == 'R' and event.value == "PRESS":
                self.regular = not self.regular

            # modal circle
            try:
                self.ret = self.main(self.active, modal=True)

                # success
                if self.ret:
                    self.save_settings()
                # caught an error
                else:
                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    return {'FINISHED'}

            # unexpected error
            except:
                output_traceback(self)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                mode = m3.get_mode()
                if mode == "OBJECT":
                    m3.set_mode("EDIT")
                return {'FINISHED'}


        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        m3.set_mode("OBJECT")
        self.initbm.to_mesh(self.active.data)
        m3.set_mode("EDIT")

    def invoke(self, context, event):
        self.load_settings()
        self.active = m3.get_active()

        # make sure the current edit mode state is saved to obj.data
        self.active.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal and to reset it for each mousemove event
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        try:
            self.ret = self.main(self.active, modal=True)
            if self.ret:
                self.save_settings()
            else:
                self.cancel_modal(removeHUD=False)
                return {'FINISHED'}
        except:
            output_traceback(self)
            mode = m3.get_mode()
            if mode == "OBJECT":
                m3.set_mode("EDIT")
            return {'FINISHED'}

        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        active = m3.get_active()

        self.main(active)
        return {'FINISHED'}

    def main(self, active, modal=False):
        if modal:
            m3.set_mode("OBJECT")
            self.initbm.to_mesh(active.data)
            m3.set_mode("EDIT")

        bpy.ops.mesh.looptools_circle(custom_radius=self.custom_radius, fit=self.method, flatten=self.flatten, influence=self.influence, lock_x=self.lock_x, lock_y=self.lock_y, lock_z=self.lock_z, radius=self.radius, regular=self.regular)

        return True
