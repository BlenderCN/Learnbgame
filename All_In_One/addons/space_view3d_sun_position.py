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

# <pep8 compliant>


bl_info = {
    "name": "Sun Position",
    "author": "Michael Martin",
    "version": (1, 3, 2),
    "blender": (2, 6, 1),
    "api": 43774,
    "location": "View3D > Properties > Sun Position",
    "description": "Show sun position with objects and/or sky texture",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/" \
        "Scripts/3D_interaction/Sun_Position",
        "tracker_url": "https://projects.blender.org/tracker/" \
        "index.php?func=detail&aid=29714",
    "category": "Learnbgame",
}

"""
 v 1.3 2/1/2012
 Matrix changes took place sometime after revision 42615 and are
 reflected in this version. The only thing effected was the compass needle
 pointing north. Also modified sun lamps to automatically point in right
 direction without needing a "Track to" constraint.

 v 1.3.2 2/3/2012
 Overhauled the way callbacks were being handled as they were continuely 
 eating CPU time. Animations with keyframed Sun panel values now work
 cleanly even with the Properties shelf hidden.

"""

import bpy
from mathutils import *
import math
import bgl

############################################################################
# Bucket used for comparing changes in SolarPanel button values
############################################################################


class SunPosAttributes:

    StartSunModal = True
    ShowPanel = False
    PresetLabel = "Time & Place presets"
    Latitude = 0.0
    Longitude = 0.0
    Azimuth = 0.0
    AzNorth = 0.0
    Elevation = 0.0
    Phi = 0.0
    Theta = 0.0
    Month = 0
    Day = 0
    Year = 0
    TheTime = 0.0
    UTCzone = 0
    ShowNorth = False
    DaylightSavings = False
    NorthOffset = 0.0
    SunDistance = 0.0
    UseSunObject = False
    SunObject = "Sun"
    UseSkyTexture = False
    SkyTexture = "Sky Texture"
    UseSelectedObjects = False
    TimeSpread = 23.00
    SelectedObjectsType = "1"
    Deselect_all = False

SunAttributes = SunPosAttributes()

############################################################################
# Properties and default settings for all the items in the SolarPanel
############################################################################


class SunSettings(bpy.types.PropertyGroup):

    from bpy.props import StringProperty, EnumProperty, \
                          IntProperty, FloatProperty

    DaylightSavings = bpy.props.BoolProperty(
        description="Adds 1 hour to standard time. Widely adopted in summer.",
        default=0)

    ShowNorth = bpy.props.BoolProperty(
        description="Draws line pointing north",
        default=0)

    Latitude = FloatProperty(
        attr="",
        name="Latitude",
        description="Latitude: (+) Northern (-) Southern",
        soft_min=-90.000, soft_max=90.000, step=3.001,
        default=1.000, precision=3)

    Longitude = FloatProperty(
        attr="",
        name="Longitude",
        description="Longitude: (-) West of Greenwich  (+) East of Greenwich",
        soft_min=-180.000, soft_max=180.000,
        step=3.001, default=1.000, precision=3)

    Month = IntProperty(
        attr="",
        name="Month",
        description="Month of year",
        min=1, max=12, default=6)

    Day = IntProperty(
        attr="",
        name="Day",
        description="Day of month",
        min=1, max=31, default=21)

    Year = IntProperty(
        attr="",
        name="Year",
        description="Year",
        min=1800, max=4000, default=2011)

    UTCzone = IntProperty(
        attr="",
        name="UTC zone",
        description="Time zone: Difference from Greenwich England in hours.",
        min=0, max=12, default=0)

    TheTime = FloatProperty(
        attr="",
        name="Hour",
        description="Time of day",
        precision=4,
        soft_min=0.00, soft_max=23.9999, step=1.00, default=1.00)

    NorthOffset = FloatProperty(
        attr="",
        name="North Offset",
        description="Degrees or radians from  scene's units settings",
        unit="ROTATION",
        soft_min=-3.14159265, soft_max=3.14159265, step=10.00, default=0.00)

    SunDistance = FloatProperty(
        attr="",
        name="Sun Distance",
        description="Distance to sun object from center axis",
        unit="LENGTH",
        soft_min=1, soft_max=3000.00, step=10.00, default=50.00)

    UseSunObject = bpy.props.BoolProperty(
        description="Enable sun positioning of named lamp or mesh",
        default=False)

    SunObject = StringProperty(
        default="Sun",
        name="theSun",
        description="Name of sun object")

    UseSkyTexture = bpy.props.BoolProperty(
        description="Enable sun positioning of Cycles' "
                    "sky texture. World nodes must be enabled.",
        default=False)

    SkyTexture = StringProperty(
        default="Sky Texture",
        name="sunSky",
        description="Name of sky texture to be used")

    UseSelectedObjects = bpy.props.BoolProperty(
        description="Position all the currently selected objects",
        default=False)

    TimeSpread = FloatProperty(
        attr="",
        name="Time Spread",
        description="Time period in which to spread selected objects",
        precision=4,
        soft_min=1.00, soft_max=24.00, step=1.00, default=23.00)

    SelectedObjectsType = EnumProperty(
        name="Display type",
        description="Show selected objects as ecliptic or analemma",
        items=(
            ("1", "On the Ecliptic", ""),
            ("0", "As and Analemma", ""),
            ),
        default="1")

