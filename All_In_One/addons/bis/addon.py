# Nikita Akimov
# interplanety@interplanety.org

from distutils.version import StrictVersion
import addon_utils


class Addon:

    _addon_name = 'BIS'
    node_group_first_version = '1.4.1'  # from 1.4.1 start to save it

    @staticmethod
    def version_equal_or_higher(version_num):
        return StrictVersion(__class__.current_version()) >= StrictVersion(version_num)

    @staticmethod
    def version_equal_or_less(version_num):
        return StrictVersion(__class__.current_version()) <= StrictVersion(version_num)

    @staticmethod
    def node_group_version_higher(node_group_version, version_num):
        # node_group_version = node_group['BIS_addon_version'] if 'BIS_addon_version' in node_group else __class__.node_group_first_version
        node_group_version = node_group_version if node_group_version else __class__.node_group_first_version
        return StrictVersion(node_group_version) > StrictVersion(version_num)

    @staticmethod
    def node_group_version_equal_or_less(node_group_version, version_num):
        # node_group_version = node_group['BIS_addon_version'] if 'BIS_addon_version' in node_group else __class__.node_group_first_version
        node_group_version = node_group_version if node_group_version else __class__.node_group_first_version
        return StrictVersion(node_group_version) <= StrictVersion(version_num)

    @staticmethod
    def current_version():
        version_tuple = [addon.bl_info['version'] for addon in addon_utils.modules() if addon.bl_info['name'] == __class__._addon_name][0]   # (1, 4, 2)
        return '.'.join(map(str, version_tuple))    # '1.4.2'
