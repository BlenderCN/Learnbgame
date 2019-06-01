// Filename: bpbID.I
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


////////////////////////////////////////////////////////////////////
//     Function: BPBID::get_context
//       Access: Public
//  Description: Returns the context object.
////////////////////////////////////////////////////////////////////
INLINE BPBContext *BPBID::
get_context() const {
  return _context;
}
