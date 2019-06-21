import bpy

class ModifierProxy:
#Modify
    def add_to_data_transfer(self, mod, prop_list): #DATA_TRANSFER DataTransfer
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.use_vert_data = prop_list[4]
        mod.vert_mapping = prop_list[5]
        mod.data_types_verts = prop_list[6]
        mod.layers_vgroup_select_src = prop_list[7]
        mod.layers_vgroup_select_dst = prop_list[8]
        mod.use_edge_data = prop_list[9]
        mod.edge_mapping = prop_list[10]
        mod.data_types_edges = prop_list[11]
        mod.use_loop_data = prop_list[12]
        mod.loop_mapping = prop_list[13]
        mod.data_types_loops = prop_list[14]
        mod.layers_vcol_select_src = prop_list[15]
        mod.layers_vcol_select_dst = prop_list[16]
        mod.layers_uv_select_src = prop_list[17]
        mod.layers_uv_select_dst = prop_list[18]
        mod.islands_precision = prop_list[19]
        mod.use_poly_data = prop_list[20]
        mod.poly_mapping = prop_list[21]
        mod.data_types_polys = prop_list[22]
        mod.max_distance = prop_list[23]
        mod.use_max_distance = prop_list[24]
        mod.ray_radius = prop_list[25]
        mod.mix_mode = prop_list[26]
        mod.mix_factor = prop_list[27]
        mod.vertex_group = prop_list[28]
        mod.invert_vertex_group = prop_list[29]

    def add_to_mesh_cache(self, mod, prop_list): #MESH_CACHE Mesh Cache
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.cache_format = prop_list[4]
        mod.filepath = prop_list[5]
        mod.factor = prop_list[6]
        mod.deform_mode = prop_list[7]
        mod.interpolation = prop_list[8]
        mod.time_mode = prop_list[9]
        mod.play_mode = prop_list[10]
        mod.frame_start = prop_list[11]
        mod.frame_scale = prop_list[12]
        mod.eval_factor = prop_list[13]
        mod.forward_axis = prop_list[14]
        mod.up_axis = prop_list[15]
        mod.flip_axis = prop_list[16]

    def add_to_mesh_sequence_cache(self, mod, prop_list): #MESH_SEQUENCE_CACHE Mesh Sequence Cache
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.read_data = prop_list[3]
        
    def add_to_normal_edit(self, mod, prop_list): #NORMAL_EDIT Set Split Normals
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.mode = prop_list[5]
        mod.target = prop_list[6]
        mod.use_direction_parallel = prop_list[7]
        mod.offset[0] = prop_list[8]
        mod.offset[1] = prop_list[9]
        mod.offset[2] = prop_list[10]
        mod.mix_mode = prop_list[11]
        mod.mix_factor = prop_list[12]
        mod.vertex_group = prop_list[13]
        mod.mix_limit = prop_list[14]

    def add_to_uv_project(self, mod, prop_list): #UV_PROJECT UVProject
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.uv_layer = prop_list[5]
        mod.use_image_override = prop_list[6]
        mod.projector_count = prop_list[7]
        mod.aspect_x = prop_list[8]
        mod.aspect_y = prop_list[9]
        mod.scale_x = prop_list[10]
        mod.scale_y = prop_list[11]

    def add_to_uv_warp(self, mod, prop_list): #UV_WARP UVWarp
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.center[0] = prop_list[4]
        mod.center[1] = prop_list[5]
        mod.axis_u = prop_list[6]
        mod.axis_v = prop_list[7]
        mod.object_from = prop_list[8]
        mod.object_to = prop_list[9]
        mod.vertex_group = prop_list[10]
        mod.uv_layer = prop_list[11]

    def add_to_vertex_weight_edit(self, mod, prop_list): #VERTEXT_WEIGHT_EDIT VertexWeightEdit
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.use_add = prop_list[6]
        mod.add_threshold = prop_list[7]
        mod.use_remove = prop_list[8]
        mod.remove_threshold = prop_list[9]
        mod.default_weight = prop_list[10]
        mod.falloff_type = prop_list[11]
        mod.mask_constant = prop_list[12]
        mod.mask_vertex_group = prop_list[13]

    def add_to_vertex_weight_mix(self, mod, prop_list): #VERTEX_WEIGHT_MIX VertexWeightMix
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.vertex_group_a = prop_list[4]
        mod.vertex_group_b = prop_list[5]
        mod.default_weight_a = prop_list[6]
        mod.default_weight_b = prop_list[7]
        mod.mix_mode = prop_list[8]
        mod.mix_set = prop_list[9]
        mod.mask_constant = prop_list[10]
        mod.mask_vertex_group = prop_list[11]

    def add_to_vertex_weight_proximity(self, mod, prop_list): #VERTEX_WEIGHT_PROXIMITY VertexWeightProximity
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.vertex_group = prop_list[4]
        mod.target = prop_list[5]
        mod.proximity_mode = prop_list[6]
        mod.proximity_geometry = prop_list[7]
        mod.min_dist = prop_list[8]
        mod.max_dist = prop_list[9]
        mod.falloff_type = prop_list[10]
        mod.mask_constant = prop_list[11]
        mod.mask_vertex_group = prop_list[12]
        mod.mask_tex_mapping = prop_list[13]
        mod.mask_tex_use_channel = prop_list[14]

#Generate
    def add_to_array(self, mod, prop_list): #ARRAY Array
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.fit_type = prop_list[5]
        mod.curve = prop_list[6]
        mod.fit_length = prop_list[7]
        mod.use_constant_offset = prop_list[8]
        mod.constant_offset_displace[0] = prop_list[9]
        mod.constant_offset_displace[1] = prop_list[10]
        mod.constant_offset_displace[2] = prop_list[11]
        mod.use_relative_offset = prop_list[12]
        mod.relative_offset_displace[0]= prop_list[13]
        mod.relative_offset_displace[1]= prop_list[14]
        mod.relative_offset_displace[2]= prop_list[15]
        mod.use_merge_vertices = prop_list[16]
        mod.use_merge_vertices_cap = prop_list[17]
        mod.use_object_offset = prop_list[18]
        mod.offset_object = prop_list[19]
        mod.merge_threshold = prop_list[20]
        mod.start_cap = prop_list[21]
        mod.end_cap = prop_list[22]

    def add_to_bevel(self, mod, prop_list): #BEVEL Bevel
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.width = prop_list[4]
        mod.segments = prop_list[5]
        mod.profile = prop_list[6]
        mod.material = prop_list[7]
        mod.use_only_vertices = prop_list[8]
        mod.use_clamp_overlap = prop_list[9]
        mod.loop_slide = prop_list[10]
        mod.limit_method = prop_list[11]
        mod.angle_limit = prop_list[12]
        mod.vertex_group = prop_list[13]
        mod.offset_type = prop_list[14]

    def add_to_boolean(self, mod, prop_list): #BOOLEAN boolean
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.operation = prop_list[3]
        mod.object = prop_list[4]

    def add_to_build(self, mod, prop_list): #BUILD Build
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.frame_start = prop_list[3]
        mod.frame_duration = prop_list[4]
        mod.use_random_order = prop_list[5]
        mod.seed = prop_list[6]
        mod.use_reverse = prop_list[7]

    def add_to_decimate(self, mod, prop_list): #DECIMATE Decimate
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.decimate_type = prop_list[3]
        mod.ratio = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.invert_vertex_group = prop_list[6]
        mod.vertex_group_factor = prop_list[7]
        mod.use_collapse_triangulate = prop_list[8]
        mod.use_symmetry = prop_list[9]
        mod.symmetry_axis = prop_list[10]
        mod.iterations = prop_list[11]
        mod.angle_limit = prop_list[12]
        mod.use_dissolve_boundaries = prop_list[13]
        mod.delimit = prop_list[14]

    def add_to_edge_split(self, mod, prop_list): #EDGE_SPLIT EdgeSplit
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.use_edge_angle = prop_list[5]
        mod.split_angle = prop_list[6]
        mod.use_edge_sharp = prop_list[7]

    def add_to_mask(self, mod, prop_list): #MASK Mask
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.mode = prop_list[5]
        mod.armature = prop_list[6]
        mod.invert_vertex_group = prop_list[7]
        mod.vertex_group = prop_list[8]

    def add_to_mirror(self, mod, prop_list): #MIRROR Mirror
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.use_x = prop_list[5]
        mod.use_y = prop_list[6]
        mod.use_z = prop_list[7]
        mod.use_mirror_merge = prop_list[8]
        mod.use_clip = prop_list[9]
        mod.use_mirror_vertex_groups = prop_list[10]
        mod.use_mirror_u = prop_list[11]
        mod.use_mirror_v = prop_list[12]
        mod.mirror_object = prop_list[13]

    def add_to_multires(self, mod, prop_list): #MULTIRES Multires
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.subdivision_type = prop_list[3]
        mod.levels = prop_list[4]
        mod.sculpt_levels = prop_list[5]
        mod.render_levels = prop_list[6]
        mod.use_subsurf_uv = prop_list[7]
        mod.show_only_control_edges = prop_list[8]

    def add_to_remesh(self, mod, prop_list): #REMESH Remesh
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.mode = prop_list[4]
        mod.octree_depth = prop_list[5]
        mod.scale = prop_list[6]
        mod.sharpness = prop_list[7]
        mod.use_smooth_shade = prop_list[8]
        mod.use_remove_disconnected = prop_list[9]
        mod.threshold = prop_list[10]

    def add_to_screw(self, mod, prop_list): #SCREW Screw
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.axis = prop_list[4]
        mod.object = prop_list[5]
        mod.angle = prop_list[6]
        mod.steps = prop_list[7]
        mod.render_steps = prop_list[8]
        mod.use_smooth_shade = prop_list[9]
        mod.screw_offset = prop_list[10]
        mod.use_object_screw_offset = prop_list[11]
        mod.use_normal_calculate = prop_list[12]
        mod.use_normal_flip = prop_list[13]
        mod.iterations = prop_list[14]
        mod.use_stretch_u = prop_list[15]
        mod.use_stretch_v = prop_list[16]

    def add_to_skin(self, mod, prop_list): #SKIN Skin
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.branch_smoothing = prop_list[4]
        mod.use_smooth_shade = prop_list[5]
        mod.use_x_symmetry = prop_list[6]
        mod.use_y_symmetry = prop_list[7]
        mod.use_z_symmetry = prop_list[8]

    def add_to_solidify(self, mod, prop_list): #SOLIDIFY Solidify
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.thickness = prop_list[5]
        mod.thickness_clamp = prop_list[6]
        mod.vertex_group = prop_list[7]
        mod.invert_vertex_group = prop_list[8]
        mod.thickness_vertex_group = prop_list[9]
        mod.edge_crease_inner = prop_list[10]
        mod.edge_crease_outer = prop_list[11]
        mod.edge_crease_rim = prop_list[12]
        mod.offset = prop_list[13]
        mod.use_flip_normals = prop_list[14]
        mod.use_even_offset = prop_list[15]
        mod.use_quality_normals = prop_list[16]
        mod.use_rim = prop_list[16]
        mod.use_rim_only = prop_list[17]
        mod.material_offset = prop_list[18]
        mod.material_offset_rim = prop_list[19]

    def add_to_subsurf(self, mod, prop_list): #SUBSURF Subsurf
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.subdivision_type = prop_list[5]
        mod.levels = prop_list[6]
        mod.render_levels = prop_list[7]
        mod.use_subsurf_uv = prop_list[8]
        mod.show_only_control_edges = prop_list[9]

    def add_to_triangulate(self, mod, prop_list): #TRIANGULATE Triangulate
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.quad_method = prop_list[5]
        mod.ngon_method = prop_list[6]

    def add_to_wireframe(self, mod, prop_list): #WIREFRAME Wireframe
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.thickness = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.invert_vertex_group = prop_list[6]
        mod.thickness_vertex_group = prop_list[7]
        mod.use_crease = prop_list[8]
        mod.crease_weight = prop_list[9]
        mod.offset = prop_list[10]
        mod.use_even_offset = prop_list[11]
        mod.use_relative_offset = prop_list[12]
        mod.use_boundary = prop_list[13]
        mod.use_replace = prop_list[14]
        mod.material_offset = prop_list[15]

