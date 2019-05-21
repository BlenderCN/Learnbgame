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
    for x in [base, common, menu]:
        imp.reload(x)
else:
    from . import base
    from . import common
    from . import menu
from .base import bpy, root_dot, database, Operator, Entity, Bundle, BPY, SelectedObjects
from .common import safe_name
from .menu import default_klasses, drive_tree

class Base(Operator):
    bl_label = "Drives"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.drive_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.drive_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.drive_uilist
        del bpy.types.Scene.drive_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.drive_index, context.scene.drive_uilist
    def set_index(self, context, value):
        context.scene.drive_index = value

klasses = default_klasses(drive_tree, Base)

class Array(Entity):
    def string(self):
        ret = "array, " + BPY.FORMAT(len(self.drives))
        for d in self.drives:
            ret += ",\n\t\treference, " + d.safe_name()
        return ret

class ArrayOperator(Base):
    N = bpy.props.IntProperty(min=2, max=20, name="Number of drives")
    drives = bpy.props.CollectionProperty(type = BPY.Drive)
    dimension = None
    def prereqs(self, context):
        self.drives.clear()
        for i in range(20):
            d = self.drives.add()
            d.mandatory = True
            d.dimension = self.dimension
    def assign(self, context):
        for i, d in enumerate(self.entity.drives):
            self.drives[i].assign(d)
        self.N = len(self.entity.drives)
    def store(self, context):
        self.entity.drives = [d.store() for d in self.drives[:self.N]]
    def draw(self, context):
        self.basis = self.N
        layout = self.layout
        layout.prop(self, "N")
        for d in self.drives[:self.N]:
            d.draw(layout)
    def check(self, context):
        return (self.basis != self.N) or True in [d.check(context) for d in self.drives]

class ArrayOfScalarsDrive(Array):
    dimension = "1D"

class ArrayOfScalarsDriveOperator(ArrayOperator):
    bl_label = "Array of scalar drives"
    dimension = "1D"
    def create_entity(self):
        return ArrayOfScalarsDrive(self.name)

klasses[ArrayOfScalarsDriveOperator.bl_label] = ArrayOfScalarsDriveOperator

class ArrayOf3DDrives(Array):
    dimension = "3D"

class ArrayOf3DDrivesOperator(ArrayOperator):
    bl_label = "Array of 3D drives"
    dimension = "3D"
    def create_entity(self):
        return ArrayOf3DDrives(self.name)

klasses[ArrayOf3DDrivesOperator.bl_label] = ArrayOf3DDrivesOperator

class ArrayOf6DDrives(Array):
    dimension = "6D"

class ArrayOf6DDrivesOperator(ArrayOperator):
    bl_label = "Array of 6D drives"
    dimension = "6D"
    def create_entity(self):
        return ArrayOf6DDrives(self.name)

klasses[ArrayOf6DDrivesOperator.bl_label] = ArrayOf6DDrivesOperator

class ArrayOf3x3Drive(Array):
    dimension = "3x3"

class ArrayOf3x3DriveOperator(ArrayOperator):
    bl_label = "Array of 3x3 drives"
    dimension = "3x3"
    def create_entity(self):
        return ArrayOf3x3Drive(self.name)

klasses[ArrayOf3x3DriveOperator.bl_label] = ArrayOf3x3DriveOperator

class ArrayOf6x6Drives(Array):
    dimension = "6x6"

class ArrayOf6x6DrivesOperator(ArrayOperator):
    bl_label = "Array of 6x6 drives"
    dimension = "6x6"
    def create_entity(self):
        return ArrayOf6x6Drives(self.name)

klasses[ArrayOf6x6DrivesOperator.bl_label] = ArrayOf6x6DrivesOperator

class TemplateBase(Base):
    N = None
    ordinals = {}
    matrix_type = None
    matrix = bpy.props.PointerProperty(type = BPY.Matrix)
    subtype = bpy.props.EnumProperty(items=[
        ("matr", "Matrix", "Matrix template"),
        ("sym", "Symmetric", "Symmetric matrix template"),
        ("diag", "Diagonal", "Diagonal matrix template")],
        name="Subtype", default="matr")
    drives = bpy.props.CollectionProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.matrix.type = self.matrix_type
        self.subtype = "matr"
        self.drives.clear()
        for i in range(self.N):
            d = self.drives.add()
    def assign(self, context):
        self.matrix.assign(self.entity.matrix)
        self.subtype = self.entity.subtype
        for i, f in enumerate(self.entity.drives):
            self.drives[i].assign(f)
    def store(self, context):
        self.entity.matrix = self.matrix.store()
        self.entity.subtype = self.subtype
        if self.matrix.select:
            self.entity.drives = [self.drives[0].store()]
        else:
            self.entity.drives = [d.store() if i in self.ordinals[self.subtype] else None for i, d in enumerate(self.drives)]
    def check(self, context):
        return (self.basis != self.subtype) or self.matrix.check(context) or (True in [d.check(context) for d in self.drives])

class Template3D(Entity):
    dimension = "3D"
    def string(self):
        if self.matrix is None:
            if not [drive for drive in self.drives if drive is not None]:
                return "null"
            else:
                return "component,\n\t\t" + ",\n\t\t".join([("reference, " + drive.safe_name()) if drive is not None else "null" for drive in self.drives])
        else:
            return "single, " + self.matrix.string() + ",\n\t\treference, " + self.drives[0].safe_name()

class Template3DOperator(TemplateBase):
    bl_label = "Template 3D drive"
    N = 3
    ordinals = {
        "matr": [i for i in range(3)]}
    matrix_type = "3D"
    def draw(self, context):
        layout = self.layout
        self.matrix.draw(layout, "Single")
        if self.matrix.select:
            self.drives[0].mandatory = True
            self.drives[0].draw(layout, "Drive")
        else:
            self.drives[0].mandatory = False
            for i in range(self.N):
                self.drives[i].draw(layout, "Drive-" + str(i+1))
    def create_entity(self):
        return Template3D(self.name)


klasses[Template3DOperator.bl_label] = Template3DOperator

class Template6D(Template3D):
    dimension = "6D"

class Template6DOperator(Template3DOperator):
    bl_label = "Template 6D drive"
    N = 6
    ordinals = {
        "component": [i for i in range(6)],
        "null": [],
        "single": [0]}
    def create_entity(self):
        return Template6D(self.name)

