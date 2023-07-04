# -*- coding: utf-8 -*-
from _datetime import datetime
import json
import os
import shutil
import traceback

import numpy as np

from image import ImageSIM
from interface import Interface


def get_stime():
    return str(datetime.now()).split('.')[0].replace('-', '').replace(' ', '').replace(':', '')


if __name__ == "__main__":
    image_path = 'images'
    temp_images='temp_images'
    if os.path.exists(temp_images):
        shutil.rmtree(temp_images)
    os.mkdir(temp_images)
    with open('config.json', 'r') as f:
        param_dict = json.load(f)
    blur_min, blur_max , blur_step= param_dict['blur']
    spline_min, spline_max, spline_step = param_dict['spline']
    intensity_min, intensity_max, intensity_step = param_dict['intensity']
    lower_dist_min, lower_dist_max, lower_dist_step = param_dict['lower_dist']
    upper_dist_min, upper_dist_max, upper_dist_step = param_dict['upper_dist']
    pixel_size_min, pixel_size_max, pixel_size_step = param_dict['pixel_size']
    profile_width_min, profile_width_max, profile_width_step = param_dict['profile_width']

    if blur_step==0:
        blur_array=[blur_min]
    else:
        blur_array = np.linspace(blur_min, blur_max, int((blur_max - blur_min) / blur_step) + 1)

    if spline_step == 0:
        spline_array = [spline_min]
    else:
        spline_array = np.linspace(spline_min, spline_max, int((spline_max - spline_min) / spline_step) + 1)

    if intensity_step == 0:
        intensity_array = [intensity_min]
    else:
        intensity_array = np.linspace(intensity_min, intensity_max, int((intensity_max - intensity_min) / intensity_step) + 1)

    if lower_dist_step == 0:
        lower_dist_array = [lower_dist_min]
    else:
        lower_dist_array = np.linspace(lower_dist_min, lower_dist_max, int((lower_dist_min - lower_dist_max) / lower_dist_step) + 1)

    if upper_dist_step == 0:
        upper_dist_array = [upper_dist_min]
    else:
        upper_dist_array = np.linspace(upper_dist_min, upper_dist_max, int((upper_dist_min - upper_dist_max) / upper_dist_step) + 1)

    if pixel_size_step == 0:
        pixel_size_array = [pixel_size_min]
    else:
        pixel_size_array = np.linspace(pixel_size_min, pixel_size_max, int((pixel_size_min - pixel_size_max) / pixel_size_step) + 1)

    if profile_width_step == 0:
        profile_width_array = [profile_width_min]
    else:
        profile_width_array = np.linspace(profile_width_min, profile_width_max, int((profile_width_max - profile_width_min) / profile_width_step) + 1)
    for image_file in os.listdir(image_path):
        file_path = f'{image_path}/{image_file}'
        file_name_suffix = image_file
        if 'tiff' in file_name_suffix:
            file_name = file_name_suffix.split('.tiff')[0]
            suffix = '.tiff'
        else:
            file_name = file_name_suffix.split('.tif')[0]
            suffix = '.tif'
        for blur in blur_array:
            for spline in spline_array:
                for intensity in intensity_array:
                    for lower_dist in lower_dist_array:
                        for upper_dist in upper_dist_array:
                            for pixel_size in pixel_size_array:
                                for profile_width in profile_width_array:
                                    _blur = int(blur)
                                    _spline = round(float(spline), 1)
                                    _intensity = round(float(intensity), 1)
                                    _lower_dist = int(lower_dist)
                                    _upper_dist = int(upper_dist)
                                    _pixel_size = round(float(pixel_size), 2)
                                    _profile_width = int(profile_width)
                                    params = {
                                        'blur': _blur,
                                        'spline': _spline,
                                        'intensity': _intensity,
                                        'lower': _lower_dist,
                                        'upper': _upper_dist,
                                        'pixel_size': _pixel_size,
                                        'profile': _profile_width,
                                    }
                                    target_file = f'{temp_images}/{file_name}_{get_stime()}_{_blur=}{_spline=}{_intensity=}{_lower_dist=}{_upper_dist=}{_pixel_size=}{_profile_width=}_{suffix}'
                                    shutil.copy(file_path, target_file)
                                    print(f'{datetime.now()} start params={params} on file={file_path}')
                                    try:
                                        my_interface = Interface()
                                        my_interface.show_image(ImageSIM(target_file))
                                        my_interface.start_thread(params)
                                    except Exception as e:
                                        print(traceback.format_exc())
                                    os.remove(target_file)
    if os.path.exists(temp_images):
        shutil.rmtree(temp_images)