#Deform
    def add_to_armature(self, mod, prop_list): #ARMATURE Aramature
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object = prop_list[4]
        mod.use_deform_preserve_volume = prop_list[5]
        mod.vertex_group = prop_list[6]
        mod.invert_vertex_group = prop_list[7]
        mod.use_vertex_groups = prop_list[8]
        mod.use_bone_envelopes = prop_list[9]
        mod.use_multi_modifier= prop_list[10]

    def add_to_cast(self, mod, prop_list): #CAST Cast
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.cast_type = prop_list[5]
        mod.use_x = prop_list[6]
        mod.use_y = prop_list[7]
        mod.use_z = prop_list[8]
        mod.factor = prop_list[9]
        mod.radius = prop_list[10]
        mod.size = prop_list[11]
        mod.use_radius_as_size = prop_list[12]
        mod.vertex_group = prop_list[13]
        mod.object = prop_list[14]

    def add_to_corrective_smooth(self, mod, prop_list): #CORRECTIVE_SMOOTH CorrectiveSmooth
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.factor = prop_list[5]
        mod.iterations = prop_list[6]
        mod.smooth_type = prop_list[7]
        mod.vertex_group = prop_list[8]
        mod.invert_vertex_group = prop_list[9]
        mod.use_only_smooth = prop_list[10]
        mod.use_pin_boundary = prop_list[11]
        mod.rest_source = prop_list[12]

    def add_to_curve(self, mod, prop_list): #CURVE Curve
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.deform_axis = prop_list[6]

    def add_to_displace(self, mod, prop_list): #DISPLACE Displace
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.direction = prop_list[5]
        mod.texture_coords = prop_list[6]
        mod.vertex_group = prop_list[7]
        mod.texture_coords_object = prop_list[8]
        mod.mid_level = prop_list[9]
        mod.strength = prop_list[10]

    def add_to_hook(self, mod, prop_list): #HOOK Hook
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.falloff_radius = prop_list[6]
        mod.strength = prop_list[7]
        mod.falloff_type = prop_list[8]
        mod.use_falloff_uniform = prop_list[9]

    def add_to_laplacian_smooth(self, mod, prop_list):  #LAPLACIANSMOOTH Laplacian Smooth
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.iterations = prop_list[5]
        mod.use_x = prop_list[6]
        mod.use_y = prop_list[7]
        mod.use_z = prop_list[8]
        mod.lambda_factor = prop_list[9]
        mod.lambda_border = prop_list[10]
        mod.use_volume_preserve = prop_list[11]
        mod.use_normalized = prop_list[12]
        mod.vertex_group = prop_list[13]

    def add_to_laplacian_deform(self, mod, prop_list):  #LAPLACIANDEFORM LaplacianDeform
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.iterations = prop_list[4]
        mod.vertex_group = prop_list[5]

    def add_to_lattice(self, mod, prop_list): #LATTICE Lattice
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.strength = prop_list[6]

    def add_to_mesh_deform(self, mod, prop_list): #MESH_DEFORM MeshDeform
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.invert_vertex_group = prop_list[6]
        mod.precision = prop_list[7]
        mod.use_dynamic_bind = prop_list[8]

    def add_to_shrinkwrap(self, mod, prop_list): #SHRINKWRAP Shrinkwrap
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.target = prop_list[4]
        mod.vertex_group = prop_list[5]
        mod.invert_vertex_group = prop_list[6]
        mod.offset = prop_list[7]
        mod.wrap_method = prop_list[8]
        mod.use_keep_above_surface = prop_list[9]
        mod.subsurf_levels = prop_list[10]
        mod.project_limit = prop_list[11]
        mod.use_project_x = prop_list[12]
        mod.use_project_y = prop_list[13]
        mod.use_project_z = prop_list[14]
        mod.use_negative_direction = prop_list[15]
        mod.use_positive_direction = prop_list[16]
        mod.cull_face = prop_list[17]
        mod.auxiliary_target = prop_list[18]

    def add_to_simple_deform(self, mod, prop_list): #SIMPLE_DEFORM SimpleDeform
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.deform_method = prop_list[5]
        mod.vertex_group = prop_list[6]
        mod.invert_vertex_group = prop_list[7]
        mod.origin = prop_list[8]
        mod.lock_x = prop_list[9]
        mod.lock_y = prop_list[10]
        mod.angle = prop_list[11]
        mod.limits[0] = prop_list[12]
        mod.limits[1] = prop_list[13]

    def add_to_smooth(self, mod, prop_list): #SMOOTH Smooth
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.use_x = prop_list[5]
        mod.use_y = prop_list[6]
        mod.use_z = prop_list[7]
        mod.factor = prop_list[8]
        mod.iterations = prop_list[9]
        mod.vertex_group = prop_list[10]

    def add_to_warp(self, mod, prop_list): #WARP Warp 
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object_from = prop_list[4]
        mod.object_to = prop_list[5]
        mod.vertex_group = prop_list[6]
        mod.strength = prop_list[7]
        mod.falloff_radius = prop_list[8]
        mod.falloff_type = prop_list[9]
        mod.texture_coords = prop_list[10]
        mod.texture_coords_object = prop_list[11]
        mod.uv_layer = prop_list[12]

    def add_to_wave(self, mod, prop_list): #WAVE Wave
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.show_on_cage = prop_list[4]
        mod.use_x = prop_list[5]
        mod.use_y = prop_list[6]
        mod.use_cyclic = prop_list[7]
        mod.use_normal = prop_list[8]
        mod.use_normal_x = prop_list[9]
        mod.use_normal_y = prop_list[10]
        mod.use_normal_z = prop_list[11]
        mod.time_offset = prop_list[12]
        mod.lifetime = prop_list[13]
        mod.damping_time = prop_list[14]
        mod.start_position_x = prop_list[15]
        mod.start_position_y = prop_list[16]
        mod.falloff_radius = prop_list[17]
        mod.start_position_object = prop_list[18]
        mod.vertex_group = prop_list[19]
        mod.texture_coords = prop_list[20]
        mod.texture_coords_object = prop_list[21]
        mod.uv_layer = prop_list[22]
        mod.speed = prop_list[23]
        mod.width = prop_list[24]
        mod.height = prop_list[25]
        mod.narrowness = prop_list[26]

