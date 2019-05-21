import bpy
import bmesh



class MaskFromCavity(bpy.types.Operator) :
    ''' Mask From Cavity'''
    bl_idname = "mesh.mask_from_cavity"
    bl_label = "Mask From Cavity"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'


    # A Property for cavity angle
    bpy.types.Scene.mask_cavity_angle = bpy.props.IntProperty(name = "Cavity Angle", default = 82, min = 45, max = 90)

    # A Property for cavity mask strength
    bpy.types.Scene.mask_cavity_strength = bpy.props.FloatProperty(name = "Mask Strength", default = 1.0, min = 0.1, max = 1.0)



    def execute(self, context):

        mask_cavity_angle = context.scene.mask_cavity_angle # update property from user input

        mask_cavity_strength = context.scene.mask_cavity_strength # update property from user input

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           if context.sculpt_object.use_dynamic_topology_sculpting :

              dynatopoEnabled = True

              bpy.ops.sculpt.dynamic_topology_toggle()

           bmeshContainer = bmesh.new() # New bmesh container

           bmeshContainer.from_mesh(context.active_object.data) # Fill container with our object

           mask = bmeshContainer.verts.layers.paint_mask.verify() # get active mask layer

           bmeshContainer.faces.ensure_lookup_table() # Update vertex lookup table

           mask_cavity_angle *= (3.14 * 0.0055556) # Convert angle to radians (approx)

           maskWeight = 1.0 * mask_cavity_strength

           for face in bmeshContainer.faces :

                 for vert in face.verts : # for each x face

                    vert [mask] = 0.0 # Clear any mask beforehand

                    for loop in vert.link_loops :

                        loopTan =  loop.calc_tangent()

                        angleFace = (face.normal.angle (loopTan, 0.0))

                        angleDiff = (vert.normal.angle( loopTan, 0.0 )) # get the angle between the vert normal to loop edge Tangent

#                        print ("Angle Diff: %f" % (angleDiff))
#                        print ("Cav Angle : %f" % (mask_cavity_angle))
#                        print ("Angle Face : %f" % (angleFace))
#                        print ("AD - AF : %f" % (angleDiff + angleFace))
#                        print ("Loop Tangent : [%s] " % loopTan)

                        if ( angleFace + angleDiff ) <=  (1.57 + mask_cavity_angle) : # if the difference is greater then input

                               vert [mask] = maskWeight # mask it with input weight



           bmeshContainer.to_mesh(context.active_object.data) # Fill obj data with bmesh data

           bmeshContainer.free() # Release bmesh

           if dynatopoEnabled :

               bpy.ops.sculpt.dynamic_topology_toggle()


           bpy.ops.screen.space_type_set_or_cycle(space_type="NODE_EDITOR")
           bpy.ops.screen.space_type_set_or_cycle(space_type="VIEW_3D")

        return {'FINISHED'}






class MaskFromEdges(bpy.types.Operator):
    ''' Mask From Edges'''
    bl_idname = "mesh.mask_from_edges"
    bl_label = "Mask From Edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'


    # A Property for cavity angle
    bpy.types.Scene.mask_edge_angle = bpy.props.IntProperty(name = "Sharp Angle", default = 82, min = 45, max = 90)

    # A Property for cavity mask strength
    bpy.types.Scene.mask_edge_strength = bpy.props.FloatProperty(name = "Mask Strength", default = 1.0, min = 0.1, max = 1.0)



    def execute(self, context):

        mask_edge_angle = context.scene.mask_edge_angle # update property from user input

        mask_edge_strength = context.scene.mask_edge_strength # update property from user input

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           if context.sculpt_object.use_dynamic_topology_sculpting :

              dynatopoEnabled = True

              bpy.ops.sculpt.dynamic_topology_toggle()

           bmeshContainer = bmesh.new() # New bmesh container

           bmeshContainer.from_mesh(context.active_object.data) # Fill container with our object

           mask = bmeshContainer.verts.layers.paint_mask.verify() # get active mask layer

           bmeshContainer.faces.ensure_lookup_table() # Update vertex lookup table

           mask_edge_angle *= (3.14 * 0.0055556) # Convert angle to radians (approx)

           maskWeight = 1.0 * mask_edge_strength

           for face in bmeshContainer.faces :

                 for vert in face.verts : # for each x face

                    vert [mask] = 0.0 # Clear any mask beforehand

                    for loop in vert.link_loops :

                        loopTan =  loop.calc_tangent()

                        angleFace = (face.normal.angle (-loopTan, 0.0))

                        angleDiff = (vert.normal.angle(-loopTan, 0.0 )) # get the angle between the vert normal to loop edge Tangent

