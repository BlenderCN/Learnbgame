# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

import bpy
import gc
from io import BytesIO
import pickle
from base64 import b64encode, b64decode

class Pickler(pickle.Pickler):
    def persistent_id(self, obj):
        return repr(obj) if repr(obj).startswith("bpy.data") else None

class Unpickler(pickle.Unpickler):
    def persistent_load(self, pid):
        if not pid.startswith("bpy.data") and len(pid.split()) == 1:
            raise pickle.UnpicklingError(pid + " is forbidden")
        exec("id_data = " + pid)
        name = locals()["id_data"].mbdyn_name
        exec("id_data = " + pid.split("[")[0] + "[\"" + name + "\"]")
        return locals()["id_data"]
    def find_class(self, module, name):
        if module.startswith("BlenderAndMBDyn"):
            module = ".".join((__package__, module.split(".", 1)[1]))
        elif module == "builtins" and name in ("exec", "eval"):
            raise pickle.UnpicklingError("global " + ".".join((module, name)) + " is forbidden")
        return super().find_class(module, name)

class EntityLookupError(LookupError):
    pass

class Entities(list):
    def filter(self, types, obj=None):
        if isinstance(types, str):
            types = [types,]
        return [e for e in self if e.type in types and 
            (not obj or (hasattr(e, "objects") and e.objects[0] == obj))]
    def get_by_name(self, name):
        if name != "New":
            for e in self:
                if e.name == name:
                    return e
        raise EntityLookupError
    def move(self, i, j):
        self[i], self[j] = self[j], self[i]

class Database:
    def __init__(self):
        self.compatibility_stamp = 0
        self.element = Entities()
        self.drive = Entities()
        self.driver = Entities()
        self.friction = Entities()
        self.shape = Entities()
        self.function = Entities()
#        self.ns_node = Entities()
        self.constitutive = Entities()
        self.matrix = Entities()
        self.input_card = Entities()
        self.definition = Entities()
        self.simulator = Entities()
        self.node = list()
        self.clear()
    def clear(self):
        self.element.clear()
        self.drive.clear()
        self.driver.clear()
        self.friction.clear()
        self.shape.clear()
        self.function.clear()
#        self.ns_node.clear()
        self.constitutive.clear()
        self.matrix.clear()
        self.input_card.clear()
        self.definition.clear()
        self.simulator.clear()
        self.node.clear()
        self.scene = None
    def all_entities(self):
        return (self.element + self.drive + self.driver + self.friction + self.shape + self.function +
#            self.ns_node + 
            self.constitutive + self.matrix + self.input_card + self.definition + self.simulator)
    def entities_using(self, objects):
        set_objects = set(objects)
        entities = list()
        for entity in self.all_entities():
            if hasattr(entity, "objects"):
                if not set_objects.isdisjoint(set(entity.objects)):
                    entities.append(entity)
        entities.extend([e for e in self.element if (e.type == 'Driven' and e.element in entities)])
        return entities
    def entities_originating_from(self, objects):
        entities = list()
        for entity in self.all_entities():
            if hasattr(entity, "objects"):
                if entity.objects[0] in objects:
                    entities.append(entity)
        entities.extend([e for e in self.element if (e.type == 'Driven' and e.element in entities)])
        return entities
    def users_of(self, entity):
        ret = list()
        for e in self.all_entities():
            if True in [((entity == v) or (isinstance(v, list) and entity in v)) for v in vars(e).values()]:
                ret.append(e)
        return ret
    def pickle(self):
        if not self.scene:
            self.scene = bpy.context.scene
        bpy.context.scene.mbdyn_name = bpy.context.scene.name
        for obj in bpy.context.scene.objects:
            obj.mbdyn_name = obj.name
        with BytesIO() as f:
            p = Pickler(f)
            p.dump(self)
            self.scene.pickled_database = b64encode(f.getvalue()).decode()
            del p
        gc.collect()
    def unpickle(self):
        self.clear()
        if bpy.context.scene.pickled_database:
            with BytesIO(b64decode(bpy.context.scene.pickled_database.encode())) as f:
                up = Unpickler(f)
                database = up.load()
                for k, v in vars(database).items():
                    if type(v) in [list, Entities]:
                        self.__dict__[k].extend(v)
                    elif type(v) in [dict, set]:
                        self.__dict__[k].update(v)
                    else:
                        self.__dict__[k] = v
                del up, database
        gc.collect()
    def replace(self):
        self.pickle()
        self.unpickle()
