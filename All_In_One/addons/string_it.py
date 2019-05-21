# string_it.py (c) 2011 Phil Cote (cotejrp1)
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****
"""
HOW TO USE:

The String It tool is found in the 3D view's tool panel when you hit 'T'.
To make initial curve, select scene items you to run curve through.
Once you have what you want, hit 'Make Curve'

Options:
Spline Type - Choose straight polyline or a bezier curves
running through your objects.

Close Shape - Use this to close add one more segment to close the curve.

Finalize and Attach - Place hook mods on curve to attach points to each object.

WARNING:
If you select out of this, you lose option to attach curve using the tool.
Also, Finalizing and attachment completes the operator.
Only use it when you know you have the curve
configuration you want.

"""
import bpy
from pdb import set_trace

bl_info = {
    'name': 'String It',
    'author': 'Phil Cote, cotejrp1, (http://www.blenderaddons.com)',
    'version': (0,2),
    "blender": (2, 5, 8),
    "api": 37702,
    'location': '',
    'description': 'Run a curve through each selected object in a scene.',
    'warning': '',  # used for warning icon and text in addons panel
    'category': 'Add Curve'}


def makeBezier(spline, vertList):
    numPoints = (len(vertList) / 3) - 1
    spline.bezier_points.add(numPoints)
    spline.bezier_points.foreach_set("co", vertList)
    for point in spline.bezier_points:
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"


def makePoly(spline, vertList):
    numPoints = (len(vertList) / 4) - 1
    spline.points.add(numPoints)
    spline.points.foreach_set("co", vertList)


def buildHooks(splineChoice, curveOb, object_list):

    bpy.context.scene.objects.active = curveOb

    # create the hooks to each object
    for i in range(len(object_list)):

        # object to be hooked into gets selected.
        object_list[i].select = True

        # the specific curve point on the curve needs to be selected.
        if splineChoice == 'bezier':
            curveOb.data.splines[0].bezier_points[i].select_control_point = True
        else:
            curveOb.data.splines[0].points[i].select = True

        # set hook mod between the select curve point and the selected object.
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.hook_add_selob()
        bpy.ops.object.editmode_toggle()

        # deselect the curve point.
        if splineChoice == 'bezier':
            curveOb.data.splines[0].bezier_points[i].select_control_point = False
        else:
            curveOb.data.splines[0].points[i].select = False

        # deselect the object and we're done with this point.
        object_list[i].select = False


class StringItOperator(bpy.types.Operator):
    '''Makes curve that runs through the centers of each selected object.'''
    bl_idname = "curve.string_it_operator"
    bl_label = "String It Options"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = \
        "Pick objects to run line through. Click button more options."

    splineOptionList = [('poly', 'poly', 'Poly Curve'), ('bezier', 'bezier', 'Bezier Curve')]
    splineChoice = bpy.props.EnumProperty(name="Spline Type", items=splineOptionList,
                                          description="String it up with either a straight or curved line")
    closeSpline = bpy.props.BoolProperty(name="Close Shape", default=False,
                                         description="Add one more segment to make the curve being created a closed shape." +
                                                     "If you want a closed curve to be attached, make sure to check this option first.")
    attachObjects = bpy.props.BoolProperty(name="Finalize and Attach", default=False,
                                           description="Hook attach curve to objects ONLY when ready to commit to this.")

    @classmethod
    def poll(self, context):
        selected_obs = [ob for ob in context.selectable_objects if ob.select]
        totalSelected = len(selected_obs)
        return totalSelected > 1

    def execute(self, context):

        splineType = self.splineChoice.upper()
        scn = context.scene
        obList = [ob for ob in scn.objects if ob.select]

        # build the vert data set to use to make the curve
        vertList = []
        for sceneOb in obList:
            vertList.append(sceneOb.location.x)
            vertList.append(sceneOb.location.y)
            vertList.append(sceneOb.location.z)
            if splineType == 'POLY':
                vertList.append(0)

        # build the curve itself.
        crv = bpy.data.curves.new("curve", type="CURVE")
        crv.splines.new(type=splineType)
        spline = crv.splines[0]

        # bezier option
        if splineType == 'BEZIER':
            makeBezier(spline, vertList)

        # polyline option
        else:
            makePoly(spline, vertList)

        # close spline checkbox option
        spline.use_cyclic_u = self.closeSpline

        # add the curve to the scene.
        crvOb = bpy.data.objects.new("curveOb", crv)
        scn.objects.link(crvOb)

        # attach to curve option
        if self.attachObjects:
            buildHooks(self.splineChoice, crvOb, obList)

        return {'FINISHED'}


class StringItPanel(bpy.types.Panel):
    bl_label = "String It"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        self.layout.row().operator("curve.string_it_operator", text="Make Curve")


def register():
    bpy.utils.register_class(StringItOperator)
    bpy.utils.register_class(StringItPanel)


def unregister():
    bpy.utils.unregister_class(StringItOperator)
    bpy.utils.unregister_class(StringItPanel)


if __name__ == "__main__":
    register()
