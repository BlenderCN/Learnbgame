inline fixed3 UnpackTextureNormal(fixed4 packednormal)
{
	packednormal = pow(packednormal, 0.454545F);
	return packednormal.xyz * 2 -1;
}
