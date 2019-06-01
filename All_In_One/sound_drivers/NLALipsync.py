'''
Papagayo lip sync using NLA strips
Need a face or faceControl armature with actions already set up
for each phoneme AI,E,MBP,etc,rest,O,U,FV,WQ
might extend this to have an offset frame set
.. although selecting the track and moving it aint the hardest.
'''

import bpy
import os

from sound_drivers.utils import getAction


def boob(self, context):
    #print(self.papagayo_phonemes)
    return None


def createtracks(object):
    phonemes = ["AI", "E", "MBP", "etc", "rest", "O", "U", "FV", "WQ", "L"]
    tracklist = object.animation_data.nla_tracks
    for p in phonemes:
        if p not in tracklist:
            track = tracklist.new()
            track.name = p


def readPapagayoFile(context, filepath):
    fileName = os.path.realpath(os.path.expanduser(filepath))
    (shortName, ext) = os.path.splitext(fileName)
    if ext.lower() != ".dat":
        raise NameError("Not a Papagayo Data file: " + fileName)
    print("Loading Papagayo file %s" % fileName)
    f = open(fileName, 'r')
    #print(f.readlines())
    print(context.active_object)
    if context.space_data.use_pin_id:
        speaker = context.space_data.pin_id
    else:
        speaker = context.object.data
    f.readline()  # skip the first line

    #bpy.ops.nla.tracks_add()

    tracklist = context.object.animation_data.nla_tracks
    createtracks(context.object)
    offset = 0
    i = 1  # counter for actions
    for line in f:
        frame = float(line.split()[0])
        phon = line.split()[1]
        context.scene.frame_set(1)  # set the scene frame to the start frame
        speaker.animation_data.action.pose_markers.new(phon).frame = frame
        #print(line,clip.xxx)
        i += 1
    context.scene.frame_set(1)


class SoundTools_LipSync_PT(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Lip sync"
    bl_context = "data"
    selected_phoneme = "rest"
    #object = None

    @classmethod
    def poll(cls, context):
        # NLA PANEL TOO COME.
        return False

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        if context.space_data.use_pin_id:
            speaker = context.space_data.pin_id
        else:
            speaker = context.object.data

        action = getAction(speaker)
        area = layout.row()

        if True:
            area.prop(context.scene, "frame_current", text="Start")
            self.layout.operator("anim.loadlipsync")
            phon = speaker.papagayo_phonemes
            layout.prop(speaker, "papagayo_phonemes", expand=True)
            #st = context.object.animation_data.nla_tracks[phon].strips[phon]
            #layout.template_ID(st, "action", new="action.new")

            row = layout.row()
            row.template_ID(context.scene.objects, "active")

            frame = context.scene.frame_current
            timemarkers = [marker
                           for marker in action.pose_markers
                           if marker.frame == frame]
            row = layout.row()
            if True:
                row.prop(speaker, "papagayo_phonemes", expand=True)
            row = layout.row()
            if len(timemarkers) and True:
                row.label(text="%s" % timemarkers[0].name, icon='MOD_MASK')
                row.prop(timemarkers[0], "frame", text="")
            else:
                timemarkers = [marker
                               for marker in action.pose_markers
                               if marker.frame > frame]
                if len(timemarkers):
                    row.label(text="NEXT %s" % timemarkers[0].name)
                else:
                    row.label("-")
        layout.prop(context.scene, "frame_current", emboss=True)


class OBJECT_OT_LoadLipSync(bpy.types.Operator):
    bl_idname = "anim.loadlipsync"
    bl_label = "Load Papagayo Data File"
    filepath = bpy.props.StringProperty(name="File Path",
                                        maxlen=1024,
                                        default="")
    filename_ext = ".dat"
    filter_glob = bpy.props.StringProperty(default="*.dat",
                                           options={'HIDDEN'})

    phoneme = bpy.props.StringProperty(default="")

    def execute(self, context):
        SoundTools_LipSync_PT.object = context.object
        if self.phoneme != "":
            SoundTools_LipSync_PT.selected_phoneme = self.phoneme
        else:
            readPapagayoFile(context, self.properties.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.types.Speaker.papagayo_phonemes = bpy.props.EnumProperty(items=(
        ('AI', "AI", "AI"),
        ('E', "E", "E"),
        ('MBP', "MBP", "MBP"),
        ('etc', "etc", "etc"),
        ('rest', "rest", "rest"),
        ('O', "O", "O"),
        ('U', "U", "U"),
        ('WQ', "WQ", "WQ"),
        ('L', "L", "L"),
        ('FV', "FV", "FV"),
        ),
            name="Phoneme",
            description="Phoneme",
            default='rest',
            update=boob)
    bpy.utils.register_class(OBJECT_OT_LoadLipSync)
    bpy.utils.register_class(SoundTools_LipSync_PT)
    #bpy.utils.register_class()


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_LoadLipSync)
    bpy.utils.unregister_class(SoundTools_LipSync_PT)

'''
phonemes = ["AI","E","MBP","etc","rest","O","U","FV","WQ","L"]
for p in phonemes:
    if p not in bpy.data.actions:
        action = bpy.data.actions.new(p)
        action["phoneme"] = p
        action["emphasis"] = 1
'''
