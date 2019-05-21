import bpy


class VCMInitOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.vcm_init"
    bl_label = "VCM Init"

    def execute(self, context):
        vcm_screen = None

        # Select VCM screen if exists
        if "VCM" in bpy.data.screens:
            bpy.context.window.screen = bpy.data.screens["VCM"]
            return {'FINISHED'}

        # Create new VCM screen if not exists
        if not vcm_screen:
            index = bpy.data.screens.values().index(bpy.context.screen)
            bpy.ops.screen.new()
            vcm_screen = bpy.data.screens[index + 1]
            vcm_screen.name = "VCM"

        # Remove all objects
        for obj in bpy.data.objects:
            obj.select = True
        bpy.ops.object.delete()

        # Remove areas
        while len(vcm_screen.areas) > 1:
            for area1 in vcm_screen.areas:
                for area2 in vcm_screen.areas:
                    if area1 == area2:
                        continue
                    if len(area1.regions) > 1:
                        overdrive = {'window': bpy.context.window, 'screen': vcm_screen, 'area': area1, 'region': area1.regions[1]}
                        result = bpy.ops.screen.area_join(overdrive, min_x=area1.x, min_y=area1.y, max_x=area2.x, max_y=area2.y)
                        if result == {'FINISHED'}:
                            break

        # Need redraw screen before set area.type = 'VIEW_3D'
        bpy.ops.wm.modal_timer_operator()
        return {'FINISHED'}


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            # Set View3D area
            area = context.area
            area.type = 'VIEW_3D'

            # Hide header
            for region in area.regions:
                if region.type == 'HEADER' and region.height > 1:
                    bpy.ops.screen.header()
                    break

            # Reset viewport
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # space.show_only_render = True

                    region = space.region_3d

                    region.view_location.x = 0
                    region.view_location.y = 0
                    region.view_location.z = 0

                    region.view_rotation.w = 0.9
                    region.view_rotation.x = 0.9
                    region.view_rotation.y = 0
                    region.view_rotation.z = 0

                    region.view_distance = 10

            return self.cancel(context)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


class VCMFunctionOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.vcm_function"
    bl_label = "VCM Function"

    def execute(self, context):
        print("Function")
        return {'FINISHED'}
