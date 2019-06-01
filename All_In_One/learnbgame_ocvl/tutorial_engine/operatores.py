import os
import webbrowser

import bpy
import time
import logging

from ocvl.tutorial_engine.worker import print_keyborad_worker
from ocvl.tutorial_engine.settings import TUTORIAL_HEARTBEAT_INTERVAL, TUTORIAL_PATH, TUTORIAL_HEARTBEAT_INTERVAL_TIP_REFRESH
from ocvl.tutorial_engine.engine_app import NodeCommandHandler

bpy.worker_queue = []
handler = NodeCommandHandler
logger = logging.getLogger(__name__)


class ModalTimerConsumerRequestOperator(bpy.types.Operator):
    """Operator grab and run requests from queue - from Tornado"""
    bl_idname = "wm.modal_timer_consumer_request_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    _heartbeat_counter = 0

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            self._heartbeat_counter += 1
            if self._heartbeat_counter % 10 == 0:
                print(time.time())
            try:
                if bpy.worker_queue:
                    request = bpy.worker_queue.pop(0)
                    kwargs = request.get("kwargs")
                    command = request.get("command")
                    for kwarg_key, kwarg_value in kwargs.items():
                        if kwarg_value[0] in ["(", "[", "{"]:
                            kwargs[kwarg_key] = eval(kwarg_value)

                    logger.info("Pop request from queue. Command: {}, kwargs: {}".format(command, kwargs))
                    if command == "StopServer":
                        return {'CANCELLED'}
                    getattr(handler, command)(**kwargs)

            except Exception as e:
                logger.exception("{}".format(e))

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(TUTORIAL_HEARTBEAT_INTERVAL, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.area.header_text_set()
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


class ModalTimerRefreshFirstStepsTipOperator(bpy.types.Operator):
    """"""
    bl_idname = "wm.modal_timer_refresh_first_steps_tip_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    _heartbeat_counter = 0
    _absence_count = 0

    def modal(self, context, event):

        if event.type == 'TIMER':
            self._heartbeat_counter += 1
            if self._heartbeat_counter % 10 == 0:
                print("{} - {} - {}".format(time.time(), __name__, bpy.tutorial_first_step))

            for area in bpy.context.screen.areas:
                if area.type == 'NODE_EDITOR':
                    if "Tip" in bpy.data.node_groups[0].nodes:
                        bpy.data.node_groups[0].nodes["Tip"].wrapped_process()
                    else:
                        self._absence_count += 1

        if self._absence_count > 10:
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(TUTORIAL_HEARTBEAT_INTERVAL_TIP_REFRESH, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.area.header_text_set()
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


class TutorialModeOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "node.tutorial_mode"
    bl_label = "Node Tutorial Mode"

    loc_tutorial_path = bpy.props.StringProperty(default="")

    def execute(self, context):
        bpy.ops.node.clean_desk()
        NodeCommandHandler.clear_node_groups()
        NodeCommandHandler.get_or_create_node_tree()
        # orange_theme()
        bpy.engine_worker_thread.start()
        # bpy.jupyter_worker_thread.start()

        # self._timer = context.window_manager.event_timer_add(1, context.window)
        # context.window_manager.modal_handler_add(self)
        if self.loc_tutorial_path:
            url = "file://" + self.loc_tutorial_path
            webbrowser.open(url)
            logger.info("Opne tutorial from URL: {}".format(url))
        return {'FINISHED'}


class TutorialModeCommandOperator(bpy.types.Operator):
    bl_idname = "node.tutorial_mode_command"
    bl_label = "Node Tutorial Mode Command"

    loc_command = bpy.props.StringProperty(default="")

    def execute(self, context):

        if self.loc_command == "connect_sample_and_view":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="ImageViewer", node_output="ImageSample", input_name="image_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "connect_sample_and_view_and_blur":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="ImageViewer", node_output="blur", input_name="image_in", output_name="image_out")
            NodeCommandHandler.connect_nodes(node_input="blur", node_output="ImageSample", input_name="image_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "set_ksize_on_blur":
            nt = NodeCommandHandler.get_or_create_node_tree()
            blur = nt.nodes.get('blur')
            blur.ksize_in = (10, 10)
            return {'FINISHED'}

        elif self.loc_command == "file_mode_for_image_sample":
            nt = NodeCommandHandler.get_or_create_node_tree()
            blur = nt.nodes.get('ImageSample.001')
            blur.loc_image_mode = "FILE"
            return {'FINISHED'}

        elif self.loc_command == "select_file_for_sample":
            nt = NodeCommandHandler.get_or_create_node_tree()
            blur = nt.nodes.get('ImageSample.001')
            full_tutorial_path = os.path.abspath(os.path.join(TUTORIAL_PATH, "first_steps/ml.png"))
            blur.loc_filepath = full_tutorial_path
            return {'FINISHED'}

        elif self.loc_command == "connect_addweighted_first_input":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="addWeighted", node_output="ImageSample.001", input_name="image_1_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "connect_addweighted_second_input":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="addWeighted", node_output="blur", input_name="image_2_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "connect_addweighted_output":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="ImageViewer", node_output="addWeighted", input_name="image_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command:
            keyborad_worker_thread = print_keyborad_worker(text=self.loc_command)
            keyborad_worker_thread.start()

        return {'FINISHED'}


class TutorialShowFirstStepCommandOperator(bpy.types.Operator):
    bl_idname = "node.tutorial_show_first_step"
    bl_label = "Node Tutorial Show First Step"

    loc_command = bpy.props.StringProperty(default="")

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'NODE_EDITOR':
                NodeCommandHandler.clear_node_groups()
                NodeCommandHandler.get_or_create_node_tree()
                NodeCommandHandler.create_node("OCVLFirstStepsNode", location=(0, 0))
                NodeCommandHandler.create_node("OCVLTipNode", location=(400, 0))
                NodeCommandHandler.connect_nodes("Tip", "tip", "FirstSteps", "tip")
                NodeCommandHandler.view_all()
                bpy.ops.wm.modal_timer_refresh_first_steps_tip_operator()
                return {'FINISHED'}
        return {'CANCELLED'}


def orange_theme():
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    themes_dir = os.path.abspath(os.path.join(current_dir, "../../../presets/interface_theme"))
    filepath = os.path.join(themes_dir, "blend_swap_5.xml")
    bpy.ops.script.execute_preset(
        filepath=filepath,
        menu_idname="USERPREF_MT_interface_theme_presets")


def register():
    bpy.utils.register_class(ModalTimerConsumerRequestOperator)
    bpy.utils.register_class(TutorialModeOperator)
    bpy.utils.register_class(TutorialModeCommandOperator)
    bpy.utils.register_class(TutorialShowFirstStepCommandOperator)
    bpy.utils.register_class(ModalTimerRefreshFirstStepsTipOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerRefreshFirstStepsTipOperator)
    bpy.utils.unregister_class(TutorialShowFirstStepCommandOperator)
    bpy.utils.unregister_class(TutorialModeCommandOperator)
    bpy.utils.unregister_class(TutorialModeOperator)
    bpy.utils.unregister_class(ModalTimerConsumerRequestOperator)
