from datetime import datetime

import bpy
from bpy.props import (
        BoolProperty,
        IntProperty,
        IntVectorProperty,
        FloatProperty,
        StringProperty,
        PointerProperty
    )
from bpy.app.handlers import persistent
from mathutils import Color
import bgl
import blf


bl_info = {
    "name": "Thermometer",
    "author": "Nutti",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "View 3D",
    "description": "Measure and Display Temperature with a Raspberry PI",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"
}


def bgl_draw_line(x1, y1, x2, y2):
    bgl.glColor3f(1.0, 1.0, 1.0)
    bgl.glLineWidth(1.0)
    bgl.glBegin(bgl.GL_LINES)
    bgl.glVertex3f(x1, y1, 0.0)
    bgl.glVertex3f(x2, y2, 0.0)
    bgl.glEnd()


def bgl_draw_rect(x1, y1, x2, y2, color):
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(*color)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glVertex3f(x1, y2, 0.0)
    bgl.glVertex3f(x1, y1, 0.0)
    bgl.glVertex3f(x2, y1, 0.0)
    bgl.glVertex3f(x2, y2, 0.0)
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)


def get_region(context, area_type, region_type):
    region = None
    area = None

    for a in context.screen.areas:
        if a.type == area_type:
            area = a
            break
    else:
        return None

    for r in area.regions:
        if r.type == region_type:
            region = r
            break

    return region


def get_invoke_context(area_type, region_type):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == area_type:
                break
        else:
            continue
        for region in area.regions:
            if region.type == region_type:
                break
        else:
            continue

    return {'window': window, 'screen': screen, 'area': area, 'region': region}


class T_Properties(bpy.types.PropertyGroup):

    running = BoolProperty(
        name="Running State",
        description="Running if True",
        default=False
    )
    temperature = FloatProperty(
        name="Temperature",
        description="Temperature measured with Raspberry PI",
        default=0.0
    )