# ---------------------------------------------------------------------------


class SunModalEvents(bpy.types.Operator):
    bl_idname = "object.sun_modal"
    bl_label = "Sun Modal Events"
    bl_description = "Start/Stop sun panel handler"

    _handle1 = None
    _handle2 = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            return {'PASS_THROUGH'}

        if context.area:
            context.area.tag_redraw()

        if not SunAttributes.ShowPanel:
            SunAttributes.StartSunModal = True
            context.region.callback_remove(self._handle1)
            context.region.callback_remove(self._handle2)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):

        if context.area.type == 'VIEW_3D':
            if SunAttributes.StartSunModal:
                SunAttributes.StartSunModal = False
                SunAttributes.ShowPanel = True
                context.window_manager.modal_handler_add(self)
                self._handle1 = context.region.callback_add(sunPanel_callback,
                                        (self, context))
                self._handle2 = context.region.callback_add(drawNorth_callback,
                                    (self, context), 'POST_PIXEL')
            else:
                SunAttributes.ShowPanel = False
                return {'CANCELLED'}

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not available")
            return {'CANCELLED'}

###########################################################################
#
# Choice List of places, month and day at 12:00 noon
#
###########################################################################


class ChoiceList_PlaceDay(bpy.types.Operator):
    bl_idname = "object.pdp_operator"
    bl_label = "Place & Day Presets"

    #-----------  Description  --------- M   D UTC    Lat      Long   DaySav
    pdp = [["North Pole, Summer Solstice", 6, 21, 0, 90.000,   0.0000, False],
         ["Equator, Vernal Equinox",     3, 20,  0,  0.0000,   0.0000, False],
         ["Rio de Janeiro, May 10th",    5, 10, 3, -22.9002, -43.2334, False],
         ["Tokyo, August 20th",          8, 20,  9, 35.7002, 139.7669, False],
         ["Boston, Autumnal Equinox",    9, 22,  5, 42.3502, -71.0500,  True],
         ["Boston, Vernal Equinox",      3, 20,  5, 42.3502, -71.0500,  True],
         ["Honolulu, Winter Solstice",  12, 21, 10, 21.3001, -157.850, False],
         ["Honolulu, Summer Solstice",   6, 21, 10, 21.3001, -157.850, False]]

    from bpy.props import EnumProperty

    timePlacePresets = EnumProperty(
        name="Time & place presets",
        description="Preset Place & Day",
        items=(
            ("7", pdp[7][0], ""),
            ("6", pdp[6][0], ""),
            ("5", pdp[5][0], ""),
            ("4", pdp[4][0], ""),
            ("3", pdp[3][0], ""),
            ("2", pdp[2][0], ""),
            ("1", pdp[1][0], ""),
            ("0", pdp[0][0], ""),
            ),
        default="4")

    def execute(self, context):
        sp = context.scene.SolarProperty
        pdp = self.pdp
        i = int(self.properties.timePlacePresets)
        it = pdp[i]
        SunAttributes.PresetLabel = it[0]
        sp.Month = it[1]
        sp.Day = it[2]
        sp.TheTime = 12.00
        sp.UTCzone = it[3]
        sp.Latitude = it[4]
        sp.Longitude = it[5]
        sp.DaylightSavings = it[6]

        return {'FINISHED'}


############################################################################
#
# Events in the Properties Panel will cause the sunPanel_callback to be
# activated.  It will only position objects if slider values have changed.
#
############################################################################


