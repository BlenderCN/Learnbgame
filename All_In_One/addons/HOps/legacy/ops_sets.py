import bpy
import bpy.utils.previews
from bpy.types import WindowManager
#from bpy.props import BoolProperty, IntProperty
from bpy.props import *
from .. utils.addons import addon_exists

#############################
# RenderSet1
#############################

# Sets Up The Render / As Always


class HOPS_OT_renset1Operator(bpy.types.Operator):
    '''
    Sets Eevee / Cycles settings to render HighQuality
    '''

    bl_idname = 'render.setup'
    bl_label = 'RenderSetup'
    bl_options = {'REGISTER', 'UNDO'}

    colmgm : BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        box = layout.box()

    def execute(self, context):
        c = bpy.context.scene
        c2 = bpy.context.space_data.shading
        
        if c.render.engine == 'CYCLES':
            c.cycles.progressive = 'PATH'
            c.cycles.use_square_samples = True
            c.cycles.sample_clamp_indirect = 2
            c.cycles.sample_clamp_direct = 2
            c.cycles.preview_samples = 40
            c.cycles.samples = 15
            c.cycles.min_bounces = 5
            c.cycles.glossy_bounces = 16
            c.cycles.diffuse_bounces = 16
            c.cycles.blur_glossy = 0.8
            c.world.cycles.sample_as_light = True
            c.world.cycles.sample_map_resolution = 512
            c.cycles.light_sampling_threshold = 0
        if c.render.engine == 'BLENDER_EEVEE':
            c.render.engine = 'BLENDER_EEVEE'
            c.eevee.use_gtao = True
            c.eevee.use_ssr = True
            c.eevee.use_ssr_halfres = False
            c.eevee.use_soft_shadows = True
            c.eevee.use_shadow_high_bitdepth = True
            c.eevee.shadow_cube_size = '2048'
            c.eevee.gi_cubemap_resolution = '2048'
            c.eevee.shadow_cascade_size = '2048'
            c.eevee.gi_diffuse_bounces = 4
            c.eevee.taa_samples = 64
                        
            #Shading
            c2.show_shadows = True
            c2.show_cavity = True
            c2.use_scene_lights = True
            #c2.cavity_ridge_factor = 0
            #c2.cavity_valley_factor = 0.3
            c2.cavity_type = 'BOTH'
            c2.curvature_valley_factor = 0.745455
            c2.curvature_ridge_factor = 0.690909
            c2.cavity_valley_factor = 0.475
            c2.cavity_ridge_factor = 0.225
            
        else:
            pass
        return {'FINISHED'}

#############################
# RenderSet2
#############################

# Sets Up The Render / As Always
class HOPS_OT_renset2Operator(bpy.types.Operator):
    """
    Sets Eevee / Cycles settings to lower settings

    """
    bl_idname = "renderb.setup"
    bl_label = "RenderSetupb"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        c = bpy.context.scene
        c2 = bpy.context.space_data.shading
        if bpy.context.scene.render.engine == 'CYCLES':
            cycles.progressive = 'PATH'
            c.use_square_samples = True
            c.samples = 40
            c.glossy_bounces = 8
            c.transparent_max_bounces = 8
            c.transmission_bounces = 8
            c.volume_bounces = 8
            c.diffuse_bounces = 8
            c.sample_clamp_direct = 0
            c.sample_clamp_indirect = 10
            c.blur_glossy = 1
            c.caustics_reflective = True
            c.caustics_refractive = True
            c.device = 'GPU'
        if c.render.engine == 'BLENDER_EEVEE':
            c.render.engine = 'BLENDER_EEVEE'
            c.eevee.use_gtao = False
            c.eevee.use_ssr = False
            c.eevee.use_dof = False
            c.eevee.use_bloom = False
            c.eevee.use_shadow_high_bitdepth = False
            c.eevee.use_taa_reprojection = False
            c.eevee.use_ssr_halfres = True
            c.eevee.use_soft_shadows = False
            #bpy.context.space_data.overlay.show_overlays = True
            c.eevee.shadow_cube_size = '256'
            c.eevee.gi_cubemap_resolution = '256'
            c.eevee.taa_samples = 6
            
            #Shading
            c2.show_shadows = False
            c2.show_cavity = False
        else:
            pass
        return {'FINISHED'}


#############################
# Set UI Ops Start Here
#############################

# Return The UI Back To Normal


class HOPS_OT_ReguiOperator(bpy.types.Operator):
    """
    Regular viewport elements shown

    """
    bl_idname = "ui.reg"
    bl_label = "regViewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            bpy.context.space_data.overlay.show_overlays = True
        if bpy.context.scene.render.engine == 'CYCLES':
            bpy.context.space_data.overlay.show_overlays = True
        else:
            pass
        return {'FINISHED'}

# Attempting To Clean Up UI For A Clean Workspace


class HOPS_OT_CleanuiOperator(bpy.types.Operator):
    """
    Regular viewport elements hidden / simplified view.

    """
    bl_idname = "ui.clean"
    bl_label = "cleanViewport"
    bl_options = {'REGISTER', 'UNDO'}
    

    def execute(self, context):
        c = bpy.context.screen
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            bpy.context.space_data.overlay.show_overlays = False
        if bpy.context.scene.render.engine == 'CYCLES':
            bpy.context.space_data.overlay.show_overlays = True
        else:
            pass
        return {'FINISHED'}

# Sets the final frame. Experimental


class HOPS_OT_EndframeOperator(bpy.types.Operator):
    """
    Allows user to specify start / end frame

    """
    bl_idname = "setframe.end"
    bl_label = "Frame Range"
    bl_options = {'REGISTER', 'UNDO'}

    #this should be a property next to the option
    
    firstframe: IntProperty(name="StartFrame", description="SetStartFrame.", default=1, min=1, max=20000)
    lastframe: IntProperty(name="EndFrame", description="SetStartFrame.", default=100, min=1, max=20000)

    def execute(self, context):
        lastframe = self.lastframe  # needed to get var involved
        firstframe = self.firstframe
        bpy.context.scene.frame_start = firstframe
        bpy.context.scene.frame_end = lastframe
        return {'FINISHED'}

# Sets the final frame. Experimental


class HOPS_OT_MeshdispOperator(bpy.types.Operator):
    """
    Hides Marked Edges from view.

    """
    bl_idname = "hops.meshdisp"
    bl_label = "Mesh Disp"
    bl_options = {'REGISTER', 'UNDO'}

    # this should be a property next to the option

    # firstframe = IntProperty(name="StartFrame", description="SetStartFrame.", default=1, min = 1, max = 20000)
    # lastframe = IntProperty(name="EndFrame", description="SetStartFrame.", default=100, min = 1, max = 20000)

    def execute(self, context):
        bpy.context.space_data.overlay.show_edge_crease = False
        bpy.context.space_data.overlay.show_edge_sharp = False
        bpy.context.space_data.overlay.show_edge_bevel_weight = False
        bpy.context.space_data.overlay.show_edge_seams = False

        return {'FINISHED'}
