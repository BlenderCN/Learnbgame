#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from PyHSPlasma import *

class ViewFaceModifier(bpy.types.Operator):
    bl_idname = 'object.plviewfacemodifier'
    bl_label = 'Sprite'
    bl_description = 'Object swivels to face a point'
    category = 'Render'

    __has_init = False

    @staticmethod
    def InitProperties(mod):
        mod.EnumProperty(attr="followmode",
                        items = (
                            ('cam', 'Camera', ''),
                            ('list', 'Listener', ''),
                            ('play', 'Local Player', ''),
                            ('obj', 'Object', '')
                        ),
                        name="Follow Mode",
                        description="What the sprite should follow.", 
                        default='cam')
        mod.PointerProperty(attr="followobj",
                            type = bpy.types.IDPropertyGroup,
                            name = "Follow Object",
                            description="The object to follow.")
        ViewFaceModifier.__has_init = True

    @staticmethod
    def Export(ob, mod):
        pass

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        ob = context.object
        pl = ob.plasma_settings
        mod = pl.modifiers.add()
        if not ViewFaceModifier.__has_init:
            ViewFaceModifier.InitProperties(mod)
        mod.name = ob.name
        mod.modclass = ViewFaceModifier.bl_idname.split('.')[1]
        return {'FINISHED'}

class ViewFaceModPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'constraint'
    bl_label = 'Face Things'

    @classmethod
    def poll(self, context):
        ob = context.active_object
        if not ob is None:
            pl = ob.plasma_settings
            if len(pl.modifiers) > 0:
                return pl.modifiers[pl.activemodifier].modclass == ViewFaceModifier.bl_idname.split('.')[1]
        return False

    def draw(self, context):
        layout = self.layout
        
        ob = context.active_object
        pl = ob.plasma_settings
        plmod = pl.modifiers[pl.activemodifier]
        layout.prop(plmod, "followmode")
        if plmod.followmode == 'obj':
            layout.prop_object(plmod, 'followobj', context.main, 'objects')

def register():
    bpy.types.register(ViewFaceModifier)
    bpy.types.register(ViewFaceModPanel)

    return [ViewFaceModifier]

def unregister():
    bpy.types.unregister(ViewFaceModifier)
    bpy.types.unregister(ViewFaceModPanel)
