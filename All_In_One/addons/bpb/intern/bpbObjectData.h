// Filename: bpbObjectData.h
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

#ifndef BPBOBJECTDATA_H
#define BPBOBJECTDATA_H

#include "bpbID.h"
#include "bpbObject.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBObjectData
// Description : This is the implementation of BPB_object_data.
////////////////////////////////////////////////////////////////////
struct BPBObjectData : public BPBID {
public:
  INLINE BPBObjectData(BPBContext *ctx) : BPBID(ctx) {};
  virtual ~BPBObjectData();

  virtual void update(DNA_ID *dna_id);
  virtual void update_node(PandaNode *node, DNA_ID *dna_id);

private:
  typedef set<BPBObject*> Objects;
  Objects _objects;

  friend struct BPBObject;
};

#endif
