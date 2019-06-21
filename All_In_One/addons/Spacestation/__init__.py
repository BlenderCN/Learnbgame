bl_info = {
    "name": "Spacestation Generator",
    "author": "Rahix",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh",
    "description": "Procedural Spacestation generator",
    "category": "Learnbgame",
    }

import random

if "bpy" in locals():
    import importlib
    importlib.reload(spacestation)
else:
    from . import spacestation

import bpy



class GenerateSpacestation(bpy.types.Operator):
    bl_idname = "mesh.generate_spacestation"
    bl_label  = "Spacestation"
    #bl_options = {'REGISTER', 'UNDO'}

    use_seed : bpy.props.BoolProperty(default=False, name="Use Seed")
    seed : bpy.props.IntProperty(default=5, name="Seed (Requires 'Use Seed')")
    parts_min : bpy.props.IntProperty(default=3, min=0, name="Min. Parts")
    parts_max : bpy.props.IntProperty(default=8, min=3, name="Max. Parts")
    torus_major_min : bpy.props.FloatProperty(default=2.0, min=0.1, name="Min. Torus radius")
    torus_major_max : bpy.props.FloatProperty(default=5.0, min=0.1, name="Max. Torus radius")
    torus_minor_min : bpy.props.FloatProperty(default=0.1, min=0.1, name="Min. Torus thickness")
    torus_minor_max : bpy.props.FloatProperty(default=0.5, min=0.1, name="Max. Torus thickness")
    bevelbox_min : bpy.props.FloatProperty(default=0.2, min=0.1, name="Min. Bevelbox scale")
    bevelbox_max : bpy.props.FloatProperty(default=0.5, min=0.1, name="Max. Bevelbox scale")
    cylinder_min : bpy.props.FloatProperty(default=0.5, min=0.1, name="Min. Cylinder radius")
    cylinder_max : bpy.props.FloatProperty(default=3.0, min=0.1, name="Max. Cylinder radius")
    cylinder_h_min : bpy.props.FloatProperty(default=0.3, min=0.1, name="Min. Cylinder height")
    cylinder_h_max : bpy.props.FloatProperty(default=1.0, min=0.1, name="Max. Cylinder height")
    storage_min : bpy.props.FloatProperty(default=0.5, min=0.1, name="Min. Storage height")
    storage_max : bpy.props.FloatProperty(default=1.0, min=0.1, name="Max. Storage height")

    def execute(self, context):
        if not self.use_seed:
            seed = random.randint(0, 100000)
        else:
            seed = self.seed
        config = {
            "min_parts":      self.parts_min,
            "max_parts":      self.parts_max,
            "torus_major_min":self.torus_major_min,
            "torus_major_max":self.torus_major_max,
            "torus_minor_min":self.torus_minor_min,
            "torus_minor_max":self.torus_minor_max,
            "bevelbox_min":   self.bevelbox_min,
            "bevelbox_max":   self.bevelbox_max,
            "cylinder_min":   self.cylinder_min,
            "cylinder_max":   self.cylinder_max,
            "cylinder_h_min": self.cylinder_h_min,
            "cylinder_h_max": self.cylinder_h_max,
            "storage_min":    self.storage_min,
            "storage_max":    self.storage_max
        }
        spacestation.generate_station(seed, config)
        return {'FINISHED'}

def add_menu_entry(self, context):
    self.layout.operator(GenerateSpacestation.bl_idname, text="Spacestation")

def register():
    #bpy.utils.register_class(GenerateSpacestation)
    bpy.utils.register_class(GenerateSpacestation)
    bpy.types.VIEW3D_MT_mesh_add.append(add_menu_entry)

def unregister():
    #bpy.utils.unregister_class(GenerateSpacestation)
    bpy.utils.unregister_class(GenerateSpacestation)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_menu_entry)

if __name__ == "__main__":
    register()
