#version 430

uniform mat4 trans;
uniform mat4 proj;
uniform mat4 view;

uniform sampler2D tex;
uniform sampler2D normal_tex;
uniform sampler2D disp_tex;

in vec2 Texcoord;
in vec4 position_ws;
in mat3 TBN;
in vec4 lightpos_ws;
in vec4 camerapos_ws;

out vec4 out_color;

void main() {
	vec4 light_color = vec4(0.8, 0.8, 0.8, 1.0);
	
	vec4 mat_color = texture(tex, Texcoord);

	vec3 normal_map = texture(normal_tex, Texcoord).rgb;
	vec3 normal_adj = normalize(normal_map * 2.0 - 1.0);
	vec3 normal_ws = mat3(trans) * TBN * normal_adj;

	vec4 disp_map = vec4(texture(disp_tex, Texcoord).rgb, 1.0) * 2.0 - 1.0;

	vec4 position_adj = trans * (position_ws);
	
	vec4 lightdir_ws = normalize(lightpos_ws - position_adj);
	float light_dist = distance(lightpos_ws, position_adj);
	vec4 eyedir_ws = normalize(camerapos_ws - position_adj);
	
	float diff = clamp(dot(lightdir_ws.xyz, normal_ws), 0.0, 1.0);
	
	vec3 halfway_dir = normalize(lightdir_ws + eyedir_ws).xyz;
	float spec = pow(max(dot(normal_ws, halfway_dir), 0.0), 16.0);

	out_color =
		spec * mat_color +
		diff * mat_color;
}
