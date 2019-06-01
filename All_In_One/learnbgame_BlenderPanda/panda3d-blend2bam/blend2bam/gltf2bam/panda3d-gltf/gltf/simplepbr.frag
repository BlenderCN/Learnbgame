// Based on code from https://github.com/KhronosGroup/glTF-Sample-Viewer

#version 130

#ifndef MAX_LIGHTS
    #define MAX_LIGHTS 8
#endif

uniform struct {
    vec4 baseColor;
    float roughness;
    float metallic;
    float refractiveIndex;
} p3d_Material;

uniform struct {
    vec4 position;
    vec4 diffuse;
    vec4 specular;
    vec3 attenuation;
    vec3 spotDirection;
    float spotCosCutoff;
    float spotExponent;
    //sampler2DShadow shadowMap;
    //mat4 shadowMatrix;
} p3d_LightSource[MAX_LIGHTS];

struct FunctionParamters {
    float n_dot_l;
    float n_dot_v;
    float n_dot_h;
    float l_dot_h;
    float v_dot_h;
    float roughness;
    float metallic;
    vec3 reflection0;
    vec3 reflection90;
    vec3 diffuse_color;
    vec3 specular_color;
};

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;

const vec3 F0 = vec3(0.04);
const float MIN_ROUGHNESS = 0.04;
const float PI = 3.141592653589793;

in vec3 v_position;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 color;

// Give texture slots names
#define p3d_TextureBaseColor p3d_Texture0
#define p3d_TextureMetalRoughness p3d_Texture1

vec3 specular_reflection(FunctionParamters func_params) {
    return func_params.reflection0 + (func_params.reflection90 - func_params.reflection0) * pow(clamp(1.0 - func_params.v_dot_h, 0.0, 1.0), 5.0);
}

float geometric_occlusion(FunctionParamters func_params) {
{
    float n_dot_l = func_params.n_dot_l;
    float n_dot_v = func_params.n_dot_v;
    float r = func_params.roughness;

    float attenuationL = 2.0 * n_dot_l / (n_dot_l + sqrt(r * r + (1.0 - r * r) * (n_dot_l * n_dot_l)));
    float attenuationV = 2.0 * n_dot_v / (n_dot_v + sqrt(r * r + (1.0 - r * r) * (n_dot_v * n_dot_v)));
    return attenuationL * attenuationV;
}
}

float microfacet_distribution(FunctionParamters func_params) {
    float roughness2 = func_params.roughness * func_params.roughness;
    float f = (func_params.n_dot_h * roughness2 - func_params.n_dot_h) * func_params.n_dot_h + 1.0;
    return roughness2 / (PI * f * f);
}

vec3 diffuse_function(FunctionParamters func_params) {
    return func_params.diffuse_color / PI;
}

void main() {
    vec4 metal_rough = texture(p3d_TextureMetalRoughness, v_texcoord);
    float metallic = clamp(p3d_Material.metallic * metal_rough.g, 0.0, 1.0);
    float roughness = clamp(p3d_Material.roughness * metal_rough.b,  MIN_ROUGHNESS, 1.0);
    vec4 base_color = p3d_Material.baseColor * texture(p3d_TextureBaseColor, v_texcoord);
    vec3 diffuse_color = (base_color.rgb * (vec3(1.0) - F0)) * (1.0 - metallic);
    vec3 spec_color = mix(F0, base_color.rgb, metallic);
    vec3 reflection90 = vec3(clamp(max(max(spec_color.r, spec_color.g), spec_color.b) * 25.0, 0.0, 1.0));
    vec3 n = v_normal;
    vec3 v = normalize(-v_position);

    color = vec4(0.0);

    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        vec3 l = normalize(p3d_LightSource[i].position.xyz - v_position * p3d_LightSource[i].position.w);
        vec3 h = normalize(l + v);
        vec3 r = -normalize(reflect(l, n));

        FunctionParamters func_params;
        func_params.n_dot_l = clamp(dot(n, l), 0.001, 1.0);
        func_params.n_dot_v = clamp(abs(dot(n, v)), 0.001, 1.0);
        func_params.n_dot_h = clamp(dot(n, h), 0.0, 1.0);
        func_params.l_dot_h = clamp(dot(l, h), 0.0, 1.0);
        func_params.v_dot_h = clamp(dot(v, h), 0.0, 1.0);
        func_params.roughness = roughness;
        func_params.metallic =  metallic;
        func_params.reflection0 = spec_color;
        func_params.reflection90 = reflection90;
        func_params.diffuse_color = diffuse_color;
        func_params.specular_color = spec_color;

        vec3 F = specular_reflection(func_params);
        float G = geometric_occlusion(func_params);
        float D = microfacet_distribution(func_params);

        vec3 diffuse_contrib = (1.0 - F) * diffuse_function(func_params);
        vec3 spec_contrib = vec3(F * G * D / (4.0 * func_params.n_dot_l * func_params.n_dot_v));
        color.rgb += func_params.n_dot_l * p3d_LightSource[i].diffuse.rgb * (diffuse_contrib + spec_contrib);
    }
}
