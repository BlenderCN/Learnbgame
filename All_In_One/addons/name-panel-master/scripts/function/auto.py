
# imports
import bpy
import re
from random import random
from . import shared
from .. import storage

# name
def main(self, context):
  '''
    Send datablock values to name.
  '''

  # option
  option = context.window_manager.AutoName

  # mode
  if option.mode in {'SELECTED', 'OBJECTS'}:

    for object in bpy.data.objects:

      # objects
      if option.objects:

        # mode
        if option.mode in 'SELECTED':
          if object.select:

            # object type
            if option.objectType in 'ALL':

              # populate
              populate(self, context, object)

            # object type
            elif option.objectType in object.type:

              # populate
              populate(self, context, object)

        # mode
        else:

          # object type
          if option.objectType in 'ALL':

            # populate
            populate(self, context, object)

          # object type
          elif option.objectType in object.type:

            # populate
            populate(self, context, object)

      # constraints
      if option.constraints:

        # mode
        if option.mode in 'SELECTED':
          if object.select:
            for constraint in object.constraints:

              # constraint type
              if option.constraintType in 'ALL':

                # populate
                populate(self, context, constraint)

              # constraint type
              elif option.constraintType in constraint.type:

                # populate
                populate(self, context, constraint)

        # mode
        else:
          for constraint in object.constraints:

            # constraint type
            if option.constraintType in 'ALL':

              # populate
              populate(self, context, constraint)

            # constraint type
            elif option.constraintType in constraint.type:

              # populate
              populate(self, context, constraint)

        # process
        process(self, context, self.constraints)

      # modifiers
      if option.modifiers:

        # mode
        if option.mode in 'SELECTED':
          if object.select:
            for modifier in object.modifiers:

              # modifier type
              if option.modifierType in 'ALL':

                # populate
                populate(self, context, modifier)

              # modifier type
              elif option.modifierType in modifier.type:

                # populate
                populate(self, context, modifier)
        else:
          for modifier in object.modifiers:

            # modifier type
            if option.modifierType in 'ALL':

              # populate
              populate(self, context, modifier)

            # modifier type
            elif option.modifierType in modifier.type:

              # populate
              populate(self, context, modifier)

        # process
        process(self, context, self.modifiers)

      # object data
      if option.objectData:
        if object.type not in 'EMPTY':

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # object type
              if option.objectType in 'ALL':

                # populate
                populate(self, context, object.data, object)

              # object type
              elif option.objectType in object.type:

                # populate
                populate(self, context, object.data, object)

          # mode
          else:

            # object type
            if option.objectType in 'ALL':

              # populate
              populate(self, context, object.data, object)

            # object type
            elif option.objectType in object.type:

              # populate
              populate(self, context, object.data, object)

      # bone constraints
      if option.boneConstraints:

        # mode
        if option.mode in 'SELECTED':
          if object.select:
            if object.type in 'ARMATURE':
              for bone in object.pose.bones:
                if bone.bone.select:
                  for constraint in bone.constraints:

                    # constraint type
                    if option.constraintType in 'ALL':

                      # populate
                      populate(self, context, constraint)

                    # constraint type
                    elif option.constraintType in constraint.type:

                      # populate
                      populate(self, context, constraint)
        else:
          if object.type in 'ARMATURE':
            for bone in object.pose.bones:
              for constraint in bone.constraints:

                # constraint type
                if option.constraintType in 'ALL':

                  # populate
                  populate(self, context, constraint)

                # constraint type
                elif option.constraintType in constraint.type:

                  # populate
                  populate(self, context, constraint)

        # process
        process(self, context, self.constraints)

  # mode
  else:
    for object in context.scene.objects:

      # objects
      if option.objects:

        # object type
        if option.objectType in 'ALL':

          # populate
          populate(self, context, object)

        # object type
        elif option.objectType in object.type:

          # populate
          populate(self, context, object)

      # constraints
      if option.constraints:
        for constraint in object.constraints:

          # constraint type
          if option.constraintType in 'ALL':

            # populate
            populate(self, context, constraint)

          # constraint type
          elif option.constraintType in constraint.type:

            # populate
            populate(self, context, constraint)

        # process
        process(self, context, self.constraints)

      # modifiers
      if option.modifiers:
        for modifier in object.modifiers:

          # modifier type
          if option.modifierType in 'ALL':

            # populate
            populate(self, context, modifier)

          # modifier type
          elif option.modifierType in modifier.type:

            # populate
            populate(self, context, modifier)

        # process
        process(self, context, self.modifiers)

      # object data
      if option.objectData:
        if object.type not in 'EMPTY':

          # object type
          if option.objectType in 'ALL':

            # populate
            populate(self, context, object.data, object)

          # object type
          elif option.objectType in object.type:

            # populate
            populate(self, context, object.data, object)

      # bone constraints
      if option.boneConstraints:
        if object.type in 'ARMATURE':
          for bone in object.pose.bones:
            for constraint in bone.constraints:

              # constraint type
              if option.constraintType in 'ALL':

                # populate
                populate(self, context, constraint)

              # constraint type
              elif option.constraintType in constraint.type:

                # populate
                populate(self, context, constraint)

        # process
        process(self, context, self.constraints)

  # all
  all = [
    # object
    self.objects,

    # constraints
    # self.constraints,

    # modifiers
    # self.modifiers,

    # cameras
    self.cameras,

    # meshes
    self.meshes,

    # curves
    self.curves,

    # lamps
    self.lamps,

    # lattices
    self.lattices,

    # metaballs
    self.metaballs,

    # speakers
    self.speakers,

    # armatures
    self.armatures,
  ]

  # process
  for collection in all:
    if collection != []:

      # process
      process(self, context, collection)