klasses[Template6DOperator.bl_label] = Template6DOperator

class Template3x3(Entity):
    dimension = "3x3"
    def string(self):
        if self.subtype == "matr":
            ret = ("\n\t\t\tmatr,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[0:3]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[3:6]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[6:9]]))
        elif self.subtype == "sym":
            ret = ("\n\t\t\tsym,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[0:3]]) + ",\n" +
            "\t"*5 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[4:6]]) + ",\n" +
            "\t"*6 + BPY.FORMAT(self.drives[8]))
        elif self.subtype == "skew":
            ret = "\n\t\t\tskew, " + ", ".join([BPY.FORMAT(self.drives[i]) for i in [7, 2, 3]])
        elif self.subtype == "diag":
            ret = "\n\t\t\tdiag, " + ", ".join([BPY.FORMAT(self.drives[i]) for i in [0, 4, 8]])
        elif self.subtype == "eye":
            ret = "\n\t\t\teye"
        elif self.subtype == "null":
            ret = "\n\t\t\tnull"
        return ret

class Template3x3Operator(TemplateBase):
    bl_label = "Template 3x3 drive"
    N = 9
    subtype = bpy.props.EnumProperty(items=[
        ("matr", "Matrix", "Matrix template"),
        ("null", "Null", "Null template"),
        ("sym", "Symmetric", "Symmetric matrix template"),
        ("diag", "Diagonal", "Diagonal matrix template"),
        ("single", "Single", "Single template")],
        name="Subtype", default="single")
    ordinals = {
        "matr": [i for i in range(9)],
        "null": [],
        "sym": [0,1,2,4,5,8],
        "diag": [0,4,8],
        "single": [0]}
    def draw(self, context):
        self.basis = self.subtype
        layout = self.layout
        layout.prop(self, "subtype")
        if self.subtype == "single":
            self.drives[0].draw(layout, "Drive")
        elif self.subtype in "matr sym diag".split():
            for i in range(3):
                row = layout.row()
                for j in range(3):
                    k = 3*i+j
                    if k in self.ordinals[self.subtype]:
                        self.drives[k].draw(row, "")
                    else:
                        row.label()
    def create_entity(self):
        return Template3x3(self.name)

klasses[Template3x3Operator.bl_label] = Template3x3Operator

class Template6x6(Entity):
    dimension = "6x6"
    def string(self):
        if self.subtype == "matr":
            ret = ("\n\t\t\tmatr,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[0:6]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[6:12]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[12:18]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[18:24]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[24:30]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[30:36]]))
        elif self.subtype == "sym":
            ret = ("\n\t\t\tsym,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[0:6]]) + ",\n" +
            "\t"*5 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[7:12]]) + ",\n" +
            "\t"*6 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[14:18]]) + ",\n" +
            "\t"*7 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[21:24]]) + ",\n" +
            "\t"*8 + ", ".join([BPY.FORMAT(prop) for prop in self.drives[28:30]]) + ",\n" +
            "\t"*9 + BPY.FORMAT(self.drives[35]))
        elif self.subtype == "diag":
            ret = "\n\t\t\tdiag, " + ", ".join([BPY.FORMAT(self.drives[i]) for i in [0,7,14,21,28,35]])
        elif self.subtype == "eye":
            ret = "\n\t\t\teye"
        elif self.subtype == "null":
            ret = "\n\t\t\tnull"
        return ret

class Template6x6Operator(TemplateBase):
    bl_label = "Template 6x6 drive"
    N = 36
    subtype = bpy.props.EnumProperty(items=[
        ("matr", "Matrix", "Matrix template"),
        ("null", "Null", "Null template"),
        ("sym", "Symmetric", "Symmetric matrix template"),
        ("diag", "Diagonal", "Diagonal matrix template"),
        ("single", "Single", "Single template")],
        name="Subtype", default="single")
    ordinals = {
        "matr": [i for i in range(36)],
        "null": [],
        "sym": [0,1,2,3,4,5,7,8,9,10,11,14,15,16,17,21,22,23,28,29,35],
        "diag": [0,7,14,21,28,35],
        "single": [0]}
    show_column = bpy.props.IntProperty(min=1, max=4, name="Show column", default=1)
    def draw(self, context):
        self.basis = (self.subtype, self.show_column)
        layout = self.layout
        layout.prop(self, "subtype")
        if self.subtype == "single":
            self.drives[0].draw(layout, "Drive")
        elif self.subtype in "matr sym diag".split():
            row = layout.row()
            row.prop(self, "show_column")
            row.label("to column: " + str(self.show_column +2))
            row = layout.row()
            for i in range(3):
                row.label(str(self.show_column + i))
            for i in range(6):
                row = layout.row()
                for j in range(self.show_column - 1, self.show_column + 2):
                    k = 6*i+j
                    if k in self.ordinals[self.subtype]:
                        self.drives[k].draw(row, "")
                    else:
                        row.label()
    def check(self, context):
        return (self.basis != (self.subtype, self.show_column)) or (True in [d.check(context) for d in self.drives])
    def create_entity(self):
        return Template6x6(self.name)

klasses[Template6x6Operator.bl_label] = Template6x6Operator

class FileDrive(Entity):
    dimension = "1D"
    def string(self):
        col = 1 + [d for d in database.drive if hasattr(d, "driver") and d.driver == self.driver].index(self)
        return ("file, " + self.driver.safe_name() + ", " + str(col) +
            (", amplitude, " + BPY.FORMAT(self.amplitude) if self.amplitude is not None else ""))

class FileDriveOperator(Base):
    bl_label = "File drive"
    driver = bpy.props.PointerProperty(type = BPY.Driver)
    amplitude = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.driver.mandatory = True
    def assign(self, context):
        self.driver.assign(self.entity.driver)
        self.amplitude.assign(self.entity.amplitude)
    def store(self, context):
        self.entity.driver = self.driver.store()
        self.entity.amplitude = self.amplitude.store()
    def draw(self, context):
        layout = self.layout
        self.driver.draw(layout, "Driver")
        self.amplitude.draw(layout, "Amplitude")
    def check(self, context):
        return self.driver.check(context) or self.amplitude.check(context)
    def create_entity(self):
        return FileDrive(self.name)

