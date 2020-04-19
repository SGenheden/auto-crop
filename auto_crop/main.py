import os
import glob

from gooey import Gooey, GooeyParser

from auto_crop.image import Image


def _get_args():
    parser = GooeyParser(
        prog="autocrop", description="tool to automatically crop images based on shapes"
    )
    parser.add_argument(
        "folder", help="the place with all the images", widget="DirChooser"
    )
    parser.add_argument(
        "--glob", help="The glob used to find the images", default="IMG_*.JPG"
    )
    parser.add_argument(
        "--thres",
        help="The threshold for separating forground from background",
        type=int,
        default=120,
    )
    parser.add_argument(
        "--quality", help="The JPEG quality", type=int, default=60,
    )
    return parser.parse_args()


@Gooey(program_name="autocrop", default_size=(610, 570))
def main():
    """ Entry-point for the autocrop command
    """
    args = _get_args()

    for filename in glob.glob(os.path.join(args.folder, args.glob)):
        image = Image(filename)
        image.find_contours(args.thres)
        image.crop_by_contour(inplace=True)

        base, ext = os.path.splitext(filename)
        image.save(f"{base}_mod{ext}", jpg_quality=args.quality or None)


if __name__ == "__main__":
    main()
