import bpy
import bpy.ops
from bpy.app.handlers import load_post, persistent

#bpy.ops.wm.jet_modal_timer_op()
from . common_utils import redraw


class JetModalTimerOp(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.jet_modal_timer_op"
    bl_label = "Jet Modal Timer Operator"

    _timer = None

    def check_removed_objs(self, context):
        """
        Checks if any mesh object is deleted from the current scene.
        If it is, the function seeks for those deleted objects in all the polycount lists in the scene
        and it removes the deleted objects from them
        :param scene: Current scene
        """
        scene = context.scene
        meshes = len([o for o in scene.objects if o.type == "MESH"])
        if meshes == scene.Jet.mesh_objs:
            return

        if meshes < scene.Jet.mesh_objs:
            not_in_scene = []
            for i in range(len(scene.Jet.list_low_res.obj_list)):
                obj = scene.Jet.list_low_res.obj_list[i].object
                list = scene.Jet.list_low_res.obj_list[i].list_high_res
                if obj is None or obj not in scene.objects.values():
                    not_in_scene.append(i)

                not_in_obj = []
                for j in range(len(list.obj_list)):
                    hi_obj = list.obj_list[j].object
                    if hi_obj is None or hi_obj not in scene.objects.values():
                        not_in_obj.append(j)

                for hi_ob in reversed(not_in_obj):
                    list.obj_list.remove(hi_ob)

            scene.Jet.list_low_res.obj_list_index_no_select = 0
            for ob in reversed(not_in_scene):
                scene.Jet.list_low_res.obj_list.remove(ob)

            redraw()

        scene.Jet.mesh_objs = meshes

    def manage_selection(self, context):
        if context.active_object is None or not hasattr(context.active_object, "select"):
            return
        if context.active_object != context.scene.Jet.active.object or \
                context.active_object.select != context.scene.Jet.active.select:
            if context.active_object.select:
                objs_in_list = [o.object
                                for o in context.scene.Jet.list_low_res.obj_list]
                if context.active_object in objs_in_list:
                    idx = objs_in_list.index(context.active_object)
                    context.scene.Jet.list_low_res.obj_list_index_select = idx
                context.scene.Jet.active.object = context.active_object
            context.scene.Jet.active.select = context.active_object.select

    def modal(self, context, event):
        if len(context.scene.Jet.list_low_res.obj_list)==0:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.manage_selection(context)
            self.check_removed_objs(context)
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        wm.Jet.timer = True
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        self._timer = None
        wm.Jet.timer = False


@persistent
def jet_load_post(param):
    """
    Called on after loading a .blend file
    :param param: In order to append this function to the load_post handler, this has to receive a parameter.
    """
    context = bpy.context
    scene = context.scene
    scene.Jet.active.object = context.active_object
    if context.active_object is not None and hasattr(context.active_object, "select"):
        scene.Jet.active.object.select = context.active_object.select

    if len(scene.Jet.list_low_res.obj_list)>0:
        bpy.ops.wm.jet_modal_timer_op()

    scene.Jet.mesh_objs = len([o for o in scene.objects if o.type == "MESH"])


def register():
    bpy.utils.register_class(JetModalTimerOp)

    if jet_load_post not in load_post:
        load_post.append(jet_load_post)


def unregister():
    bpy.utils.unregister_class(JetModalTimerOp)
    load_post.remove(jet_load_post)
