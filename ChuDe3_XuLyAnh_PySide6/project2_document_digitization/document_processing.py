from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

import cv2
import numpy as np


@dataclass
class DocumentProcessResult:
    original: np.ndarray
    perspective_corrected: np.ndarray
    normalized_gray: np.ndarray
    binary: np.ndarray
    document_found: bool


def _order_points(pts: np.ndarray) -> np.ndarray:
    """Sắp xếp 4 điểm theo thứ tự TL, TR, BR, BL."""
    pts = np.asarray(pts, dtype=np.float32).reshape(4, 2)
    ordered = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).ravel()
    ordered[0] = pts[np.argmin(s)]      # top-left
    ordered[2] = pts[np.argmax(s)]      # bottom-right
    ordered[1] = pts[np.argmin(diff)]   # top-right
    ordered[3] = pts[np.argmax(diff)]   # bottom-left
    return ordered


def four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Biến đổi phối cảnh để đưa tờ giấy về dạng nhìn thẳng."""
    rect = _order_points(points)
    tl, tr, br, bl = rect

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_w = max(1, int(round(max(width_a, width_b))))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_h = max(1, int(round(max(height_a, height_b))))

    dst = np.array(
        [[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, matrix, (max_w, max_h))


def detect_document_corners(image: np.ndarray) -> Tuple[np.ndarray | None, np.ndarray]:
    """
    PHẦN B - TÁCH TỜ GIẤY KHỎI NỀN NGOÀI.
    Tìm contour tứ giác lớn nhất từ Canny edge.
    Trả (4 corners hoặc None, edge image).
    """
    if image is None or image.size == 0:
        raise ValueError("Ảnh đầu vào rỗng")

    h, w = image.shape[:2]
    scale = 1.0
    work = image
    max_dim = max(h, w)
    if max_dim > 1200:
        scale = 1200.0 / max_dim
        work = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 60, 180)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    min_area = 0.15 * work.shape[0] * work.shape[1]
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            continue
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            corners = approx.reshape(4, 2).astype(np.float32)
            if scale != 1.0:
                corners /= scale
            return corners, edges

    return None, edges


def crop_document_from_background(image: np.ndarray) -> tuple[np.ndarray, bool]:
    corners, _ = detect_document_corners(image)
    if corners is None:
        return image.copy(), False
    return four_point_transform(image, corners), True


def remove_illumination_background(gray: np.ndarray, kernel_size: int = 51) -> np.ndarray:
    """
    PHẦN A - LOẠI BỎ NỀN/ÁNH SÁNG KHÔNG ĐỒNG ĐỀ TRÊN GIẤY.
    Ước lượng nền bằng morphological closing rồi chuẩn hóa bằng phép chia.
    """
    if gray.ndim != 2:
        raise ValueError("remove_illumination_background yêu cầu ảnh xám 2D")

    k = int(kernel_size)
    if k < 3:
        k = 3
    if k % 2 == 0:
        k += 1

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    background = np.maximum(background, 1)
    normalized = cv2.divide(gray, background, scale=255)
    return normalized


def adaptive_threshold_document(
    gray: np.ndarray,
    method: Literal["Gaussian", "Mean"] = "Gaussian",
    block_size: int = 21,
    c: float = 10.0,
) -> np.ndarray:
    """PHẦN ADAPTIVE THRESHOLD."""
    if gray.ndim != 2:
        raise ValueError("Adaptive Threshold yêu cầu ảnh xám 2D")

    block_size = int(block_size)
    if block_size <= 1 or block_size % 2 == 0:
        raise ValueError("block_size phải là số lẻ > 1")

    adaptive_method = (
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        if method.lower() == "gaussian"
        else cv2.ADAPTIVE_THRESH_MEAN_C
    )
    return cv2.adaptiveThreshold(
        gray,
        255,
        adaptive_method,
        cv2.THRESH_BINARY,
        block_size,
        float(c),
    )


def clean_binary_document(
    binary: np.ndarray,
    operation: Literal["None", "Opening", "Closing"] = "None",
    kernel_size: int = 3,
    iterations: int = 1,
) -> np.ndarray:
    """PHẦN MORPHOLOGY - làm sạch nhiễu nhỏ hoặc nối nét chữ."""
    if operation.lower() == "none":
        return binary.copy()

    # Adaptive threshold tạo chữ đen/nền trắng. Đảo ảnh để morphology
    # xử lý chữ như foreground trắng, sau đó đảo lại.
    inv = cv2.bitwise_not(binary)

    k = int(kernel_size)
    if k <= 0:
        raise ValueError("kernel_size morphology phải > 0")
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))

    if operation.lower() == "opening":
        op = cv2.MORPH_OPEN
    elif operation.lower() == "closing":
        op = cv2.MORPH_CLOSE
    else:
        raise ValueError("operation phải là None / Opening / Closing")

    cleaned_inv = cv2.morphologyEx(inv, op, kernel, iterations=max(1, int(iterations)))
    return cv2.bitwise_not(cleaned_inv)


def process_document(
    image: np.ndarray,
    *,
    detect_page: bool = True,
    remove_background: bool = True,
    background_kernel: int = 51,
    adaptive_method: str = "Gaussian",
    block_size: int = 21,
    c: float = 10.0,
    morph_operation: str = "Opening",
    morph_kernel: int = 3,
    morph_iterations: int = 1,
) -> DocumentProcessResult:
    """PIPELINE HOÀN CHỈNH CHO PROJECT 2."""
    if image is None or image.size == 0:
        raise ValueError("Ảnh đầu vào rỗng")

    # B1: tách giấy khỏi nền ngoài + perspective correction (phương án B).
    if detect_page:
        page, found = crop_document_from_background(image)
    else:
        page, found = image.copy(), False

    # B2: grayscale.
    gray = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)

    # B3: loại bỏ nền/chiếu sáng không đều trên giấy (phương án A).
    normalized = (
        remove_illumination_background(gray, background_kernel)
        if remove_background
        else gray.copy()
    )

    # B4: Adaptive Threshold.
    binary = adaptive_threshold_document(
        normalized,
        method=adaptive_method,
        block_size=block_size,
        c=c,
    )

    # B5: morphology làm sạch.
    binary = clean_binary_document(
        binary,
        operation=morph_operation,
        kernel_size=morph_kernel,
        iterations=morph_iterations,
    )

    return DocumentProcessResult(
        original=image.copy(),
        perspective_corrected=page,
        normalized_gray=normalized,
        binary=binary,
        document_found=found,
    )


def document_metrics(binary: np.ndarray) -> dict:
    """Một số số liệu đơn giản để báo cáo/đánh giá."""
    if binary.ndim != 2:
        gray = cv2.cvtColor(binary, cv2.COLOR_BGR2GRAY)
    else:
        gray = binary
    black_ratio = float(np.mean(gray < 128) * 100.0)
    white_ratio = 100.0 - black_ratio
    return {
        "black_ratio": black_ratio,
        "white_ratio": white_ratio,
        "mean": float(gray.mean()),
        "std": float(gray.std()),
    }
