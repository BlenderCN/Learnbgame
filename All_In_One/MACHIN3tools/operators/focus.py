import bpy
from bpy.props import BoolProperty, EnumProperty
from .. utils.view import update_local_view


levels_items = [("SINGLE", "Single", ""),
                ("MULTIPLE", "Multiple", "")]

# TODO: option to to it for all views? possible?


class Focus(bpy.types.Operator):
    bl_idname = "machin3.focus"
    bl_label = "MACHIN3: Focus"
    bl_options = {'REGISTER', 'UNDO'}

    levels: EnumProperty(name="Levels", items=levels_items, description="Switch between single-level Blender native Local View and multi-level MACHIN3 Focus", default="MULTIPLE")
    unmirror: BoolProperty(name="Un-Mirror", default=True)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # only show tool props when initializing local view
        # this prevents switching modes and settings while in local view
        if self.show_tool_props:
            row = column.row()
            row.label(text="Levels")
            row.prop(self, "levels", expand=True)

            column.prop(self, "unmirror")

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        view = context.space_data
        self.show_tool_props = False

        sel = context.selected_objects
        vis = context.visible_objects

        # blender native local view
        if self.levels == "SINGLE":
            if self.unmirror:
                if view.local_view:
                    mirrored = [(obj, mod) for obj in vis for mod in obj.modifiers if mod.type == "MIRROR"]

                else:
                    mirrored = [(obj, mod) for obj in sel for mod in obj.modifiers if mod.type == "MIRROR"]

                for obj, mod in mirrored:
                    mod.show_viewport = True if view.local_view else False


            if not view.local_view:
                self.show_tool_props = True

            bpy.ops.view3d.localview(frame_selected=False)


        # multi level local view
        else:
            history = context.scene.M3.focus_history

            # already in local view
            if view.local_view:

                # go deeper
                if context.selected_objects:
                    self.focus(context, view, sel, history)

                # go higher
                else:
                    if history:
                        self.unfocus(context, view, history)

                    # exit local view (for instance, when local view was initiated from batch ops, there won't be a history in that case)
                    else:
                        bpy.ops.view3d.localview(frame_selected=False)

            # initialize local view
            elif context.selected_objects:
                self.show_tool_props = True
                self.focus(context, view, sel, history, init=True)


            # for epoch in history:
                # print(epoch.name, ", hidden: ", [obj.name for obj in epoch.objects], ", unmirrored: ", [obj.name for obj in epoch.unmirrored])

        return {'FINISHED'}

    def focus(self, context, view, sel, history, init=False):
        vis = context.visible_objects
        hidden = [obj for obj in vis if obj not in sel]

        if hidden:
            # initialize
            if init:
                bpy.ops.view3d.localview(frame_selected=False)

            # hide
            else:
                update_local_view(view, [(obj, False) for obj in hidden])

            # create new epoch
            epoch = history.add()
            epoch.name = "Epoch %d" % (len(history) - 1)

            # store hidden objects in epoch
            for obj in hidden:
                entry = epoch.objects.add()
                entry.obj = obj
                entry.name = obj.name

            # disable mirror mods and store these unmirrored objects
            if self.unmirror:
                mirrored = [(obj, mod) for obj in sel for mod in obj.modifiers if mod.type == "MIRROR"]

                for obj, mod in mirrored:
                    if mod.show_viewport:
                        mod.show_viewport = False

                        entry = epoch.unmirrored.add()
                        entry.obj = obj
                        entry.name = obj.name

    def unfocus(self, context, view, history):
        last_epoch = history[-1]

        # de-inititalize
        if len(history) == 1:
            bpy.ops.view3d.localview(frame_selected=False)

        # unhide
        else:
            update_local_view(view, [(entry.obj, True) for entry in last_epoch.objects])

        # re-enbable mirror mods
        for entry in last_epoch.unmirrored:
            for mod in entry.obj.modifiers:
                if mod.type == "MIRROR":
                    mod.show_viewport = True


        # delete the last epoch
        idx = history.keys().index(last_epoch.name)
        history.remove(idx)
