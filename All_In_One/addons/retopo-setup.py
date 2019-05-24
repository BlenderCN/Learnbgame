
bl_info = {
    "name": "Retopo Setup",
    "description": "Retopology workflow setup",
    "author": "Sreenivas Alapati(cg-cnu)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "category": "Learnbgame",
}

import bpy 

def main(self, context):
    C = bpy.context
    D = bpy.data
    O = bpy.ops
    name = C.active_object.name

    if D.objects[name].type != 'MESH':
        self.report({'WARNING'}, " Valid mesh object not selected ")
        return {'FINISHED'}
    
    O.mesh.primitive_plane_add() # add plane primitive
    C.object.location.xyz = bpy.data.objects[name].location.xyz # set its positon to sculpt's origin 
    C.active_object.name = name + '_retopo' # rename the object as name_retopo
    retopo = C.active_object.name # get the name of the object as retopo         

    # rotate and translate
    bpy.ops.object.editmode_toggle()
    bpy.ops.transform.translate(value=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')
    bpy.ops.transform.rotate(value=1.5708, axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')
    bpy.ops.object.editmode_toggle()

    # scene settings
    bpy.context.scene.tool_settings.use_snap = True
    bpy.context.scene.tool_settings.snap_element = 'FACE'
    bpy.context.scene.tool_settings.use_snap_project = True

    # mirror modifier
    O.object.modifier_add(type='MIRROR') 
    mirror_modifier = bpy.context.object.modifiers["Mirror"]
    mirror_modifier.name = name + '_mirror';
    mirror_modifier.use_y = True
    mirror_modifier.use_x = False
    mirror_modifier.use_clip = True 
    mirror_modifier.show_expanded = False

    # subsurf modifier
    O.object.modifier_add(type='SUBSURF')
    subsurf_modifier = bpy.context.object.modifiers['Subsurf']
    subsurf_modifier.name = name + '_subsurf';
    subsurf_modifier.levels = 2
    subsurf_modifier.subdivision_type = 'SIMPLE'
    subsurf_modifier.show_expanded = False

    # shrinkwrap wrapping to opossite side of the object;
    # shrinkwrap modifier 
    O.object.modifier_add(type='SHRINKWRAP')
    shrinkwrap_modifier = bpy.context.object.modifiers["Shrinkwrap"]
    shrinkwrap_modifier.name = name + '_shrinkwrap' 
    shrinkwrap_modifier.target = bpy.data.objects[name]
    shrinkwrap_modifier.offset = 0.02
    shrinkwrap_modifier.show_on_cage = True
    shrinkwrap_modifier.use_keep_above_surface = True
    shrinkwrap_modifier.use_negative_direction = True
    shrinkwrap_modifier.use_positive_direction = True
    shrinkwrap_modifier.wrap_method = 'PROJECT'
    shrinkwrap_modifier.show_expanded = False

    # materials
    material = D.materials.new(name="retopo_setup_material")
    C.active_object.data.materials.append(material)
    material.diffuse_color = (0.8, 0.15, 0.05)
    material.specular_color = (0, 0, 0)

    self.report({'INFO'}, " Created setup for retopo ")

class RetopoSetup(bpy.types.Operator):
    """ sets the object ready for retopo """
    bl_idname = "object.retopo_setup"
    bl_label = "Retopo Setup"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RetopoSetup)

def unregister():
    bpy.utils.unregister_class(RetopoSetup) 

if __name__ == "__main__":
    register()