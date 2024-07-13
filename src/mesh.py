import trimesh
import numpy as np
import math

def loadMesh(obj_file):
    return trimesh.load(obj_file, force='mesh')

def saveMesh(mesh, fpath):
    mesh.export(fpath)

def rotateX(mesh, angle__deg):
    angle = angle__deg / 180 * math.pi
    direction = [1, 0, 0]
    center = [0, 0, 0]

    rot_matrix = trimesh.transformations.rotation_matrix(angle, direction, center)
    mesh.apply_transform(rot_matrix)

def cut_mesh(mesh, width, height, depth):
    # Define half-dimensions for easier boundary checking
    half_width = width / 2
    half_height = height / 2
    half_depth = depth / 2

    def within_bounds(vertex):
        return (-half_width <= vertex[0] <= half_width and
                -half_height <= vertex[1] <= half_height and
                -half_depth <= vertex[2] <= half_depth)

    new_vertices = mesh.vertices.tolist()
    new_faces = []

    for triangle in mesh.faces:
        v0, v1, v2 = triangle
        vert0, vert1, vert2 = mesh.vertices[v0], mesh.vertices[v1], mesh.vertices[v2]
        in_bounds0, in_bounds1, in_bounds2 = within_bounds(vert0), within_bounds(vert1), within_bounds(vert2)

        if in_bounds0 and in_bounds1 and in_bounds2:
            new_faces.append(triangle)
        else:
            inside = []
            outside = []

            for v, in_bounds in zip([v0, v1, v2], [in_bounds0, in_bounds1, in_bounds2]):
                if in_bounds:
                    inside.append(v)
                else:
                    outside.append(v)

            if len(inside) == 1 and len(outside) == 2:
                vi = inside[0]
                vo1, vo2 = outside
                new_v1 = linear_interpolate_to_border(mesh.vertices[vi], mesh.vertices[vo1], half_width, half_height, half_depth)
                new_v2 = linear_interpolate_to_border(mesh.vertices[vi], mesh.vertices[vo2], half_width, half_height, half_depth)

                new_v1_index = len(new_vertices)
                new_v2_index = new_v1_index + 1

                new_vertices.append(new_v1.tolist())
                new_vertices.append(new_v2.tolist())

                new_faces.append([vi, new_v1_index, new_v2_index])

            elif len(inside) == 2 and len(outside) == 1:
                vi1, vi2 = inside
                vo = outside[0]
                new_v1 = linear_interpolate_to_border(mesh.vertices[vi1], mesh.vertices[vo], half_width, half_height, half_depth)
                new_v2 = linear_interpolate_to_border(mesh.vertices[vi2], mesh.vertices[vo], half_width, half_height, half_depth)

                new_v1_index = len(new_vertices)
                new_v2_index = new_v1_index + 1

                new_vertices.append(new_v1.tolist())
                new_vertices.append(new_v2.tolist())

                new_faces.append([vi1, vi2, new_v1_index])
                new_faces.append([vi2, new_v1_index, new_v2_index])

    # Create a new mesh with the cut geometry
    cut_mesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces)

    # Ensure the mesh is closed and watertight
    cut_mesh.remove_unreferenced_vertices()
    cut_mesh.merge_vertices()
    cut_mesh.remove_degenerate_faces()
    cut_mesh.fix_normals()

    return cut_mesh

def linear_interpolate_to_border(v_inside, v_outside, half_width, half_height, half_depth):
    direction = v_outside - v_inside
    new_vertex = np.copy(v_inside)

    for i in range(3):
        if v_outside[i] > half_width:
            t = (half_width - v_inside[i]) / direction[i]
        elif v_outside[i] < -half_width:
            t = (-half_width - v_inside[i]) / direction[i]
        else:
            continue

        new_vertex = v_inside + t * direction
        break

    return new_vertex

def add_square_to_mesh(mesh, radius, thickness=2):        
    # Translate the filtered mesh vertices by 2mm along the z-axis
    mesh.vertices[:, 2] += thickness

    # Create the square mesh
    square_mesh = create_square(radius, thickness, radius)

    # Combine the filtered mesh and the square mesh
    return trimesh.util.concatenate([mesh, square_mesh])
        
def create_square(width, height, depth):
    # Define the 8 vertices of the rectangular prism
    vertices = np.array([
            [-width/2, -height/2, -depth/2],  # Bottom face
            [width/2, -height/2, -depth/2],
            [width/2, height/2, -depth/2],
            [-width/2, height/2, -depth/2],
            [-width/2, -height/2, depth/2],   # Top face
            [width/2, -height/2, depth/2],
            [width/2, height/2, depth/2],
            [-width/2, height/2, depth/2]
        ])

    # Define the 12 faces of the rectangular prism
    faces = np.array([
        [0, 1, 2], [0, 2, 3],     # Bottom face
        [4, 5, 6], [4, 6, 7],     # Top face
        [0, 1, 5], [0, 5, 4],     # Front face
        [1, 2, 6], [1, 6, 5],     # Right face
        [2, 3, 7], [2, 7, 6],     # Back face
        [3, 0, 4], [3, 4, 7]      # Left face
    ])

    # Create the mesh
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def add_walls_around_mesh(mesh, wall_height):
    # Get the existing vertices and faces
    vertices = mesh.vertices
    faces = mesh.faces

    # Calculate the bounding box of the mesh
    bbox = mesh.bounding_box.bounds
    min_corner = bbox[0]
    max_corner = bbox[1]

    # Define the bottom and top vertices for the walls
    bottom_vertices = np.array([
        [min_corner[0], min_corner[1], min_corner[2]],
        [max_corner[0], min_corner[1], min_corner[2]],
        [max_corner[0], max_corner[1], min_corner[2]],
        [min_corner[0], max_corner[1], min_corner[2]]
    ])
    top_vertices = bottom_vertices + np.array([0, 0, wall_height])

    # Combine the original vertices with the wall vertices
    new_vertices = np.vstack((vertices, bottom_vertices, top_vertices))
    
    # Calculate the indices of the new vertices
    start_index = len(vertices)
    bottom_indices = np.arange(start_index, start_index + len(bottom_vertices))
    top_indices = np.arange(start_index + len(bottom_vertices), start_index + len(bottom_vertices) + len(top_vertices))

    # Define the faces for the walls
    wall_faces = np.array([
        [bottom_indices[0], bottom_indices[1], top_indices[1], top_indices[0]],  # Front wall
        [bottom_indices[1], bottom_indices[2], top_indices[2], top_indices[1]],  # Right wall
        [bottom_indices[2], bottom_indices[3], top_indices[3], top_indices[2]],  # Back wall
        [bottom_indices[3], bottom_indices[0], top_indices[0], top_indices[3]]   # Left wall
    ])

    # Flatten the faces into triangles
    new_faces = []
    for face in faces:
        new_faces.append(face)
    for face in wall_faces:
        new_faces.append([face[0], face[1], face[2]])
        new_faces.append([face[0], face[2], face[3]])

    # Create the new mesh with walls
    new_mesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces)

    return new_mesh