# coding=utf-8


"""
    The {} in sentences are placeholders for numbers or names, to be filled in by the software,
    you can move them around the sentence if needed.
    The \n at the end of some sentences indicate a new line.

    """

dictionary = {

    '': '',

    # Panel titles
    'Presets':  'Pick Preset',
    'Simulate': 'Simulate',
    'Flow':     'Flow',
    'Power':    'Power',  # New
    'Drop':     'Drop',
    'Add':      'Add',
    'Grow':     'Grow',
    'Turn':     'Turn',
    'Interact': 'React',
    'Thicken':  'Thicken',
    'Bend':     'Bend',
    'Shade':    'Shade',
    'Repeat':   'Repeat',
    'Build':    'Build',
    'Animate':  'Animate',
    'Twigs':    'Pick Twig',


    # User preferences
    'twigs_path':       'Twigs Folder',
    'twigs_path_tt':    'Point to the folder in which you store twigs. '
                        'These twigs will be listed in the twig picker.',
    'textures_path':    'Textures Folder',
    'textures_path_tt': 'Point to the folder in which you store bark textures. '
                        'These textures will be listed in the texture picker.',


    # Interface messages
    'remove_preset_info':       'Remove {}?',
    'overwrite_preset_info':    'Overwrite {}?',
    'your_tree_is_info':        'Your tree is {0} years old and {1:.1f} meters tall.',
    'your_trees_are_info':      'Your trees are {0} years old and {1:.1f} meters tall.',
    'your_tree_is_info_feet':   'Your tree is {0} years old and {1:.1f}\' tall.',  # For example: Your tree is 20 years old and 51.2' tall.
    'your_trees_are_info_feet': 'Your trees are {0} years old and {1:.1f}\' tall.',
    'branch_has_polygons_info': '{} Branch makes up {:,} polygons.',
    'branches_have_polygons_info':
                                '{} Branches make up {:,} polygons.',
    'growing_from_empties_info':'Growing from empty objects.',
    'preset_empty_info':        'Preset empty selected. Minimal interface.',
    'vertex_color_limit_info':  'Vertex Colors are limited to 8 layers.',
    'twig_vanished_info':       'Your twig vanished! Add twigs before starting The Grove.',
    'vanished_twig_info':       'Warning: Your twig just disappeared! '
                                'Please append or link twigs before starting The Grove.',
    'empty_twig_warning':       'No twigs found in file.',
    'undo_warning':             'The Grove needs 10 global undo steps to function!',
    'grease_pencil_info':       'First draw grease pencil strokes in the 3D view.',
    'restart_info':             'Click Restart to grow the new number of trees.',
    'get_started_info':         'Click Grow to get growing.',
    'time_info':                'This may take time, please grow in small steps.',
    'wind_loop_info':           'With {} shapes, wind loops every {} frames.',

    # Terminal console messages
    'found_an_empty_message':   'Found an empty, add it as a seed: ',
    'set_units_message':        'Set units to Metric, to improve the interface. '
                                'You can revert this change in your scene settings.',
    'clean_old_data':           'To keep The Grove running smooth, cleaning up old unused branches: ',
    'read_preset_message':      'Read Preset - ',
    'add_preset_message':       'Add Preset - ',
    'replace_preset_message':   'Replace Preset - ',
    'remove_preset_message':    'Remove preset - ',
    'rename_preset_message':    'Rename preset - {} to {}',
    'done_message':             'The Grove - Done',
    'restart_message':          'Restart with {} trees.',

    'simulate_year_message':    'Simulate Year {}',
    'environment_prune_message':
                                'Environment Prune',
    'bake_bend_message':        'Bake Bend',
    'flow_message':             'Flow',
    'weigh_message':            'Weigh',
    'photosynthesize_message':  'Photosynthesize',
    'bend_message':             'Bend',
    'thicken_message':          'Thicken',

    'add_branches_message':     'Add Branches',
    'time_offset_message':      'Waiting for time offset to pass...',
    'grow_message':             'Grow Branches',
    'lateral_takeover_message': 'Lateral Takeover',
    'shade_message':            'Shade',
    'added_regenerative_branches_message':
                                'Added {} regenerative branches',
    'drop_message':             'Drop branches',
    'dropped_branches_message': 'Dropped {} branches',
    'drop_low_message':         'Drop branches lower than {} meters along the tree base',
    'ended_low_powered_branches_message':
                                'Ended {} low powered branches',
    'build_twigs_message':      'Build - Twigs',
    'build_branches_advanced_mesh_message':
                                'Build Branches - Advanced Mesh',
    'build_cached_message':     'Build - Branches - Advanced Meshing - Using Cached Mesh',
    'build_layers_message':     'Build - Simulation Data',
    'colors_limit_message':     'Vertex Colors are limited to 8 layers - skipped {} layer.',
    'add_wind_message':         'Simulating Wind...',
    'add_wind_shape_message':   'Simulating Wind Shape {} of {}',
    'plant_at_empty_message':   'Plant new tree at empty object\'s location and heading.',
    'plant_at_origin_message':  'Planting a new tree at the world origin.',


    # Presets
    'presets_menu':     'Preset',  # Read
    'presets_menu_tt':  'Load preset parameters of tree species',

    'preset_name':      'New Name',
    'preset_name_tt':   'Name of the preset to save or overwrite',

    'remove_preset':    'Remove',
    'remove_preset_tt': 'Remove selected preset',

    'remove_preset_cancel':     'No',
    'remove_preset_cancel_tt':  'Cancel removing preset',

    'remove_preset_confirm':    'Yes',
    'remove_preset_confirm_tt': 'Confirm removing preset',

    'rename_preset':    'Rename',
    'rename_preset_tt': 'Rename selected preset',

    'add_preset':    'Add',
    'add_preset_tt': 'Add a new preset',

    'replace_preset':    'Replace',
    'replace_preset_tt': 'Overwrite selected preset',

    'replace_preset_cancel':    'No',
    'replace_preset_cancel_tt': 'Cancel replacing preset',

    'replace_preset_confirm':    'Yes',
    'replace_preset_confirm_tt': 'Confirm replacing preset',


    # Simulate
    'number_of_trees': 'Trees',
    'number_of_trees_tt':
        'Number of trees to grow together\n'
        'Grow groups of trees to create a grove, forest or simply a tree with multiple stems. '
        'You can also grow trees at exact locations. '
        'To do this, add empty objects where you want them to grow (Add > Empty > Single Arrow). '
        'Optionally rotate the empty to start the tree in that direction. '
        'Then select each of the empty objects and start The Grove. '
        'It will now grow from each of the empty objects.',

    'tree_space': 'Space Between',
    'tree_space_tt':
        'Approximate distance between trees\n'
        'The Grove plants groups of trees in the same pattern seen in a sunflower disc. '
        'This pattern by itself is too even - a touch of randomness adds a natural look. '
        'This randomness varies the space from tree to tree, but the average will be close to the set value.',

    'grow_years': 'Add Years',
    'grow_years_tt':
        'Added number of years to grow\n'
        'Simulate your tree in interactive steps. '
        'The total age of your tree will show up in the info window below.',

    'zoom':    'Zoom',
    'zoom_tt': 'Zoom to fit the entire tree in the viewport',

    'simulate': 'Grow',
    'simulate_tt':
        'Grow your tree in interactive steps\n'
        'Simulate the seasons by growing, bending and pruning in interactive steps. '
        'Watch your tree evolve year by year.',

    'restart': 'Restart',
    'restart_tt':
        'Remove the tree and start over\n'
        'Tweaking the character of your tree is often a trial-and-error process. '
        'And even when your settings are spot on, nature isn\'t perfect. '
        'Grow, tweak, restart, repeat... that\'s the way to grow a tree.',

    'manual_prune': 'Prune',
    'manual_prune_tt':
        'Remove branches\n'
        'Before using this tool, draw cutting lines in the 3D view using the Grease Pencil. '
        'Press and hold D, then click and drag to draw strokes. '
        'Then click this button to trim the tree and remove unwanted branches. '
        'Although similar to the Shape tool, Prune realistically cuts off branches. '
        'It keeps the thickness at the end and kills the end to prevent further growth.',

    'shape': 'Shape',
    'shape_tt':
        'Remove branches\n'
        'Before using this tool, draw cutting lines in the 3D view using the Grease Pencil. '
        'Press and hold D, then click and drag to draw strokes. '
        'Then press this button to trim the tree and remove unwanted branches. '
        'Although similar to the Prune tool, Shape allows more artistic freedom. '
        'Cut branch ends have their thickness reset and they remain alive for further growth.',

    # Flow
    'favor_current': 'Favor Lead',
    'favor_current_tt':
        'Suppress side branches\n'
        'Favor growth of current branches over that of child branches. '
        'Slowing down side branches simulates a natural effect called Apical Dominance. '
        'It is highly dependent on other parameters, but in general: '
        'high values make for a tall and slender tree - low (or even negative) values create shrubs.',

    'favor_current_reach': 'Reach',
    'favor_current_reach_tt':
        'Maximum distance for Favor Current\n'
        'The branch tip creates a hormone that delays the growth of child branches. '
        'The concentration of the hormone decreases further away from the tip until it gets lower than a threshold. '
        'The effect of Favor Current is now gone and side branches are free to grow.',

    'Avoid Shade': 'Avoid Shade',
    'avoid_shade_tt':
        'Increase or decrease Favor Current on shaded branches\n'
        'With shade avoidance, each branch controls its own Favor Current, as a strategy to find light. '
        'The more a branch is shaded, it can either favor its current growth in search for light, '
        'or it can favor sub branch growth in order to take in as much light it can get in the shade. '
        'The latter can be seen in forest floor species like Beech and Hazel.',

    'favor_healthy': 'Favor Bright',
    'favor_healthy_tt':
        'Favor healthy branches\n'
        'Healthy branches carry many leaves that get lots of light. Branch health is a relative thing. '
        'The combined photosynthetic yield of all leaves attached to the branch is compared to that of a side branch. '
        'The healthiest branch gets favored.',

    'favor_rising': 'Favor Rising',
    'favor_rising_tt': 'Favor upward growing branches over branches that are dangling down. '
                       'Boost upward branches to get a towering tree. '
                       'A value of 1 will go as far as to reduce the power of horizontal branches to zero. '
                       'You can go even higher than that if you wish.',

    'branching_inefficiency': 'Inefficiency',
    'branching_inefficiency_tt':
        'A direct way to limit the growth power of sub branches and their consecutive sub branches. '
        'A branch attachment is imperfect and limits water transport.',


    # Drop
    'drop_low': 'Low',
    'drop_low_tt':
        'Trim low hanging branches below this height\n'
        'Automatically prune the base of city trees to allow free passage for pedestrians and traffic. '
        'Drop low hanging branches damaged by ground frost. Or lose branches to foraging animals. '
        'This pruning gradually kicks in when a tree grows taller.',

    'keep_thick': 'Keep Thick',
    'keep_thick_tt':
        'Keep thick branches\n'
        'Keep branches that are too thick to chew by animals. '
        'Animals prefer the juicy fresh branches and leave the thick ones be. '
        'This will allow the tree to grow several big main branches, giving your tree a more natural look. '
        'A look that we humans also tend to look for when pruning trees that have more space like in gardens and parks.',

    'drop_shaded': 'Shaded',
    'drop_shaded_tt':
        'Drop shaded branches\n'
        'Each year a tree will grow countless new twigs in every direction. '
        'These sensitive small branches explore new space and search for light. '
        'The tree will then invest its energy in only the bright twigs, and it will drop the many shaded ones. '
        'Decrease to keep more branches and grow a denser tree. '
        'Increase toward 1 to drop ever brighter branches, and to grow a transparent and open tree.',

    'drop_relatively_weak': 'Relatively Weak',
    'drop_relatively_weak_tt':
        'Drop relatively low performing branches\n'
        'Abscission is a form of self-pruning based on the health of a branch relative to that of the ongoing parent branch. '
        'Trees drop their least successful branches in drought and in shade. '
        'Abscission kicks in when the ratio of the photosynthesis of a side branch, to that of the main branch, gets below the set value. '
        'The side branch is then left without water and nutrients, and it will soon die.',

    'keep_dead': 'Stick Around',
    'keep_dead_tt': 'Keep dead branches on the tree\n'
                    'It takes some time for dead branches rot and break off the tree. Especially the lower trunk '
                    'of conifer trees is full of dead branches.',

    'apical_bud_fatality': 'Shaded End Buds',
    'apical_bud_fatality_tt':
        'Chance that a branch end will stop growing because of shade\n'
        'Shade pruning removes branches with low light, but only young branches without side branches. '
        'This parameter is the chance that an older branch end will die of low light. '
        'End buds are very strong and die hard. '
        'But many species don\'t have real end buds, '
        'instead they have side buds near the end and the end is often used for creating flowers and fruit. '
        'These species have a higher chance of their end buds not forming very strong in low light.',

    'flower_power': 'Dead Ends',
    'flower_power_tt':
        'The growth power below which a branch end forms a flower and stops growing in length\n'
        'High power branches are there to grow the tree to new heights. '
        'Lower power branch ends are repurposed to form flowers and fruits. '
        'This ends growth in length for the branch, allowing side branches to take over. '
        'Higher values will increase the chance of flowering. ',
    
    'peak_height': 'Peak Height',
    'peak_height_tt':
        'Maximum height in meters\n'
        'As a tree grows higher, gravity makes it harder and harder to get water to the top. '
        'At some point, it becomes impossible. This marks the peak height. '
        'Note that this value should not always be the theoretical maximum height of a species under ideal conditions. '
        'Soil conditions and drought often drastically lower the theoretical peak height. '
        'Beautiful trees can be made with low Peak Height.',

    'do_lateral_takeover': 'Lateral Takeover',
    'do_lateral_takeover_tt':
        'Chop off dead branch ends and fluently merge the remainder of the branch with the last sub branch. '
        'The effect is more prominent main branches and forking.',

    'do_lateral_takeover_thicker': 'Thicker',
    'do_lateral_takeover_thicker_tt':
        'When a child branch grows thicker than its parent, it takes over. The remaining branch end becomes the child, '
        'and what was once the child is merged fluently with the parent branch.',


    # Add
    'branching_types': 'Side Branches',
    'branching_types_tt': 'Branching type',
    'branching_type_single': 'Single',
    'branching_type_single_tt':
        'Alternate branching\n'
        'One bud at each node. Each successive internode is twisted by the phyllotaxic rotation of the golden angle.',
    'branching_type_double': 'Double',
    'branching_type_double_tt':
        'Opposite branching\n'
        'Two buds at each node, at opposite sides of the twig. '
        'Each successive internode is twisted by the phyllotaxic rotation of 90 degrees.',
    'branching_type_whorl_of_3': 'Whorl of up to 3',
    'branching_type_whorl_of_3_tt': 'Three buds at each node',
    'branching_type_whorl_of_4': 'Whorl of up to 4',
    'branching_type_whorl_of_4_tt': 'Four buds at each node',
    'branching_type_whorl_of_5': 'Whorl of up to 5',
    'branching_type_whorl_of_5_tt': 'Five buds at each node',
    'branching_type_whorl_of_6': 'Whorl of up to 6',
    'branching_type_whorl_of_6_tt': 'Six buds at each node',

    'branch_chance': 'Branch Chance',
    'branch_chance_tt':
        'Chance that a young node creates a new branch\n'
        'Not all buds will open and grow a new branch. '
        'Some are damaged by frost or insects, others are suppressed by Favor Current.',

    'bud_life': 'Bud Life',
    'bud_life_tt':
        'On most species, buds only survive a couple of years\n'
        'Buds up to this age are viable for growing a new twig.'
        'On others, almost every bud opens and forms mostly a very short twig that is restricted by apical dominance. '
        'Most of these will soon be gone, while few of them escape the repression and grow into new branches.',

    'branch_chance_light_threshold': 'Light Required',
    'branch_chance_light_threshold_tt':
        'Least amount of light a node needs to add side branches.',

    'branch_chance_only_terminal': 'Only on End Node',
    'branch_chance_only_terminal_tt':
        'Only add new branches to end nodes\n'
        'Trees like conifers suppress lateral growth with hormones. '
        'Effectively this means that only nodes that are very close to the end are free of hormones and are able '
        'to form new branches.',

    'regenerative_branch_chance': 'Regenerative',
    'regenerative_branch_chance_tt':
        'Chance that an old node will grow a regenerative branch\n'
        'Watershoots allow a damaged or pruned tree to regenerate its crown. '
        'Note that a high Drop Relatively Weak value will remove watershoots as soon as they appear. '
        'Trees like conifers that heavily drop relatively weak branches do not form watershoots.'
        'And because of that, these species do not respond well to pruning.',

    'regenerative_branch_chance_light_required': 'Light Required',
    'regenerative_branch_chance_light_required_tt':
        'Light needed to form regenerative shoots\n'
        'If a node of an old branch receives enough light, it will have a chance of growing a regenerative branch. '
        'This can happen when a significant amount of the crown is pruned (around a third on most trees).'
        'The lower trunk gets so much light that dormant buds get the chance to pop open.',


    # Grow
    'grow_length':    'Length',
    'grow_length_tt': 'Total length of new growth',

    'grow_nodes': 'Nodes',
    'grow_nodes_tt':
        'Number of nodes to grow each year\n'
        'The maximum number of nodes that a branch can grow each year. Low power branches will grow less nodes.',

    'shade_elongation': 'Shade Elongation',
    'shade_elongation_tt':
        'Shaded branches grow longer or shorter\n'
        'Plants growing in shade will grow longer in the hope of finding light. '
        'Together with a decrease in thickness, this creates longer but weaker branches that bend more. '
        'It can initiate the dangling branches often seen at the bottom of the crown.',


    # Turn
    'gravitropism': 'To Gravity',
    'gravitropism_tt':
        'Gravitropism\n'
        'Change of direction of new growth relative to gravity. '
        'A negative value makes a branch grow up, away from gravity. '
        'A positive value grows a branch down toward gravity, creating drooping branches.',

    'gravitropism_shade': 'When Shaded',
    'gravitropism_shade_tt':
        'Gravitropism when in full shade\n'
        'A positive value makes a branch grow down. '
        'A negative value makes a branch grow up.',

    'gravitropism_buds': 'To Gravity',
    'gravitropism_buds_tt':
        'Pull buds away from gravity or let gravity pull buds down instead.'
        'The initial direction of a new branch is that of the bud that it grows from. '
        'Besides the obvious angle from the parent branch, the direction of buds is also dictated by gravity. ',

    'gravitropism_buds_randomness': 'Random',
    'gravitropism_buds_randomness_tt':
        'Add randomness to the initial branch direction to create a more haphazard character.',

    'phototropism': 'To Light',
    'phototropism_tt':
        'Phototropism\n'
        'Turn new growth toward the brightest direction. '
        'This is the effect that makes a houseplant grow toward a window. '
        'On a tree, this effect will improve its distribution of branches.',

    'plagiotropism': 'To Horizon',
    'plagiotropism_tt':
        'Plagiotropism\n'
        'Turn branch growth toward the horizontal plane when a branch is shaded.',

    'plagiotropism_buds': 'Horizontal Buds',
    'plagiotropism_buds_tt':
        'Plagiotropism for buds\n'
        'Turning of the phyllotaxis angle towards a horizontal orientation.',

    'branch_angle': 'Branch Angle',
    'branch_angle_tt':
        'Angle between a new branch and its parent\n'
        'Angles between 0 and 90 degrees range from a straight continuation of the branch, '
        'to a direction perpendicular to the parent branch.',

    'twist': 'Twist',
    'twist_tt':
        'Twist each successive node\n'
        'Species like Horse Chestnut have very visible twisting along the length of their branches, '
        'you can clearly see the bark pattern swirling up around the trunk. '
        'Apart from the obvious visual quality, twisting also adds to the phyllotaxic rotation of buds. '
        'This improves branch distribution on trees with opposite branching.',

    'random_heading': 'Heading',
    'random_heading_tt':
        'Randomize the heading of new growth\n'
        'High randomness grows gnarly trees. '
        'Stray Heading only affects the heading in the horizontal plane, vertical branches are unaffected.',

    'random_pitch': 'Pitch',
    'random_pitch_tt':
        'Randomize the pitch of a new node\'s direction\n'
        'High randomness grows gnarly trees. For a straight trunk, use Stray Heading instead.',


    # Interact
    'forces_block': 'Block',
    'forces_block_tt': 'Stop growing after colliding with the environment object.',
    'forces_shade_plus_block': 'Shade + Block',
    'forces_shade_plus_block_tt':
        'The environment object casts shade and thereby influences parameters that depend on light. '
        'Stop growing after colliding with the object.',
    'forces_deflect': 'Deflect',
    'forces_deflect_tt': 'Avoid the environment object.',
    'forces_deflect_plus_block': 'Deflect + Block',
    'forces_deflect_plus_block_tt': 'Avoid the environment object and stop growing after colliding with the object.',
    'forces_attract': 'Attract',
    'forces_attract_tt':
        'Grow towards the environment object. '
        'Twigs can freely grow through the object.',
    'forces_attract_plus_block': 'Attract + Block',
    'forces_attract_plus_block_tt':
        'Grow towards the environment object. '
        'Stop growing after colliding with the object.',
    'forces_none': 'None',
    'forces_none_tt': 'No reaction to the environment.',

    'force':    'Force',
    'force_tt': 'Forces that the environment object imposes on new growth',

    'environment_name':    'Environment',
    'environment_name_tt': 'Name of the environment object to react to',

    'force_power':    'Power',
    'force_power_tt': 'Strength of the force the environment imposes.',

    'force_radius':    'Radius',
    'force_radius_tt': 'Range in which the environment influences the tree.',

    'environment_shade': 'Environment Shade',
    'environment_shade_tt':
        'Added shade from the environment\n'
        'If you want to simulate a forest tree but don\'t want to grow '
        'many trees together or create an environment object, simply add shade.',


    # Thicken
    'tip_thickness': 'Tips',
    'tip_thickness_tt':
        'Diameter at branch ends\n'
        'This is the tip thickness when a branch has full power. '
        'A lower power branch can have a decreased thickness.',

    'tip_decrease': 'Decrease',
    'tip_decrease_tt':
        'Decrease tip thickness on low power branches\n'
        'A low power branch grows thinner. '
        'This impacts tree shape because thin branches bend more. '
        'Especially on droopy conifers which heavily suppress their side branches.',

    'internode_gain': 'Internode Gain',
    'internode_gain_tt':
        'Each node further away from the tip gets this value added to its diameter.',

    'join_branches': 'Join Branches',  # Grow or Merge or Join or Reinforce
    'join_branches_tt':
        'Join branches to grow in thickness\n'
        'Thickness is added starting from the very tip. '
        'Each time two branches join, both their cross sections add up to create a thicker and stronger branch. '
        'This continues all the way down to the base of the tree. '
        'Changing how fast a branch grows in thickness will considerably change the shape of your tree. '
        'The added thickness will reinforce branches and it will reduce bending.',

    'root_scale': 'Root Scale',
    'root_scale_tt':
        'Increase thickness at the base\n'
        'At the root of the trunk, increase thickness caused by root growth.',

    'root_shape': 'Shape',
    'root_shape_tt':
        'Tweak the shape of Root Scale easing into the trunk.',

    'root_bump': 'Root Bumps',
    'root_bump_tt':
        'Multiply Root Scale with root protrusions.',

    'root_distribution': 'Distribution',
    'root_distribution_tt':
        'Reach of the Root Scale effect over the trunk.',


    # Bend
    'branch_weight': 'Branches',
    'branch_weight_tt':
        'Amount of bending under branch weight\n'
        'Higher values simulate more flexible wood.',

    'leaf_weight': 'Branch Ends',
    'leaf_weight_tt':
        'Amount of bending under leaf weight\n'
        'Branch ends carry the relatively heavy weight of their twigs full of leaves, flowers and fruit. '
        'Trees try to counter this bending by growing upward with a negative gravitropism. '
        'The interplay between bending and gravitropism plays an important role in the formation of either a fastigiate or a weeping tree character.',

    'bake_bend': 'Bake Bend',
    'bake_bend_tt':
        'Solidify branches by baking in bending every year\n'
        'Gravity continues to pull down while a branch grows new rings. '
        'Each new ring adds so much more strength that the branch will quickly escape from this gravitational pull. '
        'However, the new ring is grown with the gravitational pull in place, baking the tension inside.',

    'fatigue': 'Fatigue',
    'fatigue_tt':
        'Weaken the effect of Bake Bend\n'
        'The tree builds up strength to counter bending with Bake Bend. '
        'But with age and added weight, the branch tissue gets tired and weakens. '
        'This effect is visible on old trees which sometimes have their lower branches resting on the ground.',


    # Shade
    'shade_leaf_area': 'Leaf Area',
    'shade_leaf_area_tt':
        'Shadow casting area at each branch end, in dm²\n'
        'A Leaf Area of 4.0 equals four times an area of 10cm x 10cm. '
        'Note that this is the combined leaf area of the twig, not the area of a single leaf.',

    'shade_samples': 'Samples',
    'shade_samples_tt':
        'Number of samples for shade raytracing\n'
        'Cast a number of rays upward in a hemisphere with phyllotaxic arrangement for equal spacing. '
        'Use more samples for a smoother result or less samples for more randomness.',

    'show_shade_preview_tt':
        'Toggle shade preview\n'
        'Shade Preview shows shadow casting areas and the distribution of samples in your 3D view.',

    'show_dead_preview_tt':
        'Toggle dead branches preview, showing the dead branches colored red in the 3D viewport.',  # New

    'shade_sensitivity': 'Sensitivity',
    'shade_sensitivity_tt':
        'Sensitivity to shade\n'
        'Shade is a linear value from light to dark, but processes in nature often respond in an exponential way. '
        'Set to 0 for a slow response to shade, a branch will only react after it receives a substantial amount of shade. '
        'Set to 1 for an immediate reaction, the slightest bit of shade is magnified out of proportion.',


    # Build
    'build_type': 'Branches',
    'build_type_tt':
        'How to model branches',

    'build_type_adaptive_mesh':
        'Adaptive Mesh',
    'build_type_adaptive_mesh_tt':
        'Create a mesh with control over UV mapping and with adaptive polygon reduction based on branch thickness.',
    'build_type_adaptive_mesh_plus_wind':
        'Adaptive Mesh + Wind',
    'build_type_adaptive_mesh_plus_wind_tt':
        'Add wind animation to the tree mesh\n'
        'Shape keys play back extremely fast and export to Alembic.',

    'profile_resolution': 'Resolution',
    'profile_resolution_tt':
        'Number of points to describe branch profiles\n'
        'The resolution at the base of the tree. '
        'Increase the resolution to add detail, for example when adding root protrusions.',

    'profile_resolution_reduction': 'Reduction',
    'profile_resolution_reduction_tt':
        'Reduce polygons on thin branches\n'
        'The tree base needs many polygons to get a smooth model. '
        'But most of a tree\'s polygons are in its thousands of young branches. '
        'These thin branches can do with less polygons without loosing visual quality.',

    'smooth_branching': 'Smooth Branching Reach',
    'smooth_branching_tt':
        'Smoothly transition branch node thickness from parent to child branches.',

    'smooth': 'Smooth',
    'smooth_tt':
        'Smooth out sharp corners\n'
        'Lower this value to get more smoothly curved branches. '
        'It works by reducing the angles on sharp corners, the ones that deviate more that the set angle. '
        'This happens each year after growing.',
    'smooth_branches_message':
        'Smooth branches',

    'textures_menu': 'Texture',
    'textures_menu_tt':
        'Pick a texture',

    'u_repeat': 'UV Repeat',
    'u_repeat_tt':
        'Repeat the bark texture\n'
        'Number of times to repeat the bark texture around the girth of the tree base. '
        'Automatically reduced on thinner branches.',

    'texture': 'Texture',
    'texture_tt': 'Pick a bark texture and apply it to your tree\'s branches.'
                  'The texture picker lists each texture found in the textures folder. '
                  'You can select a folder in The Grove\'s user preferences.',
    'wind_direction_n_tt':
        'Wind blows from north to south\n'
        'Select up to two wind directions for a blend between the two.',

    'wind_direction_e_tt':
        'Wind blows from east to west\n'
        'Select up to two wind directions for a blend between the two.',

    'wind_direction_s_tt':
        'Wind blows from south to north\n'
        'Select up to two wind directions for a blend between the two.',

    'wind_direction_w_tt':
        'Wind blows from west to east\n'
        'Select up to two wind directions for a blend between the two.',

    'wind_force': 'Wind Force',
    'wind_force_tt':
        'Directional wind strength\n'
        'Wind comes from the left and flows to the right. '
        'The wind force is modulated by a gentle sine wave for added realism.',

    'turbulence': 'Turbulence',
    'turbulence_tt':
        'Turbulent wind strength\n'
        'Air moving through the tree lifts up leaves and makes branches dance in the wind.',

    'wind_shapes': 'Wind Shapes',
    'wind_shapes_tt':
        'Number of wind shapes to create\n'
        'Wind shapes are shape keys, also known as morph targets or blend shapes. '
        'Each shape is ten frames apart and interpolates fluently with the previous and next shapes. '
        'Multiply by ten to get the total length of wind animation. '
        'Afterward, wind automatically loops seamlessly. '
        'When exporting to Alembic, remember to set the correct frame range for looping. '
        'When using the defaults, this will be frame 1 to 101.',

    'play_stop_tt':
        'Start or stop animation playback',

    'wind_frequency': 'Wind Frequency',
    'wind_frequency_tt':
        'Wind Frequency.',

    'scale_to_twig':
        'Scale to Match Twig',
    'scale_to_twig_tt':
        'Adapt a preset to a different twig size\n'
        'An average twig contains one or two years of growth and is around 30cm long. '
        'A preset is designed to match this size. But twig models can be any size you want, '
        'from a single leaf up to several years of growth. '
        'The way to match a different size twig is to simply scale the branch model up or down. '
        'This keeps your twigs at the same real life scale.',
    'scale_to_twig_warning':
        'Changing Scale to Twig requires a regrow.',

    'twig_duplication_type': 'Twigs',
    'twig_duplication_type_tt':
        'The way to duplicate twigs',

    'twig_duplication_type_particle_system':
        'Particle System',
    'twig_duplication_type_particle_system_tt':
        'Create an object with a particle system that duplicates the twig object at each face. '
        'Fast and flexible.',
    'twig_duplication_type_object_instances':
        'Object Instances',
    'twig_duplication_type_object_instances_tt':
        'Create a linked duplicate of the twig object for each twig. '
        'The many objects may slow down Blender.',
    'twig_duplication_type_leaves':
        'Leaves',
    'twig_duplication_type_leaves_tt':
        'Create one mesh object with simple leaves.',
    'twig_duplication_type_none':
        'None',
    'twig_duplication_type_none_tt':
        'No Twigs',

    'twigs_menu': 'Twig',  # Twigs, Library, Pick
    'twigs_menu_tt': 'Pick a set of twigs to add them to your tree\n'
                     'The twig picker lists every twig found in the twigs folder. '
                     'You can select a folder in The Grove\'s user preferences.',

    'pick_objects': 'Scene Objects',
    'pick_objects_tt': 'Pick any 3D object in the scene.',

    'no_twigs': 'No Twig',
    'no_twigs_tt': 'No twigs',

    'calculate_wind': 'Animate Wind',
    'calculate_wind_tt': 'Calculate wind animation',

    'apical_twig': 'Apical Twig',
    'apical_twig_tt':
        'Twig object to distribute at branch ends\n'
        'To use twigs, first add the twig objects to your scene with File > Append. '
        'Browse inside the twig file and select the twig objects. '
        'Restart The Grove and your twigs will be listed. '
        'Do not append or link new twigs while The Grove is already active. '
        'Blender helps addons keep the scene tidy by performing an undo each time before the addon does its work. '
        'This causes the twig to disappear.',

    'lateral_twig': 'Lateral Twig',
    'lateral_twig_tt':
        'Twig object to distribute along the sides of branches\n'
        'To use twigs, first add the twig objects to your scene with File > Append. '
        'Browse inside the twig file and select the twig objects. '
        'Restart The Grove and your twigs will be listed. '
        'Do not append or link new twigs while The Grove is already active. '
        'Blender helps addons keep the scene tidy by performing an undo each time before the addon does its work. '
        'This causes the twig to disappear.',

    'fruit_twig': 'Fruit Twig',
    'fruit_twig_tt':
        'Name of the twig object with fruit.',

    'fruit_twig_chance': 'Fruit Twig Chance',
    'fruit_twig_chance_tt':
        'TODO',

    'fruit_twig_droop': 'Fruit Twig Droop',
    'fruit_twig_droop_tt':
        'Chance that a branch node will carry a lateral twig\n'
        'Control the density of your tree\'s foliage. '
        'Note that only nodes thinner than the Threshold Thickness have a chance to start with.',

    'lateral_twig_chance': 'Density',
    'lateral_twig_chance_tt':
        'Lateral twig density\n'
        'This is the chance that a node will have a lateral twig. '
        'Use this to control the density of your tree\'s foliage.',

    'lateral_twig_limit': 'Limit',
    'lateral_twig_limit_tt':
        'Only thinner branch nodes can have side twigs\n'
        'Another way to limit the density of your tree foliage.',

    'twig_scale': 'Scale',
    'twig_scale_tt':
        'Tweak the scale of twig models\n'
        'For ultimate realism, your twig should be modeled to scale and Twig Scale should be left at 1.',

    'twig_viewport_detail': 'Viewport Detail',
    'twig_viewport_detail_tt':
        'Lower the display resolution of twigs\n'
        'For better viewport performance, this adds a Decimate modifier to each twig model. '
        'Viewports use the modified, low resolution model - while render engines use the original.',

    'layers_type': 'Layers',
    'layers_type_tt': 'Add data layers to your tree',

    'layers_type_none': 'None',
    'layers_type_none_tt': 'No data layers',

    'layers_type_vertex_colors': 'Vertex Colors',
    'layers_type_vertex_colors_tt':
        'Add Vertex Color layers\n'
        'Can be used in Cycles materials with an Attribute node. '
        'Enter the name of the Vertex Color layer in the Attribute node. '
        'Can be exported to Alembic files.',

    'layers_type_vertex_groups': 'Vertex Groups',
    'layers_type_vertex_groups_tt':
        'Add Vertex Group layers\n'
        'Can be used to control parameters of modifiers and particle systems. '
        'Note that Alembic only supports Vertex Colors, not Groups.',

    'layers_type_vertex_groups_plus_colors':
        'Vertex Groups + Colors',
    'layers_type_vertex_groups_plus_colors_tt':
        'Add both Vertex Group and Vertex Color layers',

    'layer_thickness':     'Thickness',
    'do_layer_thickness_tt':  'Add thickness data layer to the mesh',
    'layer_weight':        'Weight',
    'do_layer_weight_tt':     'Add weight data layer to the mesh',
    'layer_health':        'Photosynthesis',
    'do_layer_health_tt':     'Add health data layer to the mesh',
    'layer_shade':         'Shade',
    'do_layer_shade_tt':      'Add shade data layer to the mesh',
    'layer_power':         'Power',
    'do_layer_power_tt':      'Add power data layer to the mesh',
    'layer_generation':    'Generation',
    'do_layer_generation_tt': 'Add generation data layer to the mesh',
    'layer_dead':          'Dead',
    'do_layer_dead_tt':       'Add dead data layer to the mesh',
    'layer_pitch':         'Pitch',
    'do_layer_pitch_tt':      'Add pitch data layer to the mesh',
    'layer_apical':        'Apical Twig',
    'do_layer_apical_tt':     'Add apical data layer to the mesh',
    'layer_lateral':       'Lateral Twig',
    'do_layer_lateral_tt':    'Add lateral data layer to the mesh',


    # Advanced UI toggles
    'advanced_ui_show_more':
        'Show more\n',

    'advanced_ui_presets_tt':
        'Remove, rename, replace, or add new presets.',

    'advanced_ui_shade_tt':
        'Fine tune leaf area and shade quality.',

    'advanced_ui_flow_tt':
        'Fine tune the distribution of growth power.',

    'advanced_ui_drop_tt':
        'Set an absolute peak height. '
        'Control the fate of end buds and let successful side branches take over.',

    'advanced_ui_add_tt':
        'Fine tune when and where new branches are added.',

    'advanced_ui_turn_tt':
        'Randomize the direction of growing branches. '
        'Add twist to enhance branch distribution.',

    'advanced_ui_bend_tt':
        'Fine tune the long term effects of bending.',

    'advanced_ui_build_tt':
        'Add wind animation. '
        'Enrich your tree with vertex layers. '
        'Fine tune twigs.',

    'advanced_ui_thicken_tt':
        'Fine tune the root shape of your tree.',

    'set_scene_units': 'Set Scene Units',
    'set_scene_units_tt':
        'The Grove uses units for several of its parameters. Your scene can be configured to '
        'use metric or imperial units. The Grove will work with both. But when no unit '
        'system is selected, the several parameters that require units become hard to tweak. Enable '
        'this checkbox to automatically set the scene to use metric units when no units are set.',

    'language_info': 'Language to use for the interface and tooltips:',
    'language_tt': 'Language',

    'refresh_language_message': 'Press F8 to refresh the Grove and display the new language.',

    'label_layers': 'Layers',

    'configure_twigs_path': 'Add Twigs Folder',  # NEW
    'configure_twigs_path_tt': 'Configure the path to your twigs folder in The Grove\'s user preferences.',

    'configure_textures_path': 'Add Textures Folder',  # NEW
    'configure_textures_path_tt': 'Configure the path to your textures folder in The Grove\'s user preferences.'

}
