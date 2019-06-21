skeleton = [
    ('hips', 'Hips', 'Hips'),
    ('spine', 'Spine', 'Spine'),
    ('spine1', 'Spine1', 'Spine Additional*'),
    ('spine2', 'Spine2', 'Chest'),
    ('neck', 'Neck', 'Neck'),
    ('head', 'Head', 'Head')
]

left = ["left", "l"]
right = ["right", "r"]

left_prefix = ("left_", "Left")
right_prefix = ("right_", "Right")
arms = [
    ('shoulder', 'Shoulder', 'Shoulder'),
    ('arm', 'Arm', 'Arm'),
    ('fore_arm', 'ForeArm', 'ForeArm'),
    ('hand', 'Hand', 'Hand'),
]

fingers = [
    ("hand_thumb", "HandThumb", "Thumb 1st"),
    ("hand_index", "HandIndex", "Index Finger 1st"),
    ("hand_middle", "HandMiddle", "Middle Finger 1st"),
    ("hand_ring", "HandRing", "Ring Finger 1st"),
    ("hand_pinky", "HandPinky", "Pinky 1st")
]

legs = [
    ('up_leg', 'UpLeg', 'Thigh'),
    ('leg', 'Leg', 'Leg'),
    ('foot', 'Foot', 'Foot'),
    ('toe', 'Toe', 'Toe')
]

head = [
    ('left_eye', 'LeftEye', 'Left Eye'),
    ('right_eye', 'RightEye', 'Right Eye'),
    ('head_top', 'HeadTop', 'Head Top')
]

# 4.6 mb per avatar per second.

for bone in skeleton:
    print(bone[0], "=", "bpy.props.StringProperty(name='" +
          bone[1] + "', description='" + bone[2] + "')")

print("# Head")

for bone in head:
    print(bone[0], "=", "bpy.props.StringProperty(name='" +
          bone[1] + "', description='" + bone[2] + "')")


print("# Arms")


print("right")
for bone in arms:
    print(left_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          left_prefix[1] + bone[1] + "', description='" + left_prefix[1] + " " + bone[2] + "')")
    print(right_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          right_prefix[1] + bone[1] + "', description='" + right_prefix[1] + " " + bone[2] + "')")

print("left")

for bone in arms:
    print(left_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          left_prefix[1] + bone[1] + "', description='" + left_prefix[1] + " " + bone[2] + "')")
    print(right_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          right_prefix[1] + bone[1] + "', description='" + right_prefix[1] + " " + bone[2] + "')")

print("# Fingers")

for bone in fingers:
    print(left_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          left_prefix[1] + bone[1] + "', description='" + left_prefix[1] + " " + bone[2] + "')")
    print(right_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          right_prefix[1] + bone[1] + "', description='" + right_prefix[1] + " " + bone[2] + "')")


print("# Legs")

for bone in legs:
    print(left_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          left_prefix[1] + bone[1] + "', description='" + left_prefix[1] + " " + bone[2] + "')")
    print(right_prefix[0] + bone[0], "=", "bpy.props.StringProperty(name='" +
          right_prefix[1] + bone[1] + "', description='" + right_prefix[1] + " " + bone[2] + "')")


print("## Draw Log ##")


print("layout = self.layout")
for bone in skeleton:
    print("column.prop_search(self, '" +
          bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + bone[2] + "')")


print("# Head")

for bone in head:
    print("column.prop_search(self, '" +
          bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + bone[2] + "')")

print("# Arms")

for bone in arms:
    print("column.prop_search(self, '" +
          left_prefix[0] + bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + left_prefix[1] + ' ' + bone[2] + "')")

for bone in arms:
    print("column.prop_search(self, '" +
          right_prefix[0] + bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + right_prefix[1] + ' ' + bone[2] + "')")

print("# Fingers")

for bone in fingers:
    print("column.prop_search(self, '" +
          left_prefix[0] + bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + left_prefix[1] + ' ' + bone[2] + "')")

for bone in fingers:
    print("column.prop_search(self, '" +
          right_prefix[0] + bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + right_prefix[1] + ' ' + bone[2] + "')")


print("# Legs")

for bone in legs:
    print("column.prop_search(self, '" +
          left_prefix[0] + bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + left_prefix[1] + ' ' + bone[2] + "')")


for bone in legs:
    print("column.prop_search(self, '" +
          right_prefix[0] + bone[0] + "', data, 'bones', icon='ARMATURE_DATA', text='" + right_prefix[1] + ' ' + bone[2] + "')")

