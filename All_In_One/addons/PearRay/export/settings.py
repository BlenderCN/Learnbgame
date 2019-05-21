def add_entry(exporter, key, v):
    exporter.w.write("(registry \'%s\' %s)" % (key, str(v).lower() if type(v) is bool else v))

def export_settings(exporter, pr, scene):
    s = scene.pearray

    add_entry(exporter, '/renderer/common/type', int(pr.IntegratorMode.__members__[s.integrator]))
    add_entry(exporter, "/renderer/common/max_ray_depth", s.max_ray_depth)
    add_entry(exporter, '/renderer/common/tile/mode', int(pr.TileMode.__members__[s.render_tile_mode]))

    add_entry(exporter, '/renderer/common/sampler/aa/count', s.sampler_max_aa_samples)
    add_entry(exporter, '/renderer/common/sampler/aa/type', int(pr.SamplerMode.__members__[s.sampler_aa_mode]))
    
    add_entry(exporter, '/renderer/common/sampler/lens/count', s.sampler_max_lens_samples)
    add_entry(exporter, '/renderer/common/sampler/lens/type', int(pr.SamplerMode.__members__[s.sampler_lens_mode]))

    add_entry(exporter, '/renderer/common/sampler/time/count', s.sampler_max_time_samples)
    add_entry(exporter, '/renderer/common/sampler/time/type', int(pr.SamplerMode.__members__[s.sampler_time_mode]))
    add_entry(exporter, '/renderer/common/sampler/time/mapping', int(pr.TimeMappingMode.__members__[s.sampler_time_mapping_mode]))
    add_entry(exporter, '/renderer/common/sampler/time/scale',s.sampler_time_scale)

    add_entry(exporter, '/renderer/common/sampler/spectral/count', s.sampler_max_spectral_samples)
    add_entry(exporter, '/renderer/common/sampler/spectral/type', int(pr.SamplerMode.__members__[s.sampler_spectral_mode]))

    if s.integrator == 'DIRECT':
        add_entry(exporter, '/renderer/integrator/direct/diffuse/max_depth', s.max_diffuse_bounces)
        add_entry(exporter, '/renderer/integrator/direct/light/sample_count', s.max_light_samples)
    elif s.integrator == 'BIDIRECT':
        add_entry(exporter, '/renderer/integrator/bidirect/diffuse/max_depth', s.max_diffuse_bounces)
        add_entry(exporter, '/renderer/integrator/bidirect/light/sample_count', s.max_light_samples)
        add_entry(exporter, '/renderer/integrator/bidirect/light/max_depth', s.max_light_depth)
    elif s.integrator == 'PPM':
        add_entry(exporter, '/renderer/integrator/ppm/diffuse/max_depth', s.max_diffuse_bounces)
        add_entry(exporter, '/renderer/integrator/ppm/pass/count', s.photon_passes)
        add_entry(exporter, '/renderer/integrator/ppm/pass/photons', s.photon_count)
        add_entry(exporter, '/renderer/integrator/ppm/photons/gather/max_radius', s.photon_gather_radius)
        add_entry(exporter, '/renderer/integrator/ppm/photons/gather/max_count', s.photon_max_gather_count)
        add_entry(exporter, '/renderer/integrator/ppm/photons/gather/mode', int(pr.PPMGatheringMode.__members__[s.photon_gathering_mode]))
        add_entry(exporter, '/renderer/integrator/ppm/photons/gather/squeeze_weight',s.photon_squeeze/100)
        add_entry(exporter, '/renderer/integrator/ppm/photons/gather/contract_ratio', s.photon_ratio/100)
    elif s.integrator == 'AO':
        add_entry(exporter, '/renderer/integrator/ao/sample_count', s.max_light_samples)
        add_entry(exporter, '/renderer/integrator/ao/use_materials', s.ao_use_materials)
    elif s.integrator == 'VISUALIZER':
        add_entry(exporter, '/renderer/integrator/visualizer/mode', int(pr.DebugMode.__members__[s.debug_mode]))
