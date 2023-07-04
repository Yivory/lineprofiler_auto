# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: controllers\interface.py
from display import *
from fitter import Fit, Hist
from factory import process_factory


class Interface:

    def __init__(self):
        self.current_image = None
        self.display = Display(self)
        # self.main_window.viewer_container_layout.addWidget(self.display.widget)
        self.intensity_threshold = 30
        self.pixel_size = 0.01
        self.current_spline = None
        self.fitter = Fit()
        # self.checkbox_values_changed()
        # self.set_operation_mode(self.main_window.comboBox_operation_mode.currentText())
        self.config = {'intensity_threshold': '0',
                       'px_size': '0',
                       'blur': '0',
                       'spline_parameter': '0',
                       'distance_threshold': '0',
                       'upper_limit': '0',
                       'lower_limit': '0',
                       'profil_width': '0'}
        # self.main_window.horizontalSlider_intensity_threshold.valueChanged.connect((lambda v: (
        #  setattr(self.display, 'intensity_threshold', v / 10), self.slider_threshold_changed())))
        self.processes = dict()
        self.processID = 0

    def del_process(self, id):
        process, progress_bar = self.processes.pop(str(id))
        # self.main_window.annihilate_progress_bar(progress_bar)

    def start_thread(self, params):
        self.update_config(params)
        self.processID += 1
        # progress_bar = self.main_window.create_progress_bar()
        # progress_bar.setFormat(self.current_image.file_path.split('/')[-1])
        process = process_factory(self.current_image, self.config, self.fit_data, self.del_process, self.processID)
        self.processes[str(self.processID)] = (process, None)
        process.run()

    def fit_data(self, data, center, i, path, color, size):
        self.fitter.fit_data(data, center=center, nth_line=i, path=path, c=color,
                             n_profiles=size)

    def set_channel_color(self):
        pass

    def update_config(self, params):
        self.config['intensity_threshold'] = params['intensity']
        self.config['px_size'] = params['pixel_size']
        self.config['spline_parameter'] = params['spline']
        self.config['blur'] = params['blur']
        self.config['distance_threshold'] = params['lower']
        self.config['upper_limit'] = params['upper']
        self.config['lower_limit'] = params['lower']
        self.config['profil_width'] = params['profile']

    def set_operation_mode(self, value):
        if value == 'Microtubule':
            self.main_window.checkBox_multi_cylidner_projection.setEnabled(True)
            self.main_window.checkBox_multi_cylidner_projection.setChecked(True)
            self.main_window.checkBox_cylinder_projection.setEnabled(True)
            self.main_window.checkBox_cylinder_projection.setChecked(True)
            self.main_window.doubleSpinBox_expansion_factor.setEnabled(True)
            self.main_window.spinBox_lower_limit.setEnabled(False)
            self.main_window.spinBox_upper_limit.setEnabled(False)
            self.main_window.spinBox_px_size.setValue(0.01)
            self.main_window.spinBox_gaussian_blur.setValue(20)
        else:
            if value == 'SNC':
                self.main_window.checkBox_multi_cylidner_projection.setEnabled(False)
                self.main_window.checkBox_multi_cylidner_projection.setChecked(False)
                self.main_window.checkBox_cylinder_projection.setEnabled(False)
                self.main_window.checkBox_cylinder_projection.setChecked(False)
                self.main_window.doubleSpinBox_expansion_factor.setEnabled(False)
                self.main_window.spinBox_lower_limit.setEnabled(True)
                self.main_window.spinBox_upper_limit.setEnabled(True)
                self.main_window.spinBox_px_size.setValue(0.032)
                self.main_window.spinBox_gaussian_blur.setValue(20)
            elif value == 'SNC one channel':
                self.main_window.checkBox_multi_cylidner_projection.setEnabled(False)
                self.main_window.checkBox_multi_cylidner_projection.setChecked(False)
                self.main_window.checkBox_cylinder_projection.setEnabled(False)
                self.main_window.checkBox_cylinder_projection.setChecked(False)
                self.main_window.doubleSpinBox_expansion_factor.setEnabled(False)
                self.main_window.spinBox_lower_limit.setEnabled(True)
                self.main_window.spinBox_upper_limit.setEnabled(True)
                self.main_window.spinBox_px_size.setValue(0.032)
                self.main_window.spinBox_gaussian_blur.setValue(9)

    def process_finished(self):
        self.main_window._process_finished()

    def set_channel_visible(self, i, enabled):
        self.current_image.channel = (
            i, enabled)
        self.display.show_image()

    def slider_changed(self, ch, i):
        self.current_image.index = (
            ch, i)

    def slider_threshold_changed(self):
        try:
            self.display.show_image()
        except:
            ValueError('No image')

    def expansion_factor_changed(self, value):
        self.fitter.expansion = value

    def checkbox_values_changed(self):
        functions = []
        for box in self.main_window.plot_parameters:
            if box.isChecked():
                functions.append(box.text().lower())

        if len(functions) == 0:
            raise ValueError('Select minimum one checkbox')
        self.fitter.fit_functions = functions

    def show_image(self, image):
        if image.isParsingNeeded:
            image.parse(calibration_px=(self.pixel_size))
        self.current_image = image
        # for i in range(self.current_image.metaData['ShapeSizeC']):
        #     box = getattr(self.main_window, 'checkBox_channel' + str(i))
        #     box.setEnabled(True)
        #     slider = getattr(self.main_window, 'slider_channel' + str(i) + '_slice')
        #     slider.setMaximum(self.current_image.metaData['ShapeSizeZ'] - 1)
        #
        # print(self.main_window.checkBox_channel0.isCheckable())
        self.display.show_image()

    def plot_histogram(self):
        l = []
        for i in range(self.main_window.image_list.count()):
            l.append(self.main_window.image_list.itemWidget(self.main_window.image_list.item(i)))

        histogram = Hist(l)
        histogram.create_histogram()

    def update_image(self, channel, value):
        self.current_image.index = (
            channel, value)
        self.display.show_image()
# okay decompiling controllers.interface.pyc
