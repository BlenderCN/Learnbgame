"use strict";
"not_a_module";

var aabb_tri_isect_code_attrib = """
********************************************************
* AABB-triangle overlap test code                      *
* by Tomas Akenine-Möller                              *
* Function: int triBoxOverlap(float boxcenter[3],      *
*          float boxhalfsize[3],float triverts[3][3]); *
* History:                                             *
*   2001-03-05: released the code in its first version *
*   2001-06-18: changed the order of the tests, faster *
*                                                      *
* Acknowledgement: Many thanks to Pierre Terdiman for  *
* suggestions and discussions on how to optimize code. *
* Thanks to David Hunt for finding a ">="-bug!         *
********************************************************
""";


#define CROSS(dest,v1,v2) \
    dest[0]=v1[1]*v2[2]-v1[2]*v2[1]; \
    dest[1]=v1[2]*v2[0]-v1[0]*v2[2]; \
    dest[2]=v1[0]*v2[1]-v1[1]*v2[0]; 



#define DOT(v1,v2) (v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2])



#define SUB(dest,v1,v2) \
      dest[0]=v1[0]-v2[0]; \
      dest[1]=v1[1]-v2[1]; \
      dest[2]=v1[2]-v2[2]; 



#define FINDMINMAX(x0,x1,x2,min,max) \
  min = max = x0;   \
  if(x1<min) min=x1;\
  if(x1>max) max=x1;\
  if(x2<min) min=x2;\
  if(x2>max) max=x2;

function planeBoxOverlap(Array<float> normal, Array<float> vert, Array<float> maxbox) // -NJMP-
{
  static vmin = new Vector3(), vmax = new Vector3();
  
  for(var q=0;q<=3;q++)
  {
    var v=vert[q];					// -NJMP-
    if(normal[q]>0.0) {
      vmin[q]=-maxbox[q] - v;	// -NJMP-
      vmax[q]= maxbox[q] - v;	// -NJMP-
    } else {
      vmin[q]= maxbox[q] - v;	// -NJMP-
      vmax[q]=-maxbox[q] - v;	// -NJMP-
    }
  }

  if(DOT(normal,vmin)>0.0) return 0;	// -NJMP-
  if(DOT(normal,vmax)>=0.0) return 1;	// -NJMP-

  return 0;
}





/*======================== X-tests ========================*/

#define AXISTEST_X01(a, b, fa, fb)			   \
	p0 = a*v0[1] - b*v0[2];			       	   \
	p2 = a*v2[1] - b*v2[2];			       	   \
        if(p0<p2) {min=p0; max=p2;} else {min=p2; max=p0;} \
	rad = fa * boxhalfsize[1] + fb * boxhalfsize[2];   \
	if(min>rad || max<-rad) return 0;


#define AXISTEST_X2(a, b, fa, fb)			   \
	p0 = a*v0[1] - b*v0[2];			           \
	p1 = a*v1[1] - b*v1[2];			       	   \
        if(p0<p1) {min=p0; max=p1;} else {min=p1; max=p0;} \
	rad = fa * boxhalfsize[1] + fb * boxhalfsize[2];   \
	if(min>rad || max<-rad) return 0;

/*======================== Y-tests ========================*/

#define AXISTEST_Y02(a, b, fa, fb)			   \
	p0 = -a*v0[0] + b*v0[2];		      	   \
	p2 = -a*v2[0] + b*v2[2];	       	       	   \
        if(p0<p2) {min=p0; max=p2;} else {min=p2; max=p0;} \
	rad = fa * boxhalfsize[0] + fb * boxhalfsize[2];   \
	if(min>rad || max<-rad) return 0;



#define AXISTEST_Y1(a, b, fa, fb)			   \
	p0 = -a*v0[0] + b*v0[2];		      	   \
	p1 = -a*v1[0] + b*v1[2];	     	       	   \
        if(p0<p1) {min=p0; max=p1;} else {min=p1; max=p0;} \
	rad = fa * boxhalfsize[0] + fb * boxhalfsize[2];   \
	if(min>rad || max<-rad) return 0;

/*======================== Z-tests ========================*/

#define AXISTEST_Z12(a, b, fa, fb)			   \
	p1 = a*v1[0] - b*v1[1];			           \
	p2 = a*v2[0] - b*v2[1];			       	   \
        if(p2<p1) {min=p2; max=p1;} else {min=p1; max=p2;} \
	rad = fa * boxhalfsize[0] + fb * boxhalfsize[1];   \
	if(min>rad || max<-rad) return 0;

#define AXISTEST_Z0(a, b, fa, fb)			   \
	p0 = a*v0[0] - b*v0[1];				   \
	p1 = a*v1[0] - b*v1[1];			           \
        if(p0<p1) {min=p0; max=p1;} else {min=p1; max=p0;} \
	rad = fa * boxhalfsize[0] + fb * boxhalfsize[1];   \
	if(min>rad || max<-rad) return 0;


