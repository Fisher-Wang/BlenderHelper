import OpenEXR
import Imath
import sys, os, shutil
import scipy.io as scio
import numpy as np
from matplotlib import pyplot as plt
import argparse
from os.path import join as pjoin
from skimage import io, img_as_bool
import yaml
from PIL import Image
import cv2
from glob import glob
from itertools import product
from utils import *

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
    write_mask(output_mask_path, mask)
    
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
            cv2.imwrite(pjoin(dst_dir, f'{i+1:03d}.png'), (imgs[i]*65535).astype('uint16'))
    
    ## Material Params & light directions
    shutil.copy(pjoin(src_dir, 'material_params.yaml'), pjoin(dst_dir, 'material_params.yaml'))
    shutil.copy(pjoin(src_dir, 'light_directions.txt'), pjoin(dst_dir, 'light_directions.txt'))

if  __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', '-d', required=True)
    parser.add_argument('--output_dir', '-o')
    parser.add_argument('--blender_version', '-b', default='3', choices=['3', '2'])
    parser.add_argument('--no_png', action='store_true')
    parser.add_argument('--conf', '-c', default='conf_template.yaml')
    parser.add_argument('--num_light', '-n', required=True, type=int)
    parser.add_argument('--mode', '-m', choices=['standard', 'random'], default='random')
    parser.add_argument('--over_expose', choices=['clip', 'normalize'], default='clip')
    parser.add_argument('--start', '-s', type=int)
    parser.add_argument('--end', '-e', type=int)
    args = parser.parse_args()
    
    conf = read_yaml(args.conf)
    output_dir = args.output_dir if args.output_dir else args.dataset_dir.strip(os.sep) + '_png'
    shape_names = conf['shape_names']
    if args.start is not None:
        shape_names = shape_names[args.start:args.end]
    material_types = []
    for key, value in conf['materials'].items():
        material_types += [key] * value
    scales = conf['scale']
    nrot = conf['nrot']
    angles = (np.arange(nrot) / nrot * 360).astype(int)
    objs = [f'{s}_{i+1}_{m.lower()}_{scale}_{angle}' \
                for s in shape_names \
                for i, m in enumerate(material_types)\
                for scale, angle in product(scales, angles)]
    
    unfinished = []
    for o in objs:
        src_dir = pjoin(args.dataset_dir, o)
        dst_dir = pjoin(output_dir, o)
        if not (pexists(src_dir) and pexists(pjoin(src_dir, f'{args.num_light:03d}.exr'))):
            print(f'[WARN] No src files, Skipping {o}')
            unfinished.append(o)
            continue
        if pexists(pjoin(dst_dir, f'{args.num_light:03d}.png')):
            print(f'[INFO] Skipping {o}')
            continue
        print(f'Processing {o}')
        mkdir(dst_dir)
        main(args, src_dir, dst_dir, num_light=args.num_light)
    write_txt('unfinished.txt', unfinished)