#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;

void main() {
	
	float strength = 0.5;               // How strong the contrast effect is (higher values = more contrast)
	vec3 gray = vec3(0.5, 0.5, 0.5);    // The base color that the contrast works against
	
	vec4 color = texture2D(u_texture, v_texCoords);
	color.rgb = vec4(gray.rgb + ((color.rgb - gray.rgb) * strength), color.a);
	gl_FragColor = color;

}
