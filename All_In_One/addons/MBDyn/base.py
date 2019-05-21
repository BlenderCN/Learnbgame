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

if "bpy" in locals():
    import imp
    for x in [database_module, common, menu]:
        imp.reload(x)
else:
    from . import database_module
    from . import common
    from . import menu
from .database_module import Database, EntityLookupError
from .common import FORMAT, safe_name, write_vector, write_orientation, Cube
from .menu import method, nonlinear_solver, Tree
import bpy
import addon_utils
from collections import OrderedDict
from copy import copy
from sys import getrefcount
import webbrowser, os
from collections import defaultdict

category = "MBDyn"
root_dot = "_".join(category.lower().split()) + "."
database = Database()

def update_constitutive(self, context, name, dimension=""):
    if context.scene.popups_enabled:
        if name == "New":
            bpy.ops.wm.call_menu(name=root_dot+"constitutive"+dimension)
        else:
            entity = database.constitutive.get_by_name(name)
            context.scene.constitutive_index = database.constitutive.index(entity)
            entity.edit()
def update_definition(self, context, name, definition_type):
    if context.scene.popups_enabled:
        if name == "New":
            if definition_type in ["Method", "Nonlinear solver"]:
                bpy.ops.wm.call_menu(name=root_dot + "_".join(definition_type.lower().split()))
            else:
                exec("bpy.ops." + root_dot + "c_" + "_".join(definition_type.lower().split()) + "('INVOKE_DEFAULT')")
        else:
            entity = database.definition.get_by_name(name)
            context.scene.definition_index = database.definition.index(entity)
            entity.edit()
def update_drive(self, context, name, drive_dimension, drive_type=None):
    if context.scene.popups_enabled:
        if name == "New":
            if drive_type:
                exec("bpy.ops." + root_dot + "c_" + "_".join(drive_type.lower().split()) + "('INVOKE_DEFAULT')")
            else:
                if drive_dimension == "1D":
                    bpy.ops.wm.call_menu(name=root_dot+"scalar_drive")
                else:
                    bpy.ops.wm.call_menu(name=root_dot+drive_dimension.lower()+"_drive")
        else:
            entity = database.drive.get_by_name(name)
            context.scene.drive_index = database.drive.index(entity)
            entity.edit()
def update_driver(self, context, name, driver_type=None):
    if context.scene.popups_enabled:
        if name == "New":
            if driver_type:
                exec("bpy.ops." + root_dot + "c_" + "_".join(driver_type.lower().split()) + "('INVOKE_DEFAULT')")
            else:
                bpy.ops.wm.call_menu(name=root_dot+"driver")
        else:
            entity = database.driver.get_by_name(name)
            context.scene.driver_index = database.driver.index(entity)
            entity.edit()
def update_element(self, context, name, element_type):
    if context.scene.popups_enabled:
        if name == "New":
            if element_type:
                exec("bpy.ops." + root_dot + "c_" + "_".join(element_type.lower().split()) + "('INVOKE_DEFAULT')")
            else:
                bpy.ops.wm.call_menu(name=root_dot+"element")
        else:
            entity = database.element.get_by_name(name)
            context.scene.element_index = database.element.index(entity)
            entity.edit()
            del entity
def update_friction(self, context, name):
    if context.scene.popups_enabled:
        if name == "New":
            bpy.ops.wm.call_menu(name=root_dot+"friction")
        else:
            entity = database.friction.get_by_name(name)
            context.scene.friction_index = database.friction.index(entity)
            entity.edit()
def update_function(self, context, name):
    if context.scene.popups_enabled:
        if name == "New":
            bpy.ops.wm.call_menu(name=root_dot+"function")
        else:
            entity = database.function.get_by_name(name)
            context.scene.function_index = database.function.index(entity)
            entity.edit()
def update_shape(self, context, name):
    if context.scene.popups_enabled:
        if name == "New":
            bpy.ops.wm.call_menu(name=root_dot+"shape")
        else:
            entity = database.shape.get_by_name(name)
            context.scene.shape_index = database.shape.index(entity)
            entity.edit()
def update_matrix(self, context, name, matrix_type):
    if context.scene.popups_enabled:
        if name == "New":
            exec("bpy.ops." + root_dot + "c_" + "_".join(matrix_type.lower().split()) + "('INVOKE_DEFAULT')")
        else:
            entity = database.matrix.get_by_name(name)
            context.scene.matrix_index = database.matrix.index(entity)
            entity.edit()
def update_input_card(self, context, name, input_card_type, value_type=None):
    if context.scene.popups_enabled:
        if name == "New":
            kwargs = ("value_type='" + value_type + "'") if input_card_type == "Set" and value_type else ""
            exec("bpy.ops." + root_dot + "c_" + "_".join(input_card_type.lower().split()) + "('INVOKE_DEFAULT', " + kwargs + ")")
        else:
            entity = database.input_card.get_by_name(name)
            context.scene.input_card_index = database.input_card.index(entity)
            entity.edit()
def update_scene(self, context, name):
    if name == "New":
        context.blend_data.scenes.new(context.scene.name)

def enum_scenes(self, context):
    return [(s.name, s.name, "") for s in bpy.data.scenes] + [("New", "New", "")]
def enum_objects(self, context):
    return [(o.name, o.name, "") for o in context.scene.objects if o.type == 'MESH']
