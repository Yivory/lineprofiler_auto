# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: controllers\processing_one_channel.py
from utility import *
from processing_template import QSuperThread
from micro_services import profile_painter

class QProcessThread(QSuperThread):
    __doc__ = '\n    Processing thread to compute distances between SNCs in a given SIM image.\n    Extending the QThread class keeps the GUI running while the evaluation runs in the background.\n    '

    def __init__(self, *args, parent=None):
        (super(QProcessThread, self).__init__)(*args, *(parent,))
        self.upper_limit = 800
        self.lower_limit = 400
        self.three_channel = True

    def _set_image(self, slice):
        """
        Preprocess image

        Parameters
        ----------
        slice: int
            Current slice of image stack

        """
        self.current_image = self.image_stack[:, slice].astype(np.uint16)
        processing_image = np.clip(self.current_image[0] / self.intensity_threshold, 0, 255).astype(np.uint8)
        self.gradient_table, self.shapes = get_center_of_mass_splines(processing_image, self.blur)
        self._fillhole_image()

    def _fillhole_image(self):
        """
        Build a fillhole image in red channel

        Returns
        -------

        """
        image = self.current_image[0] / self._intensity_threshold
        image = np.clip(image, 0, 255)
        self.im_floodfill_inv = create_floodfill_image(image)
        spline_positions = self.gradient_table[:, 0:2]
        indices = []
        index = 0
        to_cut = 0
        running_index = 0
        for i in range(self.gradient_table.shape[0]):
            running_index += 1
            shape = self.shapes[index]
            if self.im_floodfill_inv[(spline_positions[(i, 0)].astype(np.uint32), spline_positions[(i, 1)].astype(np.uint32))] == 0:
                indices.append(i)
                to_cut += 1
            if running_index == shape:
                self.shapes[index] -= to_cut
                to_cut = 0
                index += 1
                running_index = 0

        self.gradient_table = np.delete((self.gradient_table), (np.array(indices).astype(np.uint32)), axis=0)

    def save_avg_profile(self, profile, name):
        profile = np.array(profile)
        profile_mean = np.mean(profile, axis=0)
        X = np.arange(0, profile_mean.shape[0], 1)
        to_save = np.array([X, profile_mean]).T
        np.savetxt(self.path + '\\' + name + '.txt', to_save)
        return profile_mean

    def _show_profiles(self):
        """
        Create and evaluate line profiles.
        """
        counter = -1
        count = self.gradient_table.shape[0]
        self.results = {'p_red':[],  'p_green':[],  'p_blue':[],  'distances':[]}
        current_profile_width = int(2 * self.profil_width / 3 * self.px_size * 1000)
        if current_profile_width % 2 != 0:
            current_profile_width += 1
        painter = profile_painter(self.current_image[0] / self.intensity_threshold, self.path)
        for i in range(len(self.shapes)):
            color = self.colormap(i / len(self.shapes))
            current_profile = {'red':[],  'green':[]}
            for j in range(self.shapes[i]):
                counter += 1
                self.sig.emit(int(counter / count * 100))
                source_point = self.gradient_table[counter, 0:2]
                gradient = self.gradient_table[counter, 2:4]
                gradient = np.arctan(gradient[1] / gradient[0]) + np.pi / 2
                line = line_parameters(source_point, gradient, self.profil_width)
                profile = line_profile((self.current_image[0]), (line['start']), (line['end']), px_size=(self.px_size), sampling=(self.sampling))
                try:
                    distance, center = calc_peak_distance(profile)
                except:
                    print('could not fit')
                    continue

                if not distance < self.lower_limit:
                    if distance > self.upper_limit:
                        continue
                    profile = profile[int(center - current_profile_width / 2):int(center + current_profile_width / 2)]
                    if profile.shape[0] < current_profile_width:
                        continue
                    current_profile['red'].append(profile)
                    self.results['distances'].append(distance)
                    painter.send((line, color))

            if current_profile['red']:
                self.results['p_red'] += current_profile['red']
                red_mean = self.save_avg_profile(current_profile['red'], 'red_' + str(i))
                self.sig_plot_data.emit(red_mean, current_profile_width / 2, i, self.path, color, len(current_profile['red']))

        try:
            painter.send(None)
        except StopIteration:
            print('Overlay sucess')

        red_mean = self.save_avg_profile(self.results['p_red'], 'red_mean')
        self.sig_plot_data.emit(red_mean, current_profile_width / 2, 9999, self.path, (1.0,
                                                                                       0.0,
                                                                                       0.0,
                                                                                       1.0), len(self.results['p_red']))
        np.savetxt(self.path + '\\red.txt', np.asarray(self.results['p_red']).T)
        np.savetxt(self.path + '\\distances' + '.txt', np.array(self.results['distances']))

    def run(self):
        """
        Start computation and run thread
        """
        for i in range(self.image_stack.shape[1]):
            self._z = i
            self._set_image(i)
            self._show_profiles()

        self.done.emit(self.ID)
# okay decompiling controllers.processing_one_channel.pyc
