import bpy
import math
import numpy as np
from bpy.types import Operator
from os.path import join as pjoin
from .utils import *
from .Output_Op import get_all

def create_light_base(context, energy, type):
    '''
    #### Parameters
    - `type`: POINT, SUN, ...
    '''
    light_data = bpy.data.lights.new(name="light-data", type=type)
    light_data.energy = energy
    light = bpy.data.objects.new(name=type.title(), object_data=light_data)
    context.collection.objects.link(light)
    return light

def create_light_sun(context):
    return create_light_base(context, energy=1, type='SUN')

def set_light_direction(light, theta, phi):
    location = phi_theta_to_xyz(phi, theta)
    light.location = location
    set_direction_to(light)
    return location

class RENDER_OT_SET_LIGHT_DIRECTION(Operator):
    bl_idname = 'render.set_light_direction'
    bl_label = 'Set Direction'
    
    def execute(self, context):
        lights = find_all(bpy.context, 'LIGHT')
        if lights:
            light = lights[0]
        else:
            light = create_light_sun(context)
        set_light_direction(light, context.scene.theta, context.scene.phi)
        return {'FINISHED'}

def multi_light(context, num_light=3):
    delete_all(context, ['LIGHT'])
    ls = []
    for i in range(num_light):
        light = create_light_sun(context)
        ld = set_light_direction(light, 360 / num_light * i, 45)
        li = light.data.energy
        lc = light.data.color
        ls.append({
            'light_direction': list(ld),
            'light_intensity': li,
            'light_color': list(lc),
        })
    return ls

class RENDER_OT_MULTI_LIGHT(Operator):
    bl_idname = 'render.multi_light'
    bl_label = 'Three Light'
    
    def execute(self, context):
        multi_light(context, num_light=3)
        return {'FINISHED'}

##########################
## Fibonacci Lights
##########################

def fibonacci_sphere(num_sample):
    points = []
    phi = math.pi * (3. - math.sqrt(5.))  # golden angle in radians
    for i in range(num_sample):
        y = 1 - (i / float(num_sample - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y
        theta = phi * i  # golden angle increment
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        points.append((x, y, z))
    return points

def generate_lights_helper(num_sample, phi_min, phi_max):
    fs = fibonacci_sphere(num_sample)
    fs = np.array(fs)
    bound_min = fs[:,2] < math.cos(phi_min/180 * math.pi)
    bound_max = fs[:,2] > math.cos(phi_max/180 * math.pi)
    fs = fs[bound_min & bound_max]
    return fs

def binary_search(f, target, low, high):
    while low <= high:
        mid = (low + high) // 2
        value = f(mid)
        if value == target:
            return mid
        elif value > target:
            high = mid - 1
        else:
            low = mid + 1
    print(mid, f(mid))
    raise ValueError('No value meets target, try changing parameters!')

def generate_lights(num_light, phi_min, phi_max, sample_min=10, sample_max=5000):
    num_sample = binary_search(
        f=lambda x: len(generate_lights_helper(x, phi_min, phi_max)), 
        target=num_light, 
        low=sample_min,
        high=sample_max
    )
    lds = generate_lights_helper(num_sample, phi_min, phi_max)
    lds = lds[np.argsort(lds[:, 2])[::-1]]  # z descending order
    return lds

def render_lighting(context, num_light, phi_min, phi_max, output_dir):    
    delete_all(context, ['LIGHT'])
    light = create_light_sun(context)
    lds = generate_lights(num_light, phi_min, phi_max)
    for i, ld in enumerate(lds):
        light.location = ld * 12
        set_direction_to(light)
        get_all(context, output_dir, name=f'{i+1:03d}', combined=True)
        
    np.savetxt(pjoin(output_dir, 'light_directions.txt'), lds)

class RENDER_OT_LIGHTING(bpy.types.Operator):
    bl_idname = 'render.lighting'
    bl_label = 'Lighting'
    
    def execute(self, context):
        render_lighting(context, context.scene.num_light, context.scene.phi_min, context.scene.phi_max, bpy.path.abspath(context.scene.output_dir))
        return {'FINISHED'}