#                        print ("Angle Diff: %f" % (angleDiff))
#                        print ("Cav Angle : %f" % (mask_cavity_angle))
#                        print ("Angle Face : %f" % (angleFace))
#                        print ("AD - AF : %f" % (angleDiff + angleFace))
#                        print ("Loop Tangent : [%s] " % loopTan)

                        if ( angleFace + angleDiff ) <=  (1.57 + mask_edge_angle) : # if the difference is greater then input

                               vert [mask] = maskWeight # mask it with input weight


           bmeshContainer.to_mesh(context.active_object.data) # Fill obj data with bmesh data

           bmeshContainer.free() # Release bmesh

           if dynatopoEnabled :

               bpy.ops.sculpt.dynamic_topology_toggle()


           bpy.ops.screen.space_type_set_or_cycle(space_type="NODE_EDITOR")
           bpy.ops.screen.space_type_set_or_cycle(space_type="VIEW_3D")

        return {'FINISHED'}


class MaskSmoothAll(bpy.types.Operator):
    ''' Mask Smooth All'''
    bl_idname = "mesh.mask_smooth_all"
    bl_label = "Mask Smooth All"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'


    bpy.types.Scene.mask_smooth_strength = bpy.props.IntProperty(name = "Mask Smooth Strength", default = 20, min = 0)


    def execute(self, context):

        mask_smooth_strength = context.scene.mask_smooth_strength # update property from user input

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           bpy.ops.mesh.masktovgroup()
           bpy.ops.mesh.masktovgroup_append()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.object.vertex_group_smooth(factor=1,repeat=mask_smooth_strength)
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
           bpy.ops.mesh.vgrouptomask_append()
           bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)



           # if context.sculpt_object.use_dynamic_topology_sculpting :
           #
           #    dynatopoEnabled = True
           #
           #    bpy.ops.sculpt.dynamic_topology_toggle()
           #
           # bmeshContainer = bmesh.new() # New bmesh container
           #
           # bmeshContainer.from_mesh(context.active_object.data) # Fill container with our object
           #
           # mask = bmeshContainer.verts.layers.paint_mask.active # get active mask layer
           #
           # bmeshContainer.verts.ensure_lookup_table() # Update vertex lookup table
           #
           # for vert in bmeshContainer.verts :
           #
           #      for edge in vert.link_edges :
           #
           #          if vert [mask] < (edge.other_vert(vert) [mask] * abs(vert [mask]- mask_smooth_strength)):
           #
           #             vert [mask]  = (edge.other_vert(vert) [mask] * abs(vert [mask] -mask_smooth_strength))
           #
           #          if vert [mask]< 0.0 :
           #
           #              vert [mask] = 0.0
           #
           #          elif vert [mask]> 1.0 :
           #
           #              vert [mask] = 1.0
           #
           #
           # bmeshContainer.to_mesh(context.active_object.data) # Fill obj data with bmesh data
           #
           # bmeshContainer.free() # Release bmesh

           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

class MaskFat(bpy.types.Operator):
    ''' Mask Fat '''
    bl_idname = "mesh.mask_fat"
    bl_label = "Mask Fat"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    bpy.types.Scene.mask_fat_repeat = bpy.props.IntProperty(name = "Mask Fat Repeat", default = 1)

    def execute(self, context):
        mask_fat_repeat = context.scene.mask_fat_repeat # update property from user input


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           bpy.ops.mesh.masktovgroup()
           bpy.ops.mesh.masktovgroup_append()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.weight_paint_toggle()
           for var in range(0, mask_fat_repeat):
               bpy.ops.object.vertex_group_smooth(factor=1,repeat=1,expand=1.0)
               bpy.ops.object.vertex_group_levels(gain=1)
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
           bpy.ops.mesh.vgrouptomask_append()
           bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)


           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

class MaskLess(bpy.types.Operator):
    ''' Mask Less '''
    bl_idname = "mesh.mask_less"
    bl_label = "Mask Less"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    bpy.types.Scene.mask_less_repeat = bpy.props.IntProperty(name = "Mask Less Repeat", default = 1)


    def execute(self, context):
        mask_less_repeat = context.scene.mask_less_repeat # update property from user input


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :
           bpy.ops.paint.mask_flood_fill(mode='INVERT')
           bpy.ops.mesh.masktovgroup()
           bpy.ops.mesh.masktovgroup_append()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.weight_paint_toggle()
           for var in range(0, mask_less_repeat):
               bpy.ops.object.vertex_group_smooth(factor=1,repeat=1,expand=1.0)
               bpy.ops.object.vertex_group_levels(gain=1)
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
           bpy.ops.mesh.vgrouptomask_append()
           bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
           bpy.ops.paint.mask_flood_fill(mode='INVERT')


           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

