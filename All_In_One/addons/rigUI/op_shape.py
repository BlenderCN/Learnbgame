import bpy
from .func_shape import store_ui_data
from .utils import is_shape,find_mirror

class CreateShape(bpy.types.Operator):
    bl_label = "Create UI shape"
    bl_idname = "rigui.create_shape"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene = context.scene

        offset = 0
        for bone in context.selected_pose_bones :
            name = bone.name

            mesh = bpy.data.meshes.new(name)
            ob = bpy.data.objects.new(name,mesh)

            ob.UI.name = name

            verts=[(0,0,0)]
            edges = []
            faces =[]

            mesh.from_pydata(verts, edges, faces)

            scene.objects.link(ob)

            if scene.UI.canevas :
                ob.layers = scene.UI.canevas.layers
            else :
                layers = [False]*20
                layers[8] = True
                ob.layers = layers

            scene.cursor_location = (0,0,0.05)
            ob.location[2]=0.05
            ob.location[0]= offset

            for obj in scene.objects :
                obj.select = False

            scene.objects.active = ob
            ob.select = True

            offset += 0.05

        return {'FINISHED'}


class NameFromBone(bpy.types.Operator):
    bl_label = "Name Shape from selected bones"
    bl_idname = "rigui.name_from_bone"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene = context.scene
        rig = scene.UI.rig
        bone = rig.data.bones.active

        if bone :
            context.object.name = bone.name
            context.object.UI.name = bone.name

        return {'FINISHED'}


class MirrorShape(bpy.types.Operator):
    bl_label = "Mirror UI shape"
    bl_idname = "rigui.mirror_shape"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene = context.scene

        for ob in bpy.context.selected_objects :

            name = find_mirror(ob.name)

            if not name :
                name = ob.name+'_flip'

            old_shape = bpy.data.objects.get(name)
            if old_shape:
                bpy.data.objects.remove(old_shape,True)

            mirrorShape = ob.copy()
            mirrorShape.data = ob.data.copy()
            mirrorShape.name = name
            #mirrorShape = bpy.data.objects.new(name,ob.data.copy())

            scene.objects.link(mirrorShape)
            mirrorShape.layers = ob.layers

            if scene.UI.symmetry :
                symmetry_loc = scene.UI.symmetry.matrix_world.to_translation()[0]
            else :
                symmetry_loc = 0

            #print(symmetry_loc)
            mirrorShape.matrix_world = ob.matrix_world

            #if mirrorShape.location[0] < symmetry_loc :
            mirrorShape.location[0]= symmetry_loc+ (symmetry_loc- ob.location[0])
            #else :
            #    mirrorShape.location[0]= symmetry_loc+ (symmetry_loc- ob.location[0])

            mirrorShape.rotation_euler[1] = -ob.rotation_euler[1]
            mirrorShape.rotation_euler[2] = -ob.rotation_euler[2]

            mirrorShape.scale[0] = -ob.scale[0]


            for key,value in ob.items() :
                if key not in ["_RNA_UI",'cycles']:
                    mirrorShape[key] = value

            if ob.UI.shape_type == 'BONE' :
                mirrorShape.UI.name = find_mirror(ob.UI.name)

            elif ob.UI.shape_type == 'FUNCTION' :
                args = {}
                for key,value in eval(ob.UI.arguments).items() :
                    if type(value) == list :
                        mirrored_value = []
                        for item in value :
                            mirrored_value.append(find_mirror(item))

                    elif type(value) == str :
                        mirrored_value = find_mirror(value)
                    args[key] = mirrored_value

                mirrorShape.UI.arguments = str(args)

        return {'FINISHED'}

class SelectShapeType(bpy.types.Operator):
    bl_label = "Select Shape by Type"
    bl_idname = "rigui.select_shape_type"
    #bl_options = {'REGISTER', 'UNDO'}

    shape_type = bpy.props.EnumProperty(items =[(i.upper(),i,"") for i in ('Bone','Display','Function')])

    def draw(self,context) :
        layout = self.layout

        col = layout.column()
        col.prop(self,'shape_type',expand = True)

    def execute(self,context):
        scene = context.scene
        #print(self.shape_type)
        canevas = context.scene.UI.canevas
        if canevas :
            for ob in [o for o in bpy.data.objects if o.layers==canevas.layers] :
                if ob.type in ['MESH','CURVE','FONT'] and ob.UI.shape_type == self.shape_type :
                    ob.select = True

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self,width=150)

class StoreUIData(bpy.types.Operator):
    bl_label = "Store UI Data"
    bl_idname = "rigui.store_ui_data"

    def execute(self,context):
        scene = context.scene
        canevas= scene.UI.canevas
        rig = scene.UI.rig
        shapes = [o for o in scene.objects if o != canevas and is_shape(o)]

        if rig.type == 'ARMATURE' and canevas:
            store_ui_data(shapes,canevas,rig)

        else :
            self.report({'INFO'},'active object not rig or canevas not found')

        return {'FINISHED'}