def sunPanel_callback(self, context):
    if SunAttributes.Deselect_all:
        SunAttributes.Deselect_all = False
        bpy.ops.object.select_all(action='DESELECT')

    sp = bpy.context.scene.SolarProperty
    if (sp.UseSkyTexture != SunAttributes.UseSkyTexture or
        sp.SkyTexture != SunAttributes.SkyTexture or
        sp.UseSunObject != SunAttributes.UseSunObject or
        sp.SunObject != SunAttributes.SunObject or
        sp.UseSelectedObjects != SunAttributes.UseSelectedObjects or
        sp.TimeSpread != SunAttributes.TimeSpread or
        sp.SelectedObjectsType != SunAttributes.SelectedObjectsType or
        sp.Latitude != SunAttributes.Latitude or
        sp.Longitude != SunAttributes.Longitude or
        sp.Month != SunAttributes.Month or
        sp.Day != SunAttributes.Day or
        sp.Year != SunAttributes.Year or
        sp.TheTime != SunAttributes.TheTime or
        sp.UTCzone != SunAttributes.UTCzone or
        sp.DaylightSavings != SunAttributes.DayligthSavings or
        sp.ShowNorth != SunAttributes.ShowNorth or
        sp.NorthOffset != SunAttributes.NorthOffset or
        sp.SunDistance != SunAttributes.SunDistance):

        SunAttributes.UseSkyTexture = sp.UseSkyTexture
        SunAttributes.SkyTexture = sp.SkyTexture
        SunAttributes.UseSunObject = sp.UseSunObject
        SunAttributes.SunObject = sp.SunObject
        SunAttributes.UseSelectedObjects = sp.UseSelectedObjects
        SunAttributes.TimeSpread = sp.TimeSpread
        SunAttributes.SelectedObjectsType = sp.SelectedObjectsType
        SunAttributes.Latitude = sp.Latitude
        SunAttributes.Longitude = sp.Longitude
        SunAttributes.Month = sp.Month
        SunAttributes.Day = sp.Day
        SunAttributes.Year = sp.Year
        SunAttributes.TheTime = sp.TheTime
        SunAttributes.UTCzone = sp.UTCzone
        SunAttributes.DayligthSavings = sp.DaylightSavings
        SunAttributes.ShowNorth = sp.ShowNorth
        SunAttributes.NorthOffset = sp.NorthOffset
        SunAttributes.SunDistance = sp.SunDistance
        placeSun()


############################################################################
#
# Routine for drawing compass line pointing north.
#
############################################################################


