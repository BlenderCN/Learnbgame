'''BMesh mesh manipulations types (bmesh.types)
   
'''


class BMDeformVert:
   

   def clear():
      '''Clears all weights.
         
      '''
   
      pass
   

   def get(key, default=None):
      '''Returns the deform weight matching the key or default
         when not found (matches pythons dictionary function of the same name).
         
         Arguments:
         @key (int): The key associated with deform weight.
         @default (Undefined): Optional argument for the value to return if*key* is not found.
         
   
      '''
   
      pass
   

   def items():
      '''Return (group, weight) pairs for this vertex
         (matching pythons dict.items() functionality).
         
         @returns (list of tuples): (key, value) pairs for each deform weight of this vertex.
      '''
   
      return list of tuples
   

   def keys():
      '''Return the group indices used by this vertex
         (matching pythons dict.keys() functionality).
         
         @returns (list of ints): the deform group this vertex uses
      '''
   
      return list of ints
   

   def values():
      '''Return the weights of the deform vertex
         (matching pythons dict.values() functionality).
         
         @returns (list of floats): The weights that influence this vertex
      '''
   
      return list of floats
   



class BMEdge:
   '''The BMesh edge connecting 2 verts
      
   '''

   def calc_face_angle(fallback=None):
      '''
         Arguments:
         @fallback (any): return this when the edge doesn't have 2 faces(instead of raising a ValueError).
         
   
         @returns (float): The angle between 2 connected faces in radians.
      '''
   
      return float
   

   def calc_face_angle_signed(fallback=None):
      '''
         Arguments:
         @fallback (any): return this when the edge doesn't have 2 faces(instead of raising a ValueError).
         
   
         @returns (float): The angle between 2 connected faces in radians (negative for concave join).
      '''
   
      return float
   

   def calc_length():
      '''
         @returns (float): The length between both verts.
      '''
   
      return float
   

   def calc_tangent(loop):
      '''Return the tangent at this edge relative to a face (pointing inward into the face).
         This uses the face normal for calculation.
         
         Arguments:
         @loop (BMLoop): The loop used for tangent calculation.
   
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def copy_from(other):
      '''Copy values from another element of matching type.
         
      '''
   
      pass
   

   def hide_set(hide):
      '''Set the hide state.
         This is different from the *hide* attribute because it updates the selection and hide state of associated geometry.
         
         Arguments:
         @hide (boolean): Hidden or visible.
   
      '''
   
      pass
   

   def normal_update():
      '''Update edges vertex normals.
         
      '''
   
      pass
   

   def other_vert(vert):
      '''Return the other vertex on this edge or None if the vertex is not used by this edge.
         
         Arguments:
         @vert (BMVert): a vert in this edge.
   
         @returns (BMVert or None): The edges other vert.
      '''
   
      return BMVert or None
   

   def select_set(select):
      '''Set the selection.
         This is different from the *select* attribute because it updates the selection state of associated geometry.
         
         Arguments:
         @select (boolean): Select or de-select... note::
         Currently this only flushes down, so selecting a face will select all its vertices but de-selecting a vertex       won't de-select all the faces that use it, before finishing with a mesh typically flushing is still needed.
         
   
      '''
   
      pass
   

   hide = bool
   '''Hidden state of this element.
      
   '''
   

   index = int
   '''Index of this element.
      .. note::
      This value is not necessarily valid, while editing the mesh it can become *dirty*.
      It's also possible to assign any number to this attribute for a scripts internal logic.
      To ensure the value is up to date - see BMElemSeq.index_update.
      
   '''
   

   is_boundary = bool
   '''True when this edge is at the boundary of a face (read-only).
      
   '''
   

   is_contiguous = bool
   '''True when this edge is manifold, between two faces with the same winding (read-only).
      
   '''
   

   is_convex = bool
   '''True when this edge joins two convex faces, depends on a valid face normal (read-only).
      
   '''
   

   is_manifold = bool
   '''True when this edge is manifold (read-only).
      
   '''
   

   is_valid = bool
   '''True when this element is valid (hasn't been removed).
      
   '''
   

   is_wire = bool
   '''True when this edge is not connected to any faces (read-only).
      
   '''
   

   link_faces = BMElemSeq of BMFace
   '''Faces connected to this edge, (read-only).
      
   '''
   

   link_loops = BMElemSeq of BMLoop
   '''Loops connected to this edge, (read-only).
      
   '''
   

   seam = bool
   '''Seam for UV unwrapping.
      
   '''
   

   select = bool
   '''Selected state of this element.
      
   '''
   

   smooth = bool
   '''Smooth state of this element.
      
   '''
   

   tag = bool
   '''Generic attribute scripts can use for own logic
      
   '''
   

   verts = BMElemSeq of BMVert
   '''Verts this edge uses (always 2), (read-only).
      
   '''
   



class BMEdgeSeq:
   

   def ensure_lookup_table():
      '''Ensure internal data needed for int subscription is initialized with verts/edges/faces, eg bm.verts[index].
         This needs to be called again after adding/removing data in this sequence.
         
      '''
   
      pass
   

   def get(verts, fallback=None):
      '''Return an edge which uses the **verts** passed.
         
         Arguments:
         @verts (BMVert): Sequence of verts.
         @fallback: Return this value if nothing is found.
   
         @returns (BMEdge): The edge found or None
      '''
   
      return BMEdge
   

   def index_update():
      '''Initialize the index values of this sequence.
         This is the equivalent of looping over all elements and assigning the index values.
         .. code-block:: python
         for index, ele in enumerate(sequence):
         ele.index = index
         .. note::
         Running this on sequences besides BMesh.verts, BMesh.edges, BMesh.faces
         works but wont result in each element having a valid index, insted its order in the sequence will be set.
         
      '''
   
      pass
   

   def new(verts, example=None):
      '''Create a new edge from a given pair of verts.
         
         Arguments:
         @verts (pair of BMVert): Vertex pair.
         @example (BMEdge): Existing edge to initialize settings (optional argument).
   
         @returns (BMEdge): The newly created edge.
      '''
   
      return BMEdge
   

   def remove(edge):
      '''Remove an edge.
         
      '''
   
      pass
   

   def sort(key=None, reverse=False):
      '''Sort the elements of this sequence, using an optional custom sort key.
         Indices of elements are not changed, BMElemeSeq.index_update() can be used for that.
         
         Arguments:
         @key (:function: returning a number): The key that sets the ordering of the elements.
         @reverse (:boolean:): Reverse the order of the elements.. note::
         When the 'key' argument is not provided, the elements are reordered following their current index value.
         In particular this can be used by setting indices manually before calling this method.
         .. warning::
         Existing references to the N'th element, will continue to point the data at that index.
         
   
      '''
   
      pass
   

   layers = BMLayerAccessEdge
   '''custom-data layers (read-only).
      
   '''
   



class BMEditSelIter:
   



class BMEditSelSeq:
   

   def add(element):
      '''Add an element to the selection history (no action taken if its already added).
         
      '''
   
      pass
   

   def clear():
      '''Empties the selection history.
         
      '''
   
      pass
   

   def discard(element):
      '''Discard an element from the selection history.
         Like remove but doesn't raise an error when the elements not in the selection list.
         
      '''
   
      pass
   

   def remove(element):
      '''Remove an element from the selection history.
         
      '''
   
      pass
   

   def validate():
      '''Ensures all elements in the selection history are selected.
         
      '''
   
      pass
   

   active = BMVert, BMEdge or BMFace
   '''The last selected element or None (read-only).
      
   '''
   



class BMElemSeq:
   '''General sequence type used for accessing any sequence of 
      BMVert, BMEdge, BMFace, BMLoop.
      When accessed via BMesh.verts, BMesh.edges, BMesh.faces 
      there are also functions to create/remomove items.
      
   '''

   def index_update():
      '''Initialize the index values of this sequence.
         This is the equivalent of looping over all elements and assigning the index values.
         .. code-block:: python
         for index, ele in enumerate(sequence):
         ele.index = index
         .. note::
         Running this on sequences besides BMesh.verts, BMesh.edges, BMesh.faces
         works but wont result in each element having a valid index, insted its order in the sequence will be set.
         
      '''
   
      pass
   



class BMFace:
   '''The BMesh face with 3 or more sides
      
   '''

   def calc_area():
      '''Return the area of the face.
         
         @returns (float): Return the area of the face.
      '''
   
      return float
   

   def calc_center_bounds():
      '''Return bounds center of the face.
         
         @returns (mathutils.Vector): a 3D vector.
      '''
   
      return mathutils.Vector
   

   def calc_center_median():
      '''Return median center of the face.
         
         @returns (mathutils.Vector): a 3D vector.
      '''
   
      return mathutils.Vector
   

   def calc_center_median_weighted():
      '''Return median center of the face weighted by edge lengths.
         
         @returns (mathutils.Vector): a 3D vector.
      '''
   
      return mathutils.Vector
   

   def calc_perimeter():
      '''Return the perimeter of the face.
         
         @returns (float): Return the perimeter of the face.
      '''
   
      return float
   

   def calc_tangent_edge():
      '''Return face tangent based on longest edge.
         
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def calc_tangent_edge_diagonal():
      '''Return face tangent based on the edge farthest from any vertex.
         
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def calc_tangent_edge_pair():
      '''Return face tangent based on the two longest disconnected edges.
         - Tris: Use the edge pair with the most similar lengths.
         - Quads: Use the longest edge pair.
         - NGons: Use the two longest disconnected edges.
         
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def calc_tangent_vert_diagonal():
      '''Return face tangent based on the two most distent vertices.
         
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def copy(verts=True, edges=True):
      '''Make a copy of this face.
         
         Arguments:
         @verts (boolean): When set, the faces verts will be duplicated too.
         @edges (boolean): When set, the faces edges will be duplicated too.
   
         @returns (BMFace): The newly created face.
      '''
   
      return BMFace
   

   def copy_from(other):
      '''Copy values from another element of matching type.
         
      '''
   
      pass
   

   def copy_from_face_interp(face, vert=True):
      '''Interpolate the customdata from another face onto this one (faces should overlap).
         
         Arguments:
         @face (BMFace): The face to interpolate data from.
         @vert (boolean): When True, also copy vertex data.
   
      '''
   
      pass
   

   def hide_set(hide):
      '''Set the hide state.
         This is different from the *hide* attribute because it updates the selection and hide state of associated geometry.
         
         Arguments:
         @hide (boolean): Hidden or visible.
   
      '''
   
      pass
   

   def normal_flip():
      '''Reverses winding of a face, which flips its normal.
         
      '''
   
      pass
   

   def normal_update():
      '''Update face's normal.
         
      '''
   
      pass
   

   def select_set(select):
      '''Set the selection.
         This is different from the *select* attribute because it updates the selection state of associated geometry.
         
         Arguments:
         @select (boolean): Select or de-select... note::
         Currently this only flushes down, so selecting a face will select all its vertices but de-selecting a vertex       won't de-select all the faces that use it, before finishing with a mesh typically flushing is still needed.
         
   
      '''
   
      pass
   

   edges = BMElemSeq of BMEdge
   '''Edges of this face, (read-only).
      
   '''
   

   hide = bool
   '''Hidden state of this element.
      
   '''
   

   index = int
   '''Index of this element.
      .. note::
      This value is not necessarily valid, while editing the mesh it can become *dirty*.
      It's also possible to assign any number to this attribute for a scripts internal logic.
      To ensure the value is up to date - see BMElemSeq.index_update.
      
   '''
   

   is_valid = bool
   '''True when this element is valid (hasn't been removed).
      
   '''
   

   loops = BMElemSeq of BMLoop
   '''Loops of this face, (read-only).
      
   '''
   

   material_index = int
   '''The face's material index.
      
   '''
   

   normal = mathutils.Vector
   '''The normal for this face as a 3D, wrapped vector.
      
   '''
   

   select = bool
   '''Selected state of this element.
      
   '''
   

   smooth = bool
   '''Smooth state of this element.
      
   '''
   

   tag = bool
   '''Generic attribute scripts can use for own logic
      
   '''
   

   verts = BMElemSeq of BMVert
   '''Verts of this face, (read-only).
      
   '''
   



class BMFaceSeq:
   

   def ensure_lookup_table():
      '''Ensure internal data needed for int subscription is initialized with verts/edges/faces, eg bm.verts[index].
         This needs to be called again after adding/removing data in this sequence.
         
      '''
   
      pass
   

   def get(verts, fallback=None):
      '''Return a face which uses the **verts** passed.
         
         Arguments:
         @verts (BMVert): Sequence of verts.
         @fallback: Return this value if nothing is found.
   
         @returns (BMFace): The face found or None
      '''
   
      return BMFace
   

   def index_update():
      '''Initialize the index values of this sequence.
         This is the equivalent of looping over all elements and assigning the index values.
         .. code-block:: python
         for index, ele in enumerate(sequence):
         ele.index = index
         .. note::
         Running this on sequences besides BMesh.verts, BMesh.edges, BMesh.faces
         works but wont result in each element having a valid index, insted its order in the sequence will be set.
         
      '''
   
      pass
   

   def new(verts, example=None):
      '''Create a new face from a given set of verts.
         
         Arguments:
         @verts (BMVert): Sequence of 3 or more verts.
         @example (BMFace): Existing face to initialize settings (optional argument).
   
         @returns (BMFace): The newly created face.
      '''
   
      return BMFace
   

   def remove(face):
      '''Remove a face.
         
      '''
   
      pass
   

   def sort(key=None, reverse=False):
      '''Sort the elements of this sequence, using an optional custom sort key.
         Indices of elements are not changed, BMElemeSeq.index_update() can be used for that.
         
         Arguments:
         @key (:function: returning a number): The key that sets the ordering of the elements.
         @reverse (:boolean:): Reverse the order of the elements.. note::
         When the 'key' argument is not provided, the elements are reordered following their current index value.
         In particular this can be used by setting indices manually before calling this method.
         .. warning::
         Existing references to the N'th element, will continue to point the data at that index.
         
   
      '''
   
      pass
   

   active = BMFace or None
   '''active face.
      
   '''
   

   layers = BMLayerAccessFace
   '''custom-data layers (read-only).
      
   '''
   



class BMIter:
   '''Internal BMesh type for looping over verts/faces/edges,
      used for iterating over BMElemSeq types.
      
   '''



class BMLayerAccessEdge:
   '''Exposes custom-data layer attributes.
      
   '''

   bevel_weight = BMLayerCollection
   '''Bevel weight float in [0 - 1].
      
   '''
   

   crease = BMLayerCollection
   '''Edge crease for subsurf - float in [0 - 1].
      
   '''
   

   float = None
   '''Generic float custom-data layer.
      type: BMLayerCollection
      
   '''
   

   freestyle = None
   '''Accessor for Freestyle edge layer.
      type: BMLayerCollection
      
   '''
   

   int = None
   '''Generic int custom-data layer.
      type: BMLayerCollection
      
   '''
   

   string = None
   '''Generic string custom-data layer (exposed as bytes, 255 max length).
      type: BMLayerCollection
      
   '''
   



class BMLayerAccessFace:
   '''Exposes custom-data layer attributes.
      
   '''

   float = None
   '''Generic float custom-data layer.
      type: BMLayerCollection
      
   '''
   

   freestyle = None
   '''Accessor for Freestyle face layer.
      type: BMLayerCollection
      
   '''
   

   int = None
   '''Generic int custom-data layer.
      type: BMLayerCollection
      
   '''
   

   string = None
   '''Generic string custom-data layer (exposed as bytes, 255 max length).
      type: BMLayerCollection
      
   '''
   

   tex = None
   '''Accessor for BMTexPoly layer (TODO).
      type: BMLayerCollection
      
   '''
   



class BMLayerAccessLoop:
   '''Exposes custom-data layer attributes.
      
   '''

   color = None
   '''Accessor for vertex color layer.
      type: BMLayerCollection
      
   '''
   

   float = None
   '''Generic float custom-data layer.
      type: BMLayerCollection
      
   '''
   

   int = None
   '''Generic int custom-data layer.
      type: BMLayerCollection
      
   '''
   

   string = None
   '''Generic string custom-data layer (exposed as bytes, 255 max length).
      type: BMLayerCollection
      
   '''
   

   uv = None
   '''Accessor for BMLoopUV UV (as a 2D Vector).
      type: BMLayerCollection
      
   '''
   



class BMLayerAccessVert:
   '''Exposes custom-data layer attributes.
      
   '''

   bevel_weight = BMLayerCollection
   '''Bevel weight float in [0 - 1].
      
   '''
   

   deform = None
   '''Vertex deform weight BMDeformVert (TODO).
      type: BMLayerCollection
      
   '''
   

   float = None
   '''Generic float custom-data layer.
      type: BMLayerCollection
      
   '''
   

   int = None
   '''Generic int custom-data layer.
      type: BMLayerCollection
      
   '''
   

   paint_mask = None
   '''Accessor for paint mask layer.
      type: BMLayerCollection
      
   '''
   

   shape = BMLayerCollection
   '''Vertex shapekey absolute location (as a 3D Vector).
      
   '''
   

   skin = None
   '''Accessor for skin layer.
      type: BMLayerCollection
      
   '''
   

   string = None
   '''Generic string custom-data layer (exposed as bytes, 255 max length).
      type: BMLayerCollection
      
   '''
   



class BMLayerCollection:
   '''Gives access to a collection of custom-data layers of the same type and behaves like python dictionaries, except for the ability to do list like index access.
      
   '''

   def get(key, default=None):
      '''Returns the value of the layer matching the key or default
         when not found (matches pythons dictionary function of the same name).
         
         Arguments:
         @key (string): The key associated with the layer.
         @default (Undefined): Optional argument for the value to return if*key* is not found.
         
   
      '''
   
      pass
   

   def items():
      '''Return the identifiers of collection members
         (matching pythons dict.items() functionality).
         
         @returns (list of tuples): (key, value) pairs for each member of this collection.
      '''
   
      return list of tuples
   

   def keys():
      '''Return the identifiers of collection members
         (matching pythons dict.keys() functionality).
         
         @returns ([str]): the identifiers for each member of this collection.
      '''
   
      return [str]
   

   def new(name):
      '''Create a new layer
         
         Arguments:
         @name (string): Optional name argument (will be made unique).
   
         @returns (BMLayerItem): The newly created layer.
      '''
   
      return BMLayerItem
   

   def remove(layer):
      '''Remove a layer
         
         Arguments:
         @layer (BMLayerItem): The layer to remove.
   
      '''
   
      pass
   

   def values():
      '''Return the values of collection
         (matching pythons dict.values() functionality).
         
         @returns (list): the members of this collection.
      '''
   
      return list
   

   def verify():
      '''Create a new layer or return an existing active layer
         
         @returns (BMLayerItem): The newly verified layer.
      '''
   
      return BMLayerItem
   

   active = BMLayerItem
   '''The active layer of this type (read-only).
      
   '''
   

   is_singleton = bool
   '''True if there can exists only one layer of this type (read-only).
      
   '''
   



class BMLayerItem:
   '''Exposes a single custom data layer, their main purpose is for use as item accessors to custom-data when used with vert/edge/face/loop data.
      
   '''

   def copy_from(other):
      '''Return a copy of the layer
         
         Arguments:
         @other: Another layer to copy from.
   
      '''
   
      pass
   

   name = str
   '''The layers unique name (read-only).
      
   '''
   



class BMLoop:
   '''This is normally accessed from BMFace.loops where each face loop represents a corner of the face.
      
   '''

   def calc_angle():
      '''Return the angle at this loops corner of the face.
         This is calculated so sharper corners give lower angles.
         
         @returns (float): The angle in radians.
      '''
   
      return float
   

   def calc_normal():
      '''Return normal at this loops corner of the face.
         Falls back to the face normal for straight lines.
         
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def calc_tangent():
      '''Return the tangent at this loops corner of the face (pointing inward into the face).
         Falls back to the face normal for straight lines.
         
         @returns (mathutils.Vector): a normalized vector.
      '''
   
      return mathutils.Vector
   

   def copy_from(other):
      '''Copy values from another element of matching type.
         
      '''
   
      pass
   

   def copy_from_face_interp(face, vert=True, multires=True):
      '''Interpolate the customdata from a face onto this loop (the loops vert should overlap the face).
         
         Arguments:
         @face (BMFace): The face to interpolate data from.
         @vert (boolean): When enabled, interpolate the loops vertex data (optional).
         @multires (boolean): When enabled, interpolate the loops multires data (optional).
   
      '''
   
      pass
   

   edge = BMEdge
   '''The loop's edge (between this loop and the next), (read-only).
      
   '''
   

   face = BMFace
   '''The face this loop makes (read-only).
      
   '''
   

   index = int
   '''Index of this element.
      .. note::
      This value is not necessarily valid, while editing the mesh it can become *dirty*.
      It's also possible to assign any number to this attribute for a scripts internal logic.
      To ensure the value is up to date - see BMElemSeq.index_update.
      
   '''
   

   is_convex = bool
   '''True when this loop is at the convex corner of a face, depends on a valid face normal (read-only).
      
   '''
   

   is_valid = bool
   '''True when this element is valid (hasn't been removed).
      
   '''
   

   link_loop_next = BMLoop
   '''The next face corner (read-only).
      
   '''
   

   link_loop_prev = BMLoop
   '''The previous face corner (read-only).
      
   '''
   

   link_loop_radial_next = BMLoop
   '''The next loop around the edge (read-only).
      
   '''
   

   link_loop_radial_prev = BMLoop
   '''The previous loop around the edge (read-only).
      
   '''
   

   link_loops = BMElemSeq of BMLoop
   '''Loops connected to this loop, (read-only).
      
   '''
   

   tag = bool
   '''Generic attribute scripts can use for own logic
      
   '''
   

   vert = BMVert
   '''The loop's vertex (read-only).
      
   '''
   



class BMLoopSeq:
   

   layers = BMLayerAccessLoop
   '''custom-data layers (read-only).
      
   '''
   



class BMLoopUV:
   

   pin_uv = bool
   '''UV pin state.
      
   '''
   

   select = bool
   '''UV select state.
      
   '''
   

   select_edge = bool
   '''UV edge select state.
      
   '''
   

   uv = mathutils.Vector
   '''Loops UV (as a 2D Vector).
      
   '''
   



class BMVert:
   '''The BMesh vertex type
      
   '''

   def calc_edge_angle(fallback=None):
      '''Return the angle between this vert's two connected edges.
         
         Arguments:
         @fallback (any): return this when the vert doesn't have 2 edges(instead of raising a ValueError).
         
   
         @returns (float): Angle between edges in radians.
      '''
   
      return float
   

   def calc_shell_factor():
      '''Return a multiplier calculated based on the sharpness of the vertex.
         Where a flat surface gives 1.0, and higher values sharper edges.
         This is used to maintain shell thickness when offsetting verts along their normals.
         
         @returns (float): offset multiplier
      '''
   
      return float
   

   def copy_from(other):
      '''Copy values from another element of matching type.
         
      '''
   
      pass
   

   def copy_from_face_interp(face):
      '''Interpolate the customdata from a face onto this loop (the loops vert should overlap the face).
         
         Arguments:
         @face (BMFace): The face to interpolate data from.
   
      '''
   
      pass
   

   def copy_from_vert_interp(vert_pair, fac):
      '''Interpolate the customdata from a vert between 2 other verts.
         
         Arguments:
         @vert_pair (BMVert): The vert to interpolate data from.
   
      '''
   
      pass
   

   def hide_set(hide):
      '''Set the hide state.
         This is different from the *hide* attribute because it updates the selection and hide state of associated geometry.
         
         Arguments:
         @hide (boolean): Hidden or visible.
   
      '''
   
      pass
   

   def normal_update():
      '''Update vertex normal.
         
      '''
   
      pass
   

   def select_set(select):
      '''Set the selection.
         This is different from the *select* attribute because it updates the selection state of associated geometry.
         
         Arguments:
         @select (boolean): Select or de-select... note::
         Currently this only flushes down, so selecting a face will select all its vertices but de-selecting a vertex       won't de-select all the faces that use it, before finishing with a mesh typically flushing is still needed.
         
   
      '''
   
      pass
   

   co = mathutils.Vector
   '''The coordinates for this vertex as a 3D, wrapped vector.
      
   '''
   

   hide = bool
   '''Hidden state of this element.
      
   '''
   

   index = int
   '''Index of this element.
      .. note::
      This value is not necessarily valid, while editing the mesh it can become *dirty*.
      It's also possible to assign any number to this attribute for a scripts internal logic.
      To ensure the value is up to date - see BMElemSeq.index_update.
      
   '''
   

   is_boundary = bool
   '''True when this vertex is connected to boundary edges (read-only).
      
   '''
   

   is_manifold = bool
   '''True when this vertex is manifold (read-only).
      
   '''
   

   is_valid = bool
   '''True when this element is valid (hasn't been removed).
      
   '''
   

   is_wire = bool
   '''True when this vertex is not connected to any faces (read-only).
      
   '''
   

   link_edges = BMElemSeq of BMEdge
   '''Edges connected to this vertex (read-only).
      
   '''
   

   link_faces = BMElemSeq of BMFace
   '''Faces connected to this vertex (read-only).
      
   '''
   

   link_loops = BMElemSeq of BMLoop
   '''Loops that use this vertex (read-only).
      
   '''
   

   normal = mathutils.Vector
   '''The normal for this vertex as a 3D, wrapped vector.
      
   '''
   

   select = bool
   '''Selected state of this element.
      
   '''
   

   tag = bool
   '''Generic attribute scripts can use for own logic
      
   '''
   



class BMVertSeq:
   

   def ensure_lookup_table():
      '''Ensure internal data needed for int subscription is initialized with verts/edges/faces, eg bm.verts[index].
         This needs to be called again after adding/removing data in this sequence.
         
      '''
   
      pass
   

   def index_update():
      '''Initialize the index values of this sequence.
         This is the equivalent of looping over all elements and assigning the index values.
         .. code-block:: python
         for index, ele in enumerate(sequence):
         ele.index = index
         .. note::
         Running this on sequences besides BMesh.verts, BMesh.edges, BMesh.faces
         works but wont result in each element having a valid index, insted its order in the sequence will be set.
         
      '''
   
      pass
   

   def new(co=(0.0, 0.0, 0.0), example=None):
      '''Create a new vertex.
         
         Arguments:
         @co (float triplet): The initial location of the vertex (optional argument).
         @example (BMVert): Existing vert to initialize settings.
   
         @returns (BMVert): The newly created edge.
      '''
   
      return BMVert
   

   def remove(vert):
      '''Remove a vert.
         
      '''
   
      pass
   

   def sort(key=None, reverse=False):
      '''Sort the elements of this sequence, using an optional custom sort key.
         Indices of elements are not changed, BMElemeSeq.index_update() can be used for that.
         
         Arguments:
         @key (:function: returning a number): The key that sets the ordering of the elements.
         @reverse (:boolean:): Reverse the order of the elements.. note::
         When the 'key' argument is not provided, the elements are reordered following their current index value.
         In particular this can be used by setting indices manually before calling this method.
         .. warning::
         Existing references to the N'th element, will continue to point the data at that index.
         
   
      '''
   
      pass
   

   layers = BMLayerAccessVert
   '''custom-data layers (read-only).
      
   '''
   



class BMesh:
   '''The BMesh data structure
      
   '''

   def calc_tessface():
      '''Calculate triangle tessellation from quads/ngons.
         
         @returns (list of BMLoop tuples): The triangulated faces.
      '''
   
      return list of BMLoop tuples
   

   def calc_volume(signed=False):
      '''Calculate mesh volume based on face normals.
         
         Arguments:
         @signed (bool): when signed is true, negative values may be returned.
   
         @returns (float): The volume of the mesh.
      '''
   
      return float
   

   def clear():
      '''Clear all mesh data.
         
      '''
   
      pass
   

   def copy():
      '''
         @returns (BMesh): A copy of this BMesh.
      '''
   
      return BMesh
   

   def free():
      '''Explicitly free the BMesh data from memory, causing exceptions on further access.
         .. note::
         The BMesh is freed automatically, typically when the script finishes executing.
         However in some cases its hard to predict when this will be and its useful to
         explicitly free the data.
         
      '''
   
      pass
   

   def from_mesh(mesh, face_normals=True, use_shape_key=False, shape_key_index=0):
      '''Initialize this bmesh from existing mesh datablock.
         
         Arguments:
         @mesh (Mesh): The mesh data to load.
         @use_shape_key (boolean): Use the locations from a shape key.
         @shape_key_index (int): The shape key index to use... note::
         Multiple calls can be used to join multiple meshes.
         Custom-data layers are only copied from mesh on initialization.
         Further calls will copy custom-data to matching layers, layers missing on the target mesh wont be added.
         
   
      '''
   
      pass
   

   def from_object(object, scene, deform=True, render=False, cage=False, face_normals=True):
      '''Initialize this bmesh from existing object datablock (currently only meshes are supported).
         
         Arguments:
         @object (Object): The object data to load.
         @deform (boolean): Apply deformation modifiers.
         @render (boolean): Use render settings.
         @cage (boolean): Get the mesh as a deformed cage.
         @face_normals (boolean): Calculate face normals.
   
      '''
   
      pass
   

   def normal_update():
      '''Update mesh normals.
         
      '''
   
      pass
   

   def select_flush(select):
      '''Flush selection, independent of the current selection mode.
         
         Arguments:
         @select (boolean): flush selection or de-selected elements.
   
      '''
   
      pass
   

   def select_flush_mode():
      '''flush selection based on the current mode current BMesh.select_mode.
         
      '''
   
      pass
   

   def to_mesh(mesh):
      '''Writes this BMesh data into an existing Mesh datablock.
         
         Arguments:
         @mesh (Mesh): The mesh data to write into.
   
      '''
   
      pass
   

   def transform(matrix, filter=None):
      '''Transform the mesh (optionally filtering flagged data only).
         
         Arguments:
         @matrix (4x4 mathutils.Matrix): transform matrix.
         @filter (set): set of values in ('SELECT', 'HIDE', 'SEAM', 'SMOOTH', 'TAG').
   
      '''
   
      pass
   

   edges = BMEdgeSeq
   '''This meshes edge sequence (read-only).
      
   '''
   

   faces = BMFaceSeq
   '''This meshes face sequence (read-only).
      
   '''
   

   is_valid = bool
   '''True when this element is valid (hasn't been removed).
      
   '''
   

   is_wrapped = bool
   '''True when this mesh is owned by blender (typically the editmode BMesh).
      
   '''
   

   loops = BMLoopSeq
   '''This meshes loops (read-only).
      .. note::
      Loops must be accessed via faces, this is only exposed for layer access.
      
   '''
   

   select_history = BMEditSelSeq
   '''Sequence of selected items (the last is displayed as active).
      
   '''
   

   select_mode = set
   '''The selection mode, values can be {'VERT', 'EDGE', 'FACE'}, can't be assigned an empty set.
      
   '''
   

   verts = BMVertSeq
   '''This meshes vert sequence (read-only).
      
   '''
   