def enum_matrix(self, context, matrix_type):
    return [(m.name, m.name, "") for i, m in enumerate(context.scene.matrix_uilist)
        if database.matrix[i].type == matrix_type] + [("New", "New", "")]
def enum_constitutive(self, context, dimension):
    return  [(c.name, c.name, "") for i, c in enumerate(context.scene.constitutive_uilist)
        if dimension in database.constitutive[i].dimension] + [("New", "New", "")]
def enum_definition(self, context, definition_type):
    return [(d.name, d.name, "") for i, d in enumerate(context.scene.definition_uilist)
        if (database.definition[i].type == definition_type)
            or (definition_type == "Method" and database.definition[i].type in method)
            or (definition_type == "Nonlinear solver" and database.definition[i].type in nonlinear_solver)] + [("New", "New", "")]
def enum_drive(self, context, drive_type, drive_dimension="1D"):
    return [(d.name, d.name, "") for i, d in enumerate(context.scene.drive_uilist)
        if (database.drive[i].dimension == drive_dimension)
        and (not drive_type or (database.drive[i].type == drive_type))] + [("New", "New", "")]
def enum_driver(self, context, driver_type):
    ret = [(d.name, d.name, "") for i, d in enumerate(context.scene.driver_uilist)
        if not driver_type
        or (database.driver[i].type == driver_type)]
    if driver_type == "Event stream" and ret:
        return ret
    else:
        return ret + [("New", "New", "")]
def enum_element(self, context, element_type, group):
    return [(e.name, e.name, "") for i, e in enumerate(context.scene.element_uilist) if
        (not group and not element_type) or 
        (group and hasattr(database.element[i], "group") and database.element[i].group == group) or
        (element_type and database.element[i].type == element_type)] # if not hasattr(database.element[i], "consumer")]
def enum_function(self, context):
    return [(f.name, f.name, "") for f in context.scene.function_uilist] + [("New", "New", "")]
def enum_friction(self, context):
    return [(f.name, f.name, "") for f in context.scene.friction_uilist] + [("New", "New", "")]
def enum_shape(self, context):
    return [(s.name, s.name, "") for s in context.scene.shape_uilist] + [("New", "New", "")]
def enum_input_card(self, context, card_type, value_type=None):
    return [(c.name, c.name, "") for i, c in enumerate(context.scene.input_card_uilist)
        if database.input_card[i].type == card_type and ((not value_type) or database.input_card[i].value_type == value_type)] + [("New", "New", "")]

@bpy.app.handlers.persistent
def load_post(*args, **kwargs):
    database.unpickle()
    for scene in bpy.data.scenes:
        scene.dirty_simulator = True
        scene.hash = repr(hash(scene))
        for ob in scene.objects:
            ob.hash = repr(hash(ob))

entity_obs = defaultdict(list)

@bpy.app.handlers.persistent
def scene_update_pre(*args, **kwargs):
    for entity in database.all_entities():
        if hasattr(entity, "objects"):
            for i, ob in enumerate(entity.objects):
                entity_obs[ob.name].append((entity, i))

@bpy.app.handlers.persistent
def scene_update_post(*args, **kwargs):
    scene = bpy.context.scene
    if scene.hash != repr(hash(scene)):
        scene.hash = repr(hash(scene))
        if scene.mbdyn_name == scene.name:
            database.scene = scene
            for ob in scene.objects:
                if ob.hash != repr(hash(ob)):
                    ob.hash = repr(hash(ob))
                    for entity, i in entity_obs[ob.name]:
                        entity.objects[i] = ob
        else:
            database.replace()
            bpy.ops.object.select_all(action='DESELECT')
    elif database.scene != scene:
        database.replace()
        bpy.ops.object.select_all(action='DESELECT')
    entity_obs.clear()

@bpy.app.handlers.persistent
def save_pre(*args, **kwargs):
    database.pickle()

