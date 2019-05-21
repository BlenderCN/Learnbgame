class FVF(object):
    FVF_FLAGS = {'D3DFVFRESERVED0': 0,
                 'D3DFVF_XYZ': 1,
                 'D3DFVF_XYZRHW': 2,
                 'D3DFVF_UNUSED': 3,
                 'D3DFVF_NORMAL': 4,
                 'D3DFVF_RESERVED1': 5,
                 'D3DFVF_DIFFUSE': 6,
                 'D3DFVF_SPECULAR': 7,
                 'D3DFVF_TEX1': 8,
                 'D3DFVF_TEX2': 9,
                 'D3DFVF_TEX3': 10,
                 'D3DFVF_TEX4': 11,
                 'D3DFVF_TEX5': 12,
                 'D3DFVF_TEX6': 13,
                 'D3DFVF_TEX7': 14,
                 'D3DFVF_TEX8': 15}

    value = 0

    def set_flag(self, flag):
        self.value |= (1 << self.FVF_FLAGS[flag])

    def clear_flag(self, flag):
        self.value &= ~(1 << self.FVF_FLAGS[flag])

    def has_flag(self, flag):
        return ((self.value & (1 << self.FVF_FLAGS[flag])) != 0)

    def __init__(self, preset_flags=None):
        if preset_flags is not None:
            if isinstance(preset_flags, int):
                self.value = preset_flags
            else:
                for flg in preset_flags:
                    self.set_flag(flg)