klasses[FileDriveOperator.bl_label] = FileDriveOperator

class EventDrive(FileDrive):
    pass

event_types = ['NONE', 'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE', 'BUTTON6MOUSE', 'BUTTON7MOUSE', 'ACTIONMOUSE', 'SELECTMOUSE', 'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE', 'EVT_TWEAK_L', 'EVT_TWEAK_M', 'EVT_TWEAK_R', 'EVT_TWEAK_A', 'EVT_TWEAK_S', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'LEFT_CTRL', 'LEFT_ALT', 'LEFT_SHIFT', 'RIGHT_ALT', 'RIGHT_CTRL', 'RIGHT_SHIFT', 'OSKEY', 'GRLESS', 'ESC', 'TAB', 'RET', 'SPACE', 'LINE_FEED', 'BACK_SPACE', 'DEL', 'SEMI_COLON', 'PERIOD', 'COMMA', 'QUOTE', 'ACCENT_GRAVE', 'MINUS', 'SLASH', 'BACK_SLASH', 'EQUAL', 'LEFT_BRACKET', 'RIGHT_BRACKET', 'LEFT_ARROW', 'DOWN_ARROW', 'RIGHT_ARROW', 'UP_ARROW', 'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_8', 'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_5', 'NUMPAD_7', 'NUMPAD_9', 'NUMPAD_PERIOD', 'NUMPAD_SLASH', 'NUMPAD_ASTERIX', 'NUMPAD_0', 'NUMPAD_MINUS', 'NUMPAD_ENTER', 'NUMPAD_PLUS', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'PAUSE', 'INSERT', 'HOME', 'PAGE_UP', 'PAGE_DOWN', 'END', 'MEDIA_PLAY', 'MEDIA_STOP', 'MEDIA_FIRST', 'MEDIA_LAST', 'TEXTINPUT', 'WINDOW_DEACTIVATE', 'TIMER', 'TIMER0', 'TIMER1', 'TIMER2', 'TIMER_JOBS', 'TIMER_AUTOSAVE', 'TIMER_REPORT', 'TIMERREGION', 'NDOF_MOTION', 'NDOF_BUTTON_MENU', 'NDOF_BUTTON_FIT', 'NDOF_BUTTON_TOP', 'NDOF_BUTTON_BOTTOM', 'NDOF_BUTTON_LEFT', 'NDOF_BUTTON_RIGHT', 'NDOF_BUTTON_FRONT', 'NDOF_BUTTON_BACK', 'NDOF_BUTTON_ISO1', 'NDOF_BUTTON_ISO2', 'NDOF_BUTTON_ROLL_CW', 'NDOF_BUTTON_ROLL_CCW', 'NDOF_BUTTON_SPIN_CW', 'NDOF_BUTTON_SPIN_CCW', 'NDOF_BUTTON_TILT_CW', 'NDOF_BUTTON_TILT_CCW', 'NDOF_BUTTON_ROTATE', 'NDOF_BUTTON_PANZOOM', 'NDOF_BUTTON_DOMINANT', 'NDOF_BUTTON_PLUS', 'NDOF_BUTTON_MINUS', 'NDOF_BUTTON_ESC', 'NDOF_BUTTON_ALT', 'NDOF_BUTTON_SHIFT', 'NDOF_BUTTON_CTRL', 'NDOF_BUTTON_1', 'NDOF_BUTTON_2', 'NDOF_BUTTON_3', 'NDOF_BUTTON_4', 'NDOF_BUTTON_5', 'NDOF_BUTTON_6', 'NDOF_BUTTON_7', 'NDOF_BUTTON_8', 'NDOF_BUTTON_9', 'NDOF_BUTTON_10', 'NDOF_BUTTON_A', 'NDOF_BUTTON_B', 'NDOF_BUTTON_C']

class EventDriveOperator(FileDriveOperator):
    bl_label = "Event drive"
    initial_value = bpy.props.IntProperty(name="Initial value")
    increment = bpy.props.EnumProperty(items=[(e, e, "") for e in event_types], default='PAGE_UP', name="Increment event")
    decrement = bpy.props.EnumProperty(items=[(e, e, "") for e in event_types], default='PAGE_DOWN', name="Decrement event")
    @classmethod
    def poll(cls, context):
        return True
    def prereqs(self, context):
        self.driver.type = "Event stream"
        event_streams = database.driver.filter("Event stream")
        if event_streams:
            self.driver.assign(event_streams[0])
        super().prereqs(context)
    def assign(self, context):
        self.initial_value = self.entity.initial_value
        self.increment = self.entity.increment
        self.decrement = self.entity.decrement
        super().assign(context)
    def store(self, context):
        self.entity.initial_value = self.initial_value
        self.entity.increment = self.increment
        self.entity.decrement = self.decrement
        super().store(context)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "initial_value")
        self.amplitude.draw(layout, "Amplitude")
        layout.prop(self, "increment")
        layout.prop(self, "decrement")
        self.driver.draw(layout, "Event stream")
    def create_entity(self):
        return EventDrive(self.name)

klasses[EventDriveOperator.bl_label] = EventDriveOperator

class NullDrive(Entity):
    dimension = "1D"
    def string(self):
        return "null"

class NullDriveOperator(Base):
    bl_label = "Null drive"
    def create_entity(self):
        return NullDrive(self.name)

klasses[NullDriveOperator.bl_label] = NullDriveOperator

class DirectDrive(Entity):
    dimension = "1D"
    def string(self):
        return "direct"

class DirectDriveOperator(Base):
    bl_label = "Direct drive"
    def create_entity(self):
        return DirectDrive(self.name)

klasses[DirectDriveOperator.bl_label] = DirectDriveOperator

class UnitDrive(Entity):
    dimension = "1D"
    def string(self):
        return "unit"

class UnitDriveOperator(Base):
    bl_label = "Unit drive"
    def create_entity(self):
        return UnitDrive(self.name)

klasses[UnitDriveOperator.bl_label] = UnitDriveOperator

class ConstantDrive(Entity):
    dimension = "1D"
    def string(self):
        return BPY.FORMAT(self.constant)