class BPY:
    @classmethod
    def FORMAT(cls, prop):
        return prop.safe_name() if isinstance(prop, Entity) else (("\"" + prop + "\"") if isinstance(prop, str) else FORMAT(prop))
    class Mode:
        mandatory = bpy.props.BoolProperty(default=False)
        select = bpy.props.BoolProperty(default=False, update=lambda self, context: self.set_check_select())
        check_select_value = bpy.props.BoolProperty(default=False)
        def set_check_select(self):
            self.check_select_value = True
        def to_be_stored(self):
            return self.mandatory or self.select
        def to_be_assigned(self, arg):
            self.select = False if self.mandatory else arg is not None 
            return arg is not None and (self.select or self.mandatory)
        def draw(self, layout, text="", prefix="Use"):
            row = layout.row()
            if not self.mandatory:
                row.prop(self, "select", text="")
                if not self.select:
                    row.label(" ".join([prefix, text]))
            if self.mandatory or self.select:
                if 12 < len(text):
                    row.label(text + ":")
                    text=""
                    row = layout.row()
                row.prop(self, "name", text)
        def check(self, context):
            ret = self.check_select_value
            self.check_select_value = False
            return ret
    class ValueMode(Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_input_card(self, context, self.input_card_type, self.value_type),
            name="Name", description="Select a card, or New to create one",
            update=lambda self, context: update_input_card(self, context, self.name, self.input_card_type, self.value_type))
        is_card = bpy.props.BoolProperty(update=lambda self, context: self.set_check_is_card(), description="Toggle for variable name instead of value")
        check_is_card_value = bpy.props.BoolProperty(default=False)
        input_card_type = bpy.props.StringProperty(default="Set")
        value_type = bpy.props.StringProperty()
        def set_check_is_card(self):
            self.check_is_card_value = True
        def assign(self, arg):
            if self.to_be_assigned(arg):
                if isinstance(arg, (bool, int, float, str)):
                    self.is_card = False
                    self.value = arg
                    self.value_type = {bool: "bool", int: "integer", float: "real", str: "string"}[type(arg)]
                else:
                    self.is_card = True
                    self.name = arg.name
                    self.type = arg.type
        def store(self):
            if not self.to_be_stored():
                return None
            elif self.is_card:
                return database.input_card.get_by_name(self.name) if self.to_be_stored() else None
            else:
                return self.value
        def draw(self, layout, text="", prefix="Use"):
            row = layout.row()
            if not self.mandatory:
                row.prop(self, "select", text="")
                if not self.select:
                    row.label(" ".join([prefix, text]))
            if self.mandatory or self.select:
                if 12 < len(text):
                    row.label(text + ":")
                    text=""
                    row = layout.row()
                if self.is_card:
                    row.prop(self, "name", text=text)
                else:
                    row.prop(self, "value", text=text)
                if prefix == "Use":
                    row.prop(self, "is_card", text="", toggle=True)
        def check(self, context):
            ret = self.check_is_card_value
            self.check_is_card_value = False
            return ret or super().check(context)
    class InputCard(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_input_card(self, context, self.input_card_type, self.value_type),
            name="Name", description="Select a card, or New to create one",
            update=lambda self, context: update_input_card(self, context, self.name, self.input_card_type, self.value_type))
        input_card_type = bpy.props.StringProperty(default="Module load")
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.value_type = arg.value_type
                self.name = arg.name
        def store(self):
            return database.input_card.get_by_name(self.name) if self.to_be_stored() else None
    class Constitutive(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_constitutive(self, context, self.dimension), name="Name", description="Select a constitutive, or New to create one",
            update=lambda self, context: update_constitutive(self, context, self.name, self.dimension))
        dimension = bpy.props.StringProperty()
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.dimension = arg.dimension
                self.name = arg.name
        def store(self):
            return database.constitutive.get_by_name(self.name) if self.to_be_stored() else None
    class Definition(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_definition(self, context, self.type), name="Name", description="Select a definition, or New to create one",
            update=lambda self, context: update_definition(self, context, self.name, self.type))
        type = bpy.props.StringProperty()
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.type = arg.type
                self.name = arg.name
        def store(self):
            return database.definition.get_by_name(self.name) if self.to_be_stored() else None
    class Drive(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_drive(self, context, self.type, self.dimension), name="Name", description="Select a drive, or New to create one",
            update=lambda self, context: update_drive(self, context, self.name, self.dimension, self.type))
        dimension = bpy.props.StringProperty(default="1D")
        type = bpy.props.StringProperty()
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.dimension = arg.dimension
                self.name = arg.name
        def store(self):
            return database.drive.get_by_name(self.name) if self.to_be_stored() else None
    class Driver(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_driver(self, context, self.type), name="Name", description="Select a driver, or New to create one",
            update=lambda self, context: update_driver(self, context, self.name, self.type))
        type = bpy.props.StringProperty()
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.name = arg.name
        def store(self):
            return database.driver.get_by_name(self.name) if self.to_be_stored() else None
    class Element(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_element(self, context, self.type, self.group), name="Name", description="Select an element, or New to create one",
            update=lambda self, context: update_element(self, context, self.name, self.type))
        type = bpy.props.StringProperty()
        group = bpy.props.StringProperty()
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.name = arg.name
        def store(self):
            return database.element.get_by_name(self.name) if self.to_be_stored() else None
    class Segment(bpy.types.PropertyGroup):
        name = bpy.props.StringProperty()
        edit = bpy.props.BoolProperty(set=lambda self, value: update_element(self, bpy.context, self.name))
        def assign(self, arg):
            self.name = arg.name
        def store(self):
            return database.element.get_by_name(self.name)
    class Friction(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=enum_friction, name="Name", description="Select a friction, or New to create one",
            update=lambda self, context: update_friction(self, context, self.name))
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.name = arg.name
        def store(self):
            return database.friction.get_by_name(self.name) if self.to_be_stored() else None
    class Function(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=enum_function, name="Name", description="Select a function, or New to create one",
            update=lambda self, context: update_function(self, context, self.name))
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.name = arg.name
        def store(self):
            return database.function.get_by_name(self.name) if self.to_be_stored() else None
    class Matrix(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=lambda self, context: enum_matrix(self, context, self.type), name="Name", description="Select a matrix, or New to create one",
            update=lambda self, context: update_matrix(self, context, self.name, self.type))
        type = bpy.props.StringProperty()
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.type = arg.type
                self.name = arg.name
        def store(self):
            return database.matrix.get_by_name(self.name) if self.to_be_stored() else None
    class Shape(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=enum_shape, name="Name", description="Select a shape, or New to create one",
            update=lambda self, context: update_shape(self, context, self.name))
        def assign(self, arg):
            if self.to_be_assigned(arg):
                self.name = arg.name
        def store(self):
            return database.shape.get_by_name(self.name) if self.to_be_stored() else None
    class Scene(bpy.types.PropertyGroup, Mode):
        name = bpy.props.EnumProperty(items=enum_scenes, name="Name", description="Select a scene, or New to create one",
            update=lambda self, context: update_scene(self, context, self.name))
    class Bool(bpy.types.PropertyGroup, ValueMode):
        value = bpy.props.BoolProperty()
        value_type = bpy.props.StringProperty(default="bool")
    class Float(bpy.types.PropertyGroup, ValueMode):
        value = bpy.props.FloatProperty(min=-9.9e10, max=9.9e10, step=100, precision=6)
        value_type = bpy.props.StringProperty(default="real")
    class Int(bpy.types.PropertyGroup, ValueMode):
        value = bpy.props.IntProperty()
        value_type = bpy.props.StringProperty(default="integer")
    class Str(bpy.types.PropertyGroup, ValueMode):
        value = bpy.props.StringProperty()
        value_type = bpy.props.StringProperty(default="string")
    class MatrixFloat(bpy.types.PropertyGroup):
        mandatory = bpy.props.BoolProperty(default=False)
        type = bpy.props.StringProperty()
        is_matrix = bpy.props.BoolProperty(update=lambda self, context: self.set_check_is_matrix())
        check_is_matrix_value = bpy.props.BoolProperty(default=False)
        def set_check_is_matrix(self):
            self.check_is_matrix_value = True
        def assign(self, arg):
            if arg in database.matrix:
                self.is_matrix = True
                self.matrix.assign(arg)
            else:
                self.is_matrix = False
                self.float.assign(arg)
        def store(self):
            if self.is_matrix:
                return self.matrix.store()
            else:
                return self.float.store()
        def draw(self, layout, text=""):
            self.float.mandatory = self.matrix.mandatory = self.mandatory
            if self.type == "float":
                self.is_matrix = False
                self.float.draw(layout, text)
            else:
                self.is_matrix = True
                self.matrix.type = self.type
                self.matrix.draw(layout, text)
        def check(self, context):
            ret = self.check_is_matrix_value
            self.check_is_matrix_value = False
            return ret or self.float.check(context) or self.matrix.check(context)
    klasses = [InputCard, Constitutive, Definition, Drive, Driver, Element, Segment, Friction, Function, Matrix, Shape, Scene, Bool, Int, Float, Str, MatrixFloat]
    mbdyn_path = None
    plot_data = dict()
    @classmethod
    def register(cls):
        cls.MatrixFloat.matrix = bpy.props.PointerProperty(type = cls.Matrix)
        cls.MatrixFloat.float = bpy.props.PointerProperty(type = cls.Float)
        for klass in cls.klasses:
            bpy.utils.register_class(klass)
        bpy.app.handlers.load_post.append(load_post)
        bpy.app.handlers.scene_update_pre.append(scene_update_pre)
        bpy.app.handlers.scene_update_post.append(scene_update_post)
        bpy.app.handlers.save_pre.append(save_pre)
        bpy.types.Scene.pickled_database = bpy.props.StringProperty()
        bpy.types.Scene.dirty_simulator = bpy.props.BoolProperty(default=True)
        bpy.types.Scene.hash = bpy.props.StringProperty()
        bpy.types.Scene.clean_log = bpy.props.BoolProperty(default=False)
        bpy.types.Scene.mbdyn_default_orientation = bpy.props.StringProperty()
        bpy.types.Scene.mbdyn_name = bpy.props.StringProperty()
        bpy.types.Scene.popups_enabled = bpy.props.BoolProperty(default=False)
        bpy.types.Object.mbdyn_name = bpy.props.StringProperty()
        bpy.types.Object.hash = bpy.props.StringProperty()
    @classmethod
    def unregister(cls):
        for klass in cls.klasses:
            bpy.utils.unregister_class(klass)
        bpy.app.handlers.save_pre.append(save_pre)
        bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
        bpy.app.handlers.scene_update_post.remove(scene_update_post)
        bpy.app.handlers.load_post.remove(load_post)
        del bpy.types.Scene.pickled_database
        del bpy.types.Scene.dirty_simulator
        del bpy.types.Scene.hash
        del bpy.types.Scene.clean_log
        del bpy.types.Scene.mbdyn_default_orientation
        del bpy.types.Scene.mbdyn_name
        del bpy.types.Scene.popups_enabled
        del bpy.types.Object.mbdyn_name
        del bpy.types.Object.hash

