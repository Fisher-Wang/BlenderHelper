import OpenEXR
import Imath
import sys, os, shutil
import scipy.io as scio
import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import normalize
import argparse
from os.path import join as pjoin
from skimage import io, img_as_bool
import yaml
from PIL import Image
import cv2
from glob import glob
from itertools import product

def mkdir(p, exist_ok=True):
    os.makedirs(p, exist_ok=exist_ok)
    return p

def nmap_for_show(nmap):
    return ((nmap+1) / 2 * 255).astype('uint8')

def split_channel(f, channel, float_flag=True):
    dw = f.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    if float_flag:
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
    else:
        pt = Imath.PixelType(Imath.PixelType.HALF)
    channel_str = f.channel(channel, pt)
    img = np.frombuffer(channel_str, dtype=np.float32)
    img.shape = (size[1], size[0])
    return img

def get_channels_size(exr_path):
    f = OpenEXR.InputFile(exr_path)
    dw = f.header()['dataWindow']
    size = (dw.max.y - dw.min.y + 1, dw.max.x - dw.min.x + 1)
    channels = dict()
    for channel_name in f.header()["channels"]:
        channels[channel_name] = split_channel(f, channel_name)
    f.close()
    return channels, size

def save_binary_image(fname, binary_image):
    img = Image.fromarray(img_as_bool(binary_image))
    img.save(fname, bits=1)

def normalize(arr):
    norm = np.linalg.norm(arr, axis=-1)
    valid = norm != 0
    arr[valid] = arr[valid] / norm[valid][..., None]
    return arr

def main(args, src_dir, dst_dir, num_light=1000):
    if args.blender_version == '3':
        view_layer_name = 'ViewLayer'
    elif args.blender_version == '2':
        view_layer_name = 'View Layer'
    else:
        raise ValueError('Bad blender version!')
    
    input_exr_path = pjoin(src_dir, 'result_normal.exr')
    output_nmap_path = pjoin(dst_dir, 'Normal_gt.mat')
    output_nmap_png_path = pjoin(dst_dir, 'Normal_gt.png')
    output_mask_path = pjoin(dst_dir, 'mask.png')

    ## Normal GT
    channels, (h, w) = get_channels_size(input_exr_path)
    normal = np.zeros((h, w, 3))
    normal[..., 0] = channels[f'{view_layer_name}.Normal.X']
    normal[..., 1] = channels[f'{view_layer_name}.Normal.Y']
    normal[..., 2] = channels[f'{view_layer_name}.Normal.Z']
    normal = normalize(normal)
    print(normal.min(), normal.max())
    io.imsave(output_nmap_png_path, nmap_for_show(normal))
    scio.savemat(output_nmap_path, {'Normal_gt': normal})

    ## Mask
    mask = ~np.all(normal == 0, axis=-1)
    save_binary_image(output_mask_path, mask)
    
    ## Light Intensities
    ones = np.ones((num_light, 3), dtype=int)
    np.savetxt(pjoin(dst_dir, 'light_intensities.txt'), ones)
    
    ## Filenames
    filenames = [f'{i:03d}.png' for i in range(1, num_light+1)]
    with open(pjoin(dst_dir, 'filenames.txt'), 'w+') as f:
        f.write('\n'.join(filenames))
    
    ## Images
    if not args.no_png:
        imgs = np.zeros((num_light, h, w, 3))
        for i in range(num_light):
            channels, (h, w) = get_channels_size(pjoin(src_dir, f'{i+1:03d}.exr'))
            imgs[i, :, :, 0] = channels[f'{view_layer_name}.Combined.R']
            imgs[i, :, :, 1] = channels[f'{view_layer_name}.Combined.G']
            imgs[i, :, :, 2] = channels[f'{view_layer_name}.Combined.B']

        if args.over_expose == 'normalize':
            imgs = imgs / imgs.max()
        elif args.over_expose == 'clip':
            imgs[imgs > 1] = 1
        else:
            raise
        
        imgs = imgs[..., ::-1]  # RGB to BGR
        
        for i in range(num_light):
            cv2.imwrite(pjoin(dst_dir, f'{i+1:03d}.png'), (imgs[i]*65535).astype('uint16'), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    
    ## Material Params & light directions
    shutil.copy(pjoin(src_dir, 'material_params.yaml'), pjoin(dst_dir, 'material_params.yaml'))
    shutil.copy(pjoin(src_dir, 'light_directions.txt'), pjoin(dst_dir, 'light_directions.txt'))

if  __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', '-d', required=True)
    parser.add_argument('--output_dir', '-o', required=True)
    parser.add_argument('--blender_version', '-b', default='3', choices=['3', '2'])
    parser.add_argument('--no_png', action='store_true')
    parser.add_argument('--conf', '-c', default='conf_template.yaml')
    parser.add_argument('--num_light', '-n', required=True, type=int)
    parser.add_argument('--mode', '-m', choices=['standard', 'random'], default='random')
    parser.add_argument('--over_expose', choices=['clip', 'normalize'], default='clip')
    args = parser.parse_args()
    
    if args.mode == 'standard':
        with open(args.conf) as f:
            conf = yaml.load(f, yaml.FullLoader)
            shape_names = conf['obj_names']
            mat_names = conf['texture_names']
        
        for s in shape_names:
            for m in mat_names:
                for scale, angle in product([0.5, 1, 2], range(0, 360, 360//5)):
                    o = f'{s}_{m.lower()}_{scale}_{angle}'
                    src_dir = pjoin(args.dataset_dir, o)
                    if not (os.path.exists(src_dir) and os.listdir(src_dir) and os.path.exists(pjoin(src_dir, '001.exr'))):
                        print(f'skipped {o}')
                        continue
                    dst_dir = mkdir(pjoin(args.output_dir, o))
                    print(f'processing {o}')
                    main(args, src_dir, dst_dir, num_light=args.num_light)

    elif args.mode == 'random':
        with open(args.conf) as f:
            conf = yaml.load(f, yaml.FullLoader)
            shape_names = conf['shape_names']
        material_types = []
        for key, value in conf['materials'].items():
            material_types += [key] * value
        objs = [f'{s}_{i+1}_{m.lower()}_{scale}_{angle}' \
                    for s in shape_names \
                    for i, m in enumerate(material_types)\
                    for scale, angle in product([0.5, 1, 2], range(0, 360, 360//5))]
        for o in objs:
            src_dir = pjoin(args.dataset_dir, o)
            if not (os.path.exists(src_dir) and os.listdir(src_dir) and os.path.exists(pjoin(src_dir, '001.exr'))):
                print(f'skipped {o}')
                continue
            dst_dir = mkdir(pjoin(args.output_dir, o))
            print(f'processing {o}')
            main(args, src_dir, dst_dir, num_light=args.num_light)
    
    else:
        raise Exception(f'Unknown mode: {args.mode}')