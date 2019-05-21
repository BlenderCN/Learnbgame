// Filename: bpbOpenGLRenderer.cxx
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

#include "bpbOpenGLRenderer.h"

#include "depthTestAttrib.h"
#include "depthWriteAttrib.h"
#include "frameBufferProperties.h"
#include "graphicsEngine.h"
#include "graphicsPipeSelection.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::Constructor
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
BPBOpenGLRenderer::
BPBOpenGLRenderer(int flags) :
  BPBRenderer(flags),
  GraphicsWindow(this, get_pipe(),
                 "BPB OpenGL Viewport", FrameBufferProperties(),
                 WindowProperties(), 0, NULL, NULL) {

  _properties.set_open(false);
  _properties.set_undecorated(true);
  _properties.set_minimized(false);
  _properties.set_cursor_hidden(false);

  _fb_properties.set_rgb_color(true);
  _fb_properties.set_color_bits(24);
  _fb_properties.set_alpha_bits(8);
  _fb_properties.set_back_buffers(1);

  // Always render into the back buffer.
  _draw_buffer_type = RenderBuffer::T_back;

  _region = make_mono_display_region();

  // Tell Panda that we'll take care of the lifetime of this object
  // ourselves.
  GraphicsWindow::local_object();

  disable_clears();
  add_window(this, 0);
}

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::start
//       Access: Public
//  Description: Starts the render.  In foreground mode, this just
//               does initial set-up.  In background mode, it also
//               starts the render in a separate thread.
////////////////////////////////////////////////////////////////////
void BPBOpenGLRenderer::
start(const BPB_render_desc &desc) {
  _fb_properties.set_srgb_color((_flags & BPB_RF_srgb) != 0);

  WindowProperties props;
  props.set_origin(0, 0);
  props.set_size(desc.width, desc.height);

  system_changed_properties(props);

  // Compute the size of the display region.
  LVecBase4 dimensions(desc.region_x, desc.region_x + desc.region_width,
                       desc.region_y, desc.region_y + desc.region_height);

  LVecBase2 pixel_scale(1.0f / desc.width, 1.0f / desc.height);
  dimensions[0] *= pixel_scale[0];
  dimensions[1] *= pixel_scale[0];
  dimensions[2] *= pixel_scale[1];
  dimensions[3] *= pixel_scale[1];
  _region->set_dimensions(dimensions);

  _region->set_clear_color(LColor(0.2f, 0, 0, 1));
  _region->set_clear_color_active(true);
  _region->set_clear_depth(1);
  _region->set_clear_depth_active(true);
  _region->set_active(true);

  // This is all a test set-up.
  NodePath render("render");

  NodePath cam = render.attach_new_node(new Camera("aaaa"));
  DCAST(Camera, cam.node())->set_active(true);
  _region->set_camera(cam);

  render_frame();
}

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::finish
//       Access: Public
//  Description: Finishes the render.  In foreground mode, this does
//               the entire rendering.  In background mode, it waits
//               for the render to finish.
////////////////////////////////////////////////////////////////////
void BPBOpenGLRenderer::
finish() {
  sync_frame();
}

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::get_pipe
//       Access: Private, Static
//  Description: Returns the global OpenGL GraphicsPipe object.
////////////////////////////////////////////////////////////////////
GraphicsPipe *BPBOpenGLRenderer::
get_pipe() {
  static PT(GraphicsPipe) pipe = NULL;
  // Select the pandagl pipe.
  if (pipe == NULL) {
    GraphicsPipeSelection *sel = GraphicsPipeSelection::get_global_ptr();
    sel->print_pipe_types();
    pipe = sel->make_module_pipe("pandagl");
    nassertr(pipe != NULL, NULL);
  }
  return pipe;
}

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::begin_frame
//       Access: Private, Virtual
//  Description: This function will be called within the draw thread
//               before beginning rendering for a given frame.  It
//               should do whatever setup is required, and return true
//               if the frame should be rendered, or false if it
//               should be skipped.
////////////////////////////////////////////////////////////////////
bool BPBOpenGLRenderer::
begin_frame(FrameMode mode, Thread *current_thread) {
  _gsg->reset_if_new();
  _gsg->set_current_properties(&get_fb_properties());

  return _gsg->begin_frame(current_thread);
}

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::end_frame
//       Access: Private, Virtual
//  Description: This function will be called within the draw thread
//               after rendering is completed for a given frame.  It
//               should do whatever finalization is required.
////////////////////////////////////////////////////////////////////
void BPBOpenGLRenderer::
end_frame(FrameMode mode, Thread *current_thread) {
  GraphicsWindow::end_frame(mode, current_thread);
  _gsg->end_frame(current_thread);
  _gsg->clear_before_callback();
}

////////////////////////////////////////////////////////////////////
//     Function: BPBOpenGLRenderer::open_window
//       Access: Private, Virtual
//  Description: Opens the window right now.  Called from the window
//               thread.  Returns true if the window is successfully
//               opened, or false if there was a problem.
////////////////////////////////////////////////////////////////////
bool BPBOpenGLRenderer::
open_window() {
  if (_gsg == NULL) {
    // Create a nice GSG for ourselves.
    _gsg = get_pipe()->make_callback_gsg(this);
  }
  return true;
}
