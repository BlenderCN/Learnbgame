
 include "ObjectMaterial.mat.sc"

 trace-depths {
         diff 1
         refl 4
         refr 4
         } 

 background {
         color {
                 "sRGB nonlinear" +0.0509  +0.0509  +0.0509
                 } 
         } 

 bucket 64 hilbert
 
 shader {
         name "Floor"
         type diffuse
         texture  "SceneFloorUVgrid.png"
         } 

 light  {
         type   directional
         source   +0.0000 -17.9080 +9.9444
         target   +0.0000 -17.0421 +9.4441
         radius   +17.3205
         emit   {
                 "sRGB nonlinear" +1.0000  +1.0000  +1.0000
                 } 
         intensity  +5.0000
         } 

 camera {
         type pinhole
         eye    -0.0000 -5.2825 +3.7068
         target -0.0000 -4.3976 +3.2411
         up     +0.0000 +0.4657 +0.8849
         fov    49.13434
         aspect 1.33333
         } 

object {
	   shader ObjectMaterial
	   transform {
		  %rotatex -90
		  scaleu 0.018
		  %rotatey 245
		  translate  0 0 0
	   }
	   type teapot
	   name teapot
	   subdivs 7
	   smooth true
}

 object {
         shader Floor
         modifier None
         type generic-mesh
         name Plane
         points 4
                  +20.0000  -20.0000  +0.0000
                  -20.0000  -20.0000  +0.0000
                  +20.0000  +20.0000  +0.0000
                  -20.0000  +20.0000  +0.0000
         triangles 2
                  000001  000000  000003
                  000000  000002  000003
         normals facevarying
                  +0.0000 +0.0000 +1.0000 +0.0000 +0.0000 +1.0000 +0.0000 +0.0000 +1.0000
                  -0.0000 +0.0000 +1.0000 -0.0000 +0.0000 +1.0000 -0.0000 +0.0000 +1.0000
         uvs facevarying
                  +0.0001 +0.0001 +0.9999 +0.0001 +0.0001 +0.9999
                  +0.9999 +0.0001 +0.9999 +0.9999 +0.0001 +0.9999
          
         } 
