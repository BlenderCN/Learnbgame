import bpy
import math
from mathutils import Vector

import numpy as np
import pyopencl as cl
import pyopencl.array
clTypes = pyopencl.array.vec
mf = cl.mem_flags

from .srbf import ALL_SRBFS
from .shared import COLOUR_MAP
from .operatorShared import SharedOperatorBase

#############################################

SRBFStruct = np.dtype([ 
    ("id", np.uint32),
    ("center", clTypes.float3),
    ("width", np.float32),
    ("amplitude", np.float32)
  ])

#############################################

def srbfCollectionAsArray(coll):
    arr = np.zeros(len(coll), dtype=SRBFStruct)
    for i, func in enumerate(coll):
        arr[i]['id'] = func.ID
        arr[i]['center'] = func.position.to_4d().to_tuple()
        arr[i]['width'] = func.width
        arr[i]['amplitude'] = func.amplitude
    return arr

#############################################

# normalise pixel coords to uv
OCL_UV_FUNC = """
    float2 getUV() {
        float2 uv;
        uv.x = get_global_id(0) / (float) (get_global_size(0)-1);
        uv.y = get_global_id(1) / (float) (get_global_size(1)-1);
        return uv;
    }
"""

# sphere mapping of uv to unit sphere / direction
OCL_UV2DIR_FUNC = """
    float3 uv2dir(float2 uv) {
        uv -= 0.5f;
        uv *= 2.0f;

        float3 dir;
            //float l = length(uv);
            //dir.z = fmax( (0.5f-l) * 2, -1.0f);
        dir.z = cos( M_PI_F * fmin(length(uv), 1.0f) );
        uv = normalize(uv);
        dir.xy = sqrt( 1 - dir.z * dir.z ) * uv;
        return dir;
    }
"""

#############################################

# check for intersection of a ray starting at (0,0,0) and a triangle
OCL_RAY_TRI_INTERSECT = """
    #define SWAP(a, b) { \
        float4 tmp = a; \
        a = b; \
        b = tmp; \
    }
    
    #define SMOOTH_FACTOR(x) ( 1.0f - smoothstep( 0.3f, 0.7f, fabs(x - 0.5f) ) )

    float rayTriIntersect(float3 ray, float3 t0, float3 t1, float3 t2) {
        // construct linear system
        // a*ray = t0 + b*v0 + c*v1 => a*ray - b*v0 - c*v1 = t0
        float4 l0 = (float4)(ray.x, -(t1.x-t0.x), -(t2.x-t0.x), t0.x);
        float4 l1 = (float4)(ray.y, -(t1.y-t0.y), -(t2.y-t0.y), t0.y);
        float4 l2 = (float4)(ray.z, -(t1.z-t0.z), -(t2.z-t0.z), t0.z);
        
        if(l0.x == 0) {
            if(l1.x != 0)
              SWAP(l0, l1)
            else if(l2.x != 0)
              SWAP(l0, l2)
            else
              return 0;
        }
        
        l0 /= l0.x;
        l1 -= l0*l1.x;
        l2 -= l0*l2.x;
        
        if(l1.y == 0) {
            if(l2.y != 0)
              SWAP(l1, l2)
            else
              return 0;
        }
        
        l1 /= l1.y;
        l2 -= l1*l2.y;
        l0 -= l1*l0.y;
        
        if(l2.z == 0)
            return 0;
        
        l2 /= l2.z;
        l1 -= l2*l1.z;
        l0 -= l2*l0.z;

        if(l0.w <= 0) // wrong direction
            return 0;
        return fmin( fmin( SMOOTH_FACTOR(l1.w), SMOOTH_FACTOR(l2.w) ), SMOOTH_FACTOR(l1.w+l2.w) );
    }
"""

OCL_GROUND_LEVEL = """
    __kernel void calcGroundLevel(uint nTris, __global float *vCoords, __global float *groundLvls, __global float *heights) {
      float3 dir = uv2dir( getUV() );
      float height = 0;
      float norm = 0;
      for(uint i = 0; i < nTris; ++i) {
        float fac = rayTriIntersect( dir, vload3(i*3, vCoords), vload3(i*3 + 1, vCoords), vload3(i*3 + 2, vCoords) );
        norm += fac;
        height += fac*groundLvls[i];
      }
      int gid = get_global_id(0) + get_global_id(1)*get_global_size(0);
      heights[gid] = height/norm;
    }
"""

#############################################

#inlined OCL_CODEs of the SRBFs
OCL_EVAL_FUNC = " float eval(uint id, float dist) { " + \
    ( "\n".join( "if (id == %i) { %s }" % (func.ID, func.OCL_CODE) for func in ALL_SRBFS) ) + \
    " return 0; }"

OCL_HEIGHT_KERNEL = """
    __kernel void calcHeight(__global SRBF *funcs, uint count, __global float *heights) {
      float3 dir = uv2dir( getUV() );
      float height = 0;
      for(uint i = 0; i < count; ++i) {
          SRBF srbf = funcs[i];
          float angle = acos( dot(srbf.center, dir) );
          height += srbf.amplitude * eval(srbf.id, angle / (M_PI_F * srbf.width) );
      }
      int gid = get_global_id(0) + get_global_id(1)*get_global_size(0);
      heights[gid] += height;
    }
"""

#############################################