class ConstantDriveOperator(Base):
    bl_label = "Constant drive"
    constant = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.constant.mandatory = True
    def assign(self, context):
        self.constant.assign(self.entity.constant)
    def store(self, context):
        self.entity.constant = self.constant.store()
    def draw(self, context):
        layout = self.layout
        self.constant.draw(layout, "Constant")
    def check(self, context):
        return self.constant.check(context)
    def create_entity(self):
        return ConstantDrive(self.name)

klasses[ConstantDriveOperator.bl_label] = ConstantDriveOperator

class TimeDrive(Entity):
    dimension = "1D"
    def string(self):
        return "time"

class TimeDriveOperator(Base):
    bl_label = "Time drive"
    def create_entity(self):
        return TimeDrive(self.name)

klasses[TimeDriveOperator.bl_label] = TimeDriveOperator

class LinearDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "linear"
        for v in [self.constant, self.slope]:
            ret += ", " + BPY.FORMAT(v)
        return ret

class LinearDriveOperator(Base):
    bl_label = "Linear drive"
    constant = bpy.props.PointerProperty(type = BPY.Float)
    slope = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.constant.mandatory = True
        self.slope.mandatory = True
    def assign(self, context):
        self.constant.assign(self.entity.constant)
        self.slope.assign(self.entity.slope)
    def store(self, context):
        self.entity.constant = self.constant.store()
        self.entity.slope = self.slope.store()
    def draw(self, context):
        layout = self.layout
        self.constant.draw(layout, "Constant")
        self.slope.draw(layout, "Slope")
    def check(self, context):
        return self.constant.check(context) or self.slope.check(context)
    def create_entity(self):
        return LinearDrive(self.name)

klasses[LinearDriveOperator.bl_label] = LinearDriveOperator

class ParabolicDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "parabolic"
        for v in [self.constant, self.linear, self.parabolic]:
            ret += ", " + BPY.FORMAT(v)
        return ret

class ParabolicDriveOperator(Base):
    bl_label = "Parabolic drive"
    constant = bpy.props.PointerProperty(type = BPY.Float)
    linear = bpy.props.PointerProperty(type = BPY.Float)
    parabolic = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.constant.mandatory = True
        self.linear.mandatory = True
        self.parabolic.mandatory = True
    def assign(self, context):
        self.constant.assign(self.entity.constant)
        self.linear.assign(self.entity.linear)
        self.parabolic.assign(self.entity.parabolic)
    def store(self, context):
        self.entity.constant = self.constant.store()
        self.entity.linear = self.linear.store()
        self.entity.parabolic = self.parabolic.store()
    def draw(self, context):
        layout = self.layout
        self.constant.draw(layout, "Constant")
        self.linear.draw(layout, "Linear")
        self.parabolic.draw(layout, "Parabolic")
    def check(self, context):
        return True in [v.check(context) for v in [self.constant, self.linear, self.parabolic]]
    def create_entity(self):
        return ParabolicDrive(self.name)

klasses[ParabolicDriveOperator.bl_label] = ParabolicDriveOperator

class CubicDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "cubic"
        for v in [self.constant, self.linear, self.parabolic, self.cubic]:
            ret += ", " + BPY.FORMAT(v)
        return ret

class CubicDriveOperator(Base):
    bl_label = "Cubic drive"
    constant = bpy.props.PointerProperty(type = BPY.Float)
    linear = bpy.props.PointerProperty(type = BPY.Float)
    parabolic = bpy.props.PointerProperty(type = BPY.Float)
    cubic = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.constant.mandatory = True
        self.linear.mandatory = True
        self.parabolic.mandatory = True
        self.cubic.mandatory = True
    def assign(self, context):
        self.constant.assign(self.entity.constant)
        self.linear.assign(self.entity.linear)
        self.parabolic.assign(self.entity.parabolic)
        self.cubic.assign(self.entity.cubic)
    def store(self, context):
        self.entity.constant = self.constant.store()
        self.entity.linear = self.linear.store()
        self.entity.parabolic = self.parabolic.store()
        self.entity.cubic = self.cubic.store()
    def draw(self, context):
        layout = self.layout
        self.constant.draw(layout, "Constant")
        self.linear.draw(layout, "Linear")
        self.parabolic.draw(layout, "Parabolic")
        self.cubic.draw(layout, "Cubic")
    def check(self, context):
        return True in [v.check(context) for v in [self.constant, self.linear, self.parabolic, self.cubic]]
    def create_entity(self):
        return CubicDrive(self.name)

klasses[CubicDriveOperator.bl_label] = CubicDriveOperator

class StepDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "step"
        for v in [self.initial_time, self.step_value, self.initial_value]:
            ret += ", " + BPY.FORMAT(v)
        return ret

class StepDriveOperator(Base):
    bl_label = "Step drive"
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    step_value = bpy.props.PointerProperty(type = BPY.Float)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.initial_time.mandatory = True
        self.step_value.mandatory = True
        self.initial_value.mandatory = True
    def assign(self, context):
        self.initial_time.assign(self.entity.initial_time)
        self.step_value.assign(self.entity.step_value)
        self.initial_value.assign(self.entity.initial_value)
    def store(self, context):
        self.entity.initial_time = self.initial_time.store()
        self.entity.step_value = self.step_value.store()
        self.entity.initial_value = self.initial_value.store()
    def draw(self, context):
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.step_value.draw(layout, "Step value")
        self.initial_value.draw(layout, "Initial value")
    def check(self, context):
        return True in [v.check(context) for v in [self.initial_time, self.step_value, self.initial_value]]
    def create_entity(self):
        return StepDrive(self.name)

klasses[StepDriveOperator.bl_label] = StepDriveOperator

class DoubleStepDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "double step"
        for v in [self.initial_time, self.final_time, self.step_value, self.initial_value]:
            ret += ", " + BPY.FORMAT(v)
        return ret

class DoubleStepDriveOperator(Base):
    bl_label = "Double step drive"
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    final_time = bpy.props.PointerProperty(type = BPY.Float)
    step_value = bpy.props.PointerProperty(type = BPY.Float)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.initial_time.mandatory = True
        self.final_time.mandatory = True
        self.step_value.mandatory = True
        self.initial_value.mandatory = True
    def assign(self, context):
        self.initial_time.assign(self.entity.initial_time)
        self.final_time.assign(self.entity.final_time)
        self.step_value.assign(self.entity.step_value)
        self.initial_value.assign(self.entity.initial_value)
    def store(self, context):
        self.entity.initial_time = self.initial_time.store()
        self.entity.final_time = self.final_time.store()
        self.entity.step_value = self.step_value.store()
        self.entity.initial_value = self.initial_value.store()
    def draw(self, context):
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.final_time.draw(layout, "Final time")
        self.step_value.draw(layout, "Step value")
        self.initial_value.draw(layout, "Initial value")
    def check(self, context):
        return True in [v.check(context) for v in [self.initial_time, self.final_time, self.step_value, self.initial_value]]
    def create_entity(self):
        return DoubleStepDrive(self.name)