#Simulate
    def add_to_cloth(self, mod, prop_list): #CLOTH Cloth
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.settings.quality = prop_list[3]
        mod.settings.time_scale = prop_list[4]
        mod.settings.mass = prop_list[5]
        mod.settings.structural_stiffness = prop_list[6]
        mod.settings.bending_stiffness = prop_list[7]
        mod.settings.spring_damping = prop_list[8]
        mod.settings.air_damping = prop_list[9]
        mod.settings.vel_damping = prop_list[10]
        mod.settings.use_pin_cloth = prop_list[11]
        mod.settings.vertex_group_mass = prop_list[12]
        mod.settings.pin_stiffness = prop_list[13]
        mod.settings.use_dynamic_mesh = prop_list[14]
        mod.collision_settings.use_collision = prop_list[15]
        mod.collision_settings.collision_quality = prop_list[16]
        mod.collision_settings.distance_min = prop_list[17]
        mod.collision_settings.repel_force = prop_list[18]
        mod.collision_settings.distance_repel = prop_list[19]
        mod.collision_settings.friction = prop_list[20]
        mod.collision_settings.use_self_collision = prop_list[21]
        mod.collision_settings.self_collision_quality = prop_list[22]
        mod.collision_settings.self_distance_min = prop_list[23]
        mod.collision_settings.vertex_group_self_collisions = prop_list[24]
        mod.collision_settings.group = prop_list[25]
        mod.settings.use_stiffness_scale = prop_list[26]
        mod.settings.vertex_group_structural_stiffness = prop_list[27]
        mod.settings.structural_stiffness_max = prop_list[28]
        mod.settings.vertex_group_bending = prop_list[29]
        mod.settings.bending_stiffness_max = prop_list[30]
        mod.settings.use_sewing_springs = prop_list[31]
        mod.settings.sewing_force_max = prop_list[32]
        mod.settings.vertex_group_shrink = prop_list[33]
        mod.settings.shrink_min = prop_list[34]
        mod.settings.shrink_max = prop_list[35]
        mod.settings.effector_weights.group = prop_list[36]
        mod.settings.effector_weights.gravity = prop_list[37]
        mod.settings.effector_weights.all = prop_list[38]
        mod.settings.effector_weights.force = prop_list[39]
        mod.settings.effector_weights.vortex = prop_list[40]
        mod.settings.effector_weights.magnetic = prop_list[41]
        mod.settings.effector_weights.wind = prop_list[42]
        mod.settings.effector_weights.curve_guide = prop_list[43]
        mod.settings.effector_weights.texture = prop_list[44]
        mod.settings.effector_weights.smokeflow = prop_list[45]
        mod.settings.effector_weights.harmonic = prop_list[46]
        mod.settings.effector_weights.charge = prop_list[47]
        mod.settings.effector_weights.lennardjones = prop_list[48]
        mod.settings.effector_weights.turbulence = prop_list[49]
        mod.settings.effector_weights.drag = prop_list[50]
        mod.settings.effector_weights.boid = prop_list[51]

    def add_to_collision(self, mod, prop_list): #COLLISION Collision
        mod.name = prop_list[0]
        bpy.context.object.collision.permeability = prop_list[1]
        bpy.context.object.collision.stickiness = prop_list[2]
        bpy.context.object.collision.use_particle_kill = prop_list[3]
        bpy.context.object.collision.damping_factor = prop_list[4]
        bpy.context.object.collision.damping_random = prop_list[5]
        bpy.context.object.collision.friction_factor = prop_list[6]
        bpy.context.object.collision.friction_random = prop_list[7]
        bpy.context.object.collision.thickness_outer = prop_list[8]
        bpy.context.object.collision.thickness_inner = prop_list[9]
        bpy.context.object.collision.damping = prop_list[10]
        bpy.context.object.collision.absorption = prop_list[11]
        
    def add_to_dynamic_paint(self, mod, prop_list): #DYNAMIC_PAINT Dynamic Paint 
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.ui_type = prop_list[3]

    def add_to_explode(self, mod, prop_list): #EXPLODE Explode
        mod.name = prop_list[0]
        mod.show_render = prop_list[0]
        mod.show_viewport = prop_list[1]
        mod.vertex_group = prop_list[2]
        mod.protect = prop_list[3]
        mod.particle_uv = prop_list[4]
        mod.use_edge_cut = prop_list[5]
        mod.show_unborn = prop_list[6]
        mod.show_alive = prop_list[7]
        mod.show_dead = prop_list[8]
        mod.use_size = prop_list[9]

    def add_to_fluid_simulation(self, mod, prop_list): #FLUID_SIMULATION Fluidsim 
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.settings.type = prop_list[3]

        if mod.settings.type == 'DOMAIN':
            mod.settings.threads = prop_list[4]
            mod.settings.resolution = prop_list[5]
            mod.settings.preview_resolution = prop_list[6]
            mod.settings.render_display_mode = prop_list[7]
            mod.settings.viewport_display_mode = prop_list[8]
            mod.settings.start_time = prop_list[9]
            mod.settings.end_time = prop_list[10]
            mod.settings.use_speed_vectors = prop_list[11]
            mod.settings.use_reverse_frames = prop_list[12]
            mod.settings.simulation_rate = prop_list[13]
            mod.settings.frame_offset = prop_list[14]
            mod.settings.filepath = prop_list[15]
            mod.settings.viscosity_base = prop_list[16]
            mod.settings.viscosity_exponent = prop_list[17]
            mod.settings.simulation_scale = prop_list[18]
            mod.settings.grid_levels = prop_list[19]
            mod.settings.compressibility = prop_list[20]
            mod.settings.slip_type = prop_list[21]
            mod.settings.partial_slip_factor = prop_list[22]
            mod.settings.use_surface_noobs = prop_list[23]
            mod.settings.surface_smooth = prop_list[24]
            mod.settings.surface_subdivisions = prop_list[25]
            mod.settings.tracer_particles = prop_list[26]
            mod.settings.generate_particles = prop_list[27]

        if mod.settings.type == 'FLUID':
            mod.settings.volume_initialization = prop_list[4]
            mod.settings.use_animated_mesh = prop_list[5]
            mod.settings.initial_velocity[0] = prop_list[6]
            mod.settings.initial_velocity[1] = prop_list[7]
            mod.settings.initial_velocity[2] = prop_list[8]

        if mod.settings.type == 'INFLOW':
            mod.settings.use = prop_list[4]
            mod.settings.volume_initialization = prop_list[5]
            mod.settings.use_animated_mesh = prop_list[6]
            mod.settings.use_local_coords = prop_list[7]
            mod.settings.inflow_velocity[0] = prop_list[8]
            mod.settings.inflow_velocity[1] = prop_list[9]
            mod.settings.inflow_velocity[2] = prop_list[10]

        if mod.settings.type == 'OUTFLOW':
            mod.settings.use = prop_list[4]
            mod.settings.volume_initialization= prop_list[5]
            mod.settings.use_animated_mesh = prop_list[6]

        if mod.settings.type == 'PARTICLE':
            mod.settings.particle_influence = prop_list[4]
            mod.settings.alpha_influence = prop_list[5]
            mod.settings.use_drops = prop_list[6]
            mod.settings.use_floats = prop_list[7]
            mod.settings.show_tracer = prop_list[8]
            mod.settings.filepath = prop_list[9]

        if mod.settings.type == 'CONTROL':
            mod.settings.use = prop_list[4]
            mod.settings.quality = prop_list[5]
            mod.settings.use_reverse_frames= prop_list[6]
            mod.settings.start_time = prop_list[7]
            mod.settings.end_time = prop_list[8]
            mod.settings.attraction_strength = prop_list[9]
            mod.settings.velocity_radius = prop_list[10]

    def add_to_ocean(self, mod, prop_list): #OCEAN Ocean 
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.geometry_mode = prop_list[4]
        mod.repeat_x = prop_list[5]
        mod.repeat_y = prop_list[6]
        mod.time = prop_list[7]
        mod.depth = prop_list[8]
        mod.random_seed = prop_list[9]
        mod.resolution = prop_list[10]
        mod.size = prop_list[11]
        mod.spatial_size = prop_list[12]
        mod.choppiness = prop_list[13]
        mod.wave_scale = prop_list[14]
        mod.wave_scale_min = prop_list[15]
        mod.wind_velocity = prop_list[16]
        mod.wave_alignment = prop_list[17]
        mod.wave_direction = prop_list[18]
        mod.damping = prop_list[19]
        mod.use_normals = prop_list[20]
        mod.use_foam = prop_list[21]
        mod.foam_coverage = prop_list[22]
        mod.foam_layer_name = prop_list[23]
        mod.frame_start = prop_list[24]
        mod.frame_end = prop_list[25]
        mod.bake_foam_fade = prop_list[26]
        mod.filepath = prop_list[27]

    def add_to_particle_instance(self, mod, prop_list): #PARTICLE_INSTANCE ParticleInstance
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.show_in_editmode = prop_list[3]
        mod.object = prop_list[4]
        mod.particle_system_index = prop_list[5]
        mod.use_normal = prop_list[6]
        mod.use_children = prop_list[7]
        mod.use_size = prop_list[8]
        mod.show_alive = prop_list[9]
        mod.show_unborn = prop_list[10]
        mod.show_dead = prop_list[11]
        mod.use_path = prop_list[12]
        mod.axis = prop_list[13]
        mod.use_preserve_shape = prop_list[14]
        mod.position = prop_list[15]
        mod.random_position = prop_list[16]

    def add_to_particle_system(self, mod, prop_list): #PARTICLE_SYSTEM  
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]

    def add_to_smoke(self, mod, prop_list): #SMOKE Smoke 
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.smoke_type = prop_list[3]

        if mod.smoke_type == 'DOMAIN':
            mod.domain_settings.resolution_max = prop_list[4]
            mod.domain_settings.time_scale = prop_list[5]
            mod.domain_settings.collision_extents = prop_list[6]
            mod.domain_settings.alpha = prop_list[7]
            mod.domain_settings.beta = prop_list[8]
            mod.domain_settings.vorticity = prop_list[9]
            mod.domain_settings.use_dissolve_smoke = prop_list[10]
            mod.domain_settings.dissolve_speed = prop_list[11]
            mod.domain_settings.use_dissolve_smoke_log = prop_list[12]
            mod.domain_settings.burning_rate = prop_list[13]
            mod.domain_settings.flame_smoke = prop_list[14]
            mod.domain_settings.flame_vorticity = prop_list[15]
            mod.domain_settings.flame_ignition = prop_list[16]
            mod.domain_settings.flame_max_temp = prop_list[17]
            mod.domain_settings.flame_smoke_color = prop_list[18]
            mod.domain_settings.use_adaptive_domain = prop_list[19]
            mod.domain_settings.additional_res = prop_list[20]
            mod.domain_settings.adapt_margin = prop_list[21]
            mod.domain_settings.adapt_threshold = prop_list[22]
            mod.domain_settings.use_high_resolution = prop_list[23]
            mod.domain_settings.amplify = prop_list[24]
            mod.domain_settings.highres_sampling = prop_list[25]
            mod.domain_settings.show_high_resolution = prop_list[26]
            mod.domain_settings.noise_type = prop_list[27]
            mod.domain_settings.strength = prop_list[28]
            mod.domain_settings.fluid_group = prop_list[29]