class MaskSharp(bpy.types.Operator):
    ''' Mask Sharp '''
    bl_idname = "mesh.mask_sharp"
    bl_label = "Mask Sharp"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'


    def execute(self, context):


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           bpy.ops.mesh.masktovgroup()
           bpy.ops.mesh.masktovgroup_append()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.object.vertex_group_invert()
           bpy.ops.object.vertex_group_smooth(factor=1,repeat=3,expand=1.0)
           bpy.ops.object.vertex_group_levels(gain=5)
           bpy.ops.object.vertex_group_quantize(steps=1)
           bpy.ops.object.vertex_group_invert()
           # bpy.ops.object.vertex_group_invert()


           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
           bpy.ops.mesh.vgrouptomask_append()
           bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)


           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

class MaskSharpThick(bpy.types.Operator):
    ''' Mask Sharp Thick '''
    bl_idname = "mesh.mask_sharp_thick"
    bl_label = "Mask Sharp (Thick)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'


    bpy.types.Scene.mask_sharp_thick = bpy.props.IntProperty(name = "Mask Sharp Thick", default = 20, min = 0)




    def execute(self, context):
        mask_sharp_thick = context.scene.mask_sharp_thick # update property from user input


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           bpy.ops.mesh.masktovgroup()
           bpy.ops.mesh.masktovgroup_append()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.object.vertex_group_levels(gain=mask_sharp_thick)
           bpy.ops.paint.weight_paint_toggle()
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
           bpy.ops.mesh.vgrouptomask_append()
           bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)


           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

class MaskLattice(bpy.types.Operator):
    ''' Mask Lattice '''
    bl_idname = "mesh.mask_lattice"
    bl_label = "Mask Lattice Deform"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    bpy.types.Scene.mask_sharp_thick = bpy.props.IntProperty(name = "Mask Sharp Thick", default = 50, min = 0)

    def execute(self, context):
        mask_sharp_thick = context.scene.mask_sharp_thick # update property from user input


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           bpy.ops.mesh.masktovgroup()
           bpy.ops.mesh.masktovgroup_append()
           bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.object.mode_set(mode="EDIT")
           bpy.ops.mesh.select_all(action='DESELECT')
           bpy.ops.mesh.reveal()
           bpy.ops.view3d.snap_cursor_to_selected()
           bpy.ops.object.mode_set(mode="OBJECT")


           #  アクティブオブジェクトの定義
           # active = bpy.context.scene.active_object.name
           active = bpy.context.active_object
           name = active.name

           #  "cv_" + アクティブオブジェクト名に定義
           objname = "cv_" + name
           #  一度、アクティブの選択を解除し、リネームする
           # bpy.data.objects[active].select_set(state = False)
           bpy.ops.object.select_all(action='DESELECT')
           bpy.ops.object.add(type='LATTICE', view_align=False, enter_editmode=False)
           for obj in bpy.context.selected_objects:
               obj.name = objname
           #  再度、アクティブを選択
           bpy.ops.object.select_all(action='DESELECT')

           # bpy.data.objects[name].select_set(state = True)
           bpy.context.scene.objects.active = name
           bpy.ops.object.modifier_add(type='LATTICE')
           bpy.context.object.modifiers["Lattice"].object = objname

           bpy.data.objects[objname].select_set(state = True)
           bpy.ops.object.mode_set(mode="EDIT")
           bpy.ops.lattice.select_all()


           # ーーーーーーーーーーーーーーーーーーーーーーーーー
           # ーーーーーーーーーーーーーーーーーーーーーーーーー
           #  モディファイアを設定ーーーーーーーーーーーーーーーーーーーーーーーーー

           # 配列複製モディファイアを追加
           bpy.ops.object.modifier_add(type='ARRAY')

           # # bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
           # obj = context.object
           # bm = bmesh.from_edit_mesh(obj.data)
           # selected_verts = [i.co for i in bm.verts if i.select]
           #
           # top = None
           # bottom = None
           # left = None
           # right = None
           # front = None
           # back = None
           # for v in selected_verts:
           #     	if top == None:
           #     		top = v[2]
           #     	elif top < v[2]:
           #     		top = v[2]
           #
           #     	if bottom == None:
           #     		bottom = v[2]
           #     	elif bottom > v[2]:
           #     		bottom = v[2]
           #
           #     	if left == None:
           #     		left = v[1]
           #     	elif left > v[1]:
           #     		left = v[1]
           #
           #     	if right == None:
           #     		right = v[1]
           #     	elif right < v[1]:
           #     		right = v[1]
           #
           #     	if front == None:
           #     		front = v[0]
           #     	elif front < v[0]:
           #     		front = v[0]
           #
           #     	if back == None:
           #     		back = v[0]
           #     	elif back > v[0]:
           #     		back = v[0]
           #
           # bpy.ops.mesh.select_all(action='DESELECT')
           #
           # lattice = bpy.data.lattices.new("Lattice")
           # lattice_ob = bpy.data.objects.new("Lattice", lattice)
           #
           # # x_scale = (front - back) / (lattice.points[5].co[0] - lattice.points[4].co[0])
           # # y_scale = (right - left) / (lattice.points[7].co[1] - lattice.points[5].co[1])
           # # z_scale = (top - bottom) / (lattice.points[5].co[2] - lattice.points[1].co[2])
           # #
           # # lattice_ob.scale = (x_scale, y_scale, z_scale)
           # lattice_ob.location = ((front+back) / 2, (right+left) / 2, (top+bottom) / 2)
           #
           # scene = bpy.context.scene
           #
           # lattice_mod = obj.modifiers.new("Lattice", 'LATTICE')
           # lattice_mod.object = lattice_ob
           # lattice_mod.vertex_group = bpy.context.object.vertex_groups.active.name
           #
           # scene.objects.link(lattice_ob)
           # scene.update()
           #
           # for o in bpy.context.scene.objects:
           #     	o.select = False
           # lattice_ob.select = True
           # bpy.context.scene.objects.active = lattice_ob
           # bpy.ops.object.mode_set(mode='OBJECT')
           # bpy.ops.object.editmode_toggle()






           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
           bpy.ops.mesh.vgrouptomask_append()
           bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)


           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}


