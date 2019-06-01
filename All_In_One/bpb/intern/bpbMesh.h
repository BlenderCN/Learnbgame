// Filename: bpbMesh.h
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

#ifndef BPBMESH_H
#define BPBMESH_H

#include "bpbObjectData.h"

#include "geom.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBMesh
// Description : This is the implementation of BPB_object_data.
////////////////////////////////////////////////////////////////////
struct BPBMesh : public BPBObjectData {
public:
  INLINE BPBMesh(BPBContext *ctx) : BPBObjectData(ctx) {};

  virtual void update(DNA_ID *dna_id);
  virtual void update_node(PandaNode *node, DNA_ID *dna_id);

private:
  COWPT(Geom) _geom;

  typedef set<BPBObject*> Objects;
  Objects _objects;
};

#endif

