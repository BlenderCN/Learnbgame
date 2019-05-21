#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;

void main() {
	
	float strength = 0.5;               // How strong the tinting effect is
	vec3 tint = vec3(1.0, 0.0, 0.0);    // The targeted tinting color
	
	vec4 color = texture2D(u_texture, v_texCoords);
	color.rgb = vec4(color.rgb + (tint * strength), color.a);
	gl_FragColor = color;

}
