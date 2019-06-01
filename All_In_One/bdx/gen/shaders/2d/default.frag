#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec4 v_color;
varying vec2 v_texCoords;
uniform sampler2D u_texture;
uniform mat4 u_projTrans;

void main() {

    vec4 color = texture2D(u_texture, v_texCoords);
    gl_FragColor = color;

}
