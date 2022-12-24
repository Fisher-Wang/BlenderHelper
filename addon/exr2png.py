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
from utils import mkdir

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

def main(args, src_dir, dst_dir):
    if args.blender_version == '3':
        view_layer_name = 'ViewLayer'
    elif args.blender_version == '2':
        view_layer_name = 'View Layer'
    else:
        raise ValueError('Bad blender version!')
    
    input_exr_path = pjoin(src_dir, 'Normal_gt.exr')
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
    
if  __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender_version', '-b', default='3', choices=['3', '2'])
    parser.add_argument('--dir', '-d', required=True)
    args = parser.parse_args()
    
    main(args, args.dir, args.dir)