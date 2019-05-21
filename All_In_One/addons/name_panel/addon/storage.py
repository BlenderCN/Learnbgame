
# batch
class batch:
    '''
        Contains Classes;
            menu

        Contains Lists;
            Positional
    '''

    # classes

    # menu
    class menu:
        '''
            Contains Lists;
                objects
                modifiers
                constraints
                linestyle modifiers
        '''
        # object
        objects = [
            ('ALL', 'All Objects', '', 'OBJECT_DATA', 0),
            ('MESH', 'Mesh', '', 'OUTLINER_OB_MESH', 1),
            ('CURVE', 'Curve', '', 'OUTLINER_OB_CURVE', 2),
            ('SURFACE', 'Surface', '', 'OUTLINER_OB_SURFACE', 3),
            ('META', 'Meta', '', 'OUTLINER_OB_META', 4),
            ('FONT', 'Text', '', 'OUTLINER_OB_FONT', 5),
            ('ARMATURE', 'Armature', '', 'OUTLINER_OB_ARMATURE', 6),
            ('LATTICE', 'Lattice', '', 'OUTLINER_OB_LATTICE', 7),
            ('EMPTY', 'Empty', '', 'OUTLINER_OB_EMPTY', 8),
            ('SPEAKER', 'Speaker', '', 'OUTLINER_OB_SPEAKER', 9),
            ('CAMERA', 'Camera', '', 'OUTLINER_OB_CAMERA', 10),
            ('LAMP', 'Lamp', '', 'OUTLINER_OB_LAMP', 11)
        ]

        # constraint
        constraints = [
            ('ALL', 'All Constraints', '', 'CONSTRAINT', 0),

            # motion tracking
            ('CAMERA_SOLVER', 'Camera Solver', '', 'CONSTRAINT_DATA', 1),
            ('FOLLOW_TRACK', 'Follow Track', '', 'CONSTRAINT_DATA', 2),
            ('OBJECT_SOLVER', 'Object Solver', '', 'CONSTRAINT_DATA', 3),

            # transform
            ('COPY_LOCATION', 'Copy Location', '', 'CONSTRAINT_DATA', 4),
            ('COPY_ROTATION', 'Copy Rotation', '', 'CONSTRAINT_DATA', 5),
            ('COPY_SCALE', 'Copy Scale', '', 'CONSTRAINT_DATA', 6),
            ('COPY_TRANSFORMS', 'Copy Transforms', '', 'CONSTRAINT_DATA', 7),
            ('LIMIT_DISTANCE', 'Limit Distance', '', 'CONSTRAINT_DATA', 8),
            ('LIMIT_LOCATION', 'Limit Location', '', 'CONSTRAINT_DATA', 9),
            ('LIMIT_ROTATION', 'Limit Rotation', '', 'CONSTRAINT_DATA', 10),
            ('LIMIT_SCALE', 'Limit Scale', '', 'CONSTRAINT_DATA', 11),
            ('MAINTAIN_VOLUME', 'Maintain Volume', '', 'CONSTRAINT_DATA', 12),
            ('TRANSFORM', 'Transformation', '', 'CONSTRAINT_DATA', 13),

            # tracking
            ('CLAMP_TO', 'Clamp To', '', 'CONSTRAINT_DATA', 14),
            ('DAMPED_TRACK', 'Damped Track', '', 'CONSTRAINT_DATA', 15),
            ('IK', 'Inverse Kinematics', '', 'CONSTRAINT_DATA', 16),
            ('LOCKED_TRACK', 'Locked Track', '', 'CONSTRAINT_DATA', 17),
            ('SPLINE_IK', 'Spline IK', '', 'CONSTRAINT_DATA', 18),
            ('STRETCH_TO', 'Stretch To', '', 'CONSTRAINT_DATA', 19),
            ('TRACK_TO', 'Track To', '', 'CONSTRAINT_DATA', 20),

            # relationship
            ('ACTION', 'Action', '', 'CONSTRAINT_DATA', 21),
            ('CHILD_OF', 'Child Of', '', 'CONSTRAINT_DATA', 22),
            ('FLOOR', 'Floor', '', 'CONSTRAINT_DATA', 23),
            ('FOLLOW_PATH', 'Follow Path', '', 'CONSTRAINT_DATA', 24),
            ('PIVOT', 'Pivot', '', 'CONSTRAINT_DATA', 25),
            ('RIGID_BODY_JOINT', 'Rigid Body Joint', '', 'CONSTRAINT_DATA', 26),
            ('SHRINKWRAP', 'Shrinkwrap', '', 'CONSTRAINT_DATA', 27)
        ]

        # modifier
        modifiers = [
            ('ALL', 'All Modifiers', '', 'MODIFIER', 0),

            # modify
            ('DATA_TRANSFER', 'Data Transfer', '', 'MOD_DATA_TRANSFER', 1),
            ('MESH_CACHE', 'Mesh Cache', '', 'MOD_MESHDEFORM', 2),
            ('NORMAL_EDIT', 'Normal Edit', '', 'MOD_NORMALEDIT', 3),
            ('UV_PROJECT', 'UV Project', '', 'MOD_UVPROJECT', 4),
            ('UV_WARP', 'UV Warp', '', 'MOD_UVPROJECT', 5),
            ('VERTEX_WEIGHT_EDIT', 'Vertex Weight Edit', '', 'MOD_VERTEX_WEIGHT', 6),
            ('VERTEX_WEIGHT_MIX', 'Vertex Weight Mix', '', 'MOD_VERTEX_WEIGHT', 7),
            ('VERTEX_WEIGHT_PROXIMITY', 'Vertex Weight Proximity', '', 'MOD_VERTEX_WEIGHT', 8),

            # generate
            ('ARRAY', 'Array', '', 'MOD_ARRAY', 9),
            ('BEVEL', 'Bevel', '', 'MOD_BEVEL', 10),
            ('BOOLEAN', 'Boolean', '', 'MOD_BOOLEAN', 11),
            ('BUILD', 'Build', '', 'MOD_BUILD', 12),
            ('DECIMATE', 'Decimate', '', 'MOD_DECIM', 13),
            ('EDGE_SPLIT', 'Edge Split', '', 'MOD_EDGESPLIT', 14),
            ('MASK', 'Mask', '', 'MOD_MASK', 15),
            ('MIRROR', 'Mirror', '', 'MOD_MIRROR', 16),
            ('MULTIRES', 'Multiresolution', '', 'MOD_MULTIRES', 17),
            ('REMESH', 'Remesh', '', 'MOD_REMESH', 18),
            ('SCREW', 'Screw', '', 'MOD_SCREW', 19),
            ('SKIN', 'Skin', '', 'MOD_SKIN', 20),
            ('SOLIDIFY', 'Solidify', '', 'MOD_SOLIDIFY', 21),
            ('SUBSURF', 'Subdivision Surface', '', 'MOD_SUBSURF', 22),
            ('TRIANGULATE', 'Triangulate', '', 'MOD_TRIANGULATE', 23),
            ('WIREFRAME', 'Wireframe', '', 'MOD_WIREFRAME', 24),

            # deform
            ('ARMATURE', 'Armature', '', 'MOD_ARMATURE', 25),
            ('CAST', 'Cast', '', 'MOD_CAST', 26),
            ('CORRECTIVE_SMOOTH', 'Corrective Smooth', '', 'MOD_SMOOTH', 27),
            ('CURVE', 'Curve', '', 'MOD_CURVE', 28),
            ('DISPLACE', 'Displace', '', 'MOD_DISPLACE', 29),
            ('HOOK', 'Hook', '', 'HOOK', 30),
            ('LAPLACIANSMOOTH', 'Laplacian Smooth', '', 'MOD_SMOOTH', 31),
            ('LAPLACIANDEFORM', 'Laplacian Deform', '', 'MOD_MESHDEFORM', 32),
            ('LATTICE', 'Lattice', '', 'MOD_LATTICE', 33),
            ('MESH_DEFORM', 'Mesh Deform', '', 'MOD_MESHDEFORM', 34),
            ('SHRINKWRAP', 'Shrinkwrap', '', 'MOD_SHRINKWRAP', 35),
            ('SIMPLE_DEFORM', 'Simple Deform', '', 'MOD_SIMPLEDEFORM', 36),
            ('SMOOTH', 'Smooth', '', 'MOD_SMOOTH', 37),
            ('WARP', 'Warp', '', 'MOD_WARP', 38),
            ('WAVE', 'Wave', '', 'MOD_WAVE', 39),

            # simulate
            ('CLOTH', 'Cloth', '', 'MOD_CLOTH', 40),
            ('COLLISION', 'Collision', '', 'MOD_PHYSICS', 41),
            ('DYNAMIC_PAINT', 'Dynamic Paint', '', 'MOD_DYNAMICPAINT', 42),
            ('EXPLODE', 'Explode', '', 'MOD_EXPLODE', 43),
            ('FLUID_SIMULATION', 'Fluid Simulation', '', 'MOD_FLUIDSIM', 44),
            ('OCEAN', 'Ocean', '', 'MOD_OCEAN', 45),
            ('PARTICLE_INSTANCE', 'Particle Instance', '', 'MOD_PARTICLES', 46),
            ('PARTICLE_SYSTEM', 'Particle System', '', 'MOD_PARTICLES', 47),
            ('SMOKE', 'Smoke', '', 'MOD_SMOKE', 48),
            ('SOFT_BODY', 'Soft Body', '', 'MOD_SOFT', 49)
        ]

        linestyleModifiers = [
            ('ALL', 'All Modifiers', '', 'MODIFIER', 0),
            ('ALONG_STROKE', 'Along Stroke', '', 'MODIFIER', 1),
            ('CREASE_ANGLE', 'Crease Angle', '', 'MODIFIER', 2),
            ('CURVATURE_3D', 'Curvature 3D', '', 'MODIFIER', 3),
            ('DISTANCE_FROM_CAMERA', 'Distance from Camera', '', 'MODIFIER', 4),
            ('DISTANCE_FROM_OBJECT', 'Distance from Object', '', 'MODIFIER', 5),
            ('MATERIAL', 'Material', '', 'MODIFIER', 6),
            ('NOISE', 'Noise', '', 'MODIFIER', 7),
            ('TANGENT', 'Tangent', '', 'MODIFIER', 8),
            ('CALLIGRAPHY', 'Calligraphy', '', 'MODIFIER', 9),
            ('2D_OFFSET', '2D Offset', '', 'MODIFIER', 10),
            ('2D_TRANSFORM', '2D Transform', '', 'MODIFIER', 11),
            ('BACKBONE_STRETCHER', 'Backbone Stretcher', '', 'MODIFIER', 12),
            ('BEZIER_CURVE', 'Bezier Curve', '', 'MODIFIER', 13),
            ('BLUEPRINT', 'Blue Print', '', 'MODIFIER', 14),
            ('GUIDING_LINES', 'Guiding Lines', '', 'MODIFIER', 15),
            ('PERLIN_NOISE_1D', 'Perlin Noise 1D', '', 'MODIFIER', 16),
            ('PERLIN_NOISE_2D', 'Perlin Noise 2D', '', 'MODIFIER', 17),
            ('POLYGONIZATION', 'Polygonization', '', 'MODIFIER', 18),
            ('SAMPLING', 'Sampling', '', 'MODIFIER', 19),
            ('SIMPLIFICATION', 'Simplification', '', 'MODIFIER', 20),
            ('SINUS_DISPLACEMENT', 'Sinus Displacement', '', 'MODIFIER', 21),
            ('SPATIAL_NOISE', 'Spatial Noise', '', 'MODIFIER', 22),
            ('TIP_REMOVER', 'Tip Remover', '', 'MODIFIER', 23)
        ]

    # positional
    positional = [
        'L',
        'LEFT',
        'R',
        'RIGHT',
        'T',
        'TOP',
        'B',
        'BOT',
        'BOTTOM',
        'FR',
        'FRONT',
        'FORWARD',
        'BCK',
        'BACK',
        'BACKWARD'
    ]