#            mod.settings.effector_weights.group = prop_list[30]
#            mod.settings.effector_weights.gravity = prop_list[31]
#            mod.settings.effector_weights.all = prop_list[32]
#            mod.settings.effector_weights.force = prop_list[33]
#            mod.settings.effector_weights.vortex = prop_list[34]
#            mod.settings.effector_weights.magnetic = prop_list[35]
#            mod.settings.effector_weights.wind = prop_list[36]
#            mod.settings.effector_weights.curve_guide = prop_list[37]
#            mod.settings.effector_weights.harmonic = prop_list[38]
#            mod.settings.effector_weights.charge = prop_list[39]
#            mod.settings.effector_weights.lennardjones = prop_list[40]
#            mod.settings.effector_weights.turbulence = prop_list[41]
#            mod.settings.effector_weights.drag = prop_list[42]
#            mod.settings.effector_weights.boid = prop_list[43]
#
        if mod.smoke_type == 'FLOW':
            mod.flow_settings.smoke_flow_type = prop_list[4]
            mod.flow_settings.smoke_flow_source = prop_list[5]
            mod.flow_settings.use_particle_size = prop_list[6]
            mod.flow_settings.particle_size = prop_list[7]
            mod.flow_settings.use_initial_velocity = prop_list[8]
            mod.flow_settings.velocity_factor = prop_list[9]
            mod.flow_settings.surface_distance = prop_list[10]
            mod.flow_settings.volume_density = prop_list[11]
            mod.flow_settings.velocity_normal = prop_list[12]
            mod.flow_settings.use_absolute = prop_list[13]
            mod.flow_settings.density = prop_list[14]
            mod.flow_settings.temperature = prop_list[15]
            mod.flow_settings.smoke_color= prop_list[16]
            mod.flow_settings.fuel_amount = prop_list[17]
            mod.flow_settings.subframes = prop_list[18]
            mod.flow_settings.use_texture = prop_list[19]
            mod.flow_settings.noise_texture = prop_list[20]
            mod.flow_settings.density_vertex_group = prop_list[21]
            mod.flow_settings.texture_map_type = prop_list[22]
            mod.flow_settings.uv_layer = prop_list[23]
            mod.flow_settings.texture_size = prop_list[24]
            mod.flow_settings.texture_offset = prop_list[25]
        
        if mod.smoke_type == 'COLLISION':
            mod.coll_settings.collision_type = prop_list[4]

    def add_to_soft_body(self, mod, prop_list): #SOFT_BODY Softbody
        mod.name = prop_list[0]
        mod.show_render = prop_list[1]
        mod.show_viewport = prop_list[2]
        mod.settings.friction = prop_list[3]
        mod.settings.mass = prop_list[4]
        mod.settings.vertex_group_mass = prop_list[5]
        mod.settings.collision_group = prop_list[6]
        mod.settings.speed = prop_list[7]
        bpy.context.object.frame_start = prop_list[8]
        bpy.context.object.frame_end = prop_list[9]
        bpy.context.object.frame_step = prop_list[10]
        mod.settings.use_goal = prop_list[11]
        mod.settings.goal_default = prop_list[12]
        mod.settings.goal_min = prop_list[13]
        mod.settings.goal_max = prop_list[14]
        mod.settings.goal_spring = prop_list[15]
        mod.settings.goal_friction = prop_list[16]
        mod.settings.use_edges = prop_list[17]
        mod.settings.pull = prop_list[18]
        mod.settings.push = prop_list[19]
        mod.settings.damping = prop_list[20]
        mod.settings.plastic = prop_list[21]
        mod.settings.bend = prop_list[22]
        mod.settings.spring_length = prop_list[23]
        mod.settings.vertex_group_spring = prop_list[24]
        mod.settings.use_stiff_quads = prop_list[25]
        mod.settings.shear = prop_list[26]
        mod.settings.aerodynamics_type = prop_list[27]
        mod.settings.aero = prop_list[28]
        mod.settings.use_edge_collision = prop_list[29]
        mod.settings.use_face_collision = prop_list[30]
        mod.settings.use_self_collision = prop_list[31]
        mod.settings.collision_type = prop_list[32]
        mod.settings.ball_size = prop_list[33]
        mod.settings.ball_stiff = prop_list[34]
        mod.settings.ball_damp = prop_list[35]
        mod.settings.step_min = prop_list[36]
        mod.settings.step_max = prop_list[37]
        mod.settings.use_auto_step = prop_list[38]
        mod.settings.error_threshold = prop_list[39]
        mod.settings.choke = prop_list[40]
        mod.settings.fuzzy = prop_list[41]
        mod.settings.use_diagnose = prop_list[42]
        mod.settings.use_estimate_matrix = prop_list[43]
        mod.settings.effector_weights.group = prop_list[44]
        mod.settings.effector_weights.gravity = prop_list[45]
        mod.settings.effector_weights.all = prop_list[46]
        mod.settings.effector_weights.force = prop_list[47]
        mod.settings.effector_weights.vortex = prop_list[48]
        mod.settings.effector_weights.magnetic = prop_list[49]
        mod.settings.effector_weights.wind = prop_list[50]
        mod.settings.effector_weights.curve_guide = prop_list[51]
        mod.settings.effector_weights.texture = prop_list[52]
        mod.settings.effector_weights.smokeflow = prop_list[53]
        mod.settings.effector_weights.harmonic = prop_list[54]
        mod.settings.effector_weights.charge = prop_list[55]
        mod.settings.effector_weights.lennardjones = prop_list[56]
        mod.settings.effector_weights.turbulence = prop_list[57]
        mod.settings.effector_weights.drag = prop_list[58]
        mod.settings.effector_weights.boid = prop_list[59]

##########################
#COPY FROM 
###########################

#Modify
    def copy_from_data_transfer(self, mod, prop_list): #DATA_TRANSFER DataTransfer
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.use_vert_data)
        prop_list.append(mod.vert_mapping)
        prop_list.append(mod.data_types_verts)
        prop_list.append(mod.layers_vgroup_select_src)
        prop_list.append(mod.layers_vgroup_select_dst)
        prop_list.append(mod.use_edge_data)
        prop_list.append(mod.edge_mapping)
        prop_list.append(mod.data_types_edges)
        prop_list.append(mod.use_loop_data)
        prop_list.append(mod.loop_mapping)
        prop_list.append(mod.data_types_loops)
        prop_list.append(mod.layers_vcol_select_src)
        prop_list.append(mod.layers_vcol_select_dst)
        prop_list.append(mod.layers_uv_select_src)
        prop_list.append(mod.layers_uv_select_dst)
        prop_list.append(mod.islands_precision)
        prop_list.append(mod.use_poly_data)
        prop_list.append(mod.poly_mapping)
        prop_list.append(mod.data_types_polys)
        prop_list.append(mod.max_distance)
        prop_list.append(mod.use_max_distance)
        prop_list.append(mod.ray_radius)
        prop_list.append(mod.mix_mode)
        prop_list.append(mod.mix_factor)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)

    def copy_from_mesh_cache(self, mod, prop_list): #MESH_CACHE Mesh Cache
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.cache_format)
        prop_list.append(mod.filepath)
        prop_list.append(mod.factor)
        prop_list.append(mod.deform_mode)
        prop_list.append(mod.interpolation)
        prop_list.append(mod.time_mode)
        prop_list.append(mod.play_mode)
        prop_list.append(mod.frame_start)
        prop_list.append(mod.frame_scale)
        prop_list.append(mod.eval_factor)
        prop_list.append(mod.forward_axis)
        prop_list.append(mod.up_axis)
        prop_list.append(mod.flip_axis)

    def copy_from_mesh_sequence_cache(self, mod, prop_list): #MESH_SEQUENCE_CACHE Mesh Sequence Cache
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.read_data)

    def copy_from_normal_edit(self, mod, prop_list): #NORMAL_EDIT Set Split Normals
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.mode)
        prop_list.append(mod.target)
        prop_list.append(mod.use_direction_parallel)
        prop_list.append(mod.offset[0])
        prop_list.append(mod.offset[1])
        prop_list.append(mod.offset[2])
        prop_list.append(mod.mix_mode)
        prop_list.append(mod.mix_factor)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.mix_limit)

    def copy_from_uv_project(self, mod, prop_list): #UV_PROJECT UVProject
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.uv_layer)
        prop_list.append(mod.use_image_override)
        prop_list.append(mod.projector_count)
        prop_list.append(mod.aspect_x)
        prop_list.append(mod.aspect_y)
        prop_list.append(mod.scale_x)
        prop_list.append(mod.scale_y)

    def copy_from_uv_warp(self, mod, prop_list): #UV_WARP UVWarp
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.center[0])
        prop_list.append(mod.center[1])
        prop_list.append(mod.axis_u)
        prop_list.append(mod.axis_v)
        prop_list.append(mod.object_from)
        prop_list.append(mod.object_to)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.uv_layer)

    def copy_from_vertex_weight_edit(self, mod, prop_list): #VERTEXT_WEIGHT_EDIT VertexWeightEdit
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.use_add)
        prop_list.append(mod.add_threshold)
        prop_list.append(mod.use_remove)
        prop_list.append(mod.remove_threshold)
        prop_list.append(mod.default_weight)
        prop_list.append(mod.falloff_type)
        prop_list.append(mod.mask_constant)
        prop_list.append(mod.mask_vertex_group)

    def copy_from_vertex_weight_mix(self, mod, prop_list): #VERTEX_WEIGHT_MIX VertexWeightMix
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.vertex_group_a)
        prop_list.append(mod.vertex_group_b)
        prop_list.append(mod.default_weight_a)
        prop_list.append(mod.default_weight_b)
        prop_list.append(mod.mix_mode)
        prop_list.append(mod.mix_set)
        prop_list.append(mod.mask_constant)
        prop_list.append(mod.mask_vertex_group)

    def copy_from_vertex_weight_proximity(self, mod, prop_list): #VERTEX_WEIGHT_PROXIMITY VertexWeightProximity
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.target)
        prop_list.append(mod.proximity_mode)
        prop_list.append(mod.proximity_geometry)
        prop_list.append(mod.min_dist)
        prop_list.append(mod.max_dist)
        prop_list.append(mod.falloff_type)
        prop_list.append(mod.mask_constant)
        prop_list.append(mod.mask_vertex_group)
        prop_list.append(mod.mask_tex_mapping)
        prop_list.append(mod.mask_tex_use_channel)

