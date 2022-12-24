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
    theta = theta / 180 * math.pi
    phi = phi / 180 * math.pi
    light.location = (math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi))
    set_direction_to(light)

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
