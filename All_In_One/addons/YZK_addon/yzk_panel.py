import bpy
from mathutils import Vector
from itertools import chain #yzk_select_handle

bl_info = {
    "name" : "YZK_panel_addon",
    "author" : "YZK",
    "version" : (1,0),
    "blender" : (2,7),
    "location" : "tools",
    "description" : "YZK tools",
    "warning" : "",
    "wiki_url" : "https://github.com/coverman03/blender",
    "tracker_url" : "https://github.com/coverman03/blender/issues",
    "category" : "3D View"
}


class yzk_CustomProperties(bpy.types.Panel):
    bl_category = "yzk"
    bl_label = "yzk_Modifiers"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"

    # メニューを登録する関数
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)#モディファイア
        row = col.row(align=True)
        row.operator("object.modifier_add",text='mirror', icon='MOD_MIRROR').type='MIRROR'
        row.operator("object.modifier_add",text='subsurf', icon='MOD_SUBSURF').type='SUBSURF'

        row = col.row(align=True)
        row.operator("object.modifier_add",text='multires', icon='MOD_MULTIRES').type='MULTIRES'
        row.operator("object.modifier_add",text='array', icon='MOD_ARRAY').type='ARRAY'

        row = col.row(align=True)
        row.operator("object.modifier_add",text='decimate', icon='MOD_DECIM').type='DECIMATE'
        row.operator("object.modifier_add",text='dataTrans', icon='MOD_DATA_TRANSFER').type='DATA_TRANSFER'
        return {'FINISHED'}