klasses[DoubleStepDriveOperator.bl_label] = DoubleStepDriveOperator

class RampDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "ramp"
        for v in [self.slope, self.initial_time]:
            ret += ", " + BPY.FORMAT(v)
        if self.final_time is None:
            ret += ", forever"
        else:
            ret += ", " + BPY.FORMAT(self.final_time)
        ret += ", " + BPY.FORMAT(self.initial_value)
        return ret

class RampDriveOperator(Base):
    bl_label = "Ramp drive"
    slope = bpy.props.PointerProperty(type = BPY.Float)
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    final_time = bpy.props.PointerProperty(type = BPY.Float)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.slope.mandatory = True
        self.initial_time.mandatory = True
        self.initial_value.mandatory = True
    def assign(self, context):
        self.slope.assign(self.entity.slope)
        self.initial_time.assign(self.entity.initial_time)
        self.final_time.assign(self.entity.final_time)
        self.initial_value.assign(self.entity.initial_value)
    def store(self, context):
        self.entity.slope = self.slope.store()
        self.entity.initial_time = self.initial_time.store()
        self.entity.final_time = self.final_time.store()
        self.entity.initial_value = self.initial_value.store()
    def draw(self, context):
        layout = self.layout
        self.slope.draw(layout, "Slope")
        self.initial_time.draw(layout, "Initial time")
        self.final_time.draw(layout, "Final time")
        self.initial_value.draw(layout, "Initial value")
    def check(self, context):
        return True in [v.check(context) for v in [self.slope, self.initial_time, self.final_time, self.initial_value]]
    def create_entity(self):
        return RampDrive(self.name)

klasses[RampDriveOperator.bl_label] = RampDriveOperator

class PiecewiseLinearDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "piecewise linear, " + BPY.FORMAT(len(self.T))
        for t, x in zip(self.T, self.X):
            ret += ",\n\t\t" + BPY.FORMAT(t) + ", " + BPY.FORMAT(x)
        return ret

class PiecewiseLinearDriveOperator(Base):
    bl_label = "Piecewise linear drive"
    N = bpy.props.IntProperty(name="Number of points", min=2, max=50, description="", default=2)
    T = bpy.props.CollectionProperty(type = BPY.Float)
    X = bpy.props.CollectionProperty(type = BPY.Float)
    def prereqs(self, context):
        self.T.clear()
        self.X.clear()
        for i in range(50):
            t = self.T.add()
            t.mandatory = True
            x = self.X.add()
            x.mandatory = True
    def assign(self, context):
        for i, t in enumerate(self.entity.T):
            self.T[i].assign(t)
        for i, x in enumerate(self.entity.X):
            self.X[i].assign(x)
        self.N = len(self.entity.T)
    def store(self, context):
        self.entity.T = [t.store() for t in self.T][:self.N]
        self.entity.X = [x.store() for x in self.X][:self.N]
    def draw(self, context):
        self.basis = self.N
        layout = self.layout
        layout.prop(self, "N")
        row = layout.row()
        row.label("Time")
        row.label("Value")
        for t, x in zip(self.T[:self.N], self.X[:self.N]):
            row = layout.row()
            t.draw(row, "")
            x.draw(row, "")
    def check(self, context):
        return (self.basis != self.N) or True in [t.check(context) for t in self.T] + [x.check(context) for x in self.X]
    def create_entity(self):
        return PiecewiseLinearDrive(self.name)

klasses[PiecewiseLinearDriveOperator.bl_label] = PiecewiseLinearDriveOperator

class SineDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "sine"
        for v in [self.initial_time, self.omega, self.amplitude]:
            ret += ", " + BPY.FORMAT(v)
        if self.duration == "cycles":
            ret += ", " + BPY.FORMAT(self.cycles)
        else:
            ret += ", " + self.duration
        ret += ", " + BPY.FORMAT(self.initial_value)
        return ret

class Periodic(Base):
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    omega = bpy.props.PointerProperty(type = BPY.Float)
    duration = bpy.props.EnumProperty(items=[("cycles", "N-cycles", ""), ("half", "Half cycle", ""), ("one", "Full cycle", ""), ("forever", "Infinite cycle", "")], default="cycles")
    cycles = bpy.props.PointerProperty(type = BPY.Int)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.initial_time.mandatory = True
        self.omega.mandatory = True
        self.cycles.mandatory = True
        self.initial_value.mandatory = True
    def assign(self, context):
        self.initial_time.assign(self.entity.initial_time)
        self.omega.assign(self.entity.omega)
        self.duration = self.entity.duration
        self.cycles.assign(self.entity.cycles)
        self.initial_value.assign(self.entity.initial_value)
    def store(self, context):
        self.entity.initial_time = self.initial_time.store()
        self.entity.omega = self.omega.store()
        self.entity.duration = self.duration
        self.entity.cycles = self.cycles.store()
        self.entity.initial_value = self.initial_value.store()
    def check(self, context):
        return True in [v.check(context) for v in [self.initial_time, self.omega, self.cycles, self.initial_value]]

class SineCosine(Periodic):
    amplitude = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.amplitude.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.amplitude.assign(self.entity.amplitude)
        super().assign(context)
    def store(self, context):
        self.entity.amplitude = self.amplitude.store()
        super().store(context)
    def draw(self, context):
        self.basis = self.duration
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.omega.draw(layout, "Omega")
        self.amplitude.draw(layout, "Amplitude")
        layout.prop(self, "duration", text="Duration")
        if self.duration == "cycles":
            self.cycles.draw(layout, "Cycles")
        self.initial_value.draw(layout, "Initial value")
    def check(self, context):
        return (self.basis != self.duration) or self.amplitude.check(context) or super().check(context)
    def create_entity(self):
        return SineDrive(self.name)

