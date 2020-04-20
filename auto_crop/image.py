import cv2
import imutils
import numpy as np
from PIL import Image as PilImage
from PIL.ExifTags import TAGS


class Image:
    """
    Encapsulation of routines to an image. Internally, the
    image is stored as a numpy.ndarray.

    Arguments
    ---------
    filename: str, optional
        if given, the image referenced by the filename is loaded from disc
    """

    def __init__(self, filename=None):
        self._raw = None
        if filename:
            self.load(filename)
        self.contours = []

    def __getitem__(self, index):
        return self._raw[index]

    @property
    def height(self):
        if self._raw is None:
            raise ValueError("Cannot read height from undefined image")
        return self._raw.shape[0]

    @property
    def width(self):
        if self._raw is None:
            raise ValueError("Cannot read width from undefined image")
        return self._raw.shape[1]

    def crop_by_contour(self, index=0, inplace=False):
        """
        Crop the image about the bounding box of a contour.

        The contours need to be created first with the ``find_contours`` routine.

        Arguments
        ---------
        index: int, optional
            the index of the contour to use
        inplace: bool, optional
            if True, the image is cropped and returned, otherwise a new image is returned

        Returns
        -------
        Image:
            the cropped image
        """
        if index < 0 or index >= len(self.contours):
            raise IndexError(f"The given contour index ({index}) is out of range")

        x, y, w, h = cv2.boundingRect(self.contours[index])
        cropped = self._raw[y : y + h, x : x + w]  # noqa

        if inplace:
            self._raw = cropped
            return self

        new_image = Image()
        new_image._raw = cropped
        return new_image

    def draw_contours(self, color, inplace=False):
        """
        Draw around each contour of the image

        The contours need to be created first with the ``find_contours`` routine.

        Arguments
        ---------
        color: tuple
            the RGB color of the boundary
        inplace: bool, optional
            if True, the image is modified and returned, otherwise a new image is returned

        Returns
        -------
        Image:
            the modified image
        """
        raw = self._raw.copy()
        for contour in self.contours:
            cv2.drawContours(raw, [contour], -1, color, 2)

        if inplace:
            self._raw = raw
            return self

        new_image = Image()
        new_image._raw = raw
        return new_image

    def find_contours(self, threshold):
        """
        Find all contours of the image by first converting it
        to gray-scale and then applying a color threshold.

        Arguments
        ---------
        threshold: int
            any pixel above the threshold is counted as foreground, otherwise background
        """
        gray_img = cv2.cvtColor(self._raw, cv2.COLOR_BGR2GRAY)
        blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
        thresh_img = cv2.threshold(blurred_img, threshold, 255, cv2.THRESH_BINARY)[1]

        cnts = cv2.findContours(
            thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        self.contours = sorted(
            imutils.grab_contours(cnts), key=cv2.contourArea, reverse=True
        )

    def load(self, filename, auto_orient=True):
        """
        Load an image from file

        Arguments
        ---------
        filename: str
            the path to the file
        auto_orient: bool, optional
            if True, orient the image according to the meta data (if available)
        """
        pil_image = PilImage.open(filename)
        if auto_orient:
            self._orient_pil_image(pil_image)
        self._raw = np.array(pil_image)
        if len(self._raw.shape) == 3 and self._raw.shape[2] >= 3:
            self._raw = cv2.cvtColor(self._raw, cv2.COLOR_BGR2RGB)

    def save(self, filename, jpg_quality=None):
        """
        Save image to disc

        Arguments
        ---------
        filename: str
            the path to the file
        jpg_quality: int, optional
            an value between 1 and 100 indicating the JPG quality
        """
        params = []
        if jpg_quality:
            params = [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality]
        cv2.imwrite(filename, self._raw, params)

    @staticmethod
    def _find_exif_value(pil_image, field):
        exif = pil_image._getexif()
        if not exif:
            return 1

        for key, value in exif.items():
            if TAGS.get(key) == field:
                return value
        return 1

    @staticmethod
    def _orient_pil_image(pil_image):
        orientation = Image._find_exif_value(pil_image, "Orientation")
        rotation_angle = {3: 180, 6: 270, 8: 90}.get(orientation, 0)
        if rotation_angle:
            pil_image = pil_image.rotate(rotation_angle, expand=False)
