uniform mat4 u_ViewProjectionMatrix;

in vec3 pos;
in float arcLength;

out float v_ArcLength;

void main()
{
    v_ArcLength = arcLength;
    gl_Position = u_ViewProjectionMatrix * vec4(pos, 1.0f);
}