# populate
def populate(self, context, datablock, source=None):
  '''
    Sort datablocks into proper storage list.
  '''

  # option
  option = context.window_manager.BatchName

  # objects
  if datablock.rna_type.identifier == 'Object':
    self.objects.append([datablock.name, datablock.name, datablock.name, [datablock, ''], 'OBJECT'])

  # constraints
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Constraint':
      self.constraints.append([datablock.name, datablock.name, datablock.name, [datablock, ''], 'CONSTRAINT'])

  # modifiers
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Modifier':
      self.modifiers.append([datablock.name, datablock.name, datablock.name, [datablock, ''], 'MODIFIER'])

  # cameras
  if datablock.rna_type.identifier == 'Camera':
    self.cameras.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # meshes
  if datablock.rna_type.identifier == 'Mesh':
    self.meshes.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # curves
  if datablock.rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:
    self.curves.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # lamps
  if hasattr(datablock.rna_type.base, 'identifier'):
    if datablock.rna_type.base.identifier == 'Lamp':
      self.lamps.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # lattices
  if datablock.rna_type.identifier == 'Lattice':
    self.lattices.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # metaballs
  if datablock.rna_type.identifier == 'MetaBall':
    self.metaballs.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # speakers
  if datablock.rna_type.identifier == 'Speaker':
    self.speakers.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

  # armatures
  if datablock.rna_type.identifier == 'Armature':
    self.armatures.append([datablock.name, datablock.name, datablock.name, [datablock, '', source], 'DATA'])

def process(self, context, collection):
  '''
    Process collection, send names to rename and shared sort.
  '''

  # compare
  compare = []

  # clean
  clean = []

  # clean duplicates
  for name in collection:

    # remove duplicates
    if name[3][0] not in compare:

      # append
      compare.append(name[3][0])
      clean.append(name)

  # done with collection
  collection.clear()

  # name
  for i, name in enumerate(clean):
    rename(self, context, name, i)

  # randomize names (prevents conflicts)
  for name in clean:

    # randomize name
    name[3][0].name = str(random())

  # is shared sort or shared count
  if context.window_manager.BatchShared.sort or context.window_manager.BatchShared.count:

    # sort
    shared.main(self, context, clean, context.window_manager.BatchShared)

  # isnt shared sort or shared count
  else:

    # apply names
    for name in clean:
      name[3][0].name = name[1]

      # count
      if name[1] != name[2]:
        self.count += 1

  # purge re
  re.purge()

