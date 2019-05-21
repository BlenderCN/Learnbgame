import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty
import bgl
import mathutils
from bpy_extras import view3d_utils
from .. utils.ui import draw_init, draw_end, draw_title, draw_prop, step_enum
from .. utils.raycast import cast_ray
from .. utils import MACHIN3 as m3


coloritems = [("BLACK", "Black", ""),
              ("WHITE", "White", ""),
              ("RED", "Red", ""),
              ("GREEN", "Green", ""),
              ("BLUE", "Blue", "")]

coloritems.reverse()

colorcodes = {"BLACK": (0, 0, 0),
              "WHITE": (1, 1, 1),
              "RED": (1, 0, 0),
              "GREEN": (0, 1, 0),
              "BLUE": (0, 0, 1)}


class OperatorSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
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


class Tape(bpy.types.Operator, OperatorSettings):
    bl_idname = "machin3.tape"
    bl_label = "MACHIN3: Tape"
    bl_options = {'REGISTER', 'UNDO'}

    thickness = IntProperty(name="Thickness", min=1, max=10, default=4)
    spacing = IntProperty(name="Spacing", min=1, max=30, default=6)
    xray = BoolProperty(name="X Ray", default=False)

    color = EnumProperty(name="Color", items=coloritems, default="BLACK")

    alpha = FloatProperty(name="Alpha", min=.1, max=1, default=1)


    def draw_lines(self, args):
        self, context = args

        # draw confirmed lines
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(self.thickness)

        bgl.glColor4f(*colorcodes[self.color], self.alpha)
        bgl.glBegin(bgl.GL_LINE_STRIP)

        for x, y in self.mouse_coords:
            bgl.glVertex2i(int(x), int(y))
        bgl.glEnd()

        # draw preview line
        if self.mouse_coords:
            # see https://blender.stackexchange.com/a/21526/33919
            bgl.glPushAttrib(bgl.GL_ENABLE_BIT)

            bgl.glLineStipple(1, 0x9999)
            bgl.glEnable(bgl.GL_LINE_STIPPLE)

            # 50% alpha, 2 pixel width line
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(*colorcodes[self.color], 0.4)
            bgl.glLineWidth(self.thickness)

            bgl.glBegin(bgl.GL_LINE_STRIP)
            for x, y in [self.mouse_coords[-1], mathutils.Vector((self.mouse_x, self.mouse_y))]:
                bgl.glVertex2i(int(x), int(y))

            bgl.glEnd()
            bgl.glPopAttrib()

        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def draw_HUD(self, args):
        draw_init(self, args)

        _, context = args
        draw_title(self, "Tape", subtitle="Frame %d" % context.scene.frame_current, subtitleoffset=125)

        draw_prop(self, "Thickness", self.thickness, key="scroll UP/DOWN")
        draw_prop(self, "Spacing", self.spacing, offset=18, key="SHIFT scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "Color", self.color, offset=18, key="CTRL scroll UP/DOWN")
        draw_prop(self, "Alpha", self.alpha, offset=18, decimal=1, key="ALT scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "X Ray", self.xray, offset=18, key="toggle X")
        self.offset += 10

        draw_prop(self, "Undos", len(self.undos), offset=18, active=len(self.undos) > 0, key="undo CTRL + Z or F1, redo CTRL + SHIFT + Z or F2")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        elif event.type == 'LEFTMOUSE' and event.value == "PRESS":
            # add the current location
            self.mouse_coords.append(mathutils.Vector((self.mouse_x, self.mouse_y)))
            return {'RUNNING_MODAL'}


        # ctrl + z undo, ctrl + shift +z redo
        elif event.type == "Z" and event.value == 'PRESS':
            if event.ctrl:
                if event.shift:
                    if self.undos:
                        self.mouse_coords.append(self.undos[-1])
                        self.undos = self.undos[:-1]
                else:
                    if self.mouse_coords:
                        self.undos.append(self.mouse_coords[-1])
                        self.mouse_coords = self.mouse_coords[:-1]

        # f1 undo, f2 redo
        elif event.type == "F1" and event.value == 'PRESS':
            if self.mouse_coords:
                self.undos.append(self.mouse_coords[-1])
                self.mouse_coords = self.mouse_coords[:-1]

        elif event.type == "F2" and event.value == 'PRESS':
            if self.undos:
                self.mouse_coords.append(self.undos[-1])
                self.undos = self.undos[:-1]


        elif event.type == 'WHEELUPMOUSE':
            if event.ctrl:
                self.color = step_enum(self.color, coloritems, 1)
            elif event.alt:
                self.alpha += 0.1
            elif event.shift:
                self.spacing += 1
            else:
                self.thickness += 1

        elif event.type == 'WHEELDOWNMOUSE':
            if event.ctrl:
                self.color = step_enum(self.color, coloritems, -1)
            elif event.alt:
                self.alpha -= 0.1
            elif event.shift:
                self.spacing -= 1
            else:
                self.thickness -= 1

        elif event.type == 'X' and event.value == 'PRESS':
            self.xray = not self.xray

        # draw gpencil and finish
        elif event.type == 'SPACE':
            # interpolate strokes
            if len(self.mouse_coords) < 1:
                print("cancelled")
                bpy.types.SpaceView3D.draw_handler_remove(self.lines, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                context.window.cursor_set('DEFAULT')
                return {'CANCELLED'}
            else:
                strokes = []
                for idx, co in enumerate(self.mouse_coords):
                    if idx == len(self.mouse_coords) - 1:
                        break
                    strokes.append((co, self.mouse_coords[idx + 1]))

                strokes_interpolated = []

                for v1co, v2co in strokes:
                    # get direction and lenghts of the vector from v1 to v2
                    v12_dir = (v2co - v1co)
                    v12_len = v12_dir.length

                    # make the density depend on the lengths of the vector, this way it will be an even vert distribution all times
                    density = int(int(v12_len) / self.spacing)

                    stroke = [v1co]

                    for i in range(1, density):
                        factor = i / (density - 1)
                        stroke.append(v1co + v12_dir * factor)

                    strokes_interpolated.append(stroke)

                # project
                hits = []
                for stroke in strokes_interpolated:
                    for coord in stroke:
                        hitobj, hitco, _, _ = cast_ray(context, coord)

                        if hitobj:
                            hits.append((hitobj, hitco))

                if len(hits) > 1:
                    gpcoords = [co for _, co in hits]
                    gpencil(context, gpcoords, self.thickness, self.color, self.alpha, self.xray, debug=self.debug)

                bpy.types.SpaceView3D.draw_handler_remove(self.lines, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                context.window.cursor_set('DEFAULT')

                self.save_settings()
                return {'FINISHED'}

        elif event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("cancelled")
            bpy.types.SpaceView3D.draw_handler_remove(self.lines, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            context.window.cursor_set('DEFAULT')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.load_settings()

        self.debug = False
        # self.debug = True

        self.mouse_coords = []

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # undo
        self.undos = []

        context.window.cursor_set('CROSSHAIR')

        args = (self, context)
        self.lines = bpy.types.SpaceView3D.draw_handler_add(self.draw_lines, (args, ), 'WINDOW', 'POST_PIXEL')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def gpencil(context, coords, thickness, color, alpha, xray, debug=False):
    scene = context.scene
    context.space_data.show_grease_pencil = True

    # get/create GTape
    gp = bpy.data.grease_pencil.get("GTape")

    if gp:
        if debug:
            print("Found existing GTape!")
    else:
        gp = bpy.data.grease_pencil.new("GTape")
        if debug:
            print("Created new GTape.")

    # set active grease pencil
    scene.grease_pencil = gp

    # get/create layer
    # layername = "Tape - %d, %s, %.1f" % (thickness, color, alpha)
    layername = "Tape - %d" % (thickness)
    layer = gp.layers.get(layername)

    if layer:
        if debug:
            print("Found existing GP layer '%s'" % (layer.info))
    else:
        layer = gp.layers.new(layername, set_active=True)
        if debug:
            print("created new GP layer '%s'" % (layer.info))

    layer.line_change = thickness
    layer.show_x_ray = xray

    # get/set frame
    frame = layer.active_frame
    if frame:
        if frame.frame_number != scene.frame_current:
            frame = layer.frames.new(scene.frame_current)
    else:
        frame = layer.frames.new(scene.frame_current)

    # get/create palette
    palette = gp.palettes.get("GTape Palette")
    if palette:
        if debug:
            print("Found existing palette!")
    else:
        palette = gp.palettes.new('GTape Palette')

        # generate color/alpha pairs for palette
        for col in colorcodes:
            for a in range(1, 11):
                name = "%s_%.1f" % (col, a / 10)

                pcol = palette.colors.new()
                pcol.name = name
                pcol.color = colorcodes[col]
                pcol.alpha = a / 10

        # set the active color to opaque black, this is just in case one uses the normal GP to draw on the GTape object
        palette.colors.active = palette.colors['BLACK_1.0']

        if debug:
            print("Created new palette.")

    # create a stroke
    stroke = frame.strokes.new(colorname="%s_%.1f" % (color, alpha))
    stroke.draw_mode = '3DSPACE'  # either of ('SCREEN', '3DSPACE', '2DSPACE', '2DIMAGE')

    # add points
    stroke.points.add(len(coords))

    for idx, co in enumerate(coords):
        stroke.points[idx].co = co
