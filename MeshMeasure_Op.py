import bpy
import numpy as np
from .utils import *

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