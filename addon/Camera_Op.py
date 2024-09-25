import bpy
import math
import numpy as np
from .utils import *
from .utils_debug import *
from .matrix2camera import get_blender_camera_from_KRT
from .world2camera import get_3x4_P_matrix_from_blender
from mathutils import Vector

def add_orthographic_camera(context):
    debug_print('[INFO] Calling add_orthographic_camera')
    delete_all(context, 'CAMERA')
    
    mesh = find_all(context, 'MESH')[0]
    maxLen = max(mesh.measure.lenX, mesh.measure.lenY)
    print(maxLen)
    
    bpy.ops.object.camera_add(location=(0, 0, 10), rotation=(0, 0, -1))
    context.scene.camera = context.object
    camera = context.scene.camera
    set_direction_to(camera, distance=10)
    # This sentence fails on blender 2.93.11, but work well on blender 2.83.20 and 3.3.1
    bpy.ops.transform.rotate(value=math.pi, orient_axis='Z')

    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = maxLen
    camera.data.clip_end = 10000  # XXX: increase this value when rendered result is blank!
    return camera

class CAMERA_OT_ADD_ORTHOGRAPHIC(bpy.types.Operator):
    bl_label = 'Add Otrho Camera'
    bl_idname = 'camera.add_orthographic'
    def execute(self, context):
        add_orthographic_camera(context)
        return {'FINISHED'}

def set_camera_pos(cam, phi, theta):
    dis = np.linalg.norm(np.asarray(cam.location))
    cam.location = phi_theta_to_xyz(phi, theta)
    set_direction_to(cam, Vector((0, 0, 0)), distance=dis)

class CAMERA_OT_SET_POSITION(bpy.types.Operator):
    bl_label = 'Set Position'
    bl_idname = 'camera.set_position'
    def execute(self, context):
        set_camera_pos(context.scene.camera, context.scene.camera_phi, context.scene.camera_theta)
        return {'FINISHED'}

class CAMERA_OT_SET_POSITION_FROM_MATRIX(bpy.types.Operator):
    bl_label = 'Set Position from Matrix'
    bl_idname = 'camera.set_position_from_matrix'
    def execute(self, context):
        K = np.array([
            [
                711.1110599640117,
                0.0,
                256.0
            ],
            [
                0.0,
                711.1110599640117,
                256.0
            ],
            [
                0.0,
                0.0,
                1.0
            ]
        ])
        R = np.array([
            [
                -0.1613457202911377,
                -0.3997095823287964,
                0.9023301005363464,
            ],
            [
                0.9868979454040527,
                -0.06534761935472488,
                0.14751990139484406,
            ],
            [
                3.725290298461914e-09,
                0.914309561252594,
                0.40501612424850464,
            ],
        ])
        T = np.array([3.637409210205078, 0.5946717858314514, 1.6326723098754883])
        # camera = context.scene.camera
        # print(camera.matrix_world)
        
        # _, K, RT = get_3x4_P_matrix_from_blender(camera)
        # K = np.asarray(RT)
        # R = np.asarray(RT)[:, :3]
        # T = np.asarray(RT)[:, -1]
        # matrix_world = get_blender_camera_from_KRT(K, R, T, 1)
        # print(matrix_world)
                   
        camera = get_blender_camera_from_KRT(K, R, T, 1)
        return {'FINISHED'}