def drawNorth_callback(self, context):

    if (SunAttributes.ShowNorth):

        view3d = bpy.context
        region = view3d.region_data

        # ------------------------------------------------------------------
        # Set up the compass needle using the current north offset angle
        # less 90 degrees.  This forces the unit circle to begin at the
        # 12 O'clock instead of 3 O'clock position.
        # ------------------------------------------------------------------
        color = (0.2, 0.6, 1.0, 0.7)
        radius = 800
        angle = -(SunAttributes.NorthOffset - math.pi / 2)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        p1, p2 = (0, 0, 0), (x, y, 0)   # Start & end of needle

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Thanks to Buerbaum Martin for the following which draws openGL
        # lines.  ( From his script space_view3d_panel_measure.py )
        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # ------------------------------------------------------------------
        # Convert the Perspective Matrix of the current view/region.
        # ------------------------------------------------------------------
        perspMatrix = region.perspective_matrix
        tempMat = [perspMatrix[j][i] for i in range(4) for j in range(4)]
        perspBuff = bgl.Buffer(bgl.GL_FLOAT, 16, tempMat)

        # ---------------------------------------------------------
        # Store previous OpenGL settings.
        # ---------------------------------------------------------
        MatrixMode_prev = bgl.Buffer(bgl.GL_INT, [1])
        bgl.glGetIntegerv(bgl.GL_MATRIX_MODE, MatrixMode_prev)
        MatrixMode_prev = MatrixMode_prev[0]

        # Store projection matrix
        ProjMatrix_prev = bgl.Buffer(bgl.GL_DOUBLE, [16])
        bgl.glGetFloatv(bgl.GL_PROJECTION_MATRIX, ProjMatrix_prev)

        # Store Line width
        lineWidth_prev = bgl.Buffer(bgl.GL_FLOAT, [1])
        bgl.glGetFloatv(bgl.GL_LINE_WIDTH, lineWidth_prev)
        lineWidth_prev = lineWidth_prev[0]

        # Store GL_BLEND
        blend_prev = bgl.Buffer(bgl.GL_BYTE, [1])
        bgl.glGetFloatv(bgl.GL_BLEND, blend_prev)
        blend_prev = blend_prev[0]

        line_stipple_prev = bgl.Buffer(bgl.GL_BYTE, [1])
        bgl.glGetFloatv(bgl.GL_LINE_STIPPLE, line_stipple_prev)
        line_stipple_prev = line_stipple_prev[0]

        # Store glColor4f
        color_prev = bgl.Buffer(bgl.GL_FLOAT, [4])
        bgl.glGetFloatv(bgl.GL_COLOR, color_prev)

        # ---------------------------------------------------------
        # Prepare for 3D drawing
        # ---------------------------------------------------------
        bgl.glLoadIdentity()
        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glLoadMatrixf(perspBuff)

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_LINE_STIPPLE)

        # ------------------
        # and draw the line
        # ------------------
        width = 2
        bgl.glLineWidth(width)
        bgl.glColor4f(color[0], color[1], color[2], color[3])
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex3f(p1[0], p1[1], p1[2])
        bgl.glVertex3f(p2[0], p2[1], p2[2])
        bgl.glEnd()

        # ---------------------------------------------------------
        # Restore previous OpenGL settings
        # ---------------------------------------------------------
        bgl.glLoadIdentity()
        bgl.glMatrixMode(MatrixMode_prev)
        bgl.glLoadMatrixf(ProjMatrix_prev)
        bgl.glLineWidth(lineWidth_prev)

        if not blend_prev:
            bgl.glDisable(bgl.GL_BLEND)
        if not line_stipple_prev:
            bgl.glDisable(bgl.GL_LINE_STIPPLE)

        bgl.glColor4f(color_prev[0],
            color_prev[1],
            color_prev[2],
            color_prev[3])


############################################################################
#
# Now Draw the Solar Panel, sliders, et. al.
#
############################################################################


class SolarPanel(bpy.types.Panel):

    bl_idname = "panel.SolarPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "object"
    bl_label = "Sun Position"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if (context.area.type == 'VIEW_3D' and
           (context.mode == 'OBJECT')):
            return 1
        return 0

    def draw(self, context):
        sp = bpy.context.scene.SolarProperty
        layout = self.layout
        if SunAttributes.StartSunModal:
            layout.operator('object.sun_modal', 'Enable', icon='PLAY')
        else:
            layout.operator('object.sun_modal', 'Disable', icon='PAUSE')

        if SunAttributes.ShowPanel:
            self.draw_panel(context, sp, layout)

    def draw_panel(self, context, sp, layout):
        box = self.layout.box()
        toprow = box.row()
        row = toprow.row(align=True)
        row.alignment = 'CENTER'
        split = row.split(percentage=.5)
        colL = split.column()
        colR = split.column()
        colL.alignment = 'LEFT'
        colL.prop(sp, "UseSkyTexture", text="Use Cycles sky texture")
        if(sp.UseSkyTexture):
            try:
                colL.prop_search(sp, "SkyTexture",
                     bpy.context.scene.world.node_tree, "nodes", text="")
            except:
                pass
        colR.prop(sp, "UseSunObject", text="Use named object")
        if(sp.UseSunObject):
            try:
                colR.prop_search(sp, "SunObject",
                     bpy.context.scene, "objects", text="")
            except:
                pass
        colL.prop(sp, "UseSelectedObjects", text="Use selected objects")
        if(sp.UseSelectedObjects):
            if(sp.SelectedObjectsType == "1"):
                colR.prop(sp, "TimeSpread")
            colR.props_enum(sp, "SelectedObjectsType")
        elif sp.UseSelectedObjects != SunAttributes.UseSelectedObjects:
            if len(bpy.context.selected_objects) > 1:
                SunAttributes.Deselect_all = True

        row = layout.row()
        row.alignment = 'CENTER'
        row.operator_menu_enum('object.pdp_operator',
            'timePlacePresets', text=SunAttributes.PresetLabel)

        box = self.layout.box()
        layout.separator()
        toprow = box.row()
        row = toprow.row(align=True)
        row.alignment = 'CENTER'
        split = row.split(percentage=.6)
        colL = split.column()
        colR = split.column()
        colL.alignment = 'RIGHT'
        colR.alignment = 'LEFT'
        colL.prop(sp, "Latitude")
        colR.label(text=formatLatitudeLongitude(sp.Latitude, True))
        colL.prop(sp, "Longitude")
        colR.label(text=formatLatitudeLongitude(sp.Longitude, False))
        colL.label(text="        Azimuth:  " + \
             str(round(SunAttributes.Azimuth, 3)))
        colR.label(text="Solar Elevation: " + \
             str(round(SunAttributes.Elevation, 5)))
        row = layout.row()
        row.alignment = 'RIGHT'
        split = row.split(percentage=.4)
        colL = split.column()
        colR = split.column()

        colL.prop(sp, "Month")
        colR.prop(sp, "Day")
        colL.prop(sp, "Year")
        colL.prop(sp, "UTCzone", slider=True)
        colL.prop(sp, "ShowNorth", text="Show North")
        colR.prop(sp, "TheTime")
        gmtTime = formatTime(sp.TheTime, sp.UTCzone, \
                             sp.DaylightSavings, sp.Longitude)
        colR.label(text=gmtTime, icon='TIME')
        colR.prop(sp, "DaylightSavings", text="Daylight Savings Time")

        layout.separator()
        colL.prop(sp, "NorthOffset")
        colR.prop(sp, "SunDistance")