OCL_COLOUR_MAP = "float3 colourMap(float height) {" + \
    ( "\n".join( "if (height < %ff) return (float3)(%ff, %ff, %ff); " % ( (h,)+c.to_tuple() ) for h, c in COLOUR_MAP) ) + \
    "return (float3)(%ff, %ff, %ff);" % COLOUR_MAP[-1][1].to_tuple() + \
    "}"

OCL_COLOUR_KERNEL = """
    __kernel void calcColour(__global float *heights, __global float4 *colours) {
        int gid = get_global_id(0);
        float4 col;
        col.xyz = colourMap(heights[gid]);
        col.w = 1;
        colours[gid] = col;
    }
"""

#############################################

OCL_FULL_CODE = OCL_UV_FUNC + OCL_UV2DIR_FUNC + OCL_RAY_TRI_INTERSECT + OCL_GROUND_LEVEL + OCL_EVAL_FUNC + OCL_HEIGHT_KERNEL + OCL_COLOUR_MAP + OCL_COLOUR_KERNEL

def clInit():
    global clContext, clQueue
    clContext = cl.create_some_context(interactive=False)
    clQueue = cl.CommandQueue(clContext)
    
    global SRBFStruct
    SRBFStruct, OCL_SRBF_STRUCT = cl.tools.match_dtype_to_c_struct(clContext.devices[0], "SRBF", SRBFStruct)
    
    global clRenderProg
    clRenderProg = cl.Program(clContext, OCL_SRBF_STRUCT + OCL_FULL_CODE).build()

#############################################

def clRender(srbfs, tect, resolution = 1024):
    TEX_SIZE = resolution
    TEX_DIM = [TEX_SIZE, TEX_SIZE]
    TEX_COUNT = TEX_SIZE * TEX_SIZE
    
    dHeights = cl.Buffer(clContext, mf.READ_WRITE, TEX_COUNT*np.float32().itemsize)

    tesselation = tect.bmesh.calc_tessface()
    dTris = cl.array.to_device(clQueue, np.array( list( coord for tri in tesselation for loop in tri for coord in loop.vert.co ) , dtype=np.float32 ) )
    dGroundLvls = cl.array.to_device(clQueue, np.array( list( tect.groundLevels[tri[0].face.index] for tri in tesselation ) , dtype=np.float32 ))
    clRenderProg.calcGroundLevel(clQueue, TEX_DIM, None, np.uint32(len(tesselation)), dTris.data, dGroundLvls.data, dHeights)    
    
    dFuncs = cl.array.to_device(clQueue, srbfCollectionAsArray(srbfs.coll))
    clRenderProg.calcHeight(clQueue, TEX_DIM, None, dFuncs.data, np.uint32(len(srbfs.coll)), dHeights)

    dColours = cl.Buffer(clContext, mf.READ_WRITE, TEX_COUNT*clTypes.float4.itemsize)
    clRenderProg.calcColour(clQueue, [TEX_COUNT], None, dHeights, dColours)

    # copy height data to host
    hHeights = np.empty(TEX_COUNT, dtype=np.float32)
    cl.enqueue_copy(clQueue, hHeights, dHeights)

    # copy color data to new image
    hColours = np.empty(TEX_COUNT*4, dtype=np.float32)
    cl.enqueue_copy(clQueue, hColours, dColours)
    img = bpy.data.images.new("terrain", TEX_SIZE, TEX_SIZE, float_buffer=True)
    img.pixels = hColours
    # and make it persistent in blend file
    img.update()
    img.pack(as_png=True)
    
    return hHeights, img

#############################################

def dir2TexCoord(vec, texSize):
    norm = math.acos(vec.z) / math.pi
    uv = vec.xy.normalized()
    uv *= norm
    uv /= 2
    uv += Vector((.5, .5))
    return uv.x*(texSize-1), uv.y*(texSize-1)
    
from math import ceil, floor
def biLinSample(map, size, x, y):
    xi, yi = floor(x), floor(y)
    dx, dy = x-xi, y-yi
    return (map[xi+size*yi] * (1-dx) + map[xi+1+size*yi] * dx) * (1-dy) + \
           (map[xi+size*(yi+1)] * (1-dx) + map[xi+1+size*(yi+1)] * dx) * dy;

#############################################

class GenerateGPU(bpy.types.Operator, SharedOperatorBase):
    bl_idname = "mesh.stfu_generate_gpu"
    bl_label = "Random Planet (GPU)"
    bl_options = {"REGISTER", "UNDO"}

    res = bpy.props.IntProperty(
        name        = "Resolution",
        description = "Size of rendered texture in pixels",
        default     = 512,
        min         = 64,
        soft_max    = 1024
    )

    def processHeightmap(self, context, srbfs, tect):
        heights, img = clRender(srbfs, tect, self.res)
        tex = bpy.data.textures.new("Terrain Sphere Texture", "IMAGE")
        tex.image = img
        
        mat = bpy.data.materials["__ Terrain Sphere Map"].copy()
        mat.node_tree.nodes["Texture"].texture = tex
        context.object.data.materials.clear()
        context.object.data.materials.append(mat)
        
        # scale verts according to height value
        for vdata in context.object.data.vertices:
            vdata.co = vdata.co.normalized()
            h = biLinSample(heights, self.res, *dir2TexCoord(vdata.co, self.res))
            #x, y = dir2Idx(vdata.co, self.res)
            #h = heights[round(x) + self.res*round(y)]
            if h > 0 or not self.fillOceans:
                vdata.co *= 1 + h
        