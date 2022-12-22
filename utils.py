import bpy

def find_all(context, type):
    rst = []
    for o in context.scene.objects:
        if o.type == type:
            rst.append(o)
    return rst