#!BPY
# -*- coding: UTF-8 -*-
# bone_constraints
#
# Manage Bone Constraints Setting DATA
# 2018.06.06 N(Natukikazemizo)

class BoneConstraints:

    header = [
            "bone_name",            # 0
            "constraint_name",      # 1
            "mute",                 # 2
            "target",               # 3
            "subtarget_bone_name",  # 4
            "extrapolate",          # 5
            "from_min_x",           # 6
            "from_max_x",           # 7
            "from_min_y",           # 8
            "from_max_y",           # 9
            "from_min_z",           # 10
            "from_max_z",           # 11
            "map_to_x_from",        # 12
            "map_to_y_from",        # 13
            "map_to_z_from",        # 14
            "map_to",               # 15
            "to_min_x",             # 16
            "to_max_x",             # 17
            "to_min_y",             # 18
            "to_max_y",             # 19
            "to_min_z",             # 20
            "to_max_z",             # 21
            "target_space",         # 22
            "owner_space",          # 23
            "influence",            # 24
            "type",                 # 25
            "head_tail",            # 26 FOR COPY LOCATION
            "use_offset",           # 27
            "pole_target",          # 28 FOR IK
            "pole_subtarget",       # 29
            "pole_angle",           # 30
            "iterations",           # 31
            "chain_count",          # 32
            "use_tail",             # 33
            "use_stretch",          # 34
            "use_location",         # 35
            "weight",               # 36
            "use_rotation",         # 37
            "orient_weight"         # 38
              ]

    def __init__(self, row = None):
        if row is None:
            self.row = ["" for i in range(128)]
        else:
            self.row = row

    @property
    def bone_name(self):
        return self.row[self.header.index("bone_name")]

    @bone_name.setter
    def bone_name(self, value):
        self.row[self.header.index("bone_name")] = value

    @property
    def constraint_name(self):
        return self.row[self.header.index("constraint_name")]

    @constraint_name.setter
    def constraint_name(self, value):
        self.row[self.header.index("constraint_name")] = value

    @property
    def mute(self):
        return self.row[self.header.index("mute")]

    @bone_name.setter
    def mute(self, value):
        self.row[self.header.index("mute")] = value

    @property
    def target(self):
        return self.row[self.header.index("target")]

    @target.setter
    def target(self, value):
        self.row[self.header.index("target")] = value

    @property
    def subtarget_bone_name(self):
        return self.row[self.header.index("subtarget_bone_name")]

    @subtarget_bone_name.setter
    def subtarget_bone_name(self, value):
        self.row[self.header.index("subtarget_bone_name")] = value

    @property
    def extrapolate(self):
        return self.row[self.header.index("extrapolate")]

    @extrapolate.setter
    def extrapolate(self, value):
        self.row[self.header.index("extrapolate")] = value

    @property
    def from_min_x(self):
        return self.row[self.header.index("from_min_x")]

    @from_min_x.setter
    def from_min_x(self, value):
        self.row[self.header.index("from_min_x")] = value

    @property
    def from_max_x(self):
        return self.row[self.header.index("from_max_x")]

    @from_max_x.setter
    def from_max_x(self, value):
        self.row[self.header.index("from_max_x")] = value

    @property
    def from_min_y(self):
        return self.row[self.header.index("from_min_y")]

    @from_min_y.setter
    def from_min_y(self, value):
        self.row[self.header.index("from_min_y")] = value

    @property
    def from_max_y(self):
        return self.row[self.header.index("from_max_y")]

    @from_max_y.setter
    def from_max_y(self, value):
        self.row[self.header.index("from_max_y")] = value

    @property
    def from_min_z(self):
        return self.row[self.header.index("from_min_z")]

    @from_min_z.setter
    def from_min_z(self, value):
        self.row[self.header.index("from_min_z")] = value

    @property
    def from_max_z(self):
        return self.row[self.header.index("from_max_z")]

    @from_max_z.setter
    def from_max_z(self, value):
        self.row[self.header.index("from_max_z")] = value

    @property
    def map_to_x_from(self):
        return self.row[self.header.index("map_to_x_from")]

    @map_to_x_from.setter
    def map_to_x_from(self, value):
        self.row[self.header.index("map_to_x_from")] = value

    @property
    def map_to_y_from(self):
        return self.row[self.header.index("map_to_y_from")]

    @map_to_y_from.setter
    def map_to_y_from(self, value):
        self.row[self.header.index("map_to_y_from")] = value

    @property
    def map_to_z_from(self):
        return self.row[self.header.index("map_to_z_from")]

    @map_to_z_from.setter
    def map_to_z_from(self, value):
        self.row[self.header.index("map_to_z_from")] = value

    @property
    def map_to(self):
        return self.row[self.header.index("map_to")]

    @map_to.setter
    def map_to(self, value):
        self.row[self.header.index("map_to")] = value

    @property
    def to_min_x(self):
        return self.row[self.header.index("to_min_x")]

    @to_min_x.setter
    def to_min_x(self, value):
        self.row[self.header.index("to_min_x")] = value

    @property
    def to_max_x(self):
        return self.row[self.header.index("to_max_x")]

    @to_max_x.setter
    def to_max_x(self, value):
        self.row[self.header.index("to_max_x")] = value

    @property
    def to_min_y(self):
        return self.row[self.header.index("to_min_y")]

    @to_min_y.setter
    def to_min_y(self, value):
        self.row[self.header.index("to_min_y")] = value

    @property
    def to_max_y(self):
        return self.row[self.header.index("to_max_y")]

    @to_max_y.setter
    def to_max_y(self, value):
        self.row[self.header.index("to_max_y")] = value

    @property
    def to_min_z(self):
        return self.row[self.header.index("to_min_z")]

    @to_min_z.setter
    def to_min_z(self, value):
        self.row[self.header.index("to_min_z")] = value

    @property
    def to_max_z(self):
        return self.row[self.header.index("to_max_z")]

    @to_max_z.setter
    def to_max_z(self, value):
        self.row[self.header.index("to_max_z")] = value

    @property
    def target_space(self):
        return self.row[self.header.index("target_space")]

    @target_space.setter
    def target_space(self, value):
        self.row[self.header.index("target_space")] = value

    @property
    def owner_space(self):
        return self.row[self.header.index("owner_space")]

    @owner_space.setter
    def owner_space(self, value):
        self.row[self.header.index("owner_space")] = value

    @property
    def influence(self):
        return float(self.row[self.header.index("influence")])

    @influence.setter
    def influence(self, value):
        self.row[self.header.index("influence")] = value

    @property
    def type(self):
        return self.row[self.header.index("type")]

    @type.setter
    def type(self, value):
        self.row[self.header.index("type")] = value

    @property
    def head_tail(self):
        return self.row[self.header.index("head_tail")]

    @head_tail.setter
    def head_tail(self, value):
        self.row[self.header.index("head_tail")] = value

    @property
    def use_offset(self):
        return self.row[self.header.index("use_offset")] == "True"

    @use_offset.setter
    def use_offset(self, value):
        self.row[self.header.index("use_offset")] = value

    @property
    def pole_target(self):
        return self.row[self.header.index("pole_target")]

    @pole_target.setter
    def pole_target(self, value):
        self.row[self.header.index("pole_target")] = value

    @property
    def pole_subtarget(self):
        return self.row[self.header.index("pole_subtarget")]

    @pole_subtarget.setter
    def pole_subtarget(self, value):
        self.row[self.header.index("pole_subtarget")] = value

    @property
    def pole_angle(self):
        return float(self.row[self.header.index("pole_angle")])

    @pole_angle.setter
    def pole_angle(self, value):
        self.row[self.header.index("pole_angle")] = value

    @property
    def iterations(self):
        return int(self.row[self.header.index("iterations")])

    @iterations.setter
    def iterations(self, value):
        self.row[self.header.index("iterations")] = value

    @property
    def chain_count(self):
        return int(self.row[self.header.index("chain_count")])

    @chain_count.setter
    def chain_count(self, value):
        self.row[self.header.index("chain_count")] = value

    @property
    def use_tail(self):
        return self.row[self.header.index("use_tail")] == "True"

    @use_tail.setter
    def use_tail(self, value):
        self.row[self.header.index("use_tail")] = value

    @property
    def use_stretch(self):
        return self.row[self.header.index("use_stretch")] == "True"

    @use_stretch.setter
    def use_stretch(self, value):
        self.row[self.header.index("use_stretch")] = value

    @property
    def use_location(self):
        return self.row[self.header.index("use_location")] == "True"

    @use_location.setter
    def use_location(self, value):
        self.row[self.header.index("use_location")] = value

    @property
    def weight(self):
        return float(self.row[self.header.index("weight")])

    @weight.setter
    def weight(self, value):
        self.row[self.header.index("weight")] = value

    @property
    def use_rotation(self):
        return self.row[self.header.index("use_rotation")] == "True"

    @use_rotation.setter
    def use_rotation(self, value):
        self.row[self.header.index("use_rotation")] = value

    @property
    def orient_weight(self):
        return float(self.row[self.header.index("orient_weight")])

    @orient_weight.setter
    def orient_weight(self, value):
        self.row[self.header.index("orient_weight")] = value