# object
def rename(self, context, name, i):
  '''
    Change the datablock names based on its type.
  '''

  # option
  option = context.window_manager.AutoName

  # object name
  objectName = context.scene.ObjectNames

  # constraint name
  constraintName = context.scene.ConstraintNames

  # modifier name
  modifierName = context.scene.ModifierNames

  # object data name
  objectDataName = context.scene.ObjectDataNames

  # object
  if name[4] == 'OBJECT':

    # mesh
    if name[3][0].type == 'MESH':
      name[1] = objectName.mesh + name[1] if objectName.prefix else objectName.mesh
      name[0] = name[1] + str(i)

    # curve
    if name[3][0].type == 'CURVE':
      name[1] = objectName.curve + name[1] if objectName.prefix else objectName.curve
      name[0] = name[1] + str(i)

    # surface
    if name[3][0].type == 'SURFACE':
      name[1] = objectName.surface + name[1] if objectName.prefix else objectName.surface
      name[0] = name[1] + str(i)

    # meta
    if name[3][0].type == 'META':
      name[1] = objectName.meta + name[1] if objectName.prefix else objectName.meta
      name[0] = name[1] + str(i)

    # font
    if name[3][0].type == 'FONT':
      name[1] = objectName.font + name[1] if objectName.prefix else objectName.font
      name[0] = name[1] + str(i)

    # armature
    if name[3][0].type == 'ARMATURE':
      name[1] = objectName.armature + name[1] if objectName.prefix else objectName.armature
      name[0] = name[1] + str(i)

    # lattice
    if name[3][0].type == 'LATTICE':
      name[1] = objectName.lattice + name[1] if objectName.prefix else objectName.lattice
      name[0] = name[1] + str(i)

    # empty
    if name[3][0].type == 'EMPTY':
      name[1] = objectName.empty + name[1] if objectName.prefix else objectName.empty
      name[0] = name[1] + str(i)

    # speaker
    if name[3][0].type == 'SPEAKER':
      name[1] = objectName.speaker + name[1] if objectName.prefix else objectName.speaker
      name[0] = name[1] + str(i)

    # camera
    if name[3][0].type == 'CAMERA':
      name[1] = objectName.camera + name[1] if objectName.prefix else objectName.camera
      name[0] = name[1] + str(i)

    # lamp
    if name[3][0].type == 'LAMP':
      name[1] = objectName.lamp + name[1] if objectName.prefix else objectName.lamp
      name[0] = name[1] + str(i)

  # constraint (bone constraint)
  if name[4] == 'CONSTRAINT':

    # camera solver
    if name[3][0].type == 'CAMERA_SOLVER':
      name[1] = constraintName.cameraSolver + name[1] if constraintName.prefix else constraintName.cameraSolver
      name[0] = name[1] + str(i)

    # follow track
    if name[3][0].type == 'FOLLOW_TRACK':
      name[1] = constraintName.followTrack + name[1] if constraintName.prefix else constraintName.followTrack
      name[0] = name[1] + str(i)

    # object solver
    if name[3][0].type == 'OBJECT_SOLVER':
      name[1] = constraintName.objectSolver + name[1] if constraintName.prefix else constraintName.objectSolver
      name[0] = name[1] + str(i)

    # copy location
    if name[3][0].type == 'COPY_LOCATION':
      name[1] = constraintName.copyLocation + name[1] if constraintName.prefix else constraintName.copyLocation
      name[0] = name[1] + str(i)

    # copy rotation
    if name[3][0].type == 'COPY_ROTATION':
      name[1] = constraintName.copyRotation + name[1] if constraintName.prefix else constraintName.copyRotation
      name[0] = name[1] + str(i)

    # copy scale
    if name[3][0].type == 'COPY_SCALE':
      name[1] = constraintName.copyScale + name[1] if constraintName.prefix else constraintName.copyScale
      name[0] = name[1] + str(i)

    # copy transforms
    if name[3][0].type == 'COPY_TRANSFORMS':
      name[1] = constraintName.copyTransforms + name[1] if constraintName.prefix else constraintName.copyTransforms
      name[0] = name[1] + str(i)

    # limit distance
    if name[3][0].type == 'LIMIT_DISTANCE':
      name[1] = constraintName.limitDistance + name[1] if constraintName.prefix else constraintName.limitDistance
      name[0] = name[1] + str(i)

    # limit location
    if name[3][0].type == 'LIMIT_LOCATION':
      name[1] = constraintName.limitLocation + name[1] if constraintName.prefix else constraintName.limitLocation
      name[0] = name[1] + str(i)

    # limit rotation
    if name[3][0].type == 'LIMIT_ROTATION':
      name[1] = constraintName.limitRotation + name[1] if constraintName.prefix else constraintName.limitRotation
      name[0] = name[1] + str(i)

    # limit scale
    if name[3][0].type == 'LIMIT_SCALE':
      name[1] = constraintName.limitScale + name[1] if constraintName.prefix else constraintName.limitScale
      name[0] = name[1] + str(i)

    # maintain volume
    if name[3][0].type == 'MAINTAIN_VOLUME':
      name[1] = constraintName.maintainVolume + name[1] if constraintName.prefix else constraintName.maintainVolume
      name[0] = name[1] + str(i)

    # transform
    if name[3][0].type == 'TRANSFORM':
      name[1] = constraintName.transform + name[1] if constraintName.prefix else constraintName.transform
      name[0] = name[1] + str(i)

    # clamp to
    if name[3][0].type == 'CLAMP_TO':
      name[1] = constraintName.clampTo + name[1] if constraintName.prefix else constraintName.clampTo
      name[0] = name[1] + str(i)

    # damped track
    if name[3][0].type == 'DAMPED_TRACK':
      name[1] = constraintName.dampedTrack + name[1] if constraintName.prefix else constraintName.dampedTrack
      name[0] = name[1] + str(i)

    # inverse kinematics
    if name[3][0].type == 'IK':
      name[1] = constraintName.inverseKinematics + name[1] if constraintName.prefix else constraintName.inverseKinematics
      name[0] = name[1] + str(i)

    # locked track
    if name[3][0].type == 'LOCKED_TRACK':
      name[1] = constraintName.lockedTrack + name[1] if constraintName.prefix else constraintName.lockedTrack
      name[0] = name[1] + str(i)

    # spline inverse kinematics
    if name[3][0].type == 'SPLINE_IK':
      name[1] = constraintName.splineInverseKinematics + name[1] if constraintName.prefix else constraintName.splineInverseKinematics
      name[0] = name[1] + str(i)

    # stretch to
    if name[3][0].type == 'STRETCH_TO':
      name[1] = constraintName.stretchTo + name[1] if constraintName.prefix else constraintName.stretchTo
      name[0] = name[1] + str(i)

    # track to
    if name[3][0].type == 'TRACK_TO':
      name[1] = constraintName.trackTo + name[1] if constraintName.prefix else constraintName.trackTo
      name[0] = name[1] + str(i)

    # action
    if name[3][0].type == 'ACTION':
      name[1] = constraintName.action + name[1] if constraintName.prefix else constraintName.action
      name[0] = name[1] + str(i)

    # child of
    if name[3][0].type == 'CHILD_OF':
      name[1] = constraintName.childOf + name[1] if constraintName.prefix else constraintName.childOf
      name[0] = name[1] + str(i)

    # floor
    if name[3][0].type == 'FLOOR':
      name[1] = constraintName.floor + name[1] if constraintName.prefix else constraintName.floor
      name[0] = name[1] + str(i)

    # follow path
    if name[3][0].type == 'FOLLOW_PATH':
      name[1] = constraintName.followPath + name[1] if constraintName.prefix else constraintName.followPath
      name[0] = name[1] + str(i)

    # pivot
    if name[3][0].type == 'PIVOT':
      name[1] = constraintName.pivot + name[1] if constraintName.prefix else constraintName.pivot
      name[0] = name[1] + str(i)

    # rigid body joint
    if name[3][0].type == 'RIGID_BODY_JOINT':
      name[1] = constraintName.rigidBodyJoint + name[1] if constraintName.prefix else constraintName.rigidBodyJoint
      name[0] = name[1] + str(i)

    # shrinkwrap
    if name[3][0].type == 'SHRINKWRAP':
      name[1] = constraintName.shrinkwrap + name[1] if constraintName.prefix else constraintName.shrinkwrap
      name[0] = name[1] + str(i)

  # modifier
  if name[4] == 'MODIFIER':

    # data transfer
    if name[3][0].type == 'DATA_TRANSFER':
      name[1] = modifierName.dataTransfer + name[1] if modifierName.prefix else modifierName.dataTransfer
      name[0] = name[1] + str(i)

    # mesh cache
    if name[3][0].type == 'MESH_CACHE':
      name[1] = modifierName.meshCache + name[1] if modifierName.prefix else modifierName.meshCache
      name[0] = name[1] + str(i)

    # normal edit
    if name[3][0].type == 'NORMAL_EDIT':
      name[1] = modifierName.normalEdit + name[1] if modifierName.prefix else modifierName.normalEdit
      name[0] = name[1] + str(i)

    # uv project
    if name[3][0].type == 'UV_PROJECT':
      name[1] = modifierName.uvProject + name[1] if modifierName.prefix else modifierName.uvProject
      name[0] = name[1] + str(i)

    # uv warp
    if name[3][0].type == 'UV_WARP':
      name[1] = modifierName.uvWarp + name[1] if modifierName.prefix else modifierName.uvWarp
      name[0] = name[1] + str(i)

    # vertex weight edit
    if name[3][0].type == 'VERTEX_WEIGHT_EDIT':
      name[1] = modifierName.vertexWeightEdit + name[1] if modifierName.prefix else modifierName.vertexWeightEdit
      name[0] = name[1] + str(i)

    # vertex weight mix
    if name[3][0].type == 'VERTEX_WEIGHT_MIX':
      name[1] = modifierName.vertexWeightMix + name[1] if modifierName.prefix else modifierName.vertexWeightMix
      name[0] = name[1] + str(i)

    # vertex weight proximity
    if name[3][0].type == 'VERTEX_WEIGHT_PROXIMITY':
      name[1] = modifierName.vertexWeightProximity + name[1] if modifierName.prefix else modifierName.vertexWeightProximity
      name[0] = name[1] + str(i)

    # array
    if name[3][0].type == 'ARRAY':
      name[1] = modifierName.array + name[1] if modifierName.prefix else modifierName.array
      name[0] = name[1] + str(i)

    # bevel
    if name[3][0].type == 'BEVEL':
      name[1] = modifierName.bevel + name[1] if modifierName.prefix else modifierName.bevel
      name[0] = name[1] + str(i)

    # boolean
    if name[3][0].type == 'BOOLEAN':
      name[1] = modifierName.boolean + name[1] if modifierName.prefix else modifierName.boolean
      name[0] = name[1] + str(i)

    # build
    if name[3][0].type == 'BUILD':
      name[1] = modifierName.build + name[1] if modifierName.prefix else modifierName.build
      name[0] = name[1] + str(i)

    # decimate
    if name[3][0].type == 'DECIMATE':
      name[1] = modifierName.decimate + name[1] if modifierName.prefix else modifierName.decimate
      name[0] = name[1] + str(i)

    # edge split
    if name[3][0].type == 'EDGE_SPLIT':
      name[1] = modifierName.edgeSplit + name[1] if modifierName.prefix else modifierName.edgeSplit
      name[0] = name[1] + str(i)

    # mask
    if name[3][0].type == 'MASK':
      name[1] = modifierName.mask + name[1] if modifierName.prefix else modifierName.mask
      name[0] = name[1] + str(i)

    # mirror
    if name[3][0].type == 'MIRROR':
      name[1] = modifierName.mirror + name[1] if modifierName.prefix else modifierName.mirror
      name[0] = name[1] + str(i)

    # multiresolution
    if name[3][0].type == 'MULTIRES':
      name[1] = modifierName.multiresolution + name[1] if modifierName.prefix else modifierName.multiresolution
      name[0] = name[1] + str(i)

    # remesh
    if name[3][0].type == 'REMESH':
      name[1] = modifierName.remesh + name[1] if modifierName.prefix else modifierName.remesh
      name[0] = name[1] + str(i)

    # screw
    if name[3][0].type == 'SCREW':
      name[1] = modifierName.screw + name[1] if modifierName.prefix else modifierName.screw
      name[0] = name[1] + str(i)

    # skin
    if name[3][0].type == 'SKIN':
      name[1] = modifierName.skin + name[1] if modifierName.prefix else modifierName.skin
      name[0] = name[1] + str(i)

    # solidify
    if name[3][0].type == 'SOLIDIFY':
      name[1] = modifierName.solidify + name[1] if modifierName.prefix else modifierName.solidify
      name[0] = name[1] + str(i)

    # subdivision surface
    if name[3][0].type == 'SUBSURF':
      name[1] = modifierName.subdivisionSurface + name[1] if modifierName.prefix else modifierName.subdivisionSurface
      name[0] = name[1] + str(i)

    # triangulate
    if name[3][0].type == 'TRIANGULATE':
      name[1] = modifierName.triangulate + name[1] if modifierName.prefix else modifierName.triangulate
      name[0] = name[1] + str(i)

    # wireframe
    if name[3][0].type == 'WIREFRAME':
      name[1] = modifierName.wireframe + name[1] if modifierName.prefix else modifierName.wireframe
      name[0] = name[1] + str(i)

    # armature
    if name[3][0].type == 'ARMATURE':
      name[1] = modifierName.armature + name[1] if modifierName.prefix else modifierName.armature
      name[0] = name[1] + str(i)

    # cast
    if name[3][0].type == 'CAST':
      name[1] = modifierName.cast + name[1] if modifierName.prefix else modifierName.cast
      name[0] = name[1] + str(i)

    # corrective smooth
    if name[3][0].type == 'CORRECTIVE_SMOOTH':
      name[1] = modifierName.correctiveSmooth + name[1] if modifierName.prefix else modifierName.correctiveSmooth
      name[0] = name[1] + str(i)

    # curve
    if name[3][0].type == 'CURVE':
      name[1] = modifierName.curve + name[1] if modifierName.prefix else modifierName.curve
      name[0] = name[1] + str(i)

    # displace
    if name[3][0].type == 'DISPLACE':
      name[1] = modifierName.displace + name[1] if modifierName.prefix else modifierName.displace
      name[0] = name[1] + str(i)

    # hook
    if name[3][0].type == 'HOOK':
      name[1] = modifierName.hook + name[1] if modifierName.prefix else modifierName.hook
      name[0] = name[1] + str(i)

    # laplacian smooth
    if name[3][0].type == 'LAPLACIANSMOOTH':
      name[1] = modifierName.laplacianSmooth + name[1] if modifierName.prefix else modifierName.laplacianSmooth
      name[0] = name[1] + str(i)

    # laplacian deform
    if name[3][0].type == 'LAPLACIANDEFORM':
      name[1] = modifierName.laplacianDeform + name[1] if modifierName.prefix else modifierName.laplacianDeform
      name[0] = name[1] + str(i)

    # lattice
    if name[3][0].type == 'LATTICE':
      name[1] = modifierName.lattice + name[1] if modifierName.prefix else modifierName.lattice
      name[0] = name[1] + str(i)

    # mesh deform
    if name[3][0].type == 'MESH_DEFORM':
      name[1] = modifierName.meshDeform + name[1] if modifierName.prefix else modifierName.meshDeform
      name[0] = name[1] + str(i)

    # shrinkwrap
    if name[3][0].type == 'SHRINKWRAP':
      name[1] = modifierName.shrinkwrap + name[1] if modifierName.prefix else modifierName.shrinkwrap
      name[0] = name[1] + str(i)

    # simple deform
    if name[3][0].type == 'SIMPLE_DEFORM':
      name[1] = modifierName.simpleDeform + name[1] if modifierName.prefix else modifierName.simpleDeform
      name[0] = name[1] + str(i)

    # smooth
    if name[3][0].type == 'SMOOTH':
      name[1] = modifierName.smooth + name[1] if modifierName.prefix else modifierName.smooth
      name[0] = name[1] + str(i)

    # warp
    if name[3][0].type == 'WARP':
      name[1] = modifierName.warp + name[1] if modifierName.prefix else modifierName.warp
      name[0] = name[1] + str(i)

    # wave
    if name[3][0].type == 'WAVE':
      name[1] = modifierName.wave + name[1] if modifierName.prefix else modifierName.wave
      name[0] = name[1] + str(i)

    # cloth
    if name[3][0].type == 'CLOTH':
      name[1] = modifierName.cloth + name[1] if modifierName.prefix else modifierName.cloth
      name[0] = name[1] + str(i)

    # collision
    if name[3][0].type == 'COLLISION':
      name[1] = modifierName.collision + name[1] if modifierName.prefix else modifierName.collision
      name[0] = name[1] + str(i)

    # dynamic paint
    if name[3][0].type == 'DYNAMIC_PAINT':
      name[1] = modifierName.dynamicPaint + name[1] if modifierName.prefix else modifierName.dynamicPaint
      name[0] = name[1] + str(i)

    # explode
    if name[3][0].type == 'EXPLODE':
      name[1] = modifierName.explode + name[1] if modifierName.prefix else modifierName.explode
      name[0] = name[1] + str(i)

    # fluid simulation
    if name[3][0].type == 'FLUID_SIMULATION':
      name[1] = modifierName.fluidSimulation + name[1] if modifierName.prefix else modifierName.fluidSimulation
      name[0] = name[1] + str(i)

    # ocean
    if name[3][0].type == 'OCEAN':
      name[1] = modifierName.ocean + name[1] if modifierName.prefix else modifierName.ocean
      name[0] = name[1] + str(i)

    # particle instance
    if name[3][0].type == 'PARTICLE_INSTANCE':
      name[1] = modifierName.particleInstance + name[1] if modifierName.prefix else modifierName.particleInstance
      name[0] = name[1] + str(i)

    # particle system
    if name[3][0].type == 'PARTICLE_SYSTEM':
      name[1] = modifierName.particleSystem + name[1] if modifierName.prefix else modifierName.particleSystem
      name[0] = name[1] + str(i)

    # smoke
    if name[3][0].type == 'SMOKE':
      name[1] = modifierName.smoke + name[1] if modifierName.prefix else modifierName.smoke
      name[0] = name[1] + str(i)

    # soft body
    if name[3][0].type == 'SOFT_BODY':
      name[1] = modifierName.softBody + name[1] if modifierName.prefix else modifierName.softBody
      name[0] = name[1] + str(i)

  # object data
  if name[4] == 'DATA':

    # mesh
    if name[3][2].type == 'MESH':
      name[1] = objectDataName.mesh + name[1] if objectDataName.prefix else objectDataName.mesh
      name[0] = name[1] + str(i)

    # curve
    if name[3][2].type == 'CURVE':
      name[1] = objectDataName.curve + name[1] if objectDataName.prefix else objectDataName.curve
      name[0] = name[1] + str(i)

    # surface
    if name[3][2].type == 'SURFACE':
      name[1] = objectDataName.surface + name[1] if objectDataName.prefix else objectDataName.surface
      name[0] = name[1] + str(i)

    # meta
    if name[3][2].type == 'META':
      name[1] = objectDataName.meta + name[1] if objectDataName.prefix else objectDataName.meta
      name[0] = name[1] + str(i)

    # font
    if name[3][2].type == 'FONT':
      name[1] = objectDataName.font + name[1] if objectDataName.prefix else objectDataName.font
      name[0] = name[1] + str(i)

    # armature
    if name[3][2].type == 'ARMATURE':
      name[1] = objectDataName.armature + name[1] if objectDataName.prefix else objectDataName.armature
      name[0] = name[1] + str(i)

    # lattice
    if name[3][2].type == 'LATTICE':
      name[1] = objectDataName.lattice + name[1] if objectDataName.prefix else objectDataName.lattice
      name[0] = name[1] + str(i)

    # empty
    # if name[3][2].type == 'EMPTY':
      # name[1] = objectDataName.empty + name[1] if objectDataName.prefix else objectDataName.empty
      # name[0] = name[1] + str(i)

    # speaker
    if name[3][2].type == 'SPEAKER':
      name[1] = objectDataName.speaker + name[1] if objectDataName.prefix else objectDataName.speaker
      name[0] = name[1] + str(i)

    # camera
    if name[3][2].type == 'CAMERA':
      name[1] = objectDataName.camera + name[1] if objectDataName.prefix else objectDataName.camera
      name[0] = name[1] + str(i)

    # lamp
    if name[3][2].type == 'LAMP':
      name[1] = objectDataName.lamp + name[1] if objectDataName.prefix else objectDataName.lamp
      name[0] = name[1] + str(i)
