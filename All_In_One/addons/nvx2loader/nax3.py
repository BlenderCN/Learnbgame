"""TODO: DOC"""

import collections

Header = collections.namedtuple('Header', 'magic \
                                           num_clips \
                                           num_keys')


Clip = collections.namedtuple('Clip', 'num_curves \
                                       startkey_idx \
                                       num_keys \
                                       key_stride \
                                       key_duration \
                                       pre_infinity_type \
                                       post_infinity_type \
                                       num_events \
                                       clip_name')


Event = collections.namedtuple('Event', 'event_name \
                                         category \
                                         key_index')

Curve = collections.namedtuple('Curve', 'first_key_idx \
                                         is_active \
                                         is_static \
                                         curve_type \
                                         static_key')

CurveRaw = collections.namedtuple('Curve', 'first_key_idx \
                                            is_active \
                                            is_static \
                                            curve_type \
                                            padding \
                                            key_x \
                                            key_y \
                                            key_z \
                                            key_w')
