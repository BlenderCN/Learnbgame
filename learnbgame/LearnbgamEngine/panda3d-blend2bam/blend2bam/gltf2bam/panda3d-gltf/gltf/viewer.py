import os
import sys

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
import panda3d.core as p3d

import gltf

p3d.load_prc_file_data(
    __file__,
    'window-size 1024 768\n'
    'gl-version 3 2\n'
)


class App(ShowBase):
    def __init__(self):
        if len(sys.argv) < 2:
            print("Missing input file")
            sys.exit(1)

        super().__init__()

        self.setup_shaders(self.render)

        gltf.patch_loader(self.loader)

        infile = p3d.Filename.from_os_specific(os.path.abspath(sys.argv[1]))
        p3d.get_model_path().prepend_directory(infile.get_dirname())

        self.model_root = self.loader.load_model(infile)

        self.accept('escape', sys.exit)
        self.accept('q', sys.exit)


        self.light = self.render.attach_new_node(p3d.PointLight('light'))
        self.light.set_pos(-5, 5, 5)
        self.render.set_light(self.light)

        self.cam.set_pos(-10, 10, 10)

        if self.model_root.find('**/+Character'):
            self.actor = Actor(self.model_root)
            self.actor.reparent_to(self.render)
            anims = self.actor.get_anim_names()
            if anims:
                self.actor.loop(anims[0])
            self.cam.look_at(self.actor)
        else:
            self.model_root.reparent_to(self.render)
            self.cam.look_at(self.model_root)

    def setup_shaders(self, render_node):
        shader_dir = os.path.dirname(__file__)

        # Do not force power-of-two textures
        p3d.Texture.set_textures_power_2(p3d.ATS_none)

        # PBR shader
        pbrshader = p3d.Shader.load(
            p3d.Shader.SL_GLSL,
            vertex=os.path.join(shader_dir, 'simplepbr.vert'),
            fragment=os.path.join(shader_dir, 'simplepbr.frag')
        )
        render_node.set_shader(pbrshader)

        # Tonemapping
        manager = FilterManager(base.win, base.cam)
        tonemap_tex = p3d.Texture()
        tonemap_tex.set_component_type(p3d.Texture.T_float)
        tonemap_quad = manager.render_scene_into(colortex=tonemap_tex)
        tonemap_shader = p3d.Shader.load(
            p3d.Shader.SL_GLSL,
            vertex=os.path.join(shader_dir, 'post.vert'),
            fragment=os.path.join(shader_dir, 'tonemap.frag')
        )
        tonemap_quad.set_shader(tonemap_shader)
        tonemap_quad.set_shader_input('tex', tonemap_tex)


def main():
    App().run()

if __name__ == '__main__':
    main()