class Entity:
    def __init__(self, name):
        self.type = name
    def safe_name(self):
        return "_".join("_".join(self.name.split(".")).split())
    def edit(self):
        exec("bpy.ops." + root_dot + "e_" + "_".join(self.type.lower().split()) + "('INVOKE_DEFAULT')")
    def write(self, f):
        f.write("\t" + self.type + ".write(): FIXME please\n")
    def string(self):
        return self.type + ".string(): FIXME please\n"
    def remesh(self):
        pass
    def duplicate(self):
        dup = type(self)(self.type)
        for key, value in vars(self).items():
            dup.__dict__[key] = value if isinstance(value, Entity) else copy(value)
        return dup
    def rigid_offset(self, i):
        if self.objects[i] in database.node:
            ob = self.objects[i]
        elif self.objects[i] in database.rigid_dict:
            ob = database.rigid_dict[self.objects[i]]
        else:
            name = self.objects[i].name
            bpy.context.window_manager.popup_menu(lambda self, c: self.layout.label(
                "Object " + name + " is not associated with a Node"),
                title="MBDyn Error", icon='ERROR')
            raise Exception("***Model Error: Object " + name + " is not associated with a Node")
        rot = ob.matrix_world.to_quaternion().to_matrix().transposed()
        globalV = self.objects[i].matrix_world.translation - ob.matrix_world.translation
        return rot, globalV, ob
    def write_node(self, f, i, node=False, position=False, orientation=False, p_label="", o_label=""):
        rot_i, globalV_i, Node_i = self.rigid_offset(i)
        localV_i = rot_i*globalV_i
        rot = self.objects[i].matrix_world.to_quaternion().to_matrix()
        if node:
            f.write(",\n\t\t" + safe_name(Node_i.name))
        if position:
            f.write(",\n\t\t\t")
            if p_label:
                f.write(p_label + ", ")
            write_vector(f, localV_i, prepend=False)
        if orientation:
            if o_label:
                f.write(",\n\t\t\t" + o_label)
            write_orientation(f, rot_i*rot, "\t\t\t")

