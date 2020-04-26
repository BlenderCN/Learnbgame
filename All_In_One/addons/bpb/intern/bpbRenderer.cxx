// Filename: bpbRenderer.cxx
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

#include "bpbRenderer.h"

#include "graphicsEngine.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBRenderer::Constructor
//       Access: Protected
//  Description:
////////////////////////////////////////////////////////////////////
BPBRenderer::
BPBRenderer(int flags) : _flags(flags) {
  GraphicsEngine::local_object();
}
