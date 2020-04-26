''' Nif User Interface, custom nif properties for shaders'''

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

from bpy.types import PropertyGroup
from bpy.props import (PointerProperty,
                       IntProperty,
                       BoolProperty,
                       EnumProperty,
                       )

from pyffi.formats.nif import NifFormat


class ShaderProps(PropertyGroup):
    @classmethod
    def register(cls):
        default_item = 0
        bpy.types.Object.niftools_shader = PointerProperty(name='Niftools BsShader Property',
                                                           description='Properties used by the BsShader for the Nif File Format',
                                                           type=cls
                                                           )

        cls.bs_shadertype = EnumProperty(name='Shader Type',
                                         description='Type of property used to display meshes.',
                                         items=(('None', 'None', "", 0),
                                                ('BSShaderProperty', 'BS Shader Property', "", 1),
                                                ('BSShaderPPLightingProperty', 'BS Shader PP Lighting Property', "", 2),
                                                ('BSLightingShaderProperty', 'BS Lighting Shader Property', "", 3),
                                                ('BSEffectShaderProperty', 'BS Effect Shader Property', "", 4)
                                                )
                                         )

        cls.bsspplp_shaderobjtype = EnumProperty(name='Fallout3 Lighting Shader',
                                                 description='Type of object linked to shader',
                                                 items=[(item, item, "", i) for i, item in enumerate(NifFormat.BSShaderType._enumkeys)],
                                                 default=NifFormat.BSShaderType._enumkeys[ShaderProps.enum_list_default(default_item, NifFormat.BSShaderType)]
                                                 )

        cls.bssf_shader_list0 = NifFormat.BSShaderFlags._names
        cls.bssf_shader_list2 = NifFormat.BSShaderFlags2._names

        cls.bslsp_shaderobjtype = EnumProperty(name='Skyrim Lighting Shader',
                                               description='Type of object linked to shader',
                                               items=[(item, item, "", i) for i, item in enumerate(NifFormat.BSLightingShaderPropertyShaderType._enumkeys)],
                                               default=NifFormat.BSLightingShaderPropertyShaderType._enumkeys[ShaderProps.enum_list_default(default_item, NifFormat.BSLightingShaderPropertyShaderType)]
                                               )

        cls.bsspplp_shader_list1 = NifFormat.SkyrimShaderPropertyFlags1._names
        cls.bsspplp_shader_list2 = NifFormat.SkyrimShaderPropertyFlags2._names

        for flag_list in (cls.bssf_shader_list0, cls.bssf_shader_list2, cls.bsspplp_shader_list1, cls.bsspplp_shader_list2):
            for item in flag_list:
                setattr(cls, item, (BoolProperty(name=item)))

    def enum_list_default(self, shader_type):
        item_bool_list = []
        for i, item in enumerate(shader_type._enumkeys):
            if item in ("default", "Default", "DEFAULT"):
                shader_type_value = i
            item_bool_list.append(item)
        return shader_type_value

    @classmethod
    def unregister(cls):
        del bpy.types.Object.niftools_shader
