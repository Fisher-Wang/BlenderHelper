import bpy
import numpy as np
import math
from typing import List

def delete_node(mat, node_name):
    node = mat.node_tree.nodes[node_name]
    mat.node_tree.nodes.remove(node)

def specular2ior(specular: float) -> float:
    return 2 / (1 - math.sqrt(2)/5 * math.sqrt(specular)) - 1

def _random_float(low=0.0, high=1.0):
    return np.random.rand() * (high-low) + low

def _random_color(minGray=0.3) -> List[float]:
    gray = 0
    while gray < minGray:
        r, g, b = np.random.rand(3)
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b 
    return [r, g, b, 1]

def _set_other_bsdf_params(d):
    d['Base Color']              = _random_color()
    d['IOR']                     = specular2ior(d['Specular'])
    d['Specular Tint']           = _random_float()
    d['Sheen']                   = _random_float()
    d['Sheen Tint']              = _random_float()
    d['Clearcoat']               = _random_float()
    d['Clearcoat Roughness']     = _random_float()
    d['Anisotropic']             = _random_float()
    d['Anisotropic Rotation']    = _random_float()

def dict_random_diffuse():
    d = {}
    d['Color'] = _random_color()
    d['Roughness'] = _random_float()
    return d

def dict_random_principled_diffuse(subsurface=False):
    d = {}
    d['Subsurface']          = _random_float() if subsurface else 0
    d['Subsurface Color']    = _random_color()
    d['Metallic']            = 0
    d['Specular']            = _random_float(0, 0.5)
    d['Roughness']           = _random_float()
    _set_other_bsdf_params(d)
    return d

def dict_random_principled_specular(subsurface=False):
    d = {}
    d['Subsurface']          = _random_float() if subsurface else 0
    d['Subsurface Color']    = _random_color()
    d['Metallic']            = 0
    d['Specular']            = _random_float(0.5, 1)
    d['Roughness']           = _random_float()
    _set_other_bsdf_params(d)
    return d

def dict_random_principled_metallic(subsurface=False):
    d = {}
    d['Subsurface']          = _random_float() if subsurface else 0
    d['Subsurface Color']    = _random_color()
    d['Metallic']            = 1
    d['Specular']            = _random_float(0.5, 1)
    d['Roughness']           = _random_float(0.2, 1)
    _set_other_bsdf_params(d)
    return d

def assign_random_material(type):
    material = bpy.data.materials.new(name=f'Random {type}')
    material.use_nodes = True
    delete_node(material, 'Principled BSDF')
    node_tree = material.node_tree
    if type == 'Diffuse1':
        bsdf_node = node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    else:
        bsdf_node = node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    mat_node = node_tree.nodes['Material Output']
    node_tree.links.new(bsdf_node.outputs['BSDF'],
                        mat_node.inputs['Surface'])
    
    if type == 'Diffuse1':
        d = dict_random_diffuse()
    elif type == 'Diffuse2':
        d = dict_random_principled_diffuse()
    elif type == 'Specular':
        d = dict_random_principled_specular()
    elif type == 'Metallic':
        d = dict_random_principled_metallic()
    else:
        raise Exception(f'Unknown material type: {type}')
    
    for key, value in d.items():
        bsdf_node.inputs[key].default_value = value
    
    return material, d