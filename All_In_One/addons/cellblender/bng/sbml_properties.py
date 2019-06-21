# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 17:47:06 2013

@author: proto
"""

import bpy
from . import sbml_operators
from bpy.props import StringProperty


class SBMLPropertyGroup(bpy.types.PropertyGroup):
    filePath = StringProperty(name="Include Object in Model", default=False)


