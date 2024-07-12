import trimesh
import numpy as np

def loadMesh(obj_file):
    mesh = trimesh.load(obj_file, force='mesh')

def saveMesh(mesh, fpath):
    mesh.export(fpath)

def intersect_mesh_with_cube(mesh, cube_size):
    # Define the cube as a mesh
    cube = trimesh.creation.box(extents=(cube_size, cube_size, cube_size))

    # Ensure the cube is centered at the origin
    cube.apply_translation(-cube.bounding_box.center_mass)

    # Perform the boolean intersection
    intersected_mesh = mesh.intersection(cube)

    # Check if the resulting mesh is empty
    if intersected_mesh.is_empty:
        raise ValueError("The intersection resulted in an empty mesh.")

    # Calculate the minimum vertex coordinates
    min_vertex = intersected_mesh.vertices.min(axis=0)

    # Translate the mesh so that the minimum vertex is at the origin
    intersected_mesh.vertices -= min_vertex

    return intersected_mesh

def cut_mesh(mesh, radius):    
    # Assuming center is defined as a numpy array [x, y, z]
    center = np.array([0, 0, 0])  # Example center point

    # Compute distances from center to all vertices
    distances = np.linalg.norm(mesh.vertices - center, axis=1)

    # Find triangles whose vertices are all within the radius
    triangles_within_radius = []
    for triangle in mesh.faces:
        vertices_within_radius = True
        for vertex_index in triangle:
            if distances[vertex_index] > radius:
                vertices_within_radius = False
                break
        if vertices_within_radius:
            triangles_within_radius.append(triangle)

    # Create a new mesh with only the triangles within radius
    filtered_mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=np.array(triangles_within_radius))

    # Calculate the minimum vertex coordinates
    min_vertex = filtered_mesh.vertices.min(axis=0)

    # Translate the mesh so that the minimum vertex is at the origin
    filtered_mesh.vertices -= min_vertex

    return filtered_mesh

def detect_zero_height_vertices(mesh):
    # Load the mesh
    # mesh = trimesh.load(obj_file, force='mesh')

    # Find the indices of vertices with z-coordinate of 0
    # zero_height_indices = np.where(mesh.vertices[:, 2] == 0)[0]

    # # Iterate through vertices and add 2mm to vertices with z-coordinate of 0
    # for i, vertex in enumerate(mesh.vertices):
    #     if vertex[2] < 0.1:  # Check if z-coordinate is 0
    #         mesh.vertices[i][2] += 5.0  # Add 2mm to z-coordinate

    # # Save the modified mesh
    # mesh.export(obj_file)

    return zero_height_indices.tolist()

def add_square_to_mesh(mesh, radius):    
    thickness = 2

    # Translate the filtered mesh vertices by 2mm along the z-axis
    mesh.vertices[:, 2] += thickness

    # Create the square mesh
    square_mesh = create_square(radius, thickness, radius)

    # Combine the filtered mesh and the square mesh
    combined_mesh = trimesh.util.concatenate([mesh, square_mesh])
    
    return mesh


def create_square(width, height, depth):
    """
    Create a rectangular prism with specified dimensions.

    Parameters:
    width (float): Width of the square (x-axis).
    height (float): Height of the square (y-axis).
    depth (float): Depth of the square (z-axis).

    Returns:
    trimesh.Trimesh: The created mesh.
    """
    # Define the 8 vertices of the rectangular prism
    vertices = np.array([
        [0, 0, 0],          # Bottom face
        [width, 0, 0],
        [width, height, 0],
        [0, height, 0],
        [0, 0, depth],      # Top face
        [width, 0, depth],
        [width, height, depth],
        [0, height, depth]
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
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    return mesh