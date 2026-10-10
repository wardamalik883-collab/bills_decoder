"""Image preprocessing utilities (loading, orientation correction, resizing).

Ensures bill images are in RGB format, EXIF-rotated right-side up, and reasonably sized
for LLM vision APIs without heavy OCR dependencies.
"""

from __future__ import annotations

import logging
from pathlib import Path
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def load_and_preprocess_image(
    image_path: Path | str,
    max_dimension: int = 2500,
) -> Image.Image:
    """Load an image, correct EXIF rotation, convert to RGB, and downscale if large.

    Args:
        image_path: Path to the input image file.
        max_dimension: Maximum allowed width or height in pixels.

    Returns:
        PIL.Image.Image in RGB mode.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {path}")

    img = Image.open(path)

    # Transpose according to EXIF orientation tag if present
    img = ImageOps.exif_transpose(img)

    # Convert to RGB if needed (e.g. RGBA, grayscale, or palette)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Downscale only if dimension exceeds max_dimension
    width, height = img.size
    max_side = max(width, height)
    if max_side > max_dimension:
        scale = max_dimension / float(max_side)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        logger.debug(
            "Downscaling image %s from (%d, %d) to (%d, %d)",
            path.name,
            width,
            height,
            new_width,
            new_height,
        )
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return img


def preprocess_image_path(
    image_path: Path | str,
    output_dir: Path | str | None = None,
    max_dimension: int = 2500,
) -> Path:
    """Preprocess image and return a path to the preprocessed file.

    If the image is already standard RGB, properly oriented, and within size limits,
    the original path is returned directly. Otherwise a preprocessed image is written.

    Args:
        image_path: Input image path.
        output_dir: Directory to save processed image if modified.
        max_dimension: Maximum width or height.

    Returns:
        Path to preprocessed or original image.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {path}")

    # Inspect image without modifying
    with Image.open(path) as img:
        exif = img.getexif()
        has_exif_orientation = bool(exif and exif.get(0x0112, 1) != 1)
        is_rgb = img.mode == "RGB"
        within_bounds = max(img.size) <= max_dimension

        # If already suitable, avoid re-encoding
        if not has_exif_orientation and is_rgb and within_bounds and path.suffix.lower() in (".jpg", ".jpeg", ".png"):
            return path

    # Otherwise preprocess and save
    processed_img = load_and_preprocess_image(path, max_dimension=max_dimension)
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = path.parent / ".preprocessed"
    out_dir.mkdir(parents=True, exist_ok=True)

    dest_path = out_dir / f"proc_{path.name}.jpg"
    processed_img.save(dest_path, format="JPEG", quality=90)
    return dest_path
