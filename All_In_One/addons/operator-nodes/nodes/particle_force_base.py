from .. base_node_types import DeclarativeNode

class ParticleForceNode(DeclarativeNode):
    def get_force_code(self):
        raise NotImplementedError()