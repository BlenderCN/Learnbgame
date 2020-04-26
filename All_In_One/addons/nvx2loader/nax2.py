"""TODO: DOC"""

import collections

Header = collections.namedtuple('Header', 'magic \
                                           num_groups \
                                           num_keys')


Group = collections.namedtuple('Group', 'num_curves \
                                         startkey_idx \
                                         num_keys \
                                         key_stride \
                                         key_time \
                                         fade_in_frames \
                                         loop_type \
                                         meta_data')


Curve = collections.namedtuple('Curve', 'ipol_type \
                                         first_key_idx \
                                         curve_type \
                                         is_static \
                                         static_key')


CurveRaw = collections.namedtuple('Curve', 'ipol_type \
                                            first_key_idx \
                                            is_anim \
                                            key_x \
                                            key_y \
                                            key_z \
                                            key_w')
