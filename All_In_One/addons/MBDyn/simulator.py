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
    for x in [base, menu, common, user_defined_common]:
        imp.reload(x)
else:
    from . import base
    from . import menu
    from . import common
    from . import user_defined_common
from .base import bpy, BPY, root_dot, database, Operator, Entity, Bundle
from .common import FORMAT, safe_name, write_vector, write_orientation, StreamSender, StreamReceiver
from .menu import default_klasses, simulator_tree
from mathutils import Matrix
import subprocess
from tempfile import TemporaryFile
import os
from time import sleep
import sys
from signal import SIGTERM
import math
from mathutils import Vector, Euler, Quaternion

aerodynamic_types = [
    "Aerodynamic body",
    "Aerodynamic beam2",
    "Aerodynamic beam3",
    "Generic aerodynamic force",
    "Induced velocity"]
beam_types = [
    "Beam segment",
    "Three node beam"]
force_types = [
    "Structural force",
    "Structural internal force",
    "Structural couple",
    "Structural internal couple",
    "Total force",
    "Total internal force"]
genel_types = [
    "Swashplate"]
joint_types = [
    "Axial rotation",
    "Clamp",
    "Distance",
    "Deformable displacement joint",
    "Deformable hinge",
    "Deformable joint",
    "In line",
    "In plane",
    "Revolute hinge",
    "Rod",
    "Spherical hinge",
    "Total joint",
    "Viscous body"]
output_types = [
    "Stream animation",
    "Stream output"]
environment_types = [
    "Air properties",
    "Gravity"]
node_types = [
    "Rigid offset",
    "Dummy node",
    "Feedback node"]

rigid_body_types = ["Body"]

structural_static_types = aerodynamic_types + joint_types + ["Rotor"] + beam_types + force_types

structural_dynamic_types = rigid_body_types

class Base(Operator):
    bl_label = "Simulators"
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.simulator_uilist = bpy.props.CollectionProperty(type = ListItem)
        def update(self, context):
            if database.simulator and self.simulator_index < len(database.simulator):
                exec("bpy.ops." + root_dot + "save('INVOKE_DEFAULT')")
        bpy.types.Scene.simulator_index = bpy.props.IntProperty(default=-1, update=update)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.simulator_uilist
        del bpy.types.Scene.simulator_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.simulator_index, context.scene.simulator_uilist
    def set_index(self, context, value):
        context.scene.simulator_index = value
    def prereqs(self, context):
        pass
    def draw_panel_post(self, context, layout):
        if context.scene.dirty_simulator:
            layout.label("Choose a simulator")
        else:
            layout.operator(root_dot + "simulate")
            if context.scene.clean_log:
                layout.operator(root_dot + "write_keyframes")

klasses = default_klasses(simulator_tree, Base)

