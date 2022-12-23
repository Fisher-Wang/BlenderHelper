import bpy
import os
import shutil
import math
import numpy as np

from mathutils import Vector
from .utils import *
from .utils_debug import *

def import_mesh(path):
    _, extension = os.path.splitext(path)
    if extension == '.ply':
        bpy.ops.import_mesh.ply(filepath=path)
    elif extension == '.stl':
        bpy.ops.import_mesh.stl(filepath=path)
    elif extension == '.blend':
        shutil.copy(path, 'tmp.blend')
        bpy.ops.wm.open_mainfile(filepath='tmp.blend')
    else:
        raise ValueError('bad mesh extension')

def apply_homo_matrix(points: np.ndarray, matrix: np.ndarray):
    assert(points.shape[-1] == 3)
    assert(matrix.shape == (4, 4))
    return np.hstack([points, np.ones((points.shape[0], 1))]) @ matrix.T

def mesh_measure(mesh):
    points = np.array([v.co for v in mesh.data.vertices])
    matrix_world = np.asarray(mesh.matrix_world)
    points = apply_homo_matrix(points, matrix_world)
    mesh.measure.minX = points[:, 0].min()
    mesh.measure.maxX = points[:, 0].max()
    mesh.measure.minY = points[:, 1].min()
    mesh.measure.maxY = points[:, 1].max()
    mesh.measure.minZ = points[:, 2].min()
    mesh.measure.maxZ = points[:, 2].max()
    mesh.measure.lenX = mesh.measure.maxX - mesh.measure.minX
    mesh.measure.lenY = mesh.measure.maxY - mesh.measure.minY
    mesh.measure.lenZ = mesh.measure.maxZ - mesh.measure.minZ
    print(f'minX = {mesh.measure.minX}, maxX = {mesh.measure.maxX}')

class MESH_OT_MEASURE(bpy.types.Operator):
    bl_label = 'Measure'
    bl_idname = 'mesh.measure'
    def execute(self, context):
        mesh = find_all(context, 'MESH')[0]
        mesh_measure(mesh)
        return {'FINISHED'}

def move_to_center(mesh):
    dx = -(mesh.measure.maxX + mesh.measure.minX) / 2
    dy = -(mesh.measure.maxY + mesh.measure.minY) / 2
    dz = -(mesh.measure.maxZ + mesh.measure.minZ) / 2
    bpy.ops.transform.translate(value=(dx, dy, dz))
    mesh.measure.maxX += dx; mesh.measure.minX += dx
    mesh.measure.maxY += dy; mesh.measure.minY += dy
    mesh.measure.maxZ += dz; mesh.measure.minZ += dz

def mesh_rescale_around_world_center(mesh, scale):
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scale, scale, scale))
    mesh.measure.maxX *= scale; mesh.measure.minX *= scale
    mesh.measure.maxY *= scale; mesh.measure.minY *= scale
    mesh.measure.maxZ *= scale; mesh.measure.minZ *= scale
    mesh.measure.lenX *= scale
    mesh.measure.lenY *= scale
    mesh.measure.lenZ *= scale

def move_to_right_place(mesh):
    mesh_measure(mesh)
    move_to_center(mesh)
    maxLen = max(mesh.measure.lenX, mesh.measure.lenY)
    mesh_rescale_around_world_center(mesh, 1/(maxLen/2))

class IMPORT_MESH_OT_ANY(bpy.types.Operator):
    bl_label = 'Import Mesh of any Type'
    bl_idname = 'import_mesh.any'
    def execute(self, context):
        path = bpy.path.abspath(context.scene.mesh_path)
        _, extension = os.path.splitext(path)
        import_mesh(path)
        if extension != '.blend':
            move_to_right_place(context.object)
        return {'FINISHED'}
