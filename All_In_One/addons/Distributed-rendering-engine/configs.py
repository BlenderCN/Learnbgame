import bpy
import os
from bpy.props import *
from bpy.types import CollectionProperty

class MasterConfigurations(bpy.types.PropertyGroup):
    @classmethod
    def register(Configurations):

        default_path = os.environ.get("TEMP")
        if not default_path:
            if os.name == 'nt':
                default_path = "c:/tmp/"
            else:
                default_path = "/tmp/"
        elif not default_path.endswith(os.sep):
            default_path += os.sep
        Configurations.path = StringProperty(
                        name="Path",
                        description="Path for files",
                        maxlen = 128,
                        default = default_path,
                        subtype='FILE_PATH')

        Configurations.self_address = StringProperty(
                        name="Self IP ",
                        description="IP of this machine",
                        maxlen = 128,
                        default = "[default]")

        Configurations.port_no = StringProperty(
                        name="Port",
                        description="Port number",
                        maxlen = 128,
                        default = "8000")

        Configurations.serviceThread=None

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.Masterconfigs

class SlaveConfigurations(bpy.types.PropertyGroup):
    @classmethod
    def register(Configurations):

        default_path = os.environ.get("TEMP")
        if not default_path:
            if os.name == 'nt':
                default_path = "c:/tmp/"
            else:
                default_path = "/tmp/"
        elif not default_path.endswith(os.sep):
            default_path += os.sep
        Configurations.path = StringProperty(
                        name="Path",
                        description="Path for temp files",
                        maxlen = 128,
                        default = default_path,
                        subtype='FILE_PATH')

        Configurations.master_address = StringProperty(
                        name="Master IP ",
                        description="IP of Master",
                        maxlen = 128,
                        default = "[default]")

        Configurations.self_address = StringProperty(
                        name="Self IP ",
                        description="IP of Self",
                        maxlen = 128,
                        default = "[default]")        

        Configurations.port_no = StringProperty(
                        name="Port",
                        description="Port number",
                        maxlen = 128,
                        default = "8000")

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.SlaveConfig

bpy.utils.register_class(MasterConfigurations)
bpy.utils.register_class(SlaveConfigurations)

bpy.types.Scene.MasterConfigs = PointerProperty(type=MasterConfigurations, name="Network Render", description="Network Render Settings for Master")
bpy.types.Scene.SlaveConfigs = PointerProperty(type=SlaveConfigurations, name="Network Render22", description="Network Render Settings for Slave")
