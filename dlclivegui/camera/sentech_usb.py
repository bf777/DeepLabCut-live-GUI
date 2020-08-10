"""
DeepLabCut Toolbox (deeplabcut.org)
© A. & M. Mathis Labs

Licensed under GNU Lesser General Public License v3.0
"""

import cv2
import time
from pysentech import SentechSystem
import numpy as np


class CameraError(Exception):
    """
    Exception for incorrect use of cameras
    """

    pass


class SentechCam(object):
    """ Base camera class. Controls image capture, writing images to video, pose estimation and image display.

    Parameters
    ----------
    id : [type]
        camera id
    sdk_path : str
        path to Sentech SDK installation on your computer
    exposure : int, optional
        exposure time in microseconds, by default None
    gain : int, optional
        gain value, by default None
    rotate : [type], optional
        [description], by default None
    crop : list, optional
        camera cropping parameters: [left, right, top, bottom], by default None
    fps : float, optional
        frame rate in frames per second, by default None
    use_tk_display : bool, optional
        flag to use tk image display (if using GUI), by default False
    display_resize : float, optional
        factor to resize images if using opencv display (display is very slow for large images), by default None
    """

    @staticmethod
    def arg_restrictions():
        """ Returns a dictionary of arguments restrictions for DLCLiveGUI
        """

        return {}

    def __init__(
            self,
            device=0,
            sdk_path=None,
            resolution=None,
            exposure=None,
            gain=None,
            rotate=None,
            crop=None,
            fps=None,
            use_tk_display=False,
            display_resize=1.0,
    ):
        """ Constructor method
        """

        self.id = int(device)
        self.sdk_path = sdk_path
        self.exposure = exposure
        self.gain = gain
        self.rotate = rotate
        self.crop = [int(c) for c in crop] if crop else None
        self.set_im_size(resolution)
        self.fps = fps
        self.use_tk_display = use_tk_display
        self.display_resize = display_resize if display_resize else 1.0
        self.next_frame = 0

    def set_im_size(self, res):
        """[summary]

        Parameters
        ----------
        default : [, optional
            [description], by default None

        Raises
        ------
        DLCLiveCameraError
            throws error if resolution is not set
        """

        if not res:
            raise CameraError("Resolution is not set!")

        self.im_size = (
            (int(res[0]), int(res[1]))
            if self.crop is None
            else (self.crop[3] - self.crop[2], self.crop[1] - self.crop[0])
        )

    def set_capture_device(self):
        """ Sets frame capture device with desired properties
        """
        system = SentechSystem(self.sdk_path)
        self.cap = (
            system.get_camera(self.id)
        )

        if self.im_size:
            self.cap.image_shape((self.im_size[0], self.im_size[1]))
        if self.exposure:
            self.cap.exposure(self.exposure)
        if self.gain:
            self.cap.gain(self.gain)

        return True

    def get_image_on_time(self):
        """ Gets an image from frame capture device at the appropriate time (according to fps).

        Returns
        -------
        `np.ndarray`
            image as a numpy array
        float
            timestamp at which frame was taken, obtained from :func:`time.time`
        """

        frame = None
        while frame is None:
            cur_time = time.time()
            if cur_time > self.next_frame:
                frame = self.get_image()
                timestamp = cur_time
                self.next_frame = max(
                    self.next_frame + 1.0 / self.fps, cur_time + 0.5 / self.fps
                )

        return frame, timestamp

    def get_image(self):
        """ Gets image from frame capture device
        """
        frame = np.uint8(self.cap.grab_frame().as_numpy())

        return frame

    def close_capture_device(self):
        """ Closes frame capture device
        """
        self.cap.release()
