bl_info = {
    "name": "Midi Support",
    "author": "batFINGER",
    "location": "Properties > Speaker > MIDI",
    "description": "Midi support for Sound Drivers",
    "warning": "Still in Testing",
    "wiki_url": "http://wiki.blender.org/index.php/\
                User:BatFINGER/Addons/Sound_Drivers",
    "version": (1, 0),
    "blender": (2, 7, 6),
    "tracker_url": "",
    "icon": 'MIDI',
    "support": 'TESTING',
    "category": "Learnbgame",
}

import bpy

import json
from bpy.types import PropertyGroup, Operator, AddonPreferences
from bpy.utils import register_class, unregister_class
# make a midifiles collection property on sound
from bpy_extras.io_utils import ImportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       CollectionProperty,
                       PointerProperty,
                       EnumProperty)
                       
from sound_drivers.utils import(getSpeaker,
                                set_channel_idprop_rna,
                                unique_name,
                                scale_actions,
                                nla_drop)

from sound_drivers.presets import note_items, midi_instruments

# Using addonpreset system to save usersettings on a submodulare basis

smf_paths = set()
class MIDIAddonPreferences(AddonPreferences):
    ''' MIDI Prefs '''
    bl_idname = __name__

    @property
    def midi_support(self):
        '''
        check if there is smf midi support using importlib.util.find_spec
        '''
        import sys
        if self.smf_dir and self.smf_dir not in sys.path:
            smf_paths.add(self.smf_dir)
            sys.path.append(self.smf_dir)
        from importlib.util import find_spec 
        return find_spec("smf") is not None

    smf_dir = StringProperty(
            name="smf (midi) python path",
            description="folder where smf is installed",
            subtype='DIR_PATH',
            )

    def draw(self, context):
        layout = self.layout
        # check that automatic scripts are enabled
        
        # midi support
        if True: # self.midi_support:
            row = layout.row()
            row.label("midi_support", icon='FILE_TICK' if self.midi_support else 'ERROR')
            row = layout.row()
            row.enabled = not self.midi_support
            row.prop(self, "smf_dir")
            row = layout.row()
            op = row.operator("wm.url_open", icon='INFO', text="GitHub PySMF Project (Cython)")
            op.url="https://github.com/dsacre/pysmf"


notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
octaves = range(-1, 10)

midi_notes = ["%s%d" % (n, o) for o in octaves for n in notes]
#pop off the last 4

for i in range(4):
    midi_notes.pop()
    
def notesplit(s):
    notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', '#']
    i = 0
    while s[i] in notes:
        i += 1
    return (s[:i], int(s[i:]))  # (note, octave)

midifile = {}

def peek_midi_file(context, filepath, use_some_setting):
    print(filepath)
    prefs = context.user_preferences.addons["sound_drivers"].preferences
    #import sys
    #sys.path.append(prefs.smf_dir)
    import smf
    pin_id = getattr(context.space_data, "pin_id", None)
    sp = pin_id if pin_id is not None else context.object.data
    sound = sp.sound  
    
    f = smf.SMF(filepath)
    midi = {}
    tracks = {}
    for t in f.tracks:
        track = {} 
        for e in t.events:
            #print(e.decode(), e.time_seconds)
            s = e.decode()
            #print(s.startswith("Note"))
            
            if s.startswith("Instrument"):
                #print("INSTRUMENT", s)
                track["name"] = "Track %d" % (t.track_number)
                track["index"] = t.track_number
                
                track["instrument"] = s.title()
                
            elif s.startswith("Time Signature"):
                track["time_sig"] = s
                
            elif s.startswith("Tempo"):
                track["tempo"] = s
                
            elif s.startswith("Key Signature"):
                print("KEYSIG", s)
                track["keysig"] = s
            elif s.startswith("Program Change"):
                #print("PROGCHA", s)
                # this could be instrument too
                idx = int(s.split(" ")[-1])
                s = midi_instruments[idx]
                track["name"] = "Track %d" % (t.track_number)
                track["instrument"] = s.title() 
                track["index"] = t.track_number               
            elif s.startswith("Controller"):
                continue
                print("CONTROLLER", s)
            elif s.startswith("Pitch Wheel"):
                # do nothing for now
                continue
            elif s.startswith("Note"):
                continue
            elif s.startswith("End Of Track"):
                break
            else:
                #continue
                print("XXX", s)
        if t.track_number == 0:
            midi = track
          
        if track.get("name", False):
            tracks.setdefault(track["name"], track) 
            
    sound.midifile.filepath = filepath
    sound.midifile.tracks.clear()
    
    for k, track in tracks.items():
        t = sound.midifile.tracks.add()
        t.name = track["name"]
        
        t.data_dic = json.dumps(track)
        print("-"*77)
        print(k, tracks[k])
    

    return    
    
