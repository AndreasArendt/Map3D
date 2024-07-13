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

mesh = loadMesh("data/tile.obj")                # load

mesh = add_square_to_mesh(mesh, 500, 2)         # add build plate
rotateX(mesh, 90)
mesh = cut_mesh(mesh, 500, 500, 500)

for m in mesh.vertices:
    if m[2] < 0:
        m[2] = 0

mesh.fix_normals()
mesh.merge_vertices()
mesh.fill_holes()

# save mesh
saveMesh(mesh, "data/printable.obj")

scale_obj("data/printable.obj", 170)                     # scale it 1o 170x170 mm