import bpy
import bmesh
import numpy as np
import matplotlib.pyplot as plt
from .utils import timer_func, apply_homo_matrix, _rand

def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.
    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.
    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.
    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge
            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

def get_regions(mesh):
    from shapely.geometry import Point, MultiPoint, Polygon
    from scipy.spatial import Voronoi
    
    lenX = mesh.measure.lenX / 2
    lenY = mesh.measure.lenY / 2
    print(f'lenX = {lenX}, lenY = {lenY}')
    # assert(np.allclose(lenX, 1) and np.allclose(lenY, 1))
    
    mesh_points = np.array([v.co for v in mesh.data.vertices])
    mesh_points = apply_homo_matrix(mesh_points, np.array(mesh.matrix_world))
    mesh_points = mesh_points[:, :2]  # only x, y coordinates
    mpt = MultiPoint(mesh_points)
    polygon = Polygon(mpt.convex_hull.boundary.coords)

    num_points = 20
    points_x = _rand(-lenX, lenX, num_points)
    points_y = _rand(-lenY, lenY, num_points)
    points = np.vstack([points_x, points_y]).T
    points = np.array([p for p in points if polygon.contains(Point(p))])
    
    vor = Voronoi(points)
    regions, vertices = voronoi_finite_polygons_2d(vor)
    
    ## Preview Regions
    fig, ax = plt.subplots()
    for region in regions:
        poly = vertices[region]
        ax.fill(*zip(*poly), alpha=0.7)
    ax.plot(points[:, 0], points[:, 1], 'ro', ms=1)
    fig.savefig(bpy.path.abspath('//tmp.png'))
    
    return regions, vertices

def split_on_condition(mesh, f):
    bpy.ops.object.mode_set(mode='EDIT')

    me = mesh.data
    bm = bmesh.from_edit_mesh(me)

    any_selected = False
    for v in bm.verts:
        x, y, z = v.co @ mesh.matrix_world
        if f(x, y, z):
            v.select_set(True)
            any_selected = True
        else:
            v.select_set(False)

    bm.select_mode |= {'VERT'}
    bm.select_flush_mode()
        
    bmesh.update_edit_mesh(me)
    if any_selected:
        bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode='OBJECT')

def split_mesh(mesh, regions, vertices):
    from shapely.geometry import Point, Polygon
    for region in regions:
        poly = Polygon(vertices[region])
        poly = Polygon(poly.buffer(0.1))
        split_on_condition(mesh, lambda x, y, z: poly.contains(Point(x, y)) or poly.intersects(Point(x, y)))

@timer_func
def split(mesh):
    print('[INFO] Calling split()')
    regions, vertices = get_regions(mesh)
    split_mesh(mesh, regions, vertices)

class MESH_OT_SPLIT(bpy.types.Operator):
    bl_idname = 'mesh.split'
    bl_label = 'Split'
    
    def execute(self, context):
        split(context.object)
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return context.object is not None