class InitialValue(Entity):
    def write_input_file(self, context, directory):
        def write_structural_node(f, structural_type, node, frame):
            f.write("\tstructural: " + ", ".join([safe_name(node.name), structural_type]))
            frame_label = frame.safe_name() if frame else "global"
            location, orientation = node.matrix_world.translation, node.matrix_world.to_quaternion().to_matrix()
            if frame:
                orientation = frame.objects[0].matrix_world.to_quaternion().to_matrix().transposed()*orientation
                location = orientation * (location - frame.objects[0].matrix_world.translation)
            f.write(",\n\t\treference, " + frame_label)
            write_vector(f, location)
            f.write(",\n\t\treference, " + frame_label)
            write_orientation(f, orientation, "\t\t")
            f.write(",\n\t\treference, " + frame_label + ", null" +
                ",\n\t\treference, " + frame_label + ", null;\n")
        with open(os.path.join(directory, context.scene.name + ".mbd"), "w") as f:
            f.write("# MBDyn v1.7 input file generated using BlenderAndMBDyn v2.0\n\n")
            frame_for, frames, parent_of = dict(), list(), dict()
            reference_frames = database.input_card.filter("Reference frame")
            for frame in reference_frames:
                frame_for.update({ob : frame for ob in frame.objects[1:]})
                frames.append(frame)
                parent_of.update({frame : parent for parent in reference_frames if frame.objects[0] in parent.objects[1:]})
            frames_to_write = list()
            while frames:
                frame = frames.pop()
                if frame in parent_of and parent_of[frame] in frames:
                    frames.appendleft(frame)
                else:
                    frames_to_write.append(frame)
            if frames_to_write:
                f.write("# Frame labels:\n")
                for i, frame in enumerate(sorted(frames_to_write, key=lambda x: x.name)):
                    f.write("\tset: const integer " + safe_name(frame.name) + " = " + str(i) + ";\n")
            else:
                f.write("# Frame labels: none\n")
            nodes = set()
            dummy_dict = dict()
            structural_dynamic_nodes = set()
            structural_static_nodes = set()
            structural_dummy_nodes = set()
            database.rigid_dict = {e.objects[0] : e.objects[1] for e in database.element.filter("Rigid offset") + database.element.filter(user_defined_common.offset_types)}
            names = [e.name for e in database.all_entities()]
            for e in (e for e in database.element + database.drive if hasattr(e, "objects")):
                ob = database.rigid_dict[e.objects[0]] if e.objects[0] in database.rigid_dict else e.objects[0]
                if ob.name in names:
                    ob.name = "Node"
                nodes |= set([ob])
                if e.type in structural_dynamic_types + user_defined_common.structural_dynamic_types:
                    structural_dynamic_nodes |= set([ob])
                elif e.type in structural_static_types + user_defined_common.structural_static_types:
                    structural_static_nodes |= set([ob])
                elif e.type == "Dummy":
                    structural_dummy_nodes |= set([ob])
                    dummy_dict[ob] = e.objects[1]
            structural_static_nodes -= structural_dynamic_nodes | structural_dummy_nodes
            database.node.clear()
            database.node.extend(sorted(nodes, key=lambda x: x.name))
            if database.node:
                f.write("\n# Node labels:\n")
                for i, node in enumerate(database.node):
                    f.write("\tset: const integer " + safe_name(node.name) + " = " + str(i) + ";\n")
            else:
                f.write("\n# Node labels: none\n")
            if database.element:
                f.write("\n# Element labels:\n")
                for i, element in enumerate(sorted(database.element, key=lambda x: x.name)):
                    f.write("\tset: const integer " + element.safe_name() + " = " + str(i) + ";\n")
            else:
                f.write("\n# Element labels: none\n")
            if database.drive:
                f.write("\n# Drive labels:\n")
                for i, drive in enumerate(sorted(database.drive, key=lambda x: x.name)):
                    f.write("\tset: const integer " + drive.safe_name() + " = " + str(i) + ";\n")
            else:
                f.write("\n# Drive labels: none\n")
            if database.driver:
                f.write("\n# Driver labels:\n")
                for i, driver in enumerate(sorted(database.driver, key=lambda x: x.name)):
                    f.write("\tset: const integer " + driver.safe_name() + " = " + str(i) + ";\n")
            else:
                f.write("\n# Driver labels: none\n")
            if database.constitutive:
                f.write("\n# Constitutive labels:\n")
                for i, constitutive in enumerate(sorted(database.constitutive, key=lambda x: x.name)):
                    f.write("\tset: const integer " + constitutive.safe_name() + " = " + str(i) + ";\n")
            else:
                f.write("\n# Constitutive labels: none\n")
            set_cards = database.input_card.filter("Set")
            if set_cards:
                f.write("\n# Parameters:\n")
                for set_card in set_cards:
                    set_card.write(f)
            else:
                f.write("\n# Parameters: none\n")
            module_load_cards = database.input_card.filter("Module load")
            if module_load_cards:
                f.write("\n# Modules:\n")
                for module_load_card in module_load_cards:
                    module_load_card.write(f)
            else:
                f.write("\n# Modules: none\n")
            structural_node_count = len(structural_static_nodes | structural_dynamic_nodes | structural_dummy_nodes)
            joint_count = len([e for e in database.element if e.type in joint_types])
            output_count = len([e for e in database.element if e.type in output_types])
            force_count = len([e for e in database.element if e.type in force_types])
            rigid_body_count = len([e for e in database.element if e.type in rigid_body_types])
            aerodynamic_element_count = len([e for e in database.element if e.type in aerodynamic_types])
            rotor_count = len([e for e in database.element if e.type in ["Rotor"]])
            genel_count = len([e for e in database.element if e.type in genel_types])
            beam_count = len([e for e in database.element if e.type in beam_types and not hasattr(e, "consumer")])
            air_properties = bool([e for e in database.element if e.type in ["Air properties"]])
            gravity = bool([e for e in database.element if e.type in ["Gravity"]])
            loadable_element_count = len([e for e in database.element if e.type in user_defined_common.loadable_element_types])
            file_driver_count = len(database.driver)
            bailout_upper = False
            upper_bailout_time = 0.0