class SegmentList(list):
    def __init__(self, l=list()):
        super().__init__(l)
    def clear(self):
        for item in self:
            if isinstance(item, Entity) and hasattr(item, "consumer"):
                del item.consumer
        super().clear()
    def append(self, item):
        item.consumer = True
        super().append(item)

class SelectedObjects(list):
    def __init__(self, context):
        self.extend([o for o in context.selected_objects if o.type == 'MESH'])
        active = context.active_object if context.active_object in self else None
        if active:
            self.remove(active)
            self.insert(0, active)
        else:
            self.clear()

class Operator:
    basis = None
    def general_data_exists(self, context):
        if enum_definition(self, context, "General data") == [("New", "New", "")]:
            exec("bpy.ops." + root_dot + "c_general_data()")
    def output_data_exists(self, context):
        if enum_definition(self, context, "Output data") == [("New", "New", "")]:
            exec("bpy.ops." + root_dot + "c_output_data()")
    def job_control_exists(self, context):
        if enum_definition(self, context, "Job control") == [("New", "New", "")]:
            exec("bpy.ops." + root_dot + "c_job_control()")
    def default_output_exists(self, context):
        if enum_definition(self, context, "Default output") == [("New", "New", "")]:
            exec("bpy.ops." + root_dot + "c_default_output()")
    def meter_drive_exists(self, context):
        if enum_drive(self, context, "Meter drive") == [("New", "New", "")]:
            exec("bpy.ops." + root_dot + "c_meter_drive()")
    def draw_panel_pre(self, context, layout):
        pass
    def draw_panel_post(self, context, layout):
        pass
    def prereqs(self, context):
        pass
    def assign(self, context):
        pass
    def store(self, context):
        pass
    def pre_finished(self, context):
        pass
    def draw(self, context):
        pass

class TreeMenu(list):
    def __init__(self, tree):
        self.branches = OrderedDict()
        self.menu_maker(tree)
    def menu_maker(self, tree):
        for key, value in tree.items():
            if isinstance(value, OrderedDict):
                self.menu_maker(value)
                self.branches[key] = value
                branches = self.branches
                class Menu(bpy.types.Menu):
                    bl_label = key
                    bl_description = " ".join(["New", key, "Menu"])
                    bl_idname = root_dot + "_".join(key.lower().split())
                    def draw(self, context):
                        layout = self.layout
                        layout.operator_context = 'INVOKE_DEFAULT'
                        for k, v in branches[self.bl_label].items():
                            if isinstance(v, OrderedDict):
                                layout.menu(root_dot + "_".join(k.lower().split()))
                            else:
                                layout.operator(root_dot + "c_" + "_".join(k.lower().split()), icon='OUTLINER_OB_MESH' if v == (len(SelectedObjects(context)) + 1) else 'NONE')
                self.append(Menu)
            
    def register(self):
        for klass in self:
            bpy.utils.register_class(klass)
    def unregister(self):
        for klass in self:
            bpy.utils.unregister_class(klass)

