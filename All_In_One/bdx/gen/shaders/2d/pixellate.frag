#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;
uniform float screenWidth;
uniform float screenHeight;

void main() {
	
	int targetResolutionX = 160;			// Target resolution for pixellation
	int targetResolutionY = 80;
	
	vec2 uv = v_texCoords;	
	vec2 pixel = vec2(1 / screenWidth, 1 / screenHeight);
	
	float dx = pixel.x * (int(ceil(screenWidth / targetResolutionX)));
	float dy = pixel.y * (int(ceil(screenHeight / targetResolutionY)));
	
	vec2 coord = vec2(dx * floor(uv.x / dx), dy * floor(uv.y / dy));
	
	coord += pixel * 0.5;
	
	coord.x = min(max(0.001, coord.x), 1.0);
	coord.y = min(max(0.001, coord.y), 1.0);
	
	gl_FragColor = vec4(texture2D(u_texture, coord));

}
