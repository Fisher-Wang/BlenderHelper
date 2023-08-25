## Source: https://gist.github.com/autosquid/8e1cddbc0336a49c6f84591d35371c4d

import numpy as np
import bpy
from mathutils import Matrix

# from: http://blender.stackexchange.com/questions/40650/blender-camera-from-3x4-matrix?rq=1
# And: http://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera


# Input: P 3x4 numpy matrix
# Output: K, R, T such that P = K*[R | T], det(R) positive and K has positive diagonal
#
# Reference implementations: 
#   - Oxford's visual geometry group matlab toolbox 
#   - Scilab Image Processing toolbox
def KRT_from_P(P):
    N = 3
    H = P[:,0:N]  # if not numpy,  H = P.to_3x3()

    [K,R] = rf_rq(H)

    K /= K[-1,-1]

    # from http://ksimek.github.io/2012/08/14/decompose/
    # make the diagonal of K positive
    sg = np.diag(np.sign(np.diag(K)))

    K = K * sg
    R = sg * R
    # det(R) negative, just invert; the proj equation remains same:
    if (np.linalg.det(R) < 0):
       R = -R
    # C = -H\P[:,-1]
    C = np.linalg.lstsq(-H, P[:,-1])[0]
    T = -R*C
    return K, R, T

# RQ decomposition of a numpy matrix, using only libs that already come with
# blender by default
#
# Author: Ricardo Fabbri
# Reference implementations: 
#   Oxford's visual geometry group matlab toolbox 
#   Scilab Image Processing toolbox
#
# Input: 3x4 numpy matrix P
# Returns: numpy matrices r,q
def rf_rq(P):
    P = P.T
    # numpy only provides qr. Scipy has rq but doesn't ship with blender
    q, r = np.linalg.qr(P[ ::-1, ::-1], 'complete')
    q = q.T
    q = q[ ::-1, ::-1]
    r = r.T
    r = r[ ::-1, ::-1]

    if (np.linalg.det(q) < 0):
        r[:,0] *= -1
        q[0,:] *= -1
    return r, q

# Creates a blender camera consistent with a given 3x4 computer vision P matrix
# Run this in Object Mode
# scale: resolution scale percentage as in GUI, known a priori
# P: numpy 3x4
def get_blender_camera_from_3x4_P(P, scale):
    # get krt
    K, R_world2cv, T_world2cv = KRT_from_P(np.matrix(P))

    scene = bpy.context.scene
    sensor_width_in_mm = K[1,1]*K[0,2] / (K[0,0]*K[1,2])
    sensor_height_in_mm = 1  # doesn't matter
    resolution_x_in_px = K[0,2]*2  # principal point assumed at the center
    resolution_y_in_px = K[1,2]*2  # principal point assumed at the center

    s_u = resolution_x_in_px / sensor_width_in_mm
    s_v = resolution_y_in_px / sensor_height_in_mm
    # TODO include aspect ratio
    f_in_mm = K[0,0] / s_u
    # recover original resolution
    scene.render.resolution_x = resolution_x_in_px / scale
    scene.render.resolution_y = resolution_y_in_px / scale
    scene.render.resolution_percentage = scale * 100

    # Use this if the projection matrix follows the convention listed in my answer to
    # http://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera
    R_bcam2cv = Matrix(
        ((1, 0,  0),
         (0, -1, 0),
         (0, 0, -1)))

    # Use this if the projection matrix follows the convention from e.g. the matlab calibration toolbox:
    # R_bcam2cv = Matrix(
    #     ((-1, 0,  0),
    #      (0, 1, 0),
    #      (0, 0, 1)))

    R_cv2world = R_world2cv.T
    rotation =  Matrix(R_cv2world.tolist()) * R_bcam2cv
    location = -R_cv2world * T_world2cv

    # create a new camera
    bpy.ops.object.add(
        type='CAMERA',
        location=location)
    ob = bpy.context.object
    ob.name = 'CamFrom3x4PObj'
    cam = ob.data
    cam.name = 'CamFrom3x4P'

    # Lens
    cam.type = 'PERSP'
    cam.lens = f_in_mm 
    cam.lens_unit = 'MILLIMETERS'
    cam.sensor_width  = sensor_width_in_mm
    ob.matrix_world = Matrix.Translation(location)*rotation.to_4x4()

    # Display
    cam.show_name = True
    # Make this the current camera
    scene.camera = ob
    bpy.context.scene.update()
    
    ## added by fsw
    return ob


