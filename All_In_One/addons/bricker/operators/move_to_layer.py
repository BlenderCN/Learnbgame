# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
import bpy
from bpy.types import Operator
from bpy.props import *

# Addon imports
from ..functions.common import *

class OBJECT_OT_move_to_layer_override(Operator):
    """Move to Layer functionality"""
    bl_idname = "bricker.move_to_layer_override"
    bl_label = "Move to Layer Override"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        ev = []
        event = self.event
        if event.ctrl:
            ev.append("Ctrl")
        if event.shift:
            ev.append("Shift")
        if event.alt:
            ev.append("Alt")
        if event.oskey:
            ev.append("OS")
        changed = [i for i, (l, s) in
                enumerate(zip(self.layers, self.prev_sel))
                if l != s]

        # print("+".join(ev), event.type, event.value, changed)
        # pick only the changed one
        if not (event.ctrl or event.shift) and changed:
            self.layers = [i in changed for i in range(20)]
        self.prev_sel = self.layers[:]

        self.runMove(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.layers = [any(o.layers[i] for o in context.selected_objects)
                      for i in range(20)]
        self.event = event
        self.object_names = [o.name for o in context.selected_objects]
        self.prev_sel = self.layers[:]
        return context.window_manager.invoke_props_popup(self, event)

    def check(self, context):
        return True # thought True updated.. not working

    ###################################################
    # class variables

    layers = BoolVectorProperty(
        name="Layers",
        subtype="LAYER",
        description="Object Layers",
        size=20,
        )
    event = None
    object_names = []
    prev_sel = []

    ################################################
    # class methods

    def runMove(self, context):
        scn = bpy.context.scene
        for name in self.object_names:
            obj = scn.objects.get(name)
            obj.layers = self.layers
            if not obj.isBrickifiedObject or obj.cmlist_id == -1:
                continue
            cm = getItemByID(scn.cmlist, obj.cmlist_id)
            if not cm.animated:
                continue
            n = getSourceName(cm)
            for f in range(cm.lastStartFrame, cm.lastStopFrame + 1):
                bricksCurF = bpy.data.objects.get("Bricker_%(n)s_bricks_f_%(f)s" % locals())
                if bricksCurF is not None and bricksCurF.name != obj.name:
                    bricksCurF.layers = self.layers

class OBJECT_OT_move_to_layer(bpy.types.Operator):
    """Move to Layer"""
    bl_idname = "object.move_to_layer"
    bl_label = "Move to Layer"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return bpy.ops.bricker.move_to_layer_override('INVOKE_DEFAULT')


# def register():
#     bpy.utils.register_module(__name__)
#
# def unregister():
#     addon_updater_ops.unregister()
#
# if __name__ == "__main__":
#     register()
