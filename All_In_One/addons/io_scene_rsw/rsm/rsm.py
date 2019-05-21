
class Rsm(object):

    class Node(object):

        class LocationKeyFrame(object):
            def __init__(self):
                self.frame = 0
                self.location = (0.0, 0.0, 0.0)

        class RotationKeyFrame(object):
            def __init__(self):
                self.frame = 0
                self.rotation = (0.0, 0.0, 0.0, 0.0)

        class Face(object):
            def __init__(self):
                self.vertex_indices = (0, 0, 0)
                self.texcoord_indices = (0, 0, 0)
                self.unk1 = None

        def __init__(self):
            self.name = ''
            self.parent_name = ''
            self.texture_indices = []
            self.vertices = []
            self.texcoords = []
            self.faces = []
            self.location_keyframes = []
            self.rotation_keyframes = []

    def __init__(self):
        self.main_node = ''
        self.shade_type = 0
        self.alpha = 0xff
        self.anim_length = 0
        self.textures = []
        self.nodes = []
        pass
