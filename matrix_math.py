import math

# Vector Operations
def add_vectors(v1, v2):
    return [v1[i] + v2[i] for i in range(len(v1))]

def subtract_vectors(v1, v2):
    return [v1[i] - v2[i] for i in range(len(v1))]

def dot_product(v1, v2):
    return sum(v1[i] * v2[i] for i in range(len(v1)))

def cross_product(v1, v2):
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Cross product is only defined for 3D vectors")
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    ]

def normalize_vector(v):
    mag = math.sqrt(sum(x*x for x in v))
    if mag == 0: return v # Or raise error for zero vector
    return [x / mag for x in v]

def multiply_vector_by_scalar(v, s):
    return [x * s for x in v]

# Matrix Operations (Assuming 4x4 matrices for 3D graphics)
def identity_matrix():
    return [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]

def multiply_matrices(m1, m2):
    # Standard 4x4 matrix multiplication
    res = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                res[i][j] += m1[i][k] * m2[k][j]
    return res

def multiply_matrix_vector(matrix, vector): # Vector assumed to be (x,y,z,w)
    if len(vector) != 4: raise ValueError("Vector must have 4 components (x,y,z,w)")
    res = [0, 0, 0, 0]
    for i in range(4):
        for j in range(4):
            res[i] += matrix[i][j] * vector[j]
    return res

# Transformation Matrices
def translation_matrix(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ]

def scaling_matrix(sx, sy, sz):
    return [
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1],
    ]

def rotation_matrix_x(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return [
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1],
    ]

def rotation_matrix_y(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return [
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1],
    ]

def rotation_matrix_z(angle_rad):
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return [
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]

# Projection Matrix
def perspective_projection_matrix(fov_deg, aspect_ratio, near, far):
    fov_rad = math.radians(fov_deg)
    f = 1.0 / math.tan(fov_rad / 2.0)
    return [
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0], # This -1 is crucial for perspective divide
    ]

# View Matrix (Camera)
def look_at_matrix(eye, target, up):
    # eye: camera position (e.g. [0,0,5])
    # target: point camera is looking at (e.g. [0,0,0])
    # up: world up direction (e.g. [0,1,0])

    z_axis = normalize_vector(subtract_vectors(eye, target))
    x_axis = normalize_vector(cross_product(up, z_axis))
    y_axis = cross_product(z_axis, x_axis) # Already normalized if x and z are orthonormal

    # Transposed rotation part, because we are transforming world to camera
    # The translation part is -dot_product(axis, eye)
    return [
        [x_axis[0], x_axis[1], x_axis[2], -dot_product(x_axis, eye)],
        [y_axis[0], y_axis[1], y_axis[2], -dot_product(y_axis, eye)],
        [z_axis[0], z_axis[1], z_axis[2], -dot_product(z_axis, eye)],
        [0, 0, 0, 1],
    ]
