#version 430

uniform mat4 trans;
uniform mat4 proj;
uniform mat4 view;

in vec3 position;
in vec3 normal;
in vec3 tangent;
in vec2 texcoord;

out vec2 Texcoord;
out vec4 position_ws;
out mat3 TBN;
out vec4 lightpos_ws;
out vec4 camerapos_ws;

void main() {
	lightpos_ws = vec4(0, 0, 0, 1.0);
	camerapos_ws = vec4(0, 0, -5.0, 1.0);	/* FIXME: make a uniform */
	
	position_ws = vec4(position, abs(distance(vec3(camerapos_ws), position)));

	TBN = mat3(tangent, cross(normal, tangent), normal);
	
	Texcoord = texcoord;
	
	gl_Position = proj * view * trans * position_ws;
}
