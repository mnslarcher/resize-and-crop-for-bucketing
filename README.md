# Resize and Crop Images for Bucketing

This Python script is designed to resize and crop images for aspect ratio bucketing. It can be particularly useful when working with [Kohya's Stable Diffusion scripts](https://github.com/kohya-ss/sd-scripts) or similar scripts, helping to prevent unexpected assignment to buckets (see [Issue #731](https://github.com/kohya-ss/sd-scripts/issues/731)).

Given an input image repository, this script resizes and crops images to match the dimensions of the bucket with the closest aspect ratio. Please note the following:

- Buckets with a width or height greater than that of the image are skipped.
- If no bucket satisfies the constraints, the image is discarded and a warning is raised.

## Requirements

- Python 3.x
- Pillow (Python Imaging Library Fork)

To install Pillow, run:
```bash
pip install Pillow
```

## Usage

First, clone this repository or download the script. Then, run the script using the command-line interface.

### Command-Line Arguments:

- `--max_sqrt_area`: Maximum square root value of each resolution area. This value is squared to determine the maximum area of the buckets. Default is 1024.
- `--min_size`: Minimum size (either width or height) for the bucket resolutions. Default is 512.
- `--max_size`: Maximum size (either width or height) for the bucket resolutions. Default is 2048.
- `--divisible_by`: Factor by which the bucket widths and heights should be divisible. Default is 64.
- `--input_dir`: Directory containing the input images.
- `--output_dir`: Directory where the resized and cropped images will be saved.

### Example Command:

```bash
python resize_and_crop.py --input_dir=./input_images --output_dir=./output_images
```

This command will process images from `./input_images`, resize and crop them according to the generated bucket resolutions, and save the output to `./output_images`.

