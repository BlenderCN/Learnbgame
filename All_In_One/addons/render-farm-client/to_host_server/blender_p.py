# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# system imports
import bpy
import random
from bpy.app.handlers import persistent

scn = bpy.context.scene

""" BEGIN SUPPORT FOR BRICKER """

@persistent
def handle_bricker_animation(scene):
    print("Adjusting frame")
    groupsToAdjust = {}
    getFrameNum = lambda n: int(n[n.index("_bricks_f_") + 10:])
    for group in bpy.data.groups:
        if group.name.startswith("Bricker") and "_bricks_f_" in group.name:
            sourceName = group.name[9:(group.name.index("_bricks_f_"))]
            if sourceName not in groupsToAdjust.keys():
                groupsToAdjust[sourceName] = [group.name]
            else:
                groupsToAdjust[sourceName].append(group.name)
    for sourceName in groupsToAdjust:
        groupsToAdjust[sourceName].sort(key=lambda n: getFrameNum(n))
        for i,gName in enumerate(groupsToAdjust[sourceName]):
            group = bpy.data.groups.get(gName)
            frame = getFrameNum(group.name)
            onCurF = frame == scn.frame_current
            beforeFirstF = i == 0 and scn.frame_current < frame
            afterLastF = i == len(groupsToAdjust[sourceName]) - 1 and scn.frame_current > frame
            displayOnCurF = onCurF or beforeFirstF or afterLastF
            brick = group.objects[0]
            if brick.hide == displayOnCurF:
                brick.hide = not displayOnCurF
                brick.hide_render = not displayOnCurF

handle_bricker_animation(scn)
bpy.app.handlers.render_pre.append(handle_bricker_animation)
bpy.app.handlers.frame_change_pre.append(handle_bricker_animation)

""" END SUPPORT FOR BRICKER """

randomSeed = random.randint(1, 10000)
for scn in bpy.data.scenes:
    scn.cycles.seed = randomSeed
    scn.cycles.transparent_min_bounces = 0
    scn.cycles.min_bounces = 0
    scn.cycles.blur_glossy = 0
    scn.render.use_overwrite = True
    if scn.cycles.film_transparent:
        scn.render.image_settings.color_mode = 'RGBA'
    # apply performance settings
    # typ = "NONE"
    # cyclesPrefs = bpy.context.user_preferences.addons['cycles'].preferences
    # devices = [x[0] for x in cyclesPrefs.get_device_types(bpy.context)]
    # if typ != "DEFAULT":
    #     cyclesPrefs.compute_device_type = typ if typ in devices else "NONE"
    #
    # cyclesPrefs.
