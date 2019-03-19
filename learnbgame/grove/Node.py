# coding=utf-8

""" Copyright 2014 - 2018, Wybren van Keulen, The Grove """


from mathutils import Vector


class Node(object):
    """ A node is simple data structure without functionality. It stores all the info that defines a branch node. 
        A branch consists of a list of nodes and a node has a list of sub branches, and so on... """
    
    # Slots make a class less dynamic, but faster and less memory consumptive.
    __slots__ = ["direction", "pos", "sub_branches", "node_weight", "real_weight", "thickness", "radius",
                 "dead", "dead_thickness", "photosynthesis", "phloem", "xylem", "auxin",
                 "baked_weight", "leaf_weight", "wind_area"]

    def __init__(self, direction):
        """ Give all parameters a starting value. """
        
        self.direction = direction  # Position relative to parent node.
        self.pos = Vector((0.0, 0.0, 0.0))  # Absolute position, for pruning and building.
        self.sub_branches = []
        self.node_weight = 0
        self.real_weight = 0.0
        self.thickness = 0.0
        self.radius = 0.0
        self.dead = False
        self.dead_thickness = 0.0
        self.photosynthesis = 0.0
        self.phloem = 0.0
        self.xylem = 0.0
        self.auxin = 0.0
        self.baked_weight = 0.0
        self.leaf_weight = 0
        self.wind_area = 0.0