#            electric_node_count = len([e for e in database.ns_node if e.type in ["Electric"]])
#            abstract_node_count = len([e for e in database.ns_node if e.type in ["Abstract"]])
#            hydraulic_node_count = len([e for e in database.ns_node if e.type in ["Hydraulic"]])
#            parameter_node_count = len([e for e in database.ns_node if e.type in ["Parameter"]])
            f.write(
                "\nbegin: data" +
                ";\n\tproblem: initial value" +
                ";\nend: data" +
                ";\n\nbegin: initial value" +
                ";\n\tinitial time: " + (BPY.FORMAT(self.initial_time) if self.initial_time is not None else "0") +
                ";\n\tfinal time: " + (BPY.FORMAT(self.final_time) if self.final_time is not None else "forever") +
                ";\n")
            for a in [self.general_data, self.method, self.nonlinear_solver, self.eigenanalysis, self.abort_after, self.linear_solver, self.dummy_steps, self.output_data, self.real_time]:
                if a is not None:
                    a.write(f)
            f.write("end: initial value;\n" +
                "\nbegin: control data;\n")
            for a in [self.assembly, self.job_control, self.default_output, self.default_aerodynamic_output, self.default_beam_output]:
                if a is not None:
                    a.write(f)
            if structural_node_count:
                f.write("\tstructural nodes: " + str(structural_node_count) + ";\n")
            """
            if electric_node_count:
                f.write("\telectric nodes: " + str(electric_node_count) + ";\n")
            if abstract_node_count:
                f.write("\tabstract nodes: " + str(abstract_node_count) + ";\n")
            if hydraulic_node_count:
                f.write("\thydraulic nodes: " + str(hydraulic_node_count) + ";\n")
            """
            if joint_count:
                f.write("\tjoints: " + str(joint_count) + ";\n")
            if output_count:
                f.write("\toutput elements: " + str(output_count) + ";\n")
            if force_count:
                f.write("\tforces: " + str(force_count) + ";\n")
            if genel_count:
                f.write("\tgenels: " + str(genel_count) + ";\n")
            if beam_count:
                f.write("\tbeams: " + str(beam_count) + ";\n")
            if rigid_body_count:
                f.write("\trigid bodies: " + str(rigid_body_count) + ";\n")
            if air_properties:
                f.write("\tair properties;\n")
            if gravity:
                f.write("\tgravity;\n")
            if aerodynamic_element_count:
                f.write("\taerodynamic elements: " + str(aerodynamic_element_count) + ";\n")
            if rotor_count:
                f.write("\trotors: " + str(rotor_count) + ";\n")
            if file_driver_count:
                f.write("\tfile drivers: " + str(file_driver_count) + ";\n")
            if loadable_element_count:
                f.write("\tloadable elements: " + str(loadable_element_count) + ";\n")
            f.write("end: control data;\n")
            if frames_to_write:
                f.write("\n# Frames:\n")
                for frame in frames_to_write:
                    frame.write(f, parent_of[frame] if frame in parent_of else None)
            if database.node:
                f.write("\nbegin: nodes;\n")
                for node in structural_static_nodes:
                    write_structural_node(f, "static", node, frame_for[node] if node in frame_for else None)
                for node in structural_dynamic_nodes:
                    write_structural_node(f, "dynamic", node, frame_for[node] if node in frame_for else None)
                for node in structural_dummy_nodes:
                    base_node = dummy_dict[node]
                    rot = base_node.matrix_world.to_quaternion().to_matrix()
                    globalV = node.matrix_world.translation - base_node.matrix_world.translation
                    localV = rot*globalV
                    rotT = node.matrix_world.to_quaternion().to_matrix()
                    f.write("\tstructural: " + str(database.node.index(node)) + ", dummy,\n\t\t" +
                        str(database.node.index(base_node)) + ", offset,\n\t\t\t")
                    write_vector(f, localV, prepend=False)
                    write_orientation(f, rot*rotT, "\t\t\t")
                    f.write(";\n")
                """
                for i, ns_node in enumerate(self.ns_node):
                    if ns_node.type == "Electric":
                        f.write("\telectric: " + str(i) + ", value, " + str(ns_node._args[0]))
                        if ns_node._args[1]: f.write(", derivative, " + str(ns_node._args[2]))
                        f.write(";\n")
                    if ns_node.type == "Abstract":
                        f.write("\tabstract: " + str(i) + ", value, " + str(ns_node._args[0]))
                        if ns_node._args[1]: f.write(", differential, " + str(ns_node._args[2]))
                        f.write(";\n")
                    if ns_node.type == "Hydraulic":
                        f.write("\thydraulic: " + str(i) + ", value, " + str(ns_node._args[0]) + ";\n")
                """
                f.write("end: nodes;\n")
            if file_driver_count:
                f.write("\nbegin: drivers;\n")
                for driver in database.driver:
                    driver.write(f)
                f.write("end: drivers;\n")
            if database.function:
                f.write("\n# Functions:\n")
                for function in sorted(database.function, key=lambda x: x.name):
                    function.write(f)
            if database.drive:
                f.write("\n# Drives:\n")
                for drive in database.drive:
                    if drive.dimension == "1D":
                        f.write("\tdrive caller: " + ", ".join([drive.safe_name(), drive.string()]) + ";\n")
                    else:
                        dim_name = {"3D": "\"3\"", "6D": "\"6\"", "3x3": "\"3x3\"", "6x6": "\"6x6\""}[drive.dimension]
                        f.write("\ttemplate drive caller: " + ", ".join([drive.safe_name(), dim_name, drive.string()]) + ";\n")
            if database.constitutive:
                f.write("\n# Constitutives:\n")
                for constitutive in database.constitutive:
                    f.write("\tconstitutive law: " + ", ".join([constitutive.safe_name(), constitutive.dimension[0], constitutive.string()]) + ";\n")
            if database.element:
                f.write("\nbegin: elements;\n")
                try:
                    for element_type in aerodynamic_types + beam_types + ["Body"] + force_types + genel_types + joint_types + ["Rotor"] + environment_types + user_defined_common.loadable_element_types + ["Driven"] + output_types:
                        for element in database.element:
                            if element.type == element_type:
                                element.write(f)
                except Exception as e:
                    print(e)
                    f.write(str(e) + "\n")
                f.write("end: elements;\n")
            del database.rigid_dict
            del dummy_dict

