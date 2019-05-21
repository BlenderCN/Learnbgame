import bpy
from mathutils import Vector
from itertools import chain #yzk_select_handle

class yzk_popup_window(bpy.types.Operator):
    bl_idname = "yzk.yzk_popup_window"
    bl_label = "yzk_popup_window"
    areaType = bpy.props.StringProperty()

    def execute(self, context):
        currentAreaType = bpy.context.area.type
        bpy.context.area.type = self.areaType
        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        bpy.context.area.type = currentAreaType
        return {'FINISHED'}

class yzk_select_edit_mode_vert(bpy.types.Operator):
    bl_idname = "yzk.yzk_select_edit_mode_vert"
    bl_label = "yzk_select_edit_mode_vert"

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and obj.type == 'MESH':
            if bpy.context.object.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type="VERT")
        return {'FINISHED'}

class yzk_select_edit_mode_edge(bpy.types.Operator):
    bl_idname = "yzk.yzk_select_edit_mode_edge"
    bl_label = "yzk_select_edit_mode_edge"

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and obj.type == 'MESH':
            if bpy.context.object.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
        return {'FINISHED'}

class yzk_select_edit_mode_face(bpy.types.Operator):
    bl_idname = "yzk.yzk_select_edit_mode_face"
    bl_label = "yzk_select_edit_mode_face"

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and obj.type == 'MESH':
            if bpy.context.object.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type="FACE")
        return {'FINISHED'}

class yzk_select_separate_edge(bpy.types.Operator):
    bl_idname = "yzk.yzk_select_separate_edge"
    bl_label = "yzk_select_separate_edge"

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and obj.type == 'MESH':
            if bpy.context.object.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()
        return {'FINISHED'}