############################################################################


def formatTime(theTime, UTCzone, daylightSavings, longitude):
    hh = str(int(theTime))
    min = (theTime - int(theTime)) * 60
    sec = int((min - int(min)) * 60)
    mm = "0" + str(int(min)) if min < 10 else str(int(min))
    ss = "0" + str(sec) if sec < 10 else str(sec)

    zone = UTCzone
    if(longitude < 0):
        zone *= -1
    if (daylightSavings):
        zone += 1
    gt = int(theTime) - zone

    if gt < 0:
        gt = 24 + gt
    elif gt > 23:
        gt = gt - 24
    gt = str(gt)

    return  "Local: " + hh + ":" + mm + ":" + ss + \
                    "   UTC: " + gt + ":" + mm + ":" + ss


def formatLatitudeLongitude(latLong, isLatitude):
    hh = str(abs(int(latLong)))
    min = abs((latLong - int(latLong)) * 60)
    sec = abs(int((min - int(min)) * 60))
    mm = "0" + str(int(min)) if min < 10 else str(int(min))
    ss = "0" + str(sec) if sec < 10 else str(sec)
    degrees = '\xb0'
    if latLong == 0:
        coordTag = " "
    else:
        if isLatitude:
            coordTag = " N" if latLong > 0 else " S"
        else:
            coordTag = " E" if latLong > 0 else " W"

    return hh + degrees + " " + mm + "' " + ss + '"' + coordTag

############################################################################
#
# PlaceSun() will cycle through all the selected objects of type LAMP or
# MESH and call setSunPosition to place them in the sky.
#
############################################################################


