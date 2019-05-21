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

import bpy
from . import morphengine, skeletonengine, algorithms, proxyengine
#import cProfile, pstats, io
import os
import time
import json
import logging
import operator


#import faulthandler
#faulthandler.enable()

VALID_FINGERPRINTS = [
    "5564-5559-5565-5568-10720-10719-11163-11158-20244-20243-8077-8109",
    "4649-4825-4826-4650-9151-9050-9091-9077-914-2294-2295-931",
    "5337-5368-5367-5336-10584-10586-11009-11007-3277-3308-3305-3252",
    "4512-4506-4513-4518-8359-8376-8622-8598-14251-14245-3217-3330",
    "3684-3682-4426-4427-8441-8403-8226-8482-4836-4865-4868-4833",
    "4512-4506-4513-4518-8359-8376-8622-8598-14251-14245-3217-3330",
    "3672-8661-8712-4420-8273-8401-8222-8481-4836-4865-4868-4833"]

def get_fingerprints(obj):
    """
    Generate a quasi-unique ID for the mesh
    """
    n_poly = len(obj.data.polygons)
    if n_poly > 0:
        f01 = [str(i) for i in obj.data.polygons[int(n_poly*0.3)].vertices]
        f02 = [str(i) for i in obj.data.polygons[int(n_poly*0.6)].vertices]
        f03 = [str(i) for i in obj.data.polygons[-1].vertices]
        return "-".join(["-".join(f01), "-".join(f02), "-".join(f03)])
    else:
        #logging.warning("Object {0} has no polygons".format(obj.name))
        return("no_fingerprints")

def get_character_object():
    """
    Return the first mesh with a valid fingerprint
    """
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            if get_fingerprints(obj) in VALID_FINGERPRINTS:
                return obj
    return None

def check_humanoid(humanoid):
    """
    Check the existence of an humanoid mesh in the scene.
    """
    init_from_existing = False
    init_from_scratch = False
    skip_init = True

    if get_character_object():
        if not humanoid:
            init_from_existing = True
            init_from_scratch = False
            skip_init = False
        if humanoid and humanoid.filepath != bpy.data.filepath:
            init_from_existing = True
            init_from_scratch = False
            skip_init = False
    else:
        init_from_existing = False
        init_from_scratch = True
        skip_init = False
    return(init_from_existing, init_from_scratch, skip_init)

#class HumanProperty:
    #"""
    #The base parameter
    #"""

    #def __init__(self, name):

        #self.name = name
        #self.value = 0.5

    #def __lt__(self, other):
        #return self.name < other.name

    #def __repr__(self):
        #return "Prop <{0}>, value: {1}".format(self.name, self.value)


class HumanModifier:
    """
    A modifier is a group of related properties.
    """

    def __init__(self, name, obj_name):
        self.name = name
        self.obj_name = obj_name
        self.properties = []

    def get_object(self):
        """
        Get the blender object. It can't be stored because
        Blender's undo and redo change the memory locations
        """
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        return None

    def add(self, prop):
        self.properties.append(prop)

    def __contains__(self, prop):
        for propx in self.properties:
            if propx == prop:
                return True
        return False

    def get_properties(self):
        """
        Return the properties contained in the
        modifier. Important: keep unsorted!
        """
        return self.properties

    def get_property(self, prop):
        """
        Return the property by name.
        """
        for propx in self.properties:
            if propx == prop:
                return propx
        return None

    def is_changed(self, char_data):
        """
        If a prop is changed, the whole modifier is considered changed
        """
        obj = self.get_object()
        for prop in self.properties:
            current_val = getattr(obj, prop, 0.5)
            if char_data[prop] != current_val:
                return True
        return False

    def sync_morphdata_to_obj_prop(self, char_data):
        obj = self.get_object()
        for prop in self.properties:
            if hasattr(obj, prop):
                current_val = getattr(obj, prop, 0.5)
                char_data[prop] = current_val


    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return "Modifier <{0}> with {1} properties: {2}".format(
            self.name,
            len(self.properties),
            self.properties)

