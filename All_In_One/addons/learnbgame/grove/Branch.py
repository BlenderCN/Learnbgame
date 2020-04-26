# coding=utf-8

""" This is where the magic happens. A collection of recursive functions that treats every 
    branch generation equal. Each branch does its thing and then calls its child branches 
    to do the same.

    Copyright 2014 - 2018, Wybren van Keulen, The Grove """


import bpy
from mathutils import Matrix, Vector, bvhtree, Euler, Quaternion
from math import pi
from random import random
from copy import copy, deepcopy

from .Node import Node
from .TwigInstance import TwigInstance
from .Utils import *


class Branch:

    def __init__(self, direction):

        self.nodes = []
        self.nodes.append(Node(direction))
        self.is_trunk = False
        self.marked_to_drop = False
        self.skip = False
        self.juice = 0.0
        self.power = 1.0
        self.shade = 0.0
        self.phototropism_direction = Vector((0.0, 0.0, 0.0))
        self.dead = False
        self.offset = 0.0
        self.initial_phyllotaxic_angle = 0.0
        self.is_regenerative = False
        self.tip_thickness = 0.001
        self.uv_offset_x = random()
        self.uv_offset_y = random()

    def count_branches(self):

        if len(self.nodes) > 1:
            number = 1
        else:
            number = 0

        for node in self.nodes:
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    number += sub_branch.count_branches()

        return number

    def count_power(self):

        total_power = self.power

        for node in self.nodes:
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    total_power += sub_branch.count_power()

        return total_power

    def add_regenerative(self, shade_samples, regenerative_branch_chance, regenerative_branch_chance_light_required,
                         internode_length, branch_angle, branching, twist, plagiotropism_buds, bvh, samples):

        if self.skip or self.dead:
            return 0

        cast = bvh.ray_cast
        number_of_regenerative_branches = 0

        for i, node in enumerate(self.nodes):
            if i == 0:
                continue

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    number_of_regenerative_branches += sub_branch.add_regenerative(
                                                                    shade_samples,
                                                                    regenerative_branch_chance,
                                                                    regenerative_branch_chance_light_required,
                                                                    internode_length,
                                                                    branch_angle, branching, twist,
                                                                    plagiotropism_buds, bvh, samples)

            else:
                if self.skip:
                    continue

                if random() < regenerative_branch_chance:
                    shade = 0.0
                    pos = node.pos
                    for ray in samples:
                        if cast(pos, ray)[0]:
                            shade += 1

                    shade /= shade_samples
                    light = 1.0 - shade

                    if light > regenerative_branch_chance_light_required:
                        node.dead = False
                        branch_dir = deviate(branch_angle, branching, twist, self.initial_phyllotaxic_angle,
                                             plagiotropism_buds, 0.0, node.direction, i, 0)
                        branch_dir.normalize()
                        branch_dir *= internode_length
                        sub_branch = Branch(branch_dir)
                        sub_branch.power = 1.0
                        sub_branch.shade = self.shade
                        sub_branch.initial_phyllotaxic_angle = random() * 6.2832
                        sub_branch.nodes[0].pos = node.pos
                        sub_branch.is_regenerative = True
                        sub_branch.skip = self.skip
                        node.sub_branches.append(sub_branch)
                        number_of_regenerative_branches += 1

        return number_of_regenerative_branches

    def calculate_shade(self, shade_samples, shade_sensitivity, bvh, samples):

        for node in self.nodes:
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if not sub_branch.dead:
                        sub_branch.calculate_shade(shade_samples, shade_sensitivity, bvh, samples)
                    else:
                        sub_branch.shade = 1.0

        pos = self.nodes[-1].pos.copy()
        pos.z += 0.01

        shade = shade_samples
        light_direction = Vector((0.0, 0.0, 0.0))

        cast = bvh.ray_cast
        for ray in samples:
            if not cast(pos, ray)[0]:
                shade -= 1
                light_direction += ray

        number_of_bright_spots = shade_samples - shade
        shade /= shade_samples

        self.shade = pow(shade, shade_sensitivity)

        self.phototropism_direction = light_direction
        if number_of_bright_spots > 0:
            self.phototropism_direction /= number_of_bright_spots

    def die(self, start_node=0):

        if start_node > 0:
            self.nodes[-1].dead = True
            for node in self.nodes[start_node:]:
                for sub_branch in node.sub_branches:
                    sub_branch.die()
        else:
            self.dead = True
            for node in self.nodes:
                if node.sub_branches:
                    for sub_branch in node.sub_branches:
                        sub_branch.die()

    def drop(self, drop_relatively_weak, drop_dead_exponent, apical_bud_fatality, flower_power, drop_shaded_threshold):

        count_dropped = 0
        count_dead_ends = 0
        has_sub_branch = False

        for i, node in enumerate(self.nodes):
            if node.sub_branches:
                has_sub_branch = True
                for sub_branch in node.sub_branches:
                        if sub_branch.dead:
                            length = len(sub_branch.nodes)

                            rand = random()**drop_dead_exponent * (length - 1)
                            rand = int(rand) + 1
                            if rand < 2:
                                sub_branch.marked_to_drop = True
                            elif rand < length - 1:
                                sub_branch.nodes[rand-1].dead_thickness = sub_branch.nodes[rand-1].radius * 2.0
                                sub_branch.nodes = sub_branch.nodes[0:rand]

                        else:
                            if sub_branch.nodes[0].radius == 0.0:
                                sub_branch.die()
                            else:
                                sub_health = sub_branch.nodes[0].photosynthesis / (3.1415 * pow(sub_branch.nodes[0].radius, 2))
                                total_health = node.photosynthesis / (3.1415 * pow(node.radius, 2))
                                sub_health = (3.1415 * pow(sub_branch.nodes[0].radius, 2))
                                total_health = (3.1415 * pow(node.radius, 2))
                                sub_health = sub_branch.nodes[0].photosynthesis + 0.0000001
                                total_health = node.photosynthesis + 0.0000001

                                if sub_health / total_health < drop_relatively_weak:
                                    sub_branch.die()
                                else:
                                    if i != len(self.nodes) - 1:
                                        ongoing_health = self.nodes[i + 1].photosynthesis / (3.1415 * pow(self.nodes[i + 1].radius, 2))
                                        ongoing_health = (3.1415 * pow(self.nodes[i + 1].radius, 2))
                                        ongoing_health = self.nodes[i + 1].photosynthesis + 0.0000001
                                        if ongoing_health / total_health < drop_relatively_weak:
                                            self.die(start_node=i + 1)

                            counts = sub_branch.drop(drop_relatively_weak, drop_dead_exponent, apical_bud_fatality,
                                                     flower_power, drop_shaded_threshold)
                            count_dropped += counts[0]
                            count_dead_ends += counts[1]

                for sub_branch in node.sub_branches:
                    if sub_branch.skip:
                        continue

                    if sub_branch.marked_to_drop:
                        if len(node.sub_branches) == 1:
                            node.dead_thickness += sub_branch.nodes[0].radius * 2.0
                        node.sub_branches.remove(sub_branch)
                        node.dead = True
                        count_dropped += 1

        if self.power < flower_power:
            count_dead_ends += 1
            self.nodes[-1].dead = True

        if self.shade > drop_shaded_threshold:
            if random() < apical_bud_fatality:
                self.nodes[-1].dead = True
            if not has_sub_branch:
                self.die()

        return count_dropped, count_dead_ends

    def drop_low(self, trim_height, keep_thick):

        last_node = len(self.nodes)-1
        
        for i, node in enumerate(self.nodes):
            if node.sub_branches:
                if not self.nodes[-1].dead:
                    node.sub_branches = [branch for branch in node.sub_branches
                                         if branch.nodes[0].pos.z > trim_height
                                         or ((branch.nodes[0].radius * 2.0) > keep_thick)]

                for sub_branch in node.sub_branches:
                    sub_branch.drop_low(trim_height, keep_thick)

            if i != last_node:
                if self.nodes[i + 1].pos.z < trim_height and self.nodes[i].pos.z >= trim_height:
                    if not self.is_trunk:
                        del self.nodes[i + 1:]
                        self.nodes[i].dead = True
                        return

                if self.nodes[0].pos.z < trim_height and ((self.nodes[0].radius * 2.0) > keep_thick):
                    if self.nodes[i + 1].pos.z < self.nodes[i].pos.z:
                        if not self.is_trunk:
                            del self.nodes[i + 1:]
                            self.nodes[i].dead = True
                            return

    def prune(self, bvh, shape):

        slice_index = -1

        for i, node in enumerate(self.nodes):

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    sub_branch.prune(bvh, shape)

            node.sub_branches = [branch for branch in node.sub_branches if len(branch.nodes) > 1]

            if i == len(self.nodes)-1:
                break

            if self.is_trunk and i < 3:
                continue

            ray = self.nodes[i + 1].pos - node.pos
            if bvh.ray_cast(node.pos, ray, ray.length)[0]:
                slice_index = i + 1
                self.nodes[i].dead = False

                if not shape:
                    self.nodes[i].dead_thickness = self.nodes[i].radius * 2.0
                    self.nodes[i].dead = True
                break

        if slice_index != -1:
            del self.nodes[slice_index:]

    def lateral_takeover(self):

        if self.nodes[-1].dead:
            do = False
            skip_thicker = False
            i = 0
            thickest_sub_branch = 0

            for j in reversed(range(len(self.nodes))):
                node = self.nodes[j]
                if node.sub_branches:
                    thickest_sub_branch = node.sub_branches[0]
                    if len(node.sub_branches) > 1:
                        for sub_branch in node.sub_branches[1:]:
                            if thickest_sub_branch.dead:
                                thickest_sub_branch = sub_branch
                                continue
                            if sub_branch.nodes[0].thickness > thickest_sub_branch.nodes[0].thickness:
                                if len(sub_branch.nodes) > 1:
                                    thickest_sub_branch = sub_branch

                    if len(thickest_sub_branch.nodes) < 2:
                        continue

                    if thickest_sub_branch.dead:
                        continue

                    if node.radius < 0.01 or thickest_sub_branch.nodes[0].thickness > 0.5 * node.thickness:
                        do = True
                        i = j
                    else:
                        skip_thicker = True

                    break

            if do:
                self.nodes[i].sub_branches.remove(thickest_sub_branch)
                new_lead_branch_nodes = self.nodes[:i] + [deepcopy(self.nodes[i])] + thickest_sub_branch.nodes[1:]
                new_lead_branch_nodes[i].direction = thickest_sub_branch.nodes[0].direction

                old_branch_end = Branch(Vector((0.0, 0.0, 0.0)))
                old_branch_end.nodes = self.nodes[i:]
                old_branch_end.nodes[0].sub_branches = []
                old_branch_end.die()

                old_branch_end_tip_thickness = copy(self.tip_thickness)
                self.tip_thickness = thickest_sub_branch.tip_thickness
                old_branch_end.tip_thickness = old_branch_end_tip_thickness

                self.nodes = new_lead_branch_nodes
                self.nodes[i].sub_branches.append(old_branch_end)
            else:
                if not skip_thicker:
                    if not self.is_trunk:
                        self.die()

        do = False
        i = 0
        thickest_sub_branch = 0

        last_node = len(self.nodes) - 1
        for j in range(len(self.nodes)):
            node = self.nodes[j]
            if node.sub_branches:
                thickest_sub_branch = node.sub_branches[0]
                if len(node.sub_branches) > 1:
                    for sub_branch in node.sub_branches[1:]:
                        if sub_branch.nodes[0].thickness > thickest_sub_branch.nodes[0].thickness:
                            thickest_sub_branch = sub_branch

                if j != last_node:
                    if (thickest_sub_branch.nodes[0].radius * 2.0) > (self.nodes[j + 1].radius * 2.0 + 0.002):
                        if not thickest_sub_branch.dead:
                            do = True
                            i = j
                            break

        if do:
            old_branch_end = deepcopy(thickest_sub_branch)
            self.nodes[i].sub_branches.remove(thickest_sub_branch)
            new_lead_branch_nodes = self.nodes[:i] + [deepcopy(self.nodes[i])] + thickest_sub_branch.nodes[1:]
            new_lead_branch_nodes[i].direction = thickest_sub_branch.nodes[0].direction

            old_branch_end.nodes = self.nodes[i:]
            old_branch_end.nodes[0].sub_branches = []
            old_branch_end.nodes[-1].dead_thickness = self.nodes[-1].radius * 2.0

            old_branch_end_tip_thickness = copy(self.tip_thickness)
            self.tip_thickness = thickest_sub_branch.tip_thickness
            old_branch_end.tip_thickness = old_branch_end_tip_thickness

            self.nodes = new_lead_branch_nodes
            self.nodes[i].sub_branches.append(old_branch_end)

        for node in self.nodes:
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if not sub_branch.dead:
                        sub_branch.lateral_takeover()

    def flow_bright(self, favor_current, shade_avoidance, favor_healthy, internode_length,
                    favor_current_reach, peak_height, juice, equal_power, generation,
                    branching_inefficiency):

        self.juice = juice * 1.0

        for i, node in enumerate(self.nodes):

            if node.sub_branches:
                for j, sub_branch in enumerate(node.sub_branches):
                    if sub_branch.dead:
                        sub_branch.power = 0.0
                        continue

                    sub_juice = 1.0 - sub_branch.shade
                    self.juice -= sub_juice

                    sub_branch.flow_bright(favor_current, shade_avoidance, favor_healthy, internode_length,
                                           favor_current_reach, peak_height, sub_juice, equal_power,
                                           generation + 1, branching_inefficiency)

        self.power = self.juice
        self.power = 1.0 - self.shade

        light = 1.0 - self.shade
        self.power = (favor_healthy * light + (1.0 - favor_healthy) * equal_power)
        squeeze = pow((1.0 - branching_inefficiency), generation)
        self.power *= squeeze

    def flow_exaggerate(self, favor_current, shade_avoidance, favor_healthy, internode_length,
                        favor_current_reach, peak_height, juice):

        self.juice = juice * 1.0

        last_node_index = len(self.nodes) - 1

        for i, node in enumerate(self.nodes):
            if node.sub_branches:
                Qt = 0.0
                if i == last_node_index:
                    Qm = self.nodes[i].photosynthesis * 1.0
                    for sub_branch in node.sub_branches:
                        Qm -= sub_branch.nodes[0].photosynthesis
                else:
                    Qm = self.nodes[i + 1].photosynthesis * 1.0

                Qt += Qm
                Qls = []
                for sub_branch in node.sub_branches:
                    Qls.append(sub_branch.nodes[0].photosynthesis)
                    Qt += sub_branch.nodes[0].photosynthesis

                Qtnew = 0.0
                if Qm < 0.0:
                    print('Qm lower than 0.0, why does this happen?! For now, set to 0.0 to prevent complex numbers!')
                    Qm = 0.0
                Qm = pow(Qm, favor_healthy)
                Qtnew += Qm
                for k in range(len(Qls)):
                    Qls[k] = pow(Qls[k], favor_healthy)
                    Qtnew += Qls[k]

                if Qtnew != 0.0:
                    Qm *= (Qt / Qtnew)
                    for k in range(len(Qls)):
                        Qls[k] *= (Qt / Qtnew)

                for j, sub_branch in enumerate(node.sub_branches):
                    if sub_branch.dead:
                        sub_branch.power = 0.0
                        continue

                    if Qt == 0.0:
                        sub_juice = 0.0
                    else:
                        sub_juice = (Qls[j] / Qt) * self.juice

                    distance = (len(self.nodes) - i) * internode_length
                    if distance > favor_current_reach:
                        current_favor_current = 0.0
                    else:
                        current_favor_current = favor_current
                    sub_juice *= (1.0 - current_favor_current)

                    sub_branch.juice = sub_juice

                    sub_branch.flow_exaggerate(favor_current, shade_avoidance, favor_healthy, internode_length,
                                               favor_current_reach, peak_height, sub_juice)

                if Qt == 0.0:
                    self.juice = 0.0
                else:
                    self.juice = (Qm / Qt) * self.juice

        self.power = self.juice * 1.0

    def add_side_branches(self, grow_nodes, bud_life, branch_chance, branch_chance_only_terminal, internode_length,
                          favor_current_reach, favor_current, shade_avoidance, branch_angle, branching, twist,
                          plagiotropism_buds, do_environment_block, environment,
                          branch_chance_light_required, tip_thickness, gravitropism_buds, gravitropism_buds_randomness):

        for node in self.nodes:
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if not sub_branch.dead:
                        sub_branch.add_side_branches(grow_nodes, bud_life, branch_chance, branch_chance_only_terminal,
                                                     internode_length, favor_current_reach, favor_current,
                                                     shade_avoidance, branch_angle, branching, twist,
                                                     plagiotropism_buds, do_environment_block,
                                                     environment, branch_chance_light_required, tip_thickness,
                                                     gravitropism_buds, gravitropism_buds_randomness)

        if self.skip:
            return

        random_num = random
        number_of_nodes = len(self.nodes)

        young_wood = number_of_nodes - 1 - (grow_nodes * bud_life)

        if young_wood < 1:
            young_wood = 1
        branch_chance = branch_chance

        for i, node in enumerate(self.nodes):
            if i != number_of_nodes - 1 and random_num() < branch_chance_only_terminal:
                continue

            if i < young_wood:
                continue

            if random_num() > branch_chance or node.sub_branches:
                continue

            if node.dead:
                continue

            distance = (number_of_nodes - 1 - i) * internode_length
            if distance > favor_current_reach:
                power = self.power * 1.0
            else:
                power = self.power * (1.0 - favor_current)

            if (1.0 - self.shade) < branch_chance_light_required:
                continue

            if i != number_of_nodes - 1:
                direction = self.nodes[i + 1].pos - self.nodes[i].pos
            else:
                direction = self.nodes[i].pos - self.nodes[i - 1].pos
            diff = node.direction.rotation_difference(direction)

            current_branching = branching
            current_branching = int(branching * min(1.0, self.power))
            if branching > 1 and current_branching < 2:
                current_branching = 2
            elif branching == 1 and current_branching == 0:
                current_branching = 1

            for j in range(current_branching):
                sub_branch_dir = deviate(branch_angle, current_branching, twist, self.initial_phyllotaxic_angle,
                                         plagiotropism_buds, gravitropism_buds + gravitropism_buds_randomness * (0.5 - random()), direction, i, j)
                sub_branch_dir.normalize()
                sub_branch_dir *= internode_length

                if do_environment_block:
                    ray = (node.pos + sub_branch_dir * 4.0) - node.pos
                    if environment.ray_cast(node.pos, ray, ray.length)[0]:
                        if current_branching == 1:
                            node.dead = True
                        continue

                sub_branch_dir = diff.conjugated() @ sub_branch_dir
                sub_branch = Branch(sub_branch_dir)

                sub_branch.power = power
                sub_branch.shade = self.shade
                sub_branch.initial_phyllotaxic_angle = random() * 6.2832
                sub_branch.nodes[0].pos = node.pos
                sub_branch.tip_thickness = tip_thickness

                node.sub_branches.append(sub_branch)

                node.sub_branches[-1].skip = self.skip

    def mark(self, bvh, parent_skip):

        if not parent_skip:
            self.skip = False
            for node in self.nodes:
                if node.sub_branches:
                    for sub_branch in node.sub_branches:
                        sub_branch.mark(bvh, self.skip)

        else:
            self.skip = True
            for i, node in enumerate(self.nodes[:-1]):
                ray = self.nodes[i + 1].pos - node.pos
                if bvh.ray_cast(node.pos, ray, ray.length)[0]:
                    self.skip = False

                if node.sub_branches:
                    for sub_branch in node.sub_branches:
                        sub_branch.mark(bvh, self.skip)

    def unmark(self):

        self.skip = False
        for node in self.nodes:
            for sub_branch in node.sub_branches:
                sub_branch.unmark()

    def grow(self, grow_nodes, internode_length, shade_elongation, random_heading, random_pitch,
             gravitropism, gravitropism_shade, plagiotropism, phototropism, do_environment, do_environment_block,
             force, force_radius, force_power, environment, tip_thickness, tip_decrease,
             grow_exponent, favor_rising,
             vector_up=Vector((0.0, 0.0, 1.0)), half_pi=0.5 * pi):

        start_number_of_nodes = len(self.nodes)

        for node in self.nodes:
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if not sub_branch.dead:
                        sub_branch.grow(grow_nodes, internode_length, shade_elongation,
                                        random_heading, random_pitch, gravitropism, gravitropism_shade,
                                        plagiotropism, phototropism, do_environment, do_environment_block,
                                        force, force_radius, force_power, environment,
                                        tip_thickness, tip_decrease, grow_exponent, favor_rising)

        if self.nodes[-1].dead:
            return

        if self.skip:
            return

        current_gravitropism = (1.0 - self.shade) * gravitropism + self.shade * gravitropism_shade
        current_gravitropism /= 10.0

        if self.is_regenerative:
            current_gravitropism = gravitropism / 5.0

        phototropism_strength = phototropism * self.phototropism_direction.length * self.shade / grow_nodes

        power = self.power * 1.0

        if power > 1.0:
            power = 1.0

        direction = self.nodes[-1].direction.copy()
        if len(self.nodes) > 1:
            direction = self.nodes[-1].pos - self.nodes[-2].pos
        vector_up = Vector((0.0, 0.0, 1.0))
        squeeze = vector_up.angle(direction, 0.0) / 3.1415
        squeeze *= favor_rising
        power *= (1.0 - squeeze)

        max_power = 1.0
        if power > max_power:
            power = max_power
        new_nodes = int(power * grow_nodes)
        if (power * grow_nodes) % 1 > 0.3:
            new_nodes += 1
        new_internode_length = 0.0
        if new_nodes != 0:
            grow_length = internode_length * grow_nodes
            new_internode_length = (power * grow_length) / new_nodes

        for i in range(new_nodes):
            direction = self.nodes[-1].direction.copy()
            if len(self.nodes) > 1:
                direction = self.nodes[-1].pos - self.nodes[-2].pos
            diff = self.nodes[-1].direction.rotation_difference(direction)

            flat_dir = direction.copy()
            flat_dir.z = 0.0

            horizontal = 1.0 - (abs(direction.angle(flat_dir, 0.0)) / half_pi)
            horizontal = pow(abs(horizontal), 2.0 * 0.8)
            random_heading_angle = horizontal * (1.0 - random() * 2) * random_heading
            multiplier = (1.0 - power)
            if multiplier < 0.0:
                multiplier = 0.0
            multiplier = pow(multiplier, 0.1)

            direction = Quaternion(vector_up, random_heading_angle) @ direction

            axis_pitch = Quaternion(vector_up, half_pi) @ flat_dir
            if flat_dir.x < 0.01 and flat_dir.y < 0.01:
                axis_pitch = Quaternion(vector_up, 6.28 * random()) @ axis_pitch
            random_pitch_angle = (1.0 - random() * 2) * random_pitch
            random_pitch_angle /= (power + 0.00001)

            direction = Quaternion(axis_pitch, random_pitch_angle) @ direction

            if current_gravitropism < 0.0:
                if Vector((0.0, 0.0, -1.0)).angle(direction, 0.0) > 0.01:
                    direction = direction.slerp(vector_up, -current_gravitropism)
                else:
                    direction = direction.lerp(vector_up, -current_gravitropism)

            else:
                if vector_up.angle(direction, 0.0) > 0.01:
                    direction = direction.slerp(Vector((0.0, 0.0, -1.0)), current_gravitropism)
                else:
                    direction = direction.lerp(Vector((0.0, 0.0, -1.0)), current_gravitropism)

            if plagiotropism > 0.0 and (abs(direction.x) + abs(direction.y)) > 0.0001:
                current_plagiotropism = plagiotropism * pow(self.shade, 0.5)

                plagio_dir = direction.copy()
                plagio_dir.z = 0.0
                direction = direction.slerp(plagio_dir, current_plagiotropism)

            direction.normalize()
            direction *= new_internode_length
            if phototropism_strength != 0.0:
                direction = direction.lerp(self.phototropism_direction.normalized() * new_internode_length, phototropism_strength)

            direction.normalize()
            direction *= new_internode_length
            if self.is_regenerative:
                direction *= 1.5

            direction *= 1.0 + shade_elongation * self.shade

            if do_environment:
                if force in ["2", "3", "4", "5"]:
                    point = environment.find_nearest(self.nodes[-1].pos)[0]

                    if point:
                        force_vec = point - self.nodes[-1].pos
                        force_strength = 1.0 - (force_vec.length / force_radius)

                        if force in ["2", "3"]:
                            force_vec = -force_vec

                        if force_strength > 0.0 and len(self.nodes) > 2 and force_vec.length > 0.1:
                            force_vec = force_vec.normalized() * new_internode_length
                            direction = direction.lerp(force_vec, force_strength * force_power)

                do_environment_cling = False
                if do_environment_block:
                    last_pos = self.nodes[-1].pos
                    ray = (last_pos + direction) - last_pos
                    ray = direction
                    if environment.ray_cast(last_pos, ray, ray.length)[0]:
                        if do_environment_cling:
                            nearest = environment.find_nearest(last_pos + direction)[0]
                            direction = (nearest - last_pos) * 0.95

                        else:
                            continue

            direction = diff.conjugated() @ direction
            self.nodes.append(Node(direction))
            self.nodes[-1].pos = self.nodes[-2].pos + direction

            self.tip_thickness = tip_thickness * 1.0
            if power < 1.0:
                max_decrease = (1.0 - power) * tip_thickness
                self.tip_thickness -= tip_decrease * max_decrease

        if self.is_regenerative:
            self.is_regenerative = False

    def photosynthesize(self, favor_current, leaf_area, photo_range):
        number_of_nodes = len(self.nodes)

        for i in reversed(range(number_of_nodes)):
            node = self.nodes[i]

            if i == number_of_nodes - 1:
                node.node_weight = 0
                node.photosynthesis = (1.0 - self.shade)
                if self.dead:
                    node.photosynthesis = 0.0
                node.phloem = 0.000001
                node.xylem = 0.0
                node.auxin = 1.0 - self.shade
                if node.dead:
                    node.auxin = 0.0
            else:
                next_node = self.nodes[i + 1]
                node.node_weight = 1 + next_node.node_weight
                node.photosynthesis = next_node.photosynthesis

                node.phloem = next_node.phloem + 2 * pi * node.radius * node.direction.length
                node.xylem = next_node.xylem + pi * pow(node.radius, 2) * node.direction.length
                node.auxin = next_node.auxin * favor_current

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if not sub_branch.dead:
                        l, w, p, x, a = sub_branch.photosynthesize(favor_current, leaf_area, photo_range)
                        node.photosynthesis += l
                        node.node_weight += w
                        node.phloem += p
                        node.xylem += x
                        node.auxin += a

        return self.nodes[0].photosynthesis, self.nodes[0].node_weight, self.nodes[0].phloem, self.nodes[0].xylem, self.nodes[0].auxin

    def weigh(self, leaf_weight, lateral_twig_chance, lateral_twig_limit, branch_weight, rand=0.0, wind_vector=Vector((1.0, 0.0, 0.0))):

        number_of_nodes = len(self.nodes)

        for i in reversed(range(number_of_nodes)):
            node = self.nodes[i]

            if i == number_of_nodes - 1:
                node.real_weight = leaf_weight / 500000
                node.leaf_weight = leaf_weight / 500000
                if rand > 0.0:
                    node.real_weight += (1.0 - (random() * 2)) * rand / 200000
                self.wind_area = 0.0
            else:
                node.real_weight = node.direction.length * pi * pow(node.radius, 2)
                node.real_weight *= branch_weight / 100
                if rand > 0.0:
                    node.real_weight += (1.0-(random() * 2)) * rand / 200000
                node.real_weight += self.nodes[i + 1].real_weight
                node.leaf_weight = self.nodes[i + 1].leaf_weight

                angle = wind_vector.angle(Vector((0.0, 1.0, 0.0)))
                dir_to_wind = Quaternion(Vector((0.0, 0.0, 1.0)), -angle) @ node.direction
                dir_to_wind.x = 0.0
                length = dir_to_wind.length

                self.wind_area = self.nodes[i + 1].wind_area + (2.0 * node.radius * length)

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if not sub_branch.dead:
                        rw, lw, wa = sub_branch.weigh(leaf_weight, lateral_twig_chance, lateral_twig_limit, branch_weight, rand)
                        node.real_weight += rw
                        node.leaf_weight += lw
                        node.wind_area += wa

        return self.nodes[0].real_weight, self.nodes[0].leaf_weight, self.wind_area

    def bend(self, pos, parent_diff_quaternion, fatigue, quarter_pi=0.7854, vec_back=Vector((0.0, 1.0, 0.0)),
             wind_force=0.0, wind_vector=Vector((1.0, 0.0, 0.0))):

        current_pos = pos * 1.0
        parent_node_dif_quaternion = parent_diff_quaternion.copy()

        gravity_vector = Vector((0.0, 0.0, -1.0))

        for i, node in enumerate(self.nodes):
            node.pos = current_pos * 1.0

            bent_direction = parent_node_dif_quaternion @ node.direction

            I = quarter_pi * node.radius ** 4
            if I == 0.0:
                I = 0.001
            E = 10.0

            axis = bent_direction.copy().cross(gravity_vector)

            flat_bent_direction = bent_direction.copy()
            flat_bent_direction.z = 0.0
            arm = flat_bent_direction.length

            weight = node.real_weight - (node.baked_weight * (1.0 - fatigue))
            if weight < 0.0:
                weight = 0.0

            deflection = weight * arm ** 3 / (3 * E * I)

            v = Quaternion(axis, deflection) @ bent_direction
            v = v.normalized() * node.direction.length

            if wind_force != 0.0:
                for iteration in range(1):
                    fluctuation = (1.0 - 2.0 * random()) * 0.3 * pi
                    randomized_wind_vector = Quaternion(Vector((0.0, 0.0, 1.0)), fluctuation) @ wind_vector
                    axis = v.copy().cross(randomized_wind_vector)

                    flat_bent_direction1 = v.copy()
                    flat_bent_direction1.x = 0.0
                    arm = flat_bent_direction1.length

                    angle = wind_vector.angle(Vector((0.0, 1.0, 0.0)))
                    dir_to_wind = Quaternion(Vector((0.0, 0.0, 1.0)), -angle) @ v
                    dir_to_wind.x = 0.0
                    arm = dir_to_wind.length

                    weight = node.real_weight - (node.baked_weight * (1.0 - fatigue))
                    weight += wind_force * (1/50000)

                    weight *= wind_force

                    area = 2 * node.radius * arm

                    weight = area * wind_force / 200.0
                    weight += node.leaf_weight * wind_force

                    I = quarter_pi * node.radius ** 3
                    if I == 0.0:
                        I = 0.000001
                        print('Encounter!')
                        print(node.radius)

                    weight *= 50.0

                    deflection = weight * arm ** 3 / (3 * E * I)

                    v = Quaternion(axis, deflection) @ v
                    v = v.normalized() * node.direction.length

            parent_node_dif_quaternion = -node.direction.rotation_difference(v)

            if len(node.sub_branches):
                for sub_branch in node.sub_branches:
                    bla = wind_force * 1.0
                    if wind_force > 0.0:
                        sub_branch.bend(current_pos, parent_node_dif_quaternion, fatigue,
                                        wind_force=bla, wind_vector=wind_vector)
                    else:
                        sub_branch.bend(current_pos, parent_node_dif_quaternion, fatigue)

            current_pos += v

    def bake_bend(self, bake_bend):

        for i, node in enumerate(self.nodes):
            if i < len(self.nodes) - 1:
                node.direction = bake_bend * (self.nodes[i + 1].pos - node.pos) + (1.0 - bake_bend) * node.direction
                added_baked_weight = (node.real_weight - node.baked_weight) * bake_bend
                if added_baked_weight > 0.0:
                    node.baked_weight += added_baked_weight

            else:
                if len(self.nodes) != 1:
                    node.direction = bake_bend * (node.pos - self.nodes[i - 1].pos) + (1.0 - bake_bend) * node.direction

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    sub_branch.bake_bend(bake_bend)

    def thicken(self, e, internode_gain, tip_decrease):

        last_node_index = len(self.nodes) - 1

        for i, node in reversed(list(enumerate(self.nodes))):
            if i == last_node_index:
                node.thickness = self.tip_thickness
            else:
                node.thickness = self.nodes[i + 1].thickness + internode_gain

            sub_thickness = 0.0
            thickest_sub_thickness = 0.0

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if len(sub_branch.nodes) < 2:
                        continue
                    sub_branch.thicken(e, internode_gain, tip_decrease)

                    sub_thickness = sub_branch.nodes[0].thickness

                    if sub_thickness > 0.0:
                        a = pow(node.thickness, e)
                        b = pow(sub_thickness, e)
                        node.thickness = pow(a + b, 1 / e)

                    if sub_thickness > thickest_sub_thickness:
                        thickest_sub_thickness = sub_thickness

            if node.dead_thickness > thickest_sub_thickness:
                sub_thickness = node.dead_thickness

                a = pow(node.thickness, e)
                b = pow(sub_thickness, e)
                node.thickness = pow(a + b, 1 / e)

            node.radius = node.thickness / 2

    def make_data_relative_to_root(self, root_thickness, root_photosynthesis):

        for node in self.nodes:
            node.thickness /= root_thickness
            node.photosynthesis /= (root_photosynthesis + 0.0000001)
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    sub_branch.make_data_relative_to_root(root_thickness, root_photosynthesis)

    def smooth_kinks(self, threshold_angle):

        for i, node in enumerate(self.nodes):
            if i == 0:
                continue

            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    sub_branch.smooth_kinks(threshold_angle)
            else:
                previous_dir = self.nodes[i - 1].direction * 1.0
                node_direction = node.direction
                ang = previous_dir.angle(node_direction, 0.0)

                if ang > threshold_angle:
                    endpoint = previous_dir + node_direction
                    straight_midpoint = endpoint / 2.0
                    new_midpoint = (previous_dir + straight_midpoint) / 2.0
                    self.nodes[i - 1].direction = new_midpoint
                    node.direction = endpoint - new_midpoint

    def build_branches_mesh(self, build_type,
                            profile_resolution, profile_resolution_reduction, twist, u_repeat, texture_aspect_ratio,
                            root_distribution, root_shape, root_scale, root_bump, base_weight,
                            parent_previous_node, parent_node, parent_next_node, v, verts, faces, uvs, shape,
                            layers, origin, circles, shape_key_pass,
                            threshold, branch_angle, branching, plagiotropism_buds, wind_force,
                            vector_zero=Vector((0.0, 0.0, 0.0)),
                            vector_z=Vector((0.0, 0.0, 1.0)),
                            vector_y=Vector((0.0, 1.0, 0.0)),
                            twopi=6.2832):

        prevaxis = None

        res = profile_resolution * self.nodes[0].thickness
        res = profile_resolution_reduction * res + (1.0 - profile_resolution_reduction) * profile_resolution
        res = max(3, int(res))
        prev_res = res

        uv_offset_x = self.uv_offset_x
        uv_offset_y = self.uv_offset_y

        nodes = []
        if parent_previous_node:
            node = Node(parent_previous_node.direction)
            node.pos = (parent_previous_node.pos + self.nodes[0].pos) / 2.0
            node.node_weight = parent_previous_node.node_weight
            node.real_weight = parent_previous_node.real_weight
            node.radius = parent_node.radius * 0.95
            node.thickness = node.radius * 2.0
            node.thickness = parent_previous_node.thickness
            node.photosynthesis = parent_previous_node.photosynthesis
            nodes.append(node)

            if parent_node.radius * 2.0 < (self.nodes[1].pos-self.nodes[0].pos).length:
                node2 = Node(vector_zero)
                posa = node.pos + (self.nodes[1].pos - node.pos) / 2
                posb = posa + (self.nodes[0].pos - posa) / 2
                node2.pos = posb
                node2.thickness = parent_previous_node.thickness * 0.87
                node2.thickness = parent_previous_node.thickness
                node2.radius = parent_previous_node.radius * 2.87
                node2.radius = (parent_previous_node.radius + self.nodes[0].radius) / 2.0
                node2.thickness = node2.radius * 2.0
                node2.thickness = parent_previous_node.thickness

                if self.nodes[1].radius / parent_node.radius < 0.5:
                    node2.radius = self.nodes[1].radius
                    node2.thickness = node2.radius * 2.0
                    node2.thickness = parent_previous_node.thickness

                node2.photosynthesis = parent_previous_node.photosynthesis
                node2.node_weight = parent_previous_node.node_weight
                node2.real_weight = parent_previous_node.real_weight
                nodes.append(node2)

                if len(self.nodes) > 1:
                    node3 = Node(vector_zero)
                    node3.pos = self.nodes[0].pos + (self.nodes[1].pos - self.nodes[0].pos) / 2
                    node3.node_weight = self.nodes[1].node_weight
                    node3.real_weight = self.nodes[1].real_weight
                    node3.thickness = self.nodes[0].thickness
                    node3.radius = self.nodes[0].radius
                    node3.photosynthesis = self.nodes[0].photosynthesis
                    node3.thickness = parent_node.thickness
                    nodes.append(node3)

                nodes.extend(self.nodes[1:])
            else:
                nodes.extend(self.nodes[1:])

                ratio = nodes[1].radius / parent_node.radius
                nodes[0].pos = parent_previous_node.pos * ratio + (1.0 - ratio) * parent_node.pos
                ratio = pow(ratio, 0.5)
                nodes[0].radius = parent_node.radius * ratio + (1.0 - ratio) * nodes[1].radius

        else:
            first_node = self.nodes[0]
            if first_node.direction.x != 0.0 or first_node.direction.y != 0.0:
                root_node = Node(Vector((0.0, 0.0, 0.1)))
                root_node.pos = first_node.pos - Vector((0.0, 0.0, first_node.radius))
                root_node.thickness = first_node.thickness
                root_node.radius = first_node.radius
                nodes = [root_node] + self.nodes
            else:
                nodes = self.nodes

        number_of_nodes = len(nodes)
        circle = []
        previous_y = uv_offset_y
        current_y = uv_offset_y

        verts_append = verts.append
        verts_extend = verts.extend
        faces_append = faces.append
        uvs_extend = uvs.extend
        shape_extend = shape.extend

        do_layers = False
        if not shape_key_pass:
            do_layers = True

            layers_shade_extend = layers['layer_shade'].extend
            layers_thickness_extend = layers['layer_thickness'].extend
            layers_weight_extend = layers['layer_weight'].extend
            layers_power_extend = layers['layer_power'].extend
            layers_health_extend = layers['layer_health'].extend
            layers_dead_extend = layers['layer_dead'].extend
            layers_pitch_extend = layers['layer_pitch'].extend
            layers_apical_extend = layers['layer_apical'].extend
            layers_lateral_extend = layers['layer_lateral'].extend

            if base_weight == 0.0:
                base_weight = 0.0001

        last_node_index = len(nodes) - 1
        cur_twist = 0.0

        repeat = int(u_repeat * self.nodes[0].thickness)
        if repeat < 1:
            repeat = 1

        for j, n in enumerate(nodes):
            aspect = texture_aspect_ratio * repeat
            circumference = 2 * pi * n.radius

            pos_offset = n.pos - origin

            previous_y = current_y

            if j != 0:
                current_y += aspect / circumference * abs((n.pos - nodes[j - 1].pos).length)

            radius = n.radius

            if self.is_trunk:
                root_scale_reach = root_distribution * number_of_nodes
                if j < root_scale_reach:
                    x = 1.0 - (j / root_scale_reach)
                    y = pow(x, root_shape * 75.0)
                    multiplier = y * (root_scale - 1.0)
                    radius += radius * multiplier

                    amount = multiplier * 0.2 * root_bump * radius

            if j != last_node_index:
                direction = nodes[j + 1].pos - n.pos
                axis = direction.to_track_quat('X', 'Z') @ vector_y
                angle = vector_z.angle(direction, 0.0)

                if j != 0:
                    previous_direction = n.pos - nodes[j - 1].pos
                    previous_axis = previous_direction.to_track_quat('X', 'Z') @ vector_y
                    previous_angle = vector_z.angle(previous_direction, 3.14)

                    angle = (angle + previous_angle) / 2.0
                    axis = axis.lerp(previous_axis, 0.5)
                    axis.normalize()

            else:
                axis = (n.pos - nodes[j - 1].pos).to_track_quat('X', 'Z') @ Vector((1.0, twopi, 0.0))
                angle = vector_z.angle(n.pos - nodes[j - 1].pos, 0.0)

            if j != 0:
                if direction.z < 0.0:
                    down = cos(Vector((0.0, 0.0, -1.0)).angle(direction))
                    flip_angle = Vector((prevaxis.x, prevaxis.y)).angle_signed(Vector((axis.x, axis.y)), 0.0)
                    cur_twist -= down * flip_angle

            if j > 0:
                cur_twist += twist
            do_twist = cur_twist != 0.0

            cur_res = profile_resolution * n.thickness
            cur_res = profile_resolution_reduction * cur_res + (1.0 - profile_resolution_reduction) * profile_resolution

            cur_res = int(cur_res)
            if cur_res < 3:
                cur_res = 3

            if cur_res < prev_res - 1:
                cur_res = prev_res - 1
            if j < 3:
                cur_res = prev_res

            circle = circles[cur_res]

            for i in range(cur_res):

                a = (i - 1) / cur_res * repeat + uv_offset_x
                b = i / cur_res * repeat + uv_offset_x
                c = (1 / prev_res) * repeat

                if self.is_trunk:
                    curradius = radius + amount * (1.0 + 0.5 * sin(i * 6 / cur_res * twopi))
                    curradius += amount * (1.0 + 0.5 * cos(i * 9 / cur_res * twopi)) * 0.5
                else:
                    curradius = radius

                co = circle[i] * curradius
                if do_twist:
                    co = Quaternion(Vector((0.0, 0.0, 1.0)), cur_twist) @ co

                co = Quaternion(axis, angle) @ co
                co += pos_offset

                if shape_key_pass:
                    shape_extend(co)
                else:
                    verts_append(co)
                    v += 1

                    if j > 0 and i > 0:
                        offset = v - 1
                        faces_append((offset - 1 - cur_res,
                                      offset - cur_res,
                                      offset,
                                      offset - 1))

                        if prev_res == cur_res:
                            uvs_extend([(a, previous_y),
                                        (b, previous_y),
                                        (b, current_y),
                                        (a, current_y)])

                        elif prev_res == cur_res + 1:
                            uvs_extend([((i - 1) / prev_res * repeat + uv_offset_x + ((1 / prev_res) * repeat), previous_y),
                                        (i / prev_res * repeat + uv_offset_x + ((1 / prev_res) * repeat), previous_y),
                                        (i / cur_res * repeat + uv_offset_x, current_y),
                                        ((i - 1) / cur_res * repeat + uv_offset_x, current_y)])

            if j > 0 and not shape_key_pass:
                offset = v - 1 - i

                a = i / cur_res * repeat + uv_offset_x
                b = repeat + uv_offset_x
                c = (1 / prev_res) * repeat

                if prev_res == cur_res:
                    faces_append((offset - 1,
                                  offset - cur_res,
                                  offset,
                                  offset + cur_res - 1))

                    uvs_extend([(a, previous_y),
                                (b, previous_y),
                                (b, current_y),
                                (a, current_y)])

                elif prev_res == cur_res + 1:
                    faces_append((offset - cur_res - 1,
                                  offset - cur_res,
                                  offset,
                                  offset + cur_res - 1))

                    uvs_extend([(a + c, previous_y),
                                (b + c, previous_y),
                                (b, current_y),
                                (a, current_y)])

                    faces_append((offset - 1,
                                  offset - cur_res - 1,
                                  offset + cur_res - 1))

                    uvs_extend([(a, previous_y),
                                (b, previous_y),
                                (a, current_y)])

            if j == last_node_index:
                if shape_key_pass:
                    shape_extend(co)
                else:
                    verts_append(self.nodes[-1].pos - origin)
                    v += 1

                    for i in range(cur_res):
                        if i == cur_res - 1:
                            faces_append((v - 2,
                                          v - 2 - i,
                                          v - 1))

                            uvs_extend([(0.5 * circle[0].x + 0.5, 0.5 * circle[0].y + 0.5),
                                        (0.5 * circle[i].x + 0.5, 0.5 * circle[i].y + 0.5),
                                        (0.5, 0.5)])
                        else:
                            faces_append((v - 3 - i,
                                          v - 2 - i,
                                          v - 1))

                            uvs_extend([(0.5 * circle[i + 1].x + 0.5, 0.5 * circle[i + 1].y + 0.5),
                                        (0.5 * circle[i].x + 0.5, 0.5 * circle[i].y + 0.5),
                                        (0.5, 0.5)])

            if do_layers:
                if j == last_node_index:
                    number = cur_res + 1
                else:
                    number = cur_res

                layers_shade_extend([self.shade] * number)
                layers_thickness_extend([n.thickness] * number)
                layers_weight_extend([n.real_weight / base_weight] * number)
                layers_power_extend([self.power] * number)
                layers_health_extend([pow(n.photosynthesis, 0.2)] * number)
                if self.dead:
                    layers_dead_extend([1.0] * number)
                else:
                    layers_dead_extend([0.0] * number)
                layers_pitch_extend([1.0 - (angle / pi)] * number)
                layers_apical_extend([0.0] * number)
                layers_lateral_extend([0.0] * number)

            prev_res = cur_res

            prevaxis = axis.copy()

        if not self.dead:
            lateral_twig_chance = 1.0

            duplicator = [Vector((0.0, -0.001, -0.001)),
                          Vector((0.0, 0.001, -0.001)),
                          Vector((0.0, 0.000, 0.001))]

            last_node = self.nodes[-1]
            if not last_node.dead:
                direc = last_node.pos - self.nodes[-2].pos

                branch_mat = two_point_transform(vector_zero, direc)
                twig_matrix = Matrix.Translation(last_node.pos) @ branch_mat

                if shape_key_pass:
                    shape_extend(twig_matrix @ duplicator[0] - origin)
                    shape_extend(twig_matrix @ duplicator[1] - origin)
                    shape_extend(twig_matrix @ duplicator[2] - origin)
                else:
                    verts_extend(twig_matrix @ vert - origin for vert in duplicator)
                    v += 3

                    faces_append((v - 3, v - 2, v - 1))
                    uvs_extend([(0.5, 0.5),
                                (0.5, 0.5),
                                (0.5, 0.5)])
                    if do_layers:
                        number = 3
                        layers_shade_extend([self.shade] * number)
                        layers_thickness_extend([last_node.thickness] * number)
                        layers_weight_extend([last_node.real_weight / base_weight] * number)
                        layers_power_extend([self.power] * number)
                        layers_health_extend([pow(last_node.photosynthesis, 0.2)] * number)
                        if self.dead:
                            layers_dead_extend([1.0] * number)
                        else:
                            layers_dead_extend([0.0] * number)
                        angle = vector_z.angle(direc, 0.0)
                        layers_pitch_extend([1.0 - (angle / pi)] * number)
                        layers_apical_extend([1.0] * number)
                        layers_lateral_extend([0.0] * number)

            last_node_index = len(self.nodes) - 1
            for i, n in enumerate(self.nodes):
                if i == 0 or i == last_node_index or n.radius * 2.0 > threshold:
                    continue

                if len(n.sub_branches):
                    if len(n.sub_branches[0].nodes) > 2:
                        continue

                direction = self.nodes[i + 1].pos - n.pos

                current_branching = int(branching * min(1.0, self.power))
                if branching > 1 and current_branching < 2:
                    current_branching = 2
                elif branching == 1 and current_branching == 0:
                    current_branching = 1
                for b in range(current_branching):

                    if random() > lateral_twig_chance:
                        continue

                    sub_branch_dir = deviate(branch_angle, current_branching, twist, self.initial_phyllotaxic_angle,
                                             plagiotropism_buds, 0.0, direction, i, b)

                    branch_mat = two_point_transform(vector_zero, sub_branch_dir)
                    twig_matrix = Matrix.Translation(n.pos) @ branch_mat

                    if shape_key_pass:
                        shape_extend(twig_matrix @ duplicator[0] - origin)
                        shape_extend(twig_matrix @ duplicator[1] - origin)
                        shape_extend(twig_matrix @ duplicator[2] - origin)
                    else:
                        verts_extend(twig_matrix @ vert - origin for vert in duplicator)
                        v += 3

                        faces_append((v - 3, v - 2, v - 1))
                        uvs_extend([(0.5, 0.5),
                                    (0.5, 0.5),
                                    (0.5, 0.5)])

                        if do_layers:
                            number = 3
                            layers_shade_extend([self.shade] * number)
                            layers_thickness_extend([n.thickness] * number)
                            layers_weight_extend([n.real_weight / base_weight] * number)
                            layers_power_extend([self.power] * number)
                            layers_health_extend([pow(n.photosynthesis, 0.2)] * number)
                            if self.dead:
                                layers_dead_extend([1.0] * number)
                            else:
                                layers_dead_extend([0.0] * number)
                            angle = vector_z.angle(sub_branch_dir, 0.0)
                            layers_pitch_extend([1.0 - (angle / pi)] * number)
                            layers_apical_extend([0.0] * number)
                            layers_lateral_extend([1.0] * number)

        for i, node in enumerate(self.nodes):
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    if len(sub_branch.nodes) < 2:
                        continue

                    if i == 1 and i != len(self.nodes) - 1:
                        if len(self.nodes) == len(nodes):
                            previous_node, current_node, next_node = self.nodes[0], self.nodes[1], self.nodes[2]
                        else:
                            previous_node, current_node, next_node = nodes[2], nodes[3], nodes[4]
                    elif i < len(self.nodes) - 1:
                        previous_node, current_node, next_node = self.nodes[i - 1], self.nodes[i], self.nodes[i + 1]
                    else:
                        previous_node, current_node, next_node = self.nodes[i - 1], self.nodes[i], None

                    v = sub_branch.build_branches_mesh(build_type,
                                                       profile_resolution, profile_resolution_reduction,
                                                       twist, u_repeat, texture_aspect_ratio,
                                                       root_distribution, root_shape, root_scale, root_bump,
                                                       base_weight,
                                                       previous_node, current_node, next_node, v,
                                                       verts, faces, uvs, shape, layers,
                                                       origin, circles, shape_key_pass,
                                                       threshold, branch_angle, branching, plagiotropism_buds,
                                                       wind_force)

        return v

    def distribute_twigs(self, lateral_twig_limit, branch_angle, branching, twist, plagiotropism_buds,
                         lateral_twig_chance, apical_twigs, lateral_twigs, shade, skip_lateral_twigs,
                         random_heading, random_pitch,
                         vec_zero=Vector((0.0, 0.0, 0.0))):

        if self.dead:
            return

        number_of_nodes = len(self.nodes)

        if number_of_nodes > 1:
            apical_pos = self.nodes[-1].pos
            mat = two_point_transform(apical_pos, apical_pos + (apical_pos - self.nodes[-2].pos))
            apical_twigs.append(TwigInstance(mat, 1, apical_pos, (apical_pos - self.nodes[-2].pos)))

        for i, node in reversed(list(enumerate(self.nodes))):
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    sub_branch.distribute_twigs(lateral_twig_limit, branch_angle, branching, twist,
                                                plagiotropism_buds, lateral_twig_chance, apical_twigs,
                                                lateral_twigs, shade, skip_lateral_twigs, random_heading, random_pitch)
                continue

            if skip_lateral_twigs:
                continue

            if i == 0 or i == number_of_nodes - 1:
                continue

            if node.radius * 2.0 > lateral_twig_limit:
                continue

            direction = self.nodes[i + 1].pos - node.pos
            branch_dir = deviate(branch_angle, branching, twist, self.initial_phyllotaxic_angle,
                                 plagiotropism_buds, 0.0, direction, i, 0)

            for j in range(branching):

                if random() > lateral_twig_chance:
                    continue

                sub_branch_dir = deviate(branch_angle, branching, twist, self.initial_phyllotaxic_angle,
                                         plagiotropism_buds, 0.0, direction, i, j)

                if j == 1 and branching == 2:
                    normal = direction.normalized()
                    sub_branch_dir = -branch_dir - 2.0 * -branch_dir.dot(normal) * normal

                branch_mat = two_point_transform(vec_zero, sub_branch_dir)
                lateral_twigs.append(TwigInstance(Matrix.Translation(node.pos) @ branch_mat,
                                                  0, node.pos, sub_branch_dir))

    def find_highest_point(self, highest):

        for node in self.nodes:
            if node.pos.z > highest:
                highest = node.pos.z
            if node.sub_branches:
                for sub_branch in node.sub_branches:
                    sub_high = sub_branch.find_highest_point(highest)
                    if sub_high > highest:
                        highest = sub_high
        return highest
