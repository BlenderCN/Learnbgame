import bpy
from . add_driver import AddDriverOperator
from . analyse_tree import AnalyseTreeOperator
from . modal_runner import ModalRunnerOperator
from . execute_callback import ExecuteCallbackOperator
from . interactive_mode import InteractiveModeOperator
from . socket_type_chooser import ChooseSocketTypeOperator
from . simulate_particle_system import SimulateParticleSystemOperator
from . print_driver_dependencies import PrintDriverDependenciesOperator

from . run_tree import RunTreeOperator

operators = [
    AddDriverOperator,
    AnalyseTreeOperator,
    ModalRunnerOperator,
    InteractiveModeOperator,
    ExecuteCallbackOperator,
    ChooseSocketTypeOperator,
    SimulateParticleSystemOperator,
    PrintDriverDependenciesOperator,
    RunTreeOperator
]


def register():
    for cls in operators:
        bpy.utils.register_class(cls)

def unregister():
    for cls in operators:
        bpy.utils.unregister_class(cls)