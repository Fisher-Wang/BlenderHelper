import bpy
import math
import numpy as np
from typing import List, Dict
from bpy.types import Operator
from os.path import join as pjoin
from .utils import *
from .Output_Op import get_all
from .Light_Op import create_light, set_light_direction
from .ImportMesh_Op import import_mesh, move_to_right_place
from .exr2png import convert_all
from .Camera_Op import add_orthographic_camera
from .MeshMeasure_Op import mesh_measure

def circular_light(context: bpy.context, num_light=3, phi=45):
    delete_all(context, ['LIGHT'])
    ls = []
    for i in range(num_light):
        light = create_light(context)
        ld = set_light_direction(light, 360 / num_light * i, phi)
        li = light.data.energy
        lc = light.data.color
        ls.append({
            'light_direction': list(ld),
            'light_intensity': li,
            'light_color': list(lc),
        })
    return ls

class RENDER_OT_CIRCULAR_LIGHT(Operator):
    bl_idname = 'render.set_circular_light'
    bl_label = 'Set Circular Lights'
    
    def execute(self, context):
        circular_light(context, num_light=context.scene.num_circular_lights, phi=context.scene.circular_phi)
        return {'FINISHED'}

def pipeline_circular_light(context: bpy.context, **kargs):
    input_dir: str = kargs['input_dir']
    output_base_dir: str = kargs['output_dir']
    
    ## Configs Iodo(rjj):set light get!
    context.scene.render.resolution_x = 400
    context.scene.render.resolution_y = 400
    phi_min = 5
    phi_max = 90
    phi_nums = 40   # delta phi 2 [min,max]
    num_lights = 72 # delta theta 5
    ###-------Light Setting---------###


    ###-------Path Setting---------###
    objs = os.listdir(input_dir)

    # iterations
    phis = np.linspace(phi_min, phi_max, phi_nums)
    thetas = np.linspace(0, 360, num_lights, endpoint=False)
    
    delete_all(context, ['LIGHT', 'MESH', 'CAMERA'])
    light = create_light(context)
    
    for o in objs:
        O = o.split('.')[0]
        output_obj_dir = mkdir(pjoin(output_base_dir, O))
        mesh_path = pjoin(input_dir, o)
        import_mesh(mesh_path)
        mesh = context.object
        move_to_right_place(mesh)
        mesh_measure(mesh)
        delete_all(context, ['CAMERA'])
        add_orthographic_camera(context)
        
        get_all(context, output_obj_dir, 'result', normal=True)
        # convert_all(output_obj_dir, output_obj_dir, 'result', delete_exr=True)
        for phi in phis:
            for theta in thetas:
                light.location = phi_theta_to_xyz(phi, theta)
                set_direction_to(light)
                name = f'phi={phi:.1f}_theta={theta:.1f}'
                get_all(context, output_obj_dir, name, combined=True)
                # convert_all(output_obj_dir, output_obj_dir, name, delete_exr=True)

def pipeline_circular_light_2(context: bpy.context, **kargs):
    input_dir: str = kargs['input_dir']
    output_base_dir: str = kargs['output_dir']
    conf_path: str = kargs['conf_path']
    
    conf = read_json(conf_path)
    objs = os.listdir(input_dir)
    light_sets: List[Dict[str, List[int]]] = conf['render']
    numLights = conf['numLights']
    assert numLights == len(light_sets)
    
    context.scene.render.resolution_x = 400
    context.scene.render.resolution_y = 400
    
    for o in objs:
        O = o.split('.')[0]
        output_obj_dir = mkdir(pjoin(output_base_dir, O))
        mesh_path = pjoin(input_dir, o)
        import_mesh(mesh_path)
        mesh = context.object
        move_to_right_place(mesh)
        mesh_measure(mesh)
        delete_all(context, ['CAMERA'])
        add_orthographic_camera(context)
        
        ## Normal
        get_all(context, output_obj_dir, 'result', normal=True)
        convert_all(output_obj_dir, output_obj_dir, 'result', delete_exr=True)
        
        ## Observed image with a lot of light set
        for idx, light_set in enumerate(light_sets):
            delete_all(context, ['LIGHT'])
            
            for light_id, color in light_set.items():
                light_id = int(light_id)
                light = create_light(context)
                theta = light_id / numLights * 2 * math.pi
                light.location.x = math.cos(theta) * conf['common']['radius']
                light.location.y = math.sin(theta) * conf['common']['radius']
                light.location.z = conf['common']['height']
                light.data.color = color
                set_direction_to(light)
                
            name = f'{idx:03d}'
            get_all(context, output_obj_dir, name, combined=True)
            convert_all(output_obj_dir, output_obj_dir, name, delete_exr=True)

class RENDER_OT_PIPELINE_CIRCULAR_LIGHT(Operator):
    bl_idname = 'render.pipeline_circular_light'
    bl_label = 'Pipeline circular lights'
    
    def execute(self, context: bpy.context):
        pipeline_circular_light(context, input_dir=context.scene.mesh_dir, output_dir=context.scene.output_dir)
        return {'FINISHED'}

class RENDER_OT_PIPELINE_CIRCULAR_LIGHT_2(Operator):
    bl_idname = 'render.pipeline_circular_light_2'
    bl_label = 'Pipeline circular lights 2'
    
    def execute(self, context: bpy.context):
        pipeline_circular_light_2(context, input_dir=context.scene.mesh_dir, output_dir=context.scene.output_dir, conf_path=bpy.path.abspath(context.scene.conf_path))
        return {'FINISHED'}