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

bl_info = {
    "name" : "V-Ray For Blender 2.5",
    "author" : "",
    "blender" : (2, 67, 0),
    "location" : "Info header, render engine menu",
    "description" : "Exporter to the V-Ray Standalone file format",
    "warning" : "",
    "wiki_url" : "https://github.com/bdancer/vb25/wiki",
    "tracker_url" : "https://github.com/bdancer/vb25/issues",
    "support" : 'COMMUNITY',
    "category": "Learnbgame",
}


if "bpy" in locals():
	import imp
	imp.reload(lib)
	imp.reload(plugins)
	imp.reload(ui)
	imp.reload(preset)
	imp.reload(render_ops)
	imp.reload(events)
else:
	import bpy
	from vb25 import lib
	from vb25 import plugins
	from vb25 import ui
	from vb25 import preset
	from vb25 import render_ops
	from vb25 import events


def register():
	ui.register()
	events.register()
	plugins.add_properties()
	render_ops.register()


def unregister():
	render_ops.unregister()
	plugins.remove_properties()
	events.unregister()
	ui.unregister()
