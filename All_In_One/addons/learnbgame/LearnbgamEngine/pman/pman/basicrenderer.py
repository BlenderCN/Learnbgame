import panda3d.core as p3d
from direct.filter.FilterManager import FilterManager

_SRGB_VERT = """
#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;

varying vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}
"""


_SRGB_FRAG = """
#version 120

uniform sampler2D tex;

varying vec2 texcoord;


void main() {
    vec3 color = pow(texture2D(tex, texcoord).rgb, vec3(1.0/2.2));
    gl_FragColor = vec4(color, 1.0);
}
"""


class BasicRenderer(object):
    def __init__(self, base):
        self.base = base
        self.base.render.set_shader_auto()

        p3d.Texture.setTexturesPower2(p3d.ATS_none)

        manager = FilterManager(base.win, base.cam)
        self.post_tex = p3d.Texture()
        post_quad = manager.renderSceneInto(colortex=self.post_tex)
        post_quad.set_shader(p3d.Shader.make(p3d.Shader.SL_GLSL, _SRGB_VERT, _SRGB_FRAG))
        post_quad.set_shader_input('tex', self.post_tex)
