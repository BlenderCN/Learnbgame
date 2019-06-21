
import bpy


class WarCraft3Model:
    def __init__(self):
        self.name = None
        self.meshes = []
        self.materials = []
        self.textures = []
        self.nodes = []
        self.sequences = []
        self.geoset_animations = []
        self.pivot_points = []

    def normalize_meshes_names(self):
        for mesh in self.meshes:
            mesh.name = self.name

class WarCraft3Bone:
    def __init__(self):
        self.type = 'bone'
        self.node = None
        self.geoset_id = None


class WarCraft3Helper:
    def __init__(self):
        self.type = 'helper'
        self.node = None


class WarCraft3Attachment:
    def __init__(self):
        self.type = 'attachment'
        self.node = None


class WarCraft3Event:
    def __init__(self):
        self.type = 'event'
        self.node = None


class WarCraft3CollisionShape:
    def __init__(self):
        self.type = 'collision_shape'
        self.node = None


class WarCraft3Node:
    def __init__(self):
        self.name = None
        self.id = None
        self.parent = None
        self.translations = None
        self.rotations = None
        self.scalings = None


class WarCraft3GeosetTransformation:
    def __init__(self):
        self.tracks_count = None
        self.interpolation_type = None
        self.times = []
        self.values = []


class WarCraft3Mesh:
    def __init__(self):
        self.name = None
        self.vertices = []
        self.triangles = []
        self.uvs = []
        self.material_id = None
        self.vertex_groups = []
        self.vertex_groups_ids = None


class WarCraft3Layer:
    def __init__(self):
        self.texture_id = None
        self.material_alpha = None
        self.material_texture_id = None


class WarCraft3Material:
    def __init__(self):
        self.layers = []


class WarCraft3Texture:
    def __init__(self):
        self.image_file_name = None
        self.replaceable_id = None


class WarCraft3Sequence:
    def __init__(self):
        self.name = None
        self.interval_start = None
        self.interval_end = None


class WarCraft3GeosetAnimation:
    def __init__(self):
        self.geoset_id = None
        self.animation_color = None
        self.animation_alpha = None


class MDXImportProperties:
    def __init__(self):
        self.mdx_file_path = ''
        self.team_color = None
        self.bone_size = 1.0
        self.use_custom_fps = False
        self.fps = 30
        self.frame_time = 1.0

    def calculate_frame_time(self):
        if not self.use_custom_fps:
            self.fps = bpy.context.scene.render.fps
        self.frame_time = 1000 / self.fps
