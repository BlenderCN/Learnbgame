#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Face Bone Tool",
    "description": "Create facial bones and body bones for rigify.",
    "author": "khuuyj",
    "version": (0,6),
    "api":34074,
    "blender": (2, 5, 6),
    "location": "Tool > Face Bone Tool",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

#---------------------------------------------------------
#  Tool
#---------------------------------------------------------
import bpy
from bpy import *
from types import *
from rna_prop_ui import rna_idprop_ui_prop_get

#---------------------------------------------------------
#  Bone Data
#---------------------------------------------------------
face_bone = [["Ad-d-face_root",0.000,-0.037,0.019,0.000,-0.085,0.019,17,"****",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-t-nose.01",0.000,-0.107,0.030,0.000,-0.117,0.030,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-nose.02.L",0.013,-0.100,0.029,0.012,-0.112,0.029,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-nose.02.R",-0.013,-0.100,0.029,-0.012,-0.112,0.029,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-nose.03",0.000,-0.102,0.046,0.000,-0.112,0.046,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-nose.04",0.000,-0.090,0.059,0.000,-0.100,0.059,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-nose.05.L",0.009,-0.089,0.059,0.009,-0.102,0.059,16,"Ad-t-nose.04",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-nose.05.R",-0.009,-0.089,0.059,-0.009,-0.102,0.059,16,"Ad-t-nose.04",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-nose.06.L",0.009,-0.089,0.059,0.013,-0.100,0.029,17,"Ad-t-nose.04",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-nose.06.R",-0.009,-0.089,0.059,-0.013,-0.100,0.029,17,"Ad-t-nose.04",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-b-eye.L",0.028,-0.066,0.069,0.028,-0.092,0.069,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-b-eye.R",-0.028,-0.066,0.069,-0.028,-0.092,0.069,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-p-eye_vector",0.000,-0.066,0.069,0.000,-0.075,0.069,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-p-eyepoint",0.000,-0.161,0.072,0.000,-0.178,0.072,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-eyelid_low.L",0.028,-0.088,0.061,0.028,-0.092,0.061,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-eyelid_low.R",-0.028,-0.088,0.061,-0.028,-0.092,0.061,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-head.R",-0.057,-0.005,0.027,-0.057,-0.002,0.103,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-head.L",0.057,-0.005,0.027,0.057,-0.002,0.103,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.03.L",0.028,-0.066,0.069,0.028,-0.090,0.078,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyelid.03.L",0.028,-0.090,0.078,0.028,-0.091,0.078,17,"Ad-d-eye.03.L",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.03.R",-0.028,-0.066,0.069,-0.028,-0.090,0.078,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyelid.03.R",-0.028,-0.090,0.078,-0.028,-0.091,0.078,17,"Ad-d-eye.03.R",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.01.L",0.028,-0.066,0.069,0.028,-0.088,0.061,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.06.L",0.028,-0.088,0.061,0.038,-0.084,0.063,17,"Ad-d-eye.01.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.07.L",0.038,-0.084,0.063,0.043,-0.080,0.066,17,"Ad-d-eye.06.L",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.08.L",0.028,-0.088,0.061,0.020,-0.086,0.063,17,"Ad-d-eye.01.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.09.L",0.020,-0.086,0.063,0.014,-0.086,0.065,17,"Ad-d-eye.08.L",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.01.R",-0.028,-0.066,0.069,-0.028,-0.088,0.061,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.06.R",-0.028,-0.088,0.061,-0.038,-0.084,0.063,17,"Ad-d-eye.01.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,0.000,1.000],
["Ad-d-eye.07.R",-0.038,-0.084,0.063,-0.043,-0.080,0.066,17,"Ad-d-eye.06.R",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.08.R",-0.028,-0.088,0.061,-0.020,-0.086,0.063,17,"Ad-d-eye.01.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,0.000,1.000],
["Ad-d-eye.09.R",-0.020,-0.086,0.063,-0.014,-0.086,0.065,17,"Ad-d-eye.08.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.02.L",0.028,-0.066,0.069,0.028,-0.088,0.075,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.12.L",0.028,-0.088,0.075,0.020,-0.087,0.073,17,"Ad-d-eye.02.L",True,True,True,True,False,False,False,True,False,False,-0.349,0.349,-3.142,3.142,-3.142,3.142,1.000,True,2,0.000,1.000],
["Ad-d-eye.13.L",0.020,-0.087,0.073,0.014,-0.086,0.065,17,"Ad-d-eye.12.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],
["Ad-d-eye.10.L",0.028,-0.088,0.075,0.038,-0.086,0.073,17,"Ad-d-eye.02.L",True,True,True,True,False,False,False,True,False,False,-0.175,0.175,-3.142,3.142,-3.142,3.142,1.000,True,2,0.000,1.000],
["Ad-d-eye.11.L",0.038,-0.086,0.073,0.043,-0.080,0.066,17,"Ad-d-eye.10.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],
["Ad-d-eye.02.R",-0.028,-0.066,0.069,-0.028,-0.088,0.075,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.12.R",-0.028,-0.088,0.075,-0.020,-0.087,0.073,17,"Ad-d-eye.02.R",True,True,False,True,False,False,False,True,False,False,-0.349,0.349,-3.142,3.142,-3.142,3.142,1.000,True,2,0.000,1.000],
["Ad-d-eye.13.R",-0.020,-0.087,0.073,-0.014,-0.086,0.065,17,"Ad-d-eye.12.R",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],
["Ad-d-eye.10.R",-0.028,-0.088,0.075,-0.038,-0.086,0.073,17,"Ad-d-eye.02.R",True,True,False,True,False,False,False,True,False,False,-0.175,0.175,-3.142,3.142,-3.142,3.142,1.000,True,2,0.000,1.000],
["Ad-d-eye.11.R",-0.038,-0.086,0.073,-0.043,-0.080,0.066,17,"Ad-d-eye.10.R",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],
["Ad-t-eyelid.L",0.048,-0.072,0.069,0.048,-0.085,0.069,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.05.L",0.043,-0.080,0.066,0.045,-0.078,0.067,17,"Ad-t-eyelid.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-eyelid.R",-0.048,-0.072,0.069,-0.048,-0.085,0.069,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.05.R",-0.043,-0.080,0.066,-0.045,-0.078,0.067,17,"Ad-t-eyelid.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-eyeblow.01.L",0.012,-0.092,0.081,0.012,-0.104,0.081,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyeblow.01.R",-0.012,-0.092,0.081,-0.012,-0.104,0.081,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyeblow.02.L",0.031,-0.087,0.086,0.031,-0.100,0.086,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyeblow.02.R",-0.031,-0.087,0.086,-0.031,-0.100,0.086,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyeblow.03.L",0.052,-0.074,0.084,0.052,-0.087,0.084,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyeblow.03.R",-0.052,-0.074,0.084,-0.052,-0.087,0.084,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-forehead.03.L",0.043,-0.080,0.099,0.043,-0.092,0.099,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-forehead.03.R",-0.043,-0.080,0.099,-0.043,-0.092,0.099,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-forehead.02.L",0.023,-0.090,0.099,0.023,-0.102,0.099,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-forehead.02.R",-0.023,-0.090,0.099,-0.023,-0.102,0.099,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-forehead.04.L",0.059,-0.058,0.095,0.059,-0.070,0.095,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-forehead.04.R",-0.059,-0.058,0.095,-0.059,-0.070,0.095,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.04.L",0.014,-0.086,0.065,0.013,-0.086,0.064,17,"Ad-t-nose.04",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-eye.17.L",0.013,-0.086,0.064,0.020,-0.090,0.075,17,"Ad-d-eye.04.L",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.16.L",0.020,-0.090,0.075,0.028,-0.090,0.078,17,"Ad-d-eye.17.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.04.R",-0.014,-0.086,0.065,-0.013,-0.086,0.064,17,"Ad-t-nose.04",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-eye.17.R",-0.013,-0.086,0.064,-0.020,-0.090,0.075,17,"Ad-d-eye.04.R",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.16.R",-0.020,-0.090,0.075,-0.028,-0.090,0.078,17,"Ad-d-eye.17.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-p-forehaed.01",0.000,-0.088,0.083,0.000,-0.098,0.083,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-eyelid_up.L",0.028,-0.088,0.075,0.028,-0.093,0.075,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-eyelid_up.R",-0.028,-0.088,0.075,-0.028,-0.093,0.075,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-eye.15.L",0.045,-0.078,0.067,0.038,-0.087,0.076,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.14.L",0.038,-0.087,0.076,0.028,-0.090,0.078,17,"Ad-d-eye.15.L",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.15.R",-0.045,-0.078,0.067,-0.038,-0.087,0.076,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-eye.14.R",-0.038,-0.087,0.076,-0.028,-0.090,0.078,17,"Ad-d-eye.15.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],

["Ad-t-jaw",0.000,-0.091,-0.019,0.000,-0.100,-0.019,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-h-jaw_hinge",0.000,-0.017,0.029,0.000,-0.014,0.027,17,"Ad-d-face_root",False,True,True,True,False,True,True,True,False,False,0.000,0.785,-0.087,0.087,-0.087,0.087,0.000,True,1,1.000,1.000],

["Ad-d-jaw",0.000,-0.014,0.027,0.000,-0.091,-0.019,17,"Ad-h-jaw_hinge",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-jaw.01.L",0.042,-0.024,-0.002,0.010,-0.081,-0.021,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-jaw.02.L",0.056,-0.015,0.031,0.045,-0.024,-0.002,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-jaw.01.R",-0.042,-0.024,-0.002,-0.010,-0.081,-0.021,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-jaw.02.R",-0.056,-0.015,0.031,-0.045,-0.024,-0.002,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-p-tang.02",0.000,-0.060,0.000,0.000,-0.069,0.001,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,False,1,1.000,1.000],
["Ad-p-tang.01",0.000,-0.069,0.001,0.000,-0.080,0.001,17,"Ad-p-tang.02",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,False,1,1.000,1.000],

["Ad-t-tang",0.000,-0.080,0.001,0.000,-0.083,0.001,16,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-tang.02",0.000,-0.060,0.000,0.000,-0.069,0.001,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-tang.01",0.000,-0.069,0.001,0.000,-0.080,0.001,17,"Ad-d-tang.02",True,False,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],

["Ad-h-lip_guide",0.000,-0.085,0.019,0.000,-0.091,-0.019,17,"Ad-d-face_root",True,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],

["Ad-t-lip.01",0.000,-0.098,0.000,0.000,-0.107,0.000,16,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-lip.02.L",0.010,-0.094,0.002,0.010,-0.107,0.002,16,"Ad-d-jaw",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-lip.02.R",-0.010,-0.094,0.002,-0.010,-0.107,0.002,16,"Ad-d-jaw",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-lip.03.L",0.023,-0.089,0.007,0.023,-0.102,0.007,16,"Ad-h-lip_guide",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,2,1.000,1.000],
["Ad-t-lip.03.R",-0.023,-0.089,0.007,-0.023,-0.102,0.007,16,"Ad-h-lip_guide",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,2,1.000,1.000],
["Ad-t-lip.04.L",0.010,-0.099,0.012,0.010,-0.112,0.012,16,"Ad-d-face_root",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-lip.04.R",-0.010,-0.099,0.012,-0.010,-0.112,0.012,16,"Ad-d-face_root",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-lip.05",0.000,-0.103,0.012,0.000,-0.113,0.012,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-d-lip.00.L",0.000,-0.103,0.012,0.010,-0.099,0.012,17,"Ad-t-lip.05",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,2,1.000,1.000],
["Ad-d-lip.01.L",0.010,-0.099,0.012,0.023,-0.089,0.007,17,"Ad-d-lip.00.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],
["Ad-d-lip.02.L",-0.000,-0.098,0.000,0.010,-0.094,0.002,17,"Ad-t-lip.01",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,2,1.000,1.000],
["Ad-d-lip.03.L",0.010,-0.094,0.002,0.022,-0.089,0.007,17,"Ad-d-lip.02.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],

["Ad-d-lip.00.R",-0.000,-0.103,0.012,-0.010,-0.099,0.012,17,"Ad-t-lip.05",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,2,1.000,1.000],
["Ad-d-lip.01.R",-0.010,-0.099,0.012,-0.023,-0.089,0.007,17,"Ad-d-lip.00.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],
["Ad-d-lip.02.R",0.000,-0.098,0.000,-0.010,-0.094,0.002,17,"Ad-t-lip.01",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,2,1.000,1.000],
["Ad-d-lip.03.R",-0.010,-0.094,0.002,-0.022,-0.089,0.007,17,"Ad-d-lip.02.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,2,1.000,1.000],

["Ad-t-cheek.02.L",0.052,-0.062,0.049,0.052,-0.074,0.050,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-cheek.03.L",0.041,-0.072,0.011,0.041,-0.085,0.011,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-cheek.02.R",-0.052,-0.062,0.049,-0.052,-0.074,0.050,16,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-cheek.03.R",-0.041,-0.072,0.011,-0.041,-0.085,0.011,16,"Ad-h-lip_guide",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-d-cheek.02.L",0.028,-0.088,0.061,0.010,-0.099,0.012,17,"Ad-d-eye.01.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-cheek.02.R",-0.028,-0.088,0.061,-0.010,-0.099,0.012,17,"Ad-d-eye.01.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-cheek.06.L",0.029,-0.086,0.008,0.041,-0.072,0.011,17,"Ad-t-lip.03.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.06.R",-0.029,-0.086,0.008,-0.041,-0.072,0.011,17,"Ad-t-lip.03.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-t-cheek.01.L",0.020,-0.096,0.038,0.020,-0.100,0.038,17,"Ad-d-cheek.02.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-d-cheek.01.L",0.020,-0.096,0.038,0.028,-0.088,0.061,17,"Ad-t-cheek.01.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.03.L",0.029,-0.089,0.025,0.020,-0.096,0.038,17,"Ad-t-lip.03.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.04.L",0.029,-0.086,0.008,0.029,-0.089,0.025,17,"Ad-d-cheek.06.L",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.05.L",0.029,-0.089,0.025,0.053,-0.062,0.049,17,"Ad-t-lip.03.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.07.L",0.052,-0.062,0.049,0.042,-0.024,-0.002,17,"Ad-t-cheek.02.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.08.L",0.042,-0.024,-0.002,0.040,-0.072,0.011,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.09.L",0.029,-0.056,-0.009,0.022,-0.089,0.007,17,"Ad-d-jaw.01.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],

["Ad-t-cheek.01.R",-0.020,-0.096,0.038,-0.020,-0.100,0.038,17,"Ad-d-cheek.02.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],

["Ad-d-cheek.01.R",-0.020,-0.096,0.038,-0.028,-0.088,0.061,17,"Ad-t-cheek.01.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.03.R",-0.029,-0.089,0.025,-0.020,-0.096,0.038,17,"Ad-t-lip.03.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.04.R",-0.029,-0.086,0.008,-0.029,-0.089,0.025,17,"Ad-d-cheek.06.R",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.05.R",-0.029,-0.089,0.025,-0.053,-0.062,0.049,17,"Ad-t-lip.03.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.07.R",-0.052,-0.062,0.049,-0.042,-0.024,-0.002,17,"Ad-t-cheek.02.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.08.R",-0.042,-0.024,-0.002,-0.040,-0.072,0.011,17,"Ad-d-jaw",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-cheek.09.R",-0.029,-0.056,-0.009,-0.022,-0.089,0.007,17,"Ad-d-jaw.01.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],

["Ad-f-face.01",0.000,-0.087,0.026,0.000,-0.077,0.026,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-f-face.02",0.000,-0.093,0.039,0.000,-0.083,0.039,17,"Ad-d-face_root",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000]]

face_constraints=[["Ad-d-lip.00.L","Stretch To","STRETCH_TO","rig","Ad-t-lip.04.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-lip.01.L","Stretch To","STRETCH_TO","rig","Ad-t-lip.03.L",0.000,1.000,"NO_VOLUME","PLANE_X",1.000],
["Ad-d-lip.00.R","Stretch To","STRETCH_TO","rig","Ad-t-lip.04.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-lip.01.R","Stretch To","STRETCH_TO","rig","Ad-t-lip.03.R",0.000,1.000,"NO_VOLUME","PLANE_X",1.000],
["Ad-b-eye.L","Copy Rotation","COPY_ROTATION","rig","Ad-p-eye_vector",True,True,True,False,False,False,True,"LOCAL","LOCAL",1.000],
["Ad-b-eye.R","Copy Rotation","COPY_ROTATION","rig","Ad-p-eye_vector",True,True,True,False,False,False,True,"LOCAL","LOCAL",1.000],
["Ad-p-eye_vector","IK","IK","rig","Ad-p-eyepoint",1,1.000],
["Ad-p-eye_vector","Copy Rotation","COPY_ROTATION","rig","Ad-p-eyepoint",False,True,False,False,False,False,False,"LOCAL","LOCAL",1.000],
["Ad-d-eye.03.L","Copy Rotation","COPY_ROTATION","rig","Ad-d-eye.02.L",True,True,True,False,False,False,False,"LOCAL","LOCAL",0.200],
["Ad-d-eye.03.R","Copy Rotation","COPY_ROTATION","rig","Ad-d-eye.02.R",True,True,True,False,False,False,False,"LOCAL","LOCAL",0.200],
["Ad-d-eye.01.L","IK","IK","rig","Ad-t-eyelid_low.L",1,1.000],
["Ad-d-cheek.02.L","IK","IK","rig","Ad-t-lip.04.L",1,1.000],
["Ad-d-cheek.01.L","Floor","FLOOR","rig","Ad-f-face.02",False,True,000,"FLOOR_NEGATIVE_Y","WORLD","WORLD",1.000],
["Ad-d-cheek.01.L","Stretch To","STRETCH_TO","rig","Ad-d-eye.01.L",1.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-eye.07.L","IK","IK","rig","Ad-d-eye.05.L",2,1.000],
["Ad-d-eye.09.L","IK","IK","rig","Ad-d-eye.04.L",2,1.000],
["Ad-d-eye.01.R","IK","IK","rig","Ad-t-eyelid_low.R",1,1.000],
["Ad-d-cheek.02.R","IK","IK","rig","Ad-t-lip.04.R",1,1.000],
["Ad-d-cheek.01.R","Floor","FLOOR","rig","Ad-f-face.02",False,True,000,"FLOOR_NEGATIVE_Y","WORLD","WORLD",1.000],
["Ad-d-cheek.01.R","Stretch To","STRETCH_TO","rig","Ad-d-eye.01.R",1.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-eye.07.R","IK","IK","rig","Ad-d-eye.05.R",2,1.000],
["Ad-d-eye.09.R","IK","IK","rig","Ad-d-eye.04.R",2,1.000],
["Ad-d-eye.02.L","IK","IK","rig","Ad-t-eyelid_up.L",1,1.000],
["Ad-d-eye.13.L","IK","IK","rig","Ad-d-eye.04.L",2,1.000],
["Ad-d-eye.11.L","IK","IK","rig","Ad-d-eye.05.L",2,1.000],
["Ad-d-eye.02.R","IK","IK","rig","Ad-t-eyelid_up.R",1,1.000],
["Ad-d-eye.13.R","IK","IK","rig","Ad-d-eye.04.R",2,1.000],
["Ad-d-eye.11.R","IK","IK","rig","Ad-d-eye.05.R",2,1.000],
["Ad-d-eye.16.L","IK","IK","rig","Ad-t-eyelid.03.L",2,1.000],
["Ad-d-eye.16.R","IK","IK","rig","Ad-t-eyelid.03.R",2,1.000],
["Ad-d-nose.06.L","Stretch To","STRETCH_TO","rig","Ad-t-nose.02.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-nose.06.R","Stretch To","STRETCH_TO","rig","Ad-t-nose.02.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-eye.14.L","IK","IK","rig","Ad-t-eyelid.03.L",2,1.000],
["Ad-d-eye.14.R","IK","IK","rig","Ad-t-eyelid.03.R",2,1.000],
["Ad-d-jaw","IK","IK","rig","Ad-t-jaw",2,1.000],
["Ad-d-cheek.09.R","IK","IK","rig","Ad-t-lip.03.R",1,1.000],
["Ad-d-cheek.09.L","IK","IK","rig","Ad-t-lip.03.L",1,1.000],
["Ad-p-tang.01","IK","IK","rig","Ad-t-tang",2,1.000],
["Ad-d-tang.02","Stretch To","STRETCH_TO","rig","Ad-p-tang.01",0.000,1.000,"NO_VOLUME","PLANE_X",1.000],
["Ad-d-tang.01","Stretch To","STRETCH_TO","rig","Ad-t-tang",0.000,0.050,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.08.R","Stretch To","STRETCH_TO","rig","Ad-t-cheek.03.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.08.L","Stretch To","STRETCH_TO","rig","Ad-t-cheek.03.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-lip.02.R","Stretch To","STRETCH_TO","rig","Ad-t-lip.02.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-lip.03.R","Stretch To","STRETCH_TO","rig","Ad-t-lip.03.R",0.000,1.000,"NO_VOLUME","PLANE_X",1.000],
["Ad-d-lip.02.L","Stretch To","STRETCH_TO","rig","Ad-t-lip.02.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-lip.03.L","Stretch To","STRETCH_TO","rig","Ad-t-lip.03.L",0.000,1.000,"NO_VOLUME","PLANE_X",1.000],
["Ad-d-cheek.07.L","Stretch To","STRETCH_TO","rig","Ad-d-jaw.01.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.07.R","Stretch To","STRETCH_TO","rig","Ad-d-jaw.01.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-h-lip_guide","Stretch To","STRETCH_TO","rig","Ad-d-jaw",1.000,0.500,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.05.L","Floor","FLOOR","rig","Ad-f-face.01",False,True,0.000,"FLOOR_NEGATIVE_Y","WORLD","WORLD",1.000],
["Ad-d-cheek.05.L","Stretch To","STRETCH_TO","rig","Ad-t-cheek.02.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.06.L","Stretch To","STRETCH_TO","rig","Ad-t-cheek.03.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.04.L","Stretch To","STRETCH_TO","rig","Ad-d-cheek.05.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.03.L","Floor","FLOOR","rig","Ad-f-face.01",False,True,0.000,"FLOOR_NEGATIVE_Y","WORLD","WORLD",1.000],
["Ad-d-cheek.03.L","Stretch To","STRETCH_TO","rig","Ad-d-cheek.01.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.05.R","Floor","FLOOR","rig","Ad-f-face.01",False,True,0.000,"FLOOR_NEGATIVE_Y","WORLD","WORLD",1.000],
["Ad-d-cheek.05.R","Stretch To","STRETCH_TO","rig","Ad-t-cheek.02.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.06.R","Stretch To","STRETCH_TO","rig","Ad-t-cheek.03.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.04.R","Stretch To","STRETCH_TO","rig","Ad-d-cheek.05.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-cheek.03.R","Floor","FLOOR","rig","Ad-f-face.01",False,True,0.000,"FLOOR_NEGATIVE_Y","WORLD","WORLD",1.000],
["Ad-d-cheek.03.R","Stretch To","STRETCH_TO","rig","Ad-d-cheek.01.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000]]

body_bone=[["Ad-d-index.L",0.026,-0.008,-0.019,0.042,-0.012,-0.037,17,"ORG-palm.01.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-middle.L",0.026,-0.005,-0.019,0.042,-0.008,-0.038,17,"ORG-palm.02.L",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-ring.L",0.025,-0.001,-0.019,0.041,-0.002,-0.038,17,"ORG-palm.03.L",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-pinky.L",0.021,0.002,-0.014,0.035,0.003,-0.032,17,"ORG-palm.04.L",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-elbow.L",0.000,0.000,0.000,0.000,0.050,0.000,17,"DEF-forearm.L.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-tri.L",0.063,-0.010,-0.038,0.073,-0.010,-0.040,17,"DEF-upper_arm.L.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-serratus.L",0.072,0.072,-0.058,0.072,0.072,-0.044,17,"ORG-shoulder.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-index.R",-0.026,-0.008,-0.019,-0.042,-0.012,-0.037,17,"ORG-palm.01.R",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-middle.R",-0.026,-0.005,-0.019,-0.042,-0.008,-0.038,17,"ORG-palm.02.R",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-ring.R",-0.025,-0.001,-0.019,-0.041,-0.002,-0.038,17,"ORG-palm.03.R",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-pinky.R",-0.021,0.002,-0.014,-0.035,0.003,-0.032,17,"ORG-palm.04.R",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-elbow.R",0.000,0.000,0.000,0.000,0.050,0.000,17,"DEF-forearm.R.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-tri.R",-0.063,-0.010,-0.038,-0.073,-0.010,-0.040,17,"DEF-upper_arm.R.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-serratus.R",-0.072,0.072,-0.058,-0.072,0.072,-0.044,17,"ORG-shoulder.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-p-tri.02.L",0.049,0.010,0.003,0.082,0.052,-0.033,17,"shoulder.L",False,True,True,True,False,False,False,True,False,True,-0.524,3.142,-3.142,3.142,-0.087,0.087,0.600,False,2,1.000,1.000],
["Ad-p-tri.01.L",0.033,0.042,-0.036,0.116,0.055,-0.057,17,"Ad-p-tri.02.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,False,2,1.000,1.000],
["Ad-p-tri.02.R",-0.049,0.010,0.003,-0.082,0.052,-0.033,17,"shoulder.R",False,True,True,True,False,False,False,True,False,True,-0.524,3.142,-3.142,3.142,-0.087,0.087,0.600,False,2,1.000,1.000],
["Ad-p-tri.01.R",-0.033,0.042,-0.036,-0.116,0.055,-0.057,17,"Ad-p-tri.02.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.500,False,2,1.000,1.000],

["Ad-t-tri_up.L",0.050,0.011,0.000,0.060,0.011,0.000,17,"DEF-upper_arm.L.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-tri_up.R",-0.050,0.011,0.000,-0.060,0.011,0.000,17,"DEF-upper_arm.R.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-p-tri.04.L",0.100,0.080,0.000,0.100,0.080,0.030,17,"shoulder.L",False,True,True,True,False,False,False,True,False,True,-0.524,3.142,-3.142,3.142,-0.087,0.087,0.600,False,2,1.000,1.000],
["Ad-p-tri.04.R",-0.100,0.080,0.000,-0.100,0.080,0.030,17,"shoulder.R",False,True,True,True,False,False,False,True,False,True,-0.524,3.142,-3.142,3.142,-0.087,0.087,0.600,False,2,1.000,1.000],
["Ad-p-tri.03.L",0.000,0.000,0.000,0.116,0.000,0.057,17,"Ad-p-tri.04.L",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,3,1.000,1.000],
["Ad-p-tri.03.R",0.000,0.000,0.000,-0.116,0.000,0.057,17,"Ad-p-tri.04.R",True,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.500,True,3,1.000,1.000],

["Ad-t-scapula.L",0.061,0.025,0.091,0.061,0.025,0.180,17,"ORG-ribs",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-scapula.R",-0.061,0.025,0.091,-0.061,0.025,0.180,17,"ORG-ribs",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-sternum",-0.000,-0.094,0.047,-0.000,-0.049,0.211,17,"ORG-ribs",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-rib.01.L",0.085,0.089,-0.020,0.036,0.011,-0.017,17,"Ad-d-sternum",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-serratus.L",0.000,-0.000,0.000,0.001,0.023,0.123,17,"Ad-d-rib.01.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-rib.01.R",-0.085,0.089,-0.020,-0.034,0.012,-0.017,17,"Ad-d-sternum",False,True,False,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-serratus.R",-0.000,-0.000,0.000,-0.001,0.023,0.123,17,"Ad-d-rib.01.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,1.000,True,1,1.000,1.000],
["Ad-d-pectoralis.L",0.023,0.005,-0.004,0.096,0.092,0.128,17,"Ad-d-sternum",False,True,True,True,False,False,False,True,True,True,-0.087,0.087,-0.087,0.087,-0.087,0.087,0.500,True,1,1.000,1.000],
["Ad-d-udder.L",0.026,0.030,0.046,0.051,-0.026,0.062,17,"Ad-d-pectoralis.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-pectoralis.R",-0.023,0.005,-0.004,-0.096,0.092,0.128,17,"Ad-d-sternum",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-udder.R",-0.026,0.030,0.046,-0.051,-0.026,0.062,17,"Ad-d-pectoralis.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-r-belly",0.000,-0.013,0.125,0.000,-0.013,0.155,17,"ORG-spine",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-belly",-0.000,-0.086,0.014,-0.000,-0.106,0.014,17,"Ad-r-belly",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-knee.L",0.000,0.000,0.000,0.000,-0.079,-0.000,17,"ORG-shin.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-knee.R",0.000,-0.000,0.000,0.000,-0.079,0.000,17,"ORG-shin.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-pelvis.L.01",-0.058,-0.028,-0.006,0.033,-0.028,0.075,17,"MCH-thigh.L.socket1",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-pelvis.R.01",0.058,-0.028,-0.006,-0.033,-0.028,0.075,17,"MCH-thigh.R.socket1",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-groin",0.000,-0.052,-0.014,0.000,-0.091,-0.014,17,"ORG-hips",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-r-navel",0.000,-0.030,0.138,0.000,-0.030,0.200,17,"ORG-hips",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-navel",-0.000,-0.092,0.008,-0.000,-0.116,0.008,17,"Ad-r-navel",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-t-udder.L",0.051,-0.026,0.062,0.051,-0.046,0.062,17,"Ad-d-udder.L",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-t-udder.R",-0.051,-0.026,0.062,-0.051,-0.046,0.062,17,"Ad-d-udder.R",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-r-hips.L.01",0.000,0.000,0.000,0.000,0.000,-0.200,17,"MCH-thigh.L.socket1",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-r-hips.L.02",0.000,0.000,0.000,0.000,0.000,-0.100,17,"MCH-thigh.L.socket1",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-r-hips.R.01",0.000,0.000,0.000,0.000,0.000,-0.200,17,"MCH-thigh.R.socket1",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-r-hips.R.02",0.000,0.000,0.000,0.000,0.000,-0.100,17,"MCH-thigh.R.socket1",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,False,1,1.000,1.000],
["Ad-d-hips.L.01",0.000,0.050,0.000,0.000,0.070,0.000,17,"Ad-r-hips.L.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-hips.R.01",0.000,0.050,0.000,0.000,0.070,0.000,17,"Ad-r-hips.R.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-hips.L.02",0.000,0.070,0.000,-0.060,-0.070,-0.040,17,"Ad-d-hips.L.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-hips.R.02",0.000,0.070,0.000,0.060,-0.070,-0.040,17,"Ad-d-hips.R.01",False,True,True,True,False,False,False,False,False,False,-3.142,3.142,-3.142,3.142,-3.142,3.142,0.000,True,1,1.000,1.000],
["Ad-d-groin.L",0.007,-0.040,0.000,0.007,-0.040,0.015,17,"Ad-d-groin",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-groin.R",-0.007,-0.040,0.000,-0.007,-0.040,0.015,17,"Ad-d-groin",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-navel.L",0.030,0.020,-0.020,0.007,0.000,-0.070,17,"Ad-d-navel",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000],
["Ad-d-navel.R",-0.030,0.020,-0.020,-0.007,0.000,-0.070,17,"Ad-d-navel",False,True,True,True,False,False,False,False,False,False,-180.000,180.000,-180.000,180.000,-180.000,180.000,0.000,True,1,1.000,1.000]
]

body_constraints=[["Ad-d-index.L","Stretch To","STRETCH_TO","rig","ORG-finger_index.01.L",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-middle.L","Stretch To","STRETCH_TO","rig","ORG-finger_middle.01.L",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-ring.L","Stretch To","STRETCH_TO","rig","ORG-finger_ring.01.L",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-pinky.L","Stretch To","STRETCH_TO","rig","ORG-finger_pinky.01.L",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-index.R","Stretch To","STRETCH_TO","rig","ORG-finger_index.01.R",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-middle.R","Stretch To","STRETCH_TO","rig","ORG-finger_middle.01.R",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-ring.R","Stretch To","STRETCH_TO","rig","ORG-finger_ring.01.R",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-pinky.R","Stretch To","STRETCH_TO","rig","ORG-finger_pinky.01.R",0.500,10.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-elbow.L","Copy Rotation","COPY_ROTATION","rig","ORG-forearm.L",True,False,False,False,False,False,False,"LOCAL","LOCAL",0.500],
["Ad-d-elbow.R","Copy Rotation","COPY_ROTATION","rig","ORG-forearm.R",True,False,False,False,False,False,False,"LOCAL","LOCAL",0.500],
["Ad-p-tri.01.L","IK","IK","rig","Ad-t-tri.L",2,1.000],
["Ad-p-tri.01.R","IK","IK","rig","Ad-t-tri.R",2,1.000],
["Ad-p-tri.03.L","Stretch To","STRETCH_TO","rig","Ad-t-tri_up.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-p-tri.03.R","Stretch To","STRETCH_TO","rig","Ad-t-tri_up.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-t-scapula.L","Locked Track","LOCKED_TRACK","rig","DEF-upper_arm.L.02","TRACK_X","LOCK_Y",0.500],   
["Ad-t-scapula.R","Locked Track","LOCKED_TRACK","rig","DEF-upper_arm.R.02","TRACK_NEGATIVE_X","LOCK_Y",0.500],
["Ad-d-serratus.L","Stretch To","STRETCH_TO","rig","Ad-t-serratus.L",0.000,1.000,"NO_VOLUME","PLANE_X",0.500],
["Ad-d-serratus.R","Stretch To","STRETCH_TO","rig","Ad-t-serratus.R",0.000,1.000,"NO_VOLUME","PLANE_X",0.500],
["Ad-d-pectoralis.L","Stretch To","STRETCH_TO","rig","Ad-p-tri.01.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-pectoralis.R","Stretch To","STRETCH_TO","rig","Ad-p-tri.01.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-r-belly","Copy Rotation","COPY_ROTATION","rig","ORG-ribs",True,True,True,True,False,True,False,"LOCAL","LOCAL",0.700],
["Ad-d-knee.L","Copy Rotation","COPY_ROTATION","rig","ORG-shin.L",True,False,False,False,False,False,False,"LOCAL","LOCAL",0.500],
["Ad-d-knee.R","Copy Rotation","COPY_ROTATION","rig","ORG-shin.R",True,False,False,False,False,False,False,"LOCAL","LOCAL",0.500],
["Ad-r-navel","Copy Rotation","COPY_ROTATION","rig","ORG-spine",True,True,True,True,False,True,False,"LOCAL","LOCAL",0.500],
["Ad-r-hips.L.01","Copy Transforms","COPY_TRANSFORMS","rig","ORG-thigh.L",0,'WORLD','WORLD',0.500],
["Ad-r-hips.R.01","Copy Transforms","COPY_TRANSFORMS","rig","ORG-thigh.R",0,'WORLD','WORLD',0.500],
["Ad-r-hips.L.02","Copy Transforms","COPY_TRANSFORMS","rig","ORG-thigh.L",0,'WORLD','WORLD',0.300],
["Ad-r-hips.R.02","Copy Transforms","COPY_TRANSFORMS","rig","ORG-thigh.R",0,'WORLD','WORLD',0.300],
["Ad-d-navel.L","Stretch To","STRETCH_TO","rig","Ad-d-groin.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-navel.R","Stretch To","STRETCH_TO","rig","Ad-d-groin.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-hips.L.02","Stretch To","STRETCH_TO","rig","Ad-d-groin",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-hips.R.02","Stretch To","STRETCH_TO","rig","Ad-d-groin",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-udder.L","Stretch To","STRETCH_TO","rig","Ad-t-udder.L",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-udder.R","Stretch To","STRETCH_TO","rig","Ad-t-udder.R",0.000,1.000,"VOLUME_XZX","PLANE_X",1.000],
["Ad-d-groin.L","Floor","FLOOR","rig","Ad-d-groin",False,True,0.000,"FLOOR_Z","WORLD","WORLD",1.000],
["Ad-d-groin.R","Floor","FLOOR","rig","Ad-d-groin",False,True,0.000,"FLOOR_Z","WORLD","WORLD",1.000],
]

#---------------------------------------------------------
# Pre-set Lip Action
#---------------------------------------------------------
lipsync_actions = [['Ad-t-lip.05','pose.bones["Ad-t-lip.05"].location',0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.005118,-0.005118,-0.000000,0.000000],
['Ad-t-lip.05','pose.bones["Ad-t-lip.05"].location',1,0.000000,0.000000,-0.004558,0.002183,-0.004544,0.000000,0.000000,0.000000,0.001559,0.001559,-0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,-0.000231,-0.000231,-0.001215,0.000000],
['Ad-t-lip.05','pose.bones["Ad-t0-lip.05"].location',2,0.000000,0.000000,0.001677,0.000000,-0.001903,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.002756,0.000000,0.000000,0.000934,0.000934,0.002594,0.000000],
['Ad-t-lip.05','pose.bones["Ad-t-lip.05"].rotation_quaternion',0,0.714286,1.000000,0.978032,0.995255,0.993405,1.000000,0.714286,0.714286,0.710896,0.710896,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.709635,0.709635,0.697224,0.714286],
['Ad-t-lip.05','pose.bones["Ad-t-lip.05"].rotation_quaternion',1,0.000000,0.000000,-0.208454,0.097302,-0.114656,0.000000,0.000000,0.000000,0.069501,0.069501,-0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.062660,0.062660,0.155185,0.000000],
['Ad-t-lip.05','pose.bones["Ad-t-lip.05"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.004567,0.004567,-0.000000,0.000000],
['Ad-t-lip.05','pose.bones["Ad-t-lip.05"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.051720,0.051720,-0.000000,0.000000],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].location',0,-0.001489,0.000000,-0.010485,0.001278,-0.009554,0.002197,-0.001489,-0.001489,0.000913,0.000913,-0.000000,-0.000000,-0.000000,-0.001489,0.000000,-0.002368,-0.002525,0.006579,-0.001696,0.002208,0.000000],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].location',1,-0.000000,0.000000,-0.013299,0.000000,-0.008292,0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,-0.001535,0.000000,0.001160,-0.001086,0.000000,0.000000],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].location',2,-0.001515,0.000000,0.001452,0.000000,-0.001194,0.000000,-0.001515,-0.001515,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001515,0.002756,0.000000,-0.001576,-0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.712396,0.712396,0.714286,0.714286],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.04.L','pose.bones["Ad-t-lip.04.L"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.051921,0.051921,-0.000000,0.000000],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].location',0,0.001489,0.000000,0.010485,-0.001278,0.009554,-0.002197,0.001489,0.001489,-0.000913,-0.000913,0.000000,0.000000,0.000000,0.001489,0.000000,0.002368,0.002525,0.001696,-0.006579,-0.002208,0.000000],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].location',1,-0.000000,0.000000,-0.013299,0.000000,-0.008292,0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,-0.001535,0.000000,-0.001086,0.001160,0.000000,0.000000],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].location',2,-0.001515,0.000000,0.001452,0.000000,-0.001194,0.000000,-0.001515,-0.001515,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001515,0.002756,0.000000,-0.001576,-0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.712396,0.712396,0.714286,0.714286],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.04.R','pose.bones["Ad-t-lip.04.R"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,-0.051921,0.051921,0.000000,0.000000],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].location',0,-0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000653,-0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].location',1,0.001228,0.000000,0.000000,0.000000,0.000000,-0.001268,0.001228,0.001228,0.000000,0.000000,0.000000,0.000000,-0.001849,0.001228,0.000000,0.000000,0.000000,-0.000000,-0.000000,-0.000000,0.000000],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].location',2,0.002736,-0.025808,0.000000,-0.001329,-0.009944,-0.021375,0.002736,0.002736,-0.000950,-0.000950,-0.008564,-0.008564,-0.002285,0.002736,0.000000,0.000000,0.000000,0.003582,0.003582,0.003582,0.000000],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-jaw','pose.bones["Ad-t-jaw"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].location',0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].location',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].location',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.01','pose.bones["Ad-t-nose.01"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].location',0,0.000000,0.000000,-0.001304,0.000000,-0.001934,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.002063,-0.000000,0.000000,0.000000],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].location',1,0.000000,0.000000,-0.002165,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].location',2,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001775,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001738,0.000000,0.000000,0.000000],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.02.L','pose.bones["Ad-t-nose.02.L"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].location',0,0.000000,0.000000,0.001304,0.000000,0.001934,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.002063,0.000000,0.000000],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].location',1,0.000000,0.000000,-0.002165,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].location',2,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001775,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001738,0.000000,0.000000],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000],
['Ad-t-nose.02.R','pose.bones["Ad-t-nose.02.R"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].location',0,0.000000,0.000000,-0.008868,0.001711,-0.008250,0.002197,0.000000,0.000000,0.001222,0.001222,-0.000000,-0.000000,-0.000000,0.000000,0.000000,-0.002368,-0.000000,0.006790,0.000132,0.002208,0.000000],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].location',1,0.000000,0.000000,-0.010939,0.000000,-0.005486,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.001535,0.000000,0.001075,-0.000872,0.000000,0.000000],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].location',2,0.000000,0.000000,-0.002992,0.002130,0.000000,0.000000,0.000000,0.000000,0.001521,0.001521,0.000000,0.000000,0.000000,0.000000,0.002756,0.000000,-0.001576,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.712396,0.712396,0.714286,0.714286],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.02.L','pose.bones["Ad-t-lip.02.L"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.051921,0.051921,-0.000000,0.000000],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].location',0,0.000000,0.000000,0.008868,-0.001711,0.008250,-0.002197,0.000000,0.000000,-0.001222,-0.001222,0.000000,0.000000,0.000000,0.000000,0.000000,0.002368,-0.000000,-0.000132,-0.006790,-0.002208,0.000000],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].location',1,0.000000,0.000000,-0.010939,0.000000,-0.005486,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.001535,-0.000000,-0.000872,0.001075,0.000000,0.000000],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].location',2,0.000000,0.000000,-0.002992,0.002130,0.000000,0.000000,0.000000,0.000000,0.001521,0.001521,0.000000,0.000000,0.000000,0.000000,0.002756,0.000000,-0.001576,0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.712396,0.712396,0.714286,0.714286],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.02.R','pose.bones["Ad-t-lip.02.R"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,-0.051921,0.051921,0.000000,0.000000],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].location',0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.004399,-0.004399,0.000000,0.000000],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].location',1,-0.000000,0.000000,-0.002993,0.000000,-0.003717,0.000000,-0.000000,-0.000000,0.000000,0.000000,-0.000000,-0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,-0.000084,-0.000084,0.000402,0.000000],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].location',2,0.001637,0.000000,0.000000,0.000000,0.000000,0.000000,0.001637,0.001637,0.000000,0.000000,0.000000,0.000000,0.000000,0.001637,0.002756,0.000000,0.000000,-0.000221,-0.000221,0.001139,0.000000],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].rotation_quaternion',0,0.714286,1.000000,0.959183,0.979126,0.991832,1.000000,0.714286,0.714286,0.699376,0.699376,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.703638,0.703638,0.704025,0.714286],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].rotation_quaternion',1,0.000000,0.000000,0.282786,-0.203253,0.127555,0.000000,0.000000,0.000000,-0.145180,-0.145180,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.111365,-0.111365,-0.120635,0.000000],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.008117,-0.008117,0.000000,0.000000],
['Ad-t-lip.01','pose.bones["Ad-t-lip.01"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.051283,0.051283,0.000000,0.000000],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].location',0,0.000000,0.000000,-0.003118,0.002029,-0.003070,0.000000,0.000000,0.000000,0.001449,0.001449,-0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.006116,0.002577,0.000927,0.000000],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].location',1,0.000000,0.000000,-0.005654,-0.003174,-0.004271,-0.004671,0.000000,0.000000,-0.002267,-0.002267,-0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000516,0.007355,0.000000],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].location',2,0.000000,0.000000,0.000000,0.000000,0.000000,-0.006942,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.004816,-0.001919,0.000000],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-cheek.03.L','pose.bones["Ad-t-cheek.03.L"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].location',0,0.001034,0.000000,-0.002878,0.005327,-0.004647,0.005769,0.001034,0.001034,0.003805,0.003805,0.001775,0.001775,0.001775,0.001034,0.000000,0.000192,-0.000000,0.011889,0.006656,0.007988,0.000000],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].location',1,0.000045,0.000000,-0.010807,0.000000,-0.009385,0.000000,0.000045,0.000045,0.000000,0.000000,-0.000000,-0.000000,-0.000000,0.000045,0.000000,-0.002303,-0.000000,0.005491,-0.001894,0.000067,0.000000],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].location',2,-0.004292,-0.002755,-0.001281,-0.001067,0.000000,-0.003506,-0.004292,-0.004292,-0.000762,-0.000762,-0.001968,-0.001968,-0.001968,-0.004292,0.002756,0.002071,-0.005662,-0.000029,0.000000,-0.003551,0.000000],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.712396,0.714286,0.714286],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.03.L','pose.bones["Ad-t-lip.03.L"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.051921,-0.000000,0.000000],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].location',0,0.000000,0.000000,0.003118,-0.002029,0.003070,0.000000,0.000000,0.000000,-0.001449,-0.001449,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.002577,-0.006116,-0.000927,0.000000],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].location',1,0.000000,0.000000,-0.005654,-0.003174,-0.004271,-0.004671,0.000000,0.000000,-0.002267,-0.002267,-0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,-0.000516,-0.000000,0.007355,0.000000],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].location',2,0.000000,0.000000,0.000000,0.000000,0.000000,-0.006942,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.004816,-0.000000,-0.001919,0.000000],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000],
['Ad-t-cheek.03.R','pose.bones["Ad-t-cheek.03.R"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].location',0,-0.001034,0.000000,0.002878,-0.005327,0.004647,-0.005769,-0.001034,-0.001034,-0.003805,-0.003805,-0.001775,-0.001775,-0.001775,-0.001034,0.000000,0.000192,-0.000000,-0.006656,-0.011889,-0.007988,0.000000],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].location',1,0.000045,0.000000,-0.010807,0.000000,-0.009385,0.000000,0.000045,0.000045,0.000000,0.000000,-0.000000,-0.000000,-0.000000,0.000045,0.000000,-0.002303,-0.000000,-0.001894,0.005491,0.000067,0.000000],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].location',2,-0.004292,-0.002755,-0.001281,-0.001067,0.000000,-0.003506,-0.004292,-0.004292,-0.000762,-0.000762,-0.001968,-0.001968,-0.001968,-0.004292,0.002756,0.002071,-0.005662,0.000000,-0.000029,-0.003551,0.000000],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,1.000000,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.712396,0.714286,0.714286,0.714286],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,0.000000,0.000000,0.000000],
['Ad-t-lip.03.R','pose.bones["Ad-t-lip.03.R"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,-0.051921,0.000000,0.000000,0.000000],
['Ad-t-tang','pose.bones["Ad-t-tang"].location',0,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-tang','pose.bones["Ad-t-tang"].location',1,0.000000,0.000000,0.000000,0.000000,0.002514,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-tang','pose.bones["Ad-t-tang"].location',2,0.000000,0.000000,0.000000,0.000000,0.001696,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.002756,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-tang','pose.bones["Ad-t-tang"].rotation_quaternion',0,0.714286,1.000000,1.000000,1.000000,0.981300,1.000000,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286,0.714286],
['Ad-t-tang','pose.bones["Ad-t-tang"].rotation_quaternion',1,0.000000,0.000000,0.000000,0.000000,-0.192483,0.000000,0.000000,0.000000,-0.000000,-0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-tang','pose.bones["Ad-t-tang"].rotation_quaternion',2,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000],
['Ad-t-tang','pose.bones["Ad-t-tang"].rotation_quaternion',3,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000]]

lipsync_prop = [['Lip_01_',1,''],['Lip_02_a',2,'a'],['Lip_03_i',3,'i'],['Lip_04_M',4,'M'],['Lip_05_e',5,'e'],['Lip_06_o',6,'o'],['Lip_07_N',7,'N'],['Lip_08_n',8,'n'],['Lip_09_br1',9,'br1'],['Lip_10_br2',10,'br2'],['Lip_11_br3',11,'br3'],['Lip_12_br4',12,'br4'],['Lip_13_br5',13,'br5'],
['Lip_91',91,'*'],['Lip_92',92,'*'],['Lip_93',93,'*'],['Lip_94',94,'*'],['Lip_95',95,'*'],['Lip_96',96,'*'],['Lip_97',97,'*'],['Lip_98',98,'*'],['Lip_99',99,'*']]

#---------------------------------------------------------
# Custom bones
#   Add custom bones,and rest(without positions)
#---------------------------------------------------------
def create_bones(rig,bones,constraints):
    eb = rig.data.edit_bones
    pb = rig.pose.bones
    
    # Root
    if bones[0][8]=='****':
        face_editting = True
        pw = rig.data.bones.get('ORG-head')
        if pw==None:
            p0 = 'head'
        else:
            p0 = 'ORG-head'
        scale = rig.data.bones[p0].length / 0.15
    else:
        face_editting = False
        p0 = 'root'
        scale = 1.0

    # Bone Edit
    for d in bones:
        
        bpy.ops.object.mode_set(mode='EDIT')

        b = eb.get(d[0])
        if b==None:
            
            if face_editting:
                p1 = eb[p0]
            else:
                # Body Bones' scale adjust
                p1 = eb[d[8]]
                if d[8]=='ORG-ribs':
                    scale = rig.data.bones[d[8]].length/0.25
                elif d[8]=='ORG-hips':
                    scale = rig.data.bones[d[8]].length/0.15
                elif d[8]=='ORG-spine':
                    scale = rig.data.bones[d[8]].length/0.10
                elif d[8]=='ORG-shoulder.L':
                    scale = rig.data.bones[d[8]].length/0.12
                elif d[8]=='ORG-shoulder.R':
                    scale = rig.data.bones[d[8]].length/0.12
                elif d[8]=='Ad-d-sternum':
                    scale = rig.data.bones[d[8]].length/0.16
                elif d[8]=='Ad-r-belly':
                    scale = rig.data.bones[d[8]].length/0.032
                elif d[8]=='Ad-r-navel':
                    scale = rig.data.bones[d[8]].length/0.05
                else:
                    scale = 1.0
            # Only when there is not the bone,set the points.
            b = eb.new(d[0])

            b.head.x = p1.head.x + d[1] * scale
            b.head.y = p1.head.y + d[2] * scale
            b.head.z = p1.head.z + d[3] * scale
            b.tail.x = p1.head.x + d[4] * scale
            b.tail.y = p1.head.y + d[5] * scale
            b.tail.z = p1.head.z + d[6] * scale
            if d[0]=='Ad-d-elbow.L':
                b.roll = -1.13446
            elif d[0]=='Ad-d-elbow.R':
                b.roll = 1.13446
            else:
                b.roll = 0                
            b.use_connect = d[9]
            if d[8]=='****':
                b.parent = eb[p0]
            elif d[0]=='Ad-d-groin.L':
                b.parent = eb['Ad-r-hips.L.02']
            elif d[0]=='Ad-d-groin.R':
                b.parent = eb['Ad-r-hips.R.02']
            elif d[0]=='Ad-t-udder.L':
                b.parent = eb['Ad-d-pectoralis.L']
            elif d[0]=='Ad-t-udder.R':
                b.parent = eb['Ad-d-pectoralis.R']
            else:
                b.parent = eb[d[8]]
            b.layers = [n==d[7] for n in range(0,32)]
            b.use_inherit_rotation = d[10]
            b.use_inherit_scale = d[11]
            b.use_local_location = d[12]
            b.use_deform = d[26]
            b.bbone_segments = d[27]
            b.bbone_in = d[28]
            b.bbone_out = d[29]

            bpy.ops.object.mode_set(mode='OBJECT')

            p = pb[d[0]]
            p.lock_ik_x = d[13]
            p.lock_ik_y = d[14]
            p.lock_ik_z = d[15]
            p.use_ik_limit_x = d[16]
            p.use_ik_limit_y = d[17]
            p.use_ik_limit_z = d[18]
            p.ik_min_x = d[19]
            p.ik_max_x = d[20]
            p.ik_min_y = d[21]
            p.ik_max_y = d[22]
            p.ik_min_z = d[23]
            p.ik_max_z = d[24]
            p.ik_stretch = d[25]                   

    # Reset RestLength
    bpy.ops.object.mode_set(mode='EDIT')

    for c in constraints:
        if c[2] == 'STRETCH_TO':
            t_bone = eb[c[4]]
            eb[c[0]].tail = t_bone.head * (1-c[5]) + t_bone.tail * c[5]
        elif c[2] == 'IK' and pb[c[0]].ik_stretch > 0:
            eb[c[0]].tail = eb[c[4]].head
            
    bpy.ops.object.mode_set(mode='OBJECT')
    pose_mode = context.object.data.pose_position
    context.object.data.pose_position = 'REST'
    # Constraints
    for c in constraints:
        b = pb.get(c[0])
        if b == None:
            pass
        else:
            cn = b.constraints.get(c[1])
            if cn == None:
                cn = b.constraints.new(c[2])
                cn.name = c[1]
            # Even when there is the constraint,reset params.
            cn.target = rig
            cn.subtarget = c[4]
            if c[2]=='STRETCH_TO':
                cn.head_tail = c[5]
                cn.rest_length = rig.data.bones[c[0]].length
                cn.bulge = c[6]
                cn.volume = c[7]
                cn.keep_axis = c[8]
                cn.influence = c[9]
            elif c[2]=='COPY_ROTATION':
                cn.use_x = c[5]
                cn.use_y = c[6]
                cn.use_z = c[7]
                cn.invert_x = c[8]            
                cn.invert_y = c[9]            
                cn.invert_z = c[10]            
                cn.use_offset = c[11] 
                cn.target_space = c[12]
                cn.owner_space = c[13]
                cn.influence = c[14]
            elif c[2]=='FLOOR':
                cn.use_sticky = c[5]
                cn.use_rotation = c[6]
                cn.offset = c[7]
                cn.floor_location = c[8]
                cn.target_space = c[9]
                cn.owner_space = c[10]
                cn.influence = c[11]
            elif c[2]=='IK':
                cn.chain_count = c[5]
                cn.use_tail = True
                cn.use_stretch = True
                cn.use_target = True
                cn.use_rotation = False
                cn.influence = c[6]
            elif c[2]=='LOCKED_TRACK':
                cn.track_axis = c[5]
                cn.lock_axis = c[6]
                cn.influence = c[7]
            elif c[2]=='COPY_TRANSFORMS':
                cn.head_tail = c[5]
                cn.target_space = c[6]
                cn.owner_space = c[7]
                cn.influence = c[8]
    context.object.data.pose_position = pose_mode
    return (0)

#-------------------------------------------------------         
# Preset LipSync Action
#-------------------------------------------------------         
def action_set(obj):
    
    bb = obj.data.bones.get('ORG-head')
    if bb==None:
        bb = obj.data.bones.get('head')
    if bb==None:
        return (-1)
    else:
        scale = bb.length / 0.15
        
    #Properties
    prop = obj.get('LipSync')
    if prop==None:
        prop = rna_idprop_ui_prop_get(obj, 'LipSync', create=True)
        prop['min'] = 0.000
        prop['max'] = 1.000
    obj['LipSync'] = 1.000
    
    for p in lipsync_prop:
        prop = obj.get(p[0])
        if prop==None:
            prop = rna_idprop_ui_prop_get(obj, p[0], create=True)
            prop['min'] = 0.000
            prop['max'] = 1.000
        obj[p[0]] = 0.000

    # Action
    action_name = 'Lip_' + obj.name
    syn_action = bpy.data.actions.get(action_name)
    if syn_action==None:
        syn_action = bpy.data.actions.new(action_name)
        for k in lipsync_actions:
            grp = syn_action.groups.get(k[0])
            if grp==None:
                grp = syn_action.groups.new(k[0])
            f = syn_action.fcurves.new(k[1],k[2],k[0])
            f.color_mode = 'AUTO_RGB'
            for i in range(len(k)-3):   
                j = i + 3
                p = f.keyframe_points.insert(lipsync_prop[i][1],k[j] * scale)
    syn_action.use_fake_user = True
    prop = obj.get('Lip_Motion')
    if prop==None:
        prop = rna_idprop_ui_prop_get(obj, 'Lip_Motion', create=True)
    obj['Lip_Motion'] = syn_action.name

    for grp in syn_action.groups:
        b = obj.pose.bones.get(grp.name)
        if b==None:
            pass
        else:
            for prop in lipsync_prop:
                # Action-Constraint
                c = create_action_constraint(obj,b,prop,syn_action)
                # Driver
                df = c.driver_add('influence')
                create_lip_driver(df,obj,prop[0],'LipSync')

    #Face Action (Add@0.4)
    prop = obj.get('FaceScale')
    if prop==None:
        prop = rna_idprop_ui_prop_get(obj, 'FaceScale', create=True)
        prop['min'] = 0.000
        prop['max'] = 1.000
    obj['FaceScale'] = 1.000
    for f in range(101,121,1):
        tag = 'Face_%(f)03d'%{'f':f}
        for d in face_bone:
            if d[0].find('lip')>=0 or d[0].find('face')>=0:
                pass
            elif d[7]==16:
                prop = obj.get(tag)
                if prop==None:
                    prop = rna_idprop_ui_prop_get(obj,tag, create=True)
                    prop['min'] = 0.000
                    prop['max'] = 1.000
                obj[tag] = 0.000
                b = obj.pose.bones.get(d[0])
                if b==None:
                    pass
                else:
                    # Action-Constraint
                    c = create_action_constraint(obj,b,[tag,f],syn_action)
                    # Driver
                    df = c.driver_add('influence')
                    create_lip_driver(df,obj,tag,'FaceScale')
                    
    return (0)

# LipSync Action-Constraint
def create_action_constraint(obj,bone,prop,syn_action):
    c = bone.constraints.get(prop[0])
    if c==None:
        c = bone.constraints.new('ACTION')
        c.name = prop[0]
    c.target = obj
    c.subtarget = 'Ad-d-face_root'
    c.action = syn_action
    c.min = 0
    c.max = 1
    c.frame_start = prop[1]
    c.frame_end = prop[1]
    c.target_space = 'LOCAL'
    c.influence = 0
    return(c)

# LipSync Driver set
def create_lip_driver(drv,obj,path,scale):
    dd = drv.driver
    dd.type = 'SCRIPTED'
    dd.expression = 'scale * influence'
    v0 = dd.variables.get('scale')
    if v0==None:
        v0 = dd.variables.new()
        v0.name = 'scale'
        v0.targets[0].id_type = 'OBJECT'
        v0.targets[0].id = obj
        v0.targets[0].data_path = '["' + scale + '"]'
    v1 = dd.variables.get('influence')
    if v1==None:
        v1 = dd.variables.new()
        v1.name = 'influence'
        v1.targets[0].id_type = 'OBJECT'
        v1.targets[0].id = obj
        v1.targets[0].data_path = '["' + path + '"]'                

#-------------------------------------------------------         
# Replace Driver
#-------------------------------------------------------         
def replace_driver(obj):
    obj_name = obj.name.rpartition('.')
    
    try:
        for d in obj.data.shape_keys.animation_data.drivers:
            for v in d.driver.variables:
                for t in v.targets:
                    # Only when same preserfix name and object type
                    if t.id.name.startswith(obj_name[0]) and t.id.type == obj.type:
                        t.id = obj
    except:
        pass
    try:
        for d in obj.animation_data.drivers:
            for v in d.driver.variables:
                for t in v.targets:
                    # Only when same preserfix name and object type
                    if t.id.name.startswith(obj_name[0]) and t.id.type == obj.type:
                        t.id = obj
    except:
        pass
    
#-----------------------------------------------------------------------
# LipSync Tool
#-----------------------------------------------------------------------
# VSQ Record
class MThd:
    format = 0
    tracks = 0
    division = 0

class MTrk:
    text = ''
    tempo = 0
    size = 0
    timesigneture = [0,0,0,0]
    common = None
    master = None
    mixer = None
    eventlist = None
    pitchbendbplist = None
    pitchbendsensbplist = None

    def __init__(self):
        self.common = []
        self.master = []
        self.mixer = []
        self.eventlist = []
        self.pitchbendbplist = []
        self.pitchbendsensbplist = []

class Common:
    version = ''
    name = ''
    color = [0,0,0]
    dynamicsmode = 0
    playmode = 0

class Master:
    premesure = 0

class Mixer:
    masterfeder = 0
    masterpanpot = 0
    mastermute = 0
    mastersolo = 0
    outputmode = 0
    tracks = 0
    track = None

    def __init__(self):
        self.track = []

class mixer_track:
    feder = 0
    panpot = 0
    mute = 0
    solo = 0

class EventList:
    start = 0
    id = ''
    rec = None

class Singer:
    type = 'Singer'
    iconhandle = None

class Anote:
    type = 'Anote'
    length = 0
    note = 0
    dynamics = 0
    pmbenddepth = 0
    pmbendlength = 0
    pmbportamentouse = 0
    demdecgainrate = 0
    demaccent = 0
    lyrichandle = None
    vibratohandle = None
    vibratodelay = 0

class Voice:
    id = ''
    type = 'Voice'
    char = ''
    sign0 = ''
    sign = ''
    params = ''

class Icon:
    id = ''
    type = 'Icon'
    iconid = ''
    ids = ''
    original = 0
    caption = ''
    length = 0
    startdepth = 64
    depthbpnum = 0
    depthbpx = []
    depthbpy = []
    startrate = 50
    ratebpnum = 0

class VSQ_Data:
    mthd = None
    mtrk = None
    filepath = ''
    text = []

    __rec = []

    def __init__(self):
        self.filepath = ''
        self.mthd = MThd
        self.mtrk = []

    def __remove_sep(self,rec):
        r = ''
        r0 = rec
        r1 = rec
        for t in rec:
           r += chr(t)

        if r.find('DM:')>=0:
            s = -1 # 0xff
            t = -1 # DM:
            u = -1 # :
            for i in range(len(r0)):
                if t < 0 and r0[i]==0x00:
                    s = i
                elif s >=0 and t <0 and chr(r0[i])==':':
                    if chr(r0[i-2]) + chr(r0[i-1])=='DM':
                        t = i
                elif s>=0 and t>=0 and chr(r0[i])==':':
                    w = chr(r0[i-4]) + chr(r0[i-3]) + chr(r0[i-2]) + chr(r0[i-1])
                    if w.isdigit():
                        u = i
            if s >=0 and t >=0 and u>=0:
                r1 = []
                for i in range(len(r0)):
                    if i < s or i > u:
                        r1.append(r0[i])
            else:
                r1 = r0

        return(r1)
    
    def __readfile(self):                 
        r0 = []
        r1 = []
        cnt = 0
        vsqfile = open(self.filepath,'rb')
        for b in vsqfile.read():
            if b==0x0a:
                r1.append(self.__remove_sep(r0))
                r0 = []
                cnt += 1
            else:
                r0.append(b)
        r1.append(self.__remove_sep(r0))
        vsqfile.close()

        return(r1)

    def __read_text(self,rec):
        r = rec
        tex = ''
        if chr(r[0])=='[' or chr(r[0]).isdigit() or chr(r[0])=='[':
            for t in r:
               tex += chr(t)
        else:
            # MTrk
            for i in range(len(r)-8):
                tex += chr(r[i])
                if (r[i],r[i+1],r[i+2],r[i+3])==(0x4d,0x54,0x72,0x6b):
                    __mtrk = MTrk()
                    self.mtrk.append(__mtrk)
                    j = i + 4
                    l = r[j]*256**3 + r[j+1]*256**2 + r[j+2]*256 + r[j+3]
                    __mtrk.size = l
                    s = j + 4
                    t = s + l
                    m = r[s:t]
                    for j in range(len(m)-4):
                        if (m[j],m[j+1])==(0xff,0x03):
                            l = m[j+2]
                            t = ''
                            for k in range(l):
                                t += chr(m[j+3+k])
                            __mtrk.text = t
                        elif (m[j],m[j+1],m[j+2])==(0xff,0x51,0x03):
                            __mtrk.tempo = m[j+3]*256**2 + m[j+4]*256 + m[j+5]
                        elif (m[j],m[j+1],m[j+2])==(0xff,0x58,0x04):
                            __mtrk.timesigneture = [m[j+3],m[j+4],m[j+5],m[j+6]]
            for i in range(8):
                j = i + len(r) - 8
                tex += chr(r[j])

        return(tex)

    def __make_text(self,rec):
        # MThd
        self.mthd.format = rec[0][9]
        self.mthd.tracks = rec[0][10]*256 + rec[0][11]
        self.mthd.division = rec[0][12]*256 + rec[0][13]

        __section = ''
        for r in rec:
            t = self.__read_text(r)
            n = len(self.mtrk)
            if n > 0:
                __mtrk = self.mtrk[n-1]
                if t[0:1]=='[':
                    __section = t
                elif t.endswith(']'):
                    i = t.rfind('[')
                    __section = t[i:len(t)]

                # Append Records
                if __section=='[Common]':
                    if len(__mtrk.common)==0:
                        s = Common()
                        __mtrk.common.append(s)
                elif __section=='[Master]':
                    if len(__mtrk.master)==0:
                        s = Master()
                        __mtrk.master.append(s)
                elif __section=='[Mixer]':
                    if len(__mtrk.mixer)==0:
                        s = Mixer()
                        __mtrk.mixer.append(s)

                # Edit Records
                if __section=='[Common]':
                    l = t.partition('=')
                    if l[0]=='Version': __mtrk.common[0].version = l[2]
                    elif l[0]=='Name': __mtrk.common[0].name = l[2]
                    elif l[0]=='Color':
                        c = l[2].split(',')
                        __mtrk.common[0].color = [int(c[0]),int(c[1]),int(c[2])]
                    elif l[0]=='DynamicsMode': __mtrk.common[0].dynamicsmode = int(l[2])
                    elif l[0]=='PlayMode': __mtrk.common[0].playmode = int(l[2])
                elif __section=='[Master]':
                    l = t.partition('=')
                    if l[0]=='PreMeasure': __mtrk.master[0].premesure = int(l[2])
                elif __section=='[Mixer]':
                    l = t.partition('=')
                    if l[0]=='MasterFeder': __mtrk.mixer[0].masterfeder = int(l[2])
                    elif l[0]=='MasterPanpot': __mtrk.mixer[0].masterpanpot = int(l[2])
                    elif l[0]=='MasterMute': __mtrk.mixer[0].mastermute = int(l[2])
                    elif l[0]=='OutputMode': __mtrk.mixer[0].outputmode = int(l[2])
                    elif l[0]=='Tracks':
                        __mtrk.mixer[0].tracks = int(l[2])
                        for i in range(int(l[2])):
                            trk = mixer_track()
                            __mtrk.mixer[0].track.append(trk)
                    elif l[1]=='=':
                        k = len(l[0])
                        n = l[0][k-1:k]
                        if n.isdigit():
                            i = int(n)
                            trk = __mtrk.mixer[0].track[i]
                            if l[0].find('Feder')>=0 : trk.feder = int(l[2])
                            elif l[0].find('Panpot')>=0 : trk.panpot = int(l[2])
                            elif l[0].find('Mute')>=0 : trk.mute = int(l[2])
                            elif l[0].find('Solo')>=0 : trk.solo = int(l[2])
                elif __section=='[EventList]':
                    l = t.partition('=')
                    if l[0].isdigit() and (l[2].startswith('ID#') or l[2]=='EOS'):
                        s = EventList()
                        s.start = int(l[0])
                        s.id = l[2]
                        __mtrk.eventlist.append(s)
                elif __section.startswith('[ID#'):
                    for e in __mtrk.eventlist:
                        if '[' + e.id + ']'==__section:
                            l = t.partition('=')
                            if l[0]=='Type':
                                if l[2]=='Anote':
                                    e0 = Anote()
                                elif l[2]=='Singer':
                                    e0 = Singer()
                                e.rec = e0
                            elif l[0]=='Length':e.rec.length = int(l[2])
                            elif l[0]=='Note#':e.rec.note = int(l[2])
                            elif l[0]=='Dynamics':e.rec.dynamics = int(l[2])
                            elif l[0]=='PMBendDepth':e.rec.pmbenddepth = int(l[2])
                            elif l[0]=='PMBendLength':e.rec.pmbendlength = int(l[2])
                            elif l[0]=='PMbPortamentoUse':e.rec.pmbportamentouse = int(l[2])
                            elif l[0]=='DEMdecGainRate':e.rec.demdecgainrate = int(l[2])
                            elif l[0]=='DEMaccent':e.rec.demaccent = int(l[2])
                            elif l[0]=='IconHandle':
                                e.rec.iconhandle = Icon()
                                e.rec.iconhandle.id = l[2]
                            elif l[0]=='LyricHandle':
                                e.rec.lyrichandle = Voice()
                                e.rec.lyrichandle.id = l[2]
                            elif l[0]=='VibratoHandle':
                                e.rec.vibratohandle = Icon()
                                e.rec.vibratohandle.id = l[2]
                                e.rec.vibratohandle.type = 'Vibrato'
                            elif l[0]=='VibratoDelay':e.rec.vibratodelay = int(l[2])
                elif __section.startswith('[h#'):
                    for e in __mtrk.eventlist:
                        l = t.partition('=')
                        if l[1]=='=':
                            h = None
                            ty = 0
                            if e.rec==None:
                                pass
                            elif e.rec.type=='Anote':
                                if '[' + e.rec.lyrichandle.id + ']' == __section:
                                    h = e.rec.lyrichandle
                                    ty = 1
                                elif e.rec.vibratohandle!=None:
                                    if '[' + e.rec.vibratohandle.id + ']' == __section:
                                        h = e.rec.vibratohandle
                                        ty = 2
                            elif e.rec.type=='Singer':
                                if '[' + e.rec.iconhandle.id + ']' == __section:
                                    h = e.rec.iconhandle
                                    ty = 2
                            if ty==1:
                                l1 = l[2].split(',')
                                h.char = l1[0]
                                l1[1] = l1[1].replace('"','')
                                l2 = l1[1].rpartition(' ')
                                h.sign0 = l1[1]
                                h.sign = l2[2]
                                i = l[2].find(l1[1])
                                j = l[2].find(',',i)
                                if j>0:
                                    h.params = l[2][j+1:len(l[2])]
                            elif ty==2:
                                if l[0]=='IconID':h.iconid = l[2]
                                elif l[0]=='IDS':h.ids = l[2]
                                elif l[0]=='Original':h.original = int(l[2])
                                elif l[0]=='Caption':h.caption = l[2]
                                elif l[0]=='Length':h.length = int(l[2])
                                elif l[0]=='StartDepth':h.startdepth = int(l[2])
                                elif l[0]=='DepthBPNum':h.depthbpnum = int(l[2])
                                elif l[0]=='StartRate':h.startrate = int(l[2])
                                elif l[0]=='RateBPNum':h.ratebpnum = int(l[2])
                else:
                    pass
            else:
                __mtrk = None
            t = ''

    def read(self):
        file_rec = self.__readfile()
        self.__make_text(file_rec)

def create_lipsync(obj,vsq,filepath):

    # New key
    fno = 21
    for tr in vsq.mtrk:
        for e in tr.eventlist:
            if e.rec==None:
                pass
            elif e.rec.type=='Anote':
                k = e.rec.lyrichandle.sign
                flg_new = True
                for l in lipsync_prop:
                    if l[2]==k:
                        flg_new = False
                if flg_new:
                     l = 'Lip_' + str(fno) + '_' + k
                     lipsync_prop.append([l,fno,k])
                     fno += 1

    # Custom Props + Shapekey + Driver
    p = obj.get('LipSync')
    if p==None:
        p = rna_idprop_ui_prop_get(obj, 'LipSync', create=True)
        p['min'] = 0.000
        p['max'] = 1.000
    obj['LipSync'] = 1.000
    for l in lipsync_prop:
        if l[1]<90:
            prop = obj.get(l[0])
            if prop==None:
                p = rna_idprop_ui_prop_get(obj, l[0], create=True)
                p['min'] = 0.000
                p['max'] = 1.000
            obj[l[0]] = 0.000

            if obj.type=='MESH':
                s = context.object.data.shape_keys
                if s==None:
                    s = obj.shape_key_add(l[0])
                else:
                    s = obj.data.shape_keys.keys.get(l[0])
                    if s==None:
                        s = obj.shape_key_add(l[0])
                s = obj.data.shape_keys.keys.get(l[0])
                df = s.driver_add('value')
                create_lip_driver(df,obj,l[0])
            elif obj.type=='ARMATURE':
                for b in obj.pose.bones:
                    # Check by exist of Action#1,because LipMotion prop is changeable
                    c0 = b.constraints.get(lipsync_prop[0][0])
                    if c0==None:
                        pass
                    else:
                        c = b.constraints.get(l[0])
                        if c==None:
                            c = create_action_constraint(obj,b,l,c0.action)
                            # Driver
                            df = c.driver_add('influence')
                            create_lip_driver(df,obj,l[0])
                     
    # Action Name Create
    path0 = filepath.rpartition('/')
    path1 = path0[len(path0)-1].rpartition('\\')
    ac = path1[len(path1)-1]
    ac1 = ac.rpartition('.')
    ac = ac1[0]
    
    # Read Track
    for tr in vsq.mtrk:
        if tr.text=='Master Track':
            fps = context.scene.render.fps
            bar = vsq.mthd.division * 4            # Get length of bars
            bar_len = tr.tempo / (10**6) * 4        # Get time of bars
            bar_sec = bar / bar_len                 # Get audio frame / sec
            bar_fps = fps/bar_sec                   # Get audio frame / render frame

        # Create Action / Track
        if len(tr.eventlist)>0:
            ac1 = ac + '.' + tr.text
            a = bpy.data.actions.get(ac1)
            if a==None:
                a = bpy.data.actions.new(ac1)
                a.use_fake_user = True
            a.animation_data_clear
            
            # Set Keyframe Points
            for e in tr.eventlist:
                if e.rec==None:
                    pass
                elif e.rec.type=='Anote':
                    f = None
                    for prop in lipsync_prop:
                        if e.rec.lyrichandle.sign==prop[2] and prop[2]!='':
                            data_path = '["' + prop[0] + '"]'
                            for f0 in a.fcurves:
                                if f0.data_path == data_path:
                                    f = f0
                            if f==None:
                                g = a.groups.get(prop[0])
                                if g==None:
                                    g = a.groups.new(prop[0])
                                f = a.fcurves.new(data_path,0,prop[0])
                                f.color_mode = 'AUTO_RGB'
                                print(prop[2])
                    if f==None:
                        pass
                    else:
                        v0 = int(e.rec.dynamics) / 127 * 1.2
                        v1 = int(e.rec.dynamics) / 127
                        if v0 > 1:
                            v0 = 1
                        start = 0
                        end = 0
                        accent = 0
                        gain = 0
                        start = float(e.start) * float(bar_fps)
                        start0 = start - fps*0.1
                        if e.rec.demaccent == 0:
                            start -= 1
                        accent = start + int(e.rec.length) * int(e.rec.demaccent) / 100 * bar_fps
                        if accent < start + 1:
                            accent = start + 1
                        ga = int(e.rec.demdecgainrate) 
                        if ga==0:  # For UTAU
                            ga = 50
                        if ga <= int(e.rec.demaccent):
                            gain = accent
                        else:
                            gain = accent + int(e.rec.length) * ga / 100 * bar_fps
                        end = start + int(e.rec.length) * bar_fps + fps*0.1
                        if gain > end - 1:
                            end = gain + 1
                        k = len(f.keyframe_points)
                        if k>0:
                            ke = f.keyframe_points[k-1]
                            if ke.co.x > start0:
                                f.keyframe_points.remove(ke)
                            else:
                                f.keyframe_points.insert(start0,0)
                        else:
                            f.keyframe_points.insert(start0,0)
                        f.keyframe_points.insert(accent,v0)
                        if gain==accent:
                          pass
                        else:
                            f.keyframe_points.insert(gain,v1)
                        f.keyframe_points.insert(end,0)
            # Remove points among 1 frame 
            for f in a.fcurves:
                k0 = None
                k1 = None
                for k2 in f.keyframe_points:
                    if k0==None:
                        pass
                    else:
                        d1 = k1.co.x - k0.co.x
                        d2 = k2.co.x - k0.co.x
                        d3 = k2.co.x - k1.co.x
                        if d2 < 2:
                            k1.co.x = k0.co.x
                            k1.co.y = k0.co.y
                        elif d1 < 1 or d3 < 1:
                            if k1.co.y==k0.co.y:
                                k1.co.x = k0.co.x
                                k1.co.y = k0.co.y
                            elif k1.co.y==k2.co.y:
                                k1.co.x = k2.co.x
                                k1.co.y = k2.co.y
                            elif d1 > d3:
                                k1.co.x = k1.co.x - 1
                            else:
                                k1.co.x = k1.co.x + 1
                    k0 = k1
                    k1 = k2

def read_vsq(obj,path):
    vsq = VSQ_Data()
    vsq.filepath = path
    vsq.read()
    create_lipsync(obj,vsq,path)

#-------------------------------------------------------         
# UI Settings
#-------------------------------------------------------         
def _check_ui_poll(obj):
    try:
        if obj.type=='ARMATURE':
            rig_id = obj.data.get('rig_id')
            print(rig_id)
            if rig_id==None:
                b_head = obj.data.bones.get('head')
                if b_head==None:
                    return(0)
                else:
                    return(2)
            else:
                return(1)
        elif obj.type=='MESH':
            return(3)
    except:
        return(0)

# UI Panel
class VIEW3D_PT_tool_facebone(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Face Bone Tool"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls,context):
        if context.area.type=='VIEW_3D':
            if context.object.mode=='OBJECT':
                return(_check_ui_poll(context.object))
            else:
                return(0)
        else:
            return(0)
    
    def draw(self,context):
        layout = self.layout
        # Bone Tool
        box_bone = layout.box()
        col_0 = box_bone.column(align = True)
        col_0.label(text='Bone Tool')
        row_0 = col_0.row(align = True)
        row_0.operator('face_bone.face_bones',text='Face')
        row_0.operator('face_bone.body_bones',text='Body')
        col_0.operator('face_bone.driver_reset',text='Reset Drivers')

        # LipSync Tool
        box_syn = layout.box()
        col1 = box_syn.column(align=True)
        col1.label(text='LipSync')
        col1.operator('face_bone.import_vsq',text='Import VSQ')
        
# UI Parts : Button ( Face )
class face_bones(bpy.types.Operator):
    bl_idname = "face_bone.face_bones"
    bl_label = "Face Bones"
    bl_description = "Create custom face bones for Rigify or bone as named head"
    @classmethod
    def poll(cls,context):
        r = _check_ui_poll(context.object)
        if r in (1,2):
            return(1)
        else:
            return(0)
    def execute(self,context):
        create_bones(context.object,face_bone,face_constraints)
        if context.object.data.get('LipSync')==None:
            action_set(context.object)
        return {'FINISHED'}
          
# UI Parts : Button ( Body )
class body_bones(bpy.types.Operator):
    bl_idname = "face_bone.body_bones"
    bl_label = "Body Bones"
    bl_description = "Create custom body bones for Rigify"
    @classmethod
    def poll(cls,context):
        r = _check_ui_poll(context.object)
        if r == 1:
            return(1)
        else:
            return(0)
    def execute(self,context):
        create_bones(context.object,body_bone,body_constraints)        
        return {'FINISHED'}

# UI Parts : Button ( Reset Drivers )
class driver_reset(bpy.types.Operator):
    bl_idname = "face_bone.driver_reset"
    bl_label = "Reset Drivers"
    bl_description = "When copy object,make its driver's targets to self"
    @classmethod
    def poll(cls,context):
        return(1)
    def execute(self,context):
        replace_driver(context.object)
        return {'FINISHED'}

# UI Parts : Lipsync ( Filepath )
class import_vsq(bpy.types.Operator):
    bl_idname = "face_bone.import_vsq"
    bl_label = "Import VSQ File"
    bl_description = "Import VSQ File."

    filename_ext = ".vsq"
    filter_glob = bpy.props.StringProperty(default="*.vsq", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(name='File Path', 
        description='Filepath for VSQ File', maxlen= 1024,
        default= '',subtype='FILE_PATH')

    def execute(self, context):
        read_vsq(context.object,self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
def register():
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