def placeSun():
    sp = bpy.context.scene.SolarProperty
    totalObjects = len(bpy.context.selected_objects)

    localTime = sp.TheTime
    if (sp.Longitude > 0):
        zone = sp.UTCzone * -1
    else:
        zone = sp.UTCzone
    if (sp.DaylightSavings):
        zone -= 1

    northOffset = radToDeg(sp.NorthOffset)

    getSunPosition(None, localTime, sp.Latitude, sp.Longitude,
            northOffset, zone, sp.Month, sp.Day, sp.Year,
            sp.SunDistance, "E")

    if sp.UseSkyTexture:
        try:
            nt = bpy.context.scene.world.node_tree.nodes
            sunTex = nt.get(SunAttributes.SkyTexture)
            if sunTex:
                locX = math.sin(SunAttributes.Phi) * \
                       math.sin(-SunAttributes.Theta)
                locY = math.sin(SunAttributes.Theta) * \
                       math.cos(SunAttributes.Phi)
                locZ = math.cos(SunAttributes.Theta)
                sunTex.sun_direction = locX, locY, locZ
        except:
            pass

    if sp.UseSunObject:
        try:
            obj = bpy.context.scene.objects.get(SunAttributes.SunObject)
            setSunPosition(obj, sp.SunDistance)
            if obj.type == 'LAMP':
                obj.rotation_euler = \
                      (math.radians(SunAttributes.Elevation - 90), 0,
                        math.radians(-SunAttributes.AzNorth))
        except:
            pass

    if totalObjects < 1 or not sp.UseSelectedObjects:
        return False

    if sp.SelectedObjectsType == "1":
        # Ecliptic
        if totalObjects > 1:
            timeIncrement = sp.TimeSpread / (totalObjects - 1)
            localTime = localTime + timeIncrement * (totalObjects - 1)
        else:
            timeIncrement = sp.TimeSpread

        for obj in bpy.context.selected_objects:
            mesh = obj.type
            if mesh == 'LAMP' or mesh == 'MESH':
                getSunPosition(obj, localTime, sp.Latitude, sp.Longitude,
                    northOffset, zone, sp.Month, sp.Day, sp.Year,
                    sp.SunDistance, "E")
                setSunPosition(obj, sp.SunDistance)
                localTime = localTime - timeIncrement
                if mesh == 'LAMP':
                    obj.rotation_euler = \
                          (math.radians(SunAttributes.Elevation - 90), 0,
                            math.radians(-SunAttributes.AzNorth))
    else:
        # Analemma
        dayIncrement = 365.25 / totalObjects
        day = 1
        for obj in bpy.context.selected_objects:
            mesh = obj.type
            if mesh == 'LAMP' or mesh == 'MESH':
                getSunPosition(obj, localTime, sp.Latitude, sp.Longitude,
                    northOffset, zone, 1, day, sp.Year,
                    sp.SunDistance, "A")
                setSunPosition(obj, sp.SunDistance)
                day += dayIncrement
                if mesh == 'LAMP':
                    obj.rotation_euler = \
                          (math.radians(SunAttributes.Elevation - 90), 0,
                            math.radians(-SunAttributes.AzNorth))

    return True

############################################################################
#
# Calculate the actual position of the sun based on input parameters.
#
# The sun positioning algorithms below are based on the National Oceanic
# and Atmospheric Administration's (NOAA) Solar Position Calculator
# which rely on calculations of Jean Meeus' book "Astronomical Algorithms."
# Use of NOAA data and products are in the public domain and may be used
# freely by the public as outlined in their policies at
#               www.nws.noaa.gov/disclaimer.php
#
# The calculations of this script can be verified with those of NOAA's
# using the Azimuth and Solar Elevation displayed in the SolarPanel.
# NOAA's web site is:
#               www.srrb.noaa.gov/highlights/sunrise/azel.htm
############################################################################


def getSunPosition(obj, localTime, latitude, longitude, northOffset,
                   utcZone, month, day, year, distance, showType):

    longitude *= -1                 # for internal calculations
    utcTime = localTime + utcZone   # Set Greenwich Meridian Time

    if latitude > 89.93:            # Latitude 90 and -90 gives
        latitude = degToRad(89.93)  # erroneous results so nudge it
    elif latitude < -89.93:
        latitude = degToRad(-89.93)
    else:
        latitude = degToRad(latitude)

    if showType == "E":            # ecliptic
        t = julianTimeFromY2k(utcTime, year, month, day)
    else:                          # analemma
        t = julianTimeFromY2k(utcTime, year, 1, 1)
        if day > 1:
            dayValue = 0.00002737850787131
            t += dayValue * day

    e = degToRad(obliquityCorrection(t))
    L = degToRad(trueLongitudeOfSun(t) - 0.00569 - 0.00478 \
              * math.sin(degToRad(125.04 - 1934.136 * t)))
    solarDec = sunDeclination(e, L)
    eqtime = calcEquationOfTime(t)

    timeCorrection = (eqtime - 4 * longitude) + 60 * utcZone
    trueSolarTime = ((utcTime - utcZone) * 60.0 + timeCorrection) % 1440

    hourAngle = trueSolarTime / 4 - 180
    if(hourAngle < -180.0):
        hourAngle = hourAngle + 360.0
    h = degToRad(hourAngle)

    solarElevation = radToDeg(math.asin(math.sin(latitude) * \
         math.sin(solarDec) + math.cos(latitude) * \
         math.cos(solarDec) * math.cos(h)))
    azimuth = radToDeg(math.pi + math.atan2((math.sin(h)), ((math.cos(h) * \
       math.sin(latitude)) - math.tan(solarDec) * math.cos(latitude))))

    solarAzimuth = azimuth + northOffset
    SunAttributes.AzNorth = solarAzimuth

    SunAttributes.Theta = math.pi / 2 - degToRad(solarElevation)
    SunAttributes.Phi = degToRad(solarAzimuth) * -1
    SunAttributes.Azimuth = azimuth
    SunAttributes.Elevation = solarElevation


