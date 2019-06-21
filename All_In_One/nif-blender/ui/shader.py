''' Nif User Interface, connect custom properties from properties.py into Blenders UI'''

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright © 2005-2015, NIF File Format Library and Tools contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import bpy
from bpy.types import Panel


class ObjectShader(Panel):
    bl_label = "Niftools Shader"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        nif_obj_props = context.object.niftools_shader

        layout = self.layout
        row = layout.column()

        row.prop(nif_obj_props, "bs_shadertype")

        if nif_obj_props.bs_shadertype == 'BSShaderPPLightingProperty':
            row.prop(nif_obj_props, "bsspplp_shaderobjtype")
            row.separator()
            row.separator()
            for item in nif_obj_props.bssf_shader_list0:
                row.prop(nif_obj_props, item)
            row.separator()
            row.separator()
            for item in nif_obj_props.bssf_shader_list2:
                row.prop(nif_obj_props, item)

        if nif_obj_props.bs_shadertype in ('BSLightingShaderProperty', 'BSEffectShaderProperty'):
            row.prop(nif_obj_props, "bslsp_shaderobjtype")
            row.separator()
            row.separator()
            row.label(text="Shader Flags 1")
            row.separator()
            for item in nif_obj_props.bsspplp_shader_list1:
                row.prop(nif_obj_props, item)
            row.separator()
            row.separator()
            row.label(text="Shader Flags 2")
            row.separator()
            for item in nif_obj_props.bsspplp_shader_list2:
                row.prop(nif_obj_props, item)
            row.separator()
            row.separator()


def register():
    bpy.utils.register_class(ObjectShader)


def unregister():
    bpy.utils.unregister_class(ObjectShader)
