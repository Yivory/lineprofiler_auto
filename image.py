# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.8.10 (tags/v3.8.10:3d8993a, May  3 2021, 11:48:03) [MSC v.1928 64 bit (AMD64)]
# Embedded file name: controllers\image.py
import os
import numpy as np
from scipy import misc
import czifile
from tifffile import TiffFile
from lxml import etree as XMLET


class ImageSIM:
    __doc__ = 'ImageSIM is an instance of QListWidget class, used to read and order SIM data from common file formats.\n    Supported formats are: .czi, .lsm, .tif\n    '

    def __init__(self, *args, **kwargs):
        self.file_path = str(args[0])
        self.isParsingNeeded = True
        self.z_file_path = None
        self.extensions = ["'czi'", "'tiff'", "'tif'", "'lsm'", "'png'"]
        # self.row = QHBoxLayout()
        # self.row.addWidget(QLabel(args[0].split(os.sep)[-1]))
        # self.pushButtonOpenZ = QPushButton()
        # self.pushButtonOpenZ.setText('Open z-stack')
        # self.pushButtonOpenZ.clicked.connect(self.open_z)
        # self.row.addWidget(self.pushButtonOpenZ)
        # self.setLayout(self.row)
        self.reset_data()

    def reset_data(self):
        self.data = []
        self.relevantData = []
        self.metaData = {}
        self._index = np.zeros(4).astype(np.uint8)
        self.isParsingNeeded = True
        self.extend = None
        self._flip = {}
        self._channel = np.zeros(4).astype(np.bool)
        self.data_z = None

    def parse(self, calibration_px=0.0322, ApplyButton=False):
        self.isParsingNeeded = False
        self.metaData = {}
        self.data_z = None
        self.data = []
        self.Shape = np.ones(1, dtype={'names':['SizeX', 'SizeY', 'SizeZ', 'SizeC'],  'formats':['i4', 'i4', 'i4', 'i4']})
        self.extend = os.path.splitext(self.file_path)[1]
        self._color = np.array([[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 0, 1]])
        if self.extend == '.czi':
            with czifile.CziFile(self.file_path) as (czi):
                self.data = czi.asarray()
                Header_Metadata = czi.metadata
                Metadata = XMLET.fromstring(Header_Metadata)
                try:
                    shapes = Metadata.findall('./Metadata/Information/Image')[0]
                    self.metaData['ShapeSizeX'] = int(shapes.findall('SizeX')[0].text)
                    self.metaData['ShapeSizeY'] = int(shapes.findall('SizeY')[0].text)
                    try:
                        self.metaData['ShapeSizeZ'] = int(shapes.findall('SizeZ')[0].text)
                    except:
                        self.metaData['ShapeSizeZ'] = 1
                        print('One z-Slice')

                    try:
                        self.metaData['ShapeSizeC'] = int(shapes.findall('SizeC')[0].text)
                    except:
                        self.metaData['ShapeSizeC'] = 1
                        print('One Channel')

                    PixelSizes = Metadata.findall('./Metadata/Scaling/Items/Distance')
                    self.metaData['SizeX'] = float(PixelSizes[0].findall('Value')[0].text) * 1000000
                    self.metaData['SizeY'] = float(PixelSizes[1].findall('Value')[0].text) * 1000000
                    self.metaData['SizeZ'] = float(PixelSizes[2].findall('Value')[0].text) * 1000000
                except:
                    raise
                    print('Metadata fail')

        else:
            if self.extend == '.tif' or self.extend == '.tiff':
                if self.z_file_path is not None:
                    if os.path.exists(self.z_file_path):
                        with TiffFile(self.z_file_path) as (tif):
                            self.data_z = tif.asarray()
                with TiffFile(self.file_path) as (tif):
                    self.data = tif.asarray()
                    self.metaData['ShapeSizeC'] = 3
                    self.metaData['ShapeSizeZ'] = 1
                    self.metaData['SizeZ'] = 1
                    self.metaData['SizeX'] = calibration_px
                    self.metaData['SizeY'] = calibration_px
                    self.metaData['ShapeSizeY'] = self.data.shape[-2]
                    self.metaData['ShapeSizeX'] = self.data.shape[-1]
                    for page in tif.pages:
                        for tag in page.tags.values():
                            tag_name, tag_value = tag.name, tag.value
                            if 'ImageDescription' in tag_name:
                                tags = tag_value.split('\n')
                                axes = []
                                lengths = []
                                for tag in tags:
                                    if 'axes' in tag:
                                        axes = tag.split('=')[-1].split(',')
                                        print('calculating axe dimensions')
                                    else:
                                        if 'lengths' in tag:
                                            lengths = tag.split('=')[-1].split(',')
                                        if 'slices' in tag:
                                            print('Found Z Stack')
                                            axes.append('Slices')
                                            lengths.append(tag.split('=')[-1])
                                    if 'channels' in tag:
                                        print('Found Color Channels')
                                        axes.append('Channels')
                                        lengths.append(tag.split('=')[-1])

        if self.extend == '.lsm':
            with TiffFile(self.file_path) as (tif):
                self.data = tif.asarray(memmap=True)
                headerMetadata = str(tif.pages[0].cz_lsm_scan_info)
                metadataList = headerMetadata.split('\n*')
                for shapes in metadataList:
                    if 'images_height' in shapes:
                        self.metaData['ShapeSizeX'] = int(shapes.split()[-1])
                    else:
                        if 'images_width' in shapes:
                            self.metaData['ShapeSizeY'] = int(shapes.split()[-1])
                        if 'images_number_planes' in shapes:
                            self.metaData['ShapeSizeZ'] = int(shapes.split()[-1])
                    if 'images_number_channels' in shapes:
                        self.metaData['ShapeSizeC'] = int(shapes.split()[-1])

                self.data = np.swapaxes(self.data, 1, 2)
                LsmPixelHeader = str(tif.pages[0].tags.cz_lsm_info)
                LsmInfo = LsmPixelHeader.split(', ')
                i = 0
                for element in LsmInfo:
                    if 'e-0' in element:
                        i += 1
                        if i == 1:
                            self.metaData['SizeX'] = float(element) * 1000000
                        if i == 2:
                            self.metaData['SizeY'] = float(element) * 1000000
                        if i == 3:
                            self.metaData['SizeZ'] = float(element) * 1000000

        else:
            if self.extend == '.png':
                self.data = misc.imread(self.file_path)
                self.data = np.expand_dims(np.expand_dims(self.data[(Ellipsis, 0)], 0), 0)
                self.metaData['ShapeSizeC'] = 1
                self.metaData['ShapeSizeZ'] = 1
                self.metaData['ShapeSizeX'] = self.data.shape[2]
                self.metaData['ShapeSizeY'] = self.data.shape[3]
                self.metaData['SizeZ'] = 1
                self.metaData['SizeX'] = 0.01
                self.metaData['SizeY'] = 0.01
            else:
                if len(self.data.shape) == 2:
                    new_data = np.zeros((3, 1, self.data.shape[0], self.data.shape[1]))
                    self.metaData['SizeX'] = calibration_px
                    self.metaData['SizeY'] = calibration_px
                    new_data[(0, 0)] = self.data
                    self.data = new_data
                if len(self.data.shape) == 3:
                    if self.data.shape[2] < 5:
                        new_data = np.zeros((3, 1, self.data.shape[0], self.data.shape[1]))
                        new_data[0, :] = np.sum((self.data), axis=2)
                        self.metaData['ShapeSizeY'] = self.data.shape[0]
                        self.metaData['ShapeSizeX'] = self.data.shape[1]
                else:
                    # new_data = np.zeros((3, 1, self.data.shape[1], self.data.shape[2]))
                    new_data = np.zeros((3, 1, self.data.shape[2], self.data.shape[3]))
                    self.metaData['SizeX'] = calibration_px
                    self.metaData['SizeY'] = calibration_px
                    for i in range(self.data.shape[0]):
                        new_data[(i, 0)] = self.data[i][0]

                self.data = new_data
            for i, n in enumerate(self.data.shape):
                if n == self.metaData['ShapeSizeC']:
                    self.data = np.rollaxis(self.data, i, 0)
                else:
                    if n == self.metaData['ShapeSizeZ']:
                        self.data = np.rollaxis(self.data, i, 1)
                    if n == self.metaData['ShapeSizeY']:
                        self.data = np.rollaxis(self.data, i, 2)
                if n == self.metaData['ShapeSizeX']:
                    self.data = np.rollaxis(self.data, i, 3)

            self.data = np.reshape(self.data, (self.metaData['ShapeSizeC'], self.metaData['ShapeSizeZ'], self.metaData['ShapeSizeY'], self.metaData['ShapeSizeX']))
            self.metaData['ChannelNum'] = self.metaData['ShapeSizeC']
        if self.metaData == {}:
            self.set_calibration(calibration_px)

    @property
    def data_rgba_2d(self):
        if not np.any(self._channel):
            raise ValueError('No channel visible')
        visible_data = self.data[np.where(self._channel)]
        data_rgba = np.zeros((visible_data.shape[0], self.metaData['ShapeSizeY'], self.metaData['ShapeSizeX'], 4))
        indices = self._index[np.where(self._channel)]
        for i in range(visible_data.shape[0]):
            data_rgba[i] = np.stack(((visible_data[(i, indices[i])],) * 4), axis=(-1))
            data_rgba[i] *= self._color[np.where(self._channel)][i]

        return data_rgba

    @property
    def data_gray_2d(self):
        if not np.any(self._channel):
            raise ValueError('No channel visible')
        visible_data = self.data[np.where(self._channel)]
        data_gray = np.zeros((visible_data.shape[0], self.metaData['ShapeSizeY'], self.metaData['ShapeSizeX']))
        indices = self._index[np.where(self._channel)]
        for i in range(visible_data.shape[0]):
            data_gray[i] = visible_data[(i, indices[i])]

        return data_gray

    @property
    def data_rgba_3d(self):
        return self.data[np.where(self._channel)]

    @property
    def channel(self, index):
        return self._channel[index]

    @channel.setter
    def channel(self, value):
        self._channel[value[0]] = value[1]

    @property
    def index(self, channel):
        return self._index[channel]

    @index.setter
    def index(self, value):
        if value[1] > self.metaData['ShapeSizeZ']:
            raise ValueError('Index out of bounds')
        self._index[value[0]] = value[1]

    @property
    def color(self, channel):
        return self._color[channel]

    @color.setter
    def color(self, channel, value):
        if value.shape[0] != 4:
            raise ValueError('Not a color')
        self._color[channel] = value

    @property
    def flip(self, direction):
        """
        directions: UpsideDown, LeftRight
        value: True, False
        """
        return self._flip[direction]

    @flip.setter
    def flip(self, direction, value):
        self._flip[direction] = value

    def set_calibration(self, px):
        self.metaData['SizeX'] = px
        self.metaData['SizeY'] = px
        self.metaData['SizeZ'] = px
# okay decompiling controllers.image.pyc
