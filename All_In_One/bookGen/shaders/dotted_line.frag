uniform float u_Scale;

in float v_ArcLength;

void main()
{
    if (step(sin(v_ArcLength * u_Scale), 0.5) == 1) discard;
    gl_FragColor = vec4(1.0);
}