#Generate
    def copy_from_array(self, mod, prop_list): #ARRAY Array
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.fit_type)
        prop_list.append(mod.curve)
        prop_list.append(mod.fit_length)
        prop_list.append(mod.use_constant_offset)
        prop_list.append(mod.constant_offset_displace[0])
        prop_list.append(mod.constant_offset_displace[1])
        prop_list.append(mod.constant_offset_displace[2])
        prop_list.append(mod.use_relative_offset)
        prop_list.append(mod.relative_offset_displace[0])
        prop_list.append(mod.relative_offset_displace[1])
        prop_list.append(mod.relative_offset_displace[2])
        prop_list.append(mod.use_merge_vertices)
        prop_list.append(mod.use_merge_vertices_cap)
        prop_list.append(mod.use_object_offset)
        prop_list.append(mod.offset_object)
        prop_list.append(mod.merge_threshold)
        prop_list.append(mod.start_cap)
        prop_list.append(mod.end_cap)

    def copy_from_bevel(self, mod, prop_list): #BEVEL Bevel
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.width)
        prop_list.append(mod.segments)
        prop_list.append(mod.profile)
        prop_list.append(mod.material)
        prop_list.append(mod.use_only_vertices)
        prop_list.append(mod.use_clamp_overlap)
        prop_list.append(mod.loop_slide)
        prop_list.append(mod.limit_method)
        prop_list.append(mod.angle_limit)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.offset_type)

    def copy_from_boolean(self, mod, prop_list): #BOOLEAN boolean
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.operation)
        prop_list.append(mod.object)

    def copy_from_build(self, mod, prop_list): #BUILD Build
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.frame_start)
        prop_list.append(mod.frame_duration)
        prop_list.append(mod.use_random_order)
        prop_list.append(mod.seed)
        prop_list.append(mod.use_reverse)

    def copy_from_decimate(self, mod, prop_list): #DECIMATE Decimate
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.decimate_type)
        prop_list.append(mod.ratio)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.vertex_group_factor)
        prop_list.append(mod.use_collapse_triangulate)
        prop_list.append(mod.use_symmetry)
        prop_list.append(mod.symmetry_axis)
        prop_list.append(mod.iterations)
        prop_list.append(mod.angle_limit)
        prop_list.append(mod.use_dissolve_boundaries)
        prop_list.append(mod.delimit)

    def copy_from_edge_split(self, mod, prop_list): #EDGE_SPLIT EdgeSplit
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.use_edge_angle)
        prop_list.append(mod.split_angle)
        prop_list.append(mod.use_edge_sharp)

    def copy_from_mask(self, mod, prop_list): #MASK Mask
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.mode)
        prop_list.append(mod.armature)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.vertex_group)

    def copy_from_mirror(self, mod, prop_list): #MIRROR Mirror
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.use_x)
        prop_list.append(mod.use_y)
        prop_list.append(mod.use_z)
        prop_list.append(mod.use_mirror_merge)
        prop_list.append(mod.use_clip)
        prop_list.append(mod.use_mirror_vertex_groups)
        prop_list.append(mod.use_mirror_u)
        prop_list.append(mod.use_mirror_v)
        prop_list.append(mod.mirror_object)

    def copy_from_multires(self, mod, prop_list): #MULTIRES Multires
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.subdivision_type)
        prop_list.append(mod.levels)
        prop_list.append(mod.sculpt_levels)
        prop_list.append(mod.render_levels)
        prop_list.append(mod.use_subsurf_uv)
        prop_list.append(mod.show_only_control_edges)

    def copy_from_remesh(self, mod, prop_list): #REMESH Remesh
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.mode)
        prop_list.append(mod.octree_depth)
        prop_list.append(mod.scale)
        prop_list.append(mod.sharpness)
        prop_list.append(mod.use_smooth_shade)
        prop_list.append(mod.use_remove_disconnected)
        prop_list.append(mod.threshold)

    def copy_from_screw(self, mod, prop_list): #SCREW Screw
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.axis)
        prop_list.append(mod.object)
        prop_list.append(mod.angle)
        prop_list.append(mod.steps)
        prop_list.append(mod.render_steps)
        prop_list.append(mod.use_smooth_shade)
        prop_list.append(mod.screw_offset)
        prop_list.append(mod.use_object_screw_offset)
        prop_list.append(mod.use_normal_calculate)
        prop_list.append(mod.use_normal_flip)
        prop_list.append(mod.iterations)
        prop_list.append(mod.use_stretch_u)
        prop_list.append(mod.use_stretch_v)

    def copy_from_skin(self, mod, prop_list): #SKIN Skin
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.branch_smoothing)
        prop_list.append(mod.use_smooth_shade)
        prop_list.append(mod.use_x_symmetry)
        prop_list.append(mod.use_y_symmetry)
        prop_list.append(mod.use_z_symmetry)

    def copy_from_solidify(self, mod, prop_list): #SOLIDIFY Solidify
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.thickness)
        prop_list.append(mod.thickness_clamp)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.thickness_vertex_group)
        prop_list.append(mod.edge_crease_inner)
        prop_list.append(mod.edge_crease_outer)
        prop_list.append(mod.edge_crease_rim)
        prop_list.append(mod.offset)
        prop_list.append(mod.use_flip_normals)
        prop_list.append(mod.use_even_offset)
        prop_list.append(mod.use_quality_normals)
        prop_list.append(mod.use_rim)
        prop_list.append(mod.use_rim_only)
        prop_list.append(mod.material_offset)
        prop_list.append(mod.material_offset_rim)

    def copy_from_subsurf(self, mod, prop_list): #SUBSURF Subsurf
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.subdivision_type)
        prop_list.append(mod.levels)
        prop_list.append(mod.render_levels)
        prop_list.append(mod.use_subsurf_uv)
        prop_list.append(mod.show_only_control_edges)

    def copy_from_triangulate(self, mod, prop_list): #TRIANGULATE Triangulate
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.quad_method)
        prop_list.append(mod.ngon_method)

    def copy_from_wireframe(self, mod, prop_list): #WIREFRAME Wireframe
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.thickness)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.thickness_vertex_group)
        prop_list.append(mod.use_crease)
        prop_list.append(mod.crease_weight)
        prop_list.append(mod.offset)
        prop_list.append(mod.use_even_offset)
        prop_list.append(mod.use_relative_offset)
        prop_list.append(mod.use_boundary)
        prop_list.append(mod.use_replace)
        prop_list.append(mod.material_offset)

#Deform
    def copy_from_armature(self, mod, prop_list): #ARMATURE Aramature
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object)
        prop_list.append(mod.use_deform_preserve_volume)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.use_vertex_groups)
        prop_list.append(mod.use_bone_envelopes)
        prop_list.append(mod.use_multi_modifier)

    def copy_from_cast(self, mod, prop_list): #CAST Cast
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.cast_type)
        prop_list.append(mod.use_x)
        prop_list.append(mod.use_y)
        prop_list.append(mod.use_z)
        prop_list.append(mod.factor)
        prop_list.append(mod.radius)
        prop_list.append(mod.size)
        prop_list.append(mod.use_radius_as_size)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.object)

    def copy_from_corrective_smooth(self, mod, prop_list): #CORRECTIVE_SMOOTH CorrectiveSmooth
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.factor)
        prop_list.append(mod.iterations)
        prop_list.append(mod.smooth_type)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.use_only_smooth)
        prop_list.append(mod.use_pin_boundary)
        prop_list.append(mod.rest_source)

    def copy_from_curve(self, mod, prop_list): #CURVE Curve
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.deform_axis)

    def copy_from_displace(self, mod, prop_list): #DISPLACE Displace
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.direction)
        prop_list.append(mod.texture_coords)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.texture_coords_object)
        prop_list.append(mod.mid_level)
        prop_list.append(mod.strength)

    def copy_from_hook(self, mod, prop_list): #HOOK Hook
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.falloff_radius)
        prop_list.append(mod.strength)
        prop_list.append(mod.falloff_type)
        prop_list.append(mod.use_falloff_uniform)

    def copy_from_laplacian_smooth(self, mod, prop_list):  #LAPLACIANSMOOTH Laplacian Smooth
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.iterations)
        prop_list.append(mod.use_x)
        prop_list.append(mod.use_y)
        prop_list.append(mod.use_z)
        prop_list.append(mod.lambda_factor)
        prop_list.append(mod.lambda_border)
        prop_list.append(mod.use_volume_preserve)
        prop_list.append(mod.use_normalized)
        prop_list.append(mod.vertex_group)

    def copy_from_laplacian_deform(self, mod, prop_list):  #LAPLACIANDEFORM LaplacianDeform
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.iterations)
        prop_list.append(mod.vertex_group)

    def copy_from_lattice(self, mod, prop_list): #LATTICE Lattice
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.strength)

    def copy_from_mesh_deform(self, mod, prop_list): #MESH_DEFORM MeshDeform
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.precision)
        prop_list.append(mod.use_dynamic_bind)

    def copy_from_shrinkwrap(self, mod, prop_list): #SHRINKWRAP Shrinkwrap
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.target)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.offset)
        prop_list.append(mod.wrap_method)
        prop_list.append(mod.use_keep_above_surface)
        prop_list.append(mod.subsurf_levels)
        prop_list.append(mod.project_limit)
        prop_list.append(mod.use_project_x)
        prop_list.append(mod.use_project_y)
        prop_list.append(mod.use_project_z)
        prop_list.append(mod.use_negative_direction)
        prop_list.append(mod.use_positive_direction)
        prop_list.append(mod.cull_face)
        prop_list.append(mod.auxiliary_target)

    def copy_from_simple_deform(self, mod, prop_list): #SIMPLE_DEFORM SimpleDeform
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.deform_method)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.invert_vertex_group)
        prop_list.append(mod.origin)
        prop_list.append(mod.lock_x)
        prop_list.append(mod.lock_y)
        prop_list.append(mod.angle)
        prop_list.append(mod.limits[0])
        prop_list.append(mod.limits[1])

    def copy_from_smooth(self, mod, prop_list): #SMOOTH Smooth
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.use_x)
        prop_list.append(mod.use_y)
        prop_list.append(mod.use_z)
        prop_list.append(mod.factor)
        prop_list.append(mod.iterations)
        prop_list.append(mod.vertex_group)

    def copy_from_warp(self, mod, prop_list): #WARP Warp 
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object_from)
        prop_list.append(mod.object_to)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.strength)
        prop_list.append(mod.falloff_radius)
        prop_list.append(mod.falloff_type)
        prop_list.append(mod.texture_coords)
        prop_list.append(mod.texture_coords_object)
        prop_list.append(mod.uv_layer)

    def copy_from_wave(self, mod, prop_list): #WAVE Wave
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.show_on_cage)
        prop_list.append(mod.use_x)
        prop_list.append(mod.use_y)
        prop_list.append(mod.use_cyclic)
        prop_list.append(mod.use_normal)
        prop_list.append(mod.use_normal_x)
        prop_list.append(mod.use_normal_y)
        prop_list.append(mod.use_normal_z)
        prop_list.append(mod.time_offset)
        prop_list.append(mod.lifetime)
        prop_list.append(mod.damping_time)
        prop_list.append(mod.start_position_x)
        prop_list.append(mod.start_position_y)
        prop_list.append(mod.falloff_radius)
        prop_list.append(mod.start_position_object)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.texture_coords)
        prop_list.append(mod.texture_coords_object)
        prop_list.append(mod.uv_layer)
        prop_list.append(mod.speed)
        prop_list.append(mod.width)
        prop_list.append(mod.height)
        prop_list.append(mod.narrowness)

