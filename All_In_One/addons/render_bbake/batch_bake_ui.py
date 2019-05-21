import bpy
from bpy.types import Panel

###########################################################################
class CyclesButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        ob = context.active_object
        return rd.engine in cls.COMPAT_ENGINES and ob and ob.type == 'MESH'

class BBake_Panel(CyclesButtonsPanel, Panel):
    bl_label = "BBake"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'CYCLES'}

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        cscene = scene.cycles
        cbk = scene.render.bake
        ob = context.active_object
        bbake = ob.bbake
        ob_settings = bbake.ob_settings
        scene_settings = scene.bbake

        col = layout.column()

        box_global = col.box()
        row=box_global.row(align=True)
        row.operator('scene.bbake_bake_selected', icon='RENDER_STILL', text='Bake Selected Objects')
        row.operator('scene.bbake_bake_selected', icon='RENDER_STILL', text='Bake All Objects').all=True
        row=box_global.row(align=True)
        row.prop(scene_settings, 'turn_off')
        row.prop(scene_settings, 'create_object_folders')

        ### OB_SETTINGS ###
        col.separator()
        box_ob_settings = col.box()
        box_ob_settings.prop(ob_settings, 'use', text='Bake this object ("%s")' %ob.name, toggle=0)

        if ob_settings.use:
            box_ob_settings.prop(ob_settings, 'path')
            box_ob_settings.prop_search(ob_settings, "uv_layer", ob.data, "uv_layers", text="UV Layer")
            row = box_ob_settings.row()
            row.prop(ob_settings, 'use_selected_to_active')
            row.prop(ob_settings, 'margin')
            if ob_settings.use_selected_to_active:
                if ob_settings.sources:
                    sources = [s.strip() for s in ob_settings.sources.split(',')]
                    if len(sources) == 1:
                        row.prop(ob_settings, 'align')

                row = box_ob_settings.row()
                row.prop(ob_settings, 'use_cage')
                if ob_settings.use_cage:
                    row.prop_search(ob_settings, "cage_object", scene, "objects", text="")

                row = box_ob_settings.row()
                if ob_settings.use_cage:
                    ray_name = 'Extrusion'
                else:
                    ray_name = 'Ray Distance'
                row.prop(ob_settings, 'cage_extrusion', text=ray_name)

                subbox = box_ob_settings.box()
                row = subbox.row()
                row.label('Source Objects:')
                row.operator('object.set_bbake_sources', icon='FORWARD', text='Set Sources')
                row = subbox.row()
                if ob_settings.sources:
                    row.prop(ob_settings, 'sources', text='')

            ### AOVs SETTINGS ###
            col.separator()
            box = col.box()

            row = box.row()
            row.label('AOVs:')
            row.operator('object.bbake_copy_settings',
                        text='Copy AOVs to selected',
                        icon='COPY_ID').copy_aov = True

            def draw_aov_header(layout, aov):
                row = layout.row()
                row.prop(aov, 'use', text=aov.name, toggle=1)
                if aov.dimensions == 'CUSTOM':
                    row.prop(aov, 'dimensions_custom', text='')
                row.prop(aov, 'dimensions', text='')

            def draw_pass_types(layout, aov):
                if aov.use:
                    row = layout.row(align=True)
                    row.prop(aov, 'use_pass_direct', toggle=True)
                    row.prop(aov, 'use_pass_indirect', toggle=True)
                    row.prop(aov, 'use_pass_color', toggle=True)

            def draw_pass_types_combined(layout, aov):
                if aov.use:
                    col = layout.column()
                    row = col.row(align=True)
                    row.prop(aov, "use_pass_direct", toggle=True)
                    row.prop(aov, "use_pass_indirect", toggle=True)

                    split = col.split()
                    split.active = aov.use_pass_direct or aov.use_pass_indirect

                    col = split.column()
                    col.prop(aov, "use_pass_diffuse")
                    col.prop(aov, "use_pass_glossy")
                    col.prop(aov, "use_pass_transmission")

                    col = split.column()
                    col.prop(aov, "use_pass_subsurface")
                    col.prop(aov, "use_pass_ambient_occlusion")
                    col.prop(aov, "use_pass_emit")


            def draw_pass_types_normal(layout, aov):
                if aov.use:
                    layout.label('Normal Settings:')
                    layout.prop(aov, "normal_space", text="Space")
                    row = layout.row(align=True)
                    row.label(text="Swizzle:")
                    row.prop(aov, "normal_r", text="")
                    row.prop(aov, "normal_g", text="")
                    row.prop(aov, "normal_b", text="")

            #COMBINED
            aov = bbake.aov_combined
            box_aov = box.box()
            draw_aov_header(box_aov, aov)
            draw_pass_types_combined(box_aov, aov)

            #DIFFUSE
            aov = bbake.aov_diffuse
            box_aov = box.box()
            draw_aov_header(box_aov, aov)
            draw_pass_types(box_aov, aov)

            #GLOSSY
            aov = bbake.aov_glossy
            box_aov = box.box()
            draw_aov_header(box_aov, aov)
            draw_pass_types(box_aov, aov)


            #TRANSMISSION
            aov = bbake.aov_transmission
            box_aov = box.box()
            draw_aov_header(box_aov, aov)
            draw_pass_types(box_aov, aov)

            #SUBSURFACE
            aov = bbake.aov_subsurface
            box_aov = box.box()
            draw_aov_header(box_aov, aov)
            draw_pass_types(box_aov, aov)

            #NORMAL
            aov = bbake.aov_normal
            box_aov = box.box()
            draw_aov_header(box_aov, aov)
            draw_pass_types_normal(box_aov, aov)

            #AO
            aov = bbake.aov_ao
            box_aov = box.box()
            draw_aov_header(box_aov, aov)

            #SHADOW
            aov = bbake.aov_shadow
            box_aov = box.box()
            draw_aov_header(box_aov, aov)

            #EMIT
            aov = bbake.aov_emit
            box_aov = box.box()
            draw_aov_header(box_aov, aov)

            #UV
            aov = bbake.aov_uv
            box_aov = box.box()
            draw_aov_header(box_aov, aov)

            #ENVIRONMENT
            aov = bbake.aov_environment
            box_aov = box.box()
            draw_aov_header(box_aov, aov)


def register():
    #print('\nREGISTER:\n', __name__)
    bpy.utils.register_class(BBake_Panel)

def unregister():
    #print('\nUN-REGISTER:\n', __name__)
    bpy.utils.unregister_class(BBake_Panel)