def read_midi_file(context, filepath, use_some_setting):
    print(filepath)
    prefs = context.user_preferences.addons["sound_drivers"].preferences
    #import sys
    #sys.path.append(prefs.smf_dir)
    import smf
    pin_id = context.space_data.pin_id
    sp = pin_id if pin_id is not None else context.object.data
    
    channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
    midichannels = []
    f = smf.SMF(filepath)
    tracks = []
    for t in f.tracks:
        print("TRACK : %s" % t.track_number)
        a = {}
        #a = bpy.data.actions.new("MidiAction")
        
        print(channels)
        channel_name = unique_name(channels, 'AA')
        channels.append(channel_name)
        a["name"] = "%s Unknown (trk %d)" % (channel_name, t.track_number)
        a['wavfile'] = sp.sound.name
        a['start'] = 0
        a['end'] = len(midi_notes)
        a['row_height'] = 0.4
        a["Channels"] = 0
        a["channel_name"] = channel_name
        a['MIDI'] = filepath
        #sp.animation_data.action = a
        a["keyframe_points"] = {} # list of tups (dp, frame, value)
        
        '''
        for i, n in enumerate(midi_notes):
            channel = "%s%d" % (channel_name, i)
            sp[channel] = 0
            sp.keyframe_insert('["%s"]' % channel, frame = 0)
            #sp.keyframe_insert('["%s"]' % channel, frame = 0)
            #sp.keyframe_insert('["%s"]' % channel, frame = 0)
        '''
        for e in t.events:
            s = e.decode()
            print("XXXXXXXX", s, e.time_seconds)
            #print(s.startswith("Note"))
            
            if s.startswith("Instrument"):
                print("INSTRUMENT", s)
                a["name"] = "%s:%s (trk %d)" % (channel_name, s.title(), t.track_number)
            elif s.startswith("Key Signature"):
                print("KEYSIG", s)
            elif s.startswith("Program Change"):
                #print("PROGCHA", s)
                # this could be instrument too
                idx = int(s.split(" ")[-1])
                #print(midi_instruments[idx])
                a["name"] = "%s:%s (trk %d)" % (channel_name, midi_instruments[idx].title(), t.track_number)
            elif s.startswith("Controller"):
                continue
                print("CONTROLLER", s)
            elif s.startswith("Pitch Wheel"):
                print("PITCHWEEL", s)
                # do nothing for now
                continue
            elif s.startswith("Note"):
                v = 0
                s = s.replace("Note ", "")
                #print("StartsWithNote", s)
                c = s.split(",")
                #print("CC", c[0])
                v = int(c[3].replace(" velocity ", ""))
                if c[0] == "On":
                    note = c[2].replace(" note ","")
                    print("ON key[%s] = %d @ %fs" % (note, v, e.time_seconds))
                elif c[0] == "Off":
                    v = 0
                    note = c[2].replace(" note ","")
                    print("OFF key[%s] = %d @ %fs" % (note, v, e.time_seconds))
                if note not in midi_notes:
                    print("WARNING: unable to use note %s %d" % notesplit(note))
                    continue
                channel = "%s%i" % (channel_name, midi_notes.index(note))
                fcurve = a["keyframe_points"].setdefault(channel, [])
                fcurve.append(( e.time_seconds * context.scene.render.fps, v))
                #sp[channel] = v
                #a["keyframe_points"].append(('["%s"]' % channel, e.time_seconds * context.scene.render.fps, v))
            else:
                #continue
                print("XXX", s)
        
        if len(a["keyframe_points"].keys()):
            midichannels.append(channel_name)          
            midifile["TRACK : %s" % t.track_number] = a
    
    print(midichannels)
    
    keys = ["name", "wavfile", "start", "end", "row_height", "Channels", "channel_name", "MIDI"]
    actions = []
    channels = []
    action = bpy.data.actions.new("MidiAction")
    sp.animation_data.action = action
    for k, a in midifile.items():
        print("-"*77)
        print(midifile[k]["name"])
        
        tracks = a["keyframe_points"]

        #action = bpy.data.actions.new("MidiAction")
        #sp.animation_data.action = action
        for key in keys:
            action[key] = a[key]
        channel = a["channel_name"]
        channels.append(channel)
        for t in tracks.keys():
            kfps = tracks[t]
            print(t)
            #fc = action.fcurves.new('["%s"]' % t)
            # make the fcurves
            sp[t] = 0
            sp.keyframe_insert('["%s"]' % t, frame=1, group=a["name"])        
            for kfp in kfps:
                f, v = kfp
                sp[t] = v
                sp.keyframe_insert('["%s"]' % t, frame=f, group=a["name"])        
            print("KFPS", t, len(tracks[t]))

    actions.append(action)

    # would normally load the data here

    vals = []
    sp_rna = {}
    for a in actions:

        if len(a.fcurves) <= 1:
            print("NO FCURVES IN ", a.name)
            try:
                del(a["wavfile"])
                a.user_clear()
                actions.remove(a)
                #bpy.data.actions.remove(a)
                #print("REMOVED")
            except:
                print("XCPT")
                continue
            print("WTF")
            continue 

            
        a["Channels"] = len(a.fcurves) 
        a["channels"] = channels
        channel_name = a["channel_name"] 

        for fc in a.fcurves:

            for kp in fc.keyframe_points:
                kp.interpolation = 'CONSTANT'
            fc_range, points = fc.minmax
            cn = fc.data_path.replace('["','').replace('"]', '')
            print(channel_name, cn)
            n = int(cn[2:])
            f = pow(2, (n - 69) / 12.0) * 440
            high = low = f
            vals.extend(list(fc_range))
            rna = sp['_RNA_UI']
            set_channel_idprop_rna(cn,
                                   rna,
                                   low,
                                   high,
                                   fc_range,
                                   fc_range,
                                   is_music=True)        
        
            '''
            vcns = ["%s%d" % (channel_name, i) for i in
                    range(len(midi_notes))]

            '''
        sp_rna = {k: sp['_RNA_UI'][k].to_dict()
                      for k in sp['_RNA_UI'].keys()}
                      # if k in vcns}

        a['rna'] = str(sp_rna)
        a['min'] = min(vals)
        a['max'] = max(vals)

        nla_drop(sp, action, 1, "%s %s" %(channel_name, channel_name))

    return {'FINISHED'}


