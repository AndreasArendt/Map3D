import os

def get_obj_dimensions(file_path):
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.split()
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
                min_z, max_z = min(min_z, z), max(max_z, z)
    
    return (min_x, max_x), (min_y, max_y), (min_z, max_z)

def scale_obj(input_path, desired_dimension):
    output_path = './data/scaled_file.obj'

    # Get the current dimensions of the OBJ file
    (x_range, y_range, z_range) = get_obj_dimensions(input_path)

    # Calculate the current maximum dimension
    current_max_dimension = max(x_range[1] - x_range[0], y_range[1] - y_range[0], z_range[1] - z_range[0])

    # Calculate the scale factor to fit the model within the desired dimension
    scale_factor = desired_dimension / current_max_dimension

    with open(input_path, 'r') as file:
        lines = file.readlines()

    with open(output_path, 'w') as file:
        for line in lines:
            if line.startswith('v '):
                parts = line.split()
                x = float(parts[1]) * scale_factor
                y = float(parts[2]) * scale_factor
                z = float(parts[3]) * scale_factor
                file.write(f'v {x} {y} {z}\n')
            else:
                file.write(line)
    
    print(f"OBJ file scaled by a factor of {scale_factor} and saved to {output_path}")
    return output_path