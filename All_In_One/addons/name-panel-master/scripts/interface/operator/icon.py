
# imports
import bpy
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, EnumProperty

# operator
class operator(Operator):
  '''
    Assigns an active object.
  '''
  bl_idname = 'view3d.name_panel_icon'
  bl_label = 'Name Panel Icon'
  bl_description = 'Changes active object.'
  bl_options = {'UNDO', 'INTERNAL'}

  # active
  active = BoolProperty(
    name = 'Active',
    description = 'Make this the active object.',
    default = False
  )

  # extend
  extend = BoolProperty(
    name = 'Extend',
    description = 'Keep old selection.',
    default = False
  )

  # view
  view = BoolProperty(
    name = 'View',
    description = 'Center the 3D view on the object.',
    default = False
  )

  # owner
  owner = StringProperty(
    name = 'Owner',
    description = 'The owner\'s name of the target datablock.',
    default = ''
  )

  # target
  target = StringProperty(
    name = 'Target',
    description = 'Datablock target\'s name belonging to the owner.',
    default = ''
  )

  # context
  context = EnumProperty(
    name = 'Context',
    description = 'The context the name panel is in based on last icon clicked',
    items = [
      ('OBJECT', 'Object', '', 'OBJECT_DATA', 0),
      ('GROUP', 'Group', '', 'GROUP', 1),
      ('ACTION', 'Action', '', 'ACTION', 2),
      # ('GREASE_PENCIL', 'Grease Pencil', '', 'GREASEPENCIL', 3),
      ('CONSTRAINT', 'Constraint', '', 'CONSTRAINT', 4),
      ('MODIFIER', 'Modifier', '', 'MODIFIER', 5),
      ('OBJECT_DATA', 'Object Data', '', 'MESH_DATA', 6),
      ('BONE_GROUP', 'Bone Group', '', 'GROUP_BONE', 7),
      ('BONE', 'Bone', '', 'BONE_DATA', 8),
      ('BONE_CONSTRAINT', 'Bone Constraint', '', 'CONSTRAINT_BONE', 9),
      ('VERTEX_GROUP', 'Vertex Group', '', 'GROUP_VERTEX', 10),
      ('SHAPEKEY', 'Shapekey', '', 'SHAPEKEY_DATA', 11),
      ('UV', 'UV Map', '', 'GROUP_UVS', 12),
      ('VERTEX_COLOR', 'Vertex Colors', '', 'GROUP_VCOL', 13),
      # ('MATERIAL', 'Material', '', 'MATERIAL', 14),
      # ('TEXTURE', 'Texture', '', 'TEXTURE', 15),
      # ('PARTICLE_SYSTEM', 'Particle System', '', 'PARTICLES', 16),
      # ('PARTICLE_SETTING', 'Particle Settings', '', 'DOT', 17)
    ],
    default = 'OBJECT'
  )

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Operator options.
    '''

    # layout
    layout = self.layout

    # active
    layout.prop(self, 'active')

    # extend
    layout.prop(self, 'extend')

    # view
    layout.prop(self, 'view')

  # execute
  def invoke(self, context, event):
    '''
      Invoke the operator.
    '''

    # panel
    panel = context.scene.NamePanel
    panel.previousOwner = panel.owner
    panel.previousTarget = panel.target
    panel.previousContext = panel.context
    panel.owner = self.owner
    panel.target = self.target
    panel.context = self.context

    # shift
    if event.shift:
      self.extend = True

    # shift
    else:
      self.extend = False

    # ctrl
    if event.ctrl:
      self.view = True

    # ctrl
    else:
      self.view = False

    # alt
    if event.alt:
      self.active = False

    # alt
    else:
      self.active = True

    # object
    if panel.context not in {'BONE', 'BONE_CONSTRAINT'}: # temporary

      # is hide
      if bpy.data.objects[panel.owner].hide: # preferable for objects, not bones
        bpy.data.objects[panel.owner].hide = False

      # extend
      if self.extend:

        # select active
        context.active_object.select = True

        # owner selected
        if bpy.data.objects[panel.owner].select == True:

          # deselect
          bpy.data.objects[panel.owner].select = False

        # owner selected
        else:

          # select owner
          bpy.data.objects[panel.owner].select = True

          # active
          if self.active:

            # active object
            context.scene.objects.active = bpy.data.objects[panel.owner]

        # extend
      else:

        # deselect all
        for object in context.scene.objects:
          object.select = False

        # active object
        context.scene.objects.active = bpy.data.objects[panel.owner]

        # select active
        context.active_object.select = True

      # view
      if self.view:

        # view selected
        bpy.ops.view3d.view_selected()

    # group
    # action
    # grease pencil

    # constraint
    if panel.context == 'BONE_CONSTRAINT':

      # extend
      if self.extend:

        # select active
        context.active_object.data.bones.active.select = True

        # owner selected
        if context.active_object.data.bones[panel.owner].select == True:

          # deselect
          context.active_object.data.bones[panel.owner].select = False

        # owner selected
        else:

          # select owner
          context.active_object.data.bones[panel.owner].select = True

          # active
          if self.active:

            # active bone
            context.active_object.data.bones.active = context.active_object.data.bones[panel.owner]

      else:

        for bone in context.selected_pose_bones:
          bone.bone.select = False

        # target
        context.active_object.data.bones.active = context.active_object.data.bones[panel.owner]

        # select
        context.active_object.data.bones.active.select = True

      # view
      if self.view:
        bpy.ops.view3d.view_selected()

    # modifier
    # object data

    # bone
    if panel.context == 'BONE':

      # edit mode
      if context.object.mode in 'EDIT':

        # extend
        if self.extend:

          # select
          context.active_object.data.edit_bones.active.select = True

          # select head
          context.active_object.data.edit_bones.active.select_head = True

          # select tail
          context.active_object.data.edit_bones.active.select_tail = True

          # owner selected
          if context.active_object.data.edit_bones[panel.target].select == True:

            # deselect
            context.active_object.data.edit_bones[panel.target].select = False

            # deselect head
            context.active_object.data.edit_bones[panel.target].select_head = False

            # deselect tail
            context.active_object.data.edit_bones[panel.target].select_tail = False

          # owner selected
          else:

            # deselect
            context.active_object.data.edit_bones[panel.target].select = True

            # deselect head
            context.active_object.data.edit_bones[panel.target].select_head = True

            # deselect tail
            context.active_object.data.edit_bones[panel.target].select_tail = True

            # active
            if self.active:

              # active bone
              context.active_object.data.edit_bones.active = context.active_object.data.edit_bones[panel.target]


        # extend
        else:
          for bone in context.selected_editable_bones:

            # deselect
            bone.select = False

            # deselect head
            bone.select_head = False

            # deselect tail
            bone.select_tail = False

          # active bone
          context.active_object.data.edit_bones.active = context.active_object.data.edit_bones[panel.target]

          # select
          context.active_object.data.edit_bones.active.select = True

          # select head
          context.active_object.data.edit_bones.active.select_head = True

          # select tail
          context.active_object.data.edit_bones.active.select_tail = True

      # pose mode
      else:

        # extend
        if self.extend:

          # select active
          context.active_object.data.bones.active.select = True

          # owner selected
          if context.active_object.data.bones[panel.target].select == True:

            # deselect
            context.active_object.data.bones[panel.target].select = False

          # owner selected
          else:

            # select
            context.active_object.data.bones[panel.target].select = True

            # active
            if self.active:

              # active bone
              context.active_object.data.bones.active = context.active_object.data.bones[panel.target]

        # extend
        else:

          for bone in context.selected_pose_bones:
            bone.bone.select = False

          # target
          context.active_object.data.bones.active = context.active_object.data.bones[panel.target]

          # select
          context.active_object.data.bones.active.select = True

      # view
      if self.view:
        bpy.ops.view3d.view_selected()


    # vertex group
    # warning
    # try:
    #
    #   # not active
    #   if bpy.data.objects[self.object] != context.scene.objects.active:
    #
    #     # object mode
    #     if context.mode != 'OBJECT':
    #       bpy.ops.object.mode_set(mode='OBJECT')
    #
    #     # extend
    #     if self.extend:
    #
    #       # select
    #       context.scene.objects.active.select = True
    #
    #     # extend
    #     else:
    #
    #       # object
    #       for object in context.scene.objects:
    #
    #         # deselect
    #         object.select = False
    #
    #     # select
    #     bpy.data.objects[self.object].select = True
    #
    #     # active object
    #     context.scene.objects.active = bpy.data.objects[self.object]
    #
    # # report
    # except:
    #   self.report({'WARNING'}, 'Invalid object.')
    #
    # # edit mode
    # if context.mode != 'EDIT':
    #   bpy.ops.object.mode_set(mode='EDIT')
    #
    # # bmesh
    # mesh = bmesh.from_edit_mesh(context.active_object.data)
    #
    # # extend
    # if not self.extend:
    #
    #   # clear vertex
    #   for vertex in mesh.verts:
    #     vertex.select = False
    #
    #   # clear edge
    #   for edge in mesh.edges:
    #     edge.select = False
    #
    #   # clear face
    #   for face in mesh.faces:
    #     face.select = False
    #
    # # warning
    # try:
    #
    #   # group index
    #   groupIndex = context.active_object.vertex_groups[self.target].index
    #
    #   # active index
    #   context.active_object.vertex_groups.active_index = groupIndex
    #
    # # report
    # except:
    #   self.report({'WARNING'}, 'Invalid target.')
    #
    # # deform layer
    # deformLayer = mesh.verts.layers.deform.active
    #
    # # select vertices
    # for vertex in mesh.verts:
    #   try:
    #     deformVertex = vertex[deformLayer]
    #     if groupIndex in deformVertex:
    #       vertex.select = True
    #   except:
    #     pass
    #
    # # flush selection
    # mesh.select_flush(True)
    #
    # # update viewport
    # context.scene.objects.active = context.scene.objects.active
    #
    # # properties
    # if self.properties:
    #
    #   # screen
    #   if self.screen != '':
    #
    #     # warning
    #     try:
    #
    #       # area
    #       for area in bpy.data.screens[self.screen].areas:
    #
    #         # type
    #         if area.type in 'PROPERTIES':
    #
    #           # context
    #           area.spaces.active.context = 'DATA'
    #
    #     # report
    #     except:
    #       self.report({'WARNING'}, 'Invalid screen')
    #
    #   # screen
    #   else:
    #
    #     # area
    #     for area in context.window.screen.areas:
    #
    #       # type
    #       if area.type in 'PROPERTIES':
    #
    #         # context
    #         area.spaces.active.context = 'DATA'
    #
    # # layout
    # if self.layout:
    #
    #   # screen
    #   if self.screen != '':
    #
    #     # warning
    #     try:
    #
    #       # active screen
    #       context.window.screen = bpy.data.screens[self.screen]
    #
    #     # report
    #     except:
    #       self.report({'WARNING'}, 'Invalid screen')

    # shapekey
    # uv
    # vertex color
    # material
    # texture
    # particle system
    # particle setting

    return {'FINISHED'}
