#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texCoords;
uniform sampler2D u_texture;

void main() {

	int sampleNumX = 5;                 // Number of samples on X and Y axes
	int sampleNumY = 5;                 // (To be exact, it's (X*2)*(Y*2) number of samples); higher values = smoother blurs
	float width = 0.001;                // Percent of the screen to sample in width and height; higher values = larger blurs
	float height = 0.001;				
	float strength = 1.0;               // What percent the blur is applied over the screen; lower value = weaker blur

	vec4 color = texture2D(u_texture, v_texCoords);
	vec4 blur = vec4(0);  
	vec2 coords;
	
	for (int i = -sampleNumX; i < sampleNumX; i++) {
		
		for (int j = -sampleNumY; j < sampleNumY; j++) {
			
			coords.x = v_texCoords.x + (i * width);
			coords.y = v_texCoords.y + (j * height);
						
			blur += texture2D(u_texture, coords);
			
		}
		
	}
	
	blur /= (sampleNumX * 2) * (sampleNumY * 2);
	
    gl_FragColor = mix(color, blur, strength);

}