class yzk_object_mode(bpy.types.Operator):
    bl_idname = "yzk.yzk_object_mode"
    bl_label = "yzk_object_mode"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.context.object

        if obj is not None and obj.type in {'MESH', 'CURVE', 'SURFACE','META','FONT','ARMATURE','LATTICE'}:
            if obj.mode == 'OBJECT':
                bpy.ops.object.select_all(action='INVERT')
                bpy.ops.object.select_all(action='INVERT')
                bpy.ops.object.mode_set(mode = 'EDIT')
            elif obj.mode in {'EDIT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'SCULPT', 'VERTEX_PAINT', 'POSE'}:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='INVERT')
                bpy.ops.object.select_all(action='INVERT')
        return {'FINISHED'}

class yzk_outliner_mode(bpy.types.Operator):
    bl_idname = "yzk.yzk_outliner_mode"
    bl_label = "yzk_outliner_mode"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.context.object
        display_mode = bpy.context.space_data.display_mode

        if obj is not None:
            if display_mode == 'SELECTED':
                bpy.ops.wm.context_set_enum(data_path="space_data.display_mode", value="VISIBLE_LAYERS")
            else:
                bpy.ops.wm.context_set_enum(data_path="space_data.display_mode", value="SELECTED")
        return {'FINISHED'}

class yzk_show_isolate(bpy.types.Operator):
    bl_idname = "yzk.yzk_show_isolate"
    bl_label = "yzk_show_isolate"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.context.scene.objects.active
        if obj.mode == 'OBJECT':
            bpy.ops.object.hide_view_clear()
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.ops.object.hide_view_set(unselected=True)
            obj.select = True
        return {'FINISHED'}


class yzk_delete(bpy.types.Operator):
    bl_idname = "yzk.yzk_delete"
    bl_label = "yzk_delete"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.context.object
        if obj.mode == 'OBJECT':
            bpy.ops.object.delete()
        elif obj.mode == 'EDIT':
            if bpy.context.tool_settings.mesh_select_mode[0] == True: #vertex
                bpy.ops.mesh.delete(type='VERT')
            elif bpy.context.tool_settings.mesh_select_mode[1] == True: #edge
                #bpy.ops.mesh.delete(type='EDGE')
                bpy.ops.mesh.dissolve_limited(angle_limit=180.00)
            elif bpy.context.tool_settings.mesh_select_mode[2] == True: #face
                bpy.ops.mesh.delete(type='FACE')
        return {'FINISHED'}

class yzk_deselect(bpy.types.Operator):
    bl_idname = "yzk.yzk_deselect"
    bl_label = "yzk_deselect"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.scene.objects.active = None
        return {'FINISHED'}


class yzk_duplicate(bpy.types.Operator):
    bl_idname = "yzk.yzk_duplicate"
    bl_label = "yzk_duplicate"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.object.duplicate(linked=False)
        return {'FINISHED'}

class yzk_instance(bpy.types.Operator):
    bl_idname = "yzk.yzk_instance"
    bl_label = "yzk_instance"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.object.duplicate(linked=True)
        return {'FINISHED'}

class yzk_edge_soft(bpy.types.Operator):
    bl_idname = "yzk.yzk_edge_soft"
    bl_label = "yzk_soft"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.transform.edge_bevelweight(value=-1.0)
        bpy.ops.transform.edge_crease(value=-1.0)
        return {'FINISHED'}

class yzk_edge_hard(bpy.types.Operator):
    bl_idname = "yzk.yzk_edge_hard"
    bl_label = "yzk_hard"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.mesh.mark_sharp(clear=False)
        bpy.ops.transform.edge_bevelweight(value=1)
        bpy.ops.transform.edge_crease(value=1.0)
        return {'FINISHED'}

class yzk_snap_to_vertex_on(bpy.types.Operator):
    bl_idname = "yzk.yzk_snap_to_vertex_on"
    bl_label = "yzk_snap_to_vertex_on"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        bpy.context.scene.tool_settings.use_snap = True
        return {'FINISHED'}

class yzk_snap_to_vertex_off(bpy.types.Operator):
    bl_idname = "yzk.yzk_snap_to_vertex_off"
    bl_label = "yzk_snap_to_vertex_off"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        bpy.context.scene.tool_settings.use_snap = False
        return {'FINISHED'}

class yzk_snap_vertex_toggle(bpy.types.Operator):
    bl_idname = "yzk.yzk_snap_vertex_toggle"
    bl_label = "yzk_snap_vertex_toggle"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_element = 'VERTEX'
        snap = bpy.context.scene.tool_settings.use_snap
        if snap == False:
            bpy.context.scene.tool_settings.use_snap = True
        else:
            bpy.context.scene.tool_settings.use_snap = False
        return {'FINISHED'}

class yzk_3dcursor(bpy.types.Operator):
    bl_idname = "yzk.yzk_3dcursor"
    bl_label = "yzk_3dcursor"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.context.object
        if obj.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        elif obj.mode == 'EDIT':
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

class yzk_manipulator_size_plus(bpy.types.Operator):
    bl_idname = "yzk.yzk_manipulator_size_plus"
    bl_label = "yzk_manipulator_size_plus"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.user_preferences.view.manipulator_size += 10
        return {'FINISHED'}

class yzk_manipulator_size_minus(bpy.types.Operator):
    bl_idname = "yzk.yzk_manipulator_size_minus"
    bl_label = "yzk_manipulator_size_minus"
    editType = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.user_preferences.view.manipulator_size -= 10
        return {'FINISHED'}

class yzk_curve_new(bpy.types.Operator):
    bl_idname = "yzk.yzk_curve_new"
    bl_label = "yzk_curve_new"

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and not obj.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.curve.primitive_bezier_curve_add()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.delete(type='VERT')
        return {'FINISHED'}

class yzk_smooth(bpy.types.Operator):
    bl_idname = "yzk.yzk_smooth"
    bl_label = "yzk_smooth"

    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 3.14159
        return {'FINISHED'}

class yzk_select_handle(bpy.types.Operator):
    bl_idname = "yzk.yzk_select_handle"
    bl_label = "yzk_select_handle"

    def execute(self, context):
        obj = bpy.context.object
        curve = obj.data # Assumed that obj.type == 'CURVE'
        obj.update_from_editmode() # Loads edit-mode data into object data

        selected_cpoints = [p for p in chain(*[s.bezier_points for s in curve.splines])
                            if p.select_control_point]

        #bpy.ops.curve.select_all(action='DESELECT')
        for cp in selected_cpoints:
            cp.select_control_point = True
            cp.select_left_handle = True
            cp.select_right_handle = True
        return {'FINISHED'}

class yzk_set_handle(bpy.types.Operator):
    bl_idname = "yzk.yzk_set_handle"
    bl_label = "yzk_set_handle"
    type = bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.yzk.yzk_select_handle()
        if self.type == "AUTOMATIC":
            bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        elif self.type == "VECTOR":
            bpy.ops.curve.handle_type_set(type='VECTOR')
        elif self.type == "ALIGNED":
            bpy.ops.curve.handle_type_set(type='ALIGNED')
        elif self.type == "FREE":
            bpy.ops.curve.handle_type_set(type='FREE')
        return {'FINISHED'}

class yzk_copy_transform(bpy.types.Operator):
    bl_idname = "yzk.yzk_copy_transform"
    bl_label = "yzk_copy_transform"
    type = bpy.props.StringProperty()

    def execute(self, context):
        matrix_world = bpy.context.object.matrix_world
        for obj in bpy.context.selected_objects:
            #if obj.type == "MESH":
            bpy.context.scene.objects.active = obj
            obj.matrix_world  = matrix_world
        return {'FINISHED'}

class yzk_curve_dimensions(bpy.types.Operator):
    bl_idname = "yzk.yzk_curve_dimensions"
    bl_label = "yzk_curve_dimensions"

    def execute(self, context):
        obj = bpy.context.object
        if obj.data.dimensions == '2D':
            bpy.context.object.data.dimensions = '3D'
        else:
            bpy.context.object.data.dimensions = '2D'
        return{'FINISHED'}

class yzk_set_screen(bpy.types.Operator):
    bl_idname = "yzk.yzk_set_screen"
    bl_label = "yzk_set_screen"
    screenNum = bpy.props.IntProperty()

    def execute(self, context):
        screenList = bpy.data.screens
        str_currentScreen = bpy.context.screen.name
        str_targetScreen = "scripting"

        int_currentScreen = 0
        int_targetScreen = self.screenNum

        i=0
        for var in screenList:
            if var.name == str_currentScreen:
                int_currentScreen = i
            i=i+1

        i=0
        for var in screenList:
            if i == int_targetScreen:
                print(var.name)
                print(i)
            i=i+1

        int_delta = int_targetScreen - int_currentScreen
        print(int_currentScreen)
        print(int_delta)

        if int_delta < 0:
            int_delta_a = int_delta * (-1)
            i=0
            for i in range(0,int_delta_a):
                bpy.ops.screen.screen_set(delta=-1)
                i=i+1
        elif int_delta > 0:
            i=0
            for i in range(0,int_delta):
                bpy.ops.screen.screen_set(delta=1)
                i=i+1
        elif int_delta == 0:
            print("screenDelta=0")

        return {'FINISHED'}

class yzk_apply_modifiers_and_join(bpy.types.Operator):
    bl_idname = "yzk.yzk_apply_modifiers_and_join"
    bl_label = "yzk_apply_modifiers_and_join"
    bl_description = "apply all modifiers"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pre_active_object = context.active_object
        for obj in context.selected_objects:
            bpy.context.scene.objects.active = obj
            for mod in obj.modifiers[:]:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        for obj in context.selected_objects:
            bpy.context.scene.objects.active = obj
            context.scene.objects.active = pre_active_object
            bpy.ops.object.join()
        return {'FINISHED'}


class yzk_remove_all_materials(bpy.types.Operator):
    bl_idname = "yzk.yzk_remove_all_materials"
    bl_label = "yzk_remove_all_materials"
    bl_description = "remove all materials"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pre_active_object = context.active_object
        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})
        return {'FINISHED'}