#Simulate
    def copy_from_cloth(self, mod, prop_list): #CLOTH Cloth
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.settings.quality)
        prop_list.append(mod.settings.time_scale)
        prop_list.append(mod.settings.mass)
        prop_list.append(mod.settings.structural_stiffness)
        prop_list.append(mod.settings.bending_stiffness)
        prop_list.append(mod.settings.spring_damping)
        prop_list.append(mod.settings.air_damping)
        prop_list.append(mod.settings.vel_damping)
        prop_list.append(mod.settings.use_pin_cloth)
        prop_list.append(mod.settings.vertex_group_mass)
        prop_list.append(mod.settings.pin_stiffness)
        prop_list.append(mod.settings.use_dynamic_mesh)
        prop_list.append(mod.collision_settings.use_collision)
        prop_list.append(mod.collision_settings.collision_quality)
        prop_list.append(mod.collision_settings.distance_min)
        prop_list.append(mod.collision_settings.repel_force)
        prop_list.append(mod.collision_settings.distance_repel)
        prop_list.append(mod.collision_settings.friction)
        prop_list.append(mod.collision_settings.use_self_collision)
        prop_list.append(mod.collision_settings.self_collision_quality)
        prop_list.append(mod.collision_settings.self_distance_min)
        prop_list.append(mod.collision_settings.vertex_group_self_collisions)
        prop_list.append(mod.collision_settings.group)
        prop_list.append(mod.settings.use_stiffness_scale)
        prop_list.append(mod.settings.vertex_group_structural_stiffness)
        prop_list.append(mod.settings.structural_stiffness_max)
        prop_list.append(mod.settings.vertex_group_bending)
        prop_list.append(mod.settings.bending_stiffness_max)
        prop_list.append(mod.settings.use_sewing_springs)
        prop_list.append(mod.settings.sewing_force_max)
        prop_list.append(mod.settings.vertex_group_shrink)
        prop_list.append(mod.settings.shrink_min)
        prop_list.append(mod.settings.shrink_max)
        prop_list.append(mod.settings.effector_weights.group)
        prop_list.append(mod.settings.effector_weights.gravity)
        prop_list.append(mod.settings.effector_weights.all)
        prop_list.append(mod.settings.effector_weights.force)
        prop_list.append(mod.settings.effector_weights.vortex)
        prop_list.append(mod.settings.effector_weights.magnetic)
        prop_list.append(mod.settings.effector_weights.wind)
        prop_list.append(mod.settings.effector_weights.curve_guide)
        prop_list.append(mod.settings.effector_weights.texture)
        prop_list.append(mod.settings.effector_weights.smokeflow)
        prop_list.append(mod.settings.effector_weights.harmonic)
        prop_list.append(mod.settings.effector_weights.charge)
        prop_list.append(mod.settings.effector_weights.lennardjones)
        prop_list.append(mod.settings.effector_weights.turbulence)
        prop_list.append(mod.settings.effector_weights.drag)
        prop_list.append(mod.settings.effector_weights.boid)

    def copy_from_collision(self, mod, prop_list): #COLLISION Collision
        prop_list.append(mod.name)
        prop_list.append(bpy.context.object.collision.permeability)
        prop_list.append(bpy.context.object.collision.stickiness)
        prop_list.append(bpy.context.object.collision.use_particle_kill)
        prop_list.append(bpy.context.object.collision.damping_factor)
        prop_list.append(bpy.context.object.collision.damping_random)
        prop_list.append(bpy.context.object.collision.friction_factor)
        prop_list.append(bpy.context.object.collision.friction_random)
        prop_list.append(bpy.context.object.collision.thickness_outer)
        prop_list.append(bpy.context.object.collision.thickness_inner)
        prop_list.append(bpy.context.object.collision.damping)
        prop_list.append(bpy.context.object.collision.absorption)

    def copy_from_dynamic_paint(self, mod, prop_list): #DYNAMIC_PAINT Dynamic Paint 
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.ui_type)

    def copy_from_explode(self, mod, prop_list): #EXPLODE Explode
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.vertex_group)
        prop_list.append(mod.protect)
        prop_list.append(mod.particle_uv)
        prop_list.append(mod.use_edge_cut)
        prop_list.append(mod.show_unborn)
        prop_list.append(mod.show_alive)
        prop_list.append(mod.show_dead)
        prop_list.append(mod.use_size)

    def copy_from_fluid_simulation(self, mod, prop_list): #FLUID_SIMULATION Fluidsim
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.settings.type)

        if mod.settings.type == 'DOMAIN':
            prop_list.append(mod.settings.threads)
            prop_list.append(mod.settings.resolution)
            prop_list.append(mod.settings.preview_resolution)
            prop_list.append(mod.settings.render_display_mode)
            prop_list.append(mod.settings.viewport_display_mode)
            prop_list.append(mod.settings.start_time)
            prop_list.append(mod.settings.end_time)
            prop_list.append(mod.settings.use_speed_vectors)
            prop_list.append(mod.settings.use_reverse_frames)
            prop_list.append(mod.settings.simulation_rate)
            prop_list.append(mod.settings.frame_offset)
            prop_list.append(mod.settings.filepath)
            prop_list.append(mod.settings.viscosity_base)
            prop_list.append(mod.settings.viscosity_exponent)
            prop_list.append(mod.settings.simulation_scale)
            prop_list.append(mod.settings.grid_levels)
            prop_list.append(mod.settings.compressibility)
            prop_list.append(mod.settings.slip_type)
            prop_list.append(mod.settings.partial_slip_factor)
            prop_list.append(mod.settings.use_surface_noobs)
            prop_list.append(mod.settings.surface_smooth)
            prop_list.append(mod.settings.surface_subdivisions)
            prop_list.append(mod.settings.tracer_particles)
            prop_list.append(mod.settings.generate_particles)

        if mod.settings.type == 'FLUID':
            prop_list.append(mod.settings.volume_initialization)
            prop_list.append(mod.settings.use_animated_mesh)
            prop_list.append(mod.settings.initial_velocity[0])
            prop_list.append(mod.settings.initial_velocity[1])
            prop_list.append(mod.settings.initial_velocity[2])

        if mod.settings.type == 'INFLOW':
            prop_list.append(mod.settings.use)
            prop_list.append(mod.settings.volume_initialization)
            prop_list.append(mod.settings.use_animated_mesh)
            prop_list.append(mod.settings.use_local_coords)
            prop_list.append(mod.settings.inflow_velocity[0])
            prop_list.append(mod.settings.inflow_velocity[1])
            prop_list.append(mod.settings.inflow_velocity[2])

        if mod.settings.type == 'OUTFLOW':
            prop_list.append(mod.settings.use)
            prop_list.append(mod.settings.volume_initialization)
            prop_list.append(mod.settings.use_animated_mesh)

        if mod.settings.type == 'PARTICLE':
            prop_list.append(mod.settings.particle_influence)
            prop_list.append(mod.settings.alpha_influence)
            prop_list.append(mod.settings.use_drops)
            prop_list.append(mod.settings.use_floats)
            prop_list.append(mod.settings.show_tracer)
            prop_list.append(mod.settings.filepath)

        if mod.settings.type == 'CONTROL':
            prop_list.append(mod.settings.use)
            prop_list.append(mod.settings.quality)
            prop_list.append(mod.settings.use_reverse_frames)
            prop_list.append(mod.settings.start_time)
            prop_list.append(mod.settings.end_time)
            prop_list.append(mod.settings.attraction_strength)
            prop_list.append(mod.settings.velocity_radius)

    def copy_from_ocean(self, mod, prop_list): #OCEAN Ocean 
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.geometry_mode)
        prop_list.append(mod.repeat_x)
        prop_list.append(mod.repeat_y)
        prop_list.append(mod.time)
        prop_list.append(mod.depth)
        prop_list.append(mod.random_seed)
        prop_list.append(mod.resolution)
        prop_list.append(mod.size)
        prop_list.append(mod.spatial_size)
        prop_list.append(mod.choppiness)
        prop_list.append(mod.wave_scale)
        prop_list.append(mod.wave_scale_min)
        prop_list.append(mod.wind_velocity)
        prop_list.append(mod.wave_alignment)
        prop_list.append(mod.wave_direction)
        prop_list.append(mod.damping)
        prop_list.append(mod.use_normals)
        prop_list.append(mod.use_foam)
        prop_list.append(mod.foam_coverage)
        prop_list.append(mod.foam_layer_name)
        prop_list.append(mod.frame_start)
        prop_list.append(mod.frame_end)
        prop_list.append(mod.bake_foam_fade)
        prop_list.append(mod.filepath)

    def copy_from_particle_instance(self, mod, prop_list): #PARTICLE_INSTANCE ParticleInstance
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.show_in_editmode)
        prop_list.append(mod.object)
        prop_list.append(mod.particle_system_index)
        prop_list.append(mod.use_normal)
        prop_list.append(mod.use_children)
        prop_list.append(mod.use_size)
        prop_list.append(mod.show_alive)
        prop_list.append(mod.show_unborn)
        prop_list.append(mod.show_dead)
        prop_list.append(mod.use_path)
        prop_list.append(mod.axis)
        prop_list.append(mod.use_preserve_shape)
        prop_list.append(mod.position)
        prop_list.append(mod.random_position)

    def copy_from_particle_system(self, mod, prop_list): #PARTICLE_SYSTEM  
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)

    def copy_from_smoke(self, mod, prop_list): #SMOKE Smoke 
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.smoke_type)

        if mod.smoke_type == 'DOMAIN':
            prop_list.append(mod.domain_settings.resolution_max)
            prop_list.append(mod.domain_settings.time_scale)
            prop_list.append(mod.domain_settings.collision_extents)
            prop_list.append(mod.domain_settings.alpha)
            prop_list.append(mod.domain_settings.beta)
            prop_list.append(mod.domain_settings.vorticity)
            prop_list.append(mod.domain_settings.use_dissolve_smoke)
            prop_list.append(mod.domain_settings.dissolve_speed)
            prop_list.append(mod.domain_settings.use_dissolve_smoke_log)
            prop_list.append(mod.domain_settings.burning_rate)
            prop_list.append(mod.domain_settings.flame_smoke)
            prop_list.append(mod.domain_settings.flame_vorticity)
            prop_list.append(mod.domain_settings.flame_ignition)
            prop_list.append(mod.domain_settings.flame_max_temp)
            prop_list.append(mod.domain_settings.flame_smoke_color)
            prop_list.append(mod.domain_settings.use_adaptive_domain)
            prop_list.append(mod.domain_settings.additional_res)
            prop_list.append(mod.domain_settings.adapt_margin)
            prop_list.append(mod.domain_settings.adapt_threshold)
            prop_list.append(mod.domain_settings.use_high_resolution)
            prop_list.append(mod.domain_settings.amplify)
            prop_list.append(mod.domain_settings.highres_sampling)
            prop_list.append(mod.domain_settings.show_high_resolution)
            prop_list.append(mod.domain_settings.noise_type)
            prop_list.append(mod.domain_settings.strength)
            prop_list.append(mod.domain_settings.fluid_group)
