#
#  Copyright (c) 2018 Shane Ambler
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# made in response to https://blender.stackexchange.com/q/97746/935

bl_info = {
    "name": "Cycle mesh select",
    "author": "sambler",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "blender",
    "description": "Cycle through mesh selection modes.",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/mesh_select_cycle.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
    }

import bpy

class SelectCycle(bpy.types.Operator):
    bl_idname = 'mesh.select_cycle'
    bl_label = 'Cycles through selection modes.'

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        ts = context.tool_settings
        if ts.mesh_select_mode[0]:
            ts.mesh_select_mode = [False,True,False]
        elif ts.mesh_select_mode[1]:
            ts.mesh_select_mode = [False,False,True]
        else:
            ts.mesh_select_mode = [True,False,False]
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SelectCycle)

def unregister():
    bpy.utils.unregister_class(SelectCycle)

if __name__ == "__main__":
    register()