ts = []
def glonk(self, context):
    peek_midi_file(context, self.filepath, self.use_setting)
    print("GLONK",self.filepath, self.filename)


    
class BakeMIDI(Operator, ImportHelper):
#class BakeMIDI(Operator, ImportHelper):
    """Bake using Midi File"""
    bl_idname = "sound_drivers.import_midi"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Bake MIDI"

    # ImportHelper mixin class uses this
    #filename_ext = ".txt"

    filter_glob = StringProperty(
            default="*.mid;*.midi",
            options={'HIDDEN'},
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="All Tracks",
            description="All Tracks",
            default=True,
            update=glonk
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
           
            )
    filename = StringProperty(update=glonk)
    filepath = StringProperty(
            name="File Path",
            description="Filepath used for importing the file",
            maxlen=1024,
            subtype='FILE_PATH',
            #update=glonk,
            )
    
    def invoke(self, context, event):
        print("INVOKE MIDI")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(self.filename)
        print(self.filename, self.properties.filepath)
        if len(self.filepath):
            layout.prop(self, "use_setting", text="PEEK", toggle=True)
            sound = context.scene.speaker.sound.midifile
            ts = sound.tracks
            for t in ts:
                row = layout.row()
                row.label(t.name)
                row.label(t.instrument)
            layout.operator("file.execute")

    def execute(self, context):
        read_midi_file(context, self.filepath, self.use_setting)
        return {'FINISHED'}
# midi file

class SD_MIDIFilesPanel(bpy.types.Panel):
    """MidFiles Panel"""
    bl_label = "MIDI Files"
    bl_idname = "SOUNDDRIVER_PT_MIDIFiles"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        pin_id = context.space_data.pin_id
        sp = pin_id if pin_id is not None else context.object.data
        return getattr(sp, "sound", False) and 'MIDI' in getattr(sp, "vismode", [])

    def draw_header(self, context):
        from sound_drivers.icons import get_icon
        icon = get_icon("main", "midi")
        self.layout.label("", icon_value=icon.icon_id)

    def draw(self, context):
        sp = getSpeaker(context)
        #sound = sp.sound
        
        layout = self.layout
        
        #layout.prop(sound, "midi_file")
        op = layout.operator("sound_drivers.import_midi")
        #op.filepath = sound.midi_file


def get_value(prop):
    def get(self):
        dic = json.loads(self.data_dic)
        return dic.get(prop)
    return get

def get(self):
    return 4

def regdic():
    propdic = {"data_dic": StringProperty(),
               "index": property(get_value("index")),
               "instrument": property(get_value("instrument")),
               "is_selected": BoolProperty(default=False),
               }
               
    SD_MIDIFileTrack = type("SD_MIDIFileTrack", (PropertyGroup,), propdic)
    register_class(SD_MIDIFileTrack)
    
    propdic = {"filepath": StringProperty(subtype='FILE_PATH'),
               "tracks": CollectionProperty(type=SD_MIDIFileTrack),
              
              }

    SD_MIDIFile = type("SD_MIDIFile", (PropertyGroup,), propdic)
    register_class(SD_MIDIFile)

    bpy.types.Sound.midifile = PointerProperty(type=SD_MIDIFile)
    
    
def register():
    regdic()
    register_class(BakeMIDI)
    register_class(SD_MIDIFilesPanel)

def unregister():
    unregister_class(BakeMIDI)
    unregister_class(SD_MIDIFilesPanel)
    # remove sfm from sys
    if len(smf_paths):
        from sys import path 
        for p in smf_paths:
            if p in path:
                path.remove(p)
                smf_paths.remove(p)
            

if __name__ == "__main__":
    register()