#            prop_list.append(mod.settings.effector_weights.group)
#            prop_list.append(mod.settings.effector_weights.gravity)
#            prop_list.append(mod.settings.effector_weights.all)
#            prop_list.append(mod.settings.effector_weights.force)
#            prop_list.append(mod.settings.effector_weights.vortex)
#            prop_list.append(mod.settings.effector_weights.magnetic)
#            prop_list.append(mod.settings.effector_weights.wind)
#            prop_list.append(mod.settings.effector_weights.curve_guide)
#            prop_list.append(mod.settings.effector_weights.harmonic)
#            prop_list.append(mod.settings.effector_weights.charge)
#            prop_list.append(mod.settings.effector_weights.lennardjones)
#            prop_list.append(mod.settings.effector_weights.turbulence)
#            prop_list.append(mod.settings.effector_weights.drag)

        if mod.smoke_type == 'FLOW':
            prop_list.append(mod.flow_settings.smoke_flow_type)
            prop_list.append(mod.flow_settings.smoke_flow_source)
            prop_list.append(mod.flow_settings.use_particle_size)
            prop_list.append(mod.flow_settings.particle_size)
            prop_list.append(mod.flow_settings.use_initial_velocity)
            prop_list.append(mod.flow_settings.velocity_factor)
            prop_list.append(mod.flow_settings.surface_distance)
            prop_list.append(mod.flow_settings.volume_density)
            prop_list.append(mod.flow_settings.velocity_normal)
            prop_list.append(mod.flow_settings.use_absolute)
            prop_list.append(mod.flow_settings.density)
            prop_list.append(mod.flow_settings.temperature)
            prop_list.append(mod.flow_settings.smoke_color)
            prop_list.append(mod.flow_settings.fuel_amount)
            prop_list.append(mod.flow_settings.subframes)
            prop_list.append(mod.flow_settings.use_texture)
            prop_list.append(mod.flow_settings.noise_texture)
            prop_list.append(mod.flow_settings.density_vertex_group)
            prop_list.append(mod.flow_settings.texture_map_type)
            prop_list.append(mod.flow_settings.uv_layer)
            prop_list.append(mod.flow_settings.texture_size)
            prop_list.append(mod.flow_settings.texture_offset)

        if mod.smoke_type == 'COLLISION':
            prop_list.append(mod.coll_settings.collision_type)

    def copy_from_soft_body(self, mod, prop_list): #SOFT_BODY Softbody
        prop_list.append(mod.name)
        prop_list.append(mod.show_render)
        prop_list.append(mod.show_viewport)
        prop_list.append(mod.settings.friction)
        prop_list.append(mod.settings.mass)
        prop_list.append(mod.settings.vertex_group_mass)
        prop_list.append(mod.settings.collision_group)
        prop_list.append(mod.settings.speed)
        prop_list.append(bpy.context.object.frame_start)
        prop_list.append(bpy.context.object.frame_end)
        prop_list.append(bpy.context.object.frame_step)
        prop_list.append(mod.settings.use_goal)
        prop_list.append(mod.settings.goal_default)
        prop_list.append(mod.settings.goal_min)
        prop_list.append(mod.settings.goal_max)
        prop_list.append(mod.settings.goal_spring)
        prop_list.append(mod.settings.goal_friction)
        prop_list.append(mod.settings.use_edges)
        prop_list.append(mod.settings.pull)
        prop_list.append(mod.settings.push)
        prop_list.append(mod.settings.damping)
        prop_list.append(mod.settings.plastic)
        prop_list.append(mod.settings.bend)
        prop_list.append(mod.settings.spring_length)
        prop_list.append(mod.settings.vertex_group_spring)
        prop_list.append(mod.settings.use_stiff_quads)
        prop_list.append(mod.settings.shear)
        prop_list.append(mod.settings.aerodynamics_type)
        prop_list.append(mod.settings.aero)
        prop_list.append(mod.settings.use_edge_collision)
        prop_list.append(mod.settings.use_face_collision)
        prop_list.append(mod.settings.use_self_collision)
        prop_list.append(mod.settings.collision_type)
        prop_list.append(mod.settings.ball_size)
        prop_list.append(mod.settings.ball_stiff)
        prop_list.append(mod.settings.ball_damp)
        prop_list.append(mod.settings.step_min)
        prop_list.append(mod.settings.step_max)
        prop_list.append(mod.settings.use_auto_step)
        prop_list.append(mod.settings.error_threshold)
        prop_list.append(mod.settings.choke)
        prop_list.append(mod.settings.fuzzy)
        prop_list.append(mod.settings.use_diagnose)
        prop_list.append(mod.settings.use_estimate_matrix)
        prop_list.append(mod.settings.effector_weights.group)
        prop_list.append(mod.settings.effector_weights.gravity)
        prop_list.append(mod.settings.effector_weights.all)
        prop_list.append(mod.settings.effector_weights.force)
        prop_list.append(mod.settings.effector_weights.vortex)
        prop_list.append(mod.settings.effector_weights.magnetic)
        prop_list.append(mod.settings.effector_weights.wind)
        prop_list.append(mod.settings.effector_weights.curve_guide)
        prop_list.append(mod.settings.effector_weights.texture)
        prop_list.append(mod.settings.effector_weights.smokeflow)
        prop_list.append(mod.settings.effector_weights.harmonic)
        prop_list.append(mod.settings.effector_weights.charge)
        prop_list.append(mod.settings.effector_weights.lennardjones)
        prop_list.append(mod.settings.effector_weights.turbulence)
        prop_list.append(mod.settings.effector_weights.drag)
        prop_list.append(mod.settings.effector_weights.boid)

    def __init__(self, mod = None, mod_cache = None):
        self.prop_list = []

        if mod:
            self.mod_type = mod.type
    #Modify
            if self.mod_type == 'DATA_TRANSFER':
                self.copy_from_data_transfer(mod, self.prop_list)

            elif self.mod_type == 'MESH_CACHE':
                self.copy_from_mesh_cache(mod, self.prop_list)

            elif self.mod_type == 'MESH_SEQUENCE_CACHE':
                self.copy_from_mesh_sequence_cache(mod, self.prop_list)

            elif self.mod_type == 'NORMAL_EDIT':
                self.copy_from_normal_edit(mod, self.prop_list)

            elif self.mod_type == 'UV_PROJECT':
                self.copy_from_uv_project(mod, self.prop_list)

            elif self.mod_type == 'UV_WARP':
                self.copy_from_uv_warp(mod, self.prop_list)

            elif self.mod_type == 'VERTEX_WEIGHT_EDIT':
                self.copy_from_vertex_weight_edit(mod, self.prop_list)

            elif self.mod_type == 'VERTEX_WEIGHT_MIX':
                self.copy_from_vertex_weight_mix(mod, self.prop_list)

            elif self.mod_type == 'VERTEX_WEIGHT_PROXIMITY':
                self.copy_from_vertex_weight_proximity(mod, self.prop_list)
    #Generate
            elif self.mod_type == 'ARRAY':
                self.copy_from_array(mod, self.prop_list)

            elif self.mod_type == 'BEVEL':
                self.copy_from_bevel(mod, self.prop_list)

            elif self.mod_type == 'BOOLEAN':
                self.copy_from_boolean(mod, self.prop_list)

            elif self.mod_type == 'BUILD':
                self.copy_from_build(mod, self.prop_list)

            elif self.mod_type == 'DECIMATE':
                self.copy_from_decimate(mod, self.prop_list)

            elif self.mod_type == 'EDGE_SPLIT':
                self.copy_from_edge_split(mod, self.prop_list)

            elif self.mod_type == 'MASK':
                self.copy_from_mask(mod, self.prop_list)

            elif self.mod_type == 'MIRROR':
                self.copy_from_mirror(mod, self.prop_list)

            elif self.mod_type == 'MULTIRES':
                self.copy_from_multires(mod, self.prop_list)

            elif self.mod_type == 'REMESH':
                self.copy_from_remesh(mod, self.prop_list)

            elif self.mod_type == 'SCREW':
                self.copy_from_screw(mod, self.prop_list)

            elif self.mod_type == 'SKIN':
                self.copy_from_skin(mod, self.prop_list)

            elif self.mod_type == 'SOLIDIFY':
                self.copy_from_solidify(mod, self.prop_list)

            elif self.mod_type == 'SUBSURF':
                self.copy_from_subsurf(mod, self.prop_list)

            elif self.mod_type == 'TRIANGULATE':
                self.copy_from_triangulate(mod, self.prop_list)

            elif self.mod_type == 'WIREFRAME':
                self.copy_from_wireframe(mod, self.prop_list)
    #Deform
            elif self.mod_type == 'ARMATURE':
                self.copy_from_armature(mod, self.prop_list)

            elif self.mod_type == 'CAST':
                self.copy_from_cast(mod, self.prop_list)

            elif self.mod_type == 'CORRECTIVE_SMOOTH':
                self.copy_from_corrective_smooth(mod, self.prop_list)

            elif self.mod_type == 'CURVE':
                self.copy_from_curve(mod, self.prop_list)

            elif self.mod_type == 'DISPLACE':
                self.copy_from_displace(mod, self.prop_list)

            elif self.mod_type == 'HOOK':
                self.copy_from_hook(mod, self.prop_list)

            elif self.mod_type == 'LAPLACIANSMOOTH':
                self.copy_from_laplacian_smooth(mod, self.prop_list)

            elif self.mod_type == 'LAPLACIANDEFORM':
                self.copy_from_laplacian_deform(mod, self.prop_list)

            elif self.mod_type == 'LATTICE':
                self.copy_from_lattice(mod, self.prop_list)

            elif self.mod_type == 'MESH_DEFORM':
                self.copy_from_mesh_deform(mod, self.prop_list)

            elif self.mod_type == 'SHRINKWRAP':
                self.copy_from_shrinkwrap(mod, self.prop_list)

            elif self.mod_type == 'SIMPLE_DEFORM':
                self.copy_from_simple_deform(mod, self.prop_list)

            elif self.mod_type == 'SMOOTH':
                self.copy_from_smooth(mod, self.prop_list)

            elif self.mod_type == 'WARP':
                self.copy_from_warp(mod, self.prop_list)

            elif self.mod_type == 'WAVE':
                self.copy_from_wave(mod, self.prop_list)
    #Simulate
            elif self.mod_type == 'CLOTH':
                self.copy_from_cloth(mod, self.prop_list)

            elif self.mod_type == 'COLLISION':
                self.copy_from_collision(mod, self.prop_list)

            elif self.mod_type == 'DYNAMIC_PAINT':
                self.copy_from_dynamic_paint(mod, self.prop_list)

            elif self.mod_type == 'EXPLODE':
                self.copy_from_explode(mod, self.prop_list)

            elif self.mod_type == 'FLUID_SIMULATION':
                self.copy_from_fluid_simulation(mod, self.prop_list)

            elif self.mod_type == 'OCEAN':
                self.copy_from_ocean(mod, self.prop_list)

            elif self.mod_type == 'PARTICLE_INSTANCE':
                self.copy_from_particle_instance(mod, self.prop_list)

            elif self.mod_type == 'PARTICLE_SYSTEM':
                self.copy_from_particle_system(mod, self.prop_list)

            elif self.mod_type == 'SMOKE':
                self.copy_from_smoke(mod, self.prop_list)

            elif self.mod_type == 'SOFT_BODY':
                self.copy_from_soft_body(mod, self.prop_list)

        if mod_cache:
            self.mod_type = mod_cache.mod_type
            self.restore_from_prop_cache(mod_cache.props)

    def apply(self, mod):