class yzk_CustomPanel1(bpy.types.Panel):
    bl_category = "yzk"
    bl_label = "yzk_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)#ツールシェルフを隠す
        col.operator("view3d.toolshelf", text="Hide Tool Shelf", icon="BACK")

        layout.prop(scene, "camera")
        self.draw_camera_menu(layout)#カメラ

        obj = context.active_object
        if obj is None:#オブジェクト選択判定
            self.draw_add_object(layout)
        else:#オブジェクトタイプを判定
            if obj.type == 'MESH':
                obj = context.active_object
                if obj.mode == "OBJECT":#選択モードを判定
                    self.draw_mesh_object(layout)
                elif obj.mode == "EDIT":
                    self.draw_mesh_edit(layout)
                elif obj.mode == "SCULPT":
                    self.draw_mesh_sculpt(layout)
                elif obj.mode == "VERTEX_PAINT":
                    self.draw_mesh_vertexPaint(layout)
                elif obj.mode == "WEIGHT_PAINT":
                    self.draw_mesh_weightPaint(layout)
                elif obj.mode == "TEXTURE_PAINT":
                    self.draw_mesh_texturePaint(layout)
            elif obj.type == 'CURVE':
                if obj.mode == "OBJECT":
                    self.draw_curve_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    self.draw_curve_edit(layout)
                    print("None")
            elif obj.type == 'SURFACE':
                if obj.mode == "OBJECT":
                    self.draw_surface_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'META':
                if obj.mode == "OBJECT":
                    self.draw_meta_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'FONT':
                if obj.mode == "OBJECT":
                    self.draw_font_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'ARMATURE':
                if obj.mode == "OBJECT":
                    self.draw_armature_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
                elif obj.mode == "POSE":
                    self.draw_armature_pose(layout)
                    print("None")
            elif obj.type == 'LATTICE':
                if obj.mode == "OBJECT":
                    self.draw_lattice_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'EMPTY':
                if obj.mode == "OBJECT":
                    self.draw_empty_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'SPEAKER':
                if obj.mode == "OBJECT":
                    self.draw_speaker_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'CAMERA':
                if obj.mode == "OBJECT":
                    self.draw_acamera_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")
            elif obj.type == 'LAMP':
                if obj.mode == "OBJECT":
                    self.draw_lamp_object(layout)
                    print("None")
                elif obj.mode == "EDIT":
                    print("None")

    def draw_camera_menu(self, layout):
        #col = layout.column(align=True)#ウィンドウ
        #col.operator("yzk.yzk_popup_window", text="duplicateWindow", icon='INFO').areaType="INFO"
        #row = col.row(align=True)
        #row.operator("yzk.yzk_popup_window", text="python", icon='CONSOLE').areaType="CONSOLE"
        #row.operator("yzk.yzk_popup_window", text="text", icon='TEXT').areaType="TEXT_EDITOR"
        #row.operator("yzk.yzk_popup_window", text="user", icon='PREFERENCES').areaType="USER_PREFERENCES"

        #col = layout.column(align=True)
        #row = col.row(align=True)
        #props = row.operator("view3d.viewnumpad",text="camera")
        #props.type = "CAMERA"
        #props.align_active = True

        col = layout.column(align=True)#カメラ
        row = col.row(align=True)
        row.operator("view3d.view_persportho",text='pers/orth', icon='CAMERA_DATA')
        row.operator("view3d.fly")
        #row.operator("view3d.view_all", text="focus", icon='BBOX')

        row = col.row(align=True)
        row.operator("view3d.viewnumpad",text="top").type="TOP"
        row.operator("view3d.viewnumpad",text="bottom").type="BOTTOM"
        row = col.row(align=True)
        row.operator("view3d.viewnumpad",text="front").type="FRONT"
        row.operator("view3d.viewnumpad",text="back").type="BACK"
        row.operator("view3d.viewnumpad",text="right").type="RIGHT"
        row.operator("view3d.viewnumpad",text="left").type="LEFT"
        col.operator("view3d.viewnumpad",text="use_camera").type="CAMERA";

        row = col.row(align=True)
        props = row.operator("view3d.view_roll", text="roll_Left")
        props.angle=-1.5708
        props.type="ANGLE"
        props = row.operator("view3d.view_roll", text="roll_Right")
        props.angle=1.5708
        props.type="ANGLE"

        col = layout.column(align=True)
        col.operator("object.hide_view_clear",text='UnHide_all ')
        return {'FINISHED'}

    def draw_add_object(self, layout):#Addオブジェクト
        col = layout.column(align=True)
        col.menu("INFO_MT_add",text='Add', icon='OBJECT_DATA')
        row = col.row(align=True)
        row.operator("mesh.primitive_cube_add", text='cube', icon='MESH_CUBE')
        #row.operator("mesh.primitive_cylinder_add", text='cylinder', icon='MESH_CYLINDER')
        row.operator("yzk.yzk_apend_cylinder", text='cylinder', icon='MESH_CYLINDER')
        row.operator("yzk.yzk_curve_new", text="curve", icon="CURVE_BEZCURVE")
        return {'FINISHED'}

    def draw_mesh_object(self, layout): #MESH_OBJECT_MODE
        col = layout.column(align=True)
        row = col.row(align=True)#モード選択
        props = row.operator("object.mode_set",text="", icon="OBJECT_DATAMODE")
        props.mode = "OBJECT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="EDITMODE_HLT")
        props.mode = "EDIT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="SCULPTMODE_HLT")
        props.mode = "SCULPT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="TPAINT_HLT")
        props.mode = "TEXTURE_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="VPAINT_HLT")
        props.mode = "VERTEX_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="WPAINT_HLT")
        props.mode = "WEIGHT_PAINT"
        props.toggle = True

        self.draw_add_object(layout)

        col = layout.column(align=True)#オブジェクトモード
        col.menu("VIEW3D_MT_object", icon="OBJECT_DATAMODE")
        col.menu("VIEW3D_MT_master_material", icon="MATERIAL")

        col = layout.column(align=True)#トランスフォーム
        col.menu("VIEW3D_MT_transform_object", icon="MANIPUL")
        row = col.row(align=True)
        row.operator("object.location_clear", text="resetTrans")
        row.operator("object.rotation_clear", text="resetRot")
        row.operator("object.scale_clear", text="resetScale")
        row = col.row(align=True)
        props = row.operator("object.transform_apply" ,text="freezeTrans")
        props.location=True
        props.rotation=False
        props.scale=False
        props = row.operator("object.transform_apply" ,text="freezeRot")
        props.location=False
        props.rotation=True
        props.scale=False
        props = row.operator("object.transform_apply" ,text="freezeScale")
        props.location=False
        props.rotation=False
        props.scale=True
        row = col.row(align=True)
        row.operator("yzk.yzk_copy_transform", text="transform copy")
        props = row.operator("object.transform_apply" ,text="freeze_All")
        props.location=True
        props.rotation=True
        props.scale=True

        col = layout.column(align=True)#カーソル
        row = col.row(align=True)
        row.operator("view3d.snap_cursor_to_center", text="CursorReset", icon="X")
        row.operator("view3d.snap_cursor_to_selected", text="CursorToSelected", icon="CURSOR")
        row = col.row(align=True)
        row.operator("object.origin_set", text="Center", icon="CURSOR").type='ORIGIN_CENTER_OF_MASS'
        props = row.operator("object.origin_set", text="OriginToCursor", icon="CURSOR")
        props.type='ORIGIN_CURSOR'

        col = layout.column(align=True)#スムージング
        row = col.row(align=True)
        #row.operator("object.shade_smooth", text="Smooth")
        row.operator("yzk.yzk_smooth",  text="Smooth2")
        row.operator("object.shade_flat", text="Flat")

        row = col.row(align=True)#デュプリケート
        row.operator("yzk.yzk_duplicate", text="duplicate")
        row.operator("yzk.yzk_instance", text="instance")

        row = col.row(align=True)#Merge
        row.operator("object.join", text="join")
        row.operator("mesh.separate").type='LOOSE'

        col.operator("object.select_grouped").type='GROUP'
        #col = layout.column(align=True)
        #col.operator("object.parent_clear",text='parent_clear').type='CLEAR'

        '''
        col = layout.column(align=True)#モディファイア
        col.operator("object.modifier_add",text='modifier', icon='MODIFIER')
        row = col.row(align=True)
        row.operator("object.modifier_add",text='mirror', icon='MOD_MIRROR').type='MIRROR'
        row.operator("object.modifier_add",text='subsurf', icon='MOD_SUBSURF').type='SUBSURF'

        row = col.row(align=True)
        row.operator("object.modifier_add",text='multires', icon='MOD_MULTIRES').type='MULTIRES'
        row.operator("object.modifier_add",text='array', icon='MOD_ARRAY').type='ARRAY'

        row = col.row(align=True)
        row.operator("object.modifier_add",text='decimate', icon='MOD_DECIM').type='DECIMATE'
        row.operator("object.modifier_add",text='dataTrans', icon='MOD_DATA_TRANSFER').type='DATA_TRANSFER'
        '''

        col = layout.column(align=True)
        col.operator("object.multi_object_uv_edit",text="Multi Object UV Editing",icon="IMAGE_RGB")
        col.menu("object.muv_cpuv_obj_menu")

        col = layout.column(align=True)
        col.operator("yzk.yzk_apply_modifiers_and_join",text='ApplyAllMod')
        col.operator("object.convert",text="convert to curve").target='CURVE'
        col.operator("yzk.yzk_remove_all_materials")

        #削除
        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_mesh_delete")
        col.operator("yzk.yzk_delete")

        #選択解除
        col = layout.column(align=True)
        col.operator("yzk.yzk_mirror_mesh_cleaner", text="yzk_mirror_mesh_cleaner")
        col.operator("yzk.yzk_deselect",text="deselect")
        return{'FINISHED'}

    def draw_mesh_edit(self, layout): #MESH_EDIT
        col = layout.column(align=True)#モード選択
        row = col.row(align=True)
        props = row.operator("object.mode_set",text="", icon="OBJECT_DATAMODE")
        props.mode = "OBJECT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="EDITMODE_HLT")
        props.mode = "EDIT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="SCULPTMODE_HLT")
        props.mode = "SCULPT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="TPAINT_HLT")
        props.mode = "TEXTURE_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="VPAINT_HLT")
        props.mode = "VERTEX_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="WPAINT_HLT")
        props.mode = "WEIGHT_PAINT"
        props.toggle = True

        col = layout.column(align=True)
        col.operator("yzk.yzk_mesh_display_modeling")
        col.operator("yzk.yzk_mesh_display_uvedit")

        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_mesh",icon="EDITMODE_HLT")
        col = layout.column(align=True)
        row = col.row(align=True)
        props = row.operator("transform.resize", text="alignX", icon="MANIPUL")
        props.value = (0,0,0)
        props.constraint_axis=(True, False, False)
        props = row.operator("transform.resize", text="alignY")
        props.value = (0,0,0)
        props.constraint_axis=(False, True, False)
        props = row.operator("transform.resize", text="alignZ")
        props.value = (0,0,0)
        props.constraint_axis=(False, False, True)

        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_mesh_vertices", text='vertex', icon='VERTEXSEL')
        #col.operator_menu_enum("mesh.merge", "type")
        #col.operator("mesh.merge", text="mergeVertex").type='CENTER'
        col.operator("transform.vertex_random")
        #col.operator("yzk.yzk_3dcursor", text="pivotToSelected")
        col.operator("mesh.remove_doubles")
        col.operator("mesh.delete_loose", text="deleteSingleVertex")

        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_mesh_edges", text='edge', icon='EDGESEL')
        #col.operator("mesh.loop_multi_select",text='edge_loop')
        #row = col.row(align=True)
        #row.operator("yzk.yzk_edge_hard",text='hard_edge')
        #row.operator("yzk.yzk_edge_soft",text='soft_edge')
        row = col.row(align=True)
        props = row.operator("mesh.bevel", text='bevel' )
        props.offset_type = "WIDTH"
        props.offset = 1
        props.segments = 1
        props.profile = 1
        props = row.operator("mesh.bevel", text='round' )
        props.offset_type = "WIDTH"
        props.offset = 1
        props.segments = 2
        props.profile = 1
        props = row.operator("mesh.bevel", text='filet' )
        props.offset_type = "WIDTH"
        props.offset = 1
        props.segments = 2
        props.profile = -1
        row = col.row(align=True)
        row.operator("mesh.loopcut_slide")
        row = col.row(align=True)
        props = row.operator("mesh.knife_tool",text='KnifeTool')
        props.use_occlude_geometry = True
        props.only_selected = False
        props = row.operator("mesh.knife_tool",text='KnifeThrough')
        props.use_occlude_geometry = False
        props.only_selected = False
        row = col.row(align=True)
        row.operator("mesh.edge_face_add",text='Fill')
        row.operator("mesh.subdivide")
        row = col.row(align=True)
        row.operator("transform.edge_slide")
        col.operator("yzk.yzk_select_separate_edge", text="selectSepalateEdge")

        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_mesh_faces", text='face', icon='FACESEL')
        col.operator("mesh.flip_normals")
        props = col.operator("mesh.quads_convert_to_tris")
        props.quad_method='BEAUTY'
        props.ngon_method='BEAUTY'
        col.operator("mesh.edge_split",text='edge_split')
        col.operator("mesh.inset")
        col.operator("mesh.destructive_extrude",text="destructive Extrude")
        #row = col.row(align=True)
        #row.operator("view3d.edit_mesh_extrude_move_normal", text="Extrude")
        #row.operator("view3d.edit_mesh_extrude_individual_move", text="Extrude Individual")
        props = col.operator("mesh.separate",text='extruct')
        props.type='SELECTED'
        props = col.operator("mesh.bisect")
        props.plane_co=(0, 0, 0)
        props.plane_no=(-1, 0, 0)
        props.use_fill=False
        props.clear_inner=False
        props.clear_outer=True
        props.xstart=667
        props.xend=667
        props.ystart=883
        props.yend=180

        #削除
        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_mesh_delete")
        col.operator("yzk.yzk_delete")
        col.operator("mesh.dissolve_limited",text='delete_dissolve').angle_limit=180
        return{'FINISHED'}

    def draw_mesh_sculpt(self, layout): #SCULPT_MODE
        col = layout.column(align=True)#モード選択
        row = col.row(align=True)
        props = row.operator("object.mode_set",text="", icon="OBJECT_DATAMODE")
        props.mode = "OBJECT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="EDITMODE_HLT")
        props.mode = "EDIT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="SCULPTMODE_HLT")
        props.mode = "SCULPT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="TPAINT_HLT")
        props.mode = "TEXTURE_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="VPAINT_HLT")
        props.mode = "VERTEX_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="WPAINT_HLT")
        props.mode = "WEIGHT_PAINT"
        props.toggle = True

        toolsettings = context.tool_settings
        brush = bpy.context.tool_settings.sculpt.brush
        ups = context.tool_settings.unified_paint_settings
        sculpt = toolsettings.sculpt

        col = layout.column(align=True)
        col.prop(brush, "sculpt_tool", text="Draw")
        col.prop(brush, "blend", text="Blend")

        col.separator()
        col.prop(ups, "weight")

        col.separator()
        col.prop(ups, "strength")

        col.separator()
        col.prop(brush, "auto_smooth_factor")

        col.separator()
        col.prop(brush, "normal_weight")

        col.separator()
        row = col.row(align=True)
        row.prop(ups, "use_unified_size", text="Unified Size")
        row.prop(ups, "use_unified_strength", text="Unified Strength")

        col.separator()
        col.prop(brush, "stroke_method")

        col.separator()
        col.prop(brush, "spacing")

        col.separator()
        row = col.row(align=True)
        row.label(text="Symmetry")
        row.prop(sculpt, "use_symmetry_x", text="X")
        row.prop(sculpt, "use_symmetry_y", text="Y")
        row.prop(sculpt, "use_symmetry_z", text="Z")
        col.separator()
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Lock")
        row.prop(sculpt, "lock_x", text="X")
        row.prop(sculpt, "lock_y", text="Y")
        row.prop(sculpt, "lock_z", text="Z")
        col.separator()
        col = layout.column(align=True)
        layout.prop(sculpt, "use_threaded", text="Threaded Sculpt")
        layout.prop(sculpt, "show_low_resolution")
        layout.prop(sculpt, "show_brush")
        layout.prop(sculpt, "use_deform_only")
        layout.prop(sculpt, "show_diffuse_color")
        return{'FINISHED'}

    def draw_mesh_vertexPaint(self, layout): #VERTWXPAINT
        col = layout.column(align=True)#モード選択
        row = col.row(align=True)
        props = row.operator("object.mode_set",text="", icon="OBJECT_DATAMODE")
        props.mode = "OBJECT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="EDITMODE_HLT")
        props.mode = "EDIT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="SCULPTMODE_HLT")
        props.mode = "SCULPT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="TPAINT_HLT")
        props.mode = "TEXTURE_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="VPAINT_HLT")
        props.mode = "VERTEX_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="WPAINT_HLT")
        props.mode = "WEIGHT_PAINT"
        props.toggle = True

        col = layout.column(align=True)
        col.menu("VIEW3D_MT_paint_vertex", icon="VPAINT_HLT")
        col.menu("VIEW3D_MT_brush", icon="BRUSH_DATA")
        col.separator()
        #col.operator("wm.context_toggle", text="use_paint_mask", icon="FACESEL_HLT").data_path="object.data.use_paint_mask"
        col.prop(context.active_object.data, 'use_paint_mask', text="use_paint_mask", toggle=True)

        '''
        if context.mode in {'PAIN_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}:
            col.prop(context.active_object.data, 'use_paint_mask', text="use_paint_mask", toggle=True)
            if context.mode =='PAINT_WEIGHT':
                col.prop(context.active_object.data, 'use_paint_mask', text="use_paint_mask", toggle=True)
        '''

        col.operator("paint.vertex_color_set")
        col.separator()
        col.operator("paint.vertex_color_smooth")
        col.operator("paint.vertex_color_dirt")
        return {'FINISHED'}

    def draw_mesh_weightPaint(self, layout): #WEIGHT_PAINT
        col = layout.column(align=True)#モード選択
        row = col.row(align=True)
        props = row.operator("object.mode_set",text="", icon="OBJECT_DATAMODE")
        props.mode = "OBJECT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="EDITMODE_HLT")
        props.mode = "EDIT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="SCULPTMODE_HLT")
        props.mode = "SCULPT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="TPAINT_HLT")
        props.mode = "TEXTURE_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="VPAINT_HLT")
        props.mode = "VERTEX_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="WPAINT_HLT")
        props.mode = "WEIGHT_PAINT"
        props.toggle = True

        toolsettings = context.tool_settings
        brush = bpy.context.tool_settings.sculpt.brush
        ups = context.tool_settings.unified_paint_settings

        col = layout.column(align=True)
        col.menu("VIEW3D_MT_paint_weight", icon="WPAINT_HLT")
        col.separator()
        row = col.row(align=True)
        row.prop(context.active_object.data, 'use_paint_mask', text="mask", toggle=True)
        row.prop(context.active_object.data, 'use_paint_mask_vertex', text="vertex_mask", toggle=True)

        col.separator()
        col.prop(context.scene.palette_props, "weight")
        row = col.row(align=True)
        row.operator("paint.select_weight", text="0.00").weight_index = 0
        row.operator("paint.select_weight", text="1.00").weight_index = 10
        row = col.row(align=True)
        row.operator("paint.select_weight", text="0.10").weight_index = 1
        row.operator("paint.select_weight", text="0.25").weight_index = 2
        row.operator("paint.select_weight", text="0.33").weight_index = 3
        row = col.row(align=True)
        row.operator("paint.select_weight", text="0.40").weight_index = 4
        row.operator("paint.select_weight", text="0.50").weight_index = 5
        row.operator("paint.select_weight", text="0.60").weight_index = 6
        row = col.row(align=True)
        row.operator("paint.select_weight", text="0.67").weight_index = 7
        row.operator("paint.select_weight", text="0.75").weight_index = 8
        row.operator("paint.select_weight", text="0.90").weight_index = 9
        col.operator("paint.reset_weight_palette", text="reset")

        col.separator()
        col.prop(ups, "strength")

        col.separator()
        col.prop(brush, "auto_smooth_factor")

        col.separator()
        col.prop(brush, "normal_weight")

        col.separator()
        row = col.row(align=True)
        row.prop(ups, "use_unified_size", text="Unified Size")
        row.prop(ups, "use_unified_strength", text="Unified Strength")

        col.separator()
        row = col.row(align=True)
        row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
        row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
        row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
        row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
        row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'

        col = layout.column(align=True)
        col.operator("object.vertex_group_normalize_all", text="Normalize All")
        col.operator("object.vertex_group_normalize", text="Normalize")
        col.operator("object.vertex_group_mirror", text="Mirror")
        col.operator("object.vertex_group_invert", text="Invert")
        col.operator("object.vertex_group_clean", text="Clean")
        col.operator("object.vertex_group_quantize", text="Quantize")
        col.operator("object.vertex_group_levels", text="Levels")
        col.operator("object.vertex_group_smooth", text="Smooth")
        col.operator("object.vertex_group_limit_total", text="Limit Total")
        col.operator("object.vertex_group_fix", text="Fix Deforms")
        col.operator("paint.weight_gradient", text="Weight Gradient")
        col.operator("object.data_transfer", text="Transfer Weight")
        return {'FINISHED'}

    def draw_mesh_texturePaint(self, layout): #TEXTURE_PAINT
        col = layout.column(align=True)#モード選択
        row = col.row(align=True)
        props = row.operator("object.mode_set",text="", icon="OBJECT_DATAMODE")
        props.mode = "OBJECT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="EDITMODE_HLT")
        props.mode = "EDIT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="SCULPTMODE_HLT")
        props.mode = "SCULPT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="TPAINT_HLT")
        props.mode = "TEXTURE_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="VPAINT_HLT")
        props.mode = "VERTEX_PAINT"
        props.toggle = True
        props = row.operator("object.mode_set",text="", icon="WPAINT_HLT")
        props.mode = "WEIGHT_PAINT"
        props.toggle = True

        toolsettings = context.tool_settings.image_paint
        brush = toolsettings.brush

        col = layout.column(align=True)
        col.prop(brush, "image_tool", text="Draw")
        col.prop(brush, "blend", text="Blend")

        col = layout.column(align=True)
        col.prop(context.active_object.data, 'use_paint_mask', text="use_paint_mask", toggle=True)
        row = col.row(align=True)
        row.operator("", icon='BRUSH_TEXDRAW')
        row.operator("bpy.data.brushes['Brush'].sculpt_tool = 'SMOOTH'", text="Fill", icon='BRUSH_TEXFILL')
        row.operator("yzk.yzk_smear_tool", text="Smear", icon='BRUSH_SMEAR')
        row = col.row(align=True)
        row.operator("yzk.yzk_blend_mix", text="Mix", icon='BRUSH_DATA')
        row.operator("yzk.yzk_erase_alpha", text="erase", icon='IMAGE_ALPHA' )
        row.operator("yzk.yzk_add_alpha", text="add_alpha")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(brush, "size", "radius")
        row.prop(brush, "use_pressure_size", "")
        row = col.row(align=True)
        row.prop(brush, "strength", "strength")
        row.prop(brush, "use_pressure_strength", "")

        if brush.image_tool == 'FILL':
            row = col.row(align=True)
            row.prop(brush, "fill_threshold")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
        row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
        row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
        row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
        row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(brush, "color", text="")
        row.prop(brush, "secondary_color", text="")
        row.separator()
        row.operator("paint.brush_colors_flip", icon='FILE_REFRESH', text="")

        #col = layout.column(align=True)
        #col.prop(toolsettings, "palette")

        ###palette######################################################
        palette_props = bpy.context.scene.palette_props
        bpy.types.PALETTE_MT_menu.preset_subdir = palette_props.presets_folder

        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("palette_props.add_color", icon="ZOOMIN")
        row.prop(palette_props, "index")
        row.operator("palette_props.remove_color", icon="PANEL_CLOSE")

        row = col.row(align=True)
        row.prop(palette_props, "columns")
        if palette_props.colors.items():
            layout = col.box()

        laycol = layout.column(align=False)

        if palette_props.columns:
            columns = palette_props.columns
        else :
            columns = 16
        for i, color in enumerate(palette_props.colors):
            if not i % columns:
                row1 = laycol.row(align=True)
                row1.scale_y = 0.8
                row2 = laycol.row(align=True)
                row2.scale_y = 0.8

            if i == palette_props.current_color_index:

                row1.prop(palette_props.colors[i], "color", event=True, toggle=True)
                row2.operator("paint.select_color", emboss=False).color_index = i
            else :
                row1.prop(palette_props.colors[i], "color", event=True, toggle=True)
                row2.operator("paint.select_color").color_index = i

        #col = layout.column(align=True)
        #row = col.row(align=True)
        #row.prop(palette_props, "color_name")
        #row.operator("palette_props.sample_tool_color", icon="COLOR")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.menu("PALETTE_MT_menu", text=palette_props.palette_name.rstrip())
        row.operator("palette.preset_add", text="", icon="ZOOMIN")
        row.operator("palette.preset_add", text="", icon="ZOOMOUT").remove_active = True
        layout = self.layout
        row = layout.row()
        col.prop(palette_props, "presets_folder", text="")
        #########################################################

        col = layout.column(align=True)
        col.prop(brush, "stroke_method", text="Stroke")
        col.separator()
        if brush.use_anchor:
            col.prop(brush, "use_edge_to_edge", "Edge To Edge")

        if brush.use_airbrush:
            col.prop(brush, "rate", text="Rate", slider=True)

        if brush.use_space:
            row = col.row(align=True)
            row.prop(brush, "spacing", text="Spacing")
            row.prop(brush, "use_pressure_spacing", toggle=True, text="")

        if brush.use_line or brush.use_curve:
            row = col.row(align=True)
            row.prop(brush, "spacing", text="Spacing")

        if brush.use_curve:
            col.template_ID(brush, "paint_curve", new="paintcurve.new")
            col.operator("paintcurve.draw")

        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(brush, "use_relative_jitter", icon_only=True)
        if brush.use_relative_jitter:
            row.prop(brush, "jitter", slider=True)
        else:
            row.prop(brush, "jitter_absolute")
        row.prop(brush, "use_pressure_jitter", toggle=True, text="")

        col = layout.column()

        if brush.brush_capabilities.has_smooth_stroke:
            col.prop(brush, "use_smooth_stroke")

            sub = col.column()
            sub.active = brush.use_smooth_stroke
            sub.prop(brush, "smooth_stroke_radius", text="Radius", slider=True)
            sub.prop(brush, "smooth_stroke_factor", text="Factor", slider=True)

        col.prop(toolsettings, "input_samples")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(brush, "use_paint_sculpt", text="", icon='SCULPTMODE_HLT')
        row.prop(brush, "use_paint_vertex", text="", icon='VPAINT_HLT')
        row.prop(brush, "use_paint_weight", text="", icon='WPAINT_HLT')
        row.prop(brush, "use_paint_image", text="", icon='TPAINT_HLT')
        return {'FINISHED'}

    def draw_curve_edit(self, layout): #CURVE_EDIT
        col = layout.column(align=True)
        col.menu("VIEW3D_MT_edit_curve",icon="OUTLINER_OB_CURVE")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("curve.spline_type_set", text="poly", icon="IPO_CONSTANT").type='POLY'
        row.operator("curve.spline_type_set", text="bezier", icon="CURVE_BEZCURVE").type='BEZIER'
        row.operator("curve.spline_type_set", text="nurbs", icon="CURVE_NCURVE").type='NURBS'
        row = col.row(align=True)
        row.operator("yzk.yzk_curve_dimensions", text="2D/3D")
        row.operator("curve.cyclic_toggle", text="close")

        col = layout.column(align=True)
        row = col.row(align=True)
        props = row.operator("curve.subdivide",text="subdiv1")
        props.number_cuts = 1
        props = row.operator("curve.subdivide",text="subdiv2")
        props.number_cuts = 2
        props = row.operator("curve.subdivide",text="subdiv3")
        props.number_cuts = 3
        row = col.row(align=True)
        row.operator("curve.switch_direction")
        row.operator("curve.make_segment")
        col.operator("curve.radius_set")

        col = layout.column(align=True)
        col.label(text="Handles:")
        row = col.row(align=True)
        row.operator("yzk.yzk_set_handle", text="Auto").type = 'AUTOMATIC'
        row.operator("yzk.yzk_set_handle", text="Vector").type = 'VECTOR'
        row = col.row(align=True)
        row.operator("yzk.yzk_set_handle", text="Align").type = 'ALIGNED'
        row.operator("yzk.yzk_set_handle", text="Free").type = 'FREE_ALIGN'
        col.operator("yzk.yzk_select_handle", text="getHandle")

        col = layout.column(align=True)
        col.label(text="Modeling:")
        col.operator("curve.extrude_move", text="Extrude")
        col.operator("curve.subdivide")
        col.operator("curve.smooth")
        col.operator("object.vertex_random")
        col.operator("curve.normals_make_consistent")
        return {'FINISHED'}

    def draw_curve_object(self, layout):#CURVE_OBJECT
        #選択解除
        col = layout.column(align=True)
        col.operator("yzk.yzk_deselect",text="deselect")

        col = layout.column(align=True)#トランスフォーム
        col.menu("VIEW3D_MT_transform_object", icon="MANIPUL")
        row = col.row(align=True)
        row.operator("object.location_clear", text="resetTrans")
        row.operator("object.rotation_clear", text="resetRot")
        row.operator("object.scale_clear", text="resetScale")
        row = col.row(align=True)
        props = row.operator("object.transform_apply" ,text="freezeTrans")
        props.location=True
        props.rotation=False
        props.scale=False
        props = row.operator("object.transform_apply" ,text="freezeRot")
        props.location=False
        props.rotation=True
        props.scale=False
        props = row.operator("object.transform_apply" ,text="freezeScale")
        props.location=False
        props.rotation=False
        props.scale=True
        row = col.row(align=True)
        row.operator("yzk.yzk_copy_transform", text="transform copy")
        props = row.operator("object.transform_apply" ,text="freeze_All")
        props.location=True
        props.rotation=True
        props.scale=True

        col = layout.column(align=True)#カーソル
        row = col.row(align=True)
        row.operator("view3d.snap_cursor_to_center", text="CursorReset", icon="X")
        row.operator("view3d.snap_cursor_to_selected", text="CursorToSelected", icon="CURSOR")
        row = col.row(align=True)
        row.operator("object.origin_set", text="Center", icon="CURSOR").type='ORIGIN_CENTER_OF_MASS'
        props = row.operator("object.origin_set", text="OriginToCursor", icon="CURSOR")
        props.type='ORIGIN_CURSOR'

        col = layout.column(align=True)
        col.operator("object.convert",text="convert to mesh").target='MESH'
        return {'FINISHED'}

    def draw_surface_object(self, layout):#SURFACE_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_meta_object(self, layout):#METABALL_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_font_object(self, layout):#FONT_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_armature_object(self, layout):#ARMATURE_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_armature_pose(self, layout): #POSE MODE
        #armature = obj.object.data.use_auto_ik
        col = layout.column(align=True)
        col.menu("VIEW3D_MT_pose", text='pose', icon='POSE_HLT')
        col.prop(obj.data, "use_auto_ik")
        col.operator("pose.transforms_clear",text="clear Pose")
        return {'FINISHED'}

    def draw_lattice_object(self, layout):#LATTICE_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_empty_object(self, layout):#EMPTY_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_speaker_object(self, layout):#SPEAKER_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_camera_object(self, layout):#CAMERA_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}

    def draw_lamp_object(self, layout):#LAMP_OBJECT
        self.draw_add_object(layout)
        return {'FINISHED'}




