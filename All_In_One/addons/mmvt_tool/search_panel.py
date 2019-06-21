import bpy
import os.path as op
import mmvt_utils as mu
import mathutils
import numpy as np


def _addon():
    return SearchPanel.addon


class SearchFilter(bpy.types.Operator):
    bl_idname = "mmvt.selection_filter"
    bl_label = "selection filter"
    bl_description = 'Search'
    bl_options = {"UNDO"}
    marked_objects_select = {}
    marked_objects = []

    def invoke(self, context, event=None):
        label_name = context.scene.labels_regex
        SearchMark.marked_objects_select = {}
        objects = mu.get_non_functional_objects()
        SearchPanel.marked_objects = []
        for obj in objects:
            SearchFilter.marked_objects_select[obj.name] = obj.select
            obj.select = label_name in obj.name
            try:
                import fnmatch
                if fnmatch.fnmatch(obj.name, '*{}*'.format(label_name)):
                    SearchPanel.marked_objects.append(obj.name)
            except:
                if label_name in obj.name:
                    SearchPanel.marked_objects.append(obj.name)
        if len(SearchPanel.marked_objects) == 0:
            print('No objects found for "{}"'.format(context.scene.labels_regex))
            return
        # todo: show rois only if the object is an ROI. Also, move the cursor
        selected_obj = bpy.data.objects[SearchPanel.marked_objects[0]]
        verts = np.array([vert.co for vert in selected_obj.data.vertices])
        center = np.mean(verts, axis=0)
        if any([mu.obj_is_cortex(o) for o in SearchPanel.marked_objects]):
            selected_roi = [o for o in SearchPanel.marked_objects if mu.obj_is_cortex(o)][0]
            hemi = mu.get_obj_hemi(selected_roi)
            center = _addon().where_am_i.pos_to_current_inflation(center, hemis=[hemi])
        else:
            center = mathutils.Vector(center) * mu.get_matrix_world()
            # if bpy.context.scene.search_plot_contour:
            #     _addon().where_am_i.plot_closest_label_contour(selected_roi, hemi)
        bpy.context.scene.cursor_location = tuple(center)
        _addon().set_cursor_pos()
        _addon().set_tkreg_ras(bpy.context.scene.cursor_location * 10, False)
        if bpy.context.scene.slices_rotate_view_on_click:
            mu.rotate_view_to_vertice()
        # if any([mu.obj_is_cortex(o.name) for o in SearchPanel.marked_objects]):
            # SearchPanel.addon.show_rois()
        return {"FINISHED"}


class SearchClear(bpy.types.Operator):
    bl_idname = "mmvt.selection_clear"
    bl_label = "selection clear"
    bl_description = 'Clear'
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        # Copy from where am I clear
        _addon.selection.clear_selection()
        for obj_name, h in SearchMark.marked_objects_hide.items():
            bpy.data.objects[obj_name].hide = bool(h)
        for obj_name, h in SearchFilter.marked_objects_select.items():
            # print('bpy.data.objects[{}].select = {}'.format(obj_name, bool(h)))
            bpy.data.objects[obj_name].select = bool(h)

        SearchPanel.marked_objects = []
        return {"FINISHED"}


class SearchMark(bpy.types.Operator):
    bl_idname = "mmvt.selection_mark"
    bl_label = "selection mark"
    bl_options = {"UNDO"}
    marked_objects_hide = {}
    marked_objects = []

    def invoke(self, context, event=None):
        label_name = context.scene.labels_regex
        SearchMark.marked_objects_hide = {}
        objects = mu.get_non_functional_objects()
        SearchPanel.marked_objects = []
        for obj in objects:
            is_valid = False
            try:
                import fnmatch
                if fnmatch.fnmatch(obj.name, '*{}*'.format(label_name)):
                    is_valid = True
            except:
                if label_name in obj.name:
                    is_valid = True
            if is_valid:
                bpy.context.scene.objects.active = bpy.data.objects[obj.name]
                bpy.data.objects[obj.name].select = True
                SearchMark.marked_objects_hide[obj.name] = bpy.data.objects[obj.name].hide
                bpy.data.objects[obj.name].hide = False
                # todo: mark the object in a different way
                # bpy.data.objects[obj.name].active_material = bpy.data.materials['selected_label_Mat']
                SearchPanel.marked_objects.append(obj.name)
                # bpy.data.objects['inflated_'+obj.name].select = True
        SearchPanel.addon.show_rois()
        return {"FINISHED"}


class SearchExport(bpy.types.Operator):
    bl_idname = "mmvt.search_export"
    bl_label = "selection export"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        with open(op.join(mu.get_user_fol(), 'search_panel.txt'), 'w') as text_file:
            for obj_name in SearchPanel.marked_objects:
                print(obj_name, file=text_file)
        print('List was saved to {}'.format(op.join(mu.get_user_fol(), 'search_panel.txt')))
        return {"FINISHED"}


bpy.types.Scene.labels_regex = bpy.props.StringProperty(default= '', description='Searches all objects types in MMVT')
bpy.types.Scene.search_plot_contour = bpy.props.BoolProperty(default=False,
    description='Plot the contour of first label found')


class SearchPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Search Panel"
    addon = None
    init = False
    marked_objects = []

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=0)
        row.prop(context.scene, "labels_regex", text="")
        # row.prop(context.scene, "search_plot_contour", text="Plot contour")
        # row = layout.row(align=0)
        layout.operator(SearchFilter.bl_idname, text="Search", icon='BORDERMOVE')
        # row.operator(SearchMark.bl_idname, text="Mark", icon = 'GREASEPENCIL')
        if len(SearchPanel.marked_objects) > 0:
            box = layout.box()
            col = box.column()
            for obj_name in SearchPanel.marked_objects:
                mu.add_box_line(col, obj_name, percentage=1)
        layout.operator(SearchClear.bl_idname, text="Clear", icon='PANEL_CLOSE')
            # row = layout.row(align=0)
            # row.operator(SearchExport.bl_idname, text="Export list", icon = 'FORCE_LENNARDJONES')


def init(addon):
    SearchPanel.addon = addon
    bpy.context.scene.labels_regex = ''
    SearchPanel.init = True
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(SearchPanel)
        bpy.utils.register_class(SearchMark)
        bpy.utils.register_class(SearchClear)
        bpy.utils.register_class(SearchFilter)
        bpy.utils.register_class(SearchExport)
        # print('Search Panel was registered!')
    except:
        print("Can't register Search Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(SearchPanel)
        bpy.utils.unregister_class(SearchMark)
        bpy.utils.unregister_class(SearchClear)
        bpy.utils.unregister_class(SearchFilter)
        bpy.utils.unregister_class(SearchExport)
    except:
        pass
        # print("Can't unregister Search Panel!")

