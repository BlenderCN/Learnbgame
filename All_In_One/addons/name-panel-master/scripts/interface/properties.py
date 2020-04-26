
# imports
import bpy
from bpy.types import Panel
from .buttons.object import Object
from .buttons.group import Group
from .buttons.greasepencil import GreasePencil
from .buttons.action import Action
from .buttons.constraint import Constraint
from .buttons.modifier import Modifier
from .buttons.objectdata import ObjectData
from .buttons.bonegroup import BoneGroup
from .buttons.bone import Bone
from .buttons.vertexgroup import VertexGroup
from .buttons.uv import UV
from .buttons.shapekey import Shapekey
from .buttons.vertexcolor import VertexColor
from .buttons.material import Material
from .buttons.texture import Texture
from .buttons.particlesystem import ParticleSystem
from .buttons.particlesettings import ParticleSettings

# tools properties
class toolsProperties(Panel):
  '''
    Name Panel context sensitive properties panel for the 3D View toolshelf.
  '''
  bl_idname = 'VIEW3D_PT_TOOLS_properties'
  bl_space_type = 'VIEW_3D'
  bl_label = 'Properties'
  bl_region_type = 'TOOLS'
  bl_category = 'Name'

  # draw
  def draw(self, context):
    '''
      Properties panel body.
    '''

    # main
    main(self, context)

# UI properties
class UIProperties(Panel):
  '''
    Name panel context sensitive properties panel for the 3D View property shelf.
  '''
  bl_idname = 'VIEW3D_PT_UI_properties'
  bl_space_type = 'VIEW_3D'
  bl_label = 'Properties'
  bl_region_type = 'UI'

  # draw
  def draw(self, context):
    '''
      Properties panel body.
    '''

    # main
    main(self, context)

# main
def main(self, context):
  '''
    Get the owner, target and context of name panel, populate accordingly.
  '''

  # panel
  panel = context.scene.NamePanel

  # layout
  layout = self.layout

  # row
  row = layout.row(align=True)

  # back
  row.operator('view3d.name_panel_previous', text='', icon='BACK')

  # context
  row.prop(panel, 'context', text='')

  # to object
  row.operator('view3d.name_panel_to_object', text='', icon='OBJECT_DATA')

  # to data
  row.operator('view3d.name_panel_to_data', text='', icon='MESH_DATA')

  # is context object
  if context.active_object:

    # is armature
    if context.active_object.type == 'ARMATURE':

      # to bone
      row.operator('view3d.name_panel_to_bone', text='', icon='BONE_DATA')

    # object
    if panel.context == 'OBJECT':

        # object
        Object(self, context, layout, context.active_object)


    # object data
    elif panel.context == 'OBJECT_DATA':

      # object
      ObjectData(self, context, layout, context.active_object)

    # is active bone
    if context.active_bone:

      # bone
      if panel.context == 'BONE':


          # bone
          Bone(self, context, layout)

  # is owner
  if panel.owner:

    # group
    if panel.context == 'GROUP':

      # group
      Group(self, context, layout, bpy.data.groups[panel.target])

    # # grease pencil
    # elif panel.context == 'GREASE_PENCIL':
    #
    #   # grease pencil
    #   GreasePencil(self, context, layout, bpy.data.grease_pencil[panel.target])

    # action
    elif panel.context == 'ACTION':

      # has action
      if hasattr(bpy.data.objects[panel.owner].animation_data, 'action'):

        # action
        Action(self, context, layout, bpy.data.objects[panel.owner], bpy.data.actions[panel.target])

    # constraint
    elif panel.context == 'CONSTRAINT':

      # constraint
      Constraint.main(self, context, layout, bpy.data.objects[panel.owner].constraints[panel.target])

    # modifier
    elif panel.context == 'MODIFIER':

      # modifier
      Modifier.main(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].modifiers[panel.target])

    # bone group
    elif panel.context == 'BONE_GROUP':

      # bone group
      BoneGroup(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].pose.bone_groups[panel.target])

    # bone constraint
    elif panel.context == 'BONE_CONSTRAINT':

      # bone constraint
      Constraint.main(self, context, layout, context.active_object.pose.bones[panel.owner].constraints[panel.target])

    # vertex group
    elif panel.context == 'VERTEX_GROUP':

      # vertex group
      VertexGroup(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].vertex_groups[panel.target])

    # shapekey
    elif panel.context == 'SHAPEKEY':

      # shapekey
      Shapekey(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].data.shape_keys.key_blocks[panel.target])

    # uv
    elif panel.context == 'UV':

      # uv
      UV(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].data.uv_textures[panel.target])

    # vertex color
    elif panel.context == 'VERTEX_COLOR':

      # vertex color
      VertexColor(self, context, layout, bpy.data.objects[panel.owner], bpy.data.objects[panel.owner].data.vertex_colors[panel.target])

    # material
    # elif panel.context == 'MATERIAL':
    #
    #   # material
    #   Material(self, context, layout, bpy.data.objects[panel.owner], bpy.data.materials[panel.target])

    # texture
    # elif panel.context == 'TEXTURE':
    #
    #   # texture
    #   Texture(self, context, layout, owner, bpy.data.textures[panel.target])

    # particle system
    # elif panel.context == 'PARTICLE_SYSTEM':
    #
    #   # particle systems
    #   ParticleSystem(self, context, layout, bpy.data.objects[panel.owner].particle_systems[panel.target])

    # particle setting
    # elif panel.context == 'PARTICLE_SETTING':
    #
    #   # particle settings
    #   ParticleSettings(self, context, layout, bpy.data.particles[panel.target])
