// Filename: bpb_api.cxx
// Created by:  rdb (20Jan15)
//
////////////////////////////////////////////////////////////////////
//
// PANDA 3D SOFTWARE
// Copyright (c) Carnegie Mellon University.  All rights reserved.
//
// All use of this software is subject to the terms of the revised BSD
// license.  You should have received a copy of this license along
// with this source code in a file named "LICENSE."
//
////////////////////////////////////////////////////////////////////

#include "bpb_api.h"

#include "bpbContext.h"
#include "bpbObject.h"
#include "bpbObjectData.h"
#include "bpbOpenGLRenderer.h"
#include "bpbWindowRenderer.h"

BPB_context *
BPB_initialize(int api_version) {
  if (api_version > BPB_API_VERSION) {
    return NULL;
  }

  BPBContext *context = new BPBContext(api_version);
  return context;
}

BPB_object *
BPB_new_object(BPB_context *ctx) {
  nassertr(ctx != NULL, NULL);

  BPBObject *object = new BPBObject(ctx);
  return object;
}

BPB_context *
BPB_object_get_context(BPB_object *obj) {
  nassertr(BPBID::validate(obj), NULL);
  return obj->get_context();
}

void
BPB_object_update(BPB_object *obj, DNA_Object *dna_obj) {
  nassertv(BPBID::validate(obj));

  obj->update((DNA_ID *)dna_obj);
}

void
BPB_object_set_data(BPB_object *obj, BPB_object_data *obj_data) {
  nassertv(BPBID::validate(obj));

  BPBObject *object = (BPBObject *)obj;
  BPBObjectData *object_data = (BPBObjectData *)obj_data;

  nassertv(BPBID::validate(object));
  nassertv(BPBID::validate(object_data));

  object->set_data(object_data);
}

void
BPB_object_set_parent(BPB_object *obj, BPB_object *parent) {
  nassertv(BPBID::validate(obj));
  obj->set_parent(parent);
}

void BPB_object_destroy(BPB_object *obj) {
  nassertv(BPBID::validate(obj));
  delete obj;
}

BPB_object_data *
BPB_new_object_data(BPB_context *ctx, short type) {
  nassertr(ctx != NULL, NULL);

  BPBMesh *object_data = new BPBMesh(ctx);
  return object_data;
}

BPB_context *
BPB_object_data_get_context(BPB_object_data *obj) {
  nassertr(BPBID::validate(obj), NULL);
  return obj->get_context();
}

void
BPB_object_data_update(BPB_object_data *obj, DNA_ID *dna_id) {
  nassertv(BPBID::validate(obj));

  obj->update((DNA_ID *)dna_id);
}


BPB_renderer *
BPB_new_renderer(BPB_render_type type, int flags) {
  switch (type) {
  case BPB_RT_window:
    return (BPBRenderer *)new BPBWindowRenderer(flags);

  case BPB_RT_gl_viewport:
    return (BPBRenderer *)new BPBOpenGLRenderer(flags);

  case BPB_RT_texture:
  default:
    return NULL;
  }
}

void BPB_renderer_start(BPB_renderer *renderer, BPB_render_desc *desc) {
  nassertv(renderer != NULL);
  nassertv(desc != NULL);

  const BPB_render_desc &desc2 = *desc;
  renderer->start(*desc);
}

void BPB_renderer_finish(BPB_renderer *renderer) {
  nassertv(renderer != NULL);

  renderer->finish();
}