class Operators(list):
    def __init__(self, klasses, entity_list):
        for item, klass in klasses.items():
            name = item
            klass.module = klass.__module__.split(".")[1]
            class Help(bpy.types.Operator):
                bl_idname = root_dot + "h_" + "_".join(name.lower().split())
                bl_options = {'REGISTER', 'INTERNAL'}
                bl_label = "Help"
                bl_description = "Help for " + name
                url = bpy.props.StringProperty(default="help/index.html#"+"_".join(name.lower().split()))
                def execute(self, context):
                    directory = os.path.dirname(os.path.realpath(__file__))
                    webbrowser.open("/".join(["file:/", directory, self.url]))
                    return {'FINISHED'}
            class Create(bpy.types.Operator, klass):
                bl_idname = root_dot + "c_" + "_".join(name.lower().split())
                bl_description = " ".join(["Create:", name, "instance"])
                bl_options = {'REGISTER', 'INTERNAL'}
                entity_name = bpy.props.StringProperty(name="Name")
                def invoke(self, context, event):
                    context.scene.popups_enabled = False
                    self.prereqs(context)
                    self.entity = self.create_entity()
                    self.entity_name = self.name
                    context.scene.popups_enabled = True
                    return context.window_manager.invoke_props_dialog(self)
                def execute(self, context):
                    if not hasattr(self, "entity"):
                        self.prereqs(context)
                        self.entity = self.create_entity()
                        self.entity_name = self.name
                    try:
                        self.store(context)
                    except EntityLookupError:
                        self.report({'ERROR'}, "Incomplete (click on each 'New' selector)")
                        return {'CANCELLED'}
                    index, uilist = self.get_uilist(context)
                    index = len(uilist)
                    uilist.add()
                    self.set_index(context, index)
                    entity_list.append(self.entity)
                    uilist[index].name = self.entity_name
                    context.scene.dirty_simulator = True
                    self.set_index(context, index)
                    del self.entity
                    self.pre_finished(context)
                    return {'FINISHED'}
                def draw(self, context):
                    row = self.layout.row()
                    row.prop(self, "entity_name")
                    row.operator(root_dot + "h_" + self.bl_idname[len(root_dot)+5:], icon='QUESTION', text="")
                    super().draw(context)
            class Edit(bpy.types.Operator, klass):
                bl_label = " ".join(["Edit:", name])
                bl_description = " ".join(["Edit:", name, "instance"])
                bl_idname = root_dot + "e_" + "_".join(name.lower().split())
                bl_options = {'REGISTER', 'INTERNAL'}
                entity_name = bpy.props.StringProperty(name="Name")
                def invoke(self, context, event):
                    context.scene.popups_enabled = False
                    self.prereqs(context)
                    self.index, self.uilist = self.get_uilist(context)
                    self.entity_name = self.uilist[self.index].name
                    self.entity = entity_list[self.index]
                    self.assign(context)
                    context.scene.popups_enabled = True
                    return context.window_manager.invoke_props_dialog(self)
                def execute(self, context):
                    context.scene.dirty_simulator = True
                    self.store(context)
                    self.set_index(context, self.index)
                    self.uilist[self.index].name = self.entity_name
                    del self.entity
                    self.pre_finished(context)
                    return {'FINISHED'}
                def draw(self, context):
                    row = self.layout.row()
                    row.prop(self, "entity_name")
                    row.operator(root_dot + "h_" + self.bl_idname[len(root_dot)+5:], icon='QUESTION', text="")
                    super().draw(context)
            class Duplicate(bpy.types.Operator, klass):
                bl_label = "Duplicate"
                bl_description = " ".join(["Duplicate:", name, "instance"])
                bl_idname = root_dot + "d_" + "_".join(name.lower().split())
                bl_options = {'REGISTER', 'INTERNAL'}
                @classmethod
                def poll(cls, context):
                    return True
                def execute(self, context):
                    index, uilist = self.get_uilist(context)
                    self.index = len(uilist)
                    uilist.add()
                    if hasattr(database, "to_be_duplicated"):
                        entity = database.to_be_duplicated.duplicate()
                    else:
                        entity = entity_list[index].duplicate()
                    entity_list.append(entity)
                    self.set_index(context, self.index)
                    uilist[self.index].name = entity.name
                    context.scene.dirty_simulator = True
                    if hasattr(database, "to_be_duplicated"):
                        del database.to_be_duplicated
                        database.dup = entity
                    return {'FINISHED'}
            class Users(bpy.types.Operator, klass):
                bl_label = "Users"
                bl_description = " ".join(["Users of:", name, "instance"])
                bl_idname = root_dot + "s_" + "_".join(name.lower().split())
                bl_options = {'REGISTER', 'INTERNAL'}
                entity_names = bpy.props.CollectionProperty(type=BPY.Str)
                @classmethod
                def poll(cls, context):
                    return True
                def invoke(self, context, event):
                    self.entity_names.clear()
                    self.index, uilist = self.get_uilist(context)
                    self.users = database.users_of(entity_list[self.index])
                    for user in self.users:
                        name = self.entity_names.add()
                        name.value = user.name
                    return context.window_manager.invoke_props_dialog(self)
                def execute(self, context):
                    for name, user in zip(self.entity_names, self.users):
                        if name.select:
                            exec("bpy.ops." + root_dot + "e_" + "_".join(user.type.lower().split()) + "('INVOKE_DEFAULT')")
                    del self.users
                    return {'FINISHED'}
                def draw(self, context):
                    layout = self.layout
                    for name in self.entity_names:
                        row = layout.row()
                        row.prop(name, "select", text="", toggle=True)
                        row.label(name.value)
                def check(self, context):
                    return False
            class Unlink(bpy.types.Operator, klass):
                bl_label = "Unlink"
                bl_idname = root_dot + "u_" + "_".join(name.lower().split())
                bl_options = {'REGISTER', 'INTERNAL'}
                @classmethod
                def poll(cls, context):
                    return hasattr(database, "to_be_unlinked")
                def execute(self, context):
                    self.set_index(context, entity_list.index(database.to_be_unlinked))
                    del database.to_be_unlinked
                    index, uilist = self.get_uilist(context)
                    uilist.remove(index)
                    entity = entity_list.pop(index)
                    context.scene.dirty_simulator = True
                    self.set_index(context, 0 if index == 0 and 0 < len(uilist) else index-1)
                    return{'FINISHED'}
            class Link(bpy.types.Operator, klass):
                bl_idname = root_dot + "l_" + "_".join(name.lower().split())
                bl_options = {'REGISTER', 'INTERNAL'}
                @classmethod
                def poll(cls, context):
                    return hasattr(database, "to_be_linked")
                def execute(self, context):
                    index, uilist = self.get_uilist(context)
                    self.index = len(uilist)
                    uilist.add()
                    self.set_index(context, self.index)
                    entity_list.append(database.to_be_linked)
                    uilist[self.index].name = database.to_be_linked.name
                    del database.to_be_linked
                    context.scene.dirty_simulator = True
                    self.set_index(context, self.index)
                    return {'FINISHED'}
            class Menu(bpy.types.Menu, klass):
                bl_label = name
                bl_idname = root_dot + "m_" + "_".join(name.lower().split())
                bl_description = "Actions for the selected " + klass.module
                def draw(self, context):
                    layout = self.layout
                    layout.operator_context = 'INVOKE_DEFAULT'
                    layout.operator(root_dot + "e_" + self.bl_idname[len(root_dot)+2:])
                    layout.operator(root_dot + "s_" + self.bl_idname[len(root_dot)+2:])
                    if self.module != "element" and self.bl_label != "Reference frame":
                        layout.operator(root_dot + "d_" + self.bl_idname[len(root_dot)+2:])
                    if self.module in "element".split():
                        layout.operator(root_dot + "plot_element")
            self.extend([Help, Create, Edit, Duplicate, Users, Unlink, Link, Menu])
    def register(self):
        for klass in self:
            bpy.utils.register_class(klass)
    def unregister(self):
        for klass in self:
            bpy.utils.unregister_class(klass)

