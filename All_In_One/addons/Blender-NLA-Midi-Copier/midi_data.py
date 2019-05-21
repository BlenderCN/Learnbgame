from .midi_analysis.Note import Note
from .midi_analysis.MidiData import MidiData

midi_data = None
# api documentation says that references to the values returned by callbacks need to be kept around to prevent issues
track_list = []  # list of tracks in the midi file
notes_list = []  # list of notes for the selected midi track
instruments_list = []  # list of defined instruments
instrument_notes_list = []  # list of notes for the selected instrument
instrument_note_actions_list = []  # list of actions for the selected note of the selected instrument
notes_list_dict = {}  # key is track id String, value is list of note properties

current_midi_filename = None
NO_INSTRUMENT_SELECTED = "[No Instrument Selected]"


def update_midi_file(midi_filename, force_update):
    """
    Updates the current midi file
    :param force_update: if true will reload the midi file even if it has the same name
    :param midi_filename: path to the midi file
    """
    global midi_data
    global notes_list_dict
    global track_list
    global current_midi_filename
    if midi_filename is None:
        midi_data = None
        return
    elif midi_filename == current_midi_filename and not force_update:
        return
    current_midi_filename = midi_filename
    midi_data = MidiData(midi_filename)

    def note_pitch_from_string(pitch_string):
        for int_pitch, string in Note.PITCH_DICTIONARY.items():
            if string == pitch_string:
                return int_pitch
        return 0

    def get_unique_name(name, name_list):
        if name not in name_list:
            return name
        else:
            number = 2
            unique_name = name + " (" + str(number) + ")"
            while unique_name in name_list:
                number += 1
                unique_name = name + " (" + str(number) + ")"
            return unique_name

    notes_list_dict = {}
    tracks = []
    track_list = []
    for track in midi_data.tracks:
        if len(track.notes) > 0:
            track_name = get_unique_name(track.name, tracks)
            notes_list_set = {Note.PITCH_DICTIONARY[x.pitch] for x in track.notes}
            notes_list_set_sorted = sorted(notes_list_set, key=lambda x: note_pitch_from_string(x))
            notes_list_dict[track_name] = [(x, x, x) for x in notes_list_set_sorted]
            tracks.append(track_name)
    tracks.sort()
    track_list = [(x, x, x) for x in tracks]


# noinspection PyUnusedLocal
def get_tracks_list(self, context):
    """
    :return: list of tracks in the current midi file
    """
    global track_list
    return track_list


# noinspection PyUnusedLocal
def get_notes_list(self, context):
    """
    :return: list of notes for the current selected track
    """
    global midi_data
    global notes_list
    track_id = context.scene.midi_data_property.track_list
    notes_list = notes_list_dict.get(track_id, [])
    return notes_list


def get_track_id(context):
    return context.scene.midi_data_property.track_list


def get_note_id(context):
    return context.scene.midi_data_property.notes_list


def get_instruments(midi_data_property, context):
    global instruments_list
    instruments_list.clear()
    for i in range(len(midi_data_property.instruments)):
        instrument = midi_data_property.instruments[i]
        # identifier is the index of the instrument in midi_data_property.instruments
        # explicitly define the number so that if a rename changes the position in the returned list,
        # the selected instrument is preserved
        instruments_list.append((str(i), instrument.name, instrument.name, i + 1))
    # instruments_list = [(x.name, x.name, x.name) for x in midi_data_property.instruments]
    # instruments_list.sort()
    instruments_list.sort(key=lambda x: x[1].lower())
    instruments_list.insert(0, (NO_INSTRUMENT_SELECTED, "", "No Instrument Selected", 0))

    return instruments_list


def get_instrument_notes(instrument_property, context):
    instrument_notes_dictionary = {}
    for x in instrument_property.notes:
        instrument_notes_dictionary[x.note_id] = len(x.actions)
    instrument_notes_list.clear()
    for key, value in Note.PITCH_DICTIONARY.items():
        note_display = value
        if key in instrument_notes_dictionary:
            action_count_for_note = instrument_notes_dictionary.get(key)
            note_display += " (" + str(action_count_for_note) + ")"
        instrument_notes_list.append((str(key), note_display, note_display))
    return instrument_notes_list


def selected_instrument(context):
    instrument_id = context.scene.midi_data_property.selected_instrument_id
    if instrument_id is not None and len(instrument_id) > 0 \
            and instrument_id != NO_INSTRUMENT_SELECTED:
        return context.scene.midi_data_property.instruments[int(instrument_id)]
    return None


# key is display name, value is (NoteActionProperty field name, Action id_root)
ID_PROPERTIES_DICTIONARY = {"Armature": ("armature", "ARMATURE"),
                            "Camera": ("camera", "CAMERA"),
                            # "Cache File": ("cachefile", "CACHEFILE"),
                            "Curve": ("curve", "CURVE"),
                            # "Grease Pencil": ("greasepencil", "GREASEPENCIL"),
                            "Key": ("key", "KEY"),
                            "Lattice": ("lattice", "LATTICE"),
                            "Light": ("light", "LIGHT"),
                            "Light Probe": ("light_probe", "LIGHT_PROBE"),
                            "Mask": ("mask", "MASK"),
                            "Material": ("material", "MATERIAL"),
                            "MetaBall": ("meta", "META"),
                            "Mesh": ("mesh", "MESH"),
                            "Movie Clip": ("movieclip", "MOVIECLIP"),
                            # "Node Tree": ("nodetree", "NODETREE"),
                            "Object": ("object", "OBJECT"),
                            "Scene": ("scene", "SCENE"),
                            "Speaker": ("speaker", "SPEAKER"),
                            "Texture": ("texture", "TEXTURE"),
                            "World": ("world", "WORLD")}

# node trees don't show up in the selector,
# so applying an action is done by selecting the object the node tree belongs to
note_tree_types = "MATERIAL, TEXTURE, WORLD, SCENE, LIGHT"
