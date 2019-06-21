/* Filename: bpb_api.c
 * Created by:  rdb (20Jan15)
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 * PANDA 3D SOFTWARE
 * Copyright (c) Carnegie Mellon University.  All rights reserved.
 *
 * All use of this software is subject to the terms of the revised BSD
 * license.  You should have received a copy of this license along
 * with this source code in a file named "LICENSE."
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

#ifndef BPB_API_H
#define BPB_API_H

/* This file defines the C API that forms the interface between the
   Python part and the C++ part of the Blender->Panda3D bridge.
   We don't wrap this with interrogate but instead use ctypes to access
   it, so that we can safely compile Blender and Panda3D with differing
   versions of Python without a conflict occurring.  This is also a way
   of preventing Blender's GPL license from affecting the C++ part of
   the Blender->Panda3D bridge.
*/

#ifdef __cplusplus
extern "C" {
#endif

/* This is increased whenever there is a change to the API, eg. a new
   parameter added to a function or field added to a structure.  It
   is passed to BPB_initialize() and lower values can be used to
   create a backward compatible context. */
#define BPB_API_VERSION 0

/* Forward declare struct pointers, which are actually C++ classes. */
typedef struct BPBContext BPB_context;
typedef struct BPBMaterial BPB_material;
typedef struct BPBObject BPB_object;
typedef struct BPBObjectData BPB_object_data;
typedef struct BPBRenderer BPB_renderer;

/* Forward declare Blender's DNA structs.  Let's rename them while
   we're at it for more clarity. */
typedef struct ID DNA_ID;
typedef struct Material DNA_Material;
typedef struct Object DNA_Object;

/* This function is used to initialize the bridge.  The returned
   context object is expected to be passed as the first argument to
   all of the other functions.  More than one context can be active
   at any one time.
   Pass the API version that you write the program against.  If this
   library is too old to support the given API version, BPB_initialize
   will return NULL. */

BPB_context *BPB_initialize(int api_version);

/* Call BPB_make_object when you've encountered a new Blender object.
   The object is bound to the context. */

BPB_object *BPB_new_object(BPB_context *ctx);
BPB_context *BPB_object_get_context(BPB_object *obj);

void BPB_object_update(BPB_object *obj, DNA_Object *dna_obj);
void BPB_object_set_data(BPB_object *obj, BPBObjectData *data);
void BPB_object_set_parent(BPB_object *obj, BPBObject *parent);
void BPB_object_set_material(BPB_object *obj, BPBMaterial *parent);
void BPB_object_destroy(BPB_object *obj);

/* Functions for BPB_object_data, which represents an object-associated
   data block (anything that goes into object.data in Blender) */

BPB_object_data *BPB_new_object_data(BPB_context *ctx, short type);
BPB_context *BPB_object_data_get_context(BPB_object_data *obj_data);

short BPB_object_data_get_type(BPB_object_data *obj_data);
void BPB_object_data_update(BPB_object_data *obj_data, DNA_ID *dna_data);
void BPB_object_data_destroy(BPB_object_data *obj_data);

/* Material. */

BPB_material *BPB_new_material(BPB_context *ctx);
void BPB_material_update(BPB_material *obj, DNA_Material *dna_mat);
void BPB_material_destroy(BPB_material *obj);

/* The following describes the renderer interface. */

enum BPB_renderer_flags {
  BPB_RF_background = 0x01,
  BPB_RF_srgb = 0x02,
};

enum BPB_render_type {
  /* Opens an external window to render into. */
  BPB_RT_window = 1,

  /* Renders to an OpenGL viewport. */
  BPB_RT_gl_viewport = 2,

  /* Renders to a texture object. */
  BPB_RT_texture = 3,
};

struct BPB_render_desc {
  /* The viewpoint from which the scene is to be rendered. */
  BPB_object *camera;
  BPB_object *world;

  /* Total size of the window or render area.  This is *not* the size
     of the desired render output. */
  int width, height;

  /* The dimensions of the region that needs to be rendered. */
  int region_x;
  int region_y;
  int region_width;
  int region_height;

  /* If non-NULL, the filename to write the result to. */
  char *file_name;
};

BPB_renderer *BPB_new_renderer(BPB_render_type type, int flags);
void BPB_renderer_destroy(BPB_renderer *renderer);

/* If this is a background renderer, does nothing except set the settings. */
void BPB_renderer_start(BPB_renderer *renderer, BPB_render_desc *desc);

/* Finishes a rendering approach fired off earlier.  If the render hasn't
   finished yet, this will block until the render is done. */

void BPB_renderer_finish(BPB_renderer *renderer);

#ifdef __cplusplus
};  /* end of extern "C" */
#endif

#endif  /* BPB_API_H */
