import bpy
import os
import math
import yaml
import json
from time import time
import numpy as np
from mathutils import Vector

VIEW_LAYER_NAME = 'ViewLayer'

def mkdir(dir_path, exist_ok=True):
    os.makedirs(dir_path, exist_ok=exist_ok)
    return dir_path

def get_node_tree(mesh):
    return [material.node_tree for material in mesh.data.materials if material != None][0]

def delete_all(context, types: list):
    for o in context.scene.objects:
        if o.type in types:
            o.select_set(True)
        else:
            o.select_set(False)
    bpy.ops.object.delete()

def find_all(context, type):
    rst = []
    for o in context.scene.objects:
        if o.type == type:
            rst.append(o)
    return rst

def select_one(context, object, active=True):
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    if active:
        context.view_layer.objects.active = object

def set_direction_to(object, focus_point=Vector((0.0, 0.0, 0.0)), distance=10.0):
    ## source: https://blender.stackexchange.com/a/100442
    '''
    #### Parameters
    - `object`: can be camera or light
    '''
    looking_direction = object.location - focus_point
    rot_quat = looking_direction.to_track_quat('Z', 'Y')
    object.rotation_euler = rot_quat.to_euler()
    object.location = rot_quat @ Vector((0.0, 0.0, distance))

def get_frame_range_obj(obj):
    if obj.animation_data:
        frame_start, frame_end = map(int, obj.animation_data.action.frame_range)
    else:
        frame_start, frame_end = 0, 0
    return frame_start, frame_end

def get_frame_range_scene(scene):
    min_frame_start, max_frame_end = math.inf, 0
    for obj in scene.objects:
        frame_start, frame_end = get_frame_range_obj(obj)
        min_frame_start = min(min_frame_start, frame_start)
        max_frame_end = max(max_frame_end, frame_end)
    return min_frame_start, max_frame_end

def phi_theta_to_xyz(phi, theta):
    phi = phi / 180 * math.pi
    theta = theta / 180 * math.pi
    x = math.cos(theta) * math.sin(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(phi)
    return (x, y, z)

def switch_cast_shadow(context, enable=True):
    for object in context.scene.objects:
        if object.type == 'MESH':
            object.visible_shadow = enable

def write_yaml(fname: str, data: dict, compact=False):
    with open(fname, 'w+') as f:
        yaml.dump(data, f, default_flow_style=compact)

def write_json(fname: str, data: dict):
    with open(fname, 'w+') as f:
        json.dump(data, f, indent=4, sort_keys=True)

def read_json(fname: str):
    with open(fname) as f:
        data = json.load(f)
    return data

def timer_func(func):
    ## Ref: https://www.geeksforgeeks.org/timing-functions-with-decorators-python/
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func

def apply_homo_matrix(points: np.ndarray, matrix: np.ndarray):
    assert(points.shape[-1] == 3)
    assert(matrix.shape == (4, 4))
    return np.hstack([points, np.ones((points.shape[0], 1))]) @ matrix.T

def _rand(lo, hi, size):
    return np.random.random(size) * (hi - lo) + lo

def read_yaml(path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data
