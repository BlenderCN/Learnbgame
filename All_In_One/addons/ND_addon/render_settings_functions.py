import bpy
import json

#read json
def read_json(filepath):
    with open(filepath, "r") as read_file:
        data = json.load(read_file)
    return data

#create json
def create_json(filepath, data):
    with open(filepath, "w") as write_file:
        json.dump(data, write_file)

#format render settings infos
def format_render_settings_info():
    scene=bpy.context.scene
    rd=scene.render
    im=rd.image_settings
    cy=scene.cycles
    cu=scene.cycles_curves
    
    datas = {
        "settings": {
        
        #render
            "feature_set": cy.feature_set,
            #"device": cy.device,
            "shading_system": cy.shading_system,
            
        #dimensions
            "resolution_x": rd.resolution_x,
            "resolution_y": rd.resolution_y,
            "resolution_percentage": rd.resolution_percentage,
            
        #output
            "use_overwrite": rd.use_overwrite,
            "use_placeholder": rd.use_placeholder,
            "use_file_extension": rd.use_file_extension,
            "use_render_cache": rd.use_render_cache,
            "file_format": im.file_format,
            "color_mode": im.color_mode,
            "color_depth": im.color_depth,
            "exr_codec": im.exr_codec,
            "compression": im.compression,
            
        #sampling
            "progressive": cy.progressive,
            
            "use_square_samples": cy.use_square_samples,
            "seed": cy.seed,
            "use_animated_seed": cy.use_animated_seed,
            "sample_clamp_direct": cy.sample_clamp_direct,
            "sample_clamp_indirect": cy.sample_clamp_indirect,
            "light_sampling_threshold": cy.light_sampling_threshold,
            "aa_samples": cy.aa_samples,
            "preview_aa_samples": cy.preview_aa_samples,
            "sample_all_lights_direct": cy.sample_all_lights_direct,
            "sample_all_lights_indirect": cy.sample_all_lights_indirect,
            "sampling_pattern": cy.sampling_pattern,
            
            "samples": cy.samples,
            "preview_samples": cy.preview_samples,
            
            "diffuse_samples": cy.diffuse_samples,
            "glossy_samples": cy.glossy_samples,
            "transmission_samples": cy.transmission_samples,
            "ao_samples": cy.ao_samples,
            "mesh_light_samples": cy.mesh_light_samples,
            "subsurface_samples": cy.subsurface_samples,
            "volume_samples": cy.volume_samples,
            
        #geometry
            "volume_step_size": cy.volume_step_size,
            "volume_max_steps": cy.volume_max_steps,
            
            "use_curves": cu.use_curves,
            
            "primitive": cu.primitive,
            "shape": cu.shape,
            "cull_backfacing": cu.cull_backfacing,
            "minimum_width": cu.minimum_width,
            "maximum_width": cu.maximum_width,
            "subdivisions": cu.subdivisions,
            
        #light path
            "transparent_max_bounces": cy.transparent_max_bounces,
            "transparent_min_bounces": cy.transparent_min_bounces,
            "use_transparent_shadows": cy.use_transparent_shadows,
            "caustics_reflective": cy.caustics_reflective,
            "caustics_refractive": cy.caustics_refractive,
            "blur_glossy": cy.blur_glossy,
            "max_bounces": cy.max_bounces,
            "min_bounces": cy.min_bounces,
            "diffuse_bounces": cy.diffuse_bounces,
            "diffuse_bounces": cy.diffuse_bounces,
            "transmission_bounces": cy.transmission_bounces,
            "volume_bounces": cy.volume_bounces,
            
        #motion blur
            "use_motion_blur": rd.use_motion_blur,
            "motion_blur_position": cy.motion_blur_position,
            "rolling_shutter_type": cy.rolling_shutter_type,
            "rolling_shutter_duration": cy.rolling_shutter_duration,
            
        #film
            "film_exposure": cy.film_exposure,
            "film_transparent": cy.film_transparent,
            "pixel_filter_type": cy.pixel_filter_type,
            "filter_width": cy.filter_width,
            
        #performance
            "threads_mode": rd.threads_mode,
            "threads": rd.threads,
            "tile_order": cy.tile_order,
            #"tile_x": rd.tile_x,
            #"tile_y": rd.tile_y,
            "use_progressive_refine": cy.use_progressive_refine,
            "use_save_buffers": rd.use_save_buffers,
            "debug_bvh_type": cy.debug_bvh_type,
            "preview_start_resolution": cy.preview_start_resolution,
            "use_persistent_data": rd.use_persistent_data,
            "debug_use_spatial_splits": cy.debug_use_spatial_splits,
            "debug_use_hair_bvh": cy.debug_use_hair_bvh,
            "debug_bvh_time_steps": cy.debug_bvh_time_steps,
                        
        #post processing
            "use_compositing": rd.use_compositing,
            "use_sequencer": rd.use_sequencer,
            "dither_intensity": rd.dither_intensity,
            
        },
    }
    return datas

