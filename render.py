import bpy
import argparse, os, sys

from email.message import EmailMessage
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import smtplib

#######################
## GPU
#######################
def _activate_gpu_blender2x(device_type='CUDA', use_cpus=False):
    ## For Blender 2.8
    ## Ref: https://blender.stackexchange.com/a/156680
    prefs = bpy.context.preferences.addons['cycles'].preferences
    cuda_devices, opencl_devices = prefs.get_devices()
    prefs.compute_device_type = device_type
    
    if device_type == 'CUDA':
        devices = cuda_devices
    elif device_type == 'OPENCL':
        devices = opencl_devices
    else:
        raise Exception(f'Unsupported Device Type: {device_type}')
    
    for device in devices:
        if device.type == "CPU":
            device.use = use_cpus
        else:
            print(f'Activating {device.name}')
            device.use = True

def _activate_gpu_blender3x(device_type='CUDA', use_cpus=False):
    ## For Blender 3.3
    ## Ref: https://blender.stackexchange.com/a/256665
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.refresh_devices()
    devices = prefs.devices

    if not devices:
        raise Exception('Found no devices')

    for device in devices:
        if device.type == "CPU":
            device.use = use_cpus
        else:
            print(f'Activating {device.name}')
            device.use = True

    prefs.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU"

def activate_gpu():
    blender_version: str = bpy.app.version_string
    if blender_version.startswith('2.'):
        _activate_gpu_blender2x()
    elif blender_version.startswith('3.'):
        _activate_gpu_blender3x()
    else:
        raise Exception

######################
## Mail
######################
def send_email(subject, message):
    email_sender = 'wangfeishi@pku.edu.cn'
    email_password = os.environ['password']
    email_receiver = 'wangfeishi@pku.edu.cn'
    hostname = os.uname().nodename

    em = EmailMessage()
    em['From'] = f'{hostname} <{email_sender}>'
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(message)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('mail.pku.edu.cn', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

######################
## Parse Arguments
######################
class ArgumentParserForBlender(argparse.ArgumentParser):
    ## source: https://blender.stackexchange.com/a/134596
    def _get_argv_after_doubledash(self):
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []

    def parse_args(self):
        return super().parse_args(args=self._get_argv_after_doubledash())

def parse_args():
    parser = ArgumentParserForBlender()
    parser.add_argument('--id', '-i', required=True)
    parser.add_argument('--num_light', '-n', type=int, required=True)
    parser.add_argument('--conf', '-c', type=str, required=True)
    parser.add_argument('--result_dir', '-r', type=str, required=True)
    parser.add_argument('--mode', '-m', choices=['standard', 'random', 'mix'], default='mix')
    parser.add_argument('--start_shape', '-s', type=int)
    parser.add_argument('--end_shape', '-e', type=int)
    parser.add_argument('--mesh_dir', required=True)
    parser.add_argument('--no_mail', action='store_true')
    args = parser.parse_args()
    return args

def main_gui():
    pass

def main_cmd():
    activate_gpu()
    args = parse_args()

    scene = bpy.context.scene
    scene.num_light = args.num_light
    scene.yaml_config_path = args.conf
    scene.output_base_dir = args.result_dir
    scene.mesh_dir = args.mesh_dir
    
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 410
    scene.render.resolution_y = 410
    scene.render.image_settings.color_mode = 'RGB'
    scene.cycles.max_bounces = 12
    scene.num_light = 100
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    
    bpy.ops.render.pipeline()

if __name__ == '__main__':    
    bpy.ops.preferences.addon_enable(module='addon2')  ## XXX: addon name
    if bpy.app.background:
        main_cmd()
    else:
        main_gui()