class MaskArmture(bpy.types.Operator):
    ''' Mask Armture '''
    bl_idname = "mesh.mask_armature"
    bl_label = "Mask Armture"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):
        mask_sharp_thick = context.scene.mask_sharp_thick # update property from user input


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :
           bpy.ops.sculpt.sculptmode_toggle()
           #bpy.ops.object.vertex_group_remove(all=True)
           #bpy.ops.object.delete_all_modifiers()
           bpy.ops.object.vertex_group_add()
           #bpy.context.object.name = "armmask"
           bpy.ops.sculpt.sculptmode_toggle()
           bpy.ops.mesh.masktovgroup_append()
           bpy.context.object.name = "deform_bone"
           bpy.ops.sculpt.sculptmode_toggle()
           sculptobj = bpy.context.active_object.name
           bpy.ops.object.armature_add()
           # bpy.data.objects[sculptobj].select = True
           bpy.data.objects[sculptobj].select_set(state = True)
           bpy.ops.object.editmode_toggle()

           objarm = bpy.context.selected_objects[0].name
           objmesh = bpy.context.selected_objects[1].name
           bpy.ops.object.parent_set(type='ARMATURE_AUTO')
           active = bpy.data.objects[objmesh]
           activearm = bpy.data.objects[objarm]
           bpy.context.scene.objects.active = active
           bpy.context.object.modifiers["Armature"].vertex_group = "Group"
           bpy.context.scene.objects.active = activearm
           bpy.ops.object.posemode_toggle()

           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}


class MaskPolygonRemove(bpy.types.Operator):
    ''' Mask PolygonRemove '''
    bl_idname = "mesh.mask_polygon_remove"
    bl_label = "Mask Polygon Remove"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'


    def execute(self, context):


        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :



           bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
           bpy.ops.object.mode_set(mode="EDIT")
           bpy.ops.mesh.select_all(action='DESELECT')
           bpy.ops.mesh.reveal()
           bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
           bpy.ops.mesh.dissolve_mode()
           bpy.ops.sculpt.sculptmode_toggle()


           if dynatopoEnabled :
               bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}



def register():

    bpy.types.Scene.mask_edge_angle = MaskFromEdges.mask_edge_angle

    bpy.types.Scene.mask_edge_strength = MaskFromEdges.mask_edge_strength

    bpy.types.Scene.mask_cavity_angle = MaskFromCavity.mask_cavity_angle

    bpy.types.Scene.mask_cavity_strength = MaskFromCavity.mask_cavity_strength

    bpy.types.Scene.mask_smooth_strength = MaskSmoothAll.mask_smooth_strength
    bpy.types.Scene.mask_sharp_thick = MaskSmoothAll.mask_sharp_thick

    bpy.utils.register_module(__name__)




def unregister():

    bpy.types.Scene.mask_edge_angle

    bpy.types.Scene.mask_edge_strength

    bpy.types.Scene.mask_cavity_angle

    bpy.types.Scene.mask_cavity_strength

    bpy.types.Scene.mask_smooth_strength
    bpy.types.Scene.mask_sharp_thick

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
