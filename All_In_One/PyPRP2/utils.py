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

from PyHSPlasma import *
import configparser
import bpy, mathutils
import os

class PlasmaConfigParser(configparser.ConfigParser):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(PlasmaConfigParser, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        configparser.ConfigParser.__init__(self)
        self.read([os.path.join(bpy.utils.resource_path('USER'), 'pyprp2.conf')])

class plBlenderResManager(plResManager):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(plBlenderResManager, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.scenes = {}

    def getSceneObject(self, ob):
        loc = None
        for scn in ob.scene_users:
            if scn.name in self.scenes:
               loc = self.scenes[scn.name]
               break

        if loc is None:
            return None

        keys = self.getKeys(loc, plFactory.kSceneObject)
        for key in keys:
            if key.name == ob.name:
                return self.getObject(key)

        return None

    def useScene(self, scn):
        if scn.name in self.scenes:
            return self.scenes[scn.name]

        try:
            pl = scn.plasma_settings
        except:
            raise Exception('Scene Settings do not exist!')
        
        if not pl.exportpage or not scn.world:
            raise Exception('Invalid Scene!')

        agename = scn.world.name
        ageinfo = self.useWorld(scn.world)
        
        location = plLocation()
        location.page = pl.pageid
        location.prefix = ageinfo.seqPrefix

        pageinfo = plPageInfo()
        pageinfo.loc = location
        pageinfo.age = agename
        pageinfo.page = scn.name
        #pageinfo.flags = ...
        self.AddPage(pageinfo)
        ageinfo.addPage((scn.name, pl.pageid, pl.loadpage))
        
        self.scenes[scn.name] = location
        return location
    
    def useWorld(self, world):
        age = self.FindAge(world.name)
        if not age is None:
            return age
        
        try:
            pl = world.plasma_settings
        except:
            raise Exception('Age Settings do not exist!')

        ageinfo = plAgeInfo()
        ageinfo.name = world.name
        ageinfo.dayLength = pl.daylength
        ageinfo.seqPrefix = pl.ageprefix
        ageinfo.maxCapacity = pl.maxcapacity
        ageinfo.lingerTime = pl.lingertime
        ageinfo.releaseVersion = pl.releaseversion
        if pl.startdaytime > 0:
            ageinfo.startDayTime = pl.startdaytime

        self.AddAge(ageinfo)
        return ageinfo

def transform_vector3_by_plmat(vector,m):
    x = m[0, 0]*vector[0] + m[0, 1]*vector[1] + m[0, 2]*vector[2] + m[0, 3]
    y = m[1, 0]*vector[0] + m[1, 1]*vector[1] + m[1, 2]*vector[2] + m[1, 3]
    z = m[2, 0]*vector[0] + m[2, 1]*vector[1] + m[2, 2]*vector[2] + m[2, 3]
    return [x,y,z]

def blMatrix44_2_hsMatrix44(blmat):
    hsmat = hsMatrix44()
    for i in range(4):
        for j in range(4):
            hsmat[i,j] = blmat[j][i]
    return hsmat

def hsMatrix44_2_blMatrix44(hsmat):
    blmat = mathutils.Matrix()
    for i in range(4):
        for j in range(4):
            blmat[j][i] = hsmat[i,j]
    return blmat