//boxcenter[3], boxhalfsize[3], triverts[3][3]
function triBoxOverlap(Array<float> boxcenter, Array<float> boxhalfsize, Array<Array<float>> triverts)
{


  /*    use separating axis theorem to test overlap between triangle and box */
  /*    need to test for overlap in these directions: */
  /*    1) the {x,y,z}-directions (actually, since we use the AABB of the triangle */
  /*       we do not even need to test these) */
  /*    2) normal of the triangle */
  /*    3) crossproduct(edge from tri, {x,y,z}-directin) */
  /*       this gives 3x3=9 more tests */

   static v0 = new Vector3(), v1 = new Vector3(), v2 = new Vector3();
    
   var min,max,p0,p1,p2,rad,fex,fey,fez;		// -NJMP- "d" local variable removed
   static normal = new Vector3(), e0 = new Vector3(), e1 = new Vector3(), e2 = new Vector3();


   /* This is the fastest branch on Sun */
   /* move everything so that the boxcenter is in (0,0,0) */

   SUB(v0,triverts[0],boxcenter);
   SUB(v1,triverts[1],boxcenter);
   SUB(v2,triverts[2],boxcenter);

   /* compute triangle edges */
   
   SUB(e0,v1,v0);      /* tri edge 0 */
   SUB(e1,v2,v1);      /* tri edge 1 */

   SUB(e2,v0,v2);      /* tri edge 2 */


   /* Bullet 3:  */
   /*  test the 9 tests first (this was faster) */

   fex = Math.abs(e0[0]);
   fey = Math.abs(e0[1]);
   fez = Math.abs(e0[2]);

   AXISTEST_X01(e0[2], e0[1], fez, fey);
   AXISTEST_Y02(e0[2], e0[0], fez, fex);
   AXISTEST_Z12(e0[1], e0[0], fey, fex);


   fex = Math.abs(e1[0]);
   fey = Math.abs(e1[1]);
   fez = Math.abs(e1[2]);

   AXISTEST_X01(e1[2], e1[1], fez, fey);
   AXISTEST_Y02(e1[2], e1[0], fez, fex);
   AXISTEST_Z0(e1[1], e1[0], fey, fex);


   fex = Math.abs(e2[0]);
   fey = Math.abs(e2[1]);
   fez = Math.abs(e2[2]);

   AXISTEST_X2(e2[2], e2[1], fez, fey);
   AXISTEST_Y1(e2[2], e2[0], fez, fex);
   AXISTEST_Z12(e2[1], e2[0], fey, fex);


   /* Bullet 1: */
   /*  first test overlap in the {x,y,z}-directions */
   /*  find min, max of the triangle each direction, and test for overlap in */
   /*  that direction -- this is equivalent to testing a minimal AABB around */
   /*  the triangle against the AABB */



   /* test in X-direction */

   FINDMINMAX(v0[0],v1[0],v2[0],min,max);

   if(min>boxhalfsize[0] || max<-boxhalfsize[0]) return 0;


   /* test in Y-direction */

   FINDMINMAX(v0[1],v1[1],v2[1],min,max);

   if(min>boxhalfsize[1] || max<-boxhalfsize[1]) return 0;



   /* test in Z-direction */

   FINDMINMAX(v0[2],v1[2],v2[2],min,max);

   if(min>boxhalfsize[2] || max<-boxhalfsize[2]) return 0;


   /* Bullet 2: */
   /*  test if the box intersects the plane of the triangle */
   /*  compute plane equation of triangle: normal*x+d=0 */

   CROSS(normal,e0,e1);

   // -NJMP- (line removed here)

   if(!planeBoxOverlap(normal,v0,boxhalfsize)) return 0;	// -NJMP-


   return 1;   /* box and triangle overlaps */
}

function tri_aabb_isect(v1, v2, v3, min, max)
{
    static cent = new Vector3(), size = new Vector3();
    static triverts = [0, 0, 0];
    
    triverts[0] = v1; triverts[1] = v2; triverts[2] = v3;
    
    cent.load(max).add(min).mulScalar(0.5);
    size.load(max).sub(min).mulScalar(0.5);
    
    return triBoxOverlap(cent, size, triverts);
}

var ray_tri_attrib = """
* Ray-Triangle Intersection Test Routines          *
* Different optimizations of my and Ben Trumbore's *
* code from journals of graphics tools (JGT)       *
* http://www.acm.org/jgt/                          *
* by Tomas Moller, May 2000                        *
""";

#define EPSILON 0.000001

