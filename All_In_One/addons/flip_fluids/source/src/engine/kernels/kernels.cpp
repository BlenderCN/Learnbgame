/*
MIT License

Copyright (c) 2018 Ryan L. Guy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "kernels.h"

namespace Kernels {

std::string trilinearinterpolateCL = R"CLC(
/*
MIT License

Copyright (c) 2018 Ryan L. Guy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#define CHUNK_WIDTH 8
#define CHUNK_HEIGHT 8
#define CHUNK_DEPTH 8

#define U_OFFSET 0
#define V_OFFSET 900        // U_OFFSET + (CHUNK_WIDTH + 1) * (CHUNK_HEIGHT + 2) * (CHUNK_DEPTH + 2)
#define W_OFFSET 1800       // V_OFFSET + (CHUNK_WIDTH + 2) * (CHUNK_HEIGHT + 1) * (CHUNK_DEPTH + 2)
#define VFIELD_SIZE 2700    // W_OFFSET + (CHUNK_WIDTH + 2) * (CHUNK_HEIGHT + 2) * (CHUNK_DEPTH + 1)

// VFIELD_SIZE / 6
#define MAX_VFIELD_LOAD_LOCAL_ID 450


float trilinear_interpolate(float p[8], float x, float y, float z) {
    return p[0] * (1 - x) * (1 - y) * (1 - z) +
           p[1] * x * (1 - y) * (1 - z) + 
           p[2] * (1 - x) * y * (1 - z) + 
           p[3] * (1 - x) * (1 - y) * z +
           p[4] * x * (1 - y) * z + 
           p[5] * (1 - x) * y * z + 
           p[6] * x * y * (1 - z) + 
           p[7] * x * y * z;
}

int flatten_index(int i, int j, int k, int isize, int jsize) {
    return i + isize * (j + jsize * k);
}

void fill_interpolation_data(__local float *vfield, 
                             int3 voffset, int vwidth, int vheight,
                             float points[8]) {

    points[0] = vfield[flatten_index(voffset.x,     voffset.y,     voffset.z,     vwidth, vheight)];
    points[1] = vfield[flatten_index(voffset.x + 1, voffset.y,     voffset.z,     vwidth, vheight)];
    points[2] = vfield[flatten_index(voffset.x,     voffset.y + 1, voffset.z,     vwidth, vheight)];
    points[3] = vfield[flatten_index(voffset.x,     voffset.y,     voffset.z + 1, vwidth, vheight)];
    points[4] = vfield[flatten_index(voffset.x + 1, voffset.y,     voffset.z + 1, vwidth, vheight)];
    points[5] = vfield[flatten_index(voffset.x,     voffset.y + 1, voffset.z + 1, vwidth, vheight)];
    points[6] = vfield[flatten_index(voffset.x + 1, voffset.y + 1, voffset.z,     vwidth, vheight)];
    points[7] = vfield[flatten_index(voffset.x + 1, voffset.y + 1, voffset.z + 1, vwidth, vheight)];
}

float interpolate_U(float3 pos, float dx, float invdx, __local float *ufield) {

    pos.y -= 0.5*dx;
    pos.z -= 0.5*dx;

    int3 index = (int3)(floor(pos.x * invdx),
                        floor(pos.y * invdx),
                        floor(pos.z * invdx));

    float3 index_offset = (float3)(index.x * dx,
                                   index.y * dx,
                                   index.z * dx);

    float3 interp_pos = invdx * (pos - index_offset);

    int3 vfield_index_offset = (int3)(index.x + 0,
                                      index.y + 1,
                                      index.z + 1);

    float points[8];
    int vwidth = CHUNK_WIDTH + 1;
    int vheight = CHUNK_HEIGHT + 2;

    fill_interpolation_data(ufield, vfield_index_offset, vwidth, vheight, points);

    return trilinear_interpolate(points, interp_pos.x,
                                         interp_pos.y,
                                         interp_pos.z);
}

float interpolate_V(float3 pos, float dx, float invdx, __local float *vfield) {

    pos.x -= 0.5*dx;
    pos.z -= 0.5*dx;

    int3 index = (int3)(floor(pos.x * invdx),
                        floor(pos.y * invdx),
                        floor(pos.z * invdx));

    float3 index_offset = (float3)(index.x * dx,
                                   index.y * dx,
                                   index.z * dx);

    float3 interp_pos = invdx * (pos - index_offset);

    int3 vfield_index_offset = (int3)(index.x + 1,
                                      index.y + 0,
                                      index.z + 1);

    float points[8];
    int vwidth = CHUNK_WIDTH + 2;
    int vheight = CHUNK_HEIGHT + 1;

    fill_interpolation_data(vfield, vfield_index_offset, vwidth, vheight, points);

    return trilinear_interpolate(points, interp_pos.x,
                                        interp_pos.y,
                                        interp_pos.z);
}

float interpolate_W(float3 pos, float dx, float invdx, __local float *wfield) {

    pos.x -= 0.5*dx;
    pos.y -= 0.5*dx;

    int3 index = (int3)(floor(pos.x * invdx),
                        floor(pos.y * invdx),
                        floor(pos.z * invdx));

    float3 index_offset = (float3)(index.x * dx,
                                   index.y * dx,
                                   index.z * dx);

    int3 vfield_index_offset = (int3)(index.x + 1,
                                      index.y + 1,
                                      index.z + 0);

    float3 interp_pos = invdx * (pos - index_offset);

    float points[8];
    int vwidth = CHUNK_WIDTH + 2;
    int vheight = CHUNK_HEIGHT + 2;

    fill_interpolation_data(wfield, vfield_index_offset, vwidth, vheight, points);

    return trilinear_interpolate(points, interp_pos.x,
                                         interp_pos.y,
                                         interp_pos.z);
}

__kernel void trilinear_interpolate_kernel(__global float *particles,
                                           __global float *vfield_data,
                                           __global int *chunk_offsets,
                                           __local  float *vfield,
                                           float dx) {

    size_t tid = get_global_id(0);
	size_t lid = get_local_id(0);
	size_t gid = tid / get_local_size(0);

    // Load fvield_data into local memory
    if (lid < MAX_VFIELD_LOAD_LOCAL_ID) {
        int local_offset = 6*lid;
        int vfield_data_offset = gid * VFIELD_SIZE + local_offset;

        vfield[local_offset + 0] = vfield_data[vfield_data_offset + 0];
        vfield[local_offset + 1] = vfield_data[vfield_data_offset + 1];
        vfield[local_offset + 2] = vfield_data[vfield_data_offset + 2];
        vfield[local_offset + 3] = vfield_data[vfield_data_offset + 3];
        vfield[local_offset + 4] = vfield_data[vfield_data_offset + 4];
        vfield[local_offset + 5] = vfield_data[vfield_data_offset + 5];
    }

    barrier(CLK_LOCAL_MEM_FENCE);
    
    float3 pos = (float3)(particles[3*tid + 0], 
                          particles[3*tid + 1], 
                          particles[3*tid + 2]);

    int3 chunk_offset = (int3)(chunk_offsets[3*gid + 0],
                               chunk_offsets[3*gid + 1],
                               chunk_offsets[3*gid + 2]);

    int3 index_offset = (int3)(chunk_offset.x * CHUNK_WIDTH,
                               chunk_offset.y * CHUNK_HEIGHT,
                               chunk_offset.z * CHUNK_DEPTH);

    float3 pos_offset = (float3)(index_offset.x * dx,
                                 index_offset.y * dx,
                                 index_offset.z * dx);

    float3 local_pos = pos - pos_offset;

    float invdx = 1.0 / dx;
    float result1 = interpolate_U(local_pos, dx, invdx, &(vfield[U_OFFSET]));
    float result2 = interpolate_V(local_pos, dx, invdx, &(vfield[V_OFFSET]));
    float result3 = interpolate_W(local_pos, dx, invdx, &(vfield[W_OFFSET]));

	particles[3*tid] = result1;
	particles[3*tid + 1] = result2;
	particles[3*tid + 2] = result3;
}
)CLC";

std::string scalarfieldCL = R"CLC(
/*
MIT License

Copyright (c) 2018 Ryan L. Guy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

struct KernelCoefficients {
    float coef1, coef2, coef3;
};

void load_local_memory(int chunk_width,
                       int num_values,
                       __global float *global_data, 
                       __local  float *local_data) {

    size_t lid = get_local_id(0);
    size_t gid = get_global_id(0) / get_local_size(0);

    int local_size = get_local_size(0);
    int num_read = ceil((float)num_values / (float)local_size);

    int max_read_local_id = floor((float)num_values / (float)num_read) - 1;
    int num_remainder = num_values - (max_read_local_id + 1) * num_read;

    if (lid <= max_read_local_id) {
        int local_offset = num_read * lid;
        int global_offset = gid * num_values + local_offset;

        for (int i = 0; i < num_read; i++) {
            local_data[local_offset + i] = global_data[global_offset + i];
        }

        if (lid == max_read_local_id) {
            local_offset = local_offset + num_read;
            global_offset = global_offset + num_read;
            for (int j = 0; j < num_remainder; j++) {
                local_data[local_offset + j] = global_data[global_offset + j]; 
            }  
        }
    }

    barrier(CLK_LOCAL_MEM_FENCE);
}

int3 flat_to_3d_index(int flatidx, int isize, int jsize) {
    int i = flatidx % isize;
    int j = (flatidx / isize) % jsize;
    int k = flatidx / (jsize * isize); 
    return (int3)(i, j, k);
}

struct KernelCoefficients calculate_kernel_coefficients(float r) {
    struct KernelCoefficients coefs;
    coefs.coef1 = (4.0f / 9.0f) * (1.0f / (r*r*r*r*r*r));
    coefs.coef2 = (17.0f / 9.0f) * (1.0f / (r*r*r*r));
    coefs.coef3 = (22.0f / 9.0f) * (1.0f / (r*r));

    return coefs;
}

float evaluate_kernel(float rsq, struct KernelCoefficients *coefs) {
    return 1.0 - (*coefs).coef1*rsq*rsq*rsq + (*coefs).coef2*rsq*rsq - (*coefs).coef3*rsq;
}

__kernel void compute_scalar_field_points(__global float *particles,
                                          __global float *field_data,
                                          __global int *chunk_offsets,
                                          __local  float *local_particles,
                                          int num_particles,
                                          int num_groups,
                                          float radius,
                                          float dx) {
    size_t tid = get_global_id(0);
    size_t lid = get_local_id(0);
    size_t gid = tid / get_local_size(0);

    int local_size = get_local_size(0);
    int chunk_width = (int)floor(cbrt((float)local_size));
    int num_cells = chunk_width * chunk_width * chunk_width;

    int local_data_size = 3 * num_particles;
    load_local_memory(chunk_width, local_data_size, particles, local_particles);

    if (lid >= num_cells) {
        return;
    }

    int3 cell_index = flat_to_3d_index(lid, chunk_width, chunk_width);
    float3 cell_center = (float3)(((float)cell_index.x + 0.5f) * dx,
                                  ((float)cell_index.y + 0.5f) * dx,
                                  ((float)cell_index.z + 0.5f) * dx);

    int3 chunk_index = (int3)(chunk_offsets[3*gid + 0],
                              chunk_offsets[3*gid + 1],
                              chunk_offsets[3*gid + 2]);
    float3 position_offset = (float3)(chunk_index.x * chunk_width * dx,
                                      chunk_index.y * chunk_width * dx,
                                      chunk_index.z * chunk_width * dx);

    struct KernelCoefficients coefs = calculate_kernel_coefficients(radius);

    float sum = 0.0f;
    float3 p;
    float rsq;
    float maxrsq = radius * radius;
    float k;
    float3 v;
    for (int i = 0; i < local_data_size; i += 3) {
        p.x = local_particles[i + 0];
        p.y = local_particles[i + 1];
        p.z = local_particles[i + 2];

        p -= position_offset;
        v = p - cell_center;
        rsq = v.x*v.x + v.y*v.y + v.z*v.z;

        if (rsq < maxrsq) {
            sum += evaluate_kernel(rsq, &coefs);
        }
    }

    int fieldidx = gid * num_cells + lid;
    field_data[fieldidx] = sum;
}

__kernel void compute_scalar_field_point_values(__global float *point_values,
                                                __global float *field_data,
                                                __global int *chunk_offsets,
                                                __local  float *local_point_values,
                                                int num_points,
                                                int num_groups,
                                                float radius,
                                                float dx) {
    size_t tid = get_global_id(0);
    size_t lid = get_local_id(0);
    size_t gid = tid / get_local_size(0);

    int local_size = get_local_size(0);
    int chunk_width = (int)floor(cbrt((float)local_size));
    int num_cells = chunk_width * chunk_width * chunk_width;

    int local_data_size = 4 * num_points;
    load_local_memory(chunk_width, local_data_size, point_values, local_point_values);

    if (lid >= num_cells) {
        return;
    }

    int3 cell_index = flat_to_3d_index(lid, chunk_width, chunk_width);
    float3 cell_center = (float3)(((float)cell_index.x + 0.5f) * dx,
                                  ((float)cell_index.y + 0.5f) * dx,
                                  ((float)cell_index.z + 0.5f) * dx);

    int3 chunk_index = (int3)(chunk_offsets[3*gid + 0],
                              chunk_offsets[3*gid + 1],
                              chunk_offsets[3*gid + 2]);
    float3 position_offset = (float3)(chunk_index.x * chunk_width * dx,
                                      chunk_index.y * chunk_width * dx,
                                      chunk_index.z * chunk_width * dx);

    struct KernelCoefficients coefs = calculate_kernel_coefficients(radius);

    float sum = 0.0f;
    float3 p;
    float rsq;
    float maxrsq = radius * radius;
    float value;
    float3 vect;
    for (int i = 0; i < local_data_size; i += 4) {
        p.x   = local_point_values[i + 0];
        p.y   = local_point_values[i + 1];
        p.z   = local_point_values[i + 2];
        value = local_point_values[i + 3];

        p -= position_offset;
        vect = p - cell_center;
        rsq = vect.x*vect.x + vect.y*vect.y + vect.z*vect.z;

        if (rsq < maxrsq) {
            sum += value * evaluate_kernel(rsq, &coefs);
        }
    }

    int fieldidx = gid * num_cells + lid;
    field_data[fieldidx] = sum;
}

__kernel void compute_scalar_weight_field_point_values(__global float *point_values,
                                                       __global float *field_data,
                                                       __global int *chunk_offsets,
                                                       __local  float *local_point_values,
                                                       int num_points,
                                                       int num_groups,
                                                       float radius,
                                                       float dx) {
    size_t tid = get_global_id(0);
    size_t lid = get_local_id(0);
    size_t gid = tid / get_local_size(0);

    int local_size = get_local_size(0);
    int chunk_width = (int)floor(cbrt((float)local_size));
    int num_cells = chunk_width * chunk_width * chunk_width;

    int local_data_size = 4 * num_points;
    load_local_memory(chunk_width, local_data_size, point_values, local_point_values);

    if (lid >= num_cells) {
        return;
    }

    int3 cell_index = flat_to_3d_index(lid, chunk_width, chunk_width);
    float3 cell_center = (float3)(((float)cell_index.x + 0.5f) * dx,
                                  ((float)cell_index.y + 0.5f) * dx,
                                  ((float)cell_index.z + 0.5f) * dx);

    int3 chunk_index = (int3)(chunk_offsets[3*gid + 0],
                              chunk_offsets[3*gid + 1],
                              chunk_offsets[3*gid + 2]);
    float3 position_offset = (float3)(chunk_index.x * chunk_width * dx,
                                      chunk_index.y * chunk_width * dx,
                                      chunk_index.z * chunk_width * dx);

    struct KernelCoefficients coefs = calculate_kernel_coefficients(radius);

    float scalarsum = 0.0f;
    float weightsum = 0.0f;
    float3 p;
    float rsq;
    float maxrsq = radius * radius;
    float value;
    float weight;
    float3 vect;
    for (int i = 0; i < local_data_size; i += 4) {
        p.x   = local_point_values[i + 0];
        p.y   = local_point_values[i + 1];
        p.z   = local_point_values[i + 2];
        value = local_point_values[i + 3];

        p -= position_offset;
        vect = p - cell_center;
        rsq = vect.x*vect.x + vect.y*vect.y + vect.z*vect.z;

        if (rsq < maxrsq) {
            weight = evaluate_kernel(rsq, &coefs);
            scalarsum += value * weight;
            weightsum += weight;
        }
    }

    int scalarfieldidx = gid * num_cells + lid;
    int weightfieldidx = num_groups * num_cells + scalarfieldidx;
    field_data[scalarfieldidx] = scalarsum;
    field_data[weightfieldidx] = weightsum;
}

__kernel void compute_scalar_field_levelset_points(__global float *particles,
                                                   __global float *field_data,
                                                   __global int *chunk_offsets,
                                                   __local  float *local_particles,
                                                   int num_particles,
                                                   int num_groups,
                                                   float radius,
                                                   float dx) {
    size_t tid = get_global_id(0);
    size_t lid = get_local_id(0);
    size_t gid = tid / get_local_size(0);

    int local_size = get_local_size(0);
    int chunk_width = (int)floor(cbrt((float)local_size));
    int num_cells = chunk_width * chunk_width * chunk_width;

    int local_data_size = 3 * num_particles;
    load_local_memory(chunk_width, local_data_size, particles, local_particles);

    if (lid >= num_cells) {
        return;
    }

    int3 cell_index = flat_to_3d_index(lid, chunk_width, chunk_width);
    float3 cell_center = (float3)(((float)cell_index.x + 0.5f) * dx,
                                  ((float)cell_index.y + 0.5f) * dx,
                                  ((float)cell_index.z + 0.5f) * dx);

    int3 chunk_index = (int3)(chunk_offsets[3*gid + 0],
                              chunk_offsets[3*gid + 1],
                              chunk_offsets[3*gid + 2]);
    float3 position_offset = (float3)(chunk_index.x * chunk_width * dx,
                                      chunk_index.y * chunk_width * dx,
                                      chunk_index.z * chunk_width * dx);

    float minval = 3.0f * radius;
    float3 p;
    float dist;
    float maxrsq = radius * radius;
    float k;
    float3 v;
    for (int i = 0; i < local_data_size; i += 3) {
        p.x = local_particles[i + 0];
        p.y = local_particles[i + 1];
        p.z = local_particles[i + 2];

        p -= position_offset;
        v = p - cell_center;
        dist = sqrt(v.x*v.x + v.y*v.y + v.z*v.z) - radius;
        if (dist < minval) {
            minval = dist;
        }
    }

    int fieldidx = gid * num_cells + lid;
    field_data[fieldidx] = minval;
}
)CLC";

}
