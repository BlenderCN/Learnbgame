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


def blenderActionGroup2Applicator(bl_actiongroup):
    appli = plMatrixChannelApplicator()
    appli.channelName = bl_actiongroup.name
    mtrxchl = plMatrixControllerChannel()
    mtrxchl.affine = hsAffineParts()
    mtrxchl.controller = plTMController()
    appli.channel = mtrxchl

    return appli

def processArmature(blObj,animname):
    anim = plATCAnim(animname)
    anim.name = animname
    anim.initial = -1.0
    anim.autoStart = True
    anim.loop = False

    anim.easeInMin = 0.0    
    anim.easeInMax = 0.0
    anim.easeInLength = 0.0
    anim.easeOutMin = 0.0    
    anim.easeOutMax = 0.0
    anim.easeOutLength = 0.0

    arm_action = blObj.animation_data.action
    for actiongroup in arm_action.groups:
        anim.addApplicator(blenderActionGroup2Applicator(actiongroup))
#    anim.end = endtime
#    anim.loopEnd = endtime
    
    return anim
