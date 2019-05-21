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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Randomiser",
    "author": "Ben Simonds",
    "version": (0, 3),
    "blender": (2, 7, 0),
    "location": "Properties > Object Data > Randomise",
    "description": "Tools for randomising and animating text data (and some limited object data). Website: http://bensimonds.com/2014/04/02/randomiser-add-on/",
    #"warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/BenSimonds/Randomiser/issues",
    "category": "Object",
    }

import bpy
from .Randomiser_addon import *


# Randomiser UI:

class RandomiserPanelObject(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Randomise Object Data"

    def draw(self, context):
        ob = bpy.context.active_object
        randomise = ob.randomiser
        layout = self.layout

        row = layout.row()
        row.prop(randomise, "use_randomise")
        if randomise.use_randomise:
            row.prop(randomise, "seed")
            #Update Method Props:
            box = layout.box()
            row = box.row()
            row.prop(randomise, "offset")

            row = box.row()
            row.prop(randomise, 'update_method')
            row = box.row()
            if randomise.update_method == 'man':
                row.prop(randomise, "time")
            elif randomise.update_method == 'freq':
                row.prop(randomise, 'period')

            #Generate Method Props:
            box.separator()
            row = box.row()
            row.prop(randomise, "generate_method")
            row = box.row()
            row.prop(randomise, "source_group")
            if randomise.generate_method == 'random':
                row = box.row()
                row.alignment = 'RIGHT'
                row.prop(randomise, "no_repeats")

class RandomiserPanelText(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Randomise Text Data"

    @classmethod
    def poll(self, context):
        ob = bpy.context.active_object
        return ob.type == 'FONT'


    def draw(self, context):
        ob = bpy.context.active_object
        if ob.type == 'FONT':
            text_data = ob.data
            randomise = text_data.randomiser
            layout = self.layout

            row = layout.row()
            row.prop(randomise, "use_randomise")

            if randomise.use_randomise:
                row.prop(randomise, "seed")
                #Update Method Props:
                box = layout.box()
                row = box.row()
                row.prop(randomise, "update_method")
                row = box.row()
                row.prop(randomise, "offset")
                if randomise.update_method == 'man':
                    row.prop(randomise, "time")
                elif randomise.update_method == 'freq':
                    row.prop(randomise, "period")

                #Generate Method Properties:
                row = box.row()
                col = row.column()
                col.separator()
                row = col.row()
                row.prop(randomise, "generate_method")
                if randomise.generate_method == 'random':
                    row = col.row()
                    row.prop(randomise, "no_repeats")
                elif randomise.generate_method == 'ticker':
                    row = col.row()
                    row.prop(randomise, "ticklength")

                elif randomise.generate_method == 'numeric':
                    row = col.row()
                    row.alignment = 'RIGHT'
                    row.prop(randomise, "group_digits")

                elif randomise.generate_method == 'clock':
                    row = col.row()
                    row.prop(randomise, 'clock_hours')
                    row.prop(randomise, 'clock_minutes')
                    row = col.row()
                    if randomise.clock_seconds:
                        minsec = "Seconds"
                    else:
                        minsec = "Minutes"
                    row.prop(randomise, 'clock_seconds', toggle = True, text = minsec)
                    row.prop(randomise, 'clock_24hr')
                    row = col.row()

                    frame = bpy.context.scene.frame_current
                    i = get_iter(text_data, 'update', 0, frame)
                    if randomise.clock_seconds:
                        x = 1
                    else:
                        x = 60
                    time = (i*x) + (randomise.clock_minutes*60) + (randomise.clock_hours * 3600)
                    h, m, s = time_to_clock(time)
                    if randomise.clock_24hr:
                        h = h % 24
                    else:
                        h = h % 12
                    string = str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)
                    row.label(text = "Time: " + string)

                else:
                    row = col.row()
                    row.label(text = "Source:")

                    if randomise.generate_method == "grow":
                        row = col.row()
                        row.prop(randomise, "textdata")
                        #Leader:
                        row = col.row()
                        row.prop(randomise, "leader")
                        if randomise.leader == 'flash':
                            row = box.row()
                            row.prop(randomise, "leader_period")

                    elif randomise.generate_method == "ticker":
                        row = box.row()
                        row.prop(randomise, "textdata")

                    else:
                        if randomise.textsource in ["alphanumeric","characters"]:
                            box.prop(randomise, "textsource")
                            box.prop(randomise, "caps")
                        if randomise.textsource  in ["binary", "digits"]:
                            box.prop(randomise, "textsource")
                        if randomise.textsource in ["tbchars","tblines"]:
                            box.prop(randomise, "textsource")
                            box.prop(randomise, "textdata")

                layout = self.layout
                layout.separator()


           # Noise properties
                row = layout.row()
                row.prop(randomise, "use_noise")

                if randomise.use_noise or randomise.leader == 'random':
                    box = layout.box()

                    if randomise.use_noise:
                        row = box.row()
                        row.prop(randomise, "noise_update_method")
                        if randomise.noise_update_method == 'man':
                            row.prop(randomise, "noise_time")
                        elif randomise.noise_update_method == 'freq':
                            row.prop(randomise, "noise_period")

                        row = box.row()
                        row.prop(randomise, "noise_method")
                        if randomise.noise_method == "mask":
                            row = box.row()
                            row.prop(randomise, "noise_mask")
                            row = box.row()
                        else:
                            row = box.row()
                            row.prop(randomise, "noise_threshold")

                            row = box.row()
                            row.prop(randomise, "noise_mask_update_method")
                            if randomise.noise_mask_update_method == 'man':
                                row.prop(randomise, "noise_mask_time")
                            elif randomise.noise_mask_update_method == 'freq':
                                row.prop(randomise, "noise_mask_period")
                        row = box.row()
                        #row.alignment = 'RIGHT'
                        row.prop(randomise, "noise_ignore_whitespace")
                        row.prop(randomise, "noise_ignore_custom")


                    #Noise source for both noise and leader:
                    if randomise.use_noise or randomise.leader == 'random':
                        row = box.row()
                        row.prop(randomise, "noise_source")
                        if randomise.noise_source in ['characters','alphanumeric']:
                            row = box.row()
                            row.prop(randomise, "caps")
                        elif randomise.noise_source == 'tbchars':
                            row = box.row()
                            row.prop(randomise, 'noise_textdata')

#Registration:
def register():
    #Properties:
    bpy.utils.register_class(RandomiserObjectProps)
    bpy.utils.register_class(RandomiserTextProps)
    bpy.types.Object.randomiser = bpy.props.PointerProperty(type = RandomiserObjectProps)
    bpy.types.TextCurve.randomiser = bpy.props.PointerProperty(type = RandomiserTextProps)

    #Operators:
    bpy.utils.register_class(RandomiseTextData)
    bpy.utils.register_class(RandomiseObjectData)
    bpy.utils.register_class(RandomiseSpreadSeeds)
    bpy.utils.register_class(RandomiseCopySeed)

    #UI:
    bpy.utils.register_class(RandomiserPanelObject)
    bpy.utils.register_class(RandomiserPanelText)

    #Handlers
    bpy.app.handlers.frame_change_post.append(randomise_handler)
    bpy.app.handlers.render_post.append(randomise_handler)


def unregister():
    #Properties:
    bpy.utils.unregister_class(RandomiserObjectProps)
    bpy.utils.unregister_class(RandomiserTextProps)

    #Operators:
    bpy.utils.unregister_class(RandomiseTextData)
    bpy.utils.unregister_class(RandomiseObjectData)
    bpy.utils.unregister_class(RandomiseSpreadSeeds)
    bpy.utils.unregister_class(RandomiseCopySeed)

    #UI:
    bpy.utils.unregister_class(RandomiserPanelObject)
    bpy.utils.unregister_class(RandomiserPanelText)

    #Handlers:
    bpy.app.handlers.frame_change_post.remove(randomise_handler)
    bpy.app.handlers.render_post.remove(randomise_handler)



