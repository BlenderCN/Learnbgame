# wahooney_set_bone_lengths.py Copyright (C) 2012, Keith "Wahooney" Boshoff
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

'''
HISTORY:

1.0:
 * Initial version

'''

bl_info = {
    'name': 'Set Bone Lengths',
    'author': 'Keith (Wahooney) Boshoff',
    'version': '1.0',
    'blender': (2, 6, 2),
    'url': 'http://wahooney.net',
    'category': 'Armature'}
    
import bpy
from mathutils import Vector
from bpy.props import *

def main(self, context):
    
    length = self.properties.length
    method = self.properties.method
    multiplier = self.properties.length_multiplier
    bias = self.properties.bias
    
    for bone in context.selected_bones:
        
        head = bone.head
        tail = bone.tail
        
        vec = (tail - head)
        old_length = vec.length
        
        if method == 'RELATIVE':
            length = old_length * multiplier
        
        vec = vec / old_length
        
        tail = tail + vec*(length - old_length)*(bias)
        head = head - vec*(length - old_length)*(1.0-bias)
                
        bone.tail = tail
        bone.head = head

class SetBoneLength(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "armature.set_bone_length"
    bl_label = "Set Bone Length"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(name="Length", description="Total Length",
            default=0.2,
            min=0.0,
            max=100,
            soft_min=0.0,
            soft_max=2.0)
            
    length_multiplier = FloatProperty(name="Length Multiplier", description="Length Multiplier",
            default=1.0,
            min=-100.0,
            max=100,
            soft_min=-2.0,
            soft_max=2.0)
            
    bias = FloatProperty(name="Head/Tail", description="Scale the bone towards the head or the tail",
            default=1.0,
            min=0.0,
            max=1.0,
            soft_min=0.0,
            soft_max=1.0)
            
    method = EnumProperty(items=(
                    ('ABSOLUTE', "Absolute", "Length is set"),
                    ('RELATIVE', "Relative", "Length is multiplied")),
            name="Method",
            description="Bone length method, set size absolutely or multiply",
            default='RELATIVE')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}
        
    def draw(self, context):
        layout = self.layout
        props = self.properties
        
        layout.prop(props, "method", expand=True)
        
        if self.properties.method == 'RELATIVE':
            layout.prop(props, "length_multiplier")
        else:
            layout.prop(props, "length")
        
        layout.prop(props, "bias", slider=True)

def register():
    bpy.utils.register_class(SetBoneLength)

def unregister():
    bpy.utils.unregister_class(SetBoneLength)

if __name__ == "__main__":
    register()