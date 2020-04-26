'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''

__all__ = [ 'ui' ]


def register():
    from vb25.ui import ui
    from vb25.ui import properties_data_geometry
    from vb25.ui import properties_data_camera
    from vb25.ui import properties_data_lamp
    from vb25.ui import properties_data_empty
    from vb25.ui import properties_material
    from vb25.ui import properties_object
    from vb25.ui import properties_particles
    from vb25.ui import properties_render
    from vb25.ui import properties_scene
    from vb25.ui import properties_texture
    from vb25.ui import properties_world

    ui.register()
    properties_data_geometry.register()
    properties_data_camera.register()
    properties_data_lamp.register()
    properties_data_empty.register()
    properties_material.register()
    properties_object.register()
    properties_particles.register()
    properties_render.register()
    properties_scene.register()
    properties_texture.register()
    properties_world.register()


def unregister():
    from vb25.ui import ui
    from vb25.ui import properties_data_geometry
    from vb25.ui import properties_data_camera
    from vb25.ui import properties_data_lamp
    from vb25.ui import properties_data_empty
    from vb25.ui import properties_material
    from vb25.ui import properties_object
    from vb25.ui import properties_particles
    from vb25.ui import properties_render
    from vb25.ui import properties_scene
    from vb25.ui import properties_texture
    from vb25.ui import properties_world

    ui.unregister()
    properties_data_geometry.unregister()
    properties_data_camera.unregister()
    properties_data_lamp.unregister()
    properties_data_empty.unregister()
    properties_material.unregister()
    properties_object.unregister()
    properties_particles.unregister()
    properties_render.unregister()
    properties_scene.unregister()
    properties_texture.unregister()
    properties_world.unregister()
