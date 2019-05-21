#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;
uniform sampler2D lastFrame;

void main() {
	
	float strength = 0.5;                       // Change this mix value to change how strongly the blur appears

    vec4 color = texture2D(u_texture, v_texCoords);
    vec4 lastColor = texture2D(lastFrame, v_texCoords);
    vec4 final = mix(color, lastColor, strength);	
    final.a = max(color.a, lastColor.a);        // We do this because lastFrame's initial alpha value is 0, and moving objects in front of
    gl_FragColor = final;                       // blank space won't have a trail if we just go with the current frame's alpha value.

}
