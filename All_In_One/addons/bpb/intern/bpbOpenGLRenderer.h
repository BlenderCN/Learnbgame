// Filename: bpbOpenGLRenderer.h
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

#ifndef BPBOPENGLRENDERER_H
#define BPBOPENGLRENDERER_H

#include "bpbRenderer.h"

#include "graphicsPipe.h"
#include "graphicsStateGuardian.h"
#include "graphicsWindow.h"
#include "sceneSetup.h"

////////////////////////////////////////////////////////////////////
//       Class : BPBOpenGLRenderer
// Description : This renderer renders into an existing OpenGL
//               context.
////////////////////////////////////////////////////////////////////
struct BPBOpenGLRenderer : public BPBRenderer, public GraphicsWindow {
public:
  BPBOpenGLRenderer(int flags);

public:
  virtual void start(const BPB_render_desc &desc);
  virtual void finish();

private:
  static GraphicsPipe *get_pipe();

  virtual bool begin_frame(FrameMode mode, Thread *current_thread);
  virtual void end_frame(FrameMode mode, Thread *current_thread);
  virtual bool open_window();

protected:
  SceneSetup _scene;
  PT(DisplayRegion) _region;
};

#endif

