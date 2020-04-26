'''
Copyright (C) 2018 Samy Tichadou (tonton)
samytichadou@gmail.com

Created by Samy Tichadou (tonton)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
 "name": "Playblaster",
 "author": "Samy Tichadou (tonton)",
 "version": (0, 1),
 "blender": (2, 80, 0),
 "location": "Search Menu",
 "description": "Quick Playblast of your Animation",
 "wiki_url": "https://github.com/samytichadou/Playblaster/wiki",
 "tracker_url": "https://github.com/samytichadou/Playblaster/issues/new",
 "category": "Learnbgame",
 }


import bpy


# IMPORT SPECIFICS
##################################

from .render_operator import PlayblasterRenderOperator
from .preferences import PlayblasterAddonPrefs
from .modal_check import PlayblasterModalCheck
from .set_preferences_operator import PlayblasterSetPreferences
from .play_rendered_operator import PlayblasterPlayRendered


# register
##################################

classes = (PlayblasterRenderOperator,
            PlayblasterAddonPrefs,
            PlayblasterModalCheck,
            PlayblasterSetPreferences,
            PlayblasterPlayRendered
            )

def register():

    ### OPERATORS ###

    from bpy.utils import register_class
    for cls in classes :
        register_class(cls)

    ### PROPS ###

    bpy.types.Scene.playblaster_render_engine = \
        bpy.props.EnumProperty(
                        name = "Engine",
                        default = 'BLENDER_EEVEE',
                        items = (
                        ('BLENDER_WORKBENCH', "Workbench", ""),
                        ('BLENDER_EEVEE', "EEVEE", ""),
                        ))

    bpy.types.Scene.playblaster_resolution_percentage = \
        bpy.props.IntProperty(name = "Resolution Percentage", default = 50, min = 1, max = 100)

    bpy.types.Scene.playblaster_frame_range_override = \
        bpy.props.BoolProperty(name = "Frame Range Override", default = False)

    bpy.types.Scene.playblaster_frame_range_in = \
        bpy.props.IntProperty(name = "Start Frame", min = 0, default = 1)

    bpy.types.Scene.playblaster_frame_range_out = \
        bpy.props.IntProperty(name = "End Frame", min = 1, default = 100)

    bpy.types.Scene.playblaster_use_compositing = \
        bpy.props.BoolProperty(name = "Compositing", default = False)

    bpy.types.Scene.playblaster_eevee_samples = \
        bpy.props.IntProperty(name = "EEVEE Samples", default = 8, min = 4, max = 128)

    bpy.types.Scene.playblaster_eevee_dof = \
        bpy.props.BoolProperty(name = "EEVEE DoF", default = False)

    bpy.types.Scene.playblaster_eevee_ambient_occlusion = \
        bpy.props.BoolProperty(name = "EEVEE AO", default = False)

    bpy.types.Scene.playblaster_simplify = \
        bpy.props.BoolProperty(name = "Simplify", default = True)

    bpy.types.Scene.playblaster_simplify_subdivision = \
        bpy.props.IntProperty(name = "Max Subdivision", default = 0, min = 0, max = 6)

    bpy.types.Scene.playblaster_simplify_particles = \
        bpy.props.FloatProperty(name = "Max Child Particles", default = 0, min = 0, max = 1)



    bpy.types.Scene.playblaster_is_rendering = \
        bpy.props.BoolProperty()

    bpy.types.Scene.playblaster_completion = \
        bpy.props.IntProperty(min = 0, max = 100)

    bpy.types.Scene.playblaster_previous_render = \
        bpy.props.StringProperty()

    bpy.types.Scene.playblaster_debug = \
        bpy.props.BoolProperty(name = "Debug")

def unregister():

    ### OPERATORS ###

    from bpy.utils import unregister_class
    for cls in reversed(classes) :
        unregister_class(cls)

    ### PROPS ###

    del bpy.types.Scene.playblaster_render_engine
    del bpy.types.Scene.playblaster_frame_range_override
    del bpy.types.Scene.playblaster_frame_range_in
    del bpy.types.Scene.playblaster_frame_range_out
    del bpy.types.Scene.playblaster_resolution_percentage
    del bpy.types.Scene.playblaster_use_compositing
    del bpy.types.Scene.playblaster_eevee_samples
    del bpy.types.Scene.playblaster_eevee_dof
    del bpy.types.Scene.playblaster_eevee_ambient_occlusion
    del bpy.types.Scene.playblaster_simplify
    del bpy.types.Scene.playblaster_simplify_subdivision
    del bpy.types.Scene.playblaster_simplify_particles

    del bpy.types.Scene.playblaster_is_rendering
    del bpy.types.Scene.playblaster_completion
    del bpy.types.Scene.playblaster_previous_render
    del bpy.types.Scene.playblaster_debug
