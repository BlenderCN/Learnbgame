// Filename: bpbContext.I
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
//     Function: BPBContext::Constructor
//       Access: Public
//  Description: Creates a context with the given API version.
////////////////////////////////////////////////////////////////////
INLINE BPBContext::
BPBContext(int api_version) : _api_version(api_version) {
}

////////////////////////////////////////////////////////////////////
//     Function: BPBContext::get_api_version
//       Access: Public
//  Description: Returns the API version of this context.
////////////////////////////////////////////////////////////////////
INLINE int BPBContext::
get_api_version() const {
  return _api_version;
}
