
# imports
import bpy

# main
def main(context):
  '''
    Get names from source datablock and assign to destination datablock.
  '''

  # option
  option = context.window_manager.CopyName

  # mode
  if option.mode in {'SELECTED', 'OBJECTS'}:
    for object in bpy.data.objects:

      # source object
      if option.source in 'OBJECT':

        # objects
        if option.objects:

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # use active object
              if option.useActiveObject:
                object.name = context.active_object.name
              else:
                object.name = object.name
          else:

            # use active object
            if option.useActiveObject:
              object.name = context.active_object.name
            else:
              object.name = object.name

        # object data
        if option.objectData:
          if object.type not in 'EMPTY':

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  object.data.name = context.active_object.name
                else:
                  object.data.name = object.name
            else:

              # use active object
              if option.useActiveObject:
                object.data.name = context.active_object.name
              else:
                object.data.name = object.name

        # materials
        if option.materials:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for material in object.material_slots:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    material.material.name = context.active_object.name
                  else:
                    material.material.name = object.name
          else:
            for material in object.material_slots:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  material.material.name = context.active_object.name
                else:
                  material.material.name = object.name

        # textures
        if option.textures:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for material in object.material_slots:
                if material.material != None:
                  for texture in material.material.texture_slots:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        texture.texture.name = context.active_object.name
                      else:
                        texture.texture.name = object.name
          else:
            for material in object.material_slots:
              if material.material != None:
                for texture in material.material.texture_slots:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      texture.texture.name = context.active_object.name
                    else:
                      texture.texture.name = object.name

        # particle systems
        if option.particleSystems:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  system.name = context.active_object.name
                else:
                  system.name = object.name
          else:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                system.name = context.active_object.name
              else:
                system.name = object.name

        # particle settings
        if option.particleSettings:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  system.settings.name = context.active_object.name
                else:
                  system.settings.name = object.name
          else:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                system.settings.name = context.active_object.name
              else:
                system.settings.name = object.name

      # source data
      if option.source in 'DATA':
        if object.type not in 'EMPTY':

          # objects
          if option.objects:

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  object.name = context.active_object.data.name
                else:
                  object.name = object.data.name
            else:

              # use active object
              if option.useActiveObject:
                object.name = context.active_object.data.name
              else:
                object.name = object.data.name

          # object data
          if option.objectData:

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  object.data.name = context.active_object.data.name
                else:
                  object.data.name = object.data.name
            else:

              # use active object
              if option.useActiveObject:
                object.data.name = context.active_object.data.name
              else:
                object.data.name = object.data.name

          # materials
          if option.materials:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      material.material.name = context.active_object.data.name
                    else:
                      material.material.name = object.data.name
            else:
              for material in object.material_slots:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    material.material.name = context.active_object.data.name
                  else:
                    material.material.name = object.data.name

          # textures
          if option.textures:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:
                    for texture in material.material.texture_slots:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          texture.texture.name = context.active_object.data.name
                        else:
                          texture.texture.name = object.data.name
            else:
              for material in object.material_slots:
                if material.material != None:
                  for texture in material.material.texture_slots:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        texture.texture.name = context.active_object.data.name
                      else:
                        texture.texture.name = object.data.name

          # particle systems
          if option.particleSystems:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    system.name = context.active_object.data.name
                  else:
                    system.name = object.data.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  system.name = context.active_object.data.name
                else:
                  system.name = object.data.name

          # particle settings
          if option.particleSettings:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    system.settings.name = context.active_object.data.name
                  else:
                    system.settings.name = object.data.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  system.settings.name = context.active_object.data.name
                else:
                  system.settings.name = object.data.name

      # source material
      if option.source in 'MATERIAL':

        # objects
        if option.objects:

          # mode
          if option.mode in 'SELECTED':
            if object.select:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  object.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  object.name = object.active_material.name
          else:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.active_material, 'name'):
                object.name = context.active_object.active_material.name
            else:
              if hasattr(object.active_material, 'name'):
                object.name = object.active_material.name

        # object data
        if option.objectData:
          if object.type not in 'EMPTY':

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    object.data.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    object.data.name = object.active_material.name
            else:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  object.data.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  object.data.name = object.active_material.name

        # materials
        if option.materials:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for material in object.material_slots:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'name'):
                      material.material.name = context.active_object.active_material.name
                  else:
                    if hasattr(object.active_material, 'name'):
                      material.material.name = object.active_material.name
          else:
            for material in object.material_slots:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    material.material.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    material.material.name = object.active_material.name

        # textures
        if option.textures:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for material in object.material_slots:
                if material.material != None:
                  for texture in material.material.texture_slots:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.active_material, 'name'):
                          texture.texture.name = context.active_object.active_material.name
                      else:
                        if hasattr(object.active_material, 'name'):
                          texture.texture.name = object.active_material.name
          else:
            for material in object.material_slots:
              if material.material != None:
                for texture in material.material.texture_slots:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'name'):
                        texture.texture.name = context.active_object.active_material.name
                    else:
                      if hasattr(object.active_material, 'name'):
                        texture.texture.name = object.active_material.name

        # particle systems
        if option.particleSystems:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    system.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    system.name = object.active_material.name
          else:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  system.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  system.name = object.active_material.name

        # particle settings
        if option.particleSettings:

          # mode
          if option.mode in 'SELECTED':
            if object.select:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'name'):
                    system.settings.name = context.active_object.active_material.name
                else:
                  if hasattr(object.active_material, 'name'):
                    system.settings.name = object.active_material.name
          else:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  system.settings.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  system.settings.name = object.active_material.name

      # source texture
      if option.source in 'TEXTURE':
        if context.scene.render.engine not in 'CYCLES':

          # objects
          if option.objects:

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      object.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      object.name = object.active_material.active_texture.name
            else:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'active_texture'):
                  if hasattr(context.active_object.active_material.active_texture, 'name'):
                    object.name = context.active_object.active_material.active_texture.name
              else:
                if hasattr(object.active_material, 'active_texture'):
                  if hasattr(object.active_material.active_texture, 'name'):
                    object.name = object.active_material.active_texture.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # mode
              if option.mode in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        object.data.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        object.data.name = object.active_material.active_texture.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      object.data.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      object.data.name = object.active_material.active_texture.name

          # materials
          if option.materials:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'active_texture'):
                        if hasattr(context.active_object.active_material.active_texture, 'name'):
                          material.material.name = context.active_object.active_material.active_texture.name
                    else:
                      if hasattr(object.active_material, 'active_texture'):
                        if hasattr(object.active_material.active_texture, 'name'):
                          material.material.name = object.active_material.active_texture.name
            else:
              for material in object.material_slots:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        material.material.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        material.material.name = object.active_material.active_texture.name

          # textures
          if option.textures:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:
                    for texture in material.material.texture_slots:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.active_material, 'active_texture'):
                            if hasattr(context.active_object.active_material.active_texture, 'name'):
                              texture.texture.name = context.active_object.active_material.active_texture.name
                        else:
                          if hasattr(object.active_material, 'active_texture'):
                            if hasattr(object.active_material.active_texture, 'name'):
                              texture.texture.name = object.active_material.active_texture.name
            else:
              for material in object.material_slots:
                if material.material != None:
                  for texture in material.material.texture_slots:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.active_material, 'active_texture'):
                          if hasattr(context.active_object.active_material.active_texture, 'name'):
                            texture.texture.name = context.active_object.active_material.active_texture.name
                      else:
                        if hasattr(object.active_material, 'active_texture'):
                          if hasattr(object.active_material.active_texture, 'name'):
                            texture.texture.name = object.active_material.active_texture.name

          # particle systems
          if option.particleSystems:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        system.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        system.name = object.active_material.active_texture.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      system.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      system.name = object.active_material.active_texture.name

          # particle settings
          if option.particleSettings:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'active_texture'):
                      if hasattr(context.active_object.active_material.active_texture, 'name'):
                        system.settings.name = context.active_object.active_material.active_texture.name
                  else:
                    if hasattr(object.active_material, 'active_texture'):
                      if hasattr(object.active_material.active_texture, 'name'):
                        system.settings.name = object.active_material.active_texture.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      system.settings.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      system.settings.name = object.active_material.active_texture.name

      # source particle system
      if option.source in 'PARTICLE_SYSTEM':

          # objects
          if option.objects:

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    object.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    object.name = object.particle_systems.active.name
            else:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'name'):
                  object.name = context.active_object.particle_systems.active.name
              else:
                if hasattr(object.particle_systems.active, 'name'):
                  object.name = object.particle_systems.active.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # mode
              if option.mode in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      object.data.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      object.data.name = object.particle_systems.active.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    object.data.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    object.data.name = object.particle_systems.active.name

          # materials
          if option.materials:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'name'):
                        material.material.name = context.active_object.particle_systems.active.name
                    else:
                      if hasattr(object.particle_systems.active, 'name'):
                        material.material.name = object.particle_systems.active.name
            else:
              for material in object.material_slots:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      material.material.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      material.material.name = object.particle_systems.active.name

          # textures
          if option.textures:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:
                    for texture in material.material.texture_slots:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.particle_systems.active, 'name'):
                            texture.texture.name = context.active_object.particle_systems.active.name
                        else:
                          if hasattr(object.particle_systems.active, 'name'):
                            texture.texture.name = object.particle_systems.active.name
            else:
              for material in object.material_slots:
                if material.material != None:
                  for texture in material.material.texture_slots:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.particle_systems.active, 'name'):
                          texture.texture.name = context.active_object.particle_systems.active.name
                      else:
                        if hasattr(object.particle_systems.active, 'name'):
                          texture.texture.name = object.particle_systems.active.name

          # particle system
          if option.particleSystems:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      system.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      system.name = object.particle_systems.active.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    system.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    system.name = object.particle_systems.active.name

          # particle settings
          if option.particleSettings:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'name'):
                      system.settings.name = context.active_object.particle_systems.active.name
                  else:
                    if hasattr(object.particle_systems.active, 'name'):
                      system.settings.name = object.particle_systems.active.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    system.settings.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    system.settings.name = object.particle_systems.active.name

      # source particle settings
      if option.source in 'PARTICLE_SETTINGS':

          # objects
          if option.objects:

            # mode
            if option.mode in 'SELECTED':
              if object.select:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    object.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    object.name = object.particle_systems.active.settings.name
            else:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'settings'):
                  object.name = context.active_object.particle_systems.active.settings.name
              else:
                if hasattr(object.particle_systems.active, 'settings'):
                  object.name = object.particle_systems.active.settings.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # mode
              if option.mode in 'SELECTED':
                if object.select:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      object.data.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      object.data.name = object.particle_systems.active.settings.name
              else:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    object.data.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    object.data.name = object.particle_systems.active.settings.name

          # materials
          if option.materials:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'settings'):
                        material.material.name = context.active_object.particle_systems.active.settings.name
                    else:
                      if hasattr(object.particle_systems.active, 'settings'):
                        material.material.name = object.particle_systems.active.settings.name
            else:
              for material in object.material_slots:
                if material.material != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      material.material.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      material.material.name = object.particle_systems.active.settings.name

          # textures
          if option.textures:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for material in object.material_slots:
                  if material.material != None:
                    for texture in material.material.texture_slots:
                      if texture != None:

                        # use active object
                        if option.useActiveObject:
                          if hasattr(context.active_object.particle_systems.active, 'settings'):
                            texture.texture.name = context.active_object.particle_systems.active.settings.name
                        else:
                          if hasattr(object.particle_systems.active, 'settings'):
                            texture.texture.name = object.particle_systems.active.settings.name
            else:
              for material in object.material_slots:
                if material.material != None:
                  for texture in material.material.texture_slots:
                    if texture != None:

                      # use active object
                      if option.useActiveObject:
                        if hasattr(context.active_object.particle_systems.active, 'settings'):
                          texture.texture.name = context.active_object.particle_systems.active.settings.name
                      else:
                        if hasattr(object.particle_systems.active, 'settings'):
                          texture.texture.name = object.particle_systems.active.settings.name

          # particle systems
          if option.particleSystems:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      system.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      system.name = object.particle_systems.active.settings.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    system.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    system.name = object.particle_systems.active.settings.name

          # particle settings
          if option.particleSettings:

            # mode
            if option.mode in 'SELECTED':
              if object.select:
                for system in object.particle_systems:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.particle_systems.active, 'settings'):
                      system.settings.name = context.active_object.particle_systems.active.settings.name
                  else:
                    if hasattr(object.particle_systems.active, 'settings'):
                      system.settings.name = object.particle_systems.active.settings.name
            else:
              for system in object.particle_systems:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    system.settings.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    system.settings.name = object.particle_systems.active.settings.name
  # mode
  else:
    for object in context.scene.objects:

      # source object
      if option.source in 'OBJECT':

        # objects
        if option.objects:

          # use active object
          if option.useActiveObject:
            object.name = context.active_object.name
          else:
            object.name = object.name

        # object data
        if option.objectData:
          if object.type not in 'EMPTY':

            # use active object
            if option.useActiveObject:
              object.data.name = context.active_object.name
            else:
              object.data.name = object.name

        # materials
        if option.materials:
          for material in object.material_slots:
            if material.material != None:

              # use active object
              if option.useActiveObject:
                material.material.name = context.active_object.name
              else:
                material.material.name = object.name

        # textures
        if option.textures:
          for material in object.material_slots:
            if material.material != None:
              for texture in material.material.texture_slots:
                if texture != None:

                  # use active object
                  if option.useActiveObject:
                    texture.texture.name = context.active_object.name
                  else:
                    texture.texture.name = object.name

        # particle systems
        if option.particleSystems:
          for system in object.particle_systems:

            # use active object
            if option.useActiveObject:
              system.name = context.active_object.name
            else:
              system.name = object.name

        # particle settings
        if option.particleSettings:
          for system in object.particle_systems:

            # use active object
            if option.useActiveObject:
              system.settings.name = context.active_object.name
            else:
              system.settings.name = object.name

      # source data
      if option.source in 'DATA':
        if object.type not in 'EMPTY':

          # objects
          if option.objects:

            # use active object
            if option.useActiveObject:
              object.name = context.active_object.data.name
            else:
              object.name = object.data.name

          # object data
          if option.objectData:

            # use active object
            if option.useActiveObject:
              object.data.name = context.active_object.data.name
            else:
              object.data.name = object.data.name

          # materials
          if option.materials:
            for material in object.material_slots:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  material.material.name = context.active_object.data.name
                else:
                  material.material.name = object.data.name

          # textures
          if option.textures:
            for material in object.material_slots:
              if material.material != None:
                for texture in material.material.texture_slots:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      texture.texture.name = context.active_object.data.name
                    else:
                      texture.texture.name = object.data.name

          # particle systems
          if option.particleSystems:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                system.name = context.active_object.data.name
              else:
                system.name = object.data.name

          # particle settings
          if option.particleSettings:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                system.settings.name = context.active_object.data.name
              else:
                system.settings.name = object.data.name

      # source material
      if option.source in 'MATERIAL':

        # objects
        if option.objects:

          # use active object
          if option.useActiveObject:
            if hasattr(context.active_object.active_material, 'name'):
              object.name = context.active_object.active_material.name
          else:
            if hasattr(object.active_material, 'name'):
              object.name = object.active_material.name

        # object data
        if option.objectData:
          if object.type not in 'EMPTY':

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.active_material, 'name'):
                object.data.name = context.active_object.active_material.name
            else:
              if hasattr(object.active_material, 'name'):
                object.data.name = object.active_material.name

        # materials
        if option.materials:
          for material in object.material_slots:
            if material.material != None:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'name'):
                  material.material.name = context.active_object.active_material.name
              else:
                if hasattr(object.active_material, 'name'):
                  material.material.name = object.active_material.name

        # textures
        if option.textures:
          for material in object.material_slots:
            if material.material != None:
              for texture in material.material.texture_slots:
                if texture != None:

                  # use active object
                  if option.useActiveObject:
                    if hasattr(context.active_object.active_material, 'name'):
                      texture.texture.name = context.active_object.active_material.name
                  else:
                    if hasattr(object.active_material, 'name'):
                      texture.texture.name = object.active_material.name

        # particle systems
        if option.particleSystems:
          for system in object.particle_systems:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.active_material, 'name'):
                system.name = context.active_object.active_material.name
            else:
              if hasattr(object.active_material, 'name'):
                system.name = object.active_material.name

        # particle settings
        if option.particleSettings:
          for system in object.particle_systems:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.active_material, 'name'):
                system.settings.name = context.active_object.active_material.name
            else:
              if hasattr(object.active_material, 'name'):
                system.settings.name = object.active_material.name

      # source texture
      if option.source in 'TEXTURE':
        if context.scene.render.engine not in 'CYCLES':

          # objects
          if option.objects:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.active_material, 'active_texture'):
                if hasattr(context.active_object.active_material.active_texture, 'name'):
                  object.name = context.active_object.active_material.active_texture.name
            else:
              if hasattr(object.active_material, 'active_texture'):
                if hasattr(object.active_material.active_texture, 'name'):
                  object.name = object.active_material.active_texture.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'active_texture'):
                  if hasattr(context.active_object.active_material.active_texture, 'name'):
                    object.data.name = context.active_object.active_material.active_texture.name
              else:
                if hasattr(object.active_material, 'active_texture'):
                  if hasattr(object.active_material.active_texture, 'name'):
                    object.data.name = object.active_material.active_texture.name

          # materials
          if option.materials:
            for material in object.material_slots:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.active_material, 'active_texture'):
                    if hasattr(context.active_object.active_material.active_texture, 'name'):
                      material.material.name = context.active_object.active_material.active_texture.name
                else:
                  if hasattr(object.active_material, 'active_texture'):
                    if hasattr(object.active_material.active_texture, 'name'):
                      material.material.name = object.active_material.active_texture.name

          # textures
          if option.textures:
            for material in object.material_slots:
              if material.material != None:
                for texture in material.material.texture_slots:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.active_material, 'active_texture'):
                        if hasattr(context.active_object.active_material.active_texture, 'name'):
                          texture.texture.name = context.active_object.active_material.active_texture.name
                    else:
                      if hasattr(object.active_material, 'active_texture'):
                        if hasattr(object.active_material.active_texture, 'name'):
                          texture.texture.name = object.active_material.active_texture.name

          # particle systems
          if option.particleSystems:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'active_texture'):
                  if hasattr(context.active_object.active_material.active_texture, 'name'):
                    system.name = context.active_object.active_material.active_texture.name
              else:
                if hasattr(object.active_material, 'active_texture'):
                  if hasattr(object.active_material.active_texture, 'name'):
                    system.name = object.active_material.active_texture.name

          # particle settings
          if option.particleSettings:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.active_material, 'active_texture'):
                  if hasattr(context.active_object.active_material.active_texture, 'name'):
                    system.settings.name = context.active_object.active_material.active_texture.name
              else:
                if hasattr(object.active_material, 'active_texture'):
                  if hasattr(object.active_material.active_texture, 'name'):
                    system.settings.name = object.active_material.active_texture.name

      # source particle system
      if option.source in 'PARTICLE_SYSTEM':

          # objects
          if option.objects:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.particle_systems.active, 'name'):
                object.name = context.active_object.particle_systems.active.name
            else:
              if hasattr(object.particle_systems.active, 'name'):
                object.name = object.particle_systems.active.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'name'):
                  object.data.name = context.active_object.particle_systems.active.name
              else:
                if hasattr(object.particle_systems.active, 'name'):
                  object.data.name = object.particle_systems.active.name

          # materials
          if option.materials:
            for material in object.material_slots:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'name'):
                    material.material.name = context.active_object.particle_systems.active.name
                else:
                  if hasattr(object.particle_systems.active, 'name'):
                    material.material.name = object.particle_systems.active.name

          # textures
          if option.textures:
            for material in object.material_slots:
              if material.material != None:
                for texture in material.material.texture_slots:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'name'):
                        texture.texture.name = context.active_object.particle_systems.active.name
                    else:
                      if hasattr(object.particle_systems.active, 'name'):
                        texture.texture.name = object.particle_systems.active.name

          # particle system
          if option.particleSystems:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'name'):
                  system.name = context.active_object.particle_systems.active.name
              else:
                if hasattr(object.particle_systems.active, 'name'):
                  system.name = object.particle_systems.active.name

          # particle settings
          if option.particleSettings:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'name'):
                  system.settings.name = context.active_object.particle_systems.active.name
              else:
                if hasattr(object.particle_systems.active, 'name'):
                  system.settings.name = object.particle_systems.active.name

      # source particle settings
      if option.source in 'PARTICLE_SETTINGS':

          # objects
          if option.objects:

            # use active object
            if option.useActiveObject:
              if hasattr(context.active_object.particle_systems.active, 'settings'):
                object.name = context.active_object.particle_systems.active.settings.name
            else:
              if hasattr(object.particle_systems.active, 'settings'):
                object.name = object.particle_systems.active.settings.name

          # object data
          if option.objectData:
            if object.type not in 'EMPTY':

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'settings'):
                  object.data.name = context.active_object.particle_systems.active.settings.name
              else:
                if hasattr(object.particle_systems.active, 'settings'):
                  object.data.name = object.particle_systems.active.settings.name

          # materials
          if option.materials:
            for material in object.material_slots:
              if material.material != None:

                # use active object
                if option.useActiveObject:
                  if hasattr(context.active_object.particle_systems.active, 'settings'):
                    material.material.name = context.active_object.particle_systems.active.settings.name
                else:
                  if hasattr(object.particle_systems.active, 'settings'):
                    material.material.name = object.particle_systems.active.settings.name

          # textures
          if option.textures:
            for material in object.material_slots:
              if material.material != None:
                for texture in material.material.texture_slots:
                  if texture != None:

                    # use active object
                    if option.useActiveObject:
                      if hasattr(context.active_object.particle_systems.active, 'settings'):
                        texture.texture.name = context.active_object.particle_systems.active.settings.name
                    else:
                      if hasattr(object.particle_systems.active, 'settings'):
                        texture.texture.name = object.particle_systems.active.settings.name

          # particle systems
          if option.particleSystems:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'settings'):
                  system.name = context.active_object.particle_systems.active.settings.name
              else:
                if hasattr(object.particle_systems.active, 'settings'):
                  system.name = object.particle_systems.active.settings.name

          # particle settings
          if option.particleSettings:
            for system in object.particle_systems:

              # use active object
              if option.useActiveObject:
                if hasattr(context.active_object.particle_systems.active, 'settings'):
                  system.settings.name = context.active_object.particle_systems.active.settings.name
              else:
                if hasattr(object.particle_systems.active, 'settings'):
                  system.settings.name = object.particle_systems.active.settings.name