#Modify
        if self.mod_type == 'DATA_TRANSFER':
            self.add_to_data_transfer(mod, self.prop_list)

        elif self.mod_type == 'MESH_CACHE':
            self.add_to_mesh_cache(mod, self.prop_list)

        elif self.mod_type == 'MESH_SEQUENCE_CACHE':
            self.add_to_mesh_sequence_cache(mod, self.prop_list)

        elif self.mod_type == 'NORMAL_EDIT':
            self.add_to_normal_edit(mod, self.prop_list)

        elif self.mod_type == 'UV_PROJECT':
            self.add_to_uv_project(mod, self.prop_list)

        elif self.mod_type == 'UV_WARP':
            self.add_to_uv_warp(mod, self.prop_list)

        elif self.mod_type == 'VERTEX_WEIGHT_EDIT':
            self.add_to_vertex_weight_edit(mod, self.prop_list)

        elif self.mod_type == 'VERTEX_WEIGHT_MIX':
            self.add_to_vertex_weight_mix(mod, self.prop_list)

        elif self.mod_type == 'VERTEX_WEIGHT_PROXIMITY':
            self.add_to_vertex_weight_proximity(mod, self.prop_list)
#Generate
        elif self.mod_type == 'ARRAY':
            self.add_to_array(mod, self.prop_list)

        elif self.mod_type == 'BEVEL':
            self.add_to_bevel(mod, self.prop_list)

        elif self.mod_type == 'BOOLEAN':
            self.add_to_boolean(mod, self.prop_list)

        elif self.mod_type == 'BUILD':
            self.add_to_build(mod, self.prop_list)

        elif self.mod_type == 'DECIMATE':
            self.add_to_decimate(mod, self.prop_list)

        elif self.mod_type == 'EDGE_SPLIT':
            self.add_to_edge_split(mod, self.prop_list)

        elif self.mod_type == 'MASK':
            self.add_to_mask(mod, self.prop_list)

        elif self.mod_type == 'MIRROR':
            self.add_to_mirror(mod, self.prop_list)

        elif self.mod_type == 'MULTIRES':
            self.add_to_multires(mod, self.prop_list)

        elif self.mod_type == 'REMESH':
            self.add_to_remesh(mod, self.prop_list)

        elif self.mod_type == 'SCREW':
            self.add_to_screw(mod, self.prop_list)

        elif self.mod_type == 'SKIN':
            self.add_to_skin(mod, self.prop_list)

        elif self.mod_type == 'SOLIDIFY':
            self.add_to_solidify(mod, self.prop_list)

        elif self.mod_type == 'SUBSURF':
            self.add_to_subsurf(mod, self.prop_list)

        elif self.mod_type == 'TRIANGULATE':
            self.add_to_triangulate(mod, self.prop_list)

        elif self.mod_type == 'WIREFRAME':
            self.add_to_wireframe(mod, self.prop_list)
#Deform
        elif self.mod_type == 'ARMATURE':
            self.add_to_armature(mod, self.prop_list)

        elif self.mod_type == 'CAST':
            self.add_to_cast(mod, self.prop_list)

        elif self.mod_type == 'CORRECTIVE_SMOOTH':
            self.add_to_corrective_smooth(mod, self.prop_list)

        elif self.mod_type == 'CURVE':
            self.add_to_curve(mod, self.prop_list)

        elif self.mod_type == 'DISPLACE':
            self.add_to_displace(mod, self.prop_list)

        elif self.mod_type == 'HOOK':
            self.add_to_hook(mod, self.prop_list)

        elif self.mod_type == 'LAPLACIANSMOOTH':
            self.add_to_laplacian_smooth(mod, self.prop_list)

        elif self.mod_type == 'LAPLACIANDEFORM':
            self.add_to_laplacian_deform(mod, self.prop_list)

        elif self.mod_type == 'LATTICE':
            self.add_to_lattice(mod, self.prop_list)

        elif self.mod_type == 'MESH_DEFORM':
            self.add_to_mesh_deform(mod, self.prop_list)

        elif self.mod_type == 'SHRINKWRAP':
            self.add_to_shrinkwrap(mod, self.prop_list)

        elif self.mod_type == 'SIMPLE_DEFORM':
            self.add_to_simple_deform(mod, self.prop_list)

        elif self.mod_type == 'SMOOTH':
            self.add_to_smooth(mod, self.prop_list)

        elif self.mod_type == 'WARP':
            self.add_to_warp(mod, self.prop_list)

        elif self.mod_type == 'WAVE':
            self.add_to_wave(mod, self.prop_list)
#Simulate
        elif self.mod_type == 'CLOTH':
            self.add_to_cloth(mod, self.prop_list)

        elif self.mod_type == 'COLLISION':
            self.add_to_collision(mod, self.prop_list)

        elif self.mod_type == 'DYNAMIC_PAINT':
            self.add_to_dynamic_paint(mod, self.prop_list)

        elif self.mod_type == 'EXPLODE':
            self.add_to_explode(mod, self.prop_list)

        elif self.mod_type == 'FLUID_SIMULATION':
            self.add_to_fluid_simulation(mod, self.prop_list)

        elif self.mod_type == 'OCEAN':
            self.add_to_ocean(mod, self.prop_list)

        elif self.mod_type == 'PARTICLE_INSTANCE':
            self.add_to_particle_instance(mod, self.prop_list)

        elif self.mod_type == 'PARTICLE_SYSTEM':
            self.add_to_particle_system(mod, self.prop_list)

        elif self.mod_type == 'SMOKE':
            self.add_to_smoke(mod, self.prop_list)

        elif self.mod_type == 'SOFT_BODY':
            self.add_to_soft_body(mod, self.prop_list)

    def store_to_prop_cache(self, prop_cache):
        for num, val in enumerate(self.prop_list):
            prop_cache.add()

            if str(type(val)) == "<class 'int'>":
                prop_cache[num].int_val = val
                prop_cache[num].store_type = "int" 

            elif str(type(val)) == "<class 'float'>":
                prop_cache[num].float_val = val
                prop_cache[num].store_type = "float" 

            elif str(type(val)) == "<class 'str'>":
                prop_cache[num].string_val = val
                prop_cache[num].store_type = "str" 

            elif str(type(val)) == "<class 'bool'>":
                prop_cache[num].bool_val = val
                prop_cache[num].store_type = "bool" 

            elif str(type(val)) == "<class 'Color'>":
                prop_cache[num].color_val = val
                prop_cache[num].store_type = "Color" 

            elif str(type(val)) == "<class 'set'>":
                prop_cache[num].set_val = str(val)
                prop_cache[num].store_type = "set" 
                
            elif str(type(val)) == "<class 'NoneType'>":
                prop_cache[num].non_val = "None" 
                prop_cache[num].store_type = "NoneType"

    def restore_from_prop_cache(self, prop_cache):
        if not self.prop_list:
            for cache in prop_cache:
                if cache.store_type == "int": 
                    self.prop_list.append(cache.int_val)

                elif cache.store_type == "float":
                    self.prop_list.append(cache.float_val)

                elif cache.store_type == "str":
                    self.prop_list.append(cache.string_val)

                elif cache.store_type == "bool":
                    self.prop_list.append(cache.bool_val)
                    
                elif cache.store_type == "Color":
                    self.prop_list.append(cache.color_val)

                elif cache.store_type == "set":
                    self.prop_list.append(eval(cache.set_val))
                    #self.prop_list.append(set())

                elif cache.store_type == "NoneType":
                    self.prop_list.append(None)

