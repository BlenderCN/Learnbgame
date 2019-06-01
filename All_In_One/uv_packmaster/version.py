
class VersionInfo:
    suffix = None
    name = None
    long_name = None
    marker = None

    def __init__(self, _num, _suffix, _name, _long_name, _marker):
        self.num = _num
        self.suffix = _suffix
        self.name = _name
        self.long_name = _long_name
        self.marker = _marker

def get_packer_version_array():
    version_array = [VersionInfo(1, 'e', 'extend', 'extended', 'UVP_VERSION_EXTENDED'),
                     VersionInfo(2, 'p', 'pro', 'professional', 'UVP_VERSION_PRO'),
                     VersionInfo(3, 'd', 'demo', 'DEMO', 'UVP_VERSION_DEMO')]

    return version_array