class yzk_clean_bool_objects(bpy.types.Operator):
    bl_idname = "yzk.yzk_clean_bool_objects"
    bl_label = "yzk_clean_bool_objects"
    bl_description = "yzk_clean_bool_objects"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pre_active_object = context.active_object
        for obj in bpy.context.selected_editable_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(type='VERT')
            bpy.ops.mesh.select_all()
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class yzk_update_addon(bpy.types.Operator):
    bl_idname = "yzk.yzk_update_addon"
    bl_label = "yzk_update_addon"
    bl_description = "Update YZK_panel addon"
    bl_options = {'REGISTER'}

    def execute(self, context):
        response = urllib.request.urlopen("https://github.com/coverman03/blender/archive/master.zip")
        tempDir = bpy.app.tempdir
        zipPath = tempDir + r"\blender-master.zip"
        addonDir = os.path.dirname(__file__)
        f = open(zipPath, "wb")
        f.write(response.read())
        f.close()
        zf = zipfile.ZipFile(zipPath, "r")
        for f in zf.namelist():
            if not os.path.basename(f):
                pass
            else:
                if ("blender_master/python/bpy/" in f):
                    uzf = open(addonDir +"\\"+ os.path.basename(f), 'wb')
                    uzf.write(zf.read(f))
                    uzf.close()
        zf.close()
        self.report(type={"INFO"}, message="revote blender")
        return {'FINISHED'}