class UI(list):
    def __init__(self, entity_tree, klass, entity_list):
        module = klass.__module__.split(".")[1]
        menu = root_dot + "_".join(list(entity_tree.keys())[0].lower().split())
        self.make_list = klass.make_list
        self.delete_list = klass.delete_list
        def segments_maker(base, branch):
            segments = OrderedDict()
            for i in range(len(branch)):
                if isinstance(branch[i], list):
                    if not [item for item in branch[i] if isinstance(item, list)]:
                        segments[branch[i-1]] = [item for item in branch[i]]
                    segments.update(segments_maker(branch[i-1], branch[i]))
                elif len(branch) <= i+1 or not isinstance(branch[i+1], list) :
                    item = branch[i]
                    segments[item] = [item]
            return segments
        klass.types_dict = OrderedDict()
        for key, value in [v for v in entity_tree.values()][0].items():
            if isinstance(value, Tree):
                leaves = value.get_leaves()
                klass.types_dict[key] = leaves
                for leaf in leaves:
                    klass.types_dict[leaf] = [leaf]
            else:
                klass.types_dict[key] = [key]
        #klass.types_dict.update(segments_maker(entity_tree[0], entity_tree[1]))
        enum_types = [("All", "All", "All types", 'NONE', 0)] + [(key, key, ", ".join(value), ('RIGHTARROW_THIN' if 1 < len(value) else 'NONE'), i+1) for i, (key, value) in enumerate(klass.types_dict.items())]
        klass.types_dict["All"] = None
        class ListItem(bpy.types.PropertyGroup, klass):
            def update(self, context):
                index, uilist = self.get_uilist(context)
                entities = database.all_entities()
                entities.remove(entity_list[index])
                names = [e.name for e in entities] + ["New"]
                name = "_".join(uilist[index].name.split())
                if name.split(".")[0] == "Node":
                    name = "Not_a_Node"
                if name in names or name != uilist[index].name or (3 < len(name) and name[-4] == " " and name[-3:].isdigit()):
                    while 3 < len(name) and name[-3:].isdigit() and (
                        name[-4] == " " or (name in names and name[-4] == ".")):
                        name = name[:-4]
                    if name in names:
                        name += "." + str(1).zfill(3)
                    qty = 1
                    while name in names:
                        qty += 1
                        name = name[:-4] + "." + str(qty).zfill(3)
                        if qty >=999:
                            raise ValueError(name)
                    uilist[index].name = name
                entity_list[index].name = name
            name = bpy.props.StringProperty(update=update)
        class UIList(bpy.types.UIList, klass):
            bl_idname = module
            types = bpy.props.EnumProperty(items=enum_types, name="", description="Show only items of this type")
            use_filter_consumed = bpy.props.BoolProperty(name="", description="Show consumed items", default=False)
            filter_name = bpy.props.StringProperty(name="", description="Only show items containing this string")
            def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
                layout.prop(item, "name", text="", emboss=False)
            def filter_items(self, context, data, prop):
                filter_types = self.types_dict[self.types]
                uilist = getattr(data, prop)
                entity_list.flags = [True]*len(uilist)
                for i, entity in enumerate(entity_list):
                    if ((not self.use_filter_consumed and hasattr(entity, "consumer"))
                        or self.filter_name not in entity.name
                        or (filter_types and entity.type not in filter_types)):
                        entity_list.flags[i] = False
                order = [i for i in range(len(uilist))]
                entity_list.use_filter_sort_alpha = False
                if self.use_filter_sort_alpha:
                    order.sort(key=lambda i: uilist[i].name)
                    entity_list.use_filter_sort_alpha = True
                bitflags = [b for b in map(lambda f: self.bitflag_filter_item if f else ~self.bitflag_filter_item, entity_list.flags)]
                if self.use_filter_invert:
                    entity_list.flags = [not f for f in entity_list.flags]
                return bitflags, order
            def draw_filter(self, context, layout):
                row = layout.row()
                align = row.row(True)
                column = align.column(True)
                colrow = column.row(True)
                colrow.prop(self, "filter_name", text="")
                colrow.prop(self, "use_filter_invert", icon_only=True, icon='ZOOM_IN')
                colrow = column.row(True)
                colrow.prop(self, "types")
                if self.bl_idname == "element":
                    colrow.prop(self, "use_filter_consumed", icon_only=True, icon='PLUS')
                align = row.column(True)
                align.prop(self, "use_filter_sort_alpha", icon_only=True)
                align.prop(self, "use_filter_sort_reverse", icon_only=True, icon='TRIA_DOWN')
        class Help(bpy.types.Operator):
            bl_idname = module + ".help"
            bl_options = {'REGISTER', 'INTERNAL'}
            bl_label = "Help"
            bl_description = "Help for " + klass.bl_label
            url = bpy.props.StringProperty(default="help/index.html#"+module)
            def execute(self, context):
                directory = os.path.dirname(os.path.realpath(__file__))
                webbrowser.open("/".join(["file:/", directory, self.url]))
                return {'FINISHED'}
        class Delete(bpy.types.Operator, klass):
            bl_idname = module + ".delete"
            bl_options = {'REGISTER', 'INTERNAL'}
            bl_label = "Delete"
            bl_description = "Delete the selected " + module
            @classmethod
            def poll(self, context):
                index, uilist = super().get_uilist(context)
                return len(uilist) > 0 and getrefcount(entity_list[index]) == 2 and entity_list.flags[index]
            def execute(self, context):
                index, uilist = self.get_uilist(context)
                uilist.remove(index)
                entity = entity_list.pop(index)
                for attr in vars(entity).values():
                    if isinstance(attr, SegmentList):
                        attr.clear()
                if hasattr(entity, "objects"):
                    Cube(entity.objects[0])
                    for ob in entity.objects:
                        if ob.parent in entity.objects:
                            ob.parent = None
                context.scene.dirty_simulator = True
                self.set_index(context, 0 if index == 0 and 0 < len(uilist) else index-1)
                index, uilist = self.get_uilist(context)
                if -1 < index:
                    entity_list[index].remesh()
                return{'FINISHED'}
        class MoveUp(bpy.types.Operator, klass):
            bl_idname = module + ".move_up"
            bl_options = {'REGISTER', 'INTERNAL'}
            bl_label = "Move up"
            bl_description = "Move up the selected " + module
            @classmethod
            def poll(self, context):
                index, uilist = super().get_uilist(context)
                return len(uilist) > 0 and entity_list.flags[index]
            def execute(self, context):
                index, uilist = self.get_uilist(context)
                flagged = [i for i, v in enumerate(entity_list.flags) if v]
                up = flagged[flagged.index(index) - 1]
                entity_list.move(index, up)
                uilist[index].name = entity_list[index].name
                uilist[up].name = entity_list[up].name
                context.scene.dirty_simulator = True
                self.set_index(context, up)
                return{'FINISHED'}
        class MoveDown(bpy.types.Operator, klass):
            bl_idname = module + ".move_down"
            bl_options = {'REGISTER', 'INTERNAL'}
            bl_label = "Move down"
            bl_description = "Move down the selected " + module
            @classmethod
            def poll(self, context):
                index, uilist = super().get_uilist(context)
                return len(uilist) > 0 and entity_list.flags[index]
            def execute(self, context):
                index, uilist = self.get_uilist(context)
                flagged = [i for i, v in enumerate(entity_list.flags) if v]
                down = flagged[(flagged.index(index) + 1) % len(flagged)]
                entity_list.move(index, down)
                uilist[index].name = entity_list[index].name
                uilist[down].name = entity_list[down].name
                context.scene.dirty_simulator = True
                self.set_index(context, down)
                return{'FINISHED'}
        class Panel(bpy.types.Panel, klass):
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'TOOLS'
            bl_category = category
            bl_idname = "_".join([category, module])
            @classmethod
            def poll(self, context):
                return True
            def draw(self, context):
                layout = self.layout
                self.draw_panel_pre(context, layout)
                scene = context.scene
                row = layout.row()
                row.template_list(module, module + "_list",
                    scene, module + "_uilist", scene, module + "_index" )
                col = row.column(align=True)
                col.menu(menu, icon='ZOOMIN', text="")
                col.operator(module + ".delete", icon='ZOOMOUT', text="")
                col.operator(module + ".help", icon='QUESTION', text="")
                index, uilist = self.get_uilist(context)
                if not entity_list.use_filter_sort_alpha:
                    col.operator(module + ".move_up", icon='TRIA_UP', text="")
                    col.operator(module + ".move_down", icon='TRIA_DOWN', text="")
                if 0 < len(uilist) and entity_list.flags[index]:
                    col.menu(root_dot + "m_" +
                        "_".join(entity_list[index].type.lower().split()), icon='DOWNARROW_HLT', text="")
                self.draw_panel_post(context, layout)
        self.extend([ListItem, UIList, Help, Delete, MoveUp, MoveDown, Panel])
    def register(self):
        for klass in self:
            bpy.utils.register_class(klass)
        self.make_list(self[0])
    def unregister(self):
        for klass in self:
            bpy.utils.unregister_class(klass)
        self.delete_list()

class Bundle(list):
    def __init__(self, tree, klass, klasses, entity_list):
        self.append(UI(tree, klass, entity_list))
        self.append(TreeMenu(tree))
        self.append(Operators(klasses, entity_list))
    def register(self):
        for ob in self:
            ob.register()
    def unregister(self):
        for ob in self:
            ob.unregister()