class InitialValueOperator(Base):
    bl_label = "Initial value"
    mbdyn_path = bpy.props.PointerProperty(type=BPY.Str)
    initial_time = bpy.props.PointerProperty(type=BPY.Float)
    final_time = bpy.props.PointerProperty(type=BPY.Float)
    general_data = bpy.props.PointerProperty(type=BPY.Definition)
    method = bpy.props.PointerProperty(type=BPY.Definition)
    nonlinear_solver = bpy.props.PointerProperty(type=BPY.Definition)
    eigenanalysis = bpy.props.PointerProperty(type=BPY.Definition)
    abort_after = bpy.props.PointerProperty(type=BPY.Definition)
    linear_solver = bpy.props.PointerProperty(type=BPY.Definition)
    dummy_steps = bpy.props.PointerProperty(type=BPY.Definition)
    output_data = bpy.props.PointerProperty(type=BPY.Definition)
    real_time = bpy.props.PointerProperty(type=BPY.Definition)
    assembly = bpy.props.PointerProperty(type=BPY.Definition)
    job_control = bpy.props.PointerProperty(type=BPY.Definition)
    default_output = bpy.props.PointerProperty(type=BPY.Definition)
    default_aerodynamic_output = bpy.props.PointerProperty(type=BPY.Definition)
    default_beam_output = bpy.props.PointerProperty(type=BPY.Definition)
    def prereqs(self, context):
        self.mbdyn_path.assign(BPY.mbdyn_path)
        self.final_time.select, self.final_time.value = True, 10.0
        self.general_data.type = "General data"
        self.general_data.mandatory = True
        self.general_data_exists(context)
        self.method.type = "Method"
        self.nonlinear_solver.type = "Nonlinear solver"
        self.eigenanalysis.type = "Eigenanalysis"
        self.abort_after.type = "Abort after"
        self.linear_solver.type = "Linear solver"
        self.dummy_steps.type = "Dummy steps"
        self.output_data.type = "Output data"
        self.output_data.mandatory = True
        self.output_data_exists(context)
        self.real_time.type = "Real time"
        self.assembly.type = "Assembly"
        self.job_control.type = "Job control"
        self.job_control.mandatory = True
        self.job_control_exists(context)
        self.default_output.type = "Default output"
        self.default_output.mandatory = True
        self.default_output_exists(context)
        self.default_aerodynamic_output.type = "Default aerodynamic output"
        self.default_beam_output.type = "Default beam output"
    def assign(self, context):
        self.mbdyn_path.assign(self.entity.mbdyn_path)
        self.initial_time.assign(self.entity.initial_time)
        self.final_time.assign(self.entity.final_time)
        self.general_data.assign(self.entity.general_data)
        self.method.assign(self.entity.method)
        self.nonlinear_solver.assign(self.entity.nonlinear_solver)
        self.eigenanalysis.assign(self.entity.eigenanalysis)
        self.abort_after.assign(self.entity.abort_after)
        self.linear_solver.assign(self.entity.linear_solver)
        self.dummy_steps.assign(self.entity.dummy_steps)
        self.output_data.assign(self.entity.output_data)
        self.real_time.assign(self.entity.real_time)
        self.assembly.assign(self.entity.assembly)
        self.job_control.assign(self.entity.job_control)
        self.default_output.assign(self.entity.default_output)
        self.default_aerodynamic_output.assign(self.entity.default_aerodynamic_output)
        self.default_beam_output.assign(self.entity.default_beam_output)
    def store(self, context):
        self.entity.mbdyn_path = BPY.mbdyn_path = self.mbdyn_path.store()
        self.entity.initial_time = self.initial_time.store()
        self.entity.final_time = self.final_time.store()
        self.entity.general_data = self.general_data.store()
        self.entity.method = self.method.store()
        self.entity.nonlinear_solver = self.nonlinear_solver.store()
        self.entity.eigenanalysis = self.eigenanalysis.store()
        self.entity.abort_after = self.abort_after.store()
        self.entity.linear_solver = self.linear_solver.store()
        self.entity.dummy_steps = self.dummy_steps.store()
        self.entity.output_data = self.output_data.store()
        self.entity.real_time = self.real_time.store()
        self.entity.assembly = self.assembly.store()
        self.entity.job_control = self.job_control.store()
        self.entity.default_output = self.default_output.store()
        self.entity.default_aerodynamic_output = self.default_aerodynamic_output.store()
        self.entity.default_beam_output = self.default_beam_output.store()
    def pre_finished(self, context):
        exec("bpy.ops." + root_dot + "save('INVOKE_DEFAULT')")
    def draw(self, context):
        layout = self.layout
        self.mbdyn_path.draw(layout, "MBDyn path", "Set")
        self.initial_time.draw(layout, "Initial time")
        self.final_time.draw(layout, "Final time")
        self.general_data.draw(layout, "General data")
        self.method.draw(layout, "Method", "Set")
        self.nonlinear_solver.draw(layout, "Nonlinear solver", "Set")
        self.eigenanalysis.draw(layout, "Eigenanalysis", "Set")
        self.abort_after.draw(layout, "Abort after", "Set")
        self.linear_solver.draw(layout, "Linear solver", "Set")
        self.dummy_steps.draw(layout, "Dummy steps", "Set")
        self.output_data.draw(layout, "Output data", "Set")
        self.real_time.draw(layout, "Real time", "Set")
        self.assembly.draw(layout, "Assembly", "Set")
        self.job_control.draw(layout, "Job control", "Set")
        self.default_output.draw(layout, "Default output", "Set")
        self.default_aerodynamic_output.draw(layout, "Default aerodynamic output", "Set")
        self.default_beam_output.draw(layout, "Default beam output", "Set")
    def check(self, context):
        return (True in [x.check(context) for x in [self.mbdyn_path, self.initial_time, self.final_time, self.general_data, self.method, self.nonlinear_solver, self.eigenanalysis, self.abort_after, self.linear_solver, self.dummy_steps, self.output_data, self.real_time, self.assembly, self.default_output, self.default_aerodynamic_output, self.default_beam_output]])
    def create_entity(self):
        return InitialValue(self.name)

