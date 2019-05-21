# def _memo_vert_face_distances(
#         context, ob, target_ob, space=Space.GLOBAL, axis=Axis.X,
#         apply_modifiers=False, settings='PREVIEW'):
#     space = Space.get(space)
#     axis = Axis.get(axis)
#     key = (ob.name, target_ob.name, space, axis, apply_modifiers, settings)
#     key = memo_append_mat(key, context, space, ob)
#     return key
#
#
# @memoize(_memo_vert_face_distances)
# def vert_face_distances(
#         context, ob, target_ob, space=Space.GLOBAL, axis=Axis.X,
#         apply_modifiers=False, settings='PREVIEW'):
#     import numpy as np
#     from . import funcs
#
#     def get_mesh_coords(mesh, dtype=np.float32):
#         coords = np.empty(len(mesh.vertices) * 3, dtype=dtype)
#         mesh.vertices.foreach_get('co', coords)
#         coords.shape = (-1, 3)
#         return coords
#
#     space = Space.get(space)
#     axis = Axis.get(axis)
#
#     scene = context.scene
#     do_transform = ob.matrix_world != Matrix.Identity(4)
#     omat = funcs.get_orientation(context, space)
#     if omat != ob.matrix_world.to_3x3():
#         do_transform = True
#     if ob.mode == 'EDIT':
#         bm = bmesh.from_edit_mesh(ob.data)
#         tmp_mesh = bpy.data.meshes.new('_')
#         bm.to_mesh(tmp_mesh)
#     else:
#         if do_transform:
#             tmp_mesh = ob.data.copy()
#         else:
#             tmp_mesh = ob.data
#     if do_transform:
#         tmp_mesh.transform(omat.inverted() * ob.matrix_world)
#     tmp_ob = bpy.data.objects.new('_', tmp_mesh)
#     scene.objects.link(tmp_ob)
#     mod = tmp_ob.modifiers.new('_', 'SHRINKWRAP')
#     """:type: bpy.types.ShrinkwrapModifier"""
#     mod.wrap_method = 'PROJECT'
#     if axis == Axis.X:
#         mod.use_project_x = True
#     elif axis == Axis.Y:
#         mod.use_project_y = True
#     elif axis == Axis.Z:
#         mod.use_project_z = True
#     mod.use_negative_direction = True
#     mod.target = target_ob
#
#     # FIX ME !!
#     target_ob.matrix_world = omat.inverted().to_4x4()
#
#     scene.update()  # 必須
#
#     coords_orig = get_mesh_coords(tmp_mesh)
#
#     mesh_mod = tmp_ob.to_mesh(scene, apply_modifiers=apply_modifiers,
#                               settings=settings)
#     coords_mod = get_mesh_coords(mesh_mod)
#     bpy.data.meshes.remove(mesh_mod)
#
#     mod.offset = 1.0
#     mesh_mod = tmp_ob.to_mesh(scene, apply_modifiers=apply_modifiers,
#                               settings=settings)
#     coords_mod_ofs = get_mesh_coords(mesh_mod)
#     bpy.data.meshes.remove(mesh_mod)
#
#     dists = coords_mod.astype(np.float64) - coords_orig
#     valid_flags = coords_mod != coords_mod_ofs
#
#     scene.objects.unlink(tmp_ob)
#     bpy.data.objects.remove(tmp_ob)
#     if do_transform:
#         bpy.data.meshes.remove(tmp_mesh)
#
#     scene.update()
#
#     return dists, valid_flags