class yzk_CustomPanel5(bpy.types.Panel):
    bl_label = "show/hide"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "yzk"

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.object
        if obj is not None and obj.type == 'MESH' and obj.mode == "EDIT":
            col = layout.column(align=True)
            col.menu("VIEW3D_MT_edit_mesh_showhide")
            col.operator("mesh.reveal",text='Show_all (Shift+A)')
            col.operator("mesh.hide",text='Hide_selected (Ctrl+H)').unselected=False
            col.operator("mesh.hide",text='Hide_Unselected (Alt+H)').unselected=True
        else:
            col = layout.column(align=True)
            col.menu("Show/Hide")
            col.menu("VIEW3D_MT_object_showhide")
            col.operator("object.hide_view_clear",text='Show_all (Shift+A)')
            col.operator("object.hide_view_set",text='Hide_selected (Ctrl+H)').unselected=False
            col.operator("object.hide_view_set",text='Hide_Unselected (Alt+H)').unselected=True

class yzk2_CustomPanel1(bpy.types.Panel):
    bl_label = "oldTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "old"

    def draw(self, context):
        layout = self.layout

        obj = bpy.context.object
        layout.label(text="modeSelect")
        col = layout.column(align=True)
        col.operator("object.mode_set", text='objectMode', icon='OBJECT_DATAMODE').mode='OBJECT'
        col.operator("object.mode_set", text='editMode', icon='EDITMODE_HLT').mode='EDIT'

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("view3d.fly",text='fly')
        row.operator("view3d.walk", text="walk")

        layout.label(text="callMenu")
        col = layout.column(align=True)
        col.operator("wm.call_menu").name='INFO_MT_add'
        col.operator("wm.call_menu",text='addMeshMenu').name="INFO_MT_mesh_add"
        col.operator("wm.call_menu",text='addCurveMenu', icon='OUTLINER_OB_CURVE').name="INFO_MT_curve_add"
        col.operator("wm.call_menu",text='addSurfaceMenu', icon='OUTLINER_OB_SURFACE').name="INFO_MT_surface_add"
        col.operator("object.metaball_add",text='metaBall', icon='OUTLINER_OB_META')
        col.operator("object.text_add",text='addTextMenu', icon='OUTLINER_OB_FONT')
        col.operator("object.add",text='addLatticeMenu', icon='OUTLINER_OB_LATTICE').type='LATTICE'
        col.operator("wm.call_menu",text='addArmatureMenu', icon='OUTLINER_OB_ARMATURE').name="INFO_MT_armature_add"
        col.operator("object.empty_add",text='addEmptyMenu', icon='OUTLINER_OB_EMPTY')
        col.operator("object.lamp_add",text="addLampMenu", icon='OUTLINER_OB_LAMP')

        layout.label(text="addPrimitive")
        col = layout.column(align=True)
        col.menu("INFO_MT_add")
        col.menu("INFO_MT_mesh_add")
        row = col.row(align=True)
        row.operator("mesh.primitive_cube_add", text='cube', icon='MESH_CUBE')
        row.operator("mesh.primitive_cylinder_add", text='cylinder', icon='MESH_CYLINDER')
        row = col.row(align=True)
        row.operator("mesh.primitive_uv_sphere_add",text='sphere', icon='MESH_UVSPHERE')

        col.menu("INFO_MT_metaball_add")
        row = col.row(align=True)
        row.operator("object.metaball_add",text='metaBall', icon='META_BALL').type='BALL'
        row.operator("object.metaball_add",text='metaBall', icon='META_ELLIPSOID').type='ELLIPSOID'

        col.menu("INFO_MT_curve_add")
        row = col.row(align=True)
        row.operator("curve.primitive_nurbs_path_add", text='path',icon='CURVE_PATH')
        row.operator("curve.primitive_nurbs_circle_add",text='circle', icon='CURVE_NCIRCLE')

        row = layout.row(align=True)
        row.menu("INFO_MT_mesh_add")
        row.menu("INFO_MT_curve_add")
        row.operator("wm.call_menu",text="surfaceMenu", icon='OUTLINER_OB_SURFACE').name="INFO_MT_surface_add"
        row.menu("OUTLINER_OB_META")
        row.operator("object.text_add",text='textMenu', icon='OUTLINER_OB_FONT')
        row.operator("object.add",text='latticeMenu', icon='OUTLINER_OB_LATTICE').type='LATTICE'
        row.operator("wm.call_menu",text='armatureMenu', icon='OUTLINER_OB_ARMATURE').name="INFO_MT_armature_add"
        row.operator("object.empty_add",text='emptyMenu', icon='OUTLINER_OB_EMPTY')
        row.operator("object.lamp_add",text="lampMenu", icon='OUTLINER_OB_LAMP')
        return {'FINISHED'}




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
    bpy.utils.register_class(yzk_CustomProperties)
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
    bpy.utils.register_class(yzk_CustomPanel1)
    bpy.utils.register_class(yzk2_CustomPanel1)
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
    bpy.utils.unregister_class(yzk_CustomProperties)
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
    bpy.utils.unregister_class(yzk_CustomPanel1)
    bpy.utils.unregister_class(yzk2_CustomPanel1)
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