klasses[InitialValueOperator.bl_label] = InitialValueOperator

class Save(bpy.types.Operator, Base):
    bl_idname = root_dot + "save"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = "Save Blender File"
    filter_glob = bpy.props.StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            )
    filepath = bpy.props.StringProperty()
    def invoke(self, context, event):
        if not context.blend_data.filepath:
            self.filepath = "untitled.blend"
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        self.filepath = context.blend_data.filepath
        return self.execute(context)
    def execute(self, context):
        directory = os.path.splitext(self.filepath)[0]
        if not os.path.exists(directory):
            os.mkdir(directory)
        database.simulator[context.scene.simulator_index].write_input_file(context, directory)
        bpy.ops.object.select_all(action='DESELECT')
        for node in database.node:
            node.select = True
        bpy.ops.wm.save_mainfile(filepath=self.filepath)
        context.scene.dirty_simulator = False
        context.scene.clean_log = False
        return{'FINISHED'}
BPY.klasses.append(Save)

class Simulate(bpy.types.Operator, Base):
    bl_idname = root_dot + "simulate"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = "Run simulation"
    bl_description = "Run MBDyn for the input file"
    def modal(self, context, event):
        if not (event.type in ['ESC', 'TIMER'] or (hasattr(self, "channels") and event.type in self.channels)):
            return {'PASS_THROUGH'}
        if event.type == 'ESC':
            return self.close(context)
        #self.report({'INFO'}, self.process.stdout.read().decode())
        if hasattr(self, "sender") and event.type in self.channels:
            i, dv = self.channels[event.type]
            self.values[i] += dv
            try:
                self.sender.send(self.values)
            except BrokenPipeError:
                return self.close(context)
        if hasattr(self, "receiver"):
            data = self.receiver.get_data()
            for i, node in enumerate(self.nodes):
                node.location = Vector(data[12*i : 12*i+3])
                node.rotation_euler = Matrix([data[12*i+3 : 12*i+6], data[12*i+6 : 12*i+9], data[12*i+9 : 12*i+12]]).to_euler(node.rotation_euler.order)
        if self.process.poll() == None:
            if self.platform != "win32":
                output = subprocess.check_output(("tail", "-n", "1", self.out_file))
                if output and 2 < len(output.split()):
                    percent = 100.*(1.-(self.t_final - float(output.split()[2]))/self.t_range)
                    context.window_manager.progress_update(percent)
            return {'PASS_THROUGH'}
        else:
            return self.close(context)
    def close(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)
        if hasattr(self, "nodes"):
            for preserved, node in zip(self.preserve, self.nodes):
                node.location, node.rotation_euler = preserved
            del self.nodes
        try:
            stdout, stderr = self.process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            stdout, stderr = self.process.communicate()
        del self.process
        if stdout:
            self.report({'INFO'}, stdout.decode())
        if stderr:
            self.report({'INFO'}, stderr.decode())
        if hasattr(self, "receiver"):
            self.receiver.close()
        if hasattr(self, "sender"):
            self.sender.close()
        context.scene.clean_log = True
        context.scene.mbdyn_default_orientation = database.simulator[context.scene.simulator_index].job_control.default_orientation
        BPY.plot_data.clear()
        wm.progress_end()
        return {'FINISHED'}
    def execute(self, context):
        sim = database.simulator[context.scene.simulator_index]
        directory = os.path.splitext(context.blend_data.filepath)[0]
        command = [sim.mbdyn_path if sim.mbdyn_path is not None else "mbdyn", "-s", "-f", os.path.join(directory, context.scene.name + ".mbd")]
        self.report({'INFO'}, " ".join(command))
        animation = database.element.filter("Stream animation")
        events = database.driver.filter("Event stream")
        drives = database.drive.filter("Event drive")
        if drives:
            self.values = [d.initial_value for d in drives]
            self.channels = {d.increment : (i, 1) for i, d in enumerate(drives)}
            self.channels.update({d.decrement : (i, -1) for i, d in enumerate(drives)})
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if events:
            host_name, port_number = events[0].host_name, events[0].port_number
            self.sender = StreamSender(host_name=host_name, port_number=port_number)
            self.sender.send(self.values)
        if animation:
            host_name, port_number, self.nodes = animation[0].host_name, animation[0].port_number, animation[0].objects if hasattr(animation[0], "objects") else database.node
            self.preserve = [(n.location.copy(), n.rotation_euler.copy()) for n in self.nodes]
            initial_data = list()
            for v, e in self.preserve:
                initial_data.extend(v.to_tuple())
                for row in e.to_matrix():
                    initial_data.extend(row)
            self.receiver = StreamReceiver('d'*12*len(self.nodes), initial_data, host_name=host_name, port_number=port_number)
            if self.receiver.socket:
                self.receiver.start()
            else:
                self.report({'INFO'}, "Animation stream socket failed to connect")
                del self.receiver
        self.out_file = os.path.join(directory, context.scene.name + ".out")
        self.t_final = sim.final_time if sim.final_time is not None else float("inf")
        self.t_range = self.t_final - (sim.initial_time if sim.initial_time is not None else 0.0)
        while not os.path.exists(self.out_file):
            sleep(0.5)
        wm = context.window_manager
        wm.progress_begin(0., 100.)
        self.timer = wm.event_timer_add(1./24., context.window)
        wm.modal_handler_add(self)
        self.platform = sys.platform
        return{'RUNNING_MODAL'}
