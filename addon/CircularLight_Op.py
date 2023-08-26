import bpy
import math
import numpy as np
from bpy.types import Operator
from os.path import join as pjoin
from .utils import *
from .Output_Op import get_all
from .Light_Op import create_light, set_light_direction

def circular_light(context, num_light=3, phi=45):
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