class yzk_material_remove(bpy.types.Operator):
    bl_idname = "yzk.yzk_material_remove"
    bl_label = "yzk_material_remove"
    bl_description = "yzk_material_remove"
    bl_options = {'REGISTER'}

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                materials.remove(material)
        return {'FINISHED'}

class yzk_mesh_display_modeling(bpy.types.Operator):
    bl_idname = "yzk.yzk_mesh_display_modeling"
    bl_label = "display_modeling"
    bl_description = "yzk_mesh_display_modeling"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.context.object.data.show_faces = True
        bpy.context.object.data.show_edges = True
        bpy.context.object.data.show_edge_crease = True
        bpy.context.object.data.show_edge_seams = False
        bpy.context.object.data.show_weight = False
        bpy.context.object.data.show_edge_sharp = True
        bpy.context.object.data.show_edge_bevel_weight = False
        bpy.context.object.data.show_freestyle_edge_marks = False
        bpy.context.object.data.show_freestyle_face_marks = False
        bpy.context.object.data.show_normal_vertex = False
        bpy.context.object.data.show_normal_loop = False
        bpy.context.object.data.show_normal_face = True
        return {'FINISHED'}

class yzk_mesh_display_uvedit(bpy.types.Operator):
    bl_idname = "yzk.yzk_mesh_display_uvedit"
    bl_label = "display_UV"
    bl_description = "yzk_mesh_display_uvedit"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.context.object.data.show_faces = True
        bpy.context.object.data.show_edges = True
        bpy.context.object.data.show_edge_crease = False
        bpy.context.object.data.show_edge_seams = True
        bpy.context.object.data.show_weight = False
        bpy.context.object.data.show_edge_sharp = False
        bpy.context.object.data.show_edge_bevel_weight = False
        bpy.context.object.data.show_freestyle_edge_marks = False
        bpy.context.object.data.show_freestyle_face_marks = False
        bpy.context.object.data.show_normal_vertex = False
        bpy.context.object.data.show_normal_loop = False
        bpy.context.object.data.show_normal_face = False
        return {'FINISHED'}

class yzk_mirror_mesh_cleaner(bpy.types.Operator):
    bl_idname = "yzk.yzk_mirror_mesh_cleaner"
    bl_label = "yzk_mirror_mesh_cleaner"
    bl_description = "yzk_mirror_mesh_cleaner"
    bl_options = {'REGISTER'}

    def execute(self, context):
        #ポリゴンセンターを取得
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        f_level = 4 #小数点精度
        src_list = []

        bpy.context.selected_objects[1].data.name
        for poly in bpy.context.selected_objects[1].data.polygons:
        	src_list.append(Vector((round(poly.center[0], f_level), round(poly.center[1], f_level), round(poly.center[2], f_level))))

        bpy.context.selected_objects[0].data.name
        for tgt in bpy.context.selected_objects[0].data.polygons:
        	for src in src_list:
        		if src == Vector((round(tgt.center[0], f_level), round(tgt.center[1], f_level), round(tgt.center[2], f_level))):
        			tgt.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.select_all(action='INVERT')
        #bpy.ops.mesh.delete(type='FACE')
        #bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class yzk_apend_cylinder(bpy.types.Operator):
    bl_idname = "yzk.yzk_apend_cylinder"
    bl_label = "yzk_apend_cylinder"
    bl_description = "yzk_apend_cylinder"
    bl_options = {'REGISTER'}

    def execute(self, context):
        blendfile = "D:/googleDrive/3dcg/blender/base/Cylinder.blend"
        section   = "\\Object\\"
        object    = "Cylinder"

        filepath  = blendfile + section + object
        directory = blendfile + section
        filename  = object

        bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(yzk_popup_window)
    bpy.utils.register_class(yzk_select_edit_mode_vert)
    bpy.utils.register_class(yzk_select_edit_mode_edge)
    bpy.utils.register_class(yzk_select_edit_mode_face)
    bpy.utils.register_class(yzk_select_separate_edge)
    bpy.utils.register_class(yzk_object_mode)
    bpy.utils.register_class(yzk_outliner_mode)
    bpy.utils.register_class(yzk_delete)
    bpy.utils.register_class(yzk_deselect)
    bpy.utils.register_class(yzk_duplicate)
    bpy.utils.register_class(yzk_instance)
    bpy.utils.register_class(yzk_edge_soft)
    bpy.utils.register_class(yzk_edge_hard)
    bpy.utils.register_class(yzk_snap_vertex_toggle)
    bpy.utils.register_class(yzk_snap_to_vertex_on)
    bpy.utils.register_class(yzk_snap_to_vertex_off)
    bpy.utils.register_class(yzk_3dcursor)
    bpy.utils.register_class(yzk_manipulator_size_plus)
    bpy.utils.register_class(yzk_manipulator_size_minus)
    bpy.utils.register_class(yzk_curve_new)
    bpy.utils.register_class(yzk_show_isolate)
    bpy.utils.register_class(yzk_select_handle)
    bpy.utils.register_class(yzk_set_handle)
    bpy.utils.register_class(yzk_smooth)
    bpy.utils.register_class(yzk_copy_transform)
    bpy.utils.register_class(yzk_curve_dimensions)
    bpy.utils.register_class(yzk_set_screen)
    bpy.utils.register_class(yzk_apply_modifiers_and_join)
    bpy.utils.register_class(yzk_clean_bool_objects)
    bpy.utils.register_class(yzk_remove_all_materials)
    bpy.utils.register_class(yzk_update_addon)
    bpy.utils.register_class(yzk_material_remove)
    bpy.utils.register_class(yzk_mesh_display_modeling)
    bpy.utils.register_class(yzk_mesh_display_uvedit)
    bpy.utils.register_class(yzk_mirror_mesh_cleaner)
    bpy.utils.register_class(yzk_apend_cylinder)