class HumanCategory:
    """
    A category is a group of related modifiers
    """

    def __init__(self, name):
        self.name = name
        self.modifiers = []

    def add(self, modifier):
        self.modifiers.append(modifier)

    def get_modifiers(self):
        return self.modifiers

    def get_modifier(self, name):
        for modifier in self.modifiers:
            if modifier.name == name:
                return modifier
        return None

    def get_all_properties(self):
        """
        Return all properties involved in the category,
        sorted and without double entries.
        """
        properties = []
        for modifier in self.modifiers:
            for prop in modifier.properties:
                if prop not in properties:
                    properties.append(prop)
        properties.sort()
        return properties

    def __contains__(self, mdf):
        for modifier in self.modifiers:
            if mdf.name == modifier.name:
                return True
        return False

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return "Category {0} with {1} modfiers".format(
            self.name,
            len(self.modifiers))


class Humanoid:
    """
    The humanoid is a container for categories of modifiers.
    """

    def __init__(self, update_funct, update_expr, update_pres, update_pose, update_eth, update_units, data_path, obj, lab_version):

        self.lab_vers = lab_version
        self.name = "" #The name is also used for boolean check so it must exist even if the obj is not valid.
        if obj:
            if get_fingerprints(obj) in VALID_FINGERPRINTS:
                logging.info("Init the humanoid: {0}".format(obj.name))
                obj["manuellab_vers"] = self.lab_vers
                self.name = obj.name
                self.filepath = bpy.data.filepath
                if obj.data.shape_keys:
                    logging.error("The human object can't have shapekeys")

                self.no_categories = "BasisAsymTest"
                self.categories = {}
                self.data_path = data_path
                self.realtime = True
                self.generator_bool_props = [
                    "preserve_mass", "preserve_height", "preserve_tone",
                    "preserve_face", "preserve_phenotype",
                    "set_tone_and_mass"]
                self.generator_float_props = ["body_mass", "body_tone"]
                self.armat = skeletonengine.SkeletonEngine(
                    obj,
                    obj.parent,
                    data_path)
                self.m_engine = morphengine.MorphingEngine(obj, data_path)
                self.character_data = {}
                for morph in self.m_engine.morph_data.keys():
                    self.init_character_data(morph)
                self.init_properties(
                    update_funct,
                    update_expr,
                    update_pres,
                    update_pose,
                    update_eth,
                    update_units)
                logging.info("Loaded {0} categories from morph database".format(
                    len(self.categories)))
                bpy.context.scene.objects.active = obj
                self.measures = self.m_engine.measures
                self.delta_measures = {}
                self.init_delta_measures()
            else:
                logging.error("Object {0} has not valid fingerprints".format(obj.name))
        else:
            logging.error("Impossible to init the humanoid if Blender object is none")

    def get_object(self):
        if self.name in bpy.data.objects:
            return bpy.data.objects[self.name]
        return None

    def __bool__(self):
        obj = self.get_object()
        if obj and len(self.get_categories()) > 0 and not obj.data.shape_keys:
            return True
        else:
            return False

    def get_categories(self):
        categories = self.categories.values()
        return sorted(categories)

    def get_category(self, name):
        if name in self.categories:
            return self.categories[name]

    def init_character_data(self, morph_name):
        """
        Creates categories and properties from shapekey name
        """
        components = morph_name.split("_")
        if components[0][:4] not in self.no_categories:
            if len(components) == 3:
                category_name = components[0]
                if category_name not in self.categories:
                    category = HumanCategory(category_name)
                    self.categories[category_name] = category
                else:
                    category = self.categories[category_name]

                modifier_name = components[0]+"_"+components[1]
                modifier = category.get_modifier(modifier_name)
                if not modifier:
                    modifier = HumanModifier(modifier_name, self.name)
                    category.add(modifier)

                for element in components[1].split("-"):
                    prop = components[0]+"_" + element
                    if prop not in modifier:
                        modifier.add(prop)
                    self.character_data[prop] = 0.5
            else:
                logging.warning("Wrong name for morph: {0}".format(morph_name))

    def reset_category(self):
        time1 = time.time()
        obj = self.get_object()
        if hasattr(obj, "morphingCategory"):
            category = self.get_category(obj.morphingCategory)
            for prop in category.get_all_properties():
                self.character_data[prop] = 0.5
            self.update_character(category_name=category.name, mode = "update_all")
            logging.info("Category resetted in {0} secs".format(time.time()-time1))
        else:
            logging.warning("The object has not morphingCategory property")

    def exist_measure_database(self):
        return self.m_engine.measures_database_exist




    def automodelling(self,use_measures_from_GUI=False, use_measures_from_dict=None, use_measures_from_current_obj=False, use_database=True, mix = False):

        if self.m_engine.measures_database_exist:
            time2 = time.time()
            obj = self.get_object()
            n_samples = 3

            if mix:
                n_samples = 10

            if use_measures_from_GUI:
                convert_to_inch = getattr(obj, "use_inch", False)        
                if convert_to_inch:
                    conversion_factor = 39.37001            
                else:
                    conversion_factor = 100
                wished_measures = {}
                for measure_name in self.m_engine.measures.keys():
                    if measure_name != "body_height_Z":
                        wished_measures[measure_name] = getattr(obj, measure_name, 0.5)/conversion_factor
                wished_measures["body_height_Z"] = wished_measures["head_height_Z"] + \
                                                        wished_measures["neck_height_Z"] + \
                                                        wished_measures["torso_height_Z"] +  \
                                                        wished_measures["buttock_height_Z"] + \
                                                        wished_measures["upperleg_length"] + \
                                                        wished_measures["lowerleg_length"] + \
                                                        wished_measures["feet_height_Z"]                

            if use_measures_from_current_obj:
                current_shape_verts = []
                for vert in obj.data.vertices:
                    current_shape_verts.append(vert.co.copy())
                wished_measures = self.m_engine.calculate_measures(vert_coords=current_shape_verts)
            if use_measures_from_dict:
                wished_measures = use_measures_from_dict


            if use_database:
                self.m_engine.calculate_proportions(wished_measures)
                similar_characters_data  = self.m_engine.compare_data_proportions()

                chars_data = []
                for char_data in similar_characters_data[:n_samples]:
                    score = char_data[0]
                    filepath = char_data[1]
                    chars_data.append([self.load_character(char_data[1]),score])

                self.automix_characters(chars_data)
                self.update_character(mode = "update_only_morphdata")

            self.measure_fitting(wished_measures,mix)
            self.update_character(mode = "update_directly_verts")

            logging.info("Human fitting in {0} secs".format(time.time()-time2))

    def clean_verts_to_process(self):
        self.m_engine.verts_to_update.clear()

    def correct_expressions(self, correct_all=False, finish_it=False):
        """Correct all the expression morphing that are different from 0"""

        #TODO: re-enable the finishing after some improvements

        time1 = time.time()
        expressions_to_correct = []
        for prop in self.categories["Expressions"].get_all_properties():
            if not correct_all:
                if self.character_data[prop] != 0.5:
                    expressions_to_correct.append(prop)
            else:
                expressions_to_correct.append(prop)
        self.m_engine.correct_morphs(expressions_to_correct)
        if finish_it:
            self.m_engine.apply_finishing_morph()
        logging.info("Expression corrected in {0} secs".format(time.time()-time1))


    def reset_character(self):
        time1 = time.time()
        obj = self.get_object()
        for category in self.get_categories():
            for modifier in category.get_modifiers():
                for prop in modifier.get_properties():
                    self.character_data[prop] = 0.5
        self.update_character(mode = "update_all")
        logging.info("Character reset in {0} secs".format(time.time()-time1))

    def sync_morphdata_to_all_obj_props(self):

        time1 = time.time()
        obj = self.get_object()
        for category in self.get_categories():
            for modifier in category.get_modifiers():
                for prop in modifier.get_properties():
                    if hasattr(obj, prop):
                        self.character_data[prop] = getattr(obj, prop)
                    else:
                        logging.warning("Object {0} has not property {1}".format(obj.name, prop))
                self.combine_morphings(modifier, refresh_only=True)
        logging.info("Morph data refreshed in {0} secs".format(time.time()-time1))


    def sync_gui_according_morphdata(self):
        obj = self.get_object()
        self.realtime = False
        for prop,value in self.character_data.items():
            setattr(obj, prop, value)

    def sync_gui_according_measures(self):
        
        obj = self.get_object()        
        measures = self.m_engine.calculate_measures()        
        convert_to_inch = getattr(obj, "use_inch", False)        
        if convert_to_inch:
            conversion_factor = 39.37001            
        else:
            conversion_factor = 100
        for measure_name,measure_val in measures.items():
            setattr(obj, measure_name, measure_val*conversion_factor)

    def update_character(self, category_name = None, mode = "update_all" ):
        time1 = time.time()
        obj = self.get_object()
        self.clean_verts_to_process()

        if mode == "update_all":
            update_directly_verts = False
            update_geometry_all = True
            update_geometry_selective = False
            update_armature = True
            update_normals = True
            update_proxy = True
            update_measures = True
            sync_morphdata = False
            sync_GUI = True

        if mode == "update_directly_verts":
            update_directly_verts = True
            update_geometry_all = False
            update_geometry_selective = False
            update_armature = True
            update_normals = True
            update_proxy = False
            update_measures = True
            sync_morphdata = False
            sync_GUI = True

        if mode == "update_only_morphdata":
            update_directly_verts = False
            update_geometry_all = False
            update_geometry_selective = False
            update_armature = False
            update_normals = False
            update_proxy = False
            update_measures = False
            sync_morphdata = False
            sync_GUI = False

        if mode == "update_realtime":
            update_directly_verts = False
            update_geometry_all = False
            update_geometry_selective = True
            update_armature = True
            update_normals = False
            update_proxy = False
            update_measures = False
            sync_morphdata = True
            sync_GUI = False

        if update_directly_verts:
            self.m_engine.update(update_all_verts=True)
        else:
            if category_name:
                category = self.categories[category_name]
                modified_modifiers = []
                for modifier in category.get_modifiers():
                    if modifier.is_changed(self.character_data):
                        modified_modifiers.append(modifier)
                for modifier in modified_modifiers:
                    if sync_morphdata:
                        modifier.sync_morphdata_to_obj_prop(self.character_data)
                    self.combine_morphings(modifier)
            else:
                for category in self.get_categories():
                    for modifier in category.get_modifiers():
                        self.combine_morphings(modifier, add_vertices_to_update=False)

        if update_geometry_all:
            self.m_engine.update(update_all_verts=True)
        if update_geometry_selective:
            self.m_engine.update(update_all_verts=False)
        if sync_GUI:
            self.sync_gui_according_morphdata()
        if update_measures:
            self.sync_gui_according_measures()
        if update_armature:
            self.armat.fit_joints()
        if update_normals:
            obj.data.calc_normals()
        if update_proxy:
            self.load_proxy()
        logging.info("Character updated in {0} secs".format(time.time()-time1))

    def generate_character(self):
        logging.info("Generating character...")
        random_value = {"LI": 0.1, "RE": 0.2, "NO": 0.3, "CA":0.4, "EX": 0.5}

        obj = self.get_object()
        excluded_properties = ["Expressions"]
        if obj.preserve_mass:
            excluded_properties += ["Mass"]
        if obj.preserve_tone:
            excluded_properties += ["Tone"]
        if obj.preserve_height:
            excluded_properties += ["Length", "Body_Size"]
        if obj.preserve_face:
            excluded_properties += ["Eye", "Eyelid", "Nose", "Mouth"]
            excluded_properties += ["Ear", "Head", "Forehead", "Cheek", "Jaw"]
        if obj.preserve_phenotype:
            excluded_properties = ["Expressions"]

        for prop in self.character_data:
            if not algorithms.is_excluded(prop, excluded_properties):
                new_val = algorithms.generate_parameter(
                    self.character_data[prop],
                    random_value[obj.random_engine],
                    obj.preserve_phenotype)
                if obj.set_tone_and_mass:
                    if "Mass" in prop:
                        new_val = obj.body_mass + (1-obj.body_mass)*new_val*obj.body_mass
                    if "Tone" in prop:
                        new_val = obj.body_tone + (1-obj.body_tone)*new_val*obj.body_tone
                self.character_data[prop] = new_val
        self.update_character(mode = "update_all")


    def init_delta_measures(self):

        obj = self.get_object()
        time1 = time.time()
        for relation in self.m_engine.measures_relat_data:
            m_name = relation[0]
            modifier_name = relation[1]
            for category in self.get_categories():
                for modifier in category.get_modifiers():
                    if modifier.name == modifier_name:
                        for prop in modifier.get_properties():

                            self.character_data[prop] = 0.0
                            self.combine_morphings(modifier)
                            measure1 = self.m_engine.calculate_measures(measure_name=m_name)

                            self.character_data[prop] = 1.0
                            self.combine_morphings(modifier)
                            measure3 = self.m_engine.calculate_measures(measure_name=m_name)

                            #Last measure also restores the value to 0.5
                            self.character_data[prop] = 0.5
                            self.combine_morphings(modifier)
                            measure2 = self.m_engine.calculate_measures(measure_name=m_name)

                            delta_name = modifier_name+prop

                            delta1 = measure1-measure2
                            delta3 = measure3-measure2

                            self.delta_measures[delta_name] = [delta1,delta3]


        logging.info("Delta init in {0} secs".format(time.time()-time1))


    def search_best_value(self,m_name,wished_measure,human_modifier,prop):

        self.character_data[prop] = 0.5
        self.combine_morphings(human_modifier)
        measure2 = self.m_engine.calculate_measures(measure_name=m_name)

        delta_name = human_modifier.name+prop

        delta1 = self.delta_measures[delta_name][0]
        delta3 = self.delta_measures[delta_name][1]

        measure1 = measure2 + delta1
        measure3 = measure2 + delta3

        if wished_measure < measure2:
            xa = 0
            xb = 0.5
            ya = measure1
            yb = measure2
        else:
            xa = 0.5
            xb = 1
            ya = measure2
            yb = measure3

        if ya-yb != 0:
            value = algorithms.linear_interpolation_y(xa,xb,ya,yb,wished_measure)

            if value < 0:
                value = 0
            if value > 1:
                value = 1
        else:
            value = 0.5

        return value


    def measure_fitting(self, wished_measures,mix = False):

        if self.m_engine.measures_database_exist:
            obj = self.get_object()
            time1 = time.time()
            for relation in self.m_engine.measures_relat_data:
                measure_name = relation[0]
                modifier_name = relation[1]
                if measure_name in wished_measures:
                    wish_measure = wished_measures[measure_name]
                    for category in self.get_categories():
                        for modifier in category.get_modifiers():
                            if modifier.name == modifier_name:
                                for prop in modifier.get_properties():
                                    if mix:
                                        best_val = self.search_best_value(measure_name,wish_measure,modifier,prop)
                                        value = (self.character_data[prop]+best_val)/2
                                        self.character_data[prop] = value
                                    else:
                                        self.character_data[prop] = self.search_best_value(measure_name,wish_measure,modifier,prop)
                                self.combine_morphings(modifier)

            logging.info("Measures fitting in {0} secs".format(time.time()-time1))


    def export_character(self, filepath):
        logging.info("Exporting character to {0}".format(algorithms.simple_path(filepath)))
        obj = self.get_object()
        char_data = {"manuellab_version": self.lab_vers, "structural":dict(), "proportions":dict()}
        if obj:
            for prop in self.character_data.keys():

                if self.character_data[prop] != 0.5:
                    char_data["structural"][prop] = round(self.character_data[prop], 4)

            if obj.export_proportions:
                self.m_engine.calculate_proportions(self.m_engine.calculate_measures())
                for proportion, value in self.m_engine.proportions.items():
                    char_data["proportions"][proportion] = round(value, 4)

            output_file = open(filepath, 'w')
            json.dump(char_data, output_file)
            output_file.close()

    def export_measures(self, filepath):
        logging.info("Exporting measures to {0}".format(algorithms.simple_path(filepath)))
        obj = self.get_object()
        char_data = {"manuellab_version": self.lab_vers, "measures":dict()}
        if obj:
            measures = self.m_engine.calculate_measures()
            for measure, measure_val in measures.items():
                measures[measure] = round(measure_val, 3)
            char_data["measures"]=measures
            output_file = open(filepath, 'w')
            json.dump(char_data, output_file)
            output_file.close()


    def load_character(self, filepath):
        logging.info("Loading character from {0}".format(algorithms.simple_path(filepath)))
        if os.path.isfile(filepath):
            try:
                database_file = open(filepath, "r")
                char_data = json.load(database_file)
                database_file.close()
            except:
                logging.error("json not valid, {0}".format(algorithms.simple_path(filepath)))
                return None

            #Check the database structure
            if not ("structural" in char_data):
                logging.error("This json has not the structural info, {0}".format(algorithms.simple_path(filepath)))
                return None

            c_data = char_data["structural"]
            return c_data
        else:
            logging.warning("File not valid: {0}".format(algorithms.simple_path(filepath)))
            return None


    def load_measures(self, filepath):
        logging.info("Loading measures from {0}".format(algorithms.simple_path(filepath)))
        if os.path.isfile(filepath):
            try:
                database_file = open(filepath, "r")
                char_data = json.load(database_file)
                database_file.close()
            except:
                logging.error("json not valid, {0}".format(algorithms.simple_path(filepath)))
                return None
            #Check the database structure
            if not ("measures" in char_data):
                logging.error("This json has not the measures info, {0}".format(algorithms.simple_path(filepath)))
                return None
            c_data = char_data["measures"]
            return c_data
        else:
            logging.warning("File not valid: {0}".format(algorithms.simple_path(filepath)))
            return None

    def automix_characters(self, chars_data):

        tot_val = 0
        for c_data in chars_data:
            tot_val += abs(c_data[1])

        for c_data in chars_data:
            c_data[1] = c_data[1]/tot_val

        normalized_data = {}
        really_changed_data = set()
        for n in range(len(chars_data)):
            c_data_dict = chars_data[n][0]
            c_data_factor = chars_data[n][1]

            for name in self.character_data.keys():
                if name in c_data_dict:
                    really_changed_data.add(name)
                else:
                    c_data_dict[name] = 0.5

            for name,value in c_data_dict.items():
                if name in normalized_data:
                    normalized_data[name] += value*c_data_factor
                else:
                    normalized_data[name] = value*c_data_factor
        for name in self.character_data.keys():
            if name in normalized_data:
                if name in really_changed_data:
                    self.character_data[name] = normalized_data[name]
            else:
                logging.warning("Impossible to normalize {0}".format(name))




    def import_character(self, filepath, reset_name = "nothing", reset_unassigned=True, mix=False, update_geometry = True):
        char_data = self.load_character(filepath)
        if char_data != None:
            for name in self.character_data.keys():
                if reset_name in name:
                    self.character_data[name] = 0.5
                if name in char_data:
                    if mix:
                        self.character_data[name] = (self.character_data[name]+char_data[name])/2
                    else:
                        self.character_data[name] = char_data[name]
                else:

                    if reset_unassigned:
                        if mix:
                            self.character_data[name] = (self.character_data[name]+0.5)/2
                        else:
                            self.character_data[name] = 0.5
        self.update_character(mode = "update_all")

    def import_measures(self, filepath):
        char_data = self.load_measures(filepath)
        if char_data:
            self.automodelling(use_measures_from_dict=char_data)

    def load_pose(self, filepath):
        logging.info("Loading pose from {0}".format(algorithms.simple_path(filepath)))
        self.armat.load_pose(filepath)
        self.load_proxy()

    def reset_pose(self):
        self.armat.reset_pose()
        self.load_proxy()

    def is_there_proxies(self):
        obj = self.get_object()
        for blender_obj in bpy.data.objects:
            if blender_obj != obj and blender_obj.type == 'MESH':
                return True
        return False

    def save_proxy(self):
        """
        Any mesh object in the scene that is not the humanoid one will
        considered a potential proxy and saved.
        """
        obj = self.get_object()
        for blender_obj in bpy.data.objects:
            if blender_obj != obj and blender_obj.type == 'MESH':
                blender_obj_id = get_fingerprints(blender_obj)
                tmp_path = bpy.context.user_preferences.filepaths.temporary_directory
                filepath1 = os.path.join(tmp_path, "".join([blender_obj_id, ".proxy"]))
                filepath2 = os.path.join(tmp_path, "".join([blender_obj_id, ".forma"]))
                proxyengine.save_proxy_database(obj, blender_obj, filepath1)
                proxyengine.save_forma_database(blender_obj, filepath2)

    def load_proxy(self):
        obj = self.get_object()
        scene = bpy.context.scene
        current_form = obj.to_mesh(scene, True, 'PREVIEW')
        for blender_obj in bpy.data.objects:
            if blender_obj != obj and blender_obj.type == 'MESH':
                blender_obj_id = get_fingerprints(blender_obj)
                tmp_path = bpy.context.user_preferences.filepaths.temporary_directory
                filepath1 = os.path.join(tmp_path, "".join([blender_obj_id, ".proxy"]))
                filepath2 = os.path.join(tmp_path, "".join([blender_obj_id, ".forma"]))
                if os.path.isfile(filepath1):
                    proxyengine.load_proxy_database(current_form, blender_obj, filepath1)
                    if os.path.isfile(filepath2):
                        forma_data = proxyengine.load_forma_database(filepath2)
                        boundary_verts = proxyengine.get_boundary_verts(blender_obj)
                        proxyengine.calculate_finishing_morph(
                            blender_obj,
                            boundary_verts,
                            forma_data)
                    else:
                        logging.warning("Forma file {0} not found".format(algorithms.simple_path(filepath2)))
                else:
                    logging.warning("Proxy file {0} not found".format(algorithms.simple_path(filepath1)))
        bpy.data.meshes.remove(current_form)

    def combine_morphings(self, modifier, refresh_only=False, add_vertices_to_update=True):
        """
        Mix shapekeys using smart combo algorithm.
        """

        values = []
        for prop in modifier.properties:
            val1 = algorithms.function_modifier_a(self.character_data[prop])
            val2 = algorithms.function_modifier_b(self.character_data[prop])
            values.append([val1, val2])
        names, weights = algorithms.smart_combo(modifier.name, values)
        for i in range(len(names)):
            if refresh_only:
                self.m_engine.morph_values[names[i]] = weights[i]
            else:
                self.m_engine.calculate_morph(
                    names[i],
                    weights[i],
                    add_vertices_to_update)

    def init_properties(self, update_realtime, update_expr, update_pres, update_pose, update_eth, update_units):
        preset_path = os.path.join(self.data_path, self.name, "presets")
        ethnic_path = os.path.join(self.data_path, self.name, "phenotypes")
        pose_path = os.path.join(self.data_path, self.name, "poses")
        expression_path = os.path.join(self.data_path, self.name, "expressions")
        preset_items = []
        ethnic_items = []
        pose_items = []
        expression_items = []

        bpy.types.Object.show_parameters = bpy.props.BoolProperty(
            name="Body parameters",
            description="Show parameter controls")

        #bpy.types.Object.show_measures = bpy.props.BoolProperty(
            #name="Body measures",
            #description="Show measures controls")
            
        #bpy.types.Object.show_dimensions = bpy.props.BoolProperty(
            #name="Show dimensions",
            #default = True,
            #description="Show body dimensions in realtime")
            
        bpy.types.Object.measure_filter = bpy.props.StringProperty(
            name="Filter",
            default = "",
            description="Filter the measures to show")

        bpy.types.Object.show_automodelling = bpy.props.BoolProperty(
            name="Automodelling tools",
            description="Show automodelling controls")

        bpy.types.Object.show_expressions = bpy.props.BoolProperty(
            name="Expression tools",
            description="Show expressions controls")

        bpy.types.Object.show_poses = bpy.props.BoolProperty(
            name="Pose tools",
            description="Show poses controls")

        bpy.types.Object.show_proxies = bpy.props.BoolProperty(
            name="Proxie tools",
            description="Show proxies controls")

        bpy.types.Object.finalize_character = bpy.props.BoolProperty(
            name="Finalize",
            description="Finalize the character")

        bpy.types.Object.utilities = bpy.props.BoolProperty(
            name="Utilities",
            description="Quick access to some Blender tools")

        bpy.types.Object.options = bpy.props.BoolProperty(
            name="Options",
            description="Options")
            
        bpy.types.Object.use_inch = bpy.props.BoolProperty(
            name="Inch",
            update = update_units,
            description="Use inch instead of cm")

        bpy.types.Object.show_files = bpy.props.BoolProperty(
            name="Files import-export",
            description="Show file controls")

        bpy.types.Object.random_generator = bpy.props.BoolProperty(
            name="Random generator",
            description="Show generator controls")

        bpy.types.Object.export_proportions = bpy.props.BoolProperty(
            name="Export proportions",
            description="Include proportions in the exported character file")


        bpy.types.Object.mix_characters = bpy.props.BoolProperty(
            name="Mix with current",
            description="Mix templates")

        bpy.types.Object.realtime_expression_fitting = bpy.props.BoolProperty(
            name="Fit expressions",
            description="Fit the expression to character face (slower)")


        if os.path.isdir(preset_path):
            for file in os.listdir(preset_path):
                p_item, extension = os.path.splitext(file)
                if "json" in extension:
                    preset_items.append((p_item, p_item, p_item))
                else:
                    logging.warning("Unknow file extension in {0}".format(algorithms.simple_path(preset_path)))
            preset_items.sort()
            bpy.types.Object.preset = bpy.props.EnumProperty(
                items=preset_items,
                name="Types",
                update=update_pres)
        else:
            logging.warning("{0} not found".format(algorithms.simple_path(preset_path)))

        if os.path.isdir(pose_path):
            for file in os.listdir(pose_path):
                po_item, extension = os.path.splitext(file)
                if "json" in extension:
                    pose_items.append((po_item, po_item, po_item))
            pose_items.sort()
            bpy.types.Object.static_pose = bpy.props.EnumProperty(
                items=pose_items,
                name="Pose",
                update=update_pose)
        else:
            logging.warning("{0} not found".format(algorithms.simple_path(pose_path)))

        if os.path.isdir(ethnic_path):
            for file in os.listdir(ethnic_path):
                et_item, extension = os.path.splitext(file)
                if "json" in extension:
                    ethnic_items.append((et_item, et_item, et_item))
            ethnic_items.sort()
            bpy.types.Object.ethnic = bpy.props.EnumProperty(
                items=ethnic_items,
                name="Phenotype",
                update=update_eth)
        else:
            logging.warning("{0} not found".format(algorithms.simple_path(ethnic_path)))

        if os.path.isdir(expression_path):
            for file in os.listdir(expression_path):
                e_item, extension = os.path.splitext(file)
                if "json" in extension:
                    expression_items.append((e_item, e_item, e_item))
            expression_items.sort()
            bpy.types.Object.expressions = bpy.props.EnumProperty(
                items=expression_items,
                name="Expressions",
                update=update_expr)
        else:
            logging.warning("{0} not found".format(algorithms.simple_path(expression_path)))

        human_object = self.get_object()
        if human_object:            
            for measure_name,measure_val in self.m_engine.measures.items():
                setattr(
                    bpy.types.Object,
                    measure_name,
                    bpy.props.FloatProperty(
                        name=measure_name, min=0.0, max=500.0,                        
                        default=measure_val))                


            for bool_prp in self.generator_bool_props:
                bool_name = bool_prp.split("_")[1:]
                bool_name = " ".join(bool_name)
                bool_name.capitalize()
                bool_descr = [s.capitalize() for s in bool_prp.split("_")]
                bool_descr = " ".join(bool_descr)
                setattr(
                    bpy.types.Object,
                    bool_prp,
                    bpy.props.BoolProperty(
                        name=bool_name,
                        description=bool_descr))
            for float_prp in self.generator_float_props:
                float_name = [s.capitalize() for s in float_prp.split("_")]
                float_name = " ".join(float_name)
                setattr(
                    bpy.types.Object,
                    float_prp,
                    bpy.props.FloatProperty(
                        name=float_name, min=0.0, max=1.0,
                        default=0.5))
            all_categories = self.get_categories()


            for prop in self.character_data:
                setattr(
                    bpy.types.Object,
                    prop,
                    bpy.props.FloatProperty(
                        name=prop, min=0.0, max=1.0,
                        precision=3,
                        default=0.5, update=update_realtime))
            categories_enum = []
            for category in all_categories:
                categories_enum.append(
                    (category.name, category.name, category.name))

            bpy.types.Object.morphingCategory = bpy.props.EnumProperty(
                items=categories_enum,
                name="Morphing categories")

            random_engine = [
                ("LI", "Light", "Little variations from the standard"),
                ("RE", "Realistic", "Realistic characters"),
                ("NO", "Noticeable", "Very characterized people"),
                ("CA", "Caricature", "Engine for caricatures"),
                ("EX", "Extreme", "Extreme characters")]
            bpy.types.Object.random_engine = bpy.props.EnumProperty(
                items=random_engine,
                name="Engine",
                default="RE")

