// Filename: bpbObject.h
// Created by: rdb (20Jan15)
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

#ifndef BPBOBJECT_H
#define BPBOBJECT_H

#include "bpbContext.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBObject
// Description : This is the implementation of BPB_object.
//               It manages a scene graph object.
////////////////////////////////////////////////////////////////////
struct BPBObject : public BPBID {
public:
  INLINE BPBObject(BPBContext *ctx) : BPBID(ctx) {};

  INLINE BPBObjectData *get_data() const;
  void set_data(BPBObjectData *data);

  INLINE BPBObject *get_parent() const;
  void set_parent(BPBObject *parent);

  PandaNode *get_node();

  virtual void update(DNA_ID *dna_id);

private:
  BPBObjectData *_data;
  BPBObject *_parent;

  PT(PandaNode) _node;
  short _data_type;
};

#include "bpbObject.I"

#endif

