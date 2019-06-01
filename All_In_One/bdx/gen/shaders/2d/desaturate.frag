#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;

void main() {
	
	float strength = 1.0;                       // How strong the desaturation effect is.

	vec4 color = texture2D(u_texture, v_texCoords);
	float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
	vec4 desat = vec4(gray, gray, gray, color.a);
    gl_FragColor = mix(color, desat, strength);  

}
