#define MDLMESH_PARSER_VERSION "mdlmesh_parser Version 1.00  2/27/2008\n"

#include <limits.h>
#include "vector.h"

typedef unsigned char byte;

#define ALL_SIDES INT_MAX

/* Object Type Flags */
enum object_type_t
{
  META_OBJ,     /* Meta-object: aggregation of other objects */
  BOX_OBJ,      /* Box object: Polygonalized cuboid */
  POLY_OBJ,     /* Polygon list object: list of arbitrary triangles */
  REL_SITE_OBJ, /* Release site object */
  VOXEL_OBJ,    /* Voxel object (so-far unused) */
};

struct object {
  char *name;
  struct object *next;  // Next sibling object
  struct object *parent;  // Parent meta object
  struct object *first_child;  // First child object
  struct object *last_child;  // Last child object
  enum object_type_t object_type; // Object Type Flag
  int n_verts;
  int n_faces;
  struct vertex_list **vertices;
  struct polygon_list **faces;
  struct region_list *regions;
  double t_matrix[4][4];
};

struct polygon_list {
  int polygon_id;
  int polygon_index;
  struct polygon *polygon;
  struct polygon_list *next;
};

struct polygon {
  int n_verts;
  int vertex_index[4];
};

struct vertex_list {
  int vertex_id;
  int vertex_index;
  struct vector3 *vertex;
  struct vector3 *normal;
  struct vertex_list *next; 
};

struct region_list {
  char *name;
  int n_elements;
  int *elements;
  int viz_value;
  struct region_list *next;
};

struct object *mdl_parser(char *filename);
