'''
    Fields Format: array of tuples.
    Tuple = field description:
        t[0] - name
        t[1] - type
        t[2] - size if array, optional 

    Examples:
        ('id', 'int')
        ('xyz', 'float', 3)

    For char and byte arrays type should contain length:
        ('name', 'char[24]')

'''

ONI_FILES = {	
    'ABNA'  :  {
    	   'description' : 'BSP Tree Node Array',
    	   'fields' : [
                        ('unused', 'char[20]'),         # unused
                        ('size', 'int'),                # array size
                        ('nodes', [
                            ('num_agqg', 'int'),        # AGQG element number
                            ('num_plea', 'int'),        # PLEA element number; if high bit set the plane normal must be reversed
                            ('front_abna', 'int'),      # front ABNA child package index; -1 if there is none
                            ('back_abna', 'int')        # back ABNA child package index; -1 if there is none
                        ], 'size')
            ]
        },
    'AGQC'  :  {
    	   'description' : 'Gunk Quad Collision Array',
    	   'fields' : []
        },
    'AGQG'  :  {
    	   'description' : 'Gunk Quad General Array',
    	   'fields' : []
        },
    'AGQR'  :  {
    	   'description' : 'Gunk Quad Render Array',
    	   'fields' : []
        },
    'AISA'  :  {
    	   'description' : 'AI Character Setup Array',
    	   'fields' : []
        },
    'AKAA'  :  {
    	   'description' : 'Adjacency Array',
    	   'fields' : []
        },
    'AKBA'  :  {
    	   'description' : 'Side Array',
    	   'fields' : []
        },
    'AKBP'  :  {
    	   'description' : 'BSP Node Array',
    	   'fields' : []
        },
    'AKEV'  :  {
    	   'description' : 'Akira Environment',
    	   'fields' : []
        },
    'AKOT'  :  {
    	   'description' : 'Oct Tree',
    	   'fields' : []
        },
    'AKVA'  :  {
    	   'description' : 'BNV Node Array',
    	   'fields' : []
        },
    'BINA'  :  {
    	   'description' : 'Binary Data',
    	   'fields' : []
        },
    'CBPI'  :  {
    	   'description' : 'Character Body Part Impacts',
    	   'fields' : []
        },
    'CBPM'  :  {
    	   'description' : 'Character Body Part Material',
    	   'fields' : []
        },
    'CONS'  :  {
    	   'description' : 'Console',
    	   'fields' : []
        },
    'CRSA'  :  {
    	   'description' : 'Corpse Array',
    	   'fields' : []
        },
    'DOOR'  :  {
    	   'description' : 'Door',
    	   'fields' : []
        },
    'DPge'  :  {
    	   'description' : 'Diary Page',
    	   'fields' : []
        },
    'ENVP'  :  {
    	   'description' : 'Env Particle Array',
    	   'fields' : []
        },
    'FILM'  :  {
    	   'description' : 'Film',
    	   'fields' : []
        },
    'HPge'  :  {
    	   'description' : 'Help Page',
    	   'fields' : []
        },
    'IDXA'  :  {
    	   'description' : 'Index Array',
    	   'fields' : [
                        ('unused', 'char[20]'),         # unused
                        ('size', 'int'),                # array size
                        ('strips', 'int', 'size')       # element ID array
            ]
        },
    'IGHH'  :  {
    	   'description' : 'IGUI HUD Help',
    	   'fields' : []
        },
    'IGPA'  :  {
    	   'description' : 'IGUI Page Array',
    	   'fields' : []
        },
    'IGPG'  :  {
    	   'description' : 'IGUI Page',
    	   'fields' : []
        },
    'IGSA'  :  {
    	   'description' : 'IGUI String Array',
    	   'fields' : []
        },
    'IGSt'  :  {
    	   'description' : 'IGUI String',
    	   'fields' : []
        },
    'Impt'  :  {
    	   'description' : 'Impact Tree',
    	   'fields' : []
        },
    'IPge'  :  {
    	   'description' : 'Item Page',
    	   'fields' : []
        },
    'KeyI'  :  {
    	   'description' : 'Key Icons',
    	   'fields' : []
        },
    'M3GA'  :  {
    	   'description' : 'Geometry Array',
    	   'fields' : []
        },
    'M3GM'  :  {
    	   'description' : 'Geometry',
    	   'fields' : [
                        ('rt_var', 'int'),          # runtime only
                        ('link_xyz', 'int'),        # link to PNTA (vertex XYZs)
                        ('link_vnorm', 'int'),      # link to VCRA (vertex normals)
                        ('link_fnorm', 'int'),      # link to VCRA (face normals)
                        ('link_vuv', 'int'),        # link to TXCA (vertex UVs)
                        ('link_tstrip', 'int'),     # link to IDXA (triangle strips)
                        ('link_fgrouping', 'int'),  # link to IDXA (face groupings)
                        ('link_texture', 'int'),    # link to TXMP (texture)
                        ('link_unused', 'int'),     # unused link; never used in Oni
                        ('unused', 'char[20]')      # unused
            ]     
        },
    'Mtrl'  :  {
    	   'description' : 'Material',
    	   'fields' : []
        },
    'OBAN'  :  {
    	   'description' : 'Object Animation',
    	   'fields' : []
        },
    'OBOA'  :  {
    	   'description' : 'Starting Object Array',
    	   'fields' : []
        },
    'OFGA'  :  {
    	   'description' : 'Object Furn Geom Array',
    	   'fields' : []
        },
    'ONCC'  :  {
    	   'description' : 'Oni Character Class ',
    	   'fields' : [
                ('down_velocity', 'float'),             # downwards velocity? (unknown, always 0.55)
                ('gravity_acc', 'float'),               # downward gravity acceleration                 
                ('tap_velocity', 'float'),              # starting velocity for a simple (tap) JUMP
                ('limit_velocity', 'float'),            # limit velocity for jumping and gravity flight
                ('jetpack', 'float'),                   # upward acceleration (jetpack) if you hold JUMP
                ('gravity_timer', 'short'),             # gravity timer? (unknown, always 7)
                ('jetpack_timer', 'short'),             # jetpack timer; time during which you can use the jetpack
                ('height1', 'float'),                   # maximal falling height without damage
                ('height2', 'float'),                   # maximal falling height with damage

                ('link_txmp', 'int'),                   # link to 01016-shadow1.TXMP
                ('shadow_height1', 'float'),            # height where the shadow fades out completely
                ('shadow_height2', 'float'),            # height where the diameter of the shadow decreases and the shadow fades out half
                ('shadow_height3', 'float'),            # height where the diameter of the shadow decreases
                ('shadow_height4', 'float'),            # height where the diameter of the shadow decreases
                ('shadow_height5', 'float'),            # height where the diameter of the shadow decreases
                ('shadow_transp', 'short'),             # transparency of the shadow for the first part of a jump
                ('shadow_transp', 'short'),             # transparency of the shadow for the second part of a jump
                # Jump Constants
                ('jump_distance', 'float'),             # jumpDistance? ; always the same
                ('jump_height', 'int8'),                # jumpHeight? ; always the same
                ('jump_squares', 'int8'),               # jumpDistanceSquares?!?! ; always the same
                ('pad1', 'char[2]'),                    # pad
                # Cover Constants
                ('ray_increment', 'float'),             # rayIncrement; always the same
                ('ray_max', 'float'),                   # rayMax; always the same
                ('ray_angle', 'float'),                 # rayAngle; always the same (0.017453 = PI/180)
                ('ray_angle_max', 'float'),             # rayAngleMax; always the same (1.57 = PI/2)
                # Autofreeze Constants (unused)
                ('distance_xz', 'float'),               # distance_xz; always the same
                ('distance_y', 'float'),                # distance_y; always the same
                # Inventory Constants (unused?)
                ('hypo_regeneration', 'short'),
                ('pad2', 'char[2]'),
                # LOD Constants
                ('squared440', 'float'),                # always the same; this is 440 squared
                ('squared220', 'float'),                # always the same; this is 220 squared
                ('squared110', 'float'),                # always the same; this is 110 squared
                ('zero1', 'float'),                     # always the same
                ('zero2', 'float'),                     # always the same
                # Hurt Sound Constants
                ('hurt_base_percentage', 'short'),      # hurt_base_percentage; always the same
                ('hurt_max_percentage', 'short'),       # hurt_max_percentage; always the same
                ('hurt_percentage_threshold', 'short'), # hurt_percentage_threshold; always the same
                ('hurt_timer', 'short'),                # hurt_timer; always the same
                ('hurt_min_timer', 'short'),            # hurt_min_timer; always the same
                ('hurt_max_light', 'short'),            # hurt_max_light; always the same
                ('hurt_max_medium', 'short'),           # hurt_max_medium; always the same
                ('hurt_death_chance', 'short'),         # hurt_death_chance; always the same
                ('hurt_volume_threshold', 'short'),     # hurt_volume_threshold; always the same
                ('hurt_medium_threshold', 'short'),     # hurt_medium_threshold; always the same
                ('hurt_heavy_threshold', 'short'),      # hurt_heavy_threshold; always the same
                ('rt', 'int8'),                         # runtime only: if 1 sound pointers have been set
                ('ignored', 'char[1]'),
                ('sound_volume', 'float'),              # sound volume
                ('ref_hurt_light', 'char[32]'),         # hurt light sound (reference to OSBD of level 0)
                ('ref_hurt_medium', 'char[32]'),        # hurt medium sound (reference to OSBD of level 0)
                ('ref_hurt_heavy', 'char[32]'),         # hurt heavy sound (reference to OSBD of level 0)
                ('ref_death', 'char[32]'),              # death sound (reference to OSBD of level 0)
                ('rt_link_hurt_light_sound', 'int'),    # runtime only: pointer to hurt light sound
                ('rt_link_hurt_medium_sound', 'int'),   # runtime only: pointer to hurt medium sound
                ('rt_link_hurt_heavy_sound', 'int'),    # runtime only: pointer to hurt heavy sound
                ('rt_link_hurt_death_sound', 'int'),    # runtime only: pointer to death sound
                # AI Constants
                ('ai_options', 'int'),                  # AI options bitset; see below
                ('ai_rspeed_factor', 'float'),          # AI rotation speed factor
                ('ai_min_fallen_time', 'short'),        # minimal fallen time; number of frames for which AI 
                                                        #   remains in *fallen* position when it is knockdowned
                ('ai_max_fallen_time', 'short'),        # maximal fallen time; number of frames for which AI 
                                                        #   remains in *fallen* position when it is knockdowned
                ('ai_dodge_delay', 'int'),              # number of frames after which AI realizes that it is in 
                                                        #   the firing spread and it starts dodging
                ('ai_min_dodge_amount', 'float'),       # minimal firingspread dodge amount; 
                                                        #   IMO similar to maneouvre variable, it tells AI 
                                                        #   how long it should perform dodging/hiding in response 
                                                        #   to some time spent inside firing spread (so setting this 
                                                        #   very high means that once enemy starts dodging/hiding, he 
                                                        #   will perform it even after firing spread disappears)
                ('ai_max_dodge_amount', 'float'),       # maximal firingspread dodge amount; IMO similar to maneouvre variable
                # AI Targeting Constants
                ('unknown1', 'float'),      # something with AI targeting prediction; always the same for TURR and ONCC
                ('unknown2', 'float'),      # something with AI targeting prediction; always the same for TURR and ONCC
                ('unknown3', 'float'),      # something with AI targeting prediction; always the same for TURR
                ('unknown4', 'int'),        # frame count; something with AI targeting prediction; always the same for TURR
                ('unknown5', 'int'),        # frame count; something with AI targeting prediction; always the same for TURR
                ('unknown6', 'int'),        # frame count; something with AI targeting prediction; always the same for TURR
                ('unknown7', 'int'),        # frame count; something with AI targeting prediction; always the same for TURR
                # shooting skills
                ('shooting_skills', [           
                    ('recoil', 'float'),        # recoil compensation amount (0.0 = min, 1.0 = max)
                    ('best_angle', 'float'),    # best aiming angle in radians
                    ('error', 'float'),         # shot grouping error
                    ('decay', 'float'),         # shot grouping decay
                    ('inaccuracy', 'float'),    # shooting inaccuracy multiplier
                    ('min_delay', 'short'),     # minimum delay between shots in frames
                    ('max_delay', 'short'),     # maximum delay between shots in frames
                ], 13),
                ('unknown8', 'int'),                        # always the same
                ('unknown9', 'int'),                        # always the same
                ('unknown10', 'int'),                       # always the same
                ('taunt_chance', 'int'),                    # taunt chance 
                ('go_for_gun_chance', 'int'),               # go for gun chance; determines possibility that AI will run 
                                                            # to some weapon and take it; can be checked in devmode 
                                                            # by *debug_gun_behavior* command
                ('running_pickup_chance', 'int'),           # running pickup chance; this value is possibility of AI 
                                                            # running weapon pickup (acrobatics, slides) instead of normal 
                                                            # "stop->pickup";this is calculated AFTER engine decides 
                                                            # that AI should run for weapon
                ('combat_profile_ID', 'short'),             # combat profile ID; for example *0D* is for Mutant Muro
                ('melee_profile_ID', 'short'),              # melee profile ID
                ('taunt_sound_probability', 'int8'),        # "taunt" sound probability
                ('alert_sound_probability', 'int8'),        # "alert" sound probability
                ('startle_sound_probability', 'int8'),      # "startle" sound probability
                ('checkbody_sound_probability', 'int8'),    # "checkbody" sound probability
                ('pursue_sound_probability', 'int8'),       # "pursue" sound probability
                ('cower_sound_probability', 'int8'),        # "cower" sound probability
                ('superpunch_sound_probability', 'int8'),   # "superpunch" probability
                ('superkick_sound_probability', 'int8'),    # "superkick" probability
                ('super3_sound_probability', 'int8'),       # "super3" sound probability
                ('super4_sound_probability', 'int8'),       # "super4" sound probability
                ('pad3', 'short'),                          # probably a blank filler
                ('taunt_sound', 'char[32]'),                # "taunt" sound (reference to OSBD of level 0)
                ('alert_sound', 'char[32]'),                # "alert" sound
                ('startle_sound', 'char[32]'),              # "startle" sound
                ('checkbody_sound', 'char[32]'),            # "checkbody" sound
                ('pursue_sound', 'char[32]'),               # "pursue" sound
                ('cower_sound', 'char[32]'),                # "cower" sound
                ('superpunch_sound', 'char[32]'),           # "superpunch" sound (reference to OSBD of level 0)
                ('superkick_sound', 'char[32]'),            # "superkick" sound (reference to OSBD of level 0)
                ('super3_sound', 'char[32]'),               # "super3" sound (only the superninja uses this slot)
                ('super4_sound', 'char[32]'),               # "super4" sound (never used in Oni)
                # 7 vision fields
                ('central_vision_distance', 'float'),       # central vision distance
                ('peripheral_vision_distance', 'float'),    # peripheral vision distance
                ('vertical_vision_range', 'float'),         # vertical vision range
                ('central_vision_range', 'float'),          # central vision range
                ('central_vision_max', 'float'),            # central vision max
                ('peripheral_vision_range', 'float'),       # peripheral vision range
                ('peripheral_vision_max', 'float'),         # peripheral vision max
                ('hostilethreat_definite_timer', 'int'),    # hostilethreat definite timer; 
                                                            # how long will AI know exactly where its enemy is even if 
                                                            # it can't see him with central vision-field; AI attacks him; 
                                                            # can be checked by *ai2_report_verbose* command 
                                                            # (this command causes random crashes, beware)
                ('hostilethreat_strong_timer', 'int'),      # hostilethreat strong timer; how long will AI remain in strong 
                                                            # feeling that there is the enemy, but will not attack him 
                                                            # but investigate; can be checked by *ai2_report_verbose* command
                ('hostilethreat_weak_timer', 'int'),        # hostilethreat weak timer; how long will AI remain in weak 
                                                            # feeling of an enemy, just looking around aimlessly 
                                                            # (Glance pursue mode); can be checked by *ai2_report_verbose* command
                ('friendlythreat_definite_timer', 'int'),   # friendlythreat definite timer; how long will AI know exactly 
                                                            # where its ally (Syndicate saw Syndicate for example) is even 
                                                            # if it can't see him with central vision-field; 
                                                            # AI simply knows there is someone else nearby; 
                                                            # maybe has further possibilities; 
                                                            # can be checked by *ai2_report_verbose* command 
                                                            # (this command causes random crashes, beware)
                ('friendlythreat_strong_timer', 'int'),     # friendlythreat strong timer; how long will AI remain in strong 
                                                            # feeling that there is someone else, but will not try to find him 
                                                            # or look at him; can be checked by *ai2_report_verbose* command
                ('friendlythreat_weak_timer', 'int'),       # friendlythreat weak timer; how long will AI remain in weak 
                                                            # feeling of ally, doing its usual job; 
                                                            # can be checked by *ai2_report_verbose* command
                ('earshot_radius', 'int'),                  # defines size of the sound-collision sphere around AI
                # Character Constants
                ('link_ONCV', 'int'),                       # link to ONCV; defines variants and upgrades
                ('link_ONCP', 'int'),                       # link to ONCP; lists the particles available for this character 
                                                            # (trails, flashes, etc)
                ('link_ONIA', 'int'),                       # link to ONIA; lists the special impact sounds 
                                                            # (used for special combat moves)
                ('rt1', 'int8'),                            # runtime only
                ('pad4', 'int8'),                           # padding
                ('rt2', 'short'),                           # runtime only
                ('modifier', 'char[16]'),                   # modifier; either hardcoded or defunct 
                                                            # (only visible in pm_mod_type.WMM_, level 0)
                                                            # edit: WMDD says: Effects found for Impact x on Material y 
                                                            # with Modifier: pm_mod_types
                ('impacts', [
                    ('ref_walk_impact', 'char[128]'),       # walk impact (reference to Impt of level 0); 
                                                            # always the same; without the impacts you can't hear 
                                                            # the steps of a character
                    ('rt', 'short')                         # set at runtime to the value stored at 0x08 in Impt
                ], 15),

                ('unknown11', 'short'),                     # always the same; maybe only a filler
                ('special_death_particle', 'char[64]'),     # special death particle; only the mad bomber use it
                ('rt3', 'int'),                             # runtime only
                ('rt4', 'int'),                             # runtime only
                ('link_TRBS', 'int'),                       # link to TRBS
                ('link_TRMA', 'int'),                       # link to TRMA
                ('link_CBPM', 'int'),                       # link to CBPM
                ('link_CBPI', 'int'),                       # link to CBPI
                ('fight_mode_timer', 'int'),                # fight mode timer in 1/60 seconds
                ('idle_animation_timers', 'int[2]'),        # idle animation timers in 1/60 seconds
                ('basic_health', 'int'),                    # basic health of the character model; extra health information 
                                                            # for every unique character are stored in the Character.BINA file
                ('feet_bits', 'int'),                       # feetBits (these bits mark the characters feet)
                ('min_body_size_factor', 'int'),            # minimal body size factor
                ('max_body_size_factor', 'int'),            # maximal body size factor
                # ONCC specific multipliers for 7 PAR3 DamageTypes
                ('dtm_normal', 'float'),                    # "Normal" DamageType multiplier
                ('dtm_minor_stun', 'float'),                # "MinorStun" DamageType multiplier
                ('dtm_major_stun', 'float'),                # "MajorStun" DamageType multiplier
                ('dtm_minor_knockdown', 'float'),           # "MinorKnockdown" DamageType multiplier
                ('dtm_major_knockdown', 'float'),           # "MajorKnockdown" DamageType multiplier
                ('dtm_blownup', 'float'),                   # "Blownup" DamageType multiplier
                ('dtm_pickup', 'float'),                    # "Pickup" DamageType multiplier
                ('dtm_boss_shield', 'float'),               # Boss Shield multiplier, employed when the character has a boss shield.
                                                            # For example via BSL command chr_boss_shield(ai_name).
                                                            # Incoming Damage, StunDamage and Knockback from any DamageType 
                                                            # are all multiplied by (1-this value).
                ('link_TRAC', 'int'),                       # link to TRAC
                ('link_TRSC', 'int'),                       # link to TRSC
                ('ai_rate_of_fire', 'short'),               # AI Rate of Fire (testme)
                ('deletion_time', 'short'),                 # time between death and deletion, in frames (about 3 seconds for mad bomber)
                ('trsc_bitset', 'byte'),                    # TRSC bitset
                ('has_daodan_power', 'int8'),               # when set to 1 indicates that character has daodan powers 
                                                            # (character does more damage in overpower mode)
                ('has_supershield', 'int8'),                # when set to 1 indicates that character has supershield
                                                            #   is visible as red shield when overpowered
                                                            #   needs daodan flag above and 51% overpower to be enabled; chenille cheat works too
                                                            #   now it prevents damage from weapon fire and melee (exception are throws)
                                                            #   received (melee) hits cause not blue block flashes but orange flares
                ('canttouchthis', 'int8'),                  # when set to 1, generically turns on canttouchthis cheat for this ONCC (used by MutantMuro.ONCC
                ('unused', 'char[8]'),
           ]
        },
    'ONCP'  :  {
    	   'description' : 'Oni Character Particle Array',
    	   'fields' : []
        },
    'ONCV'  :  {
    	   'description' : 'Oni Character Variant',
    	   'fields' : [
                ('link', 'int'),                        # link to ONCV
                ('type_name', 'char[32]'),              # character type name; Oni spawns this type when you start the game
                ('hard_type_name', 'char[32]'),         # character type name; if the "upgrade difficulty" bit in the 
                                                        #   Character.BINA file is set, Oni spawns this type if you play on hard
                ('unused', 'char[20]')
           ]
        },
    'ONGS'  :  {
    	   'description' : 'Oni Game Settings',
    	   'fields' : []
        },
    'ONIA'  :  {
    	   'description' : 'Oni Character Impact Array',
    	   'fields' : []
        },
    'ONLD'  :  {
    	   'description' : 'Oni Game Level Descriptor',
    	   'fields' : []
        },
    'ONLV'  :  {
    	   'description' : 'Oni Game Level',
    	   'fields' : []
        },
    'ONOA'  :  {
    	   'description' : 'Object Gunk Array',
    	   'fields' : []
        },
    'ONSK'  :  {
    	   'description' : 'Oni Sky Class',
    	   'fields' : []
        },
    'ONVL'  :  {
    	   'description' : 'Oni Variant List',
    	   'fields' : []
        },
    'ONWC'  :  {
    	   'description' : 'Oni Weapon Class',
    	   'fields' : []
        },
    'OPge'  :  {
    	   'description' : 'Objective Page',
    	   'fields' : []
        },
    'OSBD'  :  {
    	   'description' : 'Oni Sound Binary Data',
    	   'fields' : []
        },
    'OTIT'  :  {
    	   'description' : 'Oct Tree Interior Node Array',
    	   'fields' : []
        },
    'OTLF'  :  {
    	   'description' : 'Oct Tree Leaf Node Array',
    	   'fields' : []
        },
    'PLEA'  :  {
    	   'description' : 'Plane Equation Array',
    	   'fields' : []
        },
    'PNTA'  :  {
    	   'description' : '3D Point Array',
    	   'fields' : [
                        ('unused', 'char[12]'),     # unused
                        ('min_x', 'float'),         # min. x-coordinate of all elements below
                        ('min_y', 'float'),         # min. y-coordinate (height) of all elements below
                        ('min_z', 'float'),         # min. z-coordinate of all elements below
                        ('max_x', 'float'),         # max. x-coordinate of all elements below
                        ('max_y', 'float'),         # max. y-coordinate (height) of all elements below
                        ('max_z', 'float'),         # max. z-coordinate of all elements below
                        ('center_x', 'float'),      # x-coordinate of the center [ ((max. x-coord. - min. x-coord.) ÷ 2) + min x-coord. ]
                        ('center_y', 'float'),      # y-coordinate (height) of the center [ ((max. y-coord. - min. y-coord.) ÷ 2) + min y-coord. ]
                        ('center_z', 'float'),      # z-coordinate of the center [ ((max. z-coord. - min. z-coord.) ÷ 2) + min z-coord. ]
                        ('distance', 'float'),      # distance from the center to each of the both points above
                        ('size', 'int'),            # array size
                        ('points', 'float[3]', 'size')
            ]
        },
    'PSpc'  :  {
    	   'description' : 'Part Specification',
    	   'fields' : []
        },
    'PSpL'  :  {
    	   'description' : 'Part Specification List',
    	   'fields' : []
        },
    'PSUI'  :  {
    	   'description' : 'Part Specifications UI',
    	   'fields' : []
        },
    'QTNA'  :  {
    	   'description' : 'Quad Tree Node Array',
    	   'fields' : []
        },
    'SNDD'  :  {
    	   'description' : 'Sound Data',
    	   'fields' : []
        },
    'SUBT'  :  {
    	   'description' : 'Subtitle Array',
    	   'fields' : []
        },
    'TRAC'  :  {
    	   'description' : 'Animation Collection',
    	   'fields' : [
                ('unused', 'char[16]'),
                ('link_TRAC', 'int'),
                ('rt', 'short'),
                ('size', 'short'),
                ('anims', [
                    ('weight', 'short'),       # animation weight, a higher value indicates that this animation 
                                                    #   has a better chance to be picked up if there are multiple animations 
                                                    #   possible for the same (from state, animation type, varient, first level) pair
                    ('rt', 'short'),                # used at runtime only
                    ('unused', 'int'),
                    ('link_TRAM', 'int')
                ], 'size')
           ]
        },
    'TRAM'  :  {
    	    'description' : 'Totoro Animation Sequence',
    	    'fields' : [
                ('rt1', 'int'),
                ('offset_y', 'int'),
                ('offset_xz', 'int'),
                ('offset_attack', 'int'),
                ('offset_damage', 'int'),
                ('offset_motion', 'int'),
                ('offset_shortcut', 'int'),
                ('offset_throw', 'int'),
                ('offset_footstep', 'int'),
                ('offset_particle', 'int'),
                ('offset_position', 'int'),
                ('offset_bodyparts', 'int'),
                ('offset_sound', 'int'),
                ('flags', 'int'),
                ('links_TRAM', 'int', 2),
                ('used_parts', 'int'),
                ('replaced_parts', 'int'),
                ('rotation', 'float'),
                ('main_attack_direction', 'short'),
                ('attack_sound', 'short'),
                # Extent info
                ('max_horizontal_extent', 'float'),
                ('min_y', 'float'),
                ('max_y', 'float'),                
                ('horizontal_extents', 'float', 36),
                # First and Farthest extent info
                ('extents', [
                    ('frame', 'short'),
                    ('attack_index', 'int8'),
                    ('attack_frame_offset', 'int8'),
                    ('pelvis_location', 'float', 3),
                    ('length', 'float'),
                    ('min_y', 'float'),
                    ('max_y', 'float'),
                    ('angle', 'float')
                ], 2),
                # End max extent info
                ('alternative_move_direction', 'int'),
                ('extents_num', 'int'),
                ('extent_offset', 'int'),
                # End extent info
                ('impact_particle_name', 'char[16]'),
                ('hard_pause', 'short'),
                ('soft_pause', 'short'),
                ('sounds_num', 'int'),
                ('rt2', 'int'),
                ('rt3', 'short'),
                ('fps', 'short'),
                ('compression_size', 'short'),
                ('anim_type', 'short'),
                ('aiming_type', 'short'),
                ('from_state', 'short'),
                ('to_state', 'short'),
                ('bodyparts_num', 'short'),
                ('frames_num', 'short'),
                ('duration', 'short'),
                ('varient', 'short'),
                ('unused1', 'byte[2]'),
                ('atomic_start', 'short'),
                ('atomic_end', 'short'),
                ('end_interpolation', 'short'),
                ('maximal_interpolation', 'short'),
                ('action_frame', 'short'),
                ('first_level', 'short'),
                ('invulnerable_frames', 'int8', 2),
                ('attacks_num', 'int8'),
                ('damages_num', 'int8'),
                ('motions_num', 'int8'),
                ('shortcuts_num', 'int8'),
                ('footsteps_num', 'int8'),
                ('particles_num', 'int8'),
                ('unused2', 'byte[24] ')
            ],
            'raw_fields' : {
                'bodyparts' : [
                    ('start_pos', 'short', 'bodyparts_num'),
                    ('start_pos', 'short', 'bodyparts_num'),
                ]
           }
        },
    'TRAS'  :  {
    	   'description' : 'Totoro Aiming Screen',
    	   'fields' : []
        },
    'TRBS'  :  {
    	   'description' : 'Totoro Body Set',
    	   'fields' : [
                ('links_TRCM', 'int[5]'),
                ('unused', 'byte[4]')
           ]
        },
    'TRCM'  :  {
    	   'description' : 'Totoro Quaternion Body',
    	   'fields' : [
                ('unused1', 'int'),                 # 0 for most TRCM files, "dead" for the rest
                ('bodyparts_count', 'short'),       # 19 bodyparts
                ('unused2', 'byte[2]'),
                ('internal_name', 'char[64]'),      # internal name of this file
                ('rt', 'int[3]'),                   # overwritten at runtime
                ('link_TRGA', 'int'),   
                ('link_TRTA', 'int'),
                ('link_TRIA', 'int'),
                ('unused3', 'byte[24]'),
            ]
        },
    'TRGA'  :  {
    	   'description' : 'Totoro Quaternion Body Geometry Array',
    	   'fields' : [
                ('unused', 'char[22]'),
                ('size', 'short'),
                ('links_M3GM', 'int', 'size'),
            ]
        },
    'TRGE'  :  {
    	   'description' : 'Trigger Emitter',
    	   'fields' : []
        },
    'TRIA'  :  {
    	   'description' : 'Totoro Quaternion Body Index Array',
    	   'fields' : [
                ('unused', 'char[22]'),
                ('size', 'short'),
                ('bones', [
                    ('parent', 'int8'),
                    ('child', 'int8'),
                    ('sibling', 'int8'),
                    ('unused', 'char'),
                ], 'size')
           ]
        },
    'TRIG'  :  {
    	   'description' : 'Trigger',
    	   'fields' : []
        },
    'TRMA'  :  {
    	   'description' : 'Texture Map Array',
    	   'fields' : []
        },
    'TRSC'  :  {
    	   'description' : 'Screen (Aiming) Collection',
    	   'fields' : []
        },
    'TRTA'  :  {
    	   'description' : 'Totoro Quaternion Body Translation Array',
    	   'fields' : [
                ('unused', 'char[22]'),
                ('size', 'short'),
                ('bones_offsets', 'float[3]', 'size')
           ]
        },
    'TSFF'  :  {
    	   'description' : 'Font Family',
    	   'fields' : []
        },
    'TSFL'  :  {
    	   'description' : 'Font Language',
    	   'fields' : []
        },
    'TSFT'  :  {
    	   'description' : 'Font',
    	   'fields' : []
        },
    'TSGA'  :  {
    	   'description' : 'Glyph Array',
    	   'fields' : []
        },
    'TURR'  :  {
    	   'description' : 'Turret',
    	   'fields' : []
        },
    'TXAN'  :  {
    	   'description' : 'Texture Map Animation',
    	   'fields' : []
        },
    'TXCA'  :  {
    	   'description' : 'Texture Coordinate Array',
    	   'fields' : [
                ('unused', 'char[20]'),
                ('size', 'int'),
                ('texture_coords', 'float[2]', 'size')
           ]
        },
    'TXMA'  :  {
    	   'description' : 'Texture Map Array',
    	   'fields' : []
        },
    'TXMB'  :  {
    	   'description' : 'Texture Map Big',
    	   'fields' : []
        },
    'TXMP'  :  {
    	   'description' : 'Texture Map',
    	   'fields' : [
                        ('tname', 'char[128]'),         # name of the texture; unused
                        ('options', 'int'),             # options
                        ('width', 'short'),             # width of the image in pixels
                        ('height', 'short'),            # height of the image in pixels
                        ('format', 'int'),              # texture format
                        ('link_txan', 'int'),           # link to a TXAN file; used if this texture is animated
                        ('link_txmp', 'int'),           # link to a TXMP file that contain the environment map
                        ('toffset', 'int'),             # at this position starts the texture part in the raw file (PC only)
                        ('toffset_mac', 'int'),         # at this position starts the texture part in the sep file (Mac and PC demo only)
                        ('unused', 'char[28]')          # unused
            ]
        },
    'TxtC'  :  {
    	   'description' : 'Text Console',
    	   'fields' : []
        },
    'VCRA'  :  {
    	   'description' : '3D Vector Array',
    	   'fields' : [
                ('unused', 'char[20]'),
                ('size', 'int'),
                ('vectors_coords', 'float[3]', 'size')
           ]
        },
    'WMCL'  :  {
    	   'description' : 'WM Cursor List',
    	   'fields' : []
        },
    'WMDD'  :  {
    	   'description' : 'WM Dialog Data',
    	   'fields' : []
        },
    'WMM_'  :  {
    	   'description' : 'WM Menu',
    	   'fields' : []
        },
    'WMMB'  :  {
    	   'description' : 'WM Menu Bar',
    	   'fields' : []
        },
    'WPge'  :  {
    	   'description' : 'Weapon Page',
    	   'fields' : []
        },
    'AGDB'  :  {
    	   'description' : 'Gunk Quad Debug Array',
    	   'fields' : []
        },
    'AITR'  :  {
    	   'description' : 'AI Script Trigger Array',
    	   'fields' : []
        },
    'AKDA'  :  {
    	   'description' : 'Door Frame Array',
    	   'fields' : []
        },
    'OBDC'  :  {
    	   'description' : 'Door Class Array',
    	   'fields' : []
        },
    'ONFA'  :  {
    	   'description' : 'Imported Flag Node Array',
    	   'fields' : []
        },
    'ONMA'  :  {
    	   'description' : 'Imported Marker Node Array',
    	   'fields' : []
        },
    'ONSA'  :  {
    	   'description' : 'Imported Spawn Array',
    	   'fields' : []
        },
    'ONTA'  :  {
    	   'description' : 'Trigger Array',
    	   'fields' : []
        },
    'StNA'  :  {
    	   'description' : 'String Array',
    	   'fields' : []
        },
    'TStr'  :  {
    	   'description' : 'String',
    	   'fields' : []
        }
}


BODYPARTS = ['pelvis', 'thigh.L', 'calf.L', 'foot.L',
            'thigh.R', 'calf.R', 'foot.R', 'mid', 'chest',
            'neck', 'head', 'shoulder.L', 'arm.L', 'wrist.L',
            'fist.L', 'shoulder.R', 'arm.R', 'wrist.R', 'fist.R']