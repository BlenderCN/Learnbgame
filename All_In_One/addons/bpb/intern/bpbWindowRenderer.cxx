// Filename: bpbWindowRenderer.cxx
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

#include "bpbWindowRenderer.h"

#include "frameBufferProperties.h"
#include "graphicsEngine.h"
#include "graphicsPipeSelection.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBWindowRenderer::Constructor
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
BPBWindowRenderer::
BPBWindowRenderer(int flags) : BPBRenderer(flags) {
}

////////////////////////////////////////////////////////////////////
//     Function: BPBWindowRenderer::start
//       Access: Public
//  Description: Starts the render.  In foreground mode, this just
//               does initial set-up.  In background mode, it also
//               starts the render in a separate thread.
////////////////////////////////////////////////////////////////////
void BPBWindowRenderer::
start(const BPB_render_desc &desc) {
}

////////////////////////////////////////////////////////////////////
//     Function: BPBWindowRenderer::finish
//       Access: Public
//  Description: Finishes the render.  In foreground mode, this does
//               the entire rendering.  In background mode, it waits
//               for the render to finish.
////////////////////////////////////////////////////////////////////
void BPBWindowRenderer::
finish() {
}
