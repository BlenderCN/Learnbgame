import bpy

class GideonButtonsPanel():
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.engine == 'GIDEON_RENDER_ENGINE'

class GideonRender_Source_Panel(GideonButtonsPanel, bpy.types.Panel):
    bl_label = "Program Sources"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        g_scene = scene.gideon

        layout.prop(g_scene, "std_path", text="Standard Path")
        layout.prop(g_scene, "source_path", text="Search Path")

        row = layout.row()
        row.template_list("UI_UL_list", "gideon_source_list", g_scene, "sources", g_scene, "active_source_index", rows=2)
        col = row.column(align=True)
        col.operator('gideon.add_source', icon='ZOOMIN', text="")
        col.operator('gideon.remove_source', icon='ZOOMOUT', text="")
        
        if g_scene.active_source_index >= 0:
            active_source = g_scene.sources[g_scene.active_source_index]
            layout.prop(active_source, "name", text="Filename")
            layout.prop(active_source, "external", text="External")

        layout.operator('gideon.update_kernel_functions', text="Refresh Function List")

class GideonRender_Entry_Panel(GideonButtonsPanel, bpy.types.Panel):
    bl_label = "Program Entry"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        g_scene = scene.gideon
        
        layout.prop_search(g_scene, "entry_point", g_scene, "entry_list", text = "Entry Point", icon = 'MATERIAL')
        layout.prop(scene.render, "tile_x", text = "Tile Width")
        layout.prop(scene.render, "tile_y", text = "Tile Height")



class CustomLampPanel(GideonButtonsPanel, bpy.types.Panel):
    bl_label = "Lamp"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.lamp and GideonButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout
        lamp = context.lamp
        
        layout.prop(lamp, "energy", text="Energy")
        layout.prop(lamp, "color", text="Color")
        layout.prop(lamp, "shadow_soft_size", text="Size")
        
class GideonMaterialContextPanel(GideonButtonsPanel, bpy.types.Panel):
    bl_label = ""
    bl_context = "material"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.material or context.object) and GideonButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout

        ob = context.object
        mat = context.material
        slot = context.material_slot
        space = context.space_data
        
        if ob:
            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=2)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

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

class GideonMaterialPanel(GideonButtonsPanel, bpy.types.Panel):
    bl_label = "Settings"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material and GideonButtonsPanel.poll(context)

    def draw(self, context):
        layout = self.layout
        mat = context.material
        g_mat = mat.gideon
        g_scene = context.scene.gideon
        
        layout.prop_search(g_mat, "shader", g_scene, "shader_list", icon = 'MATERIAL')
        layout.prop_search(g_mat, "volume", g_scene, "shader_list", icon = 'MATERIAL')

        layout.prop(mat, "diffuse_color", text = "Viewport Color")
        
def get_panels():
    return (
        bpy.types.RENDER_PT_render,
        bpy.types.RENDER_PT_output,
        bpy.types.RENDER_PT_encoding,
        bpy.types.RENDER_PT_dimensions,
        bpy.types.RENDER_PT_stamp,
        bpy.types.SCENE_PT_scene,
        bpy.types.SCENE_PT_audio,
        bpy.types.SCENE_PT_unit,
        bpy.types.SCENE_PT_keying_sets,
        bpy.types.SCENE_PT_keying_set_paths,
        bpy.types.SCENE_PT_physics,
        bpy.types.WORLD_PT_context_world,
        bpy.types.DATA_PT_context_mesh,
        bpy.types.DATA_PT_context_camera,
        bpy.types.DATA_PT_context_lamp,
        bpy.types.DATA_PT_context_speaker,
        bpy.types.DATA_PT_texture_space,
        bpy.types.DATA_PT_curve_texture_space,
        bpy.types.DATA_PT_mball_texture_space,
        bpy.types.DATA_PT_vertex_groups,
        bpy.types.DATA_PT_shape_keys,
        bpy.types.DATA_PT_uv_texture,
        bpy.types.DATA_PT_vertex_colors,
        bpy.types.DATA_PT_camera,
        bpy.types.DATA_PT_camera_display,
        bpy.types.DATA_PT_lens,
        bpy.types.DATA_PT_speaker,
        bpy.types.DATA_PT_distance,
        bpy.types.DATA_PT_cone,
        bpy.types.DATA_PT_customdata,
        bpy.types.DATA_PT_custom_props_mesh,
        bpy.types.DATA_PT_custom_props_camera,
        bpy.types.DATA_PT_custom_props_lamp,
        bpy.types.DATA_PT_custom_props_speaker,
        bpy.types.TEXTURE_PT_clouds,
        bpy.types.TEXTURE_PT_wood,
        bpy.types.TEXTURE_PT_marble,
        bpy.types.TEXTURE_PT_magic,
        bpy.types.TEXTURE_PT_blend,
        bpy.types.TEXTURE_PT_stucci,
        bpy.types.TEXTURE_PT_image,
        bpy.types.TEXTURE_PT_image_sampling,
        bpy.types.TEXTURE_PT_image_mapping,
        bpy.types.TEXTURE_PT_musgrave,
        bpy.types.TEXTURE_PT_voronoi,
        bpy.types.TEXTURE_PT_distortednoise,
        bpy.types.TEXTURE_PT_voxeldata,
        bpy.types.TEXTURE_PT_pointdensity,
        bpy.types.TEXTURE_PT_pointdensity_turbulence,
        bpy.types.TEXTURE_PT_mapping,
        bpy.types.TEXTURE_PT_influence,
        bpy.types.PARTICLE_PT_context_particles,
        bpy.types.PARTICLE_PT_emission,
        bpy.types.PARTICLE_PT_hair_dynamics,
        bpy.types.PARTICLE_PT_cache,
        bpy.types.PARTICLE_PT_velocity,
        bpy.types.PARTICLE_PT_rotation,
        bpy.types.PARTICLE_PT_physics,
        bpy.types.PARTICLE_PT_boidbrain,
        bpy.types.PARTICLE_PT_render,
        bpy.types.PARTICLE_PT_draw,
        bpy.types.PARTICLE_PT_children,
        bpy.types.PARTICLE_PT_field_weights,
        bpy.types.PARTICLE_PT_force_fields,
        bpy.types.PARTICLE_PT_vertexgroups,
        bpy.types.PARTICLE_PT_custom_props,
        bpy.types.MATERIAL_PT_custom_props,
        )

def register():
    for panel in get_panels():
        panel.COMPAT_ENGINES.add('GIDEON_RENDER_ENGINE')
    
def unregister():
    for panel in get_panels():
        panel.COMPAT_ENGINES.remove('GIDEON_RENDER_ENGINE')
