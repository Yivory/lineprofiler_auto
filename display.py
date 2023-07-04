# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: controllers\display.py
import numpy as np

class Display(object):

    def __init__(self, interface):
        # self.widget = pg.PlotWidget()
        # self.widget.setAspectLocked()
        self.interface = interface
        self._intensity_threshold = 1
        self.images = []
        # for i in range(4):
        #     image = pg.ImageItem()
        #     self.images.append(image)
        #     self.widget.addItem(image)

    def show_image(self):
        try:
            images = self.interface.current_image.data_rgba_2d
        except ValueError:
            print('No channel visible')
        # else:
        #     images = images / self._intensity_threshold
        #     images = np.clip(images, 0, 255)
        #     for i in range(images.shape[0]):
        #         self.images[i].setImage(images[i].astype(np.uint8))
        #         self.images[i].show()

    def plot_line(self):
        line = self.interface.current_spline
        if line is not None:
            self.line_plot.clear()
            self.line_plot.plot()

    @property
    def intensity_threshold(self):
        return self._intensity_threshold

    @intensity_threshold.setter
    def intensity_threshold(self, value):
        self._intensity_threshold = np.exp(value)
# okay decompiling controllers.display.pyc
