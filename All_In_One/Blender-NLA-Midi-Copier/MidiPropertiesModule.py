if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup


def get_tracks_list(self, context):
    return midi_data.get_tracks_list(self, context)


def get_notes_list(self, context):
    return midi_data.get_notes_list(self, context)


def action_poll(note_action_property, action):
    id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]
    return action.id_root == id_root or (action.id_root == "NODETREE" and id_root in midi_data.note_tree_types)


def on_id_type_updated(note_action_property, context):
    # clear the action since it no longer applies to the selected id type
    note_action_property.action = None


def on_action_updated(note_action_property, context):
    action = note_action_property.action
    # update the action length property to match the actual length of the action
    if action is not None:
        note_action_property.action_length = action.frame_range[1] - action.frame_range[0]


def on_object_updated(note_action_property, context):
    if note_action_property.object is not None:
        # either copy to note_action_property.object or to selected objects, not both
        note_action_property.copy_to_selected_objects = False


def on_copy_to_selected_objects_updated(note_action_property, context):
    if note_action_property.copy_to_selected_objects:
        # either copy to note_action_property.object or to selected objects, not both
        note_action_property.object = None


class NoteActionProperty(PropertyGroup):
    id_type: EnumProperty(
        items=sorted([(x, x, x) for x in midi_data.ID_PROPERTIES_DICTIONARY.keys()], key=lambda x: x[0]),
        name="Type", description="Type of object to apply the action to", default="Object", update=on_id_type_updated)

    action: PointerProperty(type=bpy.types.Action, name="Action", description="The action to create action strips from",
                            poll=action_poll, update=on_action_updated)

    midi_frame_offset: \
        IntProperty(name="Frame Offset",
                    description="Frame offset when copying strips")

    delete_source_action_strip: \
        BoolProperty(name="Delete Source Action",
                     description="Delete the source action after copying",
                     default=False)
    delete_source_track: \
        BoolProperty(name="Delete Source Track",
                     description="Delete the track containing the source action if it is empty",
                     default=False)

    nla_track_name: \
        StringProperty(name="Nla Track",
                       description="Name of the NLA Track that action strips will be placed on.\n " +
                                   "A track name will be automatically generated if this is blank.")

    duplicate_object_on_overlap: \
        BoolProperty(name="Duplicate Object on Overlap",
                     description="Copy the action to a duplicated object if it overlaps another action",
                     default=False)

    copy_to_selected_objects: \
        BoolProperty(name="Copy Action to Selected Objects",
                     description="Copy the action to all selected objects.",
                     default=False, update=on_copy_to_selected_objects_updated)

    action_length: \
        IntProperty(name="Action Length (Frames)",
                    description="Length of the action, used to determine if the next action overlaps.\n" +
                                "This will be ignored if it is shorter than the actual length of the action.")

    # used for display in the instruments panel
    expanded: BoolProperty(name="Expanded", default=True)

    armature: PointerProperty(type=bpy.types.Armature, name="Armature", description="The armature to animate")
    camera: PointerProperty(type=bpy.types.Camera, name="Camera", description="The camera to animate")
    cachefile: PointerProperty(type=bpy.types.CacheFile, name="Cache File", description="The cache file to animate")
    curve: PointerProperty(type=bpy.types.Curve, name="Curve", description="The curve to animate")
    greasepencil: PointerProperty(type=bpy.types.GreasePencil, name="Grease Pencil",
                                  description="The grease pencil to animate")
    key: PointerProperty(type=bpy.types.Key, name="Key", description="The key to animate")
    lattice: PointerProperty(type=bpy.types.Lattice, name="Lattice", description="The lattice to animate")
    light: PointerProperty(type=bpy.types.Light, name="Light", description="The light to animate")
    mask: PointerProperty(type=bpy.types.Mask, name="Mask", description="The mask to animate")
    material: PointerProperty(type=bpy.types.Material, name="Material", description="The material to animate")
    meta: PointerProperty(type=bpy.types.MetaBall, name="MetaBall", description="The meta to animate")
    mesh: PointerProperty(type=bpy.types.Mesh, name="Mesh", description="The mesh to animate")
    movieclip: PointerProperty(type=bpy.types.MovieClip, name="Movie Clip", description="The movie clip to animate")
    nodetree: PointerProperty(type=bpy.types.NodeTree, name="Node Tree", description="The node tree to animate")
    object: PointerProperty(type=bpy.types.Object, name="Object", description="The object to animate",
                            update=on_object_updated)
    light_probe: PointerProperty(type=bpy.types.LightProbe, name="Light  Probe",
                                 description="The light_probe to animate")
    scene: PointerProperty(type=bpy.types.Scene, name="Scene", description="The scene to animate")
    speaker: PointerProperty(type=bpy.types.Speaker, name="Speaker", description="The speaker to animate")
    texture: PointerProperty(type=bpy.types.Texture, name="Texture", description="The texture to animate")
    world: PointerProperty(type=bpy.types.World, name="World", description="The world to animate")


class InstrumentNoteProperty(PropertyGroup):
    name: StringProperty(name="Name")
    note_id: IntProperty(name="Note")
    actions: CollectionProperty(type=NoteActionProperty, name="Actions")


class InstrumentProperty(PropertyGroup):
    name: StringProperty(name="Name")
    default_midi_frame_offset: IntProperty(name="Default Frame Offset",
                                           description="Frame offset when copying strips")
    notes: CollectionProperty(type=InstrumentNoteProperty, name="Notes")
    selected_note_id: EnumProperty(items=midi_data.get_instrument_notes,
                                   name="Note", description="Note")

    selected_midi_track: EnumProperty(items=get_tracks_list,
                                      name="Track",
                                      description="Selected Midi Track")
    # properties for drawing the panel
    properties_expanded: BoolProperty(name="Expanded", default=True)
    notes_expanded: BoolProperty(name="Expanded", default=True)
    animate_expanded: BoolProperty(name="Expanded", default=True)


def get_midi_file_name(self):
    return self["midi_file"]


class MidiPropertyGroup(PropertyGroup):
    midi_file: StringProperty(name="Midi File", description="Select Midi File", get=get_midi_file_name)
    notes_list: EnumProperty(items=get_notes_list,
                             name="Note",
                             description="Note")
    track_list: EnumProperty(items=get_tracks_list,
                             name="Track",
                             description="Selected Midi Track")
    note_action_property: PointerProperty(type=NoteActionProperty)
    midi_frame_start: \
        IntProperty(name="First Frame",
                    description="The frame corresponding to the beginning of the midi file",
                    default=1)

    instruments: CollectionProperty(type=InstrumentProperty, name="Instruments")
    selected_instrument_id: EnumProperty(items=midi_data.get_instruments, name="Instrument",
                                         description="Select an instrument")