# class OperatorSetFaces(OperatorTemplate, bpy.types.Operator):
#     bl_idname = 'at.set_faces'
#     bl_label = 'Set Faces'
#     bl_options = {'REGISTER', 'UNDO'}
#
#     object_data = bpy.props.EnumProperty(
#         name='Object Data',
#         description='Object data type (only object mode)',
#         items=(#('ORIGIN', 'Object Origin', 'Object origin'),
#                ('MESH', 'Mesh', 'Mesh data'),
#                ('DM_PREVIEW', 'Derived Mesh Preview',
#                 'Derived mesh (apply modifiers)'),
#                ('DM_RENDER', 'Derived Mesh Render',
#                 'Derived mesh (apply modifiers)')),
#         default='MESH',
#     )
#
#     @classmethod
#     def poll(cls, context):
#         return context.mode in {'OBJECT', 'EDIT_MESH'}
#
#     def execute(self, context):
#         mesh = bpy.data.meshes.get(tool_data.temp_mesh_name)
#         if mesh:
#             bpy.data.meshes.remove(mesh)
#
#         if context.mode == 'EDIT_MESH':
#             bm = bmesh.from_edit_mesh(context.active_object.data)
#             bm.verts.index_update()
#             bm.faces.index_update()
#             verts = set()
#             faces = []
#             for f in bm.faces:
#                 if f.select:
#                     faces.append(f)
#                     verts.update(f.verts)
#             verts = sorted(verts, key=lambda v: v.index)
#             vert_index = {v: i for i, v in enumerate(verts)}
#             mesh = bpy.data.meshes.new(tool_data.temp_mesh_name)
#             mesh.from_pydata(
#                 [v.co for v in verts],
#                 [],
#                 [[vert_index[v] for v in f.verts] for f in faces])
#             mesh.update(True, True)
#             mesh.transform(context.active_object.matrix_world)
#
#         elif context.selected_objects:
#             selected_objects = context.selected_objects
#             actob = context.active_object
#
#             # create objects
#             apply_modifiers = False
#             settings = 'PREVIEW'
#             if self.object_data in {'DM_PREVIEW', 'DM_RENDER'}:
#                 apply_modifiers = True
#                 if self.object_data == 'DM_RENDER':
#                     settings = 'RENDER'
#             temp_objects = []
#             temp_meshes = []
#
#             me = bpy.data.meshes.new(tool_data.temp_mesh_name)
#             ob = bpy.data.objects.new('tmp', me)
#             ob.select = True
#             context.scene.objects.link(ob)
#             context.scene.objects.active = ob
#
#             for ob in selected_objects:
#                 ob.select = False
#                 try:
#                     me = ob.to_mesh(
#                         context.scene, apply_modifiers=apply_modifiers,
#                         settings=settings)
#                 except RuntimeError:
#                     # 変換不能ならエラー
#                     # Error: Object does not have geometry data
#                     continue
#                 temp_meshes.append(me)
#                 me.transform(ob.matrix_world)
#                 tmp_ob = bpy.data.objects.new('tmp', me)
#                 tmp_ob.select = True
#                 context.scene.objects.link(tmp_ob)
#                 temp_objects.append(tmp_ob)
#
#             # join objects
#             bpy.ops.object.join()
#             ob = context.active_object
#             for me in temp_meshes:
#                 bpy.data.meshes.remove(me)
#             context.scene.objects.unlink(ob)
#             bpy.data.objects.remove(ob)
#
#             # restore select
#             for ob in selected_objects:
#                 ob.select = True
#             context.scene.objects.active = actob
#
#         return {'FINISHED'}


# class OperatorAlignToFaces(OperatorTemplateModeSave,
#                            OperatorTemplateTranslation,
#                            OperatorTemplateGroup, bpy.types.Operator):
#     bl_idname = 'at.align_to_faces'
#     bl_label = 'Align to Faces'
#     bl_description = ''
#     bl_options = {'REGISTER', 'UNDO'}
#
#     plane_offset = bpy.props.FloatProperty(
#         name='Plane Offset',
#         subtype='DISTANCE')
#     axis_offset = bpy.props.FloatProperty(
#         name='Axis Offset',
#         subtype='DISTANCE')
#     influence = bpy.props.FloatProperty(
#         name='Influence',
#         default=1.0,
#         step=1,
#         precision=3,
#         soft_min=0.0,
#         soft_max=1.0,
#         subtype='NONE')
#
#     use_event = bpy.props.BoolProperty(options={'HIDDEN', 'SKIP_SAVE'})
#
#     show_expand_others = bpy.props.BoolProperty()
#
#     # @classmethod
#     # def poll(cls, context):
#     #     return context.mode in {'OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE', 'POSE'}
#
#     @classmethod
#     def poll(cls, context):
#         return context.mode in {'OBJECT', 'EDIT_MESH'}
#
#     def execute(self, context):
#         bpy.ops.at.fix()
#         memocoords.cache_init(context)
#         if self.space == 'AXIS':
#             self.axis = 'Z'
#         groups = self.groups = self.make_groups(context)
#
#         dists, valid = vert_face_distance(context)
#         print(dists, valid)
#
#         # plane = tool_data.plane.copy()
#         # plane.location += plane.normal * self.plane_offset
#         #
#         # groups_align_to_plane(
#         #     context, groups, self.space, self.axis, None, self.axis_offset,
#         #     self.influence, EPS, plane)
#
#         return {'FINISHED'}
#
#     def invoke(self, context, event):
#         if self.use_event:
#             if event.shift:
#                 if self.space == 'GLOBAL':
#                     self.space = 'LOCAL'
#         return self.execute(context)
#
#     def draw(self, context):
#         op_stubs.OperatorResetProperties.set_operator(self)
#
#         # Axis
#         attrs = ['space', 'axis', 'individual_orientation']
#         box = self.draw_box(self.layout, 'Axis', 'show_expand_axis',
#                             reset_attrs=attrs)
#         column = box.column(align=True)
#         # if self.show_expand_axis:
#         self.draw_property('space', column, text='')
#         prop = self.draw_property(
#             'axis', column, text='', row=True, expand=True)
#         if self.space == 'AXIS':
#             prop.active = False
#         if self.show_expand_axis:
#             column = box.column()
#             self.draw_property('individual_orientation', column)
#
#         # Group
#         self.draw_group_boxes(context, self.layout)
#
#         # Others
#         attrs = ['plane_offset', 'axis_offset', 'influence']
#         box = self.draw_box(self.layout, 'Others', 'show_expand_others',
#                             reset_attrs=attrs)
#         column = box.column()
#         if self.show_expand_others:
#             self.draw_property('plane_offset', column)
#             self.draw_property('axis_offset', column)
#         self.draw_property('influence', column)