class Thermometer(bpy.types.Operator):

    bl_idname = "system.temperature"
    bl_label = "Temperature"
    bl_description = "Measure and Display Thermometer"

    __timer = None
    __handle = None

    @staticmethod
    def __handle_add(self, context):
        if Thermometer.__handle is None:
            Thermometer.__handle = bpy.types.SpaceView3D.draw_handler_add(
                Thermometer.__render,
                (context, ), 'WINDOW', 'POST_PIXEL'
            )

    @staticmethod
    def __handle_remove(self, context):
        if Thermometer.__handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(
                Thermometer.__handle, 'WINDOW'
            )
            Thermometer.__handle = None

    def __get_temperature(self, props, prefs):
        with open(prefs.bus_path) as file:
            strs = file.readlines()
            words = strs[-1].split(" ")
            index = words[-1].find("t=")
            if index > -1:
                props.temperature = float(words[-1][2:]) / 1000.0

    def __update_text(self, props):
        if not "Temperature_Text" in bpy.data.objects:
            bpy.ops.object.text_add()
            bpy.context.active_object.name = "Temperature_Text"
        text_obj = bpy.data.objects["Temperature_Text"]
        if text_obj.type == 'FONT':
            text_obj.data.body = "{0:.1f}".format(props.temperature)

        # make material slot
        if len(text_obj.material_slots) == 0:
            bpy.context.scene.objects.active = text_obj
            bpy.ops.object.material_slot_add()
            text_obj.material_slots[0].material = bpy.data.materials['Material']
        mtrl = text_obj.material_slots[0].material

        # change color
        min_temp = -10
        max_temp = 50
        temp_range = max_temp - min_temp
        color = Color()
        color.hsv = (
            1.0 - (((props.temperature-min_temp)/(temp_range-10))*270+90)/360,
            0.95,
            1.0
        )
        mtrl.diffuse_color = color

    def __update_suzanne(self, props):
        # make object
        if not "Temperature_Suzanne" in bpy.data.objects:
            bpy.ops.mesh.primitive_monkey_add()
            bpy.context.active_object.name = "Temperature_Suzanne"
        suzanne_obj = bpy.data.objects["Temperature_Suzanne"]

        # make material
        if len(bpy.data.materials) == 0:
            bpy.ops.material.new()

        # make material slot
        if len(suzanne_obj.material_slots) == 0:
            bpy.context.scene.objects.active = suzanne_obj
            bpy.ops.object.material_slot_add()
            suzanne_obj.material_slots[0].material = bpy.data.materials['Material']
        mtrl = suzanne_obj.material_slots[0].material

        # change color
        min_temp = -10
        max_temp = 50
        temp_range = max_temp - min_temp
        color = Color()
        color.hsv = (
            1.0 - (((props.temperature-min_temp)/(temp_range-10))*270+90)/360,
            0.95,
            0.85
        )
        mtrl.diffuse_color = color

    @staticmethod
    def __draw_analog(region, props, prefs):
        start_x = prefs.ana_position[0]
        end_x = prefs.ana_position[0] + 400.0 * prefs.digi_scale_x
        base_y = prefs.ana_position[1]
        long_len_y1 = 3.0
        long_len_y2 = 10.0
        middle_len = 6.0
        short_len = 3.0
        min_temp = -10
        max_temp = 50
        temp_range = max_temp - min_temp
        interval = (end_x - start_x) / temp_range

        blf.size(0, 12, 72)

        color = Color()
        color.hsv = (
            1.0 - (((props.temperature-min_temp)/(temp_range-10))*270+90)/360,
            0.8,
            1.0
        )
        bgl_draw_rect(
            start_x,
            region.height - base_y,
            start_x + interval * (props.temperature - min_temp),
            region.height - base_y + long_len_y2,
            (color[0], color[1], color[2], 0.6)
        )

        bgl_draw_line(start_x, region.height - base_y,
                      end_x, region.height - base_y)

        for t in range(min_temp, max_temp + 1):
            x1 = start_x + interval * (t - min_temp)
            x2 = x1
            if t % 10 == 0:
                y1 = region.height - base_y - long_len_y1
                y2 = region.height - base_y + long_len_y2
                bgl_draw_line(x1, y1, x2, y2)
                blf.position(0, x1 - 2.0, y1 - 15.0, 0)
                blf.draw(0, "{0}".format(t))
            elif t % 5 == 0:
                y1 = region.height - base_y
                y2 = region.height - base_y + middle_len
                bgl_draw_line(x1, y1, x2, y2)
            else:
                y1 = region.height - base_y
                y2 = region.height - base_y + short_len
                bgl_draw_line(x1, y1, x2, y2)

    @staticmethod
    def __draw_digital(region, props, prefs):
        blf.size(0, prefs.digi_font_size, 72)
        blf.position(
            0,
            prefs.digi_position[0],
            region.height - prefs.digi_position[1],
            0
        )
        blf.draw(0, "{0:.1f}℃".format(props.temperature))

    @staticmethod
    def __render(context):
        # supress error when this add-on is disabled
        if not hasattr(context.scene, "t_props"):
            return
        props = context.scene.t_props
        prefs = context.user_preferences.addons[__name__].preferences

        # there is no region to render
        region = get_region(context, 'VIEW_3D', 'WINDOW')
        if region is None:
            return

        if prefs.render_digital:
            Thermometer.__draw_digital(region, props, prefs)
        if prefs.render_analog:
            Thermometer.__draw_analog(region, props, prefs)

    # output temperature data to the file
    def __output_log(self, props, prefs):
        with open(prefs.log_path, "a") as f:
            date = datetime.now().strftime("%Y.%m.%d.%H.%M.%S")
            f.write("{0},{1:.1f}\n".format(date, props.temperature))

    def modal(self, context, event):
        props = context.scene.t_props
        prefs = context.user_preferences.addons[__name__].preferences

        if props.running is False:
            return {'FINISHED'}

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        if context.area:
            context.area.tag_redraw()

        self.__get_temperature(props, prefs)
        if prefs.gen_meshes:
            self.__update_text(props)
            self.__update_suzanne(props)
        if prefs.logging:
            self.__output_log(props, prefs)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.t_props
        if props.running is False:
            props.running = True
            if Thermometer.__timer is None:
                Thermometer.__timer = context.window_manager.event_timer_add(
                    1.0, context.window
                )
                context.window_manager.modal_handler_add(self)
                Thermometer.__handle_add(self, context)
            return {'RUNNING_MODAL'}
        else:
            props.running = False
            if Thermometer.__timer is not None:
                Thermometer.__handle_remove(self, context)
                context.window_manager.event_timer_remove(Thermometer.__timer)
                Thermometer.__timer = None
            return {'FINISHED'}


