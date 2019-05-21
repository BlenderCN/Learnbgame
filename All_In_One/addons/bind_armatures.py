#-------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Vadim Macagon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------
# <pep8 compliant>

import bpy

bl_info = {
    "name": "Bind Armatures",
    "author": "Vadim Macagon",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "category": "Rigging",
    "description": "Hooks up a simple game-ready armature to a Rigify or advanced MakeHuman armature."
}

# mapping of game rig deform bones to Rigify deform bones, the game rig layout is similar
# to the standard Unity3d Mecanim layout (minus the mouth/eye bones since I don't have any
# use for them yet)
rigify_bone_map = {
    "hips": "DEF-hips",
        "spine": "DEF-spine",
            "chest": "DEF-chest",
                "chest-1": "DEF-chest-1",
                    "neck": "DEF-neck",
                        "head": "DEF-head",
                    "shoulder.L": "DEF-shoulder.L",
                        "upper_arm.L": "DEF-upper_arm.01.L",
                            "forearm.L": "DEF-forearm.01.L",
                                "hand.L": "DEF-hand.L",
                                    "thumb.01.L": "DEF-thumb.01.L.02",
                                        "thumb.02.L": "DEF-thumb.02.L",
                                            "thumb.03.L" : "DEF-thumb.03.L",
                                    "f_index.01.L": "DEF-f_index.01.L.02",
                                        "f_index.02.L": "DEF-f_index.02.L",
                                            "f_index.03.L" : "DEF-f_index.03.L",
                                    "f_middle.01.L": "DEF-f_middle.01.L.02",
                                        "f_middle.02.L": "DEF-f_middle.02.L",
                                            "f_middle.03.L": "DEF-f_middle.03.L",
                                    "f_ring.01.L": "DEF-f_ring.01.L.02",
                                        "f_ring.02.L": "DEF-f_ring.02.L",
                                            "f_ring.03.L": "DEF-f_ring.03.L",
                                    "f_pinky.01.L": "DEF-f_pinky.01.L.02",
                                        "f_pinky.02.L": "DEF-f_pinky.02.L",
                                            "f_pinky.03.L": "DEF-f_pinky.03.L",
                    "shoulder.R": "DEF-shoulder.R",
                        "upper_arm.R": "DEF-upper_arm.01.R",
                            "forearm.R": "DEF-forearm.01.R",
                                "hand.R": "DEF-hand.R",
                                    "thumb.01.R": "DEF-thumb.01.R.02",
                                        "thumb.02.R": "DEF-thumb.02.R",
                                            "thumb.03.R" : "DEF-thumb.03.R",
                                    "f_index.01.R": "DEF-f_index.01.R.02",
                                        "f_index.02.R": "DEF-f_index.02.R",
                                            "f_index.03.R" : "DEF-f_index.03.R",
                                    "f_middle.01.R": "DEF-f_middle.01.R.02",
                                        "f_middle.02.R": "DEF-f_middle.02.R",
                                            "f_middle.03.R": "DEF-f_middle.03.R",
                                    "f_ring.01.R": "DEF-f_ring.01.R.02",
                                        "f_ring.02.R": "DEF-f_ring.02.R",
                                            "f_ring.03.R": "DEF-f_ring.03.R",
                                    "f_pinky.01.R": "DEF-f_pinky.01.R.02",
                                        "f_pinky.02.R": "DEF-f_pinky.02.R",
                                            "f_pinky.03.R": "DEF-f_pinky.03.R",
        "thigh.L": "DEF-thigh.01.L",
            "shin.L": "DEF-shin.01.L",
                "foot.L": "DEF-foot.L",
                    "toe.L": "DEF-toe.L",
        "thigh.R": "DEF-thigh.01.R",
            "shin.R": "DEF-shin.01.R",
                "foot.R": "DEF-foot.R",
                    "toe.R": "DEF-toe.R"
}

