# API guide

Due to how Blender handles adding and registering functions that can be publically used, all public API functions are located within the `bpy.ops` namespace.
All operators **MUST** also be called with keyword arguments (see examples)

## Importing data into Blender

#### bpy.ops.nmsdk.import_scene(path)

**Parameters**:  
    path : string  
        - The complete file path to a `SCENE.MBIN` or `SCENE.EXML` file to be loaded into blender.

**Notes**:  
    The entire scene will be loaded into the active scene in blender.

**Example**:
```python
bpy.ops.nmsdk.import_scene(path='C:\\NMS-1.77\\MODELS\\PLANETS\\BIOMES\\COMMON\\CRYSTALS\\LARGE\\CRYSTAL_LARGE.SCENE.MBIN')
```

#### bpy.ops.nmsdk.import_mesh(path, mesh_id)

**Parameters**:  
    *path* : string  
        - The complete file path to a `SCENE.MBIN` or `SCENE.EXML` file to be loaded into blender.  
    *mesh_id* : string  
        - The `Name` of the `TkSceneNodeData` in the Scene being loaded. 

**Notes**:  
    Only this object will be loaded. None of the children will be.

**Example**:
```python
bpy.ops.nmsdk.import_mesh(path='C:\\NMS-1.77\\MODELS\\PLANETS\\BIOMES\\COMMON\\CRYSTALS\\LARGE\\CRYSTAL_LARGE.SCENE.MBIN', mesh_id='_CRYSTAL_A')
```