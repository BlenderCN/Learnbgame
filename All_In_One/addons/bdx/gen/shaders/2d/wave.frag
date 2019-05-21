#pragma optionNV(strict on)

#define PI 3.1415926535897932384626433832795

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;
uniform float time;

void main() {
	
	float waveStrengthX = 0.05;           // How strong the waves are onscreen (what percentage * 2 of the screen they traverse in both directions)
	float waveStrengthY = 0.025;
	int numOfCyclesX = 12;                // Number of cycles onscreen
	int numOfCyclesY = 7;
	float cyclesPerSecondX = 1.7;         // Cycles per second
	float cyclesPerSecondY = 1;         
	
	vec2 texCoords = vec2(v_texCoords);
	
	texCoords.x += (sin((texCoords.y * numOfCyclesX) + (time * PI * cyclesPerSecondX)) * waveStrengthX);
	texCoords.y += (cos((texCoords.x * numOfCyclesY) + (time * PI * cyclesPerSecondY)) * waveStrengthY);
	
	gl_FragColor = texture2D(u_texture, texCoords);

}
