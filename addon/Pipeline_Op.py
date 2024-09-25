import bpy
import numpy as np
import yaml
from bpy.types import Operator
from os.path import join as pjoin
from os.path import exists as pexists
from .utils import *
from .ImportMesh_Op import *
from .Camera_Op import *
from .Light_Op import *
from .Output_Op import *
from .SplitMesh_Op import *
from .Material_Op import assign_random_material
from .Transform_Op import trans_rotate, trans_scale_z
from itertools import product

def pipeline_ColorPSNeRF_old(obj_dir, output_base_dir, obj_names):
    context = bpy.context
    for obj_name in obj_names:
        output_dir = mkdir(pjoin(output_base_dir, obj_name))
        
        ## Add Camera
        delete_all(context, 'CAMERA')
        # bpy.ops.object.camera_add(location=(0, 0, 8), rotation=(0, 0, -1))  # duck
        bpy.ops.object.camera_add(location=(0, 0, 2500), rotation=(0, 0, -1))  # whale
        camera = context.scene.camera = context.object
        camera.data.clip_end = 10000  # XXX: increase this value when rendered result is blank!
        
        ## Set Camera
        set_camera_pos(camera, 45, 0)
        
        ## Add Light
        ls = multi_light(context, 3)
        write_json(pjoin(output_dir, 'light_information.json'), ls)
        
        ## Set Light
        # TODO
        
        ## Animation
        frame_start, frame_end = get_frame_range_scene(context.scene)
        for frame in range(frame_start, frame_end+1):
            if frame > 10: break
            od = mkdir(pjoin(output_dir, f'frame_{frame:03d}'))
            context.scene.frame_set(frame)
            get_camera(camera, od)
            
            switch_cast_shadow(context, enable=True)
            get_all(context, od, normal=True, depth=True, albedo=True, combined=True)
            convert_all(od, od)
            os.rename(pjoin(od, 'image.png'), pjoin(od, 'image_shadow.png'))
            os.rename(pjoin(od, 'image.npy'), pjoin(od, 'image_shadow.npy'))
            
            switch_cast_shadow(context, enable=False)
            get_all(context, od, combined=True)
            convert_all(od, od)

def pipeline_ColorPSNeRF(output_base_dir):
    context = bpy.context
    
    ## Config
    context.scene.cycles.max_bounces = 0
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    context.scene.render.resolution_x = 512
    context.scene.render.resolution_y = 512
    
    cur_dir = r'C:\fsw\code\psnerf_dataset\addon'
    data = read_json(pjoin(cur_dir, 'data/s3nerf.json'))
    lds = data['light_directions']
    K, R, T = np.array(data['K']), np.array(data['R']), np.array(data['T'])
    delete_all(context, ['CAMERA'])
    camera = get_blender_camera_from_KRT(K, R, T, 1)
    
    objs = ['bunny']
    output_base_dir = pjoin(r'C:\fsw\code\psnerf_dataset', 'output_dataset')
    for o in objs:
        output_dir = mkdir(pjoin(output_base_dir, o))
        tmp_dir = mkdir(pjoin(output_dir, 'tmp'))
        rgb_dir = mkdir(pjoin(output_dir, 'rgb'))
        vis_dir = mkdir(pjoin(output_dir, 'visibility'))
        
        get_camera(camera, tmp_dir)
        get_all(context, tmp_dir, normal=True, depth=True, albedo=True)
        convert_all(tmp_dir, tmp_dir)
        
        ## Convert to S3NeRF format
        shutil.move(pjoin(tmp_dir, 'Normal_gt.png'), pjoin(output_dir, 'normal.png'))
        shutil.move(pjoin(tmp_dir, 'Normal_gt.npy'), pjoin(output_dir, 'normal.npy'))
        shutil.move(pjoin(tmp_dir, 'Depth.npy'), pjoin(output_dir, 'depth.npy'))
        shutil.move(pjoin(tmp_dir, 'albedo.npy'), pjoin(output_dir, 'albedo.npy'))
        
        
        
        for i, ld in enumerate(lds):
            delete_all(context, ['LIGHT'])
            light = create_light(context, type='POINT', energy=100)
            light.location = ld
            light.data.shadow_soft_size = 0  # no soft shadow
            
            switch_cast_shadow(context, enable=True)
            get_all(context, tmp_dir, normal=True, depth=True, albedo=True, combined=True, shadow=True)
            convert_all(tmp_dir, tmp_dir)

            ## Convert to S3NeRF format
            shutil.move(pjoin(tmp_dir, 'image.png'), pjoin(rgb_dir, f'{i+1:03d}.png'))
            shutil.move(pjoin(tmp_dir, 'image.npy'), pjoin(rgb_dir, f'{i+1:03d}.npy'))
            shutil.move(pjoin(tmp_dir, 'shadow.png'), pjoin(vis_dir, f'{i+1:03d}.png'))
            shutil.move(pjoin(tmp_dir, 'shadow.npy'), pjoin(vis_dir, f'{i+1:03d}.npy'))
            
            # if i > 0: break
        
        for mesh in find_all(context, 'MESH'):
            mesh.hide_render = not mesh.name == o
        get_all(context, tmp_dir, normal=True)
        convert_all(tmp_dir, tmp_dir)
        shutil.move(pjoin(tmp_dir, 'mask.png'), pjoin(output_dir, 'mask_obj.png'))
        
        #* comment this when debugging
        # shutil.rmtree(tmp_dir)
        
        ###################################
        ## Convert to Jipeng's format (also for S3NeRF format)
        ###################################
        ## Light Directions 
        np.save(pjoin(output_dir, 'light_dirs.npy'), lds)

        ## Images
        imgs = []
        for i in range(len(lds)):
            img = np.load(pjoin(rgb_dir, f'{i+1:03d}.npy'))
            imgs.append(img)
        imgs = np.array(imgs)
        imgs /= imgs.max()  # normalize to 0~1
        np.save(pjoin(output_dir, 'imgs.npy'), imgs)
        # for S3NeRF
        for i, img in enumerate(imgs):
            cv2.imwrite(pjoin(rgb_dir, f'{i+1:03d}.png'), (img*255).astype('uint8'), [cv2.IMWRITE_PNG_COMPRESSION, 9])
        
        ## Mask
        from skimage import io, img_as_bool
        mask = img_as_bool(io.imread(pjoin(output_dir, 'mask_obj.png')))
        np.save(pjoin(output_dir, 'mask.npy'), mask)
        
        ## Visibility
        viss = []
        for i in range(len(lds)):
            vis = np.load(pjoin(vis_dir, f'{i+1:03d}.npy'))
            viss.append(vis)
        viss = np.array(viss)
        np.save(pjoin(output_dir, 'viss.npy'), viss)
        
        ## Normal
        shutil.copy(pjoin(output_dir, 'normal.npy'), pjoin(output_dir, 'normal_obj.npy'))
        

