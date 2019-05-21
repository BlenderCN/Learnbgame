import bpy
from bpy_extras import view3d_utils

class AddMat(bpy.types.Operator):
    bl_label = "Add Ui Material"
    bl_idname = "rigui.add_mat"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene = context.scene

        mat = bpy.data.materials.new('UI')
        mat.use_nodes = True

        for node in mat.node_tree.nodes :
            if node.type == 'OUTPUT_MATERIAL' :
                mat_output = node
            else :
                mat.node_tree.nodes.remove(node)

        emission = mat.node_tree.nodes.new('ShaderNodeEmission')
        mat.node_tree.links.new(emission.outputs[0],mat_output.inputs[0])


        if not context.object.data.materials :
            context.object.data.materials.append(mat)
        else :
            context.object.material_slots[0].material = mat

        return {'FINISHED'}

class RemoveMat(bpy.types.Operator):
    bl_label = "Remove Ui Material"
    bl_idname = "rigui.remove_mat"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene = context.scene
        #print(self.shape_type)
        for mat in context.object.data.materials :
            bpy.data.materials.remove(mat,True)
            context.area.tag_redraw()

        return {'FINISHED'}

class EyeDropperMat(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "rigui.eye_dropper_mat"
    bl_label = "Eye Dropper mat"
    #bl_options = {'REGISTER', 'UNDO'}

    #first_mouse_x = IntProperty()
    #first_value = FloatProperty()


    def modal(self, context, event):
        context.area.tag_redraw()

        context.window.cursor_modal_set("EYEDROPPER")

        scene = context.scene
        region = context.region
        rv3d = context.region_data


        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.mouse = event.mouse_region_x, event.mouse_region_y

            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, self.mouse)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, self.mouse)

            raycast = scene.ray_cast(ray_origin,view_vector)

            if raycast[0]==True :
                ob = raycast[4]

                if ob.data.materials :
                    mat = ob.data.materials[0]
                    for shape in [o for o in context.selected_objects if o.type in ('MESH','CURVE','FONT')] :
                        if not shape.data.materials :
                            shape.data.materials.append(mat)
                        else :
                            shape.material_slots[0].material = mat


            #context.space_data.draw_handler_remove(self._handle, 'WINDOW')

            context.window.cursor_modal_restore()

            for ob in self.temp_ob :
                bpy.data.objects.remove(ob,True)

            return {'FINISHED'}


            #return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            #context.object.location.x = self.first_value
            context.window.cursor_modal_restore()

            for ob in self.temp_ob :
                bpy.data.objects.remove(ob,True)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        scene = context.scene
        self.local_cursor = tuple(context.space_data.cursor_location)
        self.cursor = tuple(context.scene.cursor_location)

        curves =[o for o in context.visible_objects if o.type in ('CURVE','FONT')]

        self.temp_ob = []

        for c in curves :
            mesh = c.to_mesh(bpy.context.scene,False,'PREVIEW')
            copy = bpy.data.objects.new(c.name+'_tmp',mesh)
            copy.matrix_world = c.matrix_world
            for mat in c.data.materials :
                copy.data.materials.append(mat)
            scene.objects.link(copy)
            self.temp_ob.append(copy)
        #args = (self,context)
        #self._handle = context.space_data.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
