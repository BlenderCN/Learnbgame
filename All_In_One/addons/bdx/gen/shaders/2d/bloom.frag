#pragma optionNV(strict on)

#ifdef GL_ES
    precision mediump float;
#endif

varying vec4 v_color;
varying vec2 v_texCoords;
uniform sampler2D u_texture;
uniform mat4 u_projTrans;

float luminance(vec4 color) {
	
	return (((color.r * 2) + color.b + (color.g * 3)) / 6);
	
}

void main() {

    int sampleNumX = 4;                 // Number of samples on X and Y axes
    int sampleNumY = 4;                 // (To be exact, it's (X*2)*(Y*2) number of samples)
    float width = 0.002;                // Percent of the screen to sample in width and height
    float height = 0.002;
    float threshold = 0.25;             // The luminosity threshold of the surrounding pixels to trigger the effect
    float strength = 1.0;               // The strength of the overall bloom effect
    vec4 tintColor = vec4(1, 1, 1, 1);  // The color to tint the bloom effect

    vec4 base = texture2D(u_texture, v_texCoords);
    vec4 bloom = vec4(0);  
    vec4 bloomCol = vec4(0);
    vec2 coords;
    
    for (int i = -sampleNumX; i < sampleNumX; i++) {
    	
    	for (int j = -sampleNumY; j < sampleNumY; j++) {
    		
    		coords.x = v_texCoords.x + (i * width);
    		coords.y = v_texCoords.y + (j * height);
    		    		
    		bloomCol = texture2D(u_texture, coords);
    		
    		if (luminance(bloomCol) > threshold)
    			bloom += bloomCol;
    		
    	}
    	
    }
    
    bloom /= (sampleNumX * 2) * (sampleNumY * 2);
        
    bloom *= tintColor;
    
    gl_FragColor = base + (bloom * strength);

}
