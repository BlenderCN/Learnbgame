
"""
    Copyright (C) <2010>  Autin L.
    
    This file ePMV_git/blender/v25/plugin/epmv_blender_plugin.py is part of ePMV.

    ePMV is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ePMV is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ePMV.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
#!BPY

__url__ = ["http://epmv.scripps.edu/",
           'http://epmv.scripps.edu/citationinformation',]

bl_info = {
    "name": "ePMV",
    "description": """Use Blender as a molecular viewer
ePMV by Ludovic Autin,Graham Jonhson,Michel Sanner.
Develloped in the Molecular Graphics Laboratory directed by Arthur Olson.""",
    "author": "Ludovic Autin",
    "version": (0,3,7),
    "blender": (2, 5, 8),
    "api": 31236,
    "location": "View3D > Tool Shelf > ePMV",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": ""\
        "Scripts/My_Script",
    "tracker_url": ""\
        "func=detail&aid=<number>",
    "category": "Learnbgame"
}
# -------------------------------------------------------------------------- 
# ***** BEGIN GPL LICENSE BLOCK ***** 
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
# Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA. 
# 
# ***** END GPL LICENCE BLOCK ***** 
# -------------------------------------------------------------------------- 
#general import
import bpy
import bpy
import sys,os

bpath = bpy.app.binary_path
if sys.platform == "win32":
    os.chdir(os.path.dirname(bpath))
    softdir = os.path.abspath(os.path.curdir)
elif  sys.platform == "darwin":
    os.chdir(os.path.dirname(bpath))
    os.chdir("../../../")
    softdir = os.path.abspath(os.path.curdir)
MGL_ROOT =softdir
upypath = softdir+"/MGLToolsPckgs"#"/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
sys.path.insert(0,upypath)
sys.path.append(MGL_ROOT+'/MGLToolsPckgs/PIL')

import upy
upy.setUIClass('blender2.5')

class launchEPMV(bpy.types.Operator):
    bl_idname = "epmv.launch"
    bl_label = "ePMV"
    
    def execute(self, context):
        from ePMV import epmvGui
        epmvgui = epmvGui.epmvGui()
        epmvgui.setup(rep="epmv",mglroot=MGL_ROOT,host='blender25')
        ##
        #define the default options
        epmvgui.epmv.Set(bicyl=True,use_progressBar = False,doLight = True,doCamera = True,
                        useLog = False,doCloud=False,forceFetch=False)
        epmvgui.display()
        #create an empty object call "welcome to epmv ?"
        epmvobj = epmvgui.epmv.helper.newEmpty("Welcome to ePMV")
        return {'FINISHED'}
        
def menu_draw(self, context):
    self.layout.operator("epmv.launch",icon="PLUG")

def register():
    bpy.utils.register_class(launchEPMV)
    bpy.types.INFO_HT_header.append(menu_draw)
    bpy.types.INFO_MT_add.append(menu_draw)
def unregister():
#    epmvgui.close()
    bpy.types.INFO_HT_header.remove(menu_draw)
    bpy.types.INFO_MT_add.remove(menu_draw)
if __name__ == '__main__':
    register()


