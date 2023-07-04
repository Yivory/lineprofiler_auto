# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: controllers\factory.py
import processing_microtubule

def process_factory(microscope_image, config, fit_func, tear_down, ID):

    process = processing_microtubule.QProcessThread()

    process.set_data(ID, microscope_image.data, microscope_image.file_path)
    if microscope_image.data_z is not None:
        process.data_z = microscope_image.data_z
    for k in config.keys():
        setattr(process, k, config[k])

    process.sig_plot_data.connect(fit_func)
    process.done.connect(tear_down)
    return process
# okay decompiling controllers.factory.pyc
