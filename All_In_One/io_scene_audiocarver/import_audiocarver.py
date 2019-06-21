
import bmesh
import bpy
import time
from math import pi, sin, cos
import os.path
import sys

current_track = 0
current_track_start_time = 0

pitch_id = 0
modulation_wheel_id = 1
volume_id = 7

note_suffix_number = 2
note_layer = 18
note_scale = 0.01
timeline_count = 0
timeline_layer = 17
timeline_text_layer = 16
track_scale = 1.0

pitch_min = 128
pitch_max = 0
velocity_scale = 0.1

#verts_per_second = 1 # use "0" to get start and end points only
verts_per_second = 0 # use "0" to get start and end points only
verts_per_ring = 32
max_note_thickness = 0.025
#max_note_thickness = 0.25
min_note_duration = 0.2

angle_start = 30 / 180 * pi
angle_end = 330 / 180 * pi
angle_increment = 0.0

note_range_distance = 5.0
#note_range_distance = 4.0

track_meshes = [];

i = 0
while i < 1:
    track_meshes.append(bmesh.new())
    i = i + 1


class Note:
    _startTime = -1
    _duration = -1
    _velocity = -1
    _pitch = -1


def print_message(message):
    print(message);
    sys.stdout.flush();


def clear_ss():
    bpy.ops.object.select_all(action = 'DESELECT')


def current_ss():
    return bpy.context.selected_objects


def to_zero_prefixed_string(number):
    zero_prefixed_string = ""
    if number < 100:
        zero_prefixed_string += "0"
    if number < 10:
        zero_prefixed_string += "0"
    zero_prefixed_string += str(int(number))
    return zero_prefixed_string


def get_note_object_name(chord_number):
    return "Note.Main.1." + str(chord_number)


def get_note_material(chord_number):
    return bpy.data.materials["Note.Material.1." + str(chord_number)]


def get_note_object(chord_number):
    note_material = get_note_material(chord_number)

    note_object = None
    note_object_name = get_note_object_name(chord_number)
    if (note_object_name in bpy.data.objects.keys()):
        note_object = bpy.data.objects[note_object_name]
    else:
        # Select and duplicate the note template object.
        clear_ss()
        note_template_object.select = True
        bpy.ops.object.duplicate()

        # Rename the new note object.
        note_object = bpy.data.objects["Note.Main.001"]
        note_object.name = note_object_name

    # Set the note mesh materials.
    note_object.material_slots[0].material = note_material

    return note_object


def get_note_mesh(chord_number):
    return track_meshes[int(chord_number - 1)]


def add_diamond_ring_note_without_decay_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
 
    velocity = note._velocity

    # Calculate the note's location on the ring.
    pitch_delta = note._pitch - pitch_min
    pitch_angle = angle_start + (pitch_delta * angle_increment)
    velocity_angle = velocity / velocity_scale * angle_increment
    pitch_angle_low = pitch_angle - velocity_angle
    pitch_angle_high = pitch_angle + velocity_angle
    track_offset = 1.0
    min_offset = track_offset - velocity
    max_offset = track_offset + velocity

    x_start = note._startTime
    x_end = x_start + note._duration
    y1_low = track_offset * sin(pitch_angle_low)
    z1_low = track_offset * cos(pitch_angle_low)
    y1_high = track_offset * sin(pitch_angle_high)
    z1_high = track_offset * cos(pitch_angle_high)
    y1_in = min_offset * sin(pitch_angle)
    z1_in = min_offset * cos(pitch_angle)
    y1_out = max_offset * sin(pitch_angle)
    z1_out = max_offset * cos(pitch_angle)
    
    mesh_verts = mesh.verts
    v1_low = mesh_verts.new((x_start, y1_low, z1_low))
    v1_high = mesh_verts.new((x_start, y1_high, z1_high))
    v1_in = mesh_verts.new((x_start, y1_in, z1_in))
    v1_out = mesh_verts.new((x_start, y1_out, z1_out))
    v2_low = mesh_verts.new((x_end, y1_low, z1_low))
    v2_high = mesh_verts.new((x_end, y1_high, z1_high))
    v2_in = mesh_verts.new((x_end, y1_in, z1_in))
    v2_out = mesh_verts.new((x_end, y1_out, z1_out))
    
    mesh_faces = mesh.faces
    mesh_faces.new((v1_low, v1_in, v2_in, v2_low))
    mesh_faces.new((v1_in, v1_high, v2_high, v2_in))
    mesh_faces.new((v1_high, v1_out, v2_out, v2_high))
    mesh_faces.new((v1_out, v1_low, v2_low, v2_out))
    mesh_faces.new((v2_low, v2_in, v2_high, v2_out))


