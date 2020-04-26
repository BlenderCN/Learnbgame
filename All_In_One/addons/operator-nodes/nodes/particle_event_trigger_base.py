from .. base_node_types import DeclarativeNode

class ParticleEventTriggerNode(DeclarativeNode):
    def get_trigger_code(self):
        raise NotImplementedError()