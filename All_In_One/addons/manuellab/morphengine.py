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

import os
import bpy
import mathutils
from . import algorithms, proxyengine
import time, json
import logging
import operator


#import cProfile, pstats, io
#import faulthandler
#faulthandler.enable()

class MorphingEngine:

    def __init__(self, obj, data_path):
        time1 = time.time()
        if obj:
            self.base_form = []
            self.final_form = []
            self.obj_name = obj.name
            self.shared_morphs_path = obj.name[:len(obj.name)-2]+".json"
            self.shared_bodies_path = obj.name[:len(obj.name)-2]+"_bodies"
            self.shared_measures_path = obj.name[:len(obj.name)-2]+"_measures.json"



            self.measures_data_path = os.path.join(
                data_path,
                "shared_measures",
                self.shared_measures_path)

            self.bodies_data_path = os.path.join(
                data_path,
                "shared_bodies",
                self.shared_bodies_path)

            self.measures_database_exist = False
            if os.path.isdir(self.bodies_data_path):
                if os.path.isfile(self.measures_data_path):
                    self.measures_database_exist = True

            self.shared_morph_data_path = os.path.join(
                data_path,
                "shared_morphs",
                self.shared_morphs_path)
            self.morph_data_path = os.path.join(
                data_path,
                self.obj_name,
                "morphs.json")
            self.morph_forma_path = os.path.join(
                data_path,
                self.obj_name,
                "forma.json")
            self.bounding_box_path = os.path.join(
                data_path,
                self.obj_name,
                "bbox.json")
            self.expressions_path = os.path.join(
                data_path,
                self.obj_name,
                "expressions.json")
            self.vertices_path = os.path.join(
                data_path,
                self.obj_name,
                "vertices.json")
            self.verts_to_update = set()
            self.morph_data = {}
            self.morph_data_cache = {}
            self.forma_data = None
            self.bbox_data = {}
            self.morph_values = {}
            self.morph_modified_verts = {}
            self.boundary_verts = None
            self.measures_data = {}
            self.measures_relat_data = []

            self.proportions = {}

            for vert in obj.data.vertices:
                self.final_form.append(vert.co.copy())
            self.load_vertices_database(self.vertices_path)
            self.load_morphs_database(self.morph_data_path)
            self.load_morphs_database(self.shared_morph_data_path)
            self.load_morphs_database(self.expressions_path)
            self.load_bboxes_database(self.bounding_box_path)
            self.load_measures_database(self.measures_data_path)

            self.measures = self.calculate_measures()

            #Checks:
            if len(self.final_form) != len(self.base_form):
                logging.critical("Vertices database not coherent with the vertices in the obj {0}".format(obj.name))
            #TODO: add more checks

        logging.info("Databases loaded in {0} secs".format(time.time()-time1))

    def __repr__(self):
        return "MorphEngine {0} with {1} morphings".format(self.obj_name, len(self.morph_data))

    def get_object(self):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        return None

    def error_msg(self, path):
        logging.error("Database file not found or corrupted: {0}".format(algorithms.simple_path(path)))

    def reset(self, update=True):
        for i in range(len(self.base_form)):
            self.final_form[i] = self.base_form[i]
        for morph_name in self.morph_values.keys():
            self.morph_values[morph_name] = 0.0
        if update:
            self.update(update_all_verts=True)

    def load_measures_database(self, measures_path):
        if os.path.isfile(measures_path):
            time1 = time.time()
            database_file = open(measures_path, "r")
            try:
                m_database = json.load(database_file)
                self.measures_data = m_database["measures"]
                self.measures_relat_data = m_database["relations"]
                logging.info("Measure database {0} loaded with {1} measures".format(algorithms.simple_path(measures_path),len(self.measures_data)))
            except:
                logging.error("Error decoding {0}".format(algorithms.simple_path(measures_path)))
            database_file.close()
        else:
            logging.warning("Measures database not found")

    def load_bboxes_database(self, bounding_box_path):
        if os.path.isfile(bounding_box_path):
            time1 = time.time()
            database_file = open(bounding_box_path, "r")
            try:
                self.bbox_data = json.load(database_file)
            except:
                logging.error("Error decoding {0}".format(algorithms.simple_path(bounding_box_path)))
            database_file.close()
            logging.info("Boundingboxes database {0} loaded in {1} secs".format(algorithms.simple_path(bounding_box_path),time.time()-time1))
        else:
            self.error_msg(bounding_box_path)

    def load_vertices_database(self, vertices_path):
        if os.path.isfile(vertices_path):
            time1 = time.time()
            database_file = open(vertices_path, "r")
            try:
                verts = json.load(database_file)
            except:
                logging.error("Error decoding {0}".format(algorithms.simple_path(vertices_path)))
            database_file.close()
            for vert_co in verts:
                self.base_form.append(mathutils.Vector(vert_co))
            logging.info("Vertices database {0} loaded in {1} secs".format(algorithms.simple_path(vertices_path),time.time()-time1))
        else:
            self.error_msg(vertices_path)


    def load_morphs_database(self, morph_data_path):
        time1 = time.time()
        if os.path.isfile(morph_data_path):
            database_file = open(morph_data_path, "r")
            m_data = json.load(database_file)
            database_file.close()

            for morph_name, deltas in m_data.items():
                morph_deltas = []
                modified_verts = set()
                for d_data in deltas:
                    t_delta = mathutils.Vector(d_data[1:])
                    morph_deltas.append([d_data[0], t_delta])
                    modified_verts.add(d_data[0])
                if morph_name in self.morph_data:
                    logging.warning("Morph {0} duplicated while loading morphs from file".format(morph_name))

                self.morph_data[morph_name] = morph_deltas
                self.morph_values[morph_name] = 0.0
                self.morph_modified_verts[morph_name] = modified_verts
            logging.info("Morph database {0} loaded in {1} secs".format(algorithms.simple_path(morph_data_path),time.time()-time1))
        else:
            self.error_msg(morph_data_path)

    def apply_finishing_morph(self):
        """
        Modify the Blender object in order to finish the surface.
        """
        time1 = time.time()
        obj = self.get_object()
        if not self.boundary_verts:
            self.boundary_verts = proxyengine.get_boundary_verts(obj)
        if not self.forma_data:
            self.forma_data = proxyengine.load_forma_database(self.morph_forma_path)
        proxyengine.calculate_finishing_morph(obj, self.boundary_verts, self.forma_data, threshold=0.25)
        logging.info("Finishing applied in {0} secs".format(time.time()-time1))

    def calculate_measures(self,measure_name = None,vert_coords=None):

        if not vert_coords:
            vert_coords = self.final_form
        measures = {}
        time1 = time.time()
        if measure_name:
            if measure_name in self.measures_data:
                indices =  self.measures_data[measure_name]                
                axis = measure_name[-1]
                return algorithms.length_of_strip(vert_coords, indices, axis)
        else:
            for measure_name in self.measures_data.keys():
                measures[measure_name] = self.calculate_measures(measure_name, vert_coords)
            logging.info("Measures calculated in {0} secs".format(time.time()-time1))
            return measures


    def calculate_proportions(self, measures):

        if measures == None:
            measures = self.measures
        if "body_height_Z" in measures:
            for measure, value in measures.items():
                proportion = value/measures["body_height_Z"]
                if measure in self.measures:
                    self.proportions[measure] = proportion
                else:
                    logging.error("The measure {0} not present in the proportion database".format(measure))
        else:
            logging.error("The base measure not present in the analyzed database")

    def compare_file_proportions(self,filepath):

        if os.path.isfile(filepath):
            try:
                database_file = open(filepath, "r")
                char_data = json.load(database_file)
                database_file.close()
            except:
                logging.error("json not valid, {0}".format(algorithms.simple_path(filepath)))
                return False
            if "proportions" in char_data:
                return (self.calculate_matching_score(char_data["proportions"]),filepath)
            else:
                logging.info("File {0} does not contain proportions".format(algorithms.simple_path(filepath)))


    def compare_data_proportions(self):
        scores = []
        time1 = time.time()
        if os.path.isdir(self.bodies_data_path):
            for file in os.listdir(self.bodies_data_path):
                body_data, extension = os.path.splitext(file)
                if "json" in extension:
                    scores.append(self.compare_file_proportions(os.path.join(self.bodies_data_path,file)))
            scores.sort(key=operator.itemgetter(0), reverse=True)
            logging.info("Measures compared with database in {0} seconds".format(time.time()-time1))
        else:
            logging.warning("Bodies database not found")

        #error_value = scores[0][0]
        return scores

    def calculate_matching_score(self, proportions):
        data_score = 0
        for p,v in proportions.items():
            if p in self.proportions:
                if p != "body_height_Z":
                    data_score += abs(self.proportions[p]-v)*self.proportions[p]
                    if data_score > 1:
                        data_score = 1
            else:
                logging.warning("Measure {0} not present in inner proportions database".format(p))
        return len(self.proportions)-data_score


    def correct_morphs(self, names):
        morph_values_cache = {}
        for morph_name in self.morph_data.keys():
            for name in names:
                if name in morph_name:
                    morph_values_cache[morph_name] = self.morph_values[morph_name]#Store the values before the correction
                    self.calculate_morph(morph_name, 0.0) #Reset the morphs to correct

        for morph_name, morph_deltas in self.morph_data.items():
            for name in names:
                if name in morph_name: #If the morph is in the list of morph to correct
                    if morph_name in self.morph_data_cache:
                        morph_deltas_to_recalculate = self.morph_data_cache[morph_name]
                    else:
                        self.morph_data_cache[morph_name] = morph_deltas
                        morph_deltas_to_recalculate = self.morph_data_cache[morph_name]
                    self.morph_data[morph_name] = algorithms.correct_morph(
                        self.base_form,
                        self.final_form,
                        morph_deltas_to_recalculate,
                        self.bbox_data)
        for morph_name in self.morph_data.keys():
            for name in names:
                if name in morph_name:
                    self.calculate_morph(
                        morph_name,
                        morph_values_cache[morph_name])

        self.update()

    def convert_to_blshapekey(self, shape_key_name):
        obj = self.get_object()
        sk_new = obj.shape_key_add(name=shape_key_name, from_mix=False)
        sk_new.slider_min = 0
        sk_new.slider_max = 1.0
        sk_new.value = 0.0
        obj.use_shape_key_edit_mode = True

        for i in range(len(self.final_form)):
            sk_new.data[i].co = obj.data.vertices[i].co

    def convert_all_to_blshapekeys(self, finish=False):

        #TODO: re-enable the finishing (finish = True) after some improvements

        #Reset all values (for expressions only) and create the basis key
        for morph_name in self.morph_data.keys():
            if "Expression" in morph_name:
                self.calculate_morph(morph_name, 0.0)
                self.update()
        self.convert_to_blshapekey("basis")

        #Store the character in neutral expression
        obj = self.get_object()
        stored_vertices = []
        for vert in obj.data.vertices:
            stored_vertices.append(mathutils.Vector(vert.co))


        logging.info("Storing neutral character...OK")
        counter = 0
        for morph_name in sorted(self.morph_data.keys()):
            if "Expression" in morph_name:
                counter += 1
                self.calculate_morph(morph_name, 1.0)
                logging.info("Converting {} to shapekey".format(morph_name))
                self.update()
                if finish:

                    self.apply_finishing_morph()

                    self.convert_to_blshapekey(morph_name)
                    #self.calculate_morph("Finishing", 0.0)
                    #self.calculate_morph(morph_name, 0.0)
                else:
                    self.convert_to_blshapekey(morph_name)
                    #self.calculate_morph(morph_name, 0.0)

                #Restore the neutral expression
                for i in range(len(self.final_form)):
                    self.final_form[i] = stored_vertices[i]
                self.update(update_all_verts=True)
        logging.info("Successfully converted {0} morphs in shapekeys".format(counter))



    def update(self, update_all_verts=False):
        obj = self.get_object()
        vertices = obj.data.vertices
        if update_all_verts == True:
            for i in range(len(self.final_form)):
                vertices[i].co = self.final_form[i]
        else:
            for i in self.verts_to_update:
                vertices[i].co = self.final_form[i]

    def calculate_morph(self, morph_name, val, add_vertices_to_update=True):

        if morph_name in self.morph_data:
            real_val = val - self.morph_values[morph_name]
            if real_val != 0.0:
                morph = self.morph_data[morph_name]
                for d_data in morph:
                    i = d_data[0]
                    delta = d_data[1]
                    self.final_form[i] = self.final_form[i] + delta*real_val
                if add_vertices_to_update:
                    self.verts_to_update = self.verts_to_update.union(self.morph_modified_verts[morph_name])
                self.morph_values[morph_name] = val
        else:
            logging.debug("Morph data {0} not found".format(morph_name))








