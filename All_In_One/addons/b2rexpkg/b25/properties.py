import bpy

from bpy.props import StringProperty, PointerProperty, IntProperty
from bpy.props import BoolProperty, FloatProperty, CollectionProperty
from bpy.props import FloatVectorProperty, EnumProperty

if not hasattr(bpy.utils, 'register_class'):
    # blender 2.56 compatibility
    class PropertyGroup(bpy.types.IDPropertyGroup):
        pass


from .logic import B2RexFsm, B2RexComponent

import logging

states = (("UPLOADING", 'Uploading', 'standard level, show only errors'),
              ("OK", 'Ok', 'show only critical errors (least info)'),
              ("LOADING", 'Loading', 'show warnings or errors'),
              ("TAKING", 'Taking', 'show warnings or errors'),
              ("OFFLINE", 'Offline', 'show warnings or errors'),
              ("LOADED", 'Loaded', 'show info or errors'))

class B2RexConnection(bpy.types.PropertyGroup):
    name = StringProperty(name='name', default='', description='')
    url = StringProperty(name='url', default='', description='')
    username = StringProperty(name='username', default='', description='')

class B2RexConnectionForm(bpy.types.PropertyGroup):
    name = StringProperty(name='name', default='')
    url = StringProperty(name='login url', default='http://')
    username = StringProperty(name='username', default='')
    password = StringProperty(name='password', default='')

class B2RexConnections(bpy.types.PropertyGroup):
    list = CollectionProperty(type=B2RexConnection,
                                     name='Connections',
                                     description='Sessions on the server')
    selected = IntProperty(default=-1, description="Expand, to display")
    search = StringProperty(name='search', default="select connection", description="Expand, to display")
    expand = BoolProperty(default=False, description="Expand connection controls")
    form = PointerProperty(type=B2RexConnectionForm, description="Connection form")


class B2RexRegions(bpy.types.PropertyGroup):
    name = StringProperty(name='name', default='', description='')

class B2RexTextProps(bpy.types.PropertyGroup):
    uuid = StringProperty(name='uuid', default='', description='')
    state = EnumProperty(items=states, default='OFFLINE', description='')


class B2RexChatLine(bpy.types.PropertyGroup):
    name = StringProperty(name='name', default='', description='')

class B2RexBaseProps(bpy.types.PropertyGroup):
    uuid = StringProperty(name='uuid', default='', description='')

class B2RexObjectProps(B2RexBaseProps):
    name = StringProperty(name='name', default='Primitive', description='')
    uuid = StringProperty(name='uuid', default='', description='')
    state = EnumProperty(items=states, default='OFFLINE', description='')
    everyonemask_expand = BoolProperty(name='everyonemask_expand', default=False)
    fsm = PointerProperty(type=B2RexFsm, name="fsm")
    component_data = CollectionProperty(type=B2RexComponent, name='components')
    selected_component = StringProperty(default="")
    next_component_idx = IntProperty(default=0)


class B2RexMeshProps(B2RexBaseProps):
    uuid = StringProperty(name='uuid', default='', description='')

class B2RexTextureProps(B2RexBaseProps):
    uuid = StringProperty(name='uuid', default='', description='')

class B2RexImageProps(B2RexBaseProps):
    uuid = StringProperty(name='uuid', default='', description='')

class B2RexMaterialProps(B2RexBaseProps):
    uuid = StringProperty(name='uuid', default='', description='')
    autodetect = BoolProperty(name="autodetect", default=True)
    shader = StringProperty(name='shader',
                              default='',
                              description='')

class B2RexProps(bpy.types.PropertyGroup):
    #B2RexProps.credentials = PasswordManager("b2rex")
    path = StringProperty(name='path', default='', description='')
    pack = StringProperty(name='pack', default='pack')
    username = StringProperty(name='username',
                              default='caedes caedes',
                              description='')
    password = StringProperty(name='password',
                              default='nemesis',
                              description='')
    loglevel = IntProperty(name='loglevel',
                           default=logging.ERROR,
                          description='log level')
    server_url = StringProperty(name='server url',
                                default='http://delirium:9000',
                                description='')
    agent_libs_path = StringProperty(name='agent libraries',
                                     default='',
                                     description='path to the agent python libraries')
    tools_path = StringProperty(name='tools path',
                                     default='',
                                     description='path to tools required by the exporter')

    tundra_path = StringProperty(name='tundra path',
                                     default='',
                                     description='path to tundra binary folder (where server and viewer are located)')


    export_dir = StringProperty(name='export dir',
                                default='',
                                description='') 
    loc = FloatVectorProperty(name="location", 
                              description="offset to apply when exporting",
                              default=(128.0, 128.0, 20.0),
                              min=0.0,
                              max=512.0)
    regenMaterials = BoolProperty(name="Regen Material", default=True)
    rt_on = BoolProperty(name="RT", default=False, description="Enable real time connection")
    rt_budget = IntProperty(name="Rt Budget", default=20, min=5,
                              max=500, step=1, description="Number of milliseconds allocated for command execution every frame")
    rt_sec_budget = IntProperty(name="Rt Budget per second", default=250, min=50,
                              max=1000, step=1, description="Number of  milliseconds allocated for command execution every second")
    pool_workers = IntProperty(name="Download Threads", default=5, min=1,
                               max=100, step=1, description="Number of threads dedicated to downloading and transcoding")
    kbytesPerSecond = IntProperty(name="Kbyte/s", default=100,
                                      description="kbytes per second to throttle the connection to")

    regenObjects = BoolProperty(name="Regen Objects", default=False)
    regenTextures = BoolProperty(name="Regen Textures", default=False)
    regenObjects = BoolProperty(name="Regen Objects", default=False)
    importTerrain = BoolProperty(name="Import Terraion", default=True)
    importTextures = BoolProperty(name="Import Textures", default=True)

    terrainLOD = IntProperty(name="Terrain LOD", default=1, min=0, max=4,
                                  description="terrain lod level, needs restart to take effect")
    regenMeshes = BoolProperty(name="Regen Meshes", default=False)
    expand = BoolProperty(default=True,
                          description="Expand, to display settings")
    show_stats = BoolProperty(default=False,
                          description="Expand, to display stats")
    chat = CollectionProperty(type=B2RexChatLine,
                                 name='Chat',
                                 description='Chat with the server')
    connection = PointerProperty(type=B2RexConnections, name="Connections")
    def getCurrentConnection(self):
        return self.connection.list[self.connection.search]
    selected_chat = IntProperty(default=-1, description="Expand, to display")
    next_chat = StringProperty(name='next_chat',
                              default='',
                              description='')
    inventory_expand = BoolProperty(default=False, description="Expand inventory")
    #inventory_expand = property(get_expand, set_expand) # XXX doesnt work?

    regions = CollectionProperty(type=B2RexRegions,
                                 name='Regions',
                                 description='Sessions on the server')
    regions_expand = BoolProperty(default=False, description="Expand region controls")
    selected_region = IntProperty(default=-1, description="Expand, to display")
    chat_expand = BoolProperty(default=False, description="Expand chat")
#    B2RexProps.regions.name = StringProperty(name='Name', description='Name of the session', maxlen=128, default='[session]')