def add_triangular_ring_note_without_decay_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
 
    velocity = note._velocity

    # Calculate the note's location on the ring.
    pitch_delta = note._pitch - pitch_min
    pitch_angle = angle_start + (pitch_delta * angle_increment)
    velocity_angle = velocity / velocity_scale * angle_increment
    pitch_angle_low = pitch_angle - velocity_angle
    pitch_angle_high = pitch_angle + velocity_angle
    track_offset = 1.0
    max_offset = track_offset + velocity

    x_start = note._startTime
    x_end = x_start + note._duration
    y1_low = track_offset * sin(pitch_angle_low)
    z1_low = track_offset * cos(pitch_angle_low)
    y1_high = track_offset * sin(pitch_angle_high)
    z1_high = track_offset * cos(pitch_angle_high)
    y1_out = max_offset * sin(pitch_angle)
    z1_out = max_offset * cos(pitch_angle)
    
    mesh_verts = mesh.verts
    v1_low = mesh_verts.new((x_start, y1_low, z1_low))
    v1_high = mesh_verts.new((x_start, y1_high, z1_high))
    v1_out = mesh_verts.new((x_start, y1_out, z1_out))
    v2_low = mesh_verts.new((x_end, y1_low, z1_low))
    v2_high = mesh_verts.new((x_end, y1_high, z1_high))
    v2_out = mesh_verts.new((x_end, y1_out, z1_out))
    
    mesh_faces = mesh.faces
    mesh_faces.new((v1_low, v1_high, v2_high, v2_low))
    mesh_faces.new((v1_high, v1_out, v2_out, v2_high))
    mesh_faces.new((v1_out, v1_low, v2_low, v2_out))
    mesh_faces.new((v2_low, v2_high, v2_out))


def add_triangular_ring_note_with_decay_to_mesh(note, mesh):
    global pitch_min
    global pitch_max
 
    velocity = note._velocity

    # Calculate the note's location on the ring.
    pitch_delta = note._pitch - pitch_min
    pitch_angle = angle_start + (pitch_delta * angle_increment)
    velocity_angle = velocity / velocity_scale * angle_increment
    pitch_angle_low = pitch_angle - velocity_angle
    pitch_angle_high = pitch_angle + velocity_angle
    track_offset = 1.0
    total_offset = track_offset + velocity

    x_start = note._startTime
    x_end = x_start + note._duration
    y1_low = track_offset * sin(pitch_angle_low)
    z1_low = track_offset * cos(pitch_angle_low)
    y1_high = track_offset * sin(pitch_angle_high)
    z1_high = track_offset * cos(pitch_angle_high)
    y1 = total_offset * sin(pitch_angle)
    z1 = total_offset * cos(pitch_angle)
    y2 = track_offset * sin(pitch_angle)
    z2 = track_offset * cos(pitch_angle)
    
    mesh_verts = mesh.verts
    v1_low = mesh_verts.new((x_start, y1_low, z1_low))
    v1_high = mesh_verts.new((x_start, y1_high, z1_high))
    v1 = mesh_verts.new((x_start, y1, z1))
    v2 = mesh_verts.new((x_end, y2, z2))
    
    mesh_faces = mesh.faces
    #mesh_faces.new((v1, v1_high, v1_low))
    mesh_faces.new((v1, v2, v1_high))
    mesh_faces.new((v1_high, v2, v1_low))
    mesh_faces.new((v1_low, v2, v1))


def update_ranges(file_name):
    global pitch_min
    global pitch_max

    # Read each line in the file and update global max and min values.
    file = open(dir_name + file_name);
    for line in file:
        line = line.rstrip('\r\n').split(', ')
        line_id = float(line[0])
        line_value = float(line[2])
        if (pitch_id == line_id):
            if (line_value < pitch_min):
                pitch_min = line_value
            if (pitch_max < line_value):
                pitch_max = line_value


def update_current_track_start_time(file_name):
    global current_track_start_time
    
    # Read the first line's time parameter.
    file = open(dir_name + file_name);
    for line in file:
        line = line.rstrip('\r\n').split(', ')
        current_track_start_time = float(line[1])
    

def import_file(file_name, note_shape):
    chord = -1
    start_time = -1
    end_time = -1
    pitch = -1
    volume = -1

    file = open(dir_name + file_name);
    for line in file:
        line = line.rstrip('\r\n').split(', ')
        line_id = float(line[0])
        line_time = float(line[1])
        line_value = float(line[2])
        if (-1 == start_time):
            start_time = line_time
        else:
            end_time = line_time
        if (pitch_id == line_id):
            if (-1 == pitch):
                pitch = line_value
        elif (volume_id == line_id):
            if (volume < line_value):
                volume = line_value
        elif (modulation_wheel_id == line_id):
            if (-1 == chord):
                chord = line_value

    start_time -= current_track_start_time
    end_time -= current_track_start_time

    note = Note()
    note._startTime = start_time
    note._duration = end_time - start_time
    note._velocity = 0.01 + (velocity_scale * volume)
    note._pitch = pitch
    note_mesh = get_note_mesh(0)
    print_message(note_shape)
    if ("Triangular with decay" == note_shape):
        add_triangular_ring_note_with_decay_to_mesh(note, note_mesh)
    if ("Triangular without decay" == note_shape):
        add_triangular_ring_note_without_decay_to_mesh(note, note_mesh)
    elif ("Diamond without decay" == note_shape):
        add_diamond_ring_note_without_decay_to_mesh(note, note_mesh)