BPY.klasses.append(Simulate)

class FileWrapper:
    def __init__(self, file):
        self.file = file
        self.pos = 0
        self.size = self.file.seek(0, 2)
        self.file.seek(0, 0)
    def __next__(self):
        line = next(self.file)
        self.pos += len(line)
        return line
    def __iter__(self):
        line = next(self.file)
        while line:
            self.pos += len(line)
            yield line
            line = next(self.file)
    def close(self):
        self.file.close()
    def seek(self, *args, **kwargs):
        self.file.seek(*args, **kwargs)

class WriteKeyframes(bpy.types.Operator, Base):
    bl_idname = root_dot + "write_keyframes"
    bl_options = {'REGISTER', 'INTERNAL'}
    bl_label = "Write keyframes"
    bl_description = "Import each node's location and orientation into Blender keyframes starting at the next frame"
    steps = bpy.props.IntProperty(name="MBDyn steps between Blender keyframes", default=1, min=1)
    rate = bpy.props.IntProperty(name="Keyframes per MBDyn second", default=15, min=1)
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    def insert_keyframe(self, label, fields):
        database.node[label].location = fields[:3]
        if self.orientation == "orientation matrix":
            euler = Matrix([fields[3:6], fields[6:9], fields[9:12]]).to_euler()
            database.node[label].rotation_euler = euler[0], euler[1], euler[2]
        elif self.orientation == "euler321":
            database.node[label].rotation_euler = Euler((math.radians(fields[5]), math.radians(fields[4]), math.radians(fields[3])), 'XYZ')
        elif self.orientation == "euler123":
            database.node[label].rotation_euler = Euler((math.radians(fields[3]), math.radians(fields[4]), math.radians(fields[5])), 'ZYX').to_quaternion().to_euler('XYZ')
            #database.node[label].rotation_mode = 'ZYX'
        elif self.orientation == "orientation vector":
            #database.node[label].rotation_axis_angle = [math.sqrt(sum([x*x for x in fields[3:6]]))] + fields[3:6]
            database.node[label].rotation_euler = Quaternion(fields[3:6], math.sqrt(sum([x*x for x in fields[3:6]]))).to_euler('XYZ')
        for data_path in "location rotation_euler".split():
            database.node[label].keyframe_insert(data_path)
    def execute(self, context):
        self.orientation = database.simulator[context.scene.simulator_index].job_control.default_orientation
        if self.orientation == "euler313":
            self.report({'ERROR'}, "euler313 cannot be imported. Simulate in another format, selected from Job Control -> Default Orientation")
        scene = context.scene
        frame_initial = scene.frame_current
        wm = context.window_manager
        wm.progress_begin(0., 100.)
        directory = os.path.splitext(context.blend_data.filepath)[0]
        dt = 1.0 / self.rate
        keytime = - float("inf")
        parser = lambda l: (int(l[0]), [float(x) for x in l[1:]])
        with open(os.path.join(directory, scene.name + ".out")) as f_out, open(os.path.join(directory, scene.name + ".mov")) as f_mov:
            label, fields = parser(f_mov.readline().split())
            fw_out = FileWrapper(f_out)
            for step, time in map(lambda l: (int(l[1]), float(l[2])), map(str.split, filter(lambda ln: ln.startswith("Step"), fw_out))):
                is_a_keyframe = dt < time - keytime
                if is_a_keyframe:
                    keytime = time
                    scene.frame_current += 1
                    wm.progress_update(100. * float(fw_out.pos) / float(fw_out.size))
                labels = list()
                while f_mov and label not in labels:
                    if is_a_keyframe:
                        self.insert_keyframe(label, fields)
                    labels.append(label)
                    split_line = f_mov.readline().split()
                    if split_line:
                        label, fields = parser(split_line)
        for node in database.node:
            node.rotation_mode = 'XYZ'
        scene.frame_current = frame_initial + 1
        wm.progress_end()
        return{'FINISHED'}
    def draw(self, context):
        layout = self.layout
        #layout.label("File has " + str(int(self.N/(self.i+1))) + " timesteps.")
        layout.prop(self, "rate")
BPY.klasses.append(WriteKeyframes)

bundle = Bundle(simulator_tree, Base, klasses, database.simulator)
