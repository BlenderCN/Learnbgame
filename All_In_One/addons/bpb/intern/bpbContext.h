// Filename: bpbContext.h
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

#ifndef BPBCONTEXT_H
#define BPBCONTEXT_H

#include "pandaNode.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBContext
// Description : This is the implementation of BPB_context.
//               It manages all of the state that an instance of the
//               Blender->Panda3D pipeline might use.
////////////////////////////////////////////////////////////////////
struct BPBContext {
public:
  INLINE BPBContext(int api_version);

  INLINE int get_api_version() const;

private:
  int _api_version;
  PT(PandaNode) _root;
};

#include "bpbContext.I"

#endif

