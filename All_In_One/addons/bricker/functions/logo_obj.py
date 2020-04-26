# Copyright (C) 2019 Christopher Gearhart
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

# System imports
from os.path import dirname, abspath

# Addon imports
from .common import *
from .general import *

def removeDoubles(obj):
    select(obj, active=True, only=True)
    for v in obj.data.vertices:
        v.select = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    obj.data.update()


def getLegoLogo(scn, typ, res, decimate, dimensions):
    # update refLogo
    if typ == "NONE":
        refLogo = None
    else:
        refLogoName = "Bricker_LEGO_Logo_%(res)s_%(decimate)s" % locals()
        refLogo = bpy.data.objects.get(refLogoName)
        if refLogo is None:
            # get logo text reference with current settings
            logo_txt_ref = getLegoLogoTxtObj(scn, res, "Bricker_LEGO_Logo_Text")
            # convert logo_txt_ref to mesh
            refLogo = logo_txt_ref.copy()
            refLogo.data = logo_txt_ref.data.copy()
            refLogo.name = refLogoName
            # convert text to mesh
            link_object(refLogo, scn)
            unhide(refLogo)
            select(refLogo, active=True, only=True)
            bpy.ops.object.convert(target="MESH")
            # remove duplicate verts
            removeDoubles(refLogo)
            # decimate mesh
            if decimate != 0:
                dMod = refLogo.modifiers.new("Decimate", type="DECIMATE")
                dMod.ratio = 1 - (decimate / 10)
                if b280():
                    # TODO: use view layer with smoke, not just the first view layer
                    m = refLogo.to_mesh(bpy.context.depsgraph, True)
                else:
                    m = refLogo.to_mesh(scn, True, "PREVIEW")
                refLogo.modifiers.remove(dMod)
                refLogo.data = m
            safeUnlink(refLogo)
    return refLogo


def getLEGOStudFont():
    LEGOStudFont = bpy.data.fonts.get("LEGO Stud Font")
    if not LEGOStudFont:
        brickerAddonPath = dirname(dirname(abspath(__file__)))
        fontPath = "%(brickerAddonPath)s/lib/LEGO_Stud_Font.ttf" % locals()
        LEGOStudFont = bpy.data.fonts.load(fontPath)
    return LEGOStudFont

def getLegoLogoTxtObj(scn, res, name):
    # get logo_txt_ref from Bricker_storage scene
    logo_txt = bpy.data.objects.get(name)
    if logo_txt is None:
        # set up new logo_txt_ref
        c = bpy.data.curves.new("%(name)s_curve" % locals(), "FONT")
        logo_txt = bpy.data.objects.new(name, c)
        safeUnlink(logo_txt)
        logo_txt.name = name
        logo_txt.data.body = "LEGO"
        logo_txt.data.fill_mode = "FRONT"
        logo_txt.data.offset = -0.01
        logo_txt.data.extrude = 0.02
        logo_txt.data.bevel_depth = 0.044
        logo_txt.data.font = getLEGOStudFont()
        logo_txt.data.align_x = "CENTER"
        logo_txt.data.align_y = "CENTER"
        logo_txt.data.space_character = 0.8
    # set logo_txt_ref resolution
    logo_txt.data.resolution_u = res - 1
    logo_txt.data.bevel_resolution = res - 1
    return logo_txt
