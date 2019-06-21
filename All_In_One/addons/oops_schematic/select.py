
from .constants import *


def select_children(schematic_node):
    for child in schematic_node.children:
        schematic_node.active_child.append(child)
        if not child.active:
            child.active = True
            child.color[0] += LIGHT_ADD_COLOR
            child.color[1] += LIGHT_ADD_COLOR
            child.color[2] += LIGHT_ADD_COLOR
        select_children(child)


def select_parents(schematic_node):
    for parent in schematic_node.parents:
        parent.active_child.append(schematic_node)
        if not parent.active:
            parent.active = True
            parent.color[0] += LIGHT_ADD_COLOR
            parent.color[1] += LIGHT_ADD_COLOR
            parent.color[2] += LIGHT_ADD_COLOR
        select_parents(parent)
