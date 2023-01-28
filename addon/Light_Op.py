import bpy
import math
import numpy as np
from bpy.types import Operator
from .utils import *

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