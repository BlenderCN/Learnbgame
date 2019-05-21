# <pep8-80 compliant>
import bpy
from bpy.utils import preset_find, preset_paths
from bpy.types import Menu, Operator
from bpy.props import FloatProperty, EnumProperty
from bl_operators.presets import AddPresetBase
from math import log
import os

# TODO needs refactoring to start at C
notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
midi_instruments = [
    "acoustic guitar (nylon)",
    "acoustic guitar (steel)",
    "electric guitar (jazz)",
    "electric guitar (clean)",
    "electric guitar (muted)",
    "overdriven guitar",
    "distorted guitar",
    "guitar fret noise",
    "acoustic bass",
    "electric bass (finger)",
    "electric bass (pick)",
    "fretless bass",
    "slap bass 1",
    "slap bass 2",
    "synth bass 1",
    "synth bass 2",
    "acoustic grand",
    "bright acoustic",
    "electric grand",
    "honky-tonk",
    "electric piano 1",
    "electric piano 2",
    "harpsichord",
    "clav",
    "celesta",
    "glockenspiel",
    "music box",
    "vibraphone",
    "marimba",
    "xylophone",
    "tubular bells",
    "dulcimer",
    "drawbar organ",
    "percussive organ",
    "rock organ",
    "church organ",
    "reed organ",
    "accordion",
    "harmonica",
    "concertina",
    "violin",
    "viola",
    "cello",
    "contrabass",
    "tremolo strings",
    "pizzicato strings",
    "orchestral harp",
    "timpani",
    "string ensemble 1",
    "string ensemble 2",
    "synthstrings 1",
    "synthstrings 2",
    "choir aahs",
    "voice oohs",
    "synth voice",
    "orchestra hit",
    "trumpet",
    "trombone",
    "tuba",
    "muted trumpet",
    "french horn",
    "brass section",
    "synthbrass 1",
    "synthbrass 2",
    "soprano sax",
    "alto sax",
    "tenor sax",
    "baritone sax",
    "oboe",
    "english horn",
    "bassoon",
    "clarinet",
    "piccolo",
    "flute",
    "recorder",
    "pan flute",
    "blown bottle",
    "shakuhachi",
    "whistle",
    "ocarina",
    "lead 1 (square)",
    "lead 2 (sawtooth)",
    "lead 3 (calliope)",
    "lead 4 (chiff)",
    "lead 5 (charang)",
    "lead 6 (voice)",
    "lead 7 (fifths)",
    "lead 8 (bass+lead)",
    "pad 1 (new age)",
    "pad 2 (warm)",
    "pad 3 (polysynth)",
    "pad 4 (choir)",
    "pad 5 (bowed)",
    "pad 6 (metallic)",
    "pad 7 (halo)",
    "pad 8 (sweep)",
    "fx 1 (rain)",
    "fx 2 (soundtrack)",
    "fx 3 (crystal)",
    "fx 4 (atmosphere)",
    "fx 5 (brightness)",
    "fx 6 (goblins)",
    "fx 7 (echoes)",
    "fx 8 (sci-fi)",
    "sitar",
    "banjo",
    "shamisen",
    "koto",
    "kalimba",
    "bagpipe",
    "fiddle",
    "shanai",
    "tinkle bell",
    "agogo",
    "steel drums",
    "woodblock",
    "taiko drum",
    "melodic tom",
    "synth drum",
    "reverse cymbal",
    "breath noise",
    "seashore",
    "bird tweet",
    "telephone ring",
    "helicopter",
    "applause",
    "gunshot",
]


