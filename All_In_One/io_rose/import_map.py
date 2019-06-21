if "bpy" in locals():
    import importlib
    # importlib.reload(rose)
else:
    from .rose.him import *
    from .rose.til import *
    from .rose.zon import *

import glob
import os
from types import SimpleNamespace 

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


class ImportMap(bpy.types.Operator, ImportHelper):
    bl_idname = "import_map.zon"
    bl_label = "Import ROSE map (.zon)"
    bl_options = {"PRESET"}
    
    filename_ext = ".zon"
    filter_glob = StringProperty(default="*.zon", options={"HIDDEN"})

    def execute(self, context):
        him_ext = ".HIM"
        til_ext = ".TIL"
        ifo_ext = ".IFO"

        # Incase user is on case-sensitive platform and is using lowercase ext
        if self.filepath.endswith(".zon"):
            him_ext = ".him"
            til_ext = ".til"
            ifo_ext = ".ifo"    

        zon = Zon(self.filepath)
        zon_dir = os.path.dirname(self.filepath)
        
        tiles = SimpleNamespace()
        tiles.min_pos = Vector2(999, 999)
        tiles.max_pos = Vector2(-1, -1)
        tiles.dimension = Vector2(0, 0)
        tiles.count = 0
        tiles.coords = []

        for file in os.listdir(zon_dir):
            # Use HIM files to build tiles data
            if file.endswith(him_ext):
                # Extract coordinate of tiles system from file name
                x,y = map(int, file.split(".")[0].split("_"))
                
                # Get min/max pos of tile system
                tiles.min_pos.x = min(x, tiles.min_pos.x)
                tiles.min_pos.y = min(y, tiles.min_pos.y)
                tiles.max_pos.x = max(x, tiles.max_pos.x)
                tiles.max_pos.y = max(y, tiles.max_pos.y)
                
                tiles.count += 1
                tiles.coords.append((x, y))
        
        tiles.dimension.x = tiles.max_pos.x - tiles.min_pos.x + 1
        tiles.dimension.y = tiles.max_pos.y - tiles.min_pos.y + 1
        
        tiles.indices = list_2d(tiles.dimension.x, tiles.dimension.y)
        tiles.hims = list_2d(tiles.dimension.x, tiles.dimension.y)
        tiles.tils = list_2d(tiles.dimension.x, tiles.dimension.y)
        tiles.ifos = list_2d(tiles.dimension.x, tiles.dimension.y)

        for x, y in tiles.coords:
            tile_name = "{}_{}".format(x,y)
            him_file = os.path.join(zon_dir, tile_name + him_ext)
            til_file = os.path.join(zon_dir, tile_name + til_ext)
            ifo_file = os.path.join(zon_dir, tile_name + ifo_ext)

            # Calculate relative offset for this tile
            norm_x = x - tiles.min_pos.x
            norm_y = y - tiles.min_pos.y
            
            him = Him(him_file)
            til = Til(til_file)
            # ifo = Ifo(ifo_file)

            # Stores vertex indices
            him.indices = list_2d(him.width, him.length)
            
            tiles.indices[norm_y][norm_x] = list_2d(him.width, him.length)
            tiles.hims[norm_y][norm_x] = him
            tiles.tils[norm_y][norm_x] = til
            # tiles.ifos[norm_y][norm_x] = ifo
        
        tiles.offsets = list_2d(tiles.dimension.x, tiles.dimension.y)

        # Calculate tile offsets
        length, cur_length = 0, 0
        for y in range(tiles.dimension.y):
            width = 0
            for x in range(tiles.dimension.x):
                him = tiles.hims[y][x]

                offset = Vector2(width, length)
                tiles.offsets[y][x] = offset

                width += him.width
                cur_length = him.length

            length += cur_length
        
        vertices = []
        edges = []
        faces = []
        
        # Generate mesh data (vertices/edges/faces) for each tile 
        for y in range(tiles.dimension.y):
            for x in range(tiles.dimension.x):
                indices = tiles.indices[y][x]
                him = tiles.hims[y][x]

                offset_x = tiles.offsets[y][x].x
                offset_y = tiles.offsets[y][x].y
                
                for vy in range(him.length):
                    for vx in range(him.width):
                        # Create vertices
                        vz = him.heights[vy][vx] / him.patch_scale
                        vertices.append((vx+offset_x,vy+offset_y,vz))
                        
                        vi = len(vertices) - 1
                        him.indices[vy][vx] = vi
                        indices[vy][vx] = vi

                        if vx < him.width -1 and vy < him.length - 1:
                            v1 = vi
                            v2 = vi + 1
                            v3 = vi + 1 + him.width
                            v4 = vi + him.width
                            edges += ((v1,v2), (v2,v3), (v3,v4), (v4,v1))
                            faces.append((v1,v2,v3,v4))
        
        # Generate edges/faces inbetween each HIM tile
        for y in range(tiles.dimension.y):
            for x in range(tiles.dimension.x):
                indices = tiles.indices[y][x]
                him = tiles.hims[y][x]
                
                is_x_edge = (x == tiles.dimension.x - 1)
                is_y_edge = (y == tiles.dimension.y - 1)

                for vy in range(him.length):
                    for vx in range(him.width):
                        is_x_edge_vertex = (vx == him.width - 1) and \
                                            (vy < him.length - 1)
                        is_y_edge_vertex = (vx < him.width - 1) and \
                                            (vy == him.length - 1)
                        is_corner_vertex = (vx == him.width - 1) and \
                                            (vy == him.length - 1)

                        if not is_x_edge:
                            if is_x_edge_vertex:
                                next_indices = tiles.indices[y][x+1]
                                v1 = indices[vy][vx]
                                v2 = next_indices[vy][0]
                                v3 = next_indices[vy+1][0]
                                v4 = indices[vy+1][vx]
                                edges += ((v1,v2), (v2,v3), (v3,v4), (v4,v1))
                                faces.append((v1,v2,v3,v4))
                        
                        if not is_y_edge:
                            if is_y_edge_vertex:
                                next_indices = tiles.indices[y+1][x]
                                v1 = indices[vy][vx]
                                v2 = indices[vy][vx+1]
                                v3 = next_indices[0][vx+1]
                                v4 = next_indices[0][vx]
                                edges += ((v1,v2), (v2,v3), (v3,v4), (v4,v1))
                                faces.append((v1,v2,v3,v4))

                        if not is_x_edge and not is_y_edge:
                            if is_corner_vertex:
                                right = tiles.indices[y][x+1]
                                diag = tiles.indices[y+1][x+1]
                                down = tiles.indices[y+1][x]
                                diag_him = tiles.hims[y+1][x+1]
                                down_him = tiles.hims[y+1][x]

                                v1 = indices[vy][vx]
                                v2 = right[diag_him.length-1][0]
                                v3 = diag[0][0]
                                v4 = down[0][down_him.width-1]
                                edges += ((v1,v2), (v2,v3), (v3,v4), (v4,v1))
                                faces.append((v1,v2,v3,v4))
                            
        
        # Create our object and mesh
        bpy.ops.object.add(type='MESH')
        terrain_obj = bpy.context.object
        terrain_mesh = terrain_obj.data
        
        terrain_mesh.from_pydata(vertices, edges, faces)
        terrain_mesh.update()

        return {"FINISHED"}

