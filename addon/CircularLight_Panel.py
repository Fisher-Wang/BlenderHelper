import bpy
from bpy.types import Panel

class HELPER_PT_CIRCULAR_LIGHT(Panel):
    bl_label = 'Circular Light'
    bl_idname = 'HELPER_PT_CIRCULAR_LIGHT'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVPSRenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'circular_phi')
        row = layout.row()
        row.prop(context.scene, 'num_circular_lights')
        row = layout.row()
        row.prop(context.scene, 'mesh_dir')
        row = layout.row()
        row.prop(context.scene, 'output_dir')
        row = layout.row()
        row.operator('render.set_circular_light', icon='SNAP_NORMAL')
        row = layout.row()
        row.operator('render.pipeline_circular_light', icon='SNAP_NORMAL')