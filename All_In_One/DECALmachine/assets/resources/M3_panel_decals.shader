Shader "MACHIN3/Decals/Panels" 
{
	Properties 
	{
        _AoCurvHeightSubset ("Ambient Occlusion(R), Curvature(B), Height(B), Subset Mask(A)", 2D) = "white" {}
		_NormalAlpha ("Normal(RGB) Decal Mask(A)", 2D) = "bump" {}

		_BlendSurfaceNormals ("Blend Surface Normals", Range(0,1)) = 0

		_AOStrength ("AO Strength", Range (0.0, 4)) = 1

		_Offset ("Offset", Range (-20, -1)) = -2

	}
	SubShader 
	{

        Tags {"Queue"="AlphaTest+1" "IgnoreProjector"="True" "RenderType"="Opaque" "ForceNoShadowCasting"="True"}
		LOD 300
        Offset [_Offset], [_Offset]

        Blend SrcAlpha OneMinusSrcAlpha, Zero OneMinusSrcAlpha

		CGPROGRAM

        #pragma surface surf Standard finalgbuffer:DecalFinalGBuffer exclude_path:forward exclude_path:prepass noshadow noforwardadd keepalpha
		#pragma target 3.0

        #include "MACHIN3.cginc"

		sampler2D _NormalAlpha;
		sampler2D _AoCurvHeightSubset;
		half _BlendSurfaceNormals;

		struct Input 
		{	
            float2 uv_AoCurvHeightSubset;
		};

        half _AOStrength;

		void surf (Input IN, inout SurfaceOutputStandard o) 
		{
            fixed4 aocurvheightsubset = tex2D(_AoCurvHeightSubset, IN.uv_AoCurvHeightSubset);
            fixed3 normal = UnpackTextureNormal(tex2D(_NormalAlpha, IN.uv_AoCurvHeightSubset));

            o.Occlusion = pow(LinearToGammaSpace(aocurvheightsubset.r), _AOStrength);
            o.Alpha = 1 - o.Occlusion;
            o.Albedo = 0;
            o.Normal = lerp(normal, float3(normal.xy * 3, normal.z), _BlendSurfaceNormals);
		}

        void DecalFinalGBuffer (Input IN, SurfaceOutputStandard o, inout half4 diffuse, inout half4 specSmoothness, inout half4 normal, inout half4 emission)
        {

			fixed decalalpha = tex2D (_NormalAlpha, IN.uv_AoCurvHeightSubset).a;

            diffuse.a = o.Alpha;
            specSmoothness.a = o.Alpha;
            normal.a = lerp(decalalpha, decalalpha * 0.5, _BlendSurfaceNormals);
            emission.a = o.Alpha;
        }

        ENDCG
	} 
	FallBack "Diffuse"
}