/* the original jgt code */
function ray_tri_isect(Array<float> orig, Array<float> dir, 
           Array<float> vert0, Array<float> vert1, Array<float> vert2) : Array<float>
{
  static edge1 = new Vector3(), edge2 = new Vector3(), tvec = new Vector3()
  static qvec = new Vector3(), pvec = new Vector3();
  var det, inv_det;
  
  /* find vectors for two edges sharing vert0 */
  SUB(edge1, vert1, vert0);
  SUB(edge2, vert2, vert0);

  /* begin calculating determinant - also used to calculate U parameter */
  CROSS(pvec, dir, edge2);

  /* if determinant is near zero, ray lies in plane of triangle */
  det = DOT(edge1, pvec);

  if (det > -EPSILON && det < EPSILON)
   return undefined;
  inv_det = 1.0 / det;

  /* calculate distance from vert0 to ray origin */
  SUB(tvec, orig, vert0);

  /* calculate U parameter and test bounds */
  var u = DOT(tvec, pvec) * inv_det;
  if (u < 0.0 || u > 1.0)
   return undefined;

  /* prepare to test V parameter */
  CROSS(qvec, tvec, edge1);

  /* calculate V parameter and test bounds */
  var v = DOT(dir, qvec) * inv_det;
  if (v < 0.0 || u + v > 1.0)
   return undefined;

  /* calculate t, ray intersects triangle */
  var t = DOT(edge2, qvec) * inv_det;
  
  static ret = [0, 0, 0];
  
  ret[0] = t;
  ret[1] = u;
  ret[2] = v;
  
  return ret;
}

#define SWAP(a, b) ((tmp=a), (a=b), (b=tmp))

function aabb_ray_isect(co, indir, min, max) {
    var tmp;
    
    static dir = new Vector3();
    
    dir.load(indir);
    dir.mul(20000);
    
    var tmin = (min[0] - co[0]) / dir[0];
    var tmax = (max[0] - co[0]) / dir[0];
    if (tmin > tmax) SWAP(tmin, tmax);
    
    var tymin = (min[1] - co[1]) / dir[1];
    var tymax = (max[1] - co[1]) / dir[1];
    
    if (tymin > tymax) SWAP(tymin, tymax);
    
    if ((tmin > tymax) || (tymin > tmax))
        return false;
        
    if (tymin > tmin)
        tmin = tymin;
    if (tymax < tmax)
        tmax = tymax;
    
    var tzmin = (min[2] - co[2]) / dir[2];
    var tzmax = (max[2] - co[2]) / dir[2];
    
    if (tzmin > tzmax) SWAP(tzmin, tzmax);
    
    if ((tmin > tzmax) || (tzmin > tmax))
        return false;
        
    return true;
}

//taken from http://www.scratchapixel.com/lessons/3d-basic-lessons/lesson-7-intersecting-simple-shapes/ray-box-intersection/
//
//will write proper version later
//a bit sick of writing this function, actually
function aabb_ray_isectevil(co, dir, min, max) {
  var bounds = [0, 0];
  
  bounds[0] = min; 
  bounds[1] = max;
  
  var sign = [0, 0, 0];
  var invdir = new Vector3();
  
  invdir.load(dir);
  invdir.mulScalar(20000.0);
  
  /*if (invdir[0] == 0.0) invdir[0] = 0.00001;
  if (invdir[1] == 0.0) invdir[1] = 0.00001;
  if (invdir[2] == 0.0) invdir[2] = 0.00001;*/
  
  invdir[0] = 1.0/invdir[0]; invdir[1] =  1.0/invdir[1]; invdir[2] = 1.0/invdir[2];
  
  /* turn truth values into 0/1's */
  sign[0] = 0+(invdir[0] < 0);
  sign[1] = 0+(invdir[1] < 0);
  sign[2] = 0+(invdir[2] < 0);
  
  var tmin, tmax, tymin, tymax, tzmin, tzmax;
  //console.log(sign[0], sign[1], sign[2], 1-sign[0], 1-sign[1], 1-sign[2]);
  
  tmin  = (bounds[sign[0]][0]   - co[0]) * invdir[0];
  tmax  = (bounds[1-sign[0]][0] - co[0]) * invdir[0];
    
  tymin = (bounds[sign[1]][1]   - co[1]) * invdir[1];
  tymax = (bounds[1-sign[1]][1] - co[1]) * invdir[1];
  
  //console.log(tmin, tymax, tymin, tmax, "-=-==");
  
//#define GT(a, b) (Math.abs(a-b) > 0.0 && (a > b))
//#define LT(a, b) (Math.abs(a-b) > 0.0 && (a < b))

  #define GT(a, b) (a > b)
  #define LT(a, b) (a < b)
  
  if (GT(tmin, tymax) || GT(tymin, tmax))
      return false;
  if (GT(tymin, tmin))
      tmin = tymin;
  if (LT(tymax, tmax))
      tmax = tymax;
  
  tzmin = (bounds[sign[2]][2]   - co[2]) * invdir[2];
  tzmax = (bounds[1-sign[2]][2] - co[2]) * invdir[2];
  
  if (GT(tmin, tzmax) || GT(tzmin, tmax))
      return false;
  if (GT(tzmin, tmin))
      tmin = tzmin;
  if (LT(tzmax, tmax))
      tmax = tzmax;
      
  //console.log("tmin:", tmin, "tmax:", tmax);
  return true;
}
