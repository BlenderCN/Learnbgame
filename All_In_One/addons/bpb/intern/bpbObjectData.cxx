// Filename: bpbObjectData.cxx
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

#include "bpbObjectData.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBObjectData::Destructor
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
BPBObjectData::
~BPBObjectData() {
  // We should have been disassociated with all objects by now.
  Objects::iterator it;
  for (it = _objects.begin(); it != _objects.end(); ++it) {
    //TODO: better error handling.
    BPBObject *object = (*it);
    cerr << "Destroying BPBObjectData which is still associated with objects.\n";
    if (object->get_data() == this) {
      object->set_data(NULL);
    } else {
      cerr << "Internal error.\n";
    }
  }
}

////////////////////////////////////////////////////////////////////
//     Function: BPBObjectData::update
//       Access: Public, Virtual
//  Description: Called by the bridge when the corresponding Blender
//               object might have changed.
////////////////////////////////////////////////////////////////////
void BPBObjectData::
update(DNA_ID *dna_id) {
  // The default implementation simply defers to update_node.  This
  // is useful for datablocks that don't have a separate object in
  // Panda (ie. lights), and the relevant properties are specified
  // on the node instead.
  Objects::iterator it;
  for (it = _objects.begin(); it != _objects.end(); ++it) {
    update_node((*it)->get_node(), dna_id);
  }
}

////////////////////////////////////////////////////////////////////
//     Function: BPBObjectData::update_node
//       Access: Public, Virtual
//  Description: This is called by the base implementation of update()
//               for each object that references this data block.
//               This method should be overridden to make whatever
//               changes need to be done to the node.
////////////////////////////////////////////////////////////////////
void BPBObjectData::
update_node(PandaNode *node, DNA_ID *dna_id) {
}
