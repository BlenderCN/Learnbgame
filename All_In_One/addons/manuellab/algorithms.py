#Manuel Bastioni Lab - Copyright (C) 2016 Manuel Bastioni
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import mathutils
import itertools
import random
import time
import logging

#import faulthandler
#faulthandler.enable()

def simple_path(input_path, max_len=50):
    """
    Return the last part of long paths
    """
    if len(input_path) > max_len:
        return("[Trunked].."+input_path[len(input_path)-max_len:])
    else:
        return input_path

def quick_dist(p_1, p_2):
    return ((p_1[0]-p_2[0])**2) + ((p_1[1]-p_2[1])**2) + ((p_1[2]-p_2[2])**2)

def full_dist(vert1, vert2, axis="ALL"):
    v1 = mathutils.Vector(vert1)
    v2 = mathutils.Vector(vert2)
    
    if axis not in ["X","Y","Z"]:        
        v3 = v1-v2
        return v3.length
    if axis == "X":        
        return abs(v1[0]-v2[0])
    if axis == "Y":        
        return abs(v1[1]-v2[1])
    if axis == "Z":        
        return abs(v1[2]-v2[2])


def length_of_strip(vertices_coords, indices, axis="ALL"):
    strip_length = 0
    for x in range(len(indices)-1):
        v1 = vertices_coords[indices[x]]
        v2 = vertices_coords[indices[x+1]]
        strip_length += full_dist(v1,v2, axis)
    return(strip_length)

def function_modifier_a(val_x):
    val_y = 0.0
    if val_x > 0.5:
        val_y = 2*val_x-1
    return val_y

def function_modifier_b(val_x):
    val_y = 0.0
    if val_x < 0.5:
        val_y = 1-2*val_x
    return val_y

def bounding_box(verts_coo, indices, roundness=4):

    val_x, val_y, val_z = [], [], []
    for idx in indices:
        val_x.append(verts_coo[idx][0])
        val_y.append(verts_coo[idx][1])
        val_z.append(verts_coo[idx][2])

    box_x = round(max(val_x)-min(val_x), roundness)
    box_y = round(max(val_y)-min(val_y), roundness)
    box_z = round(max(val_z)-min(val_z), roundness)

    return (box_x, box_y, box_z)

def load_bbox_data(filepath):
    bboxes = []
    database_file = open(filepath, "r")
    for line in database_file:
        bboxes.append(line.split())
    database_file.close()

    bbox_data_dict = {}
    for x_data in bboxes:
        idx = x_data[0]
        idx_x_max = int(x_data[1])
        idx_y_max = int(x_data[2])
        idx_z_max = int(x_data[3])
        idx_x_min = int(x_data[4])
        idx_y_min = int(x_data[5])
        idx_z_min = int(x_data[6])

        bbox_data_dict[idx] = [
            idx_x_max, idx_y_max,
            idx_z_max, idx_x_min,
            idx_y_min, idx_z_min]
    return bbox_data_dict

def smart_combo(prefix, morph_values):

    debug1 = False
    debug2 = False
    tags = []
    names = []
    weights = []
    max_morph_values = []

    #Compute the combinations and get the max values
    for v_data in morph_values:
        tags.append(["max", "min"])
        max_morph_values.append(max(v_data))
    for n_data in itertools.product(*tags):
        names.append(prefix+"_"+'-'.join(n_data))

    #Compute the weight of each combination
    for n_data in itertools.product(*morph_values):
        weights.append(sum(n_data))

    factor = max(max_morph_values)
    best_val = max(weights)
    toll = 1.5

    #Filter on bestval and calculate the normalize factor
    summ = 0.0
    for i in range(len(weights)):
        weights[i] = max(0, weights[i]-best_val/toll)
        summ += weights[i]

    #Normalize using summ
    if summ != 0:
        for i in range(len(weights)):
            weights[i] = factor*(weights[i]/summ)

    if debug1:
        print("BESTVAL = {0}".format(best_val))
        print("SUM = {0}".format(summ))
        print("AVERAGE = {0}".format(factor))
    if debug2:
        print("MORPHINGS:")
        for i in range(len(names)):
            if weights[i] != 0:
                print(names[i], weights[i])
    return (names, weights)

def is_excluded(property_name, excluded_properties):
    for excluded_property in excluded_properties:
        if excluded_property in property_name:
            return True
    return False


def generate_parameter(val, random_value, preserve_dna=False):

    if preserve_dna:
        if val > 0.5:
            if val > 0.8:
                new_value = 0.8 + 0.2*random.random()
            else:
                new_value = 0.5+random.random()*random_value
        else:
            if val < 0.2:
                new_value = 0.2*random.random()
            else:
                new_value = 0.5-random.random()*random_value
    else:
        if random.random() > 0.5:
            new_value = min(1.0, 0.5+random.random()*random_value)
        else:
            new_value = max(0.0, 0.5-random.random()*random_value)
    return new_value


def polygon_forma(blender_object, polyg):

    obj = blender_object
    form_factors = []
    for idx in range(len(polyg.vertices)):
        index_a = idx
        index_b = idx-1
        index_c = idx+1
        if index_c > len(polyg.vertices)-1:
            index_c = 0

        p_a = obj.data.vertices[polyg.vertices[index_a]].co
        p_b = obj.data.vertices[polyg.vertices[index_b]].co
        p_c = obj.data.vertices[polyg.vertices[index_c]].co

        v_1 = p_b-p_a
        v_2 = p_c-p_a

        v_1.normalize()
        v_2.normalize()

        factor = v_1.dot(v_2)
        form_factors.append(factor)
    return form_factors

def centroid(blender_obj, verts_index_list):
    obj = blender_obj
    n_verts = len(verts_index_list)
    x_tot = 0.0; y_tot = 0.0; z_tot = 0.0

    for idx in verts_index_list:
        vert = obj.data.vertices[idx]
        x_tot += vert.co[0]
        y_tot += vert.co[1]
        z_tot += vert.co[2]
    if n_verts != 0:
        centr_x = x_tot/n_verts
        centr_y = y_tot/n_verts
        centr_z = z_tot/n_verts
    else:
        logging.warning("Warning: no verts to calc centroid")
        return [0, 0, 0]
    return [centr_x, centr_y, centr_z]

def linear_interpolation_y(xa,xb,ya,yb,y):
    return (((xa-xb)*y)+(xb*ya)-(xa*yb))/(ya-yb)


def correct_morph(base_form, current_form, morph_deltas, bboxes):
    time1 = time.time()
    new_morph_deltas = []
    for d_data in morph_deltas:

        idx = d_data[0]

        indices = bboxes[str(idx)]
        current_bounding_box = bounding_box(current_form, indices)
        base_bounding_box = bounding_box(base_form, indices)

        if base_bounding_box[0] != 0:
            scale_x = current_bounding_box[0]/base_bounding_box[0]
        else:
            scale_x = 1

        if base_bounding_box[1] != 0:
            scale_y = current_bounding_box[1]/base_bounding_box[1]
        else:
            scale_y = 1

        if base_bounding_box[2] != 0:
            scale_z = current_bounding_box[2]/base_bounding_box[2]
        else:
            scale_z = 1

        delta_x = d_data[1][0] * scale_x
        delta_y = d_data[1][1] * scale_y
        delta_z = d_data[1][2] * scale_z

        newd = mathutils.Vector((delta_x, delta_y, delta_z))
        new_morph_deltas.append([idx, newd])
    logging.info("Morphing corrected in {0} secs".format(time.time()-time1))
    return new_morph_deltas






