#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;


out vec3 v_position;
out vec3 v_normal;
out vec2 v_texcoord;

void main() {
    v_position = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    v_normal = normalize(p3d_NormalMatrix * p3d_Normal);
    v_texcoord = p3d_MultiTexCoord0;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
