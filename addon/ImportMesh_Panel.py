import bpy
from bpy.types import Panel

class HELPER_PT_IMPORT_MESH(Panel):
    bl_label = 'Import Mesh'
    bl_idname = 'HELPER_PT_IMPORT_MESH'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenderHelper'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'mesh_path')
        row = layout.row()
        row.operator('import_mesh.any', text='Import')
        row = layout.row()
        row.operator('mesh.measure')
        row = layout.row()
        row.prop(context.scene, 'output_dir')