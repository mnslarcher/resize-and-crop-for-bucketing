import argparse
import math
import warnings
from pathlib import Path

from PIL import Image


def make_bucket_resolutions(
    max_sqrt_area=1024, min_size=512, max_size=2048, divisible_by=64
):
    """
    Generate bucket resolutions based on specified constraints.

    Args:
        max_sqrt_area (int): The maximum square root value of each resolution area.
                             This value is squared to determine the maximum area of the buckets.
        min_size (int): The minimum size (either width or height) for the bucket resolutions.
        max_size (int): The maximum size (either width or height) for the bucket resolutions.
        divisible_by (int): The factor by which the bucket widths and heights should be divisible.

    Returns:
        list of tuples: A sorted list of tuples, each containing (aspect_ratio, width, height).
    """
    resolutions = set()

    max_sqrt_area = max_sqrt_area // divisible_by
    max_area = max_sqrt_area**2
    size = max_sqrt_area * divisible_by
    resolutions.add((1.0, size, size))

    size = min_size
    while size <= max_size:
        width = size
        height = min(max_size, (max_area // (width // divisible_by)) * divisible_by)
        resolutions.add((width / height, width, height))
        resolutions.add((height / width, height, width))
        size += divisible_by

    resolutions = list(resolutions)
    resolutions.sort()
    return resolutions


def resize_and_crop_images(input_dir, output_dir, bucket_resolutions):
    """
    Resize and crop images from an input directory and save them to an output directory,
    based on provided resolution buckets.

    Args:
        input_dir (str): Path to the directory containing input images.
        output_dir (str): Path to the directory where resized and cropped images will be saved.
        bucket_resolutions (list of tuples): A sorted list of tuples, each containing (aspect_ratio, width, height).

    Returns:
        None: The function saves the processed images to the output directory and does not return a value.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files in the input directory
    image_extensions = ["*.png", "*.jpg", "*.jpeg"]
    image_paths = [
        image_path for ext in image_extensions for image_path in input_dir.glob(ext)
    ]

    for image_path in image_paths:
        image = Image.open(image_path)
        width, height = image.size
        aspect_ratio = width / height
        closest_aspect_ratio = None
        target_width = None
        target_height = None
        closest_aspect_ratio_diff = float("inf")

        for bucket_aspect_ratio, bucket_width, bucket_height in bucket_resolutions:
            if width >= bucket_width and height >= bucket_height:
                aspect_ratio_diff = abs(bucket_aspect_ratio - aspect_ratio)
                if aspect_ratio_diff < closest_aspect_ratio_diff:
                    closest_aspect_ratio_diff = aspect_ratio_diff
                    closest_aspect_ratio = bucket_aspect_ratio
                    target_width = bucket_width
                    target_height = bucket_height

        if closest_aspect_ratio is not None:
            if closest_aspect_ratio > aspect_ratio:
                # Resize the image so width matches target_width
                new_width = target_width
                new_height = int(new_width / closest_aspect_ratio)
                image = image.resize((new_width, new_height), Image.LANCZOS)

                # Crop the image so that height matches target_height
                if new_height > target_height:
                    top = (new_height - target_height) // 2
                    bottom = top + target_height
                    image = image.crop((0, top, new_width, bottom))
            else:
                # Resize the image so height matches target_height
                new_height = target_height
                new_width = int(new_height * closest_aspect_ratio)
                image = image.resize((new_width, new_height), Image.LANCZOS)

                # Crop the image so that width matches target_width
                if new_width > target_width:
                    left = (new_width - target_width) // 2
                    right = left + target_width
                    image = image.crop((left, 0, right, new_height))

            output_path = output_dir / image_path.name
            image.save(output_path)
        else:
            warnings.warn(
                f"Skipping {image_path.name}: No suitable aspect ratio bucket found."
            )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Resize and crop images based on generated bucket resolutions."
    )

    # Arguments for make_bucket_resolutions function
    parser.add_argument(
        "--max_sqrt_area",
        type=int,
        default=1024,
        help="Maximum square root value of each resolution area. This value is squared to determine the maximum area of the buckets.",
    )
    parser.add_argument(
        "--min_size",
        type=int,
        default=512,
        help="Minimum size (either width or height) for the bucket resolutions.",
    )
    parser.add_argument(
        "--max_size",
        type=int,
        default=2048,
        help="Maximum size (either width or height) for the bucket resolutions.",
    )
    parser.add_argument(
        "--divisible_by",
        type=int,
        default=64,
        help="Factor by which the bucket widths and heights should be divisible.",
    )

    # Arguments for resize_and_crop_images function
    parser.add_argument(
        "--input_dir", type=str, help="Directory containing input images."
    )
    parser.add_argument(
        "--output_dir", type=str, help="Directory where output images will be saved."
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    bucket_resolutions = make_bucket_resolutions(
        args.max_sqrt_area, args.min_size, args.max_size, args.divisible_by
    )

    resize_and_crop_images(args.input_dir, args.output_dir, bucket_resolutions)
