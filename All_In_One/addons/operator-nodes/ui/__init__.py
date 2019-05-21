import bpy
from . data_flow_group_info_panel import DataFlowGroupInfoPanel
from . mesh_modifier_panel import MeshModifierPanel
from . particles_panel import ParticlesPanel
from . driver_panel import DriverPanel

panels = [
    DataFlowGroupInfoPanel,
    MeshModifierPanel,
    ParticlesPanel,
    DriverPanel
]

def register():
    for cls in panels:
        bpy.utils.register_class(cls)

def unregister():
    for cls in panels:
        bpy.utils.unregister_class(cls)