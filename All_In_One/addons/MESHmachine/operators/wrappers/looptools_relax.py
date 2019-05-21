import bpy
import bmesh
from bpy.props import BoolProperty, FloatProperty, EnumProperty
from ... utils.developer import output_traceback
from ... utils.ui import draw_init, draw_end, draw_title, draw_prop, wrap_mouse, step_enum
from ... utils import MACHIN3 as m3




inputitems = [("all", "Parallel (all)", "Also use non-selected " "parallel loops as input"),
              ("selected", "Selection", "Only use selected vertices as input")]

interpolationitems = [("cubic", "Cubic", "Natural cubic spline, smooth results"),
                      ("linear", "Linear", "Simple and fast linear algorithm")]

iterationsitems = [("1", "1", "One"),
                   ("3", "3", "Three"),
                   ("5", "5", "Five"),
                   ("10", "10", "Ten"),
                   ("25", "25", "Twenty-five")]


class RelaxSettings:
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type']:
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


class LoopToolsRelax(bpy.types.Operator, RelaxSettings):
    bl_idname = "machin3.looptools_relax"
    bl_label = "MACHIN3: LoopTools Relax"
    bl_options = {'REGISTER', 'UNDO'}

    iterations = EnumProperty(name="Iterations", items=iterationsitems, description="Number of times the loop is relaxed", default="1")

    input = EnumProperty(name="Input", items=inputitems, description="Loops that are relaxed", default='selected')
    interpolation = EnumProperty(name="Interpolation", items=interpolationitems, description="Algorithm used for interpolation", default='cubic')

    regular = BoolProperty(name="Regular", description="Distribute vertices at constant distances along the loop", default=False)


    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Relax", subtitle="LoopTools")

        draw_prop(self, "Iterations", self.iterations, key="scroll UP/DOWN")
        draw_prop(self, "Regular", self.regular, offset=18, key="toggle R")
        self.offset += 10

        draw_prop(self, "Input", self.input, offset=18, key="CTRL scroll UP/DOWN")
        draw_prop(self, "Interpolation", self.interpolation, offset=18, key="ALT scroll UP/DOWN")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        if event.type in ['WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO', 'R']:

            if event.type in {'WHEELUPMOUSE', 'ONE'} and event.value == 'PRESS':
                if event.ctrl:
                    self.input = step_enum(self.input, inputitems, 1)
                elif event.alt:
                    self.interpolation = step_enum(self.interpolation, interpolationitems, 1)
                else:
                    self.iterations = step_enum(self.iterations, iterationsitems, 1, loop=False)

            elif event.type in {'WHEELDOWNMOUSE', 'TWO'} and event.value == 'PRESS':
                if event.ctrl:
                    self.input = step_enum(self.input, inputitems, -1)
                elif event.alt:
                    self.interpolation = step_enum(self.interpolation, interpolationitems, -1)
                else:
                    self.iterations = step_enum(self.iterations, iterationsitems, -1, loop=False)

            elif event.type == 'R' and event.value == "PRESS":
                self.regular = not self.regular

            # modal relax
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

        bpy.ops.mesh.looptools_relax(input=self.input, interpolation=self.interpolation, iterations=self.iterations, regular=self.regular)

        return True
