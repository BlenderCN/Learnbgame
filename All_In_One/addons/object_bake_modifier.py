# ##### BEGIN GPL LICENSE BLOCK #####
#
#  object_bake_modifier.py
#  Bake the modifier of an object to shape keys
#  Copyright (C) 2015 Quentin Wenger
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {"name": "Bake Modifier to Shape Keys",
           "description": "Bake the modifier of an object to shape keys",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 76, 0),
           "location": "3D View -> Properties -> Bake Modifier",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "Object"
           }


import bpy


# only "Deform" modifiers
ALLOWED_MOD_TYPES = [
    'ARMATURE',
    'CAST',
    'CORRECTIVE_SMOOTH',
    'CURVE',
    'DISPLACE',
    'HOOK',
    'LAPLACIANSMOOTH',
    'LAPLACIANDEFORM',
    'LATTICE',
    'MESH_DEFORM',
    'SHRINKWRAP',
    'SIMPLE_DEFORM',
    'SMOOTH',
    'WARP',
    'WAVE'
    ]


class BakeModifierExecuteOperator(bpy.types.Operator):
    bl_idname = "object.bakemod_exec"
    bl_label = "Bake"
    bl_description = "Bake selected modifier"

    @classmethod
    def poll(cls, context):
        if not (context.area.type == 'VIEW_3D' and
            context.mode == 'OBJECT' and
            context.object is not None and
            context.object.type == 'MESH' and
            context.object.data is not None and
            context.object.modifiers):
            return False

        if context.object.bakemod_name in context.object.modifiers:
            if context.object.modifiers[context.object.bakemod_name].type in ALLOWED_MOD_TYPES:
                return True

        return False

    def execute(self, context):
        obj = context.object
        scene = context.scene

        original_frame = scene.frame_current
        
        start_frame = obj.bakemod_startframe
        end_frame = obj.bakemod_endframe
        name = obj.bakemod_name
        keys_prefix = obj.bakemod_keysprefix
        make_copy = obj.bakemod_makecopy
        settings = obj.bakemod_settings

        if make_copy:
            old_obj = obj
            obj = old_obj.copy()
            # needed?
            obj.data = old_obj.data.copy()

            scene.objects.link(obj)

        while obj.active_shape_key:
            obj.shape_key_remove(obj.active_shape_key)
        #bpy.ops.object.shape_key_remove(all=True)

        padding = len(str(end_frame))

        for frame in range(start_frame, end_frame + 1):
            scene.frame_current = frame
            
            shapekey_name = keys_prefix + str(frame).zfill(padding)
            skey = obj.shape_key_add(name=shapekey_name, from_mix=False)
            #skey.frame = frame

            new_mesh = obj.to_mesh(scene, True, settings)

            for i, v in enumerate(new_mesh.vertices):
                skey.data[i].co = v.co

            bpy.data.meshes.remove(new_mesh)
            
            obj.data.shape_keys.eval_time = 10*(frame - start_frame)
            obj.data.shape_keys.keyframe_insert(data_path="eval_time")

        obj.data.shape_keys.use_relative = False

        obj.modifiers.remove(obj.modifiers[obj.bakemod_name])
        
        scene.frame_current = original_frame

        return {'FINISHED'}


class BakeModifierPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Bake Modifier"

    @classmethod
    def poll(cls, context):
        if not (context.area.type == 'VIEW_3D' and
            context.mode == 'OBJECT' and
            context.object is not None and
            context.object.type == 'MESH' and
            context.object.data is not None and
            context.object.modifiers):
            return False

        for mod in context.object.modifiers:
            if mod.type in ALLOWED_MOD_TYPES:
                return True

        return False

    def draw(self, context):
        layout = self.layout

        """
        found = False

        if context.object.modifier_to_bake != "":
            for mod in context.object.modifiers:
                if mod == context.object.modifier_to_bake:
                    found = True
                    break

        if not found:
            context.object.modifier_to_bake = ""
        """

        #layout.prop_enum(context.object, "modifiers")
        #layout.prop(context.object, "modifier_to_bake")#, icon='OBJECT')
        #layout.template_ID(context.object, "modifier_to_bake")
        layout.prop_search(context.object,
                           "bakemod_name",
                           context.object,
                           "modifiers",
                           icon="MODIFIER")

        if context.object.bakemod_name != "":

            if context.object.bakemod_name in context.object.modifiers:
                mod = context.object.modifiers[context.object.bakemod_name]

                layout.separator()

                if mod.type in ALLOWED_MOD_TYPES:
                    row = layout.row(align=True)
                    row.prop(context.object, "bakemod_startframe")
                    row.prop(context.object, "bakemod_endframe")

                    layout.prop(context.object, "bakemod_keysprefix")

                    row2 = layout.row()
                    row2.prop(context.object, "bakemod_makecopy")
                    row2.prop(context.object, "bakemod_settings")

                    layout.separator()

                    layout.operator("object.bakemod_exec")

                else:
                    layout.label(text="The selected Modifier cannot be baked, it is not a Deform Modifier.",
                                 icon='ERROR')

            """
            else:
                layout.label(text="The selected Modifier doesn't exist.",
                             icon='ERROR')
            """

        """
        sce = context.scene
         
        act = context.active_node
        
        if act is not None:
            layout.prop(sce, "node_location")
        """




def register():
    bpy.utils.register_module(__name__)
    """
    bpy.types.Scene.node_location = bpy.props.FloatVectorProperty(name="Location",
                                                                  description="The location of active node in the Node Editor",
                                                                  size=2,
                                                                  set=setLocation,
                                                                  get=getLocation
                                                                  )
    """
    bpy.types.Object.bakemod_name = bpy.props.StringProperty(name="Modifier", options={'HIDDEN'})
    bpy.types.Object.bakemod_keysprefix = bpy.props.StringProperty(name="Shape Keys Prefix", default="BMOD_", options={'HIDDEN'})
    bpy.types.Object.bakemod_startframe = bpy.props.IntProperty(name="Start", default=1, options={'HIDDEN'})
    bpy.types.Object.bakemod_endframe = bpy.props.IntProperty(name="End", default=250, options={'HIDDEN'})
    bpy.types.Object.bakemod_makecopy = bpy.props.BoolProperty(name="Create Copy", options={'HIDDEN'})
    bpy.types.Object.bakemod_settings = bpy.props.EnumProperty(items=[("PREVIEW", "Preview", "Use preview settings", 'RESTRICT_VIEW_OFF', 0),
                                                                      ("RENDER", "Render", "Use render settings", 'SCENE', 1)],
                                                               name="Settings", default="RENDER", options={'HIDDEN'})


def unregister():
    bpy.utils.unregister_module(__name__)

    #del bpy.types.Scene.node_location
    del bpy.types.Object.bakemod_name



if __name__ == "__main__":
    register()



