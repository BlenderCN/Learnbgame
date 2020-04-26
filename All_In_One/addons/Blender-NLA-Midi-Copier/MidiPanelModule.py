if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NLAMidiCopierModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(MidiInstrumentModule)
else:
    from . import midi_data
    # noinspection PyUnresolvedReferences
    from . import NLAMidiCopierModule
    # noinspection PyUnresolvedReferences
    from . import MidiInstrumentModule

import bpy
from .NLAMidiCopierModule import NLAMidiCopier, NLAMidiInstrumentCopier
from .MidiInstrumentModule import AddInstrument, DeleteInstrument, AddActionToInstrument, RemoveActionFromInstrument, \
    TransposeInstrument
from . import midi_data
from bpy.props import EnumProperty


class MidiFileSelector(bpy.types.Operator):
    bl_idname = "ops.midi_file_selector"
    bl_label = "Midi File Selector"
    # noinspection PyArgumentList
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.midi_data_property["midi_file"] = self.filepath
        try:
            midi_data.update_midi_file(self.filepath, True)
        except Exception as e:
            self.report({"WARNING"}, "Could not load midi file: " + str(e))
            context.scene.midi_data_property["midi_file"] = ""
            midi_data.update_midi_file(None, False)

        return {'FINISHED'}

    # noinspection PyUnusedLocal
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MidiPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi"
    bl_label = "NLA Midi"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator(MidiFileSelector.bl_idname, text="Choose midi file", icon='FILE_FOLDER')

        midi_data_property = context.scene.midi_data_property
        midi_file = midi_data_property.midi_file
        if midi_data_property.midi_file:
            try:
                midi_data.update_midi_file(midi_data_property.midi_file, False)
                col.prop(midi_data_property, "midi_file")

                col.prop(midi_data_property, "track_list")
                col.prop(midi_data_property, "notes_list")
            except Exception as e:
                print("Could not load midi file: " + str(e))
                midi_data.update_midi_file(None, False)

        note_action_property = midi_data_property.note_action_property

        MidiPanel.draw_note_action_common(self.layout, col, note_action_property, midi_data_property)

        self.layout.separator()

        if midi_file:
            col = self.layout.column(align=True)
            col.enabled = note_action_property.action is not None
            col.operator(NLAMidiCopier.bl_idname, icon='FILE_SOUND')

    @staticmethod
    def draw_note_action_common(parent_layout, col, note_action_property, midi_data_property=None):
        is_main_property = midi_data_property is not None
        col.prop(note_action_property, "id_type")
        if note_action_property.id_type is not None:
            col.prop(note_action_property, midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0])
            col.prop(note_action_property, "action")

        parent_layout.separator()

        col = parent_layout.column(align=True)
        col.enabled = note_action_property.id_type == "Object"
        if is_main_property:
            col.prop(note_action_property, "copy_to_selected_objects")
        col.prop(note_action_property, "duplicate_object_on_overlap")

        col = parent_layout.column(align=True)
        col.prop(note_action_property, "nla_track_name")
        if is_main_property:
            col.prop(midi_data_property, "midi_frame_start")
        col.prop(note_action_property, "midi_frame_offset")
        if note_action_property.action is not None:
            col.prop(note_action_property, "action_length")


class MidiInstrumentPanel(bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"
    bl_category = "Midi Instruments"
    bl_label = "NLA Midi Instruments"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene.midi_data_property, "selected_instrument_id")

        instrument_id = context.scene.midi_data_property.selected_instrument_id
        if instrument_id is not None and len(instrument_id) > 0 \
                and instrument_id != midi_data.NO_INSTRUMENT_SELECTED:
            instrument = context.scene.midi_data_property.instruments[int(instrument_id)]
            self.draw_instrument_properties(instrument)
            self.draw_instrument_notes(instrument)
            self.draw_animate_instrument(context, instrument)

        self.layout.separator()
        col = self.layout.column(align=True)
        col.operator(AddInstrument.bl_idname)

    def draw_animate_instrument(self, context, instrument):
        if context.scene.midi_data_property.midi_file:
            try:
                midi_data.update_midi_file(context.scene.midi_data_property.midi_file, False)
                animate_box = self.layout.box()
                MidiInstrumentPanel.draw_expand_handle(animate_box, "Animate " + instrument.name, instrument,
                                                       "animate_expanded")
                if instrument.animate_expanded:
                    animate_box.prop(instrument, "selected_midi_track")
                    animate_box.operator(NLAMidiInstrumentCopier.bl_idname, text="Animate " + instrument.name)
            except Exception as e:
                print("Could not load midi file: " + str(e))
                midi_data.update_midi_file(None, False)

    def draw_instrument_notes(self, instrument):
        notes_box = self.layout.box()
        MidiInstrumentPanel.draw_expand_handle(notes_box, instrument.name + " Notes", instrument, "notes_expanded")
        if instrument.notes_expanded:
            notes_box.prop(instrument, "selected_note_id")
            notes_box.operator(AddActionToInstrument.bl_idname)
            note_id = int(instrument.selected_note_id)
            instrument_note_property = next((x for x in instrument.notes if x.note_id == note_id), None)
            if instrument_note_property is not None:
                for i in range(len(instrument_note_property.actions)):
                    self.draw_action(instrument_note_property.actions[i], i, notes_box)

    def draw_instrument_properties(self, instrument):
        box = self.layout.box()
        row = box.row()

        MidiInstrumentPanel.draw_expand_handle(row, instrument.name + " Properties", instrument, "properties_expanded")
        if instrument.properties_expanded:
            box.prop(instrument, "name")
            box.prop(instrument, "default_midi_frame_offset")
            col = box.column(align=True)
            col.label(text="Transpose:")
            transpose_row = col.row()
            MidiInstrumentPanel.draw_transpose_operator(instrument, -12, "- octave", transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, -1, "- step", transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, +1, "+ step", transpose_row)
            MidiInstrumentPanel.draw_transpose_operator(instrument, +12, "+ octave", transpose_row)
            box.operator(DeleteInstrument.bl_idname, text="Delete " + instrument.name)

    @staticmethod
    def draw_transpose_operator(instrument, steps: int, text: str, row: bpy.types.UILayout):
        col = row.column(align=True)
        transpose_operator = col.operator(TransposeInstrument.bl_idname, text=text)
        transpose_operator.transpose_steps = steps
        col.enabled = MidiInstrumentPanel.can_transpose(instrument, steps)

    @staticmethod
    def can_transpose(instrument, steps):
        min_note = 0 - steps
        max_note = 127 - steps
        return next((x for x in instrument.notes if x.note_id < min_note or x.note_id > max_note), None) is None

    def draw_action(self, action, action_index: int, parent: bpy.types.UILayout) -> None:
        box = parent.box()
        row = box.row()
        MidiInstrumentPanel.draw_expand_handle(row, action.name, action, "expanded")
        remove_operator = row.operator(RemoveActionFromInstrument.bl_idname, icon='CANCEL', text='')
        remove_operator.action_index = action_index

        if action.expanded:
            box.prop(action, "name")
            MidiPanel.draw_note_action_common(box, box.column(align=True), action)

    @staticmethod
    def draw_expand_handle(parent: bpy.types.UILayout, text: str, object_with_property, expand_property_field: str):
        parent.prop(object_with_property, expand_property_field, text=text,
                    icon="TRIA_DOWN" if getattr(object_with_property, expand_property_field) else "TRIA_RIGHT",
                    icon_only=True, emboss=False)