class SineDriveOperator(SineCosine):
    bl_label = "Sine drive"
    def create_entity(self):
        return SineDrive(self.name)

klasses[SineDriveOperator.bl_label] = SineDriveOperator

class CosineDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "cosine"
        for v in [self.initial_time, self.omega, self.amplitude]:
            ret += ", " + BPY.FORMAT(v)
        if self.duration == "cycles":
            ret += ", " + BPY.FORMAT(self.cycles)
        else:
            ret += ", " + self.duration
        ret += ", " + BPY.FORMAT(self.initial_value)
        return ret

class CosineDriveOperator(SineCosine):
    bl_label = "Cosine drive"
    def create_entity(self):
        return CosineDrive(self.name)

klasses[CosineDriveOperator.bl_label] = CosineDriveOperator

class TanhDrive(Entity):
    dimension = "1D"
    def string(self):
        return  "tanh, " + ", ".join([BPY.FORMAT(v) for v in [self.initial_time, self.amplitude, self.slope, self.initial_value]])

class TanhDriveOperator(Base):
    bl_label = "Tanh drive"
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    amplitude = bpy.props.PointerProperty(type = BPY.Float)
    slope = bpy.props.PointerProperty(type = BPY.Float)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.initial_time.mandatory = True
        self.amplitude.mandatory = True
        self.slope.mandatory = True
        self.initial_value.mandatory = True
    def assign(self, context):
        self.initial_time.assign(self.entity.initial_time)
        self.amplitude.assign(self.entity.amplitude)
        self.slope.assign(self.entity.slope)
        self.initial_value.assign(self.entity.initial_value)
    def store(self, context):
        self.entity.initial_time = self.initial_time.store()
        self.entity.amplitude = self.amplitude.store()
        self.entity.slope = self.slope.store()
        self.entity.initial_value = self.initial_value.store()
    def draw(self, context):
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.amplitude.draw(layout, "Final time")
        self.slope.draw(layout, "Slope")
        self.initial_value.draw(layout, "Initial value")
    def check(self, context):
        return True in [v.check(context) for v in [self.initial_time, self.amplitude, self.slope, self.initial_value]]
    def create_entity(self):
        return TanhDrive(self.name)

klasses[TanhDriveOperator.bl_label] = TanhDriveOperator

class FourierSeriesDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "fourier series"
        for v in [self.initial_time, self.omega, len(self.A)]:
            ret += ", " + BPY.FORMAT(v)
        ret += ",\n\t\t" + BPY.FORMAT(self.A[0])
        for a, b in zip(self.A[1:], self.B[1:]):
            ret += ",\n\t\t" + BPY.FORMAT(a) + ", " + BPY.FORMAT(b)
        if self.duration == "cycles":
            ret += ",\n\t\t" + BPY.FORMAT(self.cycles)
        else:
            ret += ",\n\t\t" + self.duration
        ret += ", " + BPY.FORMAT(self.initial_value)
        return ret

class FourierSeriesDriveOperator(Periodic):
    bl_label = "Fourier series drive"
    N = bpy.props.IntProperty(name="Number of terms", min=2, max=50, description="", default=2)
    A = bpy.props.CollectionProperty(type = BPY.Float)
    B = bpy.props.CollectionProperty(type = BPY.Float)
    def prereqs(self, context):
        self.A.clear()
        self.B.clear()
        for i in range(50):
            a = self.A.add()
            a.mandatory = True
            b = self.B.add()
            b.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        for i, a in enumerate(self.entity.A):
            self.A[i].assign(a)
        for i, b in enumerate(self.entity.B):
            self.B[i].assign(b)
        self.N = len(self.entity.A)
        super().assign(context)
    def store(self, context):
        self.entity.A = [a.store() for a in self.A[:self.N]]
        self.entity.B = [b.store() for b in self.B[:self.N]]
        super().store(context)
    def draw(self, context):
        self.basis = (self.N, self.duration)
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.omega.draw(layout, "Omega")
        layout.prop(self, "duration", text="Duration")
        if self.duration == "cycles":
            self.cycles.draw(layout, "Cycles")
        self.initial_value.draw(layout, "Initial value")
        layout.prop(self, "N")
        row = layout.row()
        row.label("Time")
        row.label("Value")
        row = layout.row()
        self.A[0].draw(row, "")
        row.label("")
        for a, b in zip(self.A[1:self.N], self.B[1:self.N]):
            row = layout.row()
            a.draw(row, "")
            b.draw(row, "")
    def check(self, context):
        return (self.basis != (self.N, self.duration)) or True in [a.check(context) for a in self.A] + [b.check(context) for b in self.B] or super().check(context)
    def create_entity(self):
        return FourierSeriesDrive(self.name)

klasses[FourierSeriesDriveOperator.bl_label] = FourierSeriesDriveOperator

class FrequencySweepDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "frequency sweep, " + BPY.FORMAT(self.initial_time)
        ret += ",\n\t\treference, " + self.angular_velocity_drive.safe_name()
        ret += ",\n\t\treference, " + self.amplitude_drive.safe_name()
        ret += ",\n\t\t" + BPY.FORMAT(self.initial_value)
        if self.final_time is None:
            ret += ", forever"
        else:
            ret += ", " + BPY.FORMAT(self.final_time)
        ret += ", " + BPY.FORMAT(self.final_value)
        return ret

class FrequencySweepDriveOperator(Base):
    bl_label = "Frequency sweep drive"
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    angular_velocity_drive = bpy.props.PointerProperty(type = BPY.Drive)
    amplitude_drive = bpy.props.PointerProperty(type = BPY.Drive)
    final_time = bpy.props.PointerProperty(type = BPY.Float)
    final_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.initial_time.mandatory = True
        self.initial_value.mandatory = True
        self.angular_velocity_drive.mandatory = True
        self.amplitude_drive.mandatory = True
        self.final_value.mandatory = True
    def assign(self, context):
        self.initial_time.assign(self.entity.initial_time)
        self.initial_value.assign(self.entity.initial_value)
        self.angular_velocity_drive.assign(self.entity.angular_velocity_drive)
        self.amplitude_drive.assign(self.entity.amplitude_drive)
        self.final_time.assign(self.entity.final_time)
        self.final_value.assign(self.entity.final_value)
    def store(self, context):
        self.entity.initial_time = self.initial_time.store()
        self.entity.initial_value = self.initial_value.store()
        self.entity.angular_velocity_drive = self.angular_velocity_drive.store()
        self.entity.amplitude_drive = self.amplitude_drive.store()
        self.entity.final_time = self.final_time.store()
        self.entity.final_value = self.final_value.store()
    def draw(self, context):
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.initial_value.draw(layout, "Initial value")
        self.angular_velocity_drive.draw(layout, "Angular velocity")
        self.amplitude_drive.draw(layout, "Amplitude drive")
        self.final_time.draw(layout, "Final time")
        self.final_value.draw(layout, "Final value")
    def check(self, context):
        return True in [v.check(context) for v in [self.initial_time, self.initial_value,
            self.angular_velocity_drive, self.amplitude_drive, self.final_time, self.final_value]]
    def create_entity(self):
        return FrequencySweepDrive(self.name)

