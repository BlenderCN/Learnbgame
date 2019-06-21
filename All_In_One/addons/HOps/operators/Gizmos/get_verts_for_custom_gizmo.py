import bpy
import os

path = os.path.join(os.path.dirname(bpy.context.space_data.text.filepath), "custom_gizmo_shapes.py")
print(path)

obj = bpy.context.active_object
verts = [str(tuple(obj.data.vertices[v].co)) for trig in obj.data.polygons for v in trig.vertices]
verts = ",\n    ".join(verts)

with open(path) as customShapesFileCheck:
    currentData = customShapesFileCheck.read()
    if obj.name.lower() in currentData:
        print("Custom object already exists.")

    else:
        with open(path, 'a') as customShapesFile:
            customShapesFile.write(f"\n\n{obj.name.lower()} = (\n    {verts}\n)")