def get_blender_camera_from_KRT(K, R_world2cv, T_world2cv, scale=1):
    #! XXX: Use this for S3NeRF
    T_world2cv = -R_world2cv.T @ T_world2cv
    R_world2cv = R_world2cv.T
    
    assert np.isclose(Matrix(R_world2cv).determinant(), 1)
    
    scene = bpy.context.scene
    sensor_width_in_mm = K[1,1]*K[0,2] / (K[0,0]*K[1,2])
    sensor_height_in_mm = 1  # doesn't matter
    resolution_x_in_px = K[0,2]*2  # principal point assumed at the center
    resolution_y_in_px = K[1,2]*2  # principal point assumed at the center

    s_u = resolution_x_in_px / sensor_width_in_mm
    s_v = resolution_y_in_px / sensor_height_in_mm
    # TODO include aspect ratio
    f_in_mm = K[0,0] / s_u
    # recover original resolution
    scene.render.resolution_x = int(resolution_x_in_px / scale)
    scene.render.resolution_y = int(resolution_y_in_px / scale)
    scene.render.resolution_percentage = scale * 100

    # Use this if the projection matrix follows the convention listed in my answer to
    # http://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera
    # R_bcam2cv = Matrix(
    #     ((1, 0,  0),
    #      (0, -1, 0),
    #      (0, 0, -1)))
    
    # Use this if the projection matrix follows the convention from e.g. the matlab calibration toolbox:
    # R_bcam2cv = Matrix(
    #     ((-1, 0,  0),
    #      (0, 1, 0),
    #      (0, 0, 1)))
    
    #! XXX: Use this for S3NeRF
    R_bcam2cv = Matrix(
        ((1, 0, 0),
         (0, 1, 0),
         (0, 0, 1)))

    R_cv2world = R_world2cv.T  # (3, 3)
    rotation =  Matrix((R_cv2world @ R_bcam2cv).tolist())
    location = -R_cv2world @ T_world2cv  # (3, )
    
    # create a new camera
    bpy.ops.object.camera_add()
    # bpy.ops.object.camera_add(location=location, rotation=rotation.to_euler())  # not equivalent to the composition process below, don't know why
    ob = bpy.context.object
    # ob.name = 'CamFrom3x4PObj'
    cam = ob.data
    # cam.name = 'CamFrom3x4P'

    # Lens
    cam.type = 'PERSP'
    cam.lens = f_in_mm 
    cam.lens_unit = 'MILLIMETERS'
    cam.sensor_width  = sensor_width_in_mm
        
    # composition (inverse process of decompose method)
    ob.matrix_world = Matrix.Translation(location) @ rotation.to_4x4()  
    
    location, rotation = ob.matrix_world.decompose()[0:2]

    # Display
    cam.show_name = True
    # Make this the current camera
    scene.camera = ob
    # bpy.context.scene.update()
    
    return ob

def test2():
    P = Matrix([
    [2. ,  0. , - 10. ,   282.  ],
    [0. ,- 3. , - 14. ,   417.  ],
    [0. ,  0. , - 1.  , - 18.   ]
    ])
    # This test P was constructed as k*[r | t] where
    #     k = [2 0 10; 0 3 14; 0 0 1]
    #     r = [1 0 0; 0 -1 0; 0 0 -1]
    #     t = [231 223 -18]
    # k, r, t = KRT_from_P(np.matrix(P))
    get_blender_camera_from_3x4_P(P, 1)