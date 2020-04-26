import bpy


from bl_ui.properties_material import MaterialButtonsPanel


class MATERIAL_PT_pr_context_material(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        # An exception, don't call the parent poll func because
        # this manages materials for all engine types

        engine = context.scene.render.engine
        return (context.material or context.object) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data
        is_sortable = (len(ob.material_slots) > 1)

        if ob:
            rows = 1
            if is_sortable:
                rows = 4

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.65)

        if ob:
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()


class MATERIAL_PT_pr_preview(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Preview"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        self.layout.template_preview(context.material)


class MATERIAL_PT_pr_bsdf(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "BSDF"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        type = mat.pearray.bsdf

        split = layout.split()

        col = split.column()
        col.prop(mat.pearray, "bsdf")

        split = col.split()
        col = split.column()
        col.prop(mat.pearray, "cast_shadows")
        col.prop(mat.pearray, "cast_self_shadows")

        col = split.column()
        col.prop(mat.pearray, "is_camera_visible")
        col.prop(mat.pearray, "is_shadeable")

        if type == 'COOK_TORRANCE':
            layout.separator()
            split = layout.split()
            col = split.column(align=True)
            col.prop(mat.pearray, "ct_fresnel_mode")
            col.prop(mat.pearray, "ct_distribution_mode")
            col.prop(mat.pearray, "ct_geometry_mode")


class MATERIAL_PT_pr_diffuse(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Diffuse"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (context.material.pearray.bsdf in {'DIFFUSE', 'ORENNAYAR', 'WARD', 'COOK_TORRANCE'}) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        type = mat.pearray.bsdf

        split = layout.split()

        col = split.column()
        color_template(mat, col, "diffuse_color")
        if type == 'ORENNAYAR' or type == 'COOK_TORRANCE':
            col.prop(mat, 'roughness')         


class MATERIAL_PT_pr_grid(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Grid"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (context.material.pearray.bsdf == 'GRID') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        type = mat.pearray.bsdf

        split = layout.split()

        col = split.column()


class MATERIAL_PT_pr_specular(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Specular"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (context.material.pearray.bsdf in {'GLASS', 'MIRROR', 'WARD', 'COOK_TORRANCE'}) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        type = mat.pearray.bsdf

        split = layout.split()

        col = split.column()
        color_template(mat, col, "specular_color")
        if type == 'MIRROR' or type == 'GLASS' or type == 'COOK_TORRANCE':
            ior_template(mat, col, "specular_ior")
        if type == 'WARD' or type == 'COOK_TORRANCE':
            col2 = col.column(align=True)
            col2.prop(mat.pearray, 'spec_roughness_x')
            col2.prop(mat.pearray, 'spec_roughness_y')
            col.prop(mat.pearray, 'reflectivity')
        if type == 'GLASS':
            col.prop(mat.pearray, 'glass_is_thin')


class MATERIAL_PT_pr_emission(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Emission"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (not context.material.pearray.bsdf == 'GRID') and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        type = mat.pearray.bsdf

        split = layout.split()

        col = split.column()
        color_template(mat, col, "emission_color")


def color_template(obj, layout, name):
    sub_obj = obj
    if not hasattr(obj, name):
        sub_obj = obj.pearray
    
    type = getattr(obj.pearray, '%s_type' % name)

    col = layout.column(align=True)
    col.row(align=True).prop(obj.pearray, '%s_type' % name, expand=True)
    if type == 'TEMP':
        r = col.row(align=True)
        r.prop(obj.pearray, '%s_temp_type' % name, text="")
        r.prop(obj.pearray, '%s_temp_factor' % name, text='Factor')
        col.prop(obj.pearray, '%s_temp' % name, text="")
    elif type == 'TEX' and hasattr(obj.pearray, '%s_tex_slot' % name):
        col.prop(obj.pearray, '%s_tex_slot' % name)
    else:
        col.prop(sub_obj, name, text="")


def ior_template(obj, layout, name):
    sub_obj = obj
    if not hasattr(obj, name):
        sub_obj = obj.pearray
    
    type = getattr(obj.pearray, '%s_type' % name)

    col = layout.column(align=True)
    col.row(align=True).prop(obj.pearray, '%s_type' % name, expand=True)
    if type == 'VALUE':
        col.prop(obj.pearray, '%s_value' % name, text="Ior")
    else:
        col.prop(obj.pearray, '%s_color' % name, text="Ior")