def note_string(note_number):
    mod = int(note_number) % 12
    if 0 == mod:
        return "C"
    if 2 == mod:
        return "D"
    if 4 == mod:
        return "E"
    if 5 == mod:
        return "F"
    if 7 == mod:
        return "G"
    if 9 == mod:
        return "A"
    if 11 == mod:
        return "B"
    return ""


def create_pitch_lines():
    global angle_increment
    global angle_start
    global angle_end
    global pitch_min
    global pitch_max

    print_message("\nCreating pitch lines ...")

    # Create pitch line text objects for each note in the note pitch range.
    i = pitch_min
    while i <= pitch_max:
        angle = angle_start + (angle_increment * (pitch_max - i))

        i_string = str(int(i))
        text_string = note_string(i)
        has_text = "" != text_string

        # Duplicate pitch line text template objects.
        clear_ss()
        if has_text:
            bpy.data.objects["PitchLine.Text.Arrow.0"].select = True
        else:
            bpy.data.objects["PitchLine.Text.Arrow.00"].select = True
        bpy.ops.object.duplicate()

        # Setup pitch line text arrow.
        obj = bpy.data.objects["PitchLine.Text.Arrow.001"]
        obj.rotation_euler[0] = angle + pi
        obj.name = "PitchLine.Text.Arrow.." + i_string

        if has_text:
            clear_ss()
            bpy.data.objects["PitchLine.Text.0"].select = True
            bpy.ops.object.duplicate()

            radius = 1.29
            location = (0.1, -radius * sin(angle), radius * cos(angle))

            # Setup pitch line text.
            obj = bpy.data.objects["PitchLine.Text.001"]
            obj.location = location
            obj.data.body = note_string(i)
            obj.name = "PitchLine.Text.." + i_string

            # Center pitch line text.
            bbox = obj.bound_box
            x_offset = bbox[0][1] + ((bbox[2][1] - bbox[0][1]) / 2.0)
            y_offset = bbox[0][0] + (bbox[4][0] - bbox[0][0])
            obj.location[1] += y_offset
            obj.location[2] -= x_offset

        i += 1

    # Delete pitch line text template objects.
    clear_ss()
    bpy.data.objects["PitchLine.Text.0"].select = True
    bpy.data.objects["PitchLine.Text.Arrow.0"].select = True
    bpy.data.objects["PitchLine.Text.Arrow.00"].select = True
    bpy.ops.object.delete()


def load(operator,
         context,
         file_name,
         note_shape):
    global angle_increment
    global current_track
    global current_super_track
    global dir_name
    global note_layer
    global note_template_object
    global pitch_min
    global pitch_max
    global velocity_min
    global velocity_max
    global velocity_scale
    global track_scale

    # Reset global variables.
    pitch_min = 128
    pitch_max = 0
    current_track = 0

    dir_name = os.path.dirname(file_name) + '/'
    print_message("\nImporting Csound Log Directory " + dir_name + " ...")

    start_time = time.time()

    # Store the current selection set so it can be restored later.
    cur_active_obj = bpy.context.scene.objects.active
    cur_ss = current_ss()

    # Turn on the note layers.
    bpy.context.scene.layers[note_layer] = True

    # Set the track scale.
    track_scale = bpy.data.objects[".Track.Scale.X"].scale[0]

    print_message("\nImporting tracks ...")

    for file_name in os.listdir(dir_name):
        if (file_name.endswith(".txt")):
            file_info = file_name.split('-')
            #note_id = int(file_info[1])
            note_number = int(file_info[4].split('.')[0])
            # The first note is the track time reference.  Skip it.
            if (1 < note_number):
                update_ranges(file_name)
    
    # Calculate the global angle increment.
    angle_increment = (angle_end - angle_start) / (pitch_max - pitch_min)
    print(pitch_max - pitch_min) 
    
    # Import tracks and notes.
    for file_name in os.listdir(dir_name):
        if (file_name.endswith(".txt")):
            file_info = file_name.split('-')
            note_number = int(file_info[4].split('.')[0])
            if (1 == note_number):
                current_track = int(file_info[1])
                update_current_track_start_time(file_name)
            else:
                import_file(file_name, note_shape)

    # Add each mesh to it's note.
    i = 1
    while i <= 1:
        note = get_note_object(i)
        mesh = get_note_mesh(i)
        mesh.to_mesh(note.data)
        i = i + 1

    create_pitch_lines();

    # Restore the original selection set.
    clear_ss()
    for obj in cur_ss:
        obj.select = True
    bpy.context.scene.objects.active = cur_active_obj

    print_message("\n... done in %.3f seconds\n" % (time.time() - start_time))

    return {'FINISHED'}
