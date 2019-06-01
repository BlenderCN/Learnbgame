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

#ifndef BPBID_H
#define BPBID_H

#include "bpbContext.h"
#include "bpb_api.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBID
// Description : This is the base class of every class that
//               represents a Blender datablock.
////////////////////////////////////////////////////////////////////
struct BPBID {
public:
  INLINE BPBID(BPBContext *ctx) : _context(ctx) {};
  virtual ~BPBID() {};

  static bool validate(BPBID *id);

  INLINE BPBContext *get_context() const;

  virtual void update(DNA_ID *dna_id);

protected:
  BPBContext *_context;
  string _name;
  union {
    short _type;
    char _type_code[2];
  };
};

#include "bpbID.I"

#endif

