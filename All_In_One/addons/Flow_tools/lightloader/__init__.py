import bpy
import json
import os


light_settings = bpy.context.user_preferences.system.solid_lights
current_default = "[]"

blender_default_preset_name = "blender default"
current_default_preset_name = "current default"
locked_names = [current_default_preset_name, blender_default_preset_name]

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(path, "light_presets")
if not os.path.isdir(path):
    print("mkdir")
    os.mkdir(path)

def get_filenames():
    all_files = sorted(os.listdir(path))
    
    actual_presets = []
    
    for item in all_files:
        if item.endswith(".json_lightpreset"):
            if os.path.isfile(os.path.join(path, item)):
                actual_presets.append(item[:-len(".json_lightpreset")])
    
    return actual_presets

def list_presets_callback(self, context):
    presets = get_filenames()
    
    items =  []
    
    for locked_name in locked_names:
        items.append((locked_name, locked_name, locked_name))
    
    for preset in presets:
        if preset not in locked_names:
            items.append((preset, preset, preset))
    return items

def load_unpack(name):
    if name == current_default_preset_name:
        unpack(current_default)
        return
    
    filepath = os.path.join(path, name + ".json_lightpreset")
    
    with open(filepath, "r") as file:
        unpack(file.read())
    


def save_as (name):
    filepath = os.path.join(path, name + ".json_lightpreset")
    
    with open(filepath, "w") as file:
        file.write(pack())


def delete_file(name):
    filepath = os.path.join(path, name + ".json_lightpreset")
    if not os.path.isfile(filepath) or name in locked_names:
        return False
    os.remove(filepath)


def pack():
    
    lights = []
    
    for light in light_settings:
        d = {}
        d["use"] = float(light.use)
        d["direction_x"] = float(light.direction[0])
        d["direction_y"] = float(light.direction[1])
        d["direction_z"] = float(light.direction[2])
        d["diff_coll_r"] = float(light.diffuse_color[0])
        d["diff_coll_g"] = float(light.diffuse_color[1])
        d["diff_coll_b"] = float(light.diffuse_color[2])
        d["spec_coll_r"] = float(light.specular_color[0])
        d["spec_coll_g"] = float(light.specular_color[1])
        d["spec_coll_b"] = float(light.specular_color[2])
        lights.append(d)
    
    return json.dumps(lights, sort_keys = False, indent = 4)
current_default = pack()


def unpack(string):
    
    lights = json.loads(string)
    for light, d in zip(light_settings, lights):
        light.use = d["use"]
        light.direction[0] = d["direction_x"]
        light.direction[1] = d["direction_y"]
        light.direction[2] = d["direction_z"]
        light.diffuse_color[0] = d["diff_coll_r"]
        light.diffuse_color[1] = d["diff_coll_g"]
        light.diffuse_color[2] = d["diff_coll_b"]
        light.specular_color[0] = d["spec_coll_r"]
        light.specular_color[1] = d["spec_coll_g"]
        light.specular_color[2] = d["spec_coll_b"]
            

class SavePreset(bpy.types.Operator):
    bl_idname = "f_tools_2.save_light_preset"
    bl_label = "Save Preset"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    name = bpy.props.StringProperty(
        name = "Name",
        description = "The name for the preset, will overwrite if already exist.",
    )
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.name not in locked_names:
            save_as(self.name)
        
        return {"FINISHED"}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class DeletePreset(bpy.types.Operator):
    bl_idname = "f_tools_2.delete_light_preset"
    bl_label = "Delete Preset"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    name = bpy.props.StringProperty(
        name = "Name",
        description = "The name for the preset, will overwrite if already exist.",
    )
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.name not in locked_names:
            delete_file(self.name)
        return {"FINISHED"}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete?")
        layout.prop(self, "name")
        
        