# mapping of game rig deform bones to the deform bones in an advanced MakeHuman generated rig,
# unfortunately this doesn't work properly because the hips bone of the MakeHuman rig is inverted
# (i.e. hips bone points in the opposite direction to the spine bone), also unsure about the
# shoulders
mhx_bone_map = {
    "hips": "DEF-hips",
        "spine": "DEF-spine",
            "chest": "DEF-chest",
                "chest-1": "DEF-chest-1",
                    "neck": "DEF-neck",
                        "head": "DEF-head",
                    "shoulder.L": "DEF-clavicle.L",
                        "upper_arm.L": "DEF-upper_arm.L",
                            "forearm.L": "DEF-forearm.01.L",
                                "hand.L": "DEF-hand.L",
                                    "thumb.01.L": "DEF-thumb.01.L",
                                        "thumb.02.L": "DEF-thumb.02.L",
                                            "thumb.03.L" : "DEF-thumb.03.L",
                                    "f_index.01.L": "DEF-f_index.01.L",
                                        "f_index.02.L": "DEF-f_index.02.L",
                                            "f_index.03.L" : "DEF-f_index.03.L",
                                    "f_middle.01.L": "DEF-f_middle.01.L",
                                        "f_middle.02.L": "DEF-f_middle.02.L",
                                            "f_middle.03.L": "DEF-f_middle.03.L",
                                    "f_ring.01.L": "DEF-f_ring.01.L",
                                        "f_ring.02.L": "DEF-f_ring.02.L",
                                            "f_ring.03.L": "DEF-f_ring.03.L",
                                    "f_pinky.01.L": "DEF-f_pinky.01.L",
                                        "f_pinky.02.L": "DEF-f_pinky.02.L",
                                            "f_pinky.03.L": "DEF-f_pinky.03.L",
                    "shoulder.R": "DEF-clavicle.R",
                        "upper_arm.R": "DEF-upper_arm.R",
                            "forearm.R": "DEF-forearm.01.R",
                                "hand.R": "DEF-hand.R",
                                    "thumb.01.R": "DEF-thumb.01.R",
                                        "thumb.02.R": "DEF-thumb.02.R",
                                            "thumb.03.R" : "DEF-thumb.03.R",
                                    "f_index.01.R": "DEF-f_index.01.R",
                                        "f_index.02.R": "DEF-f_index.02.R",
                                            "f_index.03.R" : "DEF-f_index.03.R",
                                    "f_middle.01.R": "DEF-f_middle.01.R",
                                        "f_middle.02.R": "DEF-f_middle.02.R",
                                            "f_middle.03.R": "DEF-f_middle.03.R",
                                    "f_ring.01.R": "DEF-f_ring.01.R",
                                        "f_ring.02.R": "DEF-f_ring.02.R",
                                            "f_ring.03.R": "DEF-f_ring.03.R",
                                    "f_pinky.01.R": "DEF-f_pinky.01.R",
                                        "f_pinky.02.R": "DEF-f_pinky.02.R",
                                            "f_pinky.03.R": "DEF-f_pinky.03.R",
        "thigh.L": "DEF-thigh.L",
            "shin.L": "DEF-shin.01.L",
                "foot.L": "DEF-foot.L",
                    "toe.L": "DEF-toe.L",
        "thigh.R": "DEF-thigh.R",
            "shin.R": "DEF-shin.01.R",
                "foot.R": "DEF-foot.R",
                    "toe.R": "DEF-toe.R"
}

class BindArmaturesOperator(bpy.types.Operator):
    """
    Hooks up the currently selected game-ready armature (generated by MakeHuman) to a more complex
    armature (also generated by MakeHuman) which is either a Rigify armature or an advanced
    MakeHuman armature. Once the armatures are hooked up the game-ready armature can be indirectly
    animated via the Rigify or MakeHuman controls.
    """
    bl_idname = "armature.bind_armatures"
    bl_label = "Bind Armatures"
    bl_options = {'REGISTER', 'UNDO'}

    target_armature_name = bpy.props.StringProperty(
        name = "Target Armature",
        description = "The armature that the currently selected armature should be bound to."
    )

    target_armature_type = bpy.props.EnumProperty(
        name = "Target Armature Type",
        description = "The type of the target armature.",
        items = [
            ("rigify", "Rigify",    "Humanoid Rigify armature"),
            ("mhx",    "MakeHuman", "Advanced MakeHuman armature")
        ],
        default = "rigify"
    )

    # collection of armatures from which the target armature must be chosen
    available_armatures = bpy.props.CollectionProperty(type = bpy.types.PropertyGroup)

    bone_maps = {
        "rigify": rigify_bone_map,
        "mhx": mhx_bone_map
    }

    @classmethod
    def poll(cls, context):
        # for this operator to work an armature must be currently selected
        return (
            (context.active_object is not None)
            and (context.mode == 'OBJECT')
            and (context.active_object.type == 'ARMATURE')
        )

    def execute(self, context):
        if self.target_armature_name in bpy.data.armatures:
            self.bind_rigs(
                context.active_object, # the simple armature
                bpy.data.objects[self.target_armature_name], # the complex armature
                self.bone_maps[self.target_armature_type]
            )
        else:
            self.report({'ERROR'}, "Target armature not found!")
        return {'FINISHED'}

    # initialize the operator from the context
    def invoke(self, context, event):
        # collect all the armatures that can be used as targets for the operator
        self.available_armatures.clear()
        for obj in bpy.data.objects:
            if (obj.type == 'ARMATURE') and (context.active_object.name != obj.name):
                self.available_armatures.add().name = obj.name

        # display a dialog to let the user set operator properties
        return context.window_manager.invoke_props_dialog(self, width = 400)

    # layout the operator properties dialog
    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "target_armature_name", self, "available_armatures")
        layout.prop(self, "target_armature_type")

    def bind_rigs(self, source_rig, target_rig, bone_map):
        # pose bones should be edited in POSE mode
        bpy.ops.object.mode_set(mode = 'POSE')

        for (source_bone_name, target_bone_name) in bone_map.items():
            # TODO: check if this constraint already exists (ignore the name), and if so don't
            #       create it again
            source_bone = source_rig.pose.bones[source_bone_name]
            constraint = source_bone.constraints.new(type = 'COPY_TRANSFORMS')
            constraint.name = "Copy Target Bone Transforms"
            constraint.target = target_rig
            constraint.subtarget = target_bone_name
            constraint.owner_space = 'WORLD'
            constraint.target_space = 'WORLD'

        bpy.ops.object.mode_set(mode = 'OBJECT')

def register():
    bpy.utils.register_class(BindArmaturesOperator)

def unregister():
    bpy.utils.unregister_class(BindArmaturesOperator)

# for debugging
if __name__ == "__main__":
    register()
