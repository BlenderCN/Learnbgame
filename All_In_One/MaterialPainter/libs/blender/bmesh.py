'''BMesh mesh manipulations (bmesh)
   This module provides access to blenders bmesh data structures.
   .. include:: include__bmesh.rst
   
'''


def from_edit_mesh(mesh):
   '''Return a BMesh from this mesh, currently the mesh must already be in editmode.
      
      Arguments:
      @mesh (bpy.types.Mesh): The editmode mesh.

      @returns (bmesh.types.BMesh): the BMesh associated with this mesh.
   '''

   return bmesh.types.BMesh

def new(use_operators=True):
   '''
      Arguments:
      @use_operators (bool): Support calling operators in :mod:bmesh.ops (uses some extra memory per vert/edge/face).

      @returns (bmesh.types.BMesh): Return a new, empty BMesh.
   '''

   return bmesh.types.BMesh

def update_edit_mesh(mesh, tessface=True, destructive=True):
   '''Update the mesh after changes to the BMesh in editmode, 
      optionally recalculating n-gon tessellation.
      
      Arguments:
      @mesh (bpy.types.Mesh): The editmode mesh.
      @tessface (boolean): Option to recalculate n-gon tessellation.
      @destructive (boolean): Use when geometry has been added or removed.

   '''

   pass