def unregister():
    bpy.utils.unregister_class(yzk_popup_window)
    bpy.utils.unregister_class(yzk_select_edit_mode_vert)
    bpy.utils.unregister_class(yzk_select_edit_mode_edge)
    bpy.utils.unregister_class(yzk_select_edit_mode_face)
    bpy.utils.unregister_class(yzk_select_separate_edge)
    bpy.utils.unregister_class(yzk_object_mode)
    bpy.utils.unregister_class(yzk_outliner_mode)
    bpy.utils.unregister_class(yzk_delete)
    bpy.utils.unregister_class(yzk_deselect)
    bpy.utils.unregister_class(yzk_duplicate)
    bpy.utils.unregister_class(yzk_instance)
    bpy.utils.unregister_class(yzk_edge_soft)
    bpy.utils.unregister_class(yzk_edge_hard)
    bpy.utils.unregister_class(yzk_snap_vertex_toggle)
    bpy.utils.unregister_class(yzk_snap_to_vertex_on)
    bpy.utils.unregister_class(yzk_snap_to_vertex_off)
    bpy.utils.unregister_class(yzk_3dcursor)
    bpy.utils.unregister_class(yzk_manipulator_size_plus)
    bpy.utils.unregister_class(yzk_manipulator_size_minus)
    bpy.utils.unregister_class(yzk_curve_new)
    bpy.utils.unregister_class(yzk_show_isolate)
    bpy.utils.unregister_class(yzk_select_handle)
    bpy.utils.unregister_class(yzk_set_handle)
    bpy.utils.unregister_class(yzk_smooth)
    bpy.utils.unregister_class(yzk_copy_transform)
    bpy.utils.unregister_class(yzk_curve_dimensions)
    bpy.utils.unregister_class(yzk_set_screen)
    bpy.utils.unregister_class(yzk_apply_modifiers_and_join)
    bpy.utils.unregister_class(yzk_clean_bool_objects)
    bpy.utils.unregister_class(yzk_remove_all_materials)
    bpy.utils.unregister_class(yzk_update_addon)
    bpy.utils.unregister_class(yzk_material_remove)
    bpy.utils.unregister_class(yzk_mesh_display_modeling)
    bpy.utils.unregister_class(yzk_mesh_display_uvedit)
    bpy.utils.unregister_class(yzk_mirror_mesh_cleaner)
    bpy.utils.unregister_class(yzk_apend_cylinder)

if __name__ == "__main__":
    register()
