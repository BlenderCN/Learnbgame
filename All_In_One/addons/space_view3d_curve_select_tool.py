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
    "name": "Curve select tool",
    "author": "jasperge",
    "version": (0, 5),
    "blender": (2, 7, 1),
    "location": "View3D > Toolbar",
    "description": "Simple tool to select the first/last/previous/next point on a curve",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}


# Import modules.
from collections import defaultdict
import bpy
from bpy.props import EnumProperty


def check_selection(curve_obj, context):
    if not curve_obj:
        curve_obj = context.object
    if curve_obj and curve_obj.type == "CURVE":
        return curve_obj
    else:
        print("No curve object selected or specified...")
        return None


def get_points(spline):
    if spline.bezier_points:
        return (spline.bezier_points, "BEZIER")
    elif spline.points:
        return (spline.points, "NURBS")
    else:
        print("Oops, no points found on the spline!")
        return (None, None)


def get_curve_selection(curve_obj):
    curve_selection = defaultdict(list)
    splines = curve_obj.data.splines
    for spline in splines:
        points, type = get_points(spline)
        for point in points:
            if (type == "BEZIER" and (point.select_control_point or point.select_left_handle or point.select_right_handle)) or (type == "NURBS" and point.select):
                curve_selection[spline].append(point)
                if not spline in curve_selection["spline_list"]:
                    curve_selection["spline_list"].append(spline)

    return curve_selection


def get_current_indices(curve, spline, point):
    s_idx = [i for i, s in enumerate(curve.splines) if s == spline][0]
    points, _ = get_points(spline)
    p_idx = [i for i, p in enumerate(points) if p == point][0]

    return (s_idx, p_idx)


def deselect_all_points(curve_obj):
    def deselect_bezier(point):
        point.select_control_point = False
        point.select_left_handle = False
        point.select_right_handle = False

    def deselect_nurbs(point):
        point.select = False

    for spline in curve_obj.data.splines:
        points, type = get_points(spline)
        for point in points:
            if type == "BEZIER":
                deselect_bezier(point)
            elif type == "NURBS":
                deselect_nurbs(point)


def select_point_handles(point, type):
    if type == "BEZIER":
        point.select_control_point = True
        point.select_left_handle = True
        point.select_right_handle = True
    elif type == "NURBS":
        point.select = True


def select_point(self, context, curve_obj=None):
    action = self.action
    supported_actions = ("FIRST", "LAST", "PREVIOUS", "NEXT")
    curve_obj = check_selection(curve_obj, context)
    point_to_select = None
    type = ""

    if not curve_obj:
        return

    if not curve_obj.data.splines:
        print("Curve doesn't have any splines")
        return

    # if not action in supported_actions:
    #     print("\"{action}\" not found in {supported_actions}".format(
    #         action=action,
    #         supported_actions=supported_actions))
    #     return

    curve_selection = get_curve_selection(curve_obj)

    if action == "FIRST":
        if curve_selection:
            spline = curve_selection["spline_list"][0]
        else:
            spline = curve_obj.data.splines[0]
        points, type = get_points(spline)
        point_to_select = points[0]
    elif action == "LAST":
        if curve_selection:
            spline = curve_selection["spline_list"][-1]
        else:
            spline = curve_obj.data.splines[-1]
        points, type = get_points(spline)
        point_to_select = points[-1]
    elif action == "PREVIOUS":
        if curve_selection:
            spline = curve_selection["spline_list"][0]
            point = curve_selection[spline][0]
            s_idx, p_idx = get_current_indices(curve_obj.data, spline, point)
            points, type = get_points(spline)
            # Check if point is first point on spline.
            if point == points[0]:
                # Select last point of previous spline.
                points, type = get_points(curve_obj.data.splines[s_idx - 1])
                point_to_select = points[-1]
            # Else get previous point on the spline.
            else:
                points, type = get_points(spline)
                point_to_select = points[p_idx - 1]
        else:
            # Select first point
            spline = curve_obj.data.splines[0]
            points, type = get_points(spline)
            point_to_select = points[0]
    elif action == "NEXT":
        if curve_selection:
            spline = curve_selection["spline_list"][-1]
            point = curve_selection[spline][-1]
            s_idx, p_idx = get_current_indices(curve_obj.data, spline, point)
            points, type = get_points(spline)
            # Check if point is last point on spline.
            if point == points[-1]:
                # Select first point on next spline.
                if s_idx + 1 > len(curve_obj.data.splines) - 1:
                    points, type = get_points(curve_obj.data.splines[0])
                else:
                    points, type = get_points(curve_obj.data.splines[s_idx + 1])
                point_to_select = points[0]
            # Else get next point on the spline.
            else:
                points, type = get_points(spline)
                point_to_select = points[p_idx + 1]
        else:
            # Select last point
            spline = curve_obj.data.splines[-1]
            points, type = get_points(spline)
            point_to_select = points[-1]

    deselect_all_points(curve_obj)
    select_point_handles(point_to_select, type)


