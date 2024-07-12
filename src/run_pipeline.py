import os
import json
from query_tile import query_tile
from scale_obj import scale_obj
from mesh import *

with open('src/meta.json', 'r', -1, 'utf-8') as f:
    meta = json.load(f)
    
# download tile
fpath = query_tile(address=meta['address'], radius=500)
fpath = os.path.normpath(fpath)

# convert tile
os.system(os.path.normpath(f"./src/conv_osm.bat ") + fpath)


mesh = loadMesh("data/test.obj")                # load
mesh = intersect_mesh_with_cube(mesh, 500)      # intersect - cut out center
mesh = scale_obj(mesh, 170)                     # scale it 1o 170x170 mm
mesh = add_square_to_mesh(mesh, 170)            # add build plate

# save mesh
saveMesh(mesh, "data/printable.obj")
