
import bpy
import bgl

from . import build


def draw_function(s):
    if s['pre_border_select_mode']:
        bgl.glColor3f(0.0, 0.8, 0.0)

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(s['border_select_mouse_x'], s['border_select_mouse_x'] - 10000)
        bgl.glVertex2f(s['border_select_mouse_x'], s['border_select_mouse_x'] + 100000)
        bgl.glEnd()

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(s['border_select_mouse_y'] - 100000, s['border_select_mouse_y'])
        bgl.glVertex2f(s['border_select_mouse_y'] + 100000, s['border_select_mouse_y'])
        bgl.glEnd()

    if s['border_select_mode']:
        bgl.glColor3f(0.0, 0.8, 0.0)

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(s['border_select_mouse_x'], s['border_select_mouse_y'])
        bgl.glVertex2f(s['border_select_mouse_x'], s['border_select_mouse_move_y'])
        bgl.glEnd()

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(s['border_select_mouse_x'], s['border_select_mouse_move_y'])
        bgl.glVertex2f(s['border_select_mouse_move_x'], s['border_select_mouse_move_y'])
        bgl.glEnd()

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(s['border_select_mouse_move_x'], s['border_select_mouse_move_y'])
        bgl.glVertex2f(s['border_select_mouse_move_x'], s['border_select_mouse_y'])
        bgl.glEnd()

        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(s['border_select_mouse_move_x'], s['border_select_mouse_y'])
        bgl.glVertex2f(s['border_select_mouse_x'], s['border_select_mouse_y'])
        bgl.glEnd()


def toggle_select(s):
    data_blocks = [
        bpy.data.scenes,
        bpy.data.objects,
        bpy.data.meshes,
        bpy.data.libraries,
        bpy.data.cameras,
        bpy.data.lamps,
        bpy.data.materials,
        bpy.data.textures,
        bpy.data.images,
        bpy.data.worlds,
    ]

    select = True

    for data in data_blocks:
        for block in data:
            if block.oops_schematic.select:
                select = False
                break

    if not select:
        s.multi_click.clear()
    else:
        for data in data_blocks:
            for block in data:
                click = s.multi_click.add()
                click.x = block.oops_schematic.position_x
                click.y = block.oops_schematic.position_y


def nodes_border_select(s):
    if s['border_select_mouse_x'] < s['border_select_mouse_move_x']:
        border_x1 = s['border_select_mouse_x']
        border_x2 = s['border_select_mouse_move_x']
    else:
        border_x1 = s['border_select_mouse_move_x']
        border_x2 = s['border_select_mouse_x']

    if s['border_select_mouse_y'] < s['border_select_mouse_move_y']:
        border_y1 = s['border_select_mouse_y']
        border_y2 = s['border_select_mouse_move_y']
    else:
        border_y1 = s['border_select_mouse_move_y']
        border_y2 = s['border_select_mouse_y']

    data_blocks = [
        bpy.data.scenes,
        bpy.data.objects,
        bpy.data.meshes,
        bpy.data.libraries,
        bpy.data.cameras,
        bpy.data.lamps,
        bpy.data.materials,
        bpy.data.textures,
        bpy.data.images,
        bpy.data.worlds,
    ]

    for data in data_blocks:
        for block in data:
            if border_x1 < block.oops_schematic.position_x < border_x2 and \
                border_y1 < block.oops_schematic.position_y < border_y2:
                click = s.multi_click.add()
                click.x = block.oops_schematic.position_x
                click.y = block.oops_schematic.position_y


def correct_context(context):
    correct = False
    region = None
    area = context.area

    if area.type == 'NODE_EDITOR':
        for region in area.regions:
            if region.type == 'WINDOW':
                correct = True
                return correct, region

    return correct, region