klasses[FrequencySweepDriveOperator.bl_label] = FrequencySweepDriveOperator

class ExponentialDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "exponential"
        for v in [self.amplitude, self.time_constant, self.initial_time, self.initial_value]:
            ret += ", " + BPY.FORMAT(v)
        return ret

class ExponentialDriveOperator(Base):
    bl_label = "Exponential drive"
    amplitude = bpy.props.PointerProperty(type = BPY.Float)
    time_constant = bpy.props.PointerProperty(type = BPY.Float)
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    initial_value = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.amplitude.mandatory = True
        self.time_constant.mandatory = True
        self.initial_time.mandatory = True
        self.initial_value.mandatory = True
    def assign(self, context):
        self.amplitude.assign(self.entity.amplitude)
        self.time_constant.assign(self.entity.time_constant)
        self.initial_time.assign(self.entity.initial_time)
        self.initial_value.assign(self.entity.initial_value)
    def store(self, context):
        self.entity.amplitude = self.amplitude.store()
        self.entity.time_constant = self.time_constant.store()
        self.entity.initial_time = self.initial_time.store()
        self.entity.initial_value = self.initial_value.store()
    def draw(self, context):
        layout = self.layout
        self.amplitude.draw(layout, "Amplitude")
        self.time_constant.draw(layout, "Time constant")
        self.initial_time.draw(layout, "Initial time")
        self.initial_value.draw(layout, "Initial value")
    def check(self, context):
        return True in [v.check(context) for v in [self.amplitude, self.time_constant, self.initial_time, self.initial_value]]
    def create_entity(self):
        return ExponentialDrive(self.name)

klasses[ExponentialDriveOperator.bl_label] = ExponentialDriveOperator

class RandomDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "random"
        for v in [self.amplitude, self.mean, self.initial_time]:
            ret += ", " + BPY.FORMAT(v)
        if self.final_time is None:
            ret += ", forever"
        else:
            ret += ", " + BPY.FORMAT(self.final_time)
        ret += ", steps, " + BPY.FORMAT(self.steps)
        if self.seed_type == "time_seed":
            ret += ", seed, time"
        else:
            ret += ", seed, " + BPY.FORMAT(self.specified_seed)
        return ret

class RandomDriveOperator(Base):
    bl_label = "Random drive"
    amplitude = bpy.props.PointerProperty(type = BPY.Float)
    mean = bpy.props.PointerProperty(type = BPY.Float)
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    final_time = bpy.props.PointerProperty(type = BPY.Float)
    steps = bpy.props.PointerProperty(type = BPY.Float)
    seed_type = bpy.props.EnumProperty(items=[("time_seed", "Time seed", ""), ("specified_seed", "Specified seed", "")], name="Seed type", default="specified_seed")
    specified_seed = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.amplitude.mandatory = True
        self.mean.mandatory = True
        self.initial_time.mandatory = True
        self.steps.mandatory = True
        self.specified_seed.mandatory = True
    def assign(self, context):
        self.amplitude.assign(self.entity.amplitude)
        self.mean.assign(self.entity.mean)
        self.initial_time.assign(self.entity.initial_time)
        self.final_time.assign(self.entity.final_time)
        self.steps.assign(self.entity.steps)
        self.seed_type = self.entity.seed_type
        self.specified_seed.assign(self.entity.specified_seed)
    def store(self, context):
        self.entity.amplitude = self.amplitude.store()
        self.entity.mean = self.mean.store()
        self.entity.initial_time = self.initial_time.store()
        self.entity.final_time = self.final_time.store()
        self.entity.steps = self.steps.store()
        self.entity.seed_type = self.seed_type
        self.entity.specified_seed = self.specified_seed.store() if self.seed_type == "specified_seed" else None
    def draw(self, context):
        self.basis = self.seed_type
        layout = self.layout
        self.amplitude.draw(layout, "Amplitude")
        self.mean.draw(layout, "Mean")
        self.initial_time.draw(layout, "Initial time")
        self.final_time.draw(layout, "Final time")
        self.steps.draw(layout, "Steps")
        layout.prop(self, "seed_type")
        if self.seed_type == "specified_seed":
            self.specified_seed.draw(layout, "Specified seed")
    def check(self, context):
        return (self.basis != self.seed_type) or True in [v.check(context) for v in [self.amplitude, self.mean, self.initial_time, self.final_time, self.steps, self.specified_seed]]
    def create_entity(self):
        return RandomDrive(self.name)

klasses[RandomDriveOperator.bl_label] = RandomDriveOperator

class MeterDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "meter, " + BPY.FORMAT(self.initial_time)
        if self.final_time is None:
            ret += ", forever"
        else:
            ret += ", " + BPY.FORMAT(self.final_time)
        ret += ", steps, " + BPY.FORMAT(self.steps)
        return ret

class MeterDriveOperator(Base):
    bl_label = "Meter drive"
    initial_time = bpy.props.PointerProperty(type = BPY.Float)
    final_time = bpy.props.PointerProperty(type = BPY.Float)
    steps = bpy.props.PointerProperty(type = BPY.Int)
    def prereqs(self, context):
        self.initial_time.mandatory = True
        self.steps.mandatory = True
        self.steps.assign(1)
    def assign(self, context):
        self.initial_time.assign(self.entity.initial_time)
        self.final_time.assign(self.entity.final_time)
        self.steps.assign(self.entity.steps)
    def store(self, context):
        self.entity.initial_time = self.initial_time.store()
        self.entity.final_time = self.final_time.store()
        self.entity.steps = self.steps.store()
    def draw(self, context):
        layout = self.layout
        self.initial_time.draw(layout, "Initial time")
        self.final_time.draw(layout, "Final time")
        self.steps.draw(layout, "Steps")
    def check(self, context):
        return True in [v.check(context) for v in [self.initial_time, self.final_time, self.steps]]
    def create_entity(self):
        return MeterDrive(self.name)

