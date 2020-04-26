### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

bl_info = {
    "name": "Automatic Walk Cycle",
    "author": "Germano Cavalcante",
    "version": (1, 5),
    "blender": (2, 76, 0),
    "location": "Armature Properties (Object Data)",
    "description": "Automatically creates a walk cycle",
    #"wiki_url" : "http://blenderartists.org/forum/showthread.php?363859-Addon-CAD-Snap-Utilities",
    "category": "Animation"}

import bpy
from .ot_add_move import WalkCycleAddMove
from .ot_copy_pos import WalkCycleCopyLocation
from .ot_generator import WalkCycleGenerate
from .ot_invert_pos import WalkCycleInvertValues
from .ot_preview import WalkCyclePreview
from .ot_remove_move import WalkCycleRemoveMove
from .properties import WalkCycleNewBones, WalkCycleSettings

class DATA_PT_auto_walk_cycle(bpy.types.Panel):
    bl_label = "Automatic Walk Cycle"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    #bl_options = {'DEFAULT_OPEN'}

    @classmethod
    def poll(cls, context):
        if not context.armature:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        obj = context.object
        awc = obj.data.aut_walk_cycle
 
        col = layout.column()
        box = layout.box()
        row = box.row()
        ex_ic = "TRIA_DOWN" if awc.expand else "TRIA_RIGHT"
        row.prop(awc, "expand", icon=ex_ic, text="", emboss=False)
        row.prop_search(awc, "torso", obj.pose, "bones")
        if awc.expand and awc.torso:
            row = box.row()
            row.label(text="Forward:")
            row.prop(awc, "forward_torso", expand=True)
            row = box.row()
            row.prop(awc, "up_torso")
            row.label()

            #box = layout.box()
            row = box.row()
            row.prop_search(awc, "l_foot_ik", obj.pose, "bones")
            row.prop_search(awc, "r_foot_ik", obj.pose, "bones")
            if awc.l_foot_ik and awc.r_foot_ik:
                box.prop(awc, "step_by_frames")
                if not awc.step_by_frames:
                    box.prop(awc, "step")
                else:
                    box.prop(awc, "step_frames")
                box.prop(awc, "anticipation")
                box.prop(awc, "amp")
                box.prop(awc, "openness")
                box.prop(awc, "foot_rot")

        if awc.torso and awc.l_foot_ik and awc.r_foot_ik:
            col = layout.column()
            col.operator("armature.walk_cycle_add_move")
            for move in awc.new_bones:
                name = move.name
                col = layout.column(align=True)
                col.context_pointer_set("awc_bone", move)
                row = col.box().row()
                ex_ic = "TRIA_DOWN" if move.expand else "TRIA_RIGHT"
                row.prop(move, "expand", icon=ex_ic, text="", emboss=False)
                row.prop_search(move, "name", obj.pose, "bones")
                shw_ic = "RESTRICT_VIEW_OFF" if move.show else "RESTRICT_VIEW_ON"
                row.prop(move, "show", icon=shw_ic, text="", emboss=False)
                row.operator("armature.walk_cycle_remove_move", text="", icon='X', emboss=False)
                if move.expand and name:
                    bone = obj.pose.bones[name]
                    split = col.box().split()
                    col = split.column()
                    col.prop(move, "seq_type")
                    col.prop(move, "add_torso", text = 'Add torso movement')
                    split = col.split()
                    split.label(text="Initial Location:")
                    split.operator("armature.walk_cycle_copy_pos", text="", icon='EYEDROPPER', emboss=False).type = 0
                    split.label(text="Final Location:")
                    split.operator("armature.walk_cycle_copy_pos", text="", icon='EYEDROPPER', emboss=False).type = 1
                    split = col.split()
                    split.prop(move, "loc1", text = '')
                    split.prop(move, "loc2", text = '')
                    split = col.split()
                    split.operator("armature.walk_cycle_invert_pos", text="", icon='FILE_REFRESH', emboss=False)
                    split = col.split()
                    split.label(text="Initial Rotation:")
                    split.operator("armature.walk_cycle_copy_pos", text="", icon='EYEDROPPER', emboss=False).type = 2
                    split.label(text="Final Rotation:")
                    split.operator("armature.walk_cycle_copy_pos", text="", icon='EYEDROPPER', emboss=False).type = 3
                    split = col.split()
                    if bone.rotation_mode == 'QUATERNION':
                        split.prop(move, "qua1", text = '')
                        split.prop(move, "qua2", text = '')
                    elif bone.rotation_mode == 'AXIS_ANGLE':
                        split.prop(move, "axi1", text = '')
                        split.prop(move, "axi2", text = '')
                    else:
                        split.prop(move, "eul1", text = '')
                        split.prop(move, "eul2", text = '')

            row = layout.row()
            if context.scene.awc_is_preview:
                text = 'Stop Preview'
            else:
                text = 'Preview'
            row.operator("armature.walk_cycle_preview", text = text)
            row.prop(awc, "anim")
            if not awc.anim:
                row.prop(awc, "frequency")
            row = layout.row(align=True)
            row.prop(awc, "frame_start")
            row.prop(awc, "frame_end")
            layout.operator("armature.walk_cycle_generate")

def register():
    print('---------------------------------------------------------------')
    bpy.utils.register_class(WalkCycleNewBones)
    bpy.utils.register_class(WalkCycleSettings)
    bpy.types.Armature.aut_walk_cycle = bpy.props.PointerProperty(type=WalkCycleSettings)
    bpy.types.Scene.awc_is_preview = bpy.props.BoolProperty()
    #bpy.app.handlers.frame_change_pre.clear()

    bpy.utils.register_class(WalkCycleAddMove)
    bpy.utils.register_class(WalkCycleRemoveMove)
    bpy.utils.register_class(WalkCycleCopyLocation)
    bpy.utils.register_class(WalkCycleInvertValues)
    bpy.utils.register_class(WalkCyclePreview)
    bpy.utils.register_class(WalkCycleGenerate)
    bpy.utils.register_class(DATA_PT_auto_walk_cycle)

def unregister():
    bpy.utils.unregister_class(DATA_PT_auto_walk_cycle)
    bpy.utils.unregister_class(WalkCycleGenerate)
    bpy.utils.unregister_class(WalkCyclePreview)
    bpy.utils.unregister_class(WalkCycleInvertValues)
    bpy.utils.unregister_class(WalkCycleCopyLocation)   
    bpy.utils.unregister_class(WalkCycleRemoveMove)
    bpy.utils.unregister_class(WalkCycleAddMove)

    #if frame_pre in bpy.app.handlers.frame_change_pre:
        #bpy.app.handlers.frame_change_pre.remove(frame_pre)
    del bpy.types.Scene.awc_is_preview
    del bpy.types.Armature.aut_walk_cycle
    bpy.utils.unregister_class(WalkCycleSettings)
    bpy.utils.unregister_class(WalkCycleNewBones)

if __name__ == "__main__":
    #__name__ = "animation_auto_walk_cycle"
    #__package__ = "animation_auto_walk_cycle"
    register()
