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
    for x in [base, menu]:
        imp.reload(x)
else:
    from . import base
    from . import menu
from .base import bpy, BPY, database, Operator, Entity, Bundle
from .menu import default_klasses, driver_tree

class Base(Operator):
    bl_label = "Drivers"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.driver_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.driver_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.driver_uilist
        del bpy.types.Scene.driver_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.driver_index, context.scene.driver_uilist
    def set_index(self, context, value):
        context.scene.driver_index = value

klasses = default_klasses(driver_tree, Base)

class Stream(Entity):
    def write(self, f):
        columns = database.drive.filter("Event drive")
        f.write("\tfile: " + self.safe_name() + ", stream"
            ",\n\t\tname, " + BPY.FORMAT(self.stream_name) +
            ",\n\t\tcreate, " + ("yes" if self.create else "no"))
        if self.path is not None:
            f.write(",\n\t\tlocal, ", BPY.FORMAT(self.path))
        else:
            f.write((",\n\t\tport, " + BPY.FORMAT(self.port_number) if self.port_number is not None else "") +
                (",\n\t\thost, " + BPY.FORMAT(self.host_name) if self.host_name is not None else ""))
        f.write(",\n\t\t" + ("" if self.signal else "no ") + "signal" +
            ",\n\t\t" + ("" if self.blocking else "non ") + "blocking")
        f.write((",\n\t\tinput every, " + BPY.FORMAT(self.steps) if self.steps is not None else "") +
            (",\n\t\treceive first, " + ("yes" if self.receive_first else "no")) +
            (",\n\t\ttimeout, " + BPY.FORMAT(self.timeout) if self.timeout is not None else ""))
        if self.file_name is not None:
            f.write(",\n\t\techo, " + BPY.FORMAT(self.file_name) +
                (",\n\t\tprecision, " + BPY.FORMAT(self.precision) if self.precision is not None else "") +
                (",\n\t\tshift, " + BPY.FORMAT(self.shift) if self.shift is not None else ""))
        f.write(",\n\t\t" + str(len(columns)) + 
            (", initial values, " + ", ".join([str(c.initial_value) for c in columns]) if columns else ""))
        f.write(";\n")

class StreamOperator(Base):
    bl_label = "Stream"
    stream_name = bpy.props.PointerProperty(type = BPY.Str)
    create = bpy.props.BoolProperty(name="Create")
    path = bpy.props.PointerProperty(type = BPY.Str)
    port_number = bpy.props.PointerProperty(type = BPY.Int)
    host_name = bpy.props.PointerProperty(type = BPY.Str)
    signal = bpy.props.BoolProperty(name="Signal")
    blocking = bpy.props.BoolProperty(name="Blocking")
    steps = bpy.props.PointerProperty(type = BPY.Int)
    receive_first = bpy.props.BoolProperty(name="Receive first")
    timeout = bpy.props.PointerProperty(type = BPY.Float)
    file_name = bpy.props.PointerProperty(type = BPY.Str)
    precision = bpy.props.PointerProperty(type = BPY.Int)
    shift = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.stream_name.mandatory = True
        self.stream_name.value = "MAILIN"
        self.port_number.value = 9012
        self.port_number.select = True
        self.host_name.value = "127.0.0.1"
        self.host_name.select = True
        self.signal = False
        self.blocking = False
        self.steps.value = 1
    def assign(self, context):
        self.stream_name.assign(self.entity.stream_name)
        self.create = self.entity.create
        self.path.assign(self.entity.path)
        self.port_number.assign(self.entity.port_number)
        self.host_name.assign(self.entity.host_name)
        self.signal = self.entity.signal
        self.blocking = self.entity.blocking
        self.steps.assign(self.entity.steps)
        self.receive_first = self.entity.receive_first
        self.timeout.assign(self.entity.timeout)
        self.file_name.assign(self.entity.file_name)
        self.precision.assign(self.entity.precision)
        self.shift.assign(self.entity.shift)
    def store(self, context):
        self.entity.stream_name = self.stream_name.store()
        self.entity.create = self.create
        self.entity.path = self.path.store() if not (self.port_number.select or self.host_name.select) else None
        self.entity.port_number = self.port_number.store() if not self.path.select else None
        self.entity.host_name = self.host_name.store() if not self.path.select else None
        self.entity.signal = self.signal
        self.entity.blocking = self.blocking
        self.entity.steps = self.steps.store()
        self.entity.receive_first = self.receive_first
        self.entity.timeout = self.timeout.store()
        self.entity.file_name = self.file_name.store()
        self.entity.precision = self.precision.store() if self.file_name.select else None
        self.entity.shift = self.shift.store() if self.file_name.select else None
    def draw(self, context):
        layout = self.layout
        self.stream_name.draw(layout, "Stream name")
        layout.prop(self, "create")
        if not (self.port_number.select or self.host_name.select):
            self.path.draw(layout, "Path")
        if not self.path.select:
            self.port_number.draw(layout, "Port number")
            self.host_name.draw(layout, "Host name")
        layout.prop(self, "signal")
        layout.prop(self, "blocking")
        self.steps.draw(layout, "Steps")
        layout.prop(self, "receive_first")
        self.timeout.draw(layout, "Timeout")
        self.file_name.draw(layout, "File name")
        if self.file_name.select:
            self.precision.draw(layout, "Precision")
            self.shift.draw(layout, "Shift")
    def check(self, context):
        return True in [x.check(context) for x in (self.stream_name, self.path, self.port_number, self.host_name, self.steps, self.timeout, self.file_name, self.precision, self.shift)]
    def create_entity(self):
        return Stream(self.name)

klasses[StreamOperator.bl_label] = StreamOperator

class EventStream(Stream):
    pass

class EventStreamOperator(StreamOperator):
    bl_label = "Event stream"
    @classmethod
    def poll(cls, context):
        return not database.driver.filter(cls.bl_label)
    def draw(self, context):
        layout = self.layout
        self.stream_name.draw(layout, "Stream name")
        self.port_number.draw(layout, "Port number")
        self.host_name.draw(layout, "Host name")
        layout.prop(self, "blocking")
        self.steps.draw(layout, "Steps")
        layout.prop(self, "receive_first")
        self.file_name.draw(layout, "File name")
        if self.file_name.select:
            self.precision.draw(layout, "Precision")
            self.shift.draw(layout, "Shift")

klasses[EventStreamOperator.bl_label] = EventStreamOperator

bundle = Bundle(driver_tree, Base, klasses, database.driver)
