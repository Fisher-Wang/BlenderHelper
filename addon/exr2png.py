import OpenEXR
import Imath
import scipy.io as scio
import numpy as np
import argparse
from os.path import join as pjoin
from skimage import io, img_as_bool
from PIL import Image
from matplotlib import cm
import matplotlib.pyplot as plt
import cv2
from .utils import *

view_layer_name = 'ViewLayer'

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

def main(src_dir, dst_dir):
    input_exr_path = pjoin(src_dir, 'result_normal_depth.exr')
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

    ## Mask
    mask = ~np.all(normal == 0, axis=-1)
    save_binary_image(output_mask_path, mask)
    
    ## Convert World to Camera
    RT = np.loadtxt(pjoin(src_dir, 'camera_RT.txt'))
    R = RT[:, :3]
    normal[mask] = normal[mask] @ R.T @ np.array(((1, 0, 0), (0, -1, 0), (0, 0, -1)))
    
    ## Save Normal
    print(normal.min(), normal.max())
    io.imsave(output_nmap_png_path, nmap_for_show(normal))
    scio.savemat(output_nmap_path, {'Normal_gt': normal})
    
    ## Depth
    # TODO: mesh are not in same size, maybe convert into pixel unit in order to unify them
    depth = channels[f'{view_layer_name}.Depth.Z'].copy()
    valid = depth != 1e10
    depth[~valid] = np.nan
    depth[~mask] = np.nan
    depth = -depth
    depth -= np.nanmin(depth)  # TODO: use common depth stantard?
    np.save(pjoin(dst_dir, 'Depth.npy'), depth)
    
    ## Depth Preview
    cmap = cm.get_cmap("jet").copy()
    cmap.set_bad(color='white')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.imshow(depth, cmap=cmap)
    plt.colorbar()
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    fig.savefig(pjoin(dst_dir, 'Depth_colorbar.png'), dpi=300, bbox_inches='tight')
    plt.close('all')
    
    norm = plt.Normalize(vmin=np.nanmin(depth), vmax=np.nanmax(depth))
    img = cmap(norm(depth))
    plt.imsave(pjoin(dst_dir, 'Depth.png'), img)

def convert_all(src_dir, dst_dir):
    channels, (h, w) = get_channels_size(pjoin(src_dir, 'result.exr'))
    
    ## Image
    if f'{view_layer_name}.Combined.R' in channels.keys():
        img = np.zeros((h, w, 3))
        img[:, :, 0] = channels[f'{view_layer_name}.Combined.R']
        img[:, :, 1] = channels[f'{view_layer_name}.Combined.G']
        img[:, :, 2] = channels[f'{view_layer_name}.Combined.B']
        img = img / img.max()  # XXX: just for preview
        
        np.save(pjoin(dst_dir, 'image.npy'), img)
        
        img = img[..., ::-1]  # RGB to BGR
        cv2.imwrite(pjoin(dst_dir, 'image.png'), (img*65535).astype('uint16'), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    
    ## Normal & Mask
    if f'{view_layer_name}.Normal.X' in channels.keys():
        normal = np.zeros((h, w, 3))
        normal[..., 0] = channels[f'{view_layer_name}.Normal.X']
        normal[..., 1] = channels[f'{view_layer_name}.Normal.Y']
        normal[..., 2] = channels[f'{view_layer_name}.Normal.Z']
        normal = normalize(normal)
        
        ## Mask
        mask = ~np.all(normal == 0, axis=-1)
        save_binary_image(pjoin(dst_dir, 'mask.png'), mask)

        ## Convert World to Camera
        RT = np.array(read_json(pjoin(src_dir, 'camera.json'))['RT'])
        R = RT[:, :3]
        normal[mask] = normal[mask] @ R.T @ np.array(((1, 0, 0), (0, -1, 0), (0, 0, -1)))
        
        ## Save Normal
        print(normal.min(), normal.max())
        io.imsave(pjoin(dst_dir, 'Normal_gt.png'), nmap_for_show(normal))
        np.save(pjoin(dst_dir, 'Normal_gt.npy'), normal)
        scio.savemat(pjoin(dst_dir, 'Normal_gt.mat'), {'Normal_gt': normal})
        
    ## Depth
    if f'{view_layer_name}.Depth.Z' in channels.keys():
        ## Depth
        # TODO: mesh are not in same size, maybe convert into pixel unit in order to unify them
        depth = channels[f'{view_layer_name}.Depth.Z'].copy()
        valid = depth != 1e10
        depth[~valid] = np.nan
        depth[~mask] = np.nan
        np.save(pjoin(dst_dir, 'Depth.npy'), depth)
        
        ## Depth Preview
        depth = -depth
        depth -= np.nanmin(depth)  # TODO: use common depth stantard?
        
        cmap = cm.get_cmap("jet").copy()
        cmap.set_bad(color='white')
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.imshow(depth, cmap=cmap)
        plt.colorbar()
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        fig.savefig(pjoin(dst_dir, 'Depth_colorbar.png'), dpi=300, bbox_inches='tight')
        plt.close('all')
        
        norm = plt.Normalize(vmin=np.nanmin(depth), vmax=np.nanmax(depth))
        img = cmap(norm(depth))
        plt.imsave(pjoin(dst_dir, 'Depth.png'), img)

    ## Albedo
    if f'{view_layer_name}.DiffCol.R' in channels.keys():
        img = np.zeros((h, w, 3))
        img[:, :, 0] = channels[f'{view_layer_name}.DiffCol.R']
        img[:, :, 1] = channels[f'{view_layer_name}.DiffCol.G']
        img[:, :, 2] = channels[f'{view_layer_name}.DiffCol.B']
        np.save(pjoin(dst_dir, 'albedo.npy'), img)
        
        img = img / img.max()  # XXX: just for preview
        img = img[..., ::-1]  # RGB to BGR
        cv2.imwrite(pjoin(dst_dir, 'preview_albedo.png'), (img*65535).astype('uint16'), [cv2.IMWRITE_PNG_COMPRESSION, 9])

if  __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender_version', '-b', default='3', choices=['3', '2'])
    parser.add_argument('--dir', '-d', required=True)
    args = parser.parse_args()
    
    if args.blender_version == '2':
        view_layer_name = 'View Layer'
    
    main(args.dir, args.dir)