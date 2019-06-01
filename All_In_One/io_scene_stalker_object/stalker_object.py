
class StalkerObject:
    class Flags:
        def __init__(self):
            self.dynamic = False
            self.progressive = False
            self.using_lod = False
            self.hom = False
            self.multiple_usage = False
            self.sound_occluder = False

    class Meshes:
        class Mesh:
            class Flags:
                def __init__(self):
                    self.visible = True
                    self.locked = False
                    self.smooth_group_mask = False

            def __init__(self):
                self.name = ''
                self.version = 17
                self.option_1 = 0
                self.option_2 = 0
                self.vertices = []
                self.triangles = []
                self.materials = {}
                self.uvs = []
                self.uv_map_name = ''
                self.smoothing_groups = []
                self.vertex_groups_names = []
                self.weights = []
                self.weight_vertices = []
                self.flags = None

            def set_flags(self, flags8bit):
                self.flags = self.Flags()
                self.flags.visible = bool(flags8bit & 0x01)
                self.flags.locked = bool(flags8bit & 0x02)
                self.flags.smooth_group_mask = bool(flags8bit & 0x04)

        def __init__(self):
            self.meshes = []

        def __getitem__(self, index):
            return self.meshes[index]

        def __len__(self):
            return len(self.meshes)

        def create(self):
            self.meshes.append(self.Mesh())

    class Material:
        def __init__(self):
            self.name = ''
            self.engine_shader = 'default'
            self.compiler_shader = 'default'
            self.game_material = 'default'
            self.texture = ''
            self.two_sided = False

    class Skelet:
        class Bones:
            class Bone:
                def __init__(self):
                    self.name = 'Bone'
                    self.parent = None
                    self.position = [0.0, 0.0, 0.0]
                    self.rotation = [0.0, 0.0, 0.0]
                    self.length = 0.01

            def __init__(self):
                self.bones = []

            def __getitem__(self, index):
                return self.bones[index]

            def __len__(self):
                return len(self.bones)

            def create(self):
                self.bones.append(self.Bone())

        def __init__(self):
            self.bones = self.Bones()

    class Context:
        def __init__(self):
            self.operator = None
            self.texture_folder = ''
            self.smoothing_groups_type = 'SOC'

    def __init__(self):
        self.context = self.Context()
        self.name = ''
        self.meshes = self.Meshes()
        self.skelet = self.Skelet()
        self.object_type = 'STATIC'
        self.materials = {}
        self.version = 16
        self.flags = self.Flags()
        self.user_data = ''
        self.creator = 'unknow'
        self.create_time = 0
        self.editor = 'unknow'
        self.edit_time = 0
        self.motion_reference = ''
        self.lod_reference = ''
        self.position = (0.0, 0.0, 0.0)
        self.rotation = (0.0, 0.0, 0.0)
