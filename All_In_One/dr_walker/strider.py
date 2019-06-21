# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>
# Copyright 2015 Bassam Kurdali 

if "bpy" in locals():
    import importlib
    importlib.reload(tag)
    importlib.reload(path)
    importlib.reload(nla)
    importlib.reload(action)
    importlib.reload(footsteps)
    importlib.reload(parambulator)
    importlib.reload(depath)

else:
    from . import tag
    from . import path
    from . import nla
    from . import action
    from . import footsteps
    from . import parambulator
    from . import depath

import bpy
from .parambulator import Parambulator


def cycle(context, use_remove_object_motion, use_only_keyframes, delta):
    """ replace a strip with a cycling version """

    try:
        strip, ob = nla.get_nla_active(context)
        print(strip.name, ob.name)
    except:
        print("couldn't get active strip, object")
        return # TODO raise error
    original_action = ob.animation_data.action
    track = ob.animation_data.nla_tracks.active
    # TODO verify that the object has been tagged, future is autotag
    auto_rig = tag.Reader(ob)
    reference_action = action.reference_action(
        [foot.name for foot in auto_rig.feet],
        strip.action, 
        delta,
        ob,
        auto_rig.stride)
    print('got here')
    print('ref_action', reference_action)
    if not reference_action: return # TODO error
    ob.animation_data.action = None
    walker = Parambulator(auto_rig, ob, reference_action)
    parent = ob.parent
    path.eval_time_activate(parent, True) # curve needs to live for footsteps
    ob.animation_data.use_nla = False # mute the nla
    cycle_frames = footsteps.steps_from_path(context, walker)
    print('got here')
    # footsteps.draw_footsteps(walker, context.scene)
    path.eval_time_activate(parent, False) # turn off to zero offset 
    frame_current = context.scene.frame_current
    context.scene.frame_set(0)
    walker.bake_walk(context)
    nla.replace_strip_action(strip, walker.object.animation_data.action, True)
    walker.object.animation_data.action = original_action
    ob.animation_data.use_nla = True
    
    context.scene.frame_set(frame_current)
    nla.eval_curve_from_steps(ob, track, strip, cycle_frames, parent)

    

class NLACycleStrip(bpy.types.Operator):
    """ replace a strip with a cycling version """
    bl_idname = 'nla.cycle_strip'
    bl_label = 'Cycle Action Strip'

    delta = bpy.props.FloatProperty(
        name="Zero Offset", default=0.0001, min=0.0000000001, max=.001)
    use_remove_object_motion = bpy.props.BoolProperty(
        name="Remove Object Motion", default=True)
    use_only_keyframes = bpy.props.BoolProperty(
        name="Only Keyframes", default=True)    
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'NLA_EDITOR'

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        props = self.properties
        cycle(
            context, props.use_remove_object_motion,
            props.use_only_keyframes, props.delta)
        return {'FINISHED'}
    
    def draw(self, context):
        props = self.properties
        layout = self.layout
        for prop in ('delta', 'use_remove_object_motion', 'use_only_keyframes'):
            row = layout.row()
            row.prop(props, prop)


class DeCurveStrips(bpy.types.Operator):
    """ add curve offsets to strip actions """
    bl_idname = 'nla.decurve_strips'
    bl_label = 'Decurve Strips'

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        specials = ('body', 'bodybase', 'R_foot', 'L_foot') # TODO
        strips, ob = nla.get_nla_selected(context)
        original_action = ob.animation_data.action
        ob.animation_data.action = None
        parent = ob.parent
        if not parent:
            return {'ABORTED'}
        path.eval_time_activate(parent, True)
        for strip in strips:
            limits = (strip.action_frame_start, strip.action_frame_end)
            frames = (strip.frame_start, strip.frame_end)
            old_action = strip.action
            new_action = action.time_offset(old_action, limits, frames)
            depath.bake_path_offsets(
                context, parent, ob, new_action, specials)
            nla.replace_strip_action(strip, new_action)
        path.eval_time_activate(parent, False)
        ob.animation_data.action = original_action
        return {'FINISHED'}

    
def register():
    bpy.utils.register_class(NLACycleStrip)
    bpy.utils.register_class(DeCurveStrips)

def unregister():
    bpy.utils.unregister_class(NLACycleStrip)
    bpy.utils.unregister_class(DeCurveStrips)

if __name__ == "__main__":
    register()
