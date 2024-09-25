import bpy
from bpy.types import Panel
from bpy.types import Operator
import numpy as np
import shutil
from .utils import *
from .Light_Op import create_light, set_direction_to
from .Output_Op import get_all
from .exr2png import convert_all

def relight():
    context = bpy.context
    
    output_base_dir = bpy.path.abspath(context.scene.output_dir)
    tmp_dir = mkdir(pjoin(output_base_dir, 'tmp'))
    lds = np.loadtxt(bpy.path.abspath(context.scene.light_direction_filepath))
    
    nLights = lds.shape[0]
    delete_all(context, ['LIGHT'])
    light = create_light(context)
    for i in range(nLights):
        ld = lds[i]
        light.location = ld
        set_direction_to(light)
        get_all(context, tmp_dir, combined=True, shadow=True)
        convert_all(tmp_dir, tmp_dir)
        
        def move(name1, name2):
            shutil.move(pjoin(tmp_dir, f'{name1}.png'), pjoin(output_base_dir, f'{name2}.png'))
        move('image', f'{i:03d}_rgb')
        move('shadow', f'{i:03d}_vis')
        
    # remove tmp directory
    shutil.rmtree(tmp_dir)

class RENDER_OP_RELIGHT(Operator):
    bl_idname = 'render.op_relight'
    bl_label = 'Relight'
    
    def execute(self, context):
        relight()
        return {'FINISHED'}

class HELPER_PT_RELIGHT(Panel):
    bl_label = 'Relight'
    bl_idname = 'HELPER_PT_RELIGHT'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(context.scene, 'light_direction_filepath')
        
        row = layout.row()
        row.operator('render.op_relight')