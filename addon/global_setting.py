import bpy

def global_setting():
    context = bpy.context
    context.scene.render.resolution_x = 1000
    context.scene.render.resolution_y = 1000
