# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: controllers\processing_microtubule.py
from utility import compute_line_orientation, line_parameters, line_profile
import numpy as np
from processing_template import QSuperThread
from micro_services import profile_painter, profile_collector, mic_project_generator

class QProcessThread(QSuperThread):
    __doc__ = '\n    Processing thread to compute Microtubule profiles.\n    Extending the QThread class keeps the GUI running while the evaluation runs in the background.\n    '

    def __init__(self, *args, parent=None):
        (super(QProcessThread, self).__init__)(*args, *(parent,))

    def _set_image(self, slice):
        """
        Preprocess image

        Parameters
        ----------
        slice: int
            Current slice of image stack

        """
        self.current_image = self.image_stack[(0, slice)].astype(np.uint16)
        processing_image = np.clip(self.image_stack[(0, slice)] / self.intensity_threshold, 0, 255).astype(np.uint8)

        self.gradient_table, self.shapes = compute_line_orientation(processing_image,
          (self.blur), expansion=(self.spline_parameter), expansion2=(self.spline_parameter))

    def _show_profiles(self):
        """
        Create and evaluate line profiles.
        """
        if not isinstance(self.data_z, np.ndarray):
            self.z_project_collection = False
        # else:
        profiles = []
        result = []
        counter = -1
        count = self.gradient_table.shape[0]
        current_profile_width = int(2 * self.profil_width / 3 * self.px_size * 1000)
        if current_profile_width % 2 != 0:
            current_profile_width += 1
        painter = profile_painter(self.current_image / self.intensity_threshold, self.path)
        for i in range(len(self.shapes)):
            color = self.colormap(i / len(self.shapes))
            collector = profile_collector(self.path, i)
            mic_generator = mic_project_generator(self.path, i)
            for j in range(self.shapes[i]):
                counter += 1
                self.sig.emit(int(counter / count * 100))
                source_point = self.gradient_table[counter, 0:2]
                gradient = self.gradient_table[counter, 2:4]
                gradient = np.arctan(gradient[1] / gradient[0]) + np.pi / 2
                line = line_parameters(source_point, gradient, self.profil_width)
                if self.z_project_collection:
                    for z in range(self.data_z.shape[0]):
                        z_profile = line_profile((self.data_z[z]), (line['start']), (line['end']), px_size=(self.px_size), sampling=1)
                        mic_generator.send((z_profile, z))

                profile = line_profile((self.current_image), (line['start']), (line['end']), px_size=(self.px_size), sampling=(self.sampling))
                profile = profile[int(profile.shape[0] / 2 - current_profile_width / 2):int(profile.shape[0] / 2 + current_profile_width / 2)]
                if profile.shape[0] < int(current_profile_width):
                    print('to short')
                    continue
                # shift tab
                collector.send(profile)
                painter.send((line, color))

            if self.z_project_collection:
                try:
                    mic_generator.send(None)
                except StopIteration as err:
                    print('created z-profile')

            try:
                collector.send(None)
            except StopIteration as err:
                result = err.value

            profiles += result['red']
            red = np.array(result['red'])
            red_mean = np.mean(red, axis=0)
            self.sig_plot_data.emit(red_mean, profiles[0].shape[0] / 2, i, self.path, color, red.shape[0])

        try:
            painter.send(None)
        except StopIteration:
            print('Overlay sucess')

        red = np.array(profiles)
        red_mean = np.mean(red, axis=0)
        try:
            np.savetxt(self.path + '\\red_mean.txt', red_mean)
            self.sig_plot_data.emit(red_mean, profiles[0].shape[0] / 2, 9999, self.path, (1.0,
                                                                                          0.0,
                                                                                          0.0,
                                                                                          1.0), red.shape[0])
            np.savetxt(self.path + '\\red.txt', red)
        except ValueError:
            print(self.path + ' couldnt be evaluated')

    def run(self):
        """
        Start computation and run thread
        """
        for i in range(self.image_stack.shape[1]):
            self._set_image(i)
            self._show_profiles()
            self.done.emit(self.ID)
# okay decompiling controllers.processing_microtubule.pyc