# class VIEW3D_PT_curve_point_select(bpy.types.Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#     bl_category = "Tools"
#     bl_label = 'Curve select'

#     # Poll
#     @classmethod
#     def poll(self, context):
#         if context.object and context.object.type == 'CURVE' and context.object.mode == 'EDIT':
#             return context.object.type

#     # Draw
#     def draw(self, context):
#         layout = self.layout
#         col = layout.column(align=True)
#         col.label(text="Selection")
#         col.operator('curve.select_point', text='Select previous').action = 'PREVIOUS'
#         col.operator('curve.select_point', text='Select next').action = 'NEXT'
#         col.operator('curve.select_point', text='Select first').action = 'FIRST'
#         col.operator('curve.select_point', text='Select last').action = 'LAST'


class CURVE_OT_select_point(bpy.types.Operator):
    """Select the first/last/previous/next point on a curve."""
    bl_idname = "curve.select_point"
    bl_label = "Select point"
    bl_options = {'REGISTER', 'UNDO'}

    select_options = [("PREVIOUS", "Previous", "Select the previous point of the curve. (Or the first one if nothing is selected."),
                      ("NEXT", "Next", "Select the next point of the curve. (Or the last one if nothing is selected."),
                      ("FIRST", "First", "Select the first point of the curve."),
                      ("LAST", "Last", "Select the last point of the curve.")]
    action = EnumProperty(name="Action",
                          description="Choose the select action to use",
                          items=select_options,
                          default="NEXT")

    # Poll
    @classmethod
    def poll(self, context):
        if context.object and context.object.type == 'CURVE' and context.object.mode == 'EDIT':
            return context.object.type

    # Execute
    def execute(self, context):
        # Run main function.
        select_point(self, context)

        return {'FINISHED'}

    # Invoke
    def invoke(self, context, event):
        self.execute(context)

        return {'FINISHED'}


def draw_func(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Selection:")
        col.operator('curve.select_point', text='Select previous').action = 'PREVIOUS'
        col.operator('curve.select_point', text='Select next').action = 'NEXT'
        col.operator('curve.select_point', text='Select first').action = 'FIRST'
        col.operator('curve.select_point', text='Select last').action = 'LAST'


def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('curve.select_point', text='Select last').action = 'LAST'
    layout.operator('curve.select_point', text='Select first').action = 'FIRST'
    layout.operator('curve.select_point', text='Select next').action = 'NEXT'
    layout.operator('curve.select_point', text='Select previous').action = 'PREVIOUS'


# store keymaps here to access after registration
addon_keymaps = []


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_PT_tools_curveedit.append(draw_func)
    bpy.types.VIEW3D_MT_select_edit_curve.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new("Curve")

    km_prev = km.keymap_items.new(
        'curve.select_point',
        'LEFT_BRACKET',
        'PRESS'
        )
    km_prev.properties.action = 'PREVIOUS'

    km_next = km.keymap_items.new(
        'curve.select_point',
        'RIGHT_BRACKET',
        'PRESS'
        )
    km_next.properties.action = 'NEXT'

    km_first = km.keymap_items.new(
        'curve.select_point',
        'LEFT_BRACKET',
        'PRESS',
        shift=True,
        ctrl=True
        )
    km_first.properties.action = 'FIRST'

    km_last = km.keymap_items.new(
        'curve.select_point',
        'RIGHT_BRACKET',
        'PRESS',
        shift=True,
        ctrl=True
        )
    km_last.properties.action = 'LAST'

    # Also add shortcuts for adding the next/previous point to the selection.
    km_add_previous = km.keymap_items.new(
        'curve.select_previous',
        'LEFT_BRACKET',
        'PRESS',
        shift=True
        )

    km_add_next = km.keymap_items.new(
        'curve.select_next',
        'RIGHT_BRACKET',
        'PRESS',
        shift=True
        )

    addon_keymaps.append((km, km_prev))
    addon_keymaps.append((km, km_next))
    addon_keymaps.append((km, km_first))
    addon_keymaps.append((km, km_last))
    addon_keymaps.append((km, km_add_previous))
    addon_keymaps.append((km, km_add_next))


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_PT_tools_curveedit.remove(draw_func)
    bpy.types.VIEW3D_MT_select_edit_curve.remove(menu_func)

    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