def note_from_freq(freq):
    steps = round(12 * log(freq / 27.5, 2))
    octave = max((steps + 9) // 12, 0)
    steps = steps % 12
    note = notes[steps]
    return "%s%d" % (note, octave)


def freq_from_note(note):
    octave = note[-1]
    step = notes.index(note[:-1])


def start(self, context):
    op = bpy.types.Scene.soundtool_op
    is_valid = op is not None
    if is_valid:
        op.minf = self.start


class SPEAKER_OT_GUI(Operator):
    bl_idname = "speaker.gui"
    bl_label = "Music GUI"
    start = FloatProperty(default=88.0)
    end = FloatProperty(default=5500.0)

    def execute(self, context):
        SOUND_MT_Music_Notes.bl_label = "XXX"
        return {'FINISHED'}
        op = bpy.types.Scene.soundtool_op
        is_valid = op is not None
        if is_valid:
            note = note_from_freq(self.start)
            op.minf = self.start
        return {'FINISHED'}


class SOUND_MT_Music_Notes(Menu):
    bl_idname = "sound.music_notes"
    bl_label = "Choose a note"

    def draw(self, context):
        layout = self.layout
        octave = 0
        for note in range(0, 88):
            name = notes[note % 12]
            if name == "C":
                octave += 1  # Go up an octave
                row = layout.row()
                row.separator()
                row = layout.row()
                row.label("%dth Octave" % octave, icon='SOUND')
            freq = 27.5 * 2 ** (note / 12.0)
            name = "%4s  (%5.2fHz)" % (name, freq)
            layout.operator("speaker.gui", text=name).start = freq


class SPEAKER_MT_Presets(Menu):
    bl_idname = "speaker.preset_menu"
    bl_label = "Choose a preset"
    preset_operator = "script.execute_preset"
    preset_subdir = "sound_drivers.bake_settings"
    draw = bpy.types.Menu.draw_preset

    '''
    def draw(self, context):
        def icon(type):
            if type == 'SFX':
                return 'SOUND'
            else:
                return 'SPEAKER'

        sound = getattr(context.object.data, 'sound', None)
        count = 0
        layout = self.layout
        path = os.path.join('operator', 'speaker.visualise')
        paths = preset_paths(path)
        # draw a menu
        for directory in paths:
            directory = os.path.join(directory, sound.type)
            if not os.path.isdir(directory):
                continue
            psts = os.listdir(directory)
            for f in psts:
                count += 1
                if count == 1:
                    layout.label(text=sound.type, icon=icon(sound.type))
                    layout.separator()
                pres = os.path.splitext(f)[0]
                layout.operator('speaker.visualise', text=pres).preset = pres
        if count == 0:
            layout.label("None")
    '''


class AddPresetSoundToolOperator(AddPresetBase, Operator):
    '''Add an Application Interaction Preset'''
    bl_idname = "wm.soundtool_operator_preset_add"
    bl_label = "Operator Preset"
    preset_menu = "speaker.preset_menu"

    name = bpy.props.StringProperty(
        name="Name",
        description="Name of the preset, used to make the path name",
        maxlen=64,
        options={'SKIP_SAVE'},
        )

    preset_defines = [
        "scene = bpy.context.scene",
        "speaker = bpy.context.speaker",
        "sound = speaker.sound",
        "bakeoptions = sound.bakeoptions",
        "bake_op = bakeoptions.bake_operator",
    ]

    preset_subdir = "sound_drivers.bake_settings"

    preset_values = [
            "bakeoptions.sound_type",
            "bakeoptions.channels",
            "bakeoptions.minf",
            "bakeoptions.maxf",
            "bakeoptions.use_log",
            "bakeoptions.auto_adjust",
            "bakeoptions.music_start_note",
            "bakeoptions.music_end_note",
            "bake_op.threshold",
            "bake_op.release",
            "bake_op.attack",
            "bake_op.use_additive",
            "bake_op.use_accumulate",
            "bake_op.use_square",
            "bake_op.sthreshold",
            ]


def note_items():
    octave = 0
    note_list = []
    for note in range(0, 88):
        name = notes[note % 12]
        if name == "C":
            octave += 1  # Go up an octave
        freq = 27.5 * 2 ** (note / 12.0)

        #name = "%s%d (%.2f)" % (name, octave, freq)
        name = "%s%d" % (name, octave)
        note_list.append((name, name, "%.4f" % freq))
    return note_list


def freq_ranges(a, b):
    m = note_items()
    l = [n for n, n, f in m]
    a = l.index(a)
    b = l.index(b)

    r = [(float(f), float(f))
         for n, (c, c, f) in enumerate(m)
         if n >= a and n <= b]

    return r


def shownote(self, context):
    '''
    if self.bl_rna.name == "BakeOptions":
        print("BAKEOPTIONS")
    '''
    if self.sound_type != 'MUSIC':
        return None
    l = note_items()
    s = [(n, k) for n, (i, j, k) in enumerate(l) if i == self.music_start_note]
    a = s[0][0]
    s = [(n, k) for n, (i, j, k) in enumerate(l) if i == self.music_end_note]
    b = s[0][0]

    m = b - a + 1

    if m < 1:
        self.music_end_note = self.music_start_note
        m = 1
    self.channels = m

    return None
    global notes
    idx = notes.index(name)

    octave = int(self.music_start_note[-1:])

    if idx > 2:
        octave = max(0, octave - 1)

    note = octave * 12 + idx

    freq = 27.5 * 2 ** (note / 12.0)

notes_enum = EnumProperty(name="notelist", items=note_items(), default="A4",
                     update=shownote)


def register():
    bpy.utils.register_class(SOUND_MT_Music_Notes)
    bpy.utils.register_class(SPEAKER_MT_Presets)
    bpy.utils.register_class(SPEAKER_OT_GUI)
    bpy.utils.register_class(AddPresetSoundToolOperator)


def unregister():
    bpy.utils.unregister_class(SOUND_MT_Music_Notes)
    bpy.utils.unregister_class(SPEAKER_MT_Presets)
    bpy.utils.unregister_class(SPEAKER_OT_GUI)
    bpy.utils.unregister_class(AddPresetSoundToolOperator)