class OBJECt_PT_T(bpy.types.Panel):

    bl_label = "Thermometer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        sc = context.scene
        layout = self.layout
        props = sc.t_props
        if props.running is False:
            layout.operator(
                Thermometer.bl_idname, text="Start", icon="PLAY"
            )
        else:
            layout.operator(
                Thermometer.bl_idname, text="Stop", icon="PAUSE"
            )


class T_Preferences(bpy.types.AddonPreferences):

    bl_idname = __name__

    render_digital = BoolProperty(
        name="Render Digital",
        default=True
    )
    render_analog = BoolProperty(
        name="Render Analog",
        default=True
    )
    gen_meshes = BoolProperty(
        name="Generate Meshes",
        default=True
    )
    logging = BoolProperty(
        name="Log Output",
        default=True
    )

    bus_path = StringProperty(
        name="Bus",
        description="File Path which will be able to get Temerature",
        default="./test.txt"
    )
    log_path = StringProperty(
        name="Log Path",
        description="File Path to be output Log",
        default="./temperature.log"
    )

    digi_font_size = IntProperty(
        name="Font Size",
        default=25,
        min=10,
        max=80
    )
    digi_position = IntVectorProperty(
        name="Position",
        default=(40, 60),
        size=2,
        min=0
    )
    digi_scale_x = FloatProperty(
        name="X",
        default=1.0,
        min=0.1,
        max=2.0
    )

    ana_position = IntVectorProperty(
        name="Position",
        default=(40, 100),
        size=2,
        min=0
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "render_digital")
        row.prop(self, "render_analog")
        row.prop(self, "gen_meshes")
        row.prop(self, "logging")

        layout.separator()

        sub = layout.split(percentage=0.7)
        col = sub.column()
        col.prop(self, "bus_path")
        col.prop(self, "log_path")

        layout.separator()

        layout.label("Digital Display:")
        sub = layout.split(percentage=0.2)
        col = sub.column()
        col.label("Font:")
        col.prop(self, "digi_font_size")
        sub = sub.split(percentage=0.2)
        sub.prop(self, "digi_position")
        sub = sub.split(percentage=0.3)
        col = sub.column()
        col.label("Scale:")
        col.prop(self, "digi_scale_x")

        layout.separator()

        layout.label("Analog Display:")
        sub = layout.split(percentage=0.2)
        sub.prop(self, "ana_position")


def init_props():
    sc = bpy.types.Scene
    sc.t_props = PointerProperty(
        name="Properties",
        description="Properties for Thermometer",
        type=T_Properties
    )


def clear_props():
    sc = bpy.types.Scene
    del sc.t_props


def info_header_fn(self, context):
    layout = self.layout
    props = context.scene.t_props

    layout.label("%.1f℃" % (props.temperature), icon='BLENDER')


@persistent
def start_fn(scene):
    bpy.app.handlers.scene_update_pre.remove(start_fn)
    bpy.ops.object.mode_set(mode='OBJECT')
    context = get_invoke_context('VIEW_3D', 'WINDOW')
    bpy.ops.system.temperature(context, 'INVOKE_DEFAULT')


def register():
    bpy.utils.register_module(__name__)
    init_props()
    bpy.types.INFO_HT_header.append(info_header_fn)
    bpy.app.handlers.scene_update_pre.append(start_fn)


def unregister():
    context = get_invoke_context('VIEW_3D', 'WINDOW')
    bpy.ops.system.temperature(context, 'INVOKE_DEFAULT')
    bpy.types.INFO_HT_header.remove(info_header_fn)
    clear_props()
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
