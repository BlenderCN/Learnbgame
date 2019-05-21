# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from .. import gtls

def add_font(textbdy = None,name = "Text"):
    textdata = bpy.data.curves.new(name = name,type = "FONT")
    textobj = bpy.data.objects.new(name = name,object_data = textdata)
    if textbdy != None:
        textdata.body = str(textbdy)
    bpy.context.scene.objects.link(textobj)
    return textobj

def update_font(var):
    bpy.context.scene.objects["Text"].data.body = str(var)
    
def make_test_font():
    textobj = gtls.make_obj(type = "CURVE",subtype = "FONT",do_link = True)
    textobj.data.body = str("Success(probably)")
    return textobj