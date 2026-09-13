from __future__ import annotations

from typing import Iterable

import cv2
import numpy as np
from PIL import Image


def _to_pil_rgb(image: np.ndarray) -> Image.Image:
    if image.ndim == 2:
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.ndim == 3 and image.shape[2] == 3:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        raise ValueError(f"Không hỗ trợ shape={image.shape}")
    return Image.fromarray(rgb)


def _fit_to_canvas(img: Image.Image, size: tuple[int, int], margin: int) -> Image.Image:
    canvas_w, canvas_h = size
    margin = max(0, int(margin))
    max_w = max(1, canvas_w - 2 * margin)
    max_h = max(1, canvas_h - 2 * margin)

    copy = img.copy()
    copy.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    x = (canvas_w - copy.width) // 2
    y = (canvas_h - copy.height) // 2
    canvas.paste(copy, (x, y))
    return canvas


def export_images_to_pdf(
    images: Iterable[np.ndarray],
    output_path: str,
    page_size: str = "Auto",
    orientation: str = "Portrait",
    margin: int = 30,
) -> None:
    """PHẦN XUẤT PDF nhiều trang."""
    pil_images = [_to_pil_rgb(img) for img in images if img is not None]
    if not pil_images:
        raise ValueError("Không có ảnh để xuất PDF")

    if page_size.lower() == "a4":
        # A4 xấp xỉ ở 150 DPI.
        size = (1240, 1754)
        if orientation.lower() == "landscape":
            size = (size[1], size[0])
        pil_images = [_fit_to_canvas(img, size, margin) for img in pil_images]

    first, rest = pil_images[0], pil_images[1:]
    first.save(
        output_path,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=rest,
    )
