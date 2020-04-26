import bpy
import sys
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .operatorsList import operatorList
from .operatorHelpers import resetTriggerSettings, simpleCube, setTrigger
from .managers import ModelManager
from .SearchOperator import SearchOperator
from .AddOperator import AddOperator
from .TriggerSetOperator import TriggerSetOperator
from .WallSetOperator import WallSetOperator
from .VolumeSetOperator import VolumeSetOperator
from .DestinationSetOperator import DestinationSetOperator

operators = []
idnamePrefix = "radix"

def addOperators():
  for opData in operatorList:
    if "action" in opData["properties"] and not isinstance(opData["properties"]["action"], str):
      opData["properties"]["action"] = staticmethod(opData["properties"]["action"])

    if "bl_idname" in opData["properties"] \
       and not opData["properties"]["bl_idname"].startswith(idnamePrefix):
      opData["properties"]["bl_idname"] = idnamePrefix + "." + opData["properties"]["bl_idname"]

    base = getattr(sys.modules[__name__], opData["base"])

    operator = type(
      opData["className"],
      (base, ),
      opData["properties"]
    )
    operators.append(operator)
    bpy.utils.register_class(operator)


def removeOperators():
  global operators

  for operator in operators:
    bpy.utils.unregister_class(operator)

  del operators[:]