class OopsSchematicShow(bpy.types.Operator):
    bl_idname = "node.oops_schematic_show"
    bl_label = "Show/Hide Oops Schematic"

    _handle = None
    _handle_2 = None
    border_mouse_x = 0.0
    border_mouse_y = 0.0

    @staticmethod
    def handle_add():
        OopsSchematicShow._handle = bpy.types.SpaceNodeEditor.draw_handler_add(build.build_schematic_scene, (), 'WINDOW', 'POST_VIEW')
        OopsSchematicShow._handle_2 = bpy.types.SpaceNodeEditor.draw_handler_add(draw_function, (bpy.context.window_manager.oops_schematic, ), 'WINDOW', 'POST_VIEW')

    @staticmethod
    def handle_remove():
        if OopsSchematicShow._handle is not None:
            bpy.types.SpaceNodeEditor.draw_handler_remove(OopsSchematicShow._handle, 'WINDOW')
            bpy.types.SpaceNodeEditor.draw_handler_remove(OopsSchematicShow._handle_2, 'WINDOW')
        OopsSchematicShow._handle = None
        OopsSchematicShow._handle_2 = None

    def cancel(self, context):
        self.handle_remove()

    def modal(self, context, event):
        s = context.window_manager.oops_schematic
        if event.type == 'RIGHTMOUSE' and event.value == 'CLICK' and not s.select_3d_view:
            correct, region = correct_context(context)
            if correct:
                click_x, click_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                use_multi_select = event.shift
                if not use_multi_select:
                    s.multi_click.clear()
                click = s.multi_click.add()
                click.x = click_x
                click.y = click_y
                region.tag_redraw()
        elif event.type == 'G' and event.value == 'RELEASE':
            correct, region = correct_context(context)
            if correct:
                self.start_mouse_x, self.start_mouse_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                s.grab_mode = True
        elif event.type == 'MOUSEMOVE' and s.grab_mode:
            correct, region = correct_context(context)
            if correct:
                mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                s.move_offset_x = mouse_x - self.start_mouse_x
                s.move_offset_y = mouse_y - self.start_mouse_y
                region.tag_redraw()
        elif (event.type == 'LEFTMOUSE' or event.type == 'RIGHTMOUSE') and s.grab_mode:
            correct, region = correct_context(context)
            if correct:
                if event.type == 'LEFTMOUSE':
                    s.apply_location = True
                s.grab_mode = False
                region.tag_redraw()
        elif event.type == 'A' and event.value == 'RELEASE':
            correct, region = correct_context(context)
            if correct:
                toggle_select(s)
                region.tag_redraw()
        elif event.type == 'B' and event.value == 'RELEASE':
            correct, region = correct_context(context)
            if correct:
                mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                s['border_select_mouse_x'] = mouse_x
                s['border_select_mouse_y'] = mouse_y
                s['pre_border_select_mode'] = True
                region.tag_redraw()
        elif event.type == 'MOUSEMOVE' and s['pre_border_select_mode']:
            correct, region = correct_context(context)
            if correct:
                mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                s['border_select_mouse_x'] = mouse_x
                s['border_select_mouse_y'] = mouse_y
                region.tag_redraw()
        elif (event.type == 'ESC' or event.type == 'RIGHTMOUSE') and event.value == 'RELEASE' and s['pre_border_select_mode']:
            correct, region = correct_context(context)
            if correct:
                s['pre_border_select_mode'] = False
                region.tag_redraw()
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS' and s['pre_border_select_mode']:
            correct, region = correct_context(context)
            if correct:
                s['pre_border_select_mode'] = False
                s['border_select_mode'] = True
                mouse_move_x, mouse_move_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                s['border_select_mouse_move_x'] = mouse_move_x
                s['border_select_mouse_move_y'] = mouse_move_y
                region.tag_redraw()
        elif event.type == 'MOUSEMOVE' and event.value == 'PRESS' and s['border_select_mode']:
            correct, region = correct_context(context)
            if correct:
                mouse_move_x, mouse_move_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
                s['border_select_mouse_move_x'] = mouse_move_x
                s['border_select_mouse_move_y'] = mouse_move_y
                region.tag_redraw()
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE' and s['border_select_mode']:
            correct, region = correct_context(context)
            if correct:
                s['border_select_mode'] = False
                nodes_border_select(s)
                region.tag_redraw()
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        s = context.window_manager.oops_schematic
        correct, region = correct_context(context)
        if region:
            mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
        else:
            mouse_x, mouse_y = 0.0, 0.0
        s['pre_border_select_mode'] = False
        s['border_select_mouse_x'] = mouse_x
        s['border_select_mouse_y'] = mouse_y
        s['border_select_mode'] = False
        s['border_select_mouse_move_x'] = 0.0
        s['border_select_mouse_move_y'] = 0.0
        if not s.show:
            s.show = True
            if context.area.type == 'NODE_EDITOR':
                self.handle_add()
                context.area.tag_redraw()
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
        else:
            s.show = False
            self.handle_remove()
            context.area.tag_redraw()
            return {'CANCELLED'}