#apply render settings from json data set
def apply_render_settings_from_dataset(datas):
    scene=bpy.context.scene
    rd=scene.render
    im=rd.image_settings
    cy=scene.cycles
    cu=scene.cycles_curves

    #render
    cy.feature_set=datas['settings']["feature_set"]
    #cy.device=datas['settings']["device"]
    cy.shading_system=datas['settings']["shading_system"]
        
    #dimensions
    rd.resolution_x=datas['settings']["resolution_x"]
    rd.resolution_y=datas['settings']["resolution_y"]
    rd.resolution_percentage=datas['settings']["resolution_percentage"]
    
    #output
    rd.use_overwrite=datas['settings']["use_overwrite"]
    rd.use_placeholder=datas['settings']["use_placeholder"]
    rd.use_file_extension=datas['settings']["use_file_extension"]
    rd.use_render_cache=datas['settings']["use_render_cache"]
    im.file_format=datas['settings']["file_format"]
    im.color_mode=datas['settings']["color_mode"]
    im.color_depth=datas['settings']["color_depth"]
    im.exr_codec=datas['settings']["exr_codec"]
    im.compression=datas['settings']["compression"]
        
    #sampling
    cy.progressive=datas['settings']["progressive"]
    
    cy.use_square_samples=datas['settings']["use_square_samples"]
    cy.seed=datas['settings']["seed"]
    cy.use_animated_seed=datas['settings']["use_animated_seed"]
    cy.sample_clamp_direct=datas['settings']["sample_clamp_direct"]
    cy.sample_clamp_indirect=datas['settings']["sample_clamp_indirect"]
    cy.light_sampling_threshold=datas['settings']["light_sampling_threshold"]
    cy.aa_samples=datas['settings']["aa_samples"]
    cy.preview_aa_samples=datas['settings']["preview_aa_samples"]
    cy.sample_all_lights_direct=datas['settings']["sample_all_lights_direct"]
    cy.sample_all_lights_indirect=datas['settings']["sample_all_lights_indirect"]
    cy.sampling_pattern=datas['settings']["sampling_pattern"]
        
    cy.samples=datas['settings']["samples"]
    cy.preview_samples=datas['settings']["preview_samples"]
    
    cy.diffuse_samples=datas['settings']["diffuse_samples"]
    cy.glossy_samples=datas['settings']["glossy_samples"]
    cy.transmission_samples=datas['settings']["transmission_samples"]
    cy.ao_samples=datas['settings']["ao_samples"]
    cy.mesh_light_samples=datas['settings']["mesh_light_samples"]
    cy.subsurface_samples=datas['settings']["subsurface_samples"]
    cy.volume_samples=datas['settings']["volume_samples"]
        
    #geometry
    cy.volume_step_size=datas['settings']["volume_step_size"]
    cy.volume_max_steps=datas['settings']["volume_max_steps"]
    
    cu.use_curves=datas['settings']["use_curves"]
    
    cu.primitive=datas['settings']["primitive"]
    cu.shape=datas['settings']["shape"]
    cu.cull_backfacing=datas['settings']["cull_backfacing"]
    cu.minimum_width=datas['settings']["minimum_width"]
    cu.maximum_width=datas['settings']["maximum_width"]
    cu.subdivisions=datas['settings']["subdivisions"]
        
    #light path
    cy.transparent_max_bounces=datas['settings']["transparent_max_bounces"]
    cy.transparent_min_bounces=datas['settings']["transparent_min_bounces"]
    cy.use_transparent_shadows=datas['settings']["use_transparent_shadows"]
    cy.caustics_reflective=datas['settings']["caustics_reflective"]
    cy.caustics_refractive=datas['settings']["caustics_refractive"]
    cy.blur_glossy=datas['settings']["blur_glossy"]
    cy.max_bounces=datas['settings']["max_bounces"]
    cy.min_bounces=datas['settings']["min_bounces"]
    cy.diffuse_bounces=datas['settings']["diffuse_bounces"]
    cy.diffuse_bounces=datas['settings']["diffuse_bounces"]
    cy.transmission_bounces=datas['settings']["transmission_bounces"]
    cy.volume_bounces=datas['settings']["volume_bounces"]
        
    #motion blur
    rd.use_motion_blur=datas['settings']["use_motion_blur"]
    cy.motion_blur_position=datas['settings']["motion_blur_position"]
    cy.rolling_shutter_type=datas['settings']["rolling_shutter_type"]
    cy.rolling_shutter_duration=datas['settings']["rolling_shutter_duration"]
        
    #film
    cy.film_exposure=datas['settings']["film_exposure"]
    cy.film_transparent=datas['settings']["film_transparent"]
    cy.pixel_filter_type=datas['settings']["pixel_filter_type"]
    cy.filter_width=datas['settings']["filter_width"]
        
    #performance
    rd.threads_mode=datas['settings']["threads_mode"]
    rd.threads=datas['settings']["threads"]
    cy.tile_order=datas['settings']["tile_order"]
    #rd.tile_x=datas['settings']["tile_x"]
    #rd.tile_y=datas['settings']["tile_y"]
    cy.use_progressive_refine=datas['settings']["use_progressive_refine"]
    rd.use_save_buffers=datas['settings']["use_save_buffers"]
    cy.debug_bvh_type=datas['settings']["debug_bvh_type"]
    cy.preview_start_resolution=datas['settings']["preview_start_resolution"]
    rd.use_persistent_data=datas['settings']["use_persistent_data"]
    cy.debug_use_spatial_splits=datas['settings']["debug_use_spatial_splits"]
    cy.debug_use_hair_bvh=datas['settings']["debug_use_hair_bvh"]
    cy.debug_bvh_time_steps=datas['settings']["debug_bvh_time_steps"]
                    
    #post processing
    rd.use_compositing=datas['settings']["use_compositing"]
    rd.use_sequencer=datas['settings']["use_sequencer"]
    rd.dither_intensity=datas['settings']["dither_intensity"]
