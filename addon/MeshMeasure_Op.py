import bpy
import numpy as np
from .utils import *

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
    print(f'minY = {mesh.measure.minY}, maxY = {mesh.measure.maxY}')
    print(f'minZ = {mesh.measure.minZ}, maxZ = {mesh.measure.maxZ}')

class MESH_OT_MEASURE(bpy.types.Operator):
    bl_label = 'Measure'
    bl_idname = 'mesh.measure'
    def execute(self, context):
        mesh = context.object
        mesh_measure(mesh)
        return {'FINISHED'}