class RENDER_OT_PIPELINE_COLORPSNERF(Operator):
    bl_idname = 'render.pipeline_colorpsnerf'
    bl_label = 'Pipeline ColorPSNeRF'
    
    def execute(self, context):
        pipeline_ColorPSNeRF(bpy.path.abspath(context.scene.output_dir))
        return {'FINISHED'}

def pipeline(mesh_dir, output_base_dir, params):
    shapes    = params['shapes']
    materials = params['materials']
    scales    = params['scales']
    angles    = params['angles']
    
    context = bpy.context
    for mesh_name, (i, material_type), scale, angle in product(
        shapes, enumerate(materials), scales, angles):
        
        o = f'{mesh_name}_{i+1}_{material_type.lower()}_{scale}_{angle}'
        output_dir = mkdir(pjoin(output_base_dir, o))
        
        if pexists(pjoin(output_dir, f'{context.scene.num_light:03d}.exr')):
            print(f'[INFO] Skipping {o}')
            continue
        
        print(mesh_name, output_dir)
        
        ## Clear
        delete_all(context, ['MESH'])

        ## Import Mesh
        mesh_path = pjoin(mesh_dir, f'{mesh_name}.stl')
        import_mesh(mesh_path)
        mesh = context.object
        move_to_right_place(mesh)
        add_orthographic_camera(context)
        
        ## Transform
        trans_rotate(mesh, angle)
        trans_scale_z(mesh, scale)
        
        # ## Split Mesh
        # print('Splitting Object')
        # select_one(context, mesh)
        # split(mesh)
        
        # ## Attach Material
        # meshes = find_all(context, 'MESH')
        # all_material_params = {}
        # for mesh in meshes:
        #     material, material_params = assign_random_material(material_type)
        #     mesh.data.materials.append(material)
        #     all_material_params[mesh.name] = material_params
        
        # write_yaml(pjoin(output_dir, 'material_params.yaml'), all_material_params)
        material, material_params = assign_random_material(material_type)
        mesh.data.materials.append(material)
        
        ## Render Normal Map
        get_all(context, output_dir, name='result_normal', normal=True)
        
        ## Render Lighting
        render_lighting(context, context.scene.num_light, context.scene.phi_min, context.scene.phi_max, output_dir)

class RENDER_OT_PIPELINE(Operator):
    bl_idname = 'render.pipeline'
    bl_label = 'Pipeline'
    
    def execute(self, context):
        conf = read_yaml(bpy.path.abspath(context.scene.yaml_config_path))
        
        shapes = conf['shape_names']
        if context.scene.start_shape is not None:
            shapes = shapes[context.scene.start_shape: context.scene.end_shape]
        
        materials = []
        for key, value in conf['materials'].items():
            materials += [key] * value
        
        scales = conf['scale']
        nrot = conf['nrot']
        angles = conf['angles'] if 'angles' in conf else (np.arange(nrot) / nrot * 360).astype(int)
        
        params = {
            "shapes": shapes,
            "materials": materials,
            "scales": scales,
            "angles": angles,
        }
        
        pipeline(
            mesh_dir=bpy.path.abspath(context.scene.mesh_dir),
            output_base_dir=bpy.path.abspath(context.scene.output_base_dir),
            params=params
        )
        return {'FINISHED'}
