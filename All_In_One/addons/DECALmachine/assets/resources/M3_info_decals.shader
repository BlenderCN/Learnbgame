Shader "MACHIN3/Decals/Info" 
{
	Properties 
	{
		_ColorMap ("Color map", 2D) = "white" {}

		_BlendSurfaceNormals ("Blend Surface Normals", Range(0,1)) = 0

        _ColorInvert ("Color Invert", Range(0, 1)) = 0
        _Opacity ("Opacity", Range(0, 1)) = 1

		_Metalness ("Metalness", Range(0,1)) = 0.0
		_Smoothness ("Smoothness", Range(0,1)) = 0.75

        _Offset ("Offset", Range(-20, -1)) = -1
	}
	SubShader 
	{
        // TODO: invert mask

        Tags {"Queue"="AlphaTest" "IgnoreProjector"="True" "RenderType"="Opaque" "ForceNoShadowCasting"="True"}
		LOD 300
		Offset [_Offset], [_Offset]

        Blend SrcAlpha OneMinusSrcAlpha, Zero OneMinusSrcAlpha

		CGPROGRAM

        #pragma surface surf Standard finalgbuffer:DecalFinalGBuffer exclude_path:forward exclude_path:prepass noshadow noforwardadd keepalpha
		#pragma target 3.0

		sampler2D _ColorMap;

        fixed _ColorInvert;
		half _Metalness;
		half _Opacity;
		half _BlendSurfaceNormals;

		struct Input 
		{
			float2 uv_ColorMap;
		};

		void surf (Input IN, inout SurfaceOutputStandard o) 
		{
			fixed4 c = tex2D (_ColorMap, IN.uv_ColorMap) * _Opacity;

            o.Alpha = c.a;
            o.Albedo = abs( _ColorInvert - c.rgb );
            o.Metallic = _Metalness;
		}

        void DecalFinalGBuffer (Input IN, SurfaceOutputStandard o, inout half4 diffuse, inout half4 specSmoothness, inout half4 normal, inout half4 emission)
        {
            diffuse.a = o.Alpha;
            specSmoothness.a = o.Alpha;
            normal.a = lerp(o.Alpha, 0, _BlendSurfaceNormals);
            emission.a = o.Alpha;
        }

        ENDCG

        // for some reason the blending above kills the specular
        // this second shader adds it

        Blend One One
        ColorMask A

        CGPROGRAM

        #pragma surface surf Standard finalgbuffer:DecalFinalGBuffer exclude_path:forward exclude_path:prepass noshadow noforwardadd keepalpha
        #pragma target 3.0

        sampler2D _ColorMap;

        half _Smoothness;
        half _Opacity;

        struct Input 
        {
            float2 uv_ColorMap; 
        };

        void surf (Input IN, inout SurfaceOutputStandard o) 
        {
            fixed4 c = tex2D (_ColorMap, IN.uv_ColorMap) * _Opacity;

            o.Alpha = c.a;
            o.Smoothness = c.a * _Smoothness;
        }

        void DecalFinalGBuffer (Input IN, SurfaceOutputStandard o, inout half4 diffuse, inout half4 specSmoothness, inout half4 normal, inout half4 emission)
        {
            specSmoothness.a = o.Alpha * _Smoothness;  // no idea, why the multiplication is necessary, but it works
        }

        ENDCG
	} 
	FallBack "Diffuse"
}




