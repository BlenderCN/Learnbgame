// Filename: bpbWindowRenderer.h
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

#ifndef BPBWINDOWRENDERER_H
#define BPBWINDOWRENDERER_H

#include "bpbRenderer.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBWindowRenderer
// Description : This type of renderer renders to an external window.
////////////////////////////////////////////////////////////////////
struct BPBWindowRenderer : public BPBRenderer {
public:
  BPBWindowRenderer(int flags);

public:
  virtual void start(const BPB_render_desc &desc);
  virtual void finish();

protected:
  PT(GraphicsWindow) _window;
};

#endif

