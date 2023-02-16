import os
import yaml
import numpy as np
from skimage import img_as_bool
from PIL import Image
from typing import List
from os.path import join as pjoin
from os.path import exists as pexists

def mkdir(p, exist_ok=True):
    os.makedirs(p, exist_ok=exist_ok)
    return p

def nmap_for_show(nmap):
    return ((nmap+1) / 2 * 255).astype('uint8')

def read_yaml(path):
    with open(path) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data

def write_mask(path, mask):
    if mask.dtype != np.bool_:
        print('[WARN] Input mask is not boolean, converting...')
        mask = img_as_bool(mask)
    image = Image.fromarray(mask)
    image.save(path, bits=1, optimize=True)

def write_txt(path, l: List[str], sep='\n'):
    with open(path, 'w+') as f:
        f.write(sep.join(l))