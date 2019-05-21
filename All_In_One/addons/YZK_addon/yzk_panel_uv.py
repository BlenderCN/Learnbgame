import bpy

bl_info = {
    "name" : "YZK_panel_uv_addon",
    "author" : "YZK",
    "version" : (1,0),
    "blender" : (2, 7),
    "location" : "tools",
    "description" : "UVEditAddon",
    "warning" : "",
    "wiki_url" : "https://github.com/coverman03/blender",
    "tracker_url" : "https://github.com/coverman03/blender/issues",
    "category" : "3D View"
}

class yzk_uvtools(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "yzk"
    bl_label = "yzk_uvtools"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("image.toolshelf", text="Hide Tool Shelf", icon="BACK")

        col = layout.column(align=True)
        col.operator("yzk.yzk_packimg",text="images internal png", icon="FILE_TICK")
        col.operator("yzk.yzk_remove_image", text="remove_unuse_images", icon="CANCEL")

        col = layout.column(align=True)
        col.operator("paint.texture_paint_toggle",text="3DPaint_toggle",icon="TPAINT_HLT")

        row = col.row(align=True)
        row.operator("yzk.yzk_change_image_mode_view",text="uv",icon="IMAGE_COL")
        row.operator("yzk.yzk_change_image_mode_paint",text="paint",icon="TPAINT_HLT")
        row.operator("yzk.yzk_change_image_mode_mask",text="mask",icon="MOD_MASK")

        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                image_editor_mode = bpy.context.space_data.mode

                if image_editor_mode == "PAINT":
                    toolsettings = context.tool_settings.image_paint
                    brush = toolsettings.brush

                    col = layout.column(align=True)
                    col.prop(brush, "image_tool", text="Draw")
                    col.prop(brush, "blend", text="Blend")

                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.operator("yzk.yzk_normal_brush_tool", text="Brush", icon='BRUSH_TEXDRAW')
                    row.operator("yzk.yzk_fill_tool", text="Fill", icon='BRUSH_TEXFILL')
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
                    row = col.row(align=True)
                    row.prop(brush, "use_paint_sculpt", text="", icon='SCULPTMODE_HLT')
                    row.prop(brush, "use_paint_vertex", text="", icon='VPAINT_HLT')
                    row.prop(brush, "use_paint_weight", text="", icon='WPAINT_HLT')
                    row.prop(brush, "use_paint_image", text="", icon='TPAINT_HLT')

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




                if image_editor_mode == "VIEW":
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.operator("image.view_all",text='view_all')
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.operator("uv.select_all",text='select_all_toggle').action="TOGGLE"

                    col = layout.column(align=True)
                    col.operator("uv.unwrap")
                    col.operator("uv.smart_project")
                    col.operator("uv.lightmap_pack")
                    col.operator("uv.follow_active_quads")

                    col = layout.column(align=True)
                    col.operator("yzk.yzk_uv_reset_cursor",icon="CURSOR",text="reset_cursor")

                    col = layout.column(align=True)
                    col.menu("IMAGE_MT_uvs", text='UVs', icon='UV_VERTEXSEL')
                    col.operator("uv.average_islands_scale")
                    col.operator("uv.seams_from_islands")

                    col = layout.column(align=True)
                    col.operator("uv.uv_squares_by_shape")
                    col.operator("uv.textools_unwrap_peel_edge")
                    col.operator("uv.muv_packuv")

                    col = layout.column(align=True)
                    row = col.row(align=True)
                    props=row.operator("transform.mirror",text='Mirror_X')
                    props.constraint_axis=(True, False, False)
                    props=row.operator("transform.mirror",text='Mirror_Y')
                    props.constraint_axis=(False, True, False)

                    col = layout.column(align=True)
                    row = col.row(align=True)
                    props=row.operator("transform.rotate",text='orientL')
                    props.value=0.7854
                    props.axis=(-0, -0, 1)
                    props=row.operator("transform.rotate",text='orientR')
                    props.value=0.7854
                    props.axis=(-0, -0, -1)

                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.operator("yzk.yzk_uv_move_left", text='move_left')
                    row.operator("yzk.yzk_uv_move_right", text='move_right')
                    row = col.row(align=True)
                    row.operator("yzk.yzk_uv_move_up", text='move_up')
                    row.operator("yzk.yzk_uv_move_down", text='move_down')

                    col = layout.column(align=True)
                    col.operator("yzk.yzk_uv_rename_texture_projection", text="textureProjection")
                    col.operator("yzk.yzk_uv_rename_texture_projection1", text="textureProjection1")


                    col = layout.column(align=True)
                    col.operator("object.bake_image",text="Bake",icon="RENDER_STILL")

                    col = layout.column(align=True)
                    col.prop(context.scene, "camera")

                    col = layout.column(align=True)
                    col.operator("render.render",text="Render",icon="RENDER_STILL")
                    row = col.row(align=True)
                    row.operator("image.view_all","View Fit").fit_view=True
                    row.operator("image.view_zoom_ratio",text="Zoom1:1").ratio=1

                    col = layout.column(align=True)
                    col.operator("image.save_as")



class yzk_uv_move_right(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_move_right"
    bl_label = "yzk_uv_move_right"

    def execute(self, context):
        bpy.ops.transform.translate(value=(1, 0, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

class yzk_uv_move_left(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_move_left"
    bl_label = "yzk_uv_move_left"

    def execute(self, context):
        bpy.ops.transform.translate(value=(-1, 0, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

class yzk_uv_move_up(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_move_up"
    bl_label = "yzk_uv_move_up"

    def execute(self, context):
        bpy.ops.transform.translate(value=(0, 1, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

class yzk_uv_move_down(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_move_down"
    bl_label = "yzk_uv_move_down"

    def execute(self, context):
        bpy.ops.transform.translate(value=(0, -1, 0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

class yzk_uv_mode_vertex(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_mode_vertex"
    bl_label = "yzk_uv_mode_vertex"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                obj = bpy.context.object
                if obj.select == True:
                    if obj.type == 'MESH':
                        if bpy.context.object.mode != 'EDIT':
                            bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_mode(type="VERT")
                        #bpy.ops.mesh.select_all(action ='SELECT')
                        #if bpy.context.scene.tool_settings.use_uv_select_sync == True:
                            #bpy.context.scene.tool_settings.use_uv_select_sync = False
                            #bpy.ops.uv.select_all(action ='SELECT')
                        bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
        return {'FINISHED'}

class yzk_uv_mode_edge(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_mode_edge"
    bl_label = "yzk_uv_mode_edge"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                obj = bpy.context.object
                if obj.select == True:
                    if obj.type == 'MESH':
                        if bpy.context.object.mode != 'EDIT':
                            bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_mode(type="EDGE")
                        bpy.context.scene.tool_settings.uv_select_mode = 'EDGE'
        return {'FINISHED'}

class yzk_uv_mode_face(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_mode_face"
    bl_label = "yzk_uv_mode_face"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                obj = bpy.context.object
                if obj.select == True:
                    if obj.type == 'MESH':
                        if bpy.context.object.mode != 'EDIT':
                            bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_mode(type="FACE")
                        bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
        return {'FINISHED'}

class yzk_change_image_mode_view(bpy.types.Operator):
    bl_idname = "yzk.yzk_change_image_mode_view"
    bl_label = "yzk_change_image_mode_view"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                space_image = area.spaces.active
                space_image.mode = 'VIEW'
                obj = bpy.context.object
                if obj.select == True:
                    if obj.type == 'MESH':
                        if bpy.context.object.mode != 'EDIT':
                            bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_mode(type="VERT")
                        #bpy.ops.mesh.select_all(action ='SELECT')
                        if bpy.context.scene.tool_settings.use_uv_select_sync == True:
                            bpy.context.scene.tool_settings.use_uv_select_sync = False
                        else:
                            bpy.context.scene.tool_settings.use_uv_select_sync = True
        return {'FINISHED'}

class yzk_change_image_mode_paint(bpy.types.Operator):
    bl_idname = "yzk.yzk_change_image_mode_paint"
    bl_label = "yzk_change_image_mode_paint"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                space_image = area.spaces.active
                space_image.mode = 'PAINT'
        return {'FINISHED'}

class yzk_change_image_mode_mask(bpy.types.Operator):
    bl_idname = "yzk.yzk_change_image_mode_mask"
    bl_label = "yzk_change_image_mode_mask"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                space_image = area.spaces.active
                space_image.mode = 'MASK'
        return {'FINISHED'}

class yzk_normal_brush_tool(bpy.types.Operator):
    bl_idname = "yzk.yzk_normal_brush_tool"
    bl_label = "yzk_normal_brush_tool"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                brush = context.tool_settings.image_paint.brush
                brush.image_tool = 'DRAW'
        return {'FINISHED'}

class yzk_blend_mix(bpy.types.Operator):
    bl_idname = "yzk.yzk_blend_mix"
    bl_label = "yzk_blend_mix"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                brush = context.tool_settings.image_paint.brush
                brush.blend = 'MIX'
        return {'FINISHED'}

class yzk_erase_alpha(bpy.types.Operator):
    bl_idname = "yzk.yzk_erase_alpha"
    bl_label = "yzk_erase_alpha"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                brush = context.tool_settings.image_paint.brush
                brush.blend = 'ERASE_ALPHA'
        return {'FINISHED'}

class yzk_add_alpha(bpy.types.Operator):
    bl_idname = "yzk.yzk_add_alpha"
    bl_label = "yzk_add_alpha"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                brush = context.tool_settings.image_paint.brush
                brush.blend = 'ADD_ALPHA'
        return {'FINISHED'}

class yzk_fill_tool(bpy.types.Operator):
    bl_idname = "yzk.yzk_fill_tool"
    bl_label = "yzk_fill_tool"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                brush = context.tool_settings.image_paint.brush
                brush.image_tool = 'FILL'
        return {'FINISHED'}

class yzk_smear_tool(bpy.types.Operator):
    bl_idname = "yzk.yzk_smear_tool"
    bl_label = "yzk_smear_tool"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type== 'IMAGE_EDITOR':
                brush = context.tool_settings.image_paint.brush
                brush.image_tool = 'SMEAR'
        return {'FINISHED'}


class yzk_packimg(bpy.types.Operator):
    bl_idname = "yzk.yzk_packimg"
    bl_label = "yzk_packimg"

    def execute(self, context):
        for img in bpy.data.images:
            if img != None:
                bpy.ops.image.pack({'edit_image': img},as_png=True)
        return {'FINISHED'}

class yzk_remove_image(bpy.types.Operator):
    bl_idname = "yzk.yzk_remove_image"
    bl_label = "yzk_remove_image"

    def execute(self, context):
        for image in bpy.data.images:
            if not image.users:
                bpy.data.images.remove(image)
        return {'FINISHED'}

class yzk_uv_rename_texture_projection(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_rename_texture_projection"
    bl_label = "yzk_uv_rename_texture_projection"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.rename_uv(name="Texture_Projection")
        return {'FINISHED'}

class yzk_uv_rename_texture_projection1(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_rename_texture_projection1"
    bl_label = "yzk_uv_rename_texture_projection1"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                bpy.context.scene.objects.active = obj
                bpy.ops.object.rename_uv(name="Texture_Projection1")
        return {'FINISHED'}

class yzk_uv_reset_cursor(bpy.types.Operator):
    bl_idname = "yzk.yzk_uv_reset_cursor"
    bl_label = "yzk_uv_reset_cursor"

    def execute(self, context):
        bpy.context.space_data.cursor_location[0] = 0
        bpy.context.space_data.cursor_location[1] = 0
        return {'FINISHED'}


def cleanDataBlock(self,block):
    for data in block:
        if not data.users:
            block.remove(data)


def register():
    bpy.utils.register_class(yzk_uvtools)
    bpy.utils.register_class(yzk_uv_move_right)
    bpy.utils.register_class(yzk_uv_move_left)
    bpy.utils.register_class(yzk_uv_move_up)
    bpy.utils.register_class(yzk_uv_move_down)
    bpy.utils.register_class(yzk_uv_mode_vertex)
    bpy.utils.register_class(yzk_uv_mode_edge)
    bpy.utils.register_class(yzk_uv_mode_face)
    bpy.utils.register_class(yzk_change_image_mode_view)
    bpy.utils.register_class(yzk_change_image_mode_paint)
    bpy.utils.register_class(yzk_change_image_mode_mask)
    bpy.utils.register_class(yzk_normal_brush_tool)
    bpy.utils.register_class(yzk_blend_mix)
    bpy.utils.register_class(yzk_erase_alpha)
    bpy.utils.register_class(yzk_add_alpha)
    bpy.utils.register_class(yzk_fill_tool)
    bpy.utils.register_class(yzk_smear_tool)
    bpy.utils.register_class(yzk_packimg)
    bpy.utils.register_class(yzk_remove_image)
    bpy.utils.register_class(yzk_uv_rename_texture_projection)
    bpy.utils.register_class(yzk_uv_rename_texture_projection1)
    bpy.utils.register_class(yzk_uv_reset_cursor)

def unregister():
    bpy.utils.unregister_class(yzk_uvtools)
    bpy.utils.unregister_class(yzk_uv_move_right)
    bpy.utils.unregister_class(yzk_uv_move_left)
    bpy.utils.unregister_class(yzk_uv_move_up)
    bpy.utils.unregister_class(yzk_uv_move_down)
    bpy.utils.unregister_class(yzk_uv_mode_vertex)
    bpy.utils.unregister_class(yzk_uv_mode_edge)
    bpy.utils.unregister_class(yzk_uv_mode_face)
    bpy.utils.unregister_class(yzk_change_image_mode_view)
    bpy.utils.unregister_class(yzk_change_image_mode_paint)
    bpy.utils.unregister_class(yzk_change_image_mode_mask)
    bpy.utils.unregister_class(yzk_normal_brush_tool)
    bpy.utils.unregister_class(yzk_blend_mix)
    bpy.utils.unregister_class(yzk_erase_alpha)
    bpy.utils.unregister_class(yzk_add_alpha)
    bpy.utils.unregister_class(yzk_fill_tool)
    bpy.utils.unregister_class(yzk_smear_tool)
    bpy.utils.unregister_class(yzk_packimg)
    bpy.utils.unregister_class(yzk_remove_image)
    bpy.utils.unregister_class(yzk_uv_rename_texture_projection)
    bpy.utils.unregister_class(yzk_uv_rename_texture_projection1)
    bpy.utils.unregister_class(yzk_uv_reset_cursor)

if __name__ == "__main__":
    register()