klasses[MeterDriveOperator.bl_label] = MeterDriveOperator

class StringDrive(Entity):
    dimension = "1D"
    def string(self):
        return "string, \"" + self.expression_string + "\""

class StringDriveOperator(Base):
    bl_label = "String drive"
    expression_string = bpy.props.PointerProperty(type = BPY.Str)
    def prereqs(self, context):
        self.expression_string.mandatory = True
    def assign(self, context):
        self.expression_string.assign(self.entity.expression_string)
    def store(self, context):
        self.entity.expression_string = self.expression_string.store()
    def draw(self, context):
        layout = self.layout
        self.expression_string.draw(layout, "Expression")
    def check(self, context):
        return self.expression_string.check(context)
    def create_entity(self):
        return StringDrive(self.name)

klasses[StringDriveOperator.bl_label] = StringDriveOperator

class MultDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "mult"
        ret += ",\n\t\treference, " + self.drive_1.safe_name()
        ret += ",\n\t\treference, " + self.drive_2.safe_name()
        return ret

class MultDriveOperator(Base):
    bl_label = "Mult drive"
    drive_1 = bpy.props.PointerProperty(type = BPY.Drive)
    drive_2 = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.drive_1.mandatory = True
        self.drive_2.mandatory = True
    def assign(self, context):
        self.drive_1.assign(self.entity.drive_1)
        self.drive_2.assign(self.entity.drive_2)
    def store(self, context):
        self.entity.drive_1 = self.drive_1.store()
        self.entity.drive_2 = self.drive_2.store()
    def draw(self, context):
        layout = self.layout
        self.drive_1.draw(layout, "Drive 1")
        self.drive_2.draw(layout, "Drive 2")
    def check(self, context):
        return self.drive_1.check(context) or self.drive_2.check(context)
    def create_entity(self):
        return MultDrive(self.name)

klasses[MultDriveOperator.bl_label] = MultDriveOperator

class NodeDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "node"
        if self.objects[0] in database.node:
            ob = self.objects[0]
        elif self.objects[0] in database.rigid_dict:
            ob = database.rigid_dict[self.objects[0]]
        else:
            wm = bpy.context.window_manager
            wm.popup_menu(lambda self, c: self.layout.label(
                "Error: Node drive " + self.name + " is not assigned to a node"), title="MBDyn Error", icon='ERROR')
            print("Error: Node drive " + self.name + " is not assigned to a node")
            return
        if ob in database.node:
            ret += ", " + safe_name(ob.name) + ", structural"
        if self.symbolic_name:
            ret += ", string, \"" + BPY.FORMAT(self.symbolic_name) + "\""
        ret += ",\n\t\treference, " + self.drive.safe_name()
        return ret

class NodeDriveOperator(Base):
    bl_label = "Node drive"
    symbolic_name = bpy.props.PointerProperty(type = BPY.Str)
    drive = bpy.props.PointerProperty(type = BPY.Drive)
    @classmethod
    def poll(cls, context):
        obs = SelectedObjects(context)
        return cls.bl_idname.startswith(root_dot + "e_") or len(obs) == 1
    def prereqs(self, context):
        self.symbolic_name.mandatory = True
        self.drive.mandatory = True
    def assign(self, context):
        self.symbolic_name.assign(self.entity.symbolic_name)
        self.drive.assign(self.entity.drive)
    def store(self, context):
        self.entity.objects = SelectedObjects(context)
        self.entity.symbolic_name = self.symbolic_name.store()
        self.entity.drive = self.drive.store()
    def draw(self, context):
        layout = self.layout
        self.symbolic_name.draw(layout, "Symbolic name")
        self.drive.draw(layout, "Drive")
    def check(self, context):
        return self.symbolic_name.check(context) or self.drive.check(context)
    def create_entity(self):
        return NodeDrive(self.name)

klasses[NodeDriveOperator.bl_label] = NodeDriveOperator

class ElementDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "element, " + self.element.safe_name() + ", " + self.element.type
        if self.symbolic_name:
            ret += ", string, \"" + self.symbolic_name + "\""
        ret += ",\n\t\treference, " + self.drive.safe_name()
        return ret

class ElementDriveOperator(Base):
    bl_label = "Structural node drive"
    element = bpy.props.PointerProperty(type = BPY.Element)
    symbolic_name = bpy.props.PointerProperty(type = BPY.Str)
    drive = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.element.mandatory = True
        self.symbolic_name.mandatory = True
        self.drive.mandatory = True
    def assign(self, context):
        self.element.assign(self.entity.element)
        self.symbolic_name.assign(self.entity.symbolic_name)
        self.drive.assign(self.entity.drive)
    def store(self, context):
        self.entity.element = self.element.store()
        self.entity.symbolic_name = self.symbolic_name.store()
        self.entity.drive = self.drive.store()
    def draw(self, context):
        layout = self.layout
        self.element.draw(layout, "Element")
        self.symbolic_name.draw(layout, "Symbol")
        self.drive.draw(layout, "Drive")
    def check(self, context):
        return self.element.check(context) or self.symbolic_name.check(context) or self.drive.check(context)
    def create_entity(self):
        return ElementDrive(self.name)

klasses[ElementDriveOperator.bl_label] = ElementDriveOperator

class DriveDrive(Entity):
    dimension = "1D"
    def string(self):
        ret = "drive"
        ret += ",\n\t\treference, " + self.drive_1.safe_name()
        ret += ",\n\t\treference, " + self.drive_2.safe_name()
        return ret

class DriveDriveOperator(MultDriveOperator):
    bl_label = "Drive drive"
    def create_entity(self):
        return DriveDrive(self.name)

klasses[DriveDriveOperator.bl_label] = DriveDriveOperator

bundle = Bundle(drive_tree, Base, klasses, database.drive)
