if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data
import bpy


class AddInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_add_instrument"
    bl_label = "Create New Instrument"
    bl_description = "Create a new instrument.  An instrument defines one or many actions for each note."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instruments = context.scene.midi_data_property.instruments
        new_instrument = instruments.add()
        new_instrument.name = "Instrument " + str(len(instruments))
        context.scene.midi_data_property.selected_instrument_id = str(len(instruments) - 1)


class DeleteInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_delete_instrument"
    bl_label = "Delete Instrument"
    bl_description = "Delete the selected instrument"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        instrument_id = context.scene.midi_data_property.selected_instrument_id
        return instrument_id is not None and \
               len(instrument_id) > 0 and instrument_id != midi_data.NO_INSTRUMENT_SELECTED

    def action_common(self, context):
        instruments = context.scene.midi_data_property.instruments
        selected_instrument_id = context.scene.midi_data_property.selected_instrument_id
        instrument_index = None
        if selected_instrument_id is not None and selected_instrument_id != midi_data.NO_INSTRUMENT_SELECTED:
            instrument_index = int(selected_instrument_id)

        if instrument_index is not None:
            context.scene.midi_data_property.selected_instrument_id = midi_data.NO_INSTRUMENT_SELECTED
            instruments.remove(instrument_index)


class AddActionToInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_add_action_to_instrument"
    bl_label = "Add Action"
    bl_description = "Add an action for the selected note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
        if instrument is not None:

            note_id = int(instrument.selected_note_id)
            instrument_note_property = next((x for x in instrument.notes if x.note_id == note_id), None)
            if instrument_note_property is None:
                instrument_note_property = instrument.notes.add()
                instrument_note_property.note_id = note_id

            note_action_property = instrument_note_property.actions.add()
            note_action_property.name = "Action " + str(len(instrument_note_property.actions))
            note_action_property.midi_frame_offset = instrument.default_midi_frame_offset


class RemoveActionFromInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_remove_action_from_instrument"
    bl_label = "Delete Action"
    bl_description = "Delete action"
    bl_options = {"REGISTER", "UNDO"}

    action_index: bpy.props.IntProperty(name="Index")

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
        if instrument is not None:

            note_id = int(instrument.selected_note_id)
            instrument_note_property = next((x for x in instrument.notes if x.note_id == note_id), None)
            instrument_note_property.actions.remove(self.properties.action_index)

            # don't store an emtpy lst of actions if there are no more actions for the note
            if len(instrument_note_property.actions) == 0:
                index = None
                for i in range(len(instrument.notes)):
                    if instrument.notes[i] == instrument_note_property:
                        index = i
                if index is not None:
                    instrument.notes.remove(index)


class TransposeInstrument(bpy.types.Operator):
    bl_idname = "ops.nla_midi_transpose_instrument"
    bl_label = "Transpose Instrument"
    bl_description = "Transpose Instrument"
    bl_options = {"REGISTER", "UNDO"}

    transpose_steps: bpy.props.IntProperty(name="Transpose Steps")

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
        for note in instrument.notes:
            note.note_id += self.properties.transpose_steps
