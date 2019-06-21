# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import bpy
from extensions_framework import log
from extensions_framework.util import TimerThread

def MtsLog(*args, popup=False):
	'''
	Send string to AF log, marked as belonging to Mitsuba module.
	Accepts variable args 
	'''
	if len(args) > 0:
		log(' '.join(['%s'%a for a in args]), module_name='Mitsuba', popup=popup)

class MtsFilmDisplay(TimerThread):
	'''
	Periodically update render result with Mituba's framebuffer
	'''
	
	STARTUP_DELAY = 1
	
	def begin(self, renderer, output_file, resolution, preview = False):
		(self.xres, self.yres) = (int(resolution[0]), int(resolution[1]))
		self.renderer = renderer
		self.output_file = output_file
		self.resolution = resolution
		self.preview = preview
		if not self.preview:
			self.result = self.renderer.begin_result(0, 0, self.xres, self.yres)
		self.start()
	
	def shutdown(self):
		if not self.preview:
			self.renderer.end_result(self.result, 0)
	
	def kick(self, render_end=False):
		if not bpy.app.background or render_end:
			if os.path.exists(self.output_file):
				if render_end:
					MtsLog('Final render result %ix%i' % self.resolution)
				else:
					MtsLog('Updating render result %ix%i' % self.resolution)
				try:
					if self.preview:
						self.result = self.renderer.begin_result(0, 0, self.xres, self.yres)
						self.result.layers[0].load_from_file(self.output_file)
						self.renderer.end_result(self.result, 0)
					else:
						self.result.layers[0].load_from_file(self.output_file)
						self.renderer.update_result(self.result)
				except:
					pass
			else:
				err_msg = 'ERROR: Could not load render result from %s' % self.output_file
				MtsLog(err_msg)
