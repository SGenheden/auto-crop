import os

import pytest
from PIL import Image as PilImage
from PIL.ImageDraw import Draw

from auto_crop.image import Image


@pytest.fixture
def make_image(tmpdir):
    img = PilImage.new("RGBA", (500, 200), "black")
    draw = Draw(img)
    draw.rectangle((50, 50, 100, 180), fill="green")
    draw.rectangle((250, 80, 450, 160), fill="red")
    filename = str(tmpdir / "image.png")
    img.save(filename)
    return Image(filename)


def test_load_image(make_image):
    img = make_image

    assert img.height == 200
    assert img.width == 500


def test_size_no_image():
    img = Image()

    with pytest.raises(ValueError):
        img.height

    with pytest.raises(ValueError):
        img.width


def test_find_contours(make_image):
    img = make_image

    assert len(img.contours) == 0

    img.find_contours(50)

    assert len(img.contours) == 2


def test_crop_by_contour(make_image):
    img = make_image
    img.find_contours(50)

    img2 = img.crop_by_contour()

    assert img2.height == 81
    assert img2.width == 201
    assert img.height == 200
    assert img.width == 500

    img2 = img.crop_by_contour(1)

    assert img2.height == 131
    assert img2.width == 51

    img.crop_by_contour(inplace=True)

    assert img.height == 81
    assert img.width == 201


def test_crop_by_contour_invalid_index(make_image):
    img = make_image

    with pytest.raises(IndexError):
        img.crop_by_contour()

    img.find_contours(50)

    with pytest.raises(IndexError):
        img.crop_by_contour(-1)

    with pytest.raises(IndexError):
        img.crop_by_contour(3)


def test_draw_contour(make_image):
    img = make_image
    img.find_contours(50)
    old1 = list(img[50, 50])
    old2 = list(img[80, 250])

    img2 = img.draw_contours((255, 255, 255))

    # Just check that one pixal of each contour has been change
    assert list(img[50, 50]) == old1
    assert list(img2[50, 50]) == [255, 255, 255]
    assert list(img[80, 250]) == old2
    assert list(img2[80, 250]) == [255, 255, 255]

    img.draw_contours((255, 255, 255), inplace=True)

    assert list(img[50, 50]) == [255, 255, 255]
    assert list(img[80, 250]) == [255, 255, 255]


def test_save_img(make_image, tmpdir):
    img = make_image
    filename = str(tmpdir / "out.png")

    img.save(filename)

    assert os.path.exists(filename)


def test_save_img_jpeg(make_image, tmpdir):
    img = make_image
    filename = str(tmpdir / "out.jpg")

    img.save(filename, jpg_quality=50)

    assert os.path.exists(filename)
