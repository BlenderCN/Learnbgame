'''
Copyright (C) 2018 Jean Da Costa machado.
Jean3dimensional@gmail.com

Created by Jean Da Costa machado

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import bgl
import gpu
from gpu_extras.batch import batch_for_shader


class DrawObject:
    def __init__(self):
        self.x_ray = False
        self.coords = []
        self.colors = []
        self.shader = gpu.shader.from_builtin("3D_SMOOTH_COLOR")

    def __call__(self, *args, **kwargs):
        self.draw()

    def add_line(self, start, end, color=(1, 0, 0, 1)):
        self.coords.append(tuple(start))
        self.coords.append(tuple(end))
        self.colors.append(color)
        self.colors.append(color)

    def start_drawing(self):
        bgl.glLineWidth(2)
        if self.x_ray:
            bgl.glDisable(bgl.GL_DEPTH_TEST)

    def stop_drawing(self):
        bgl.glLineWidth(1)
        if self.x_ray:
            bgl.glEnable(bgl.GL_DEPTH_TEST)

    def reset(self):
        self.coords.clear()
        self.colors.clear()

    def draw(self):
        self.start_drawing()
        print(len(self.coords), len(self.colors))
        batch = batch_for_shader(self.shader, 'LINES', {"pos": self.coords, "color": self.colors})
        self.shader.bind()
        batch.draw(self.shader)
        self.stop_drawing()
