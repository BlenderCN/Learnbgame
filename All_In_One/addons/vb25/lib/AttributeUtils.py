#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

import bpy

from bl_ui.properties_material import active_node_mat


def callback_match_BI_diffuse(self, context):
	if not hasattr(context, 'material'):
		return
	
	material = active_node_mat(context.material)
	
	if not context.material:
		return
	
	if not self.as_viewport_color:
		material.diffuse_color = (0.5, 0.5, 0.5)
		return

	color = self.diffuse if material.vray.type == 'BRDFVRayMtl' else self.color

	material.diffuse_color = color