def setSunPosition(obj, distance):

    locX = math.sin(SunAttributes.Phi) * \
           math.sin(-SunAttributes.Theta) * distance
    locY = math.sin(SunAttributes.Theta) * \
           math.cos(SunAttributes.Phi) * distance
    locZ = math.cos(SunAttributes.Theta) * distance

    #----------------------------------------------
    # Update selected object in viewport
    #----------------------------------------------
    obj.location = locX, locY, locZ


##########################################################################
## Get the elapsed julian time since 1/1/2000 12:00 gmt
## Y2k epoch (1/1/2000 12:00 gmt) is Julian day 2451545.0
##########################################################################


def julianTimeFromY2k(utcTime, year, month, day):
    century = 36525.0  # Days in Julian Century
    epoch = 2451545.0  # Julian Day for 1/1/2000 12:00 gmt

    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4.0)
    jd = math.floor((365.25 * (year + 4716.0))) + \
         math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    return ((jd + (utcTime / 24)) - epoch) / century


def sunDeclination(e, L):
    return (math.asin(math.sin(e) * math.sin(L)))


def calcEquationOfTime(t):
    epsilon = obliquityCorrection(t)
    ml = degToRad(meanLongitudeSun(t))
    e = eccentricityEarthOrbit(t)
    m = degToRad(meanAnomalySun(t))
    y = math.tan(degToRad(epsilon) / 2.0)
    y = y * y
    sin2ml = math.sin(2.0 * ml)
    cos2ml = math.cos(2.0 * ml)
    sin4ml = math.sin(4.0 * ml)
    sinm = math.sin(m)
    sin2m = math.sin(2.0 * m)
    etime = y * sin2ml - 2.0 * e * sinm + 4.0 * e * y * \
             sinm * cos2ml - 0.5 * y ** 2 * sin4ml - 1.25 * e ** 2 * sin2m
    return (radToDeg(etime) * 4)


def obliquityCorrection(t):
    ec = obliquityOfEcliptic(t)
    omega = 125.04 - 1934.136 * t
    return (ec + 0.00256 * math.cos(degToRad(omega)))


def obliquityOfEcliptic(t):
    return ((23.0 + 26.0 / 60 + (21.4480 - 46.8150) / 3600 * t \
             - (0.00059 / 3600) * t ** 2 + (0.001813 / 3600) * t ** 3))


def trueLongitudeOfSun(t):
    return (meanLongitudeSun(t) + equationOfSunCenter(t)) % 360.0


def meanLongitudeSun(t):
    return (280.46645 + 36000.76983 * t + 0.0003032 * t ** 2) % 360


def equationOfSunCenter(t):
    m = degToRad(meanAnomalySun(t))
    c = (1.914600 - 0.004817 * t - 0.000014 * t ** 2) * math.sin(m) + \
        (0.019993 - 0.000101 * t) * math.sin(m * 2) + \
         0.000290 * math.sin(m * 3)
    return c


def meanAnomalySun(t):
    return (357.52911 + 35999.05030 * t - \
          0.0001559 * t ** 2 - 0.00000048 * t ** 3)


def eccentricityEarthOrbit(t):
    return (0.016708617 - 0.000042037 * t - 0.0000001236 * t ** 2)


def degToRad(angleDeg):
    return (math.pi * angleDeg / 180.0)


def radToDeg(angleRad):
    return (180.0 * angleRad / math.pi)

############################################################################


def register():
    bpy.utils.register_class(SunSettings)
    bpy.types.Scene.SolarProperty = \
        bpy.props.PointerProperty(type=SunSettings, \
                        name="Sun Position", \
                        description="Sun Position Settings")
    bpy.utils.register_class(SunModalEvents)
    bpy.utils.register_class(ChoiceList_PlaceDay)
    bpy.utils.register_class(SolarPanel)


def unregister():
    bpy.utils.unregister_class(SolarPanel)
    bpy.utils.unregister_class(ChoiceList_PlaceDay)
    bpy.utils.unregister_class(SunModalEvents)
    del bpy.types.Scene.SolarProperty
    bpy.utils.unregister_class(SunSettings)

if __name__ == "__main__":
    register()
