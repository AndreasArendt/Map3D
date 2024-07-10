import os
import json
from query_tile import query_tile
from scale_obj import scale_obj
from cut_mesh import cut_mesh, add_square_to_mesh, detect_zero_height_vertices

with open('src/meta.json', 'r', -1, 'utf-8') as f:
    meta = json.load(f)
    
# download tile
fpath = query_tile(address=meta['address'], radius=500)
fpath = os.path.normpath(fpath)

# convert tile
os.system(os.path.normpath(f"./src/conv_osm.bat ") + fpath)

#cut mesh
input_obj_path = cut_mesh("data/test.obj", 500)

# Scale the OBJ file
output_path = scale_obj(input_obj_path, 170)

# detect_zero_height_vertices(output_path)

# add square
add_square_to_mesh("data/scaled_file.obj", 170)
