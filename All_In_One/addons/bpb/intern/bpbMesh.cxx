// Filename: bpbMesh.cxx
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

#include "bpbMesh.h"

#include "geomNode.h"
#include "geomTriangles.h"
#include "geomVertexWriter.h"

#define __bool_true_false_are_defined 1
#include "DNA_mesh_types.h"
#include "DNA_meshdata_types.h"

////////////////////////////////////////////////////////////////////
//     Function: BPBMesh::update
//       Access: Public, Virtual
//  Description: Called by the bridge when the corresponding Blender
//               object might have changed.
////////////////////////////////////////////////////////////////////
void BPBMesh::
update(DNA_ID *dna_id) {
  Mesh *mesh = (Mesh *)dna_id;

  PT(GeomVertexData) vdata = new GeomVertexData("NAME", GeomVertexFormat::get_v3n3(),
                                                GeomEnums::UH_stream);
  vdata->unclean_set_num_rows(mesh->totloop);

  GeomVertexWriter vertex(vdata, InternalName::get_vertex());
  GeomVertexWriter normal(vdata, InternalName::get_normal());

  // Build up the vertex table.
  for (int i = 0; i < mesh->totloop; ++i) {
    const MLoop &loop = mesh->mloop[i];
    const MVert &vert = mesh->mvert[loop.v];
    vertex.add_data3f(vert.co[0], vert.co[1], vert.co[2]);
    normal.add_data3f(vert.no[0] * (1.0f / 32767.0f),
                      vert.no[1] * (1.0f / 32767.0f),
                      vert.no[2] * (1.0f / 32767.0f));
  }

  // Build up the triangle definitions.
  PT(GeomTriangles) prim = new GeomTriangles(GeomEnums::UH_static);
  for (int i = 0; i < mesh->totpoly; ++i) {
    const MPoly &poly = mesh->mpoly[i];
    int first = poly.loopstart;

    if (poly.totloop == 3) {
      prim->add_vertices(first, first + 1, first + 2);

    } else if (poly.totloop > 3) {
      // Triangulate.
      int last = first + poly.totloop - 1;
      for (int j = first; j < last; ++j) {
        prim->add_vertices(last, j, j + 1);
      }
    }
  }

  PT(Geom) geom = new Geom(vdata);
  geom->add_primitive(prim);
  _geom = geom;

  //FIXME: update_node should be called *after*, but _name should be
  // known *before*
  BPBObjectData::update(dna_id);
}

////////////////////////////////////////////////////////////////////
//     Function: BPBMesh::update_node
//       Access: Public, Virtual
//  Description: This is called by the base implementation of update()
//               for each object that references this data block.
//               This method should be overridden to make whatever
//               changes need to be done to the node.
////////////////////////////////////////////////////////////////////
void BPBMesh::
update_node(PandaNode *node, DNA_ID *dna_id) {
  GeomNode *gnode;
  DCAST_INTO_V(gnode, node);

  gnode->remove_all_geoms();
  gnode->add_geom(_geom.get_write_pointer());
}
