import bpy

from . import livebuild_helper

class ElfinSceneProperties(bpy.types.PropertyGroup):
    """Elfin's Scene property catcher class"""

    pp_src_dir = bpy.props.StringProperty(
        subtype='DIR_PATH', 
        default='obj_aligned')
    pp_dst_dir = bpy.props.StringProperty(
        subtype='FILE_PATH', 
        default='module_library.blend')
    pp_decimate_ratio = bpy.props.FloatProperty(default=0.15, min=0.00, max=1.00)
    disable_auto_collision_check = bpy.props.BoolProperty(default=True)

    def reset(self):
        print('{} reset'.format(self.__class__.__name__))
        self.property_unset('pp_src_dir')
        self.property_unset('pp_dst_dir')
        self.property_unset('pp_decimate_ratio')
        self.property_unset('disable_auto_collision_check')
        livebuild_helper.LivebuildState().reset()