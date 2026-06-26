import cv2
import numpy as np
from typing import List, Optional, Tuple

from core.cube import ALL_FACES


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


# Note: color detection is implemented via CLAHE + inner-cell median HSV
# + nearest-neighbor classification in `extract_face_colors`.


def find_cube_face_contour(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 30, 140)

    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    edges = cv2.erode(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0
    h_img, w_img = image.shape[:2]
    img_area = h_img * w_img

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < img_area * 0.03:
            continue

        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * peri, True)

        if 4 <= len(approx) <= 6:
            x, y, w, h = cv2.boundingRect(approx)
            aspect = w / float(h) if h > 0 else 0
            if 0.6 <= aspect <= 1.8 and area > best_area:
                best_area = area
                best = (x, y, w, h)

    return best


def _rect_to_square_with_padding(
    image: np.ndarray,
    rect: Tuple[int, int, int, int],
    padding_ratio: float = 0.12,
) -> Tuple[int, int, int, int]:
    x, y, w, h = rect
    h_img, w_img = image.shape[:2]

    # Expand a bit
    pad_w = int(w * padding_ratio)
    pad_h = int(h * padding_ratio)
    x -= pad_w
    y -= pad_h
    w += pad_w * 2
    h += pad_h * 2

    side = max(w, h)
    cx = x + w // 2
    cy = y + h // 2

    x1 = cx - side // 2
    y1 = cy - side // 2

    x1 = _clamp(x1, 0, w_img - 1)
    y1 = _clamp(y1, 0, h_img - 1)
    side = _clamp(side, 1, min(w_img - x1, h_img - y1))

    return (x1, y1, side, side)


def _sample_cell_hsv(
    bgr_image: np.ndarray,
    cell_rect: Tuple[int, int, int, int],
    min_valid_pixels: int = 20,
) -> Tuple[Optional[Tuple[float, float, float]], float]:
    """
    Extract median HSV from the inner ~40% of a grid cell to avoid edge bleed.
    Returns:
      (median_hsv or None, confidence_0_1)
    """
    x, y, w, h = cell_rect
    h_img, w_img = bgr_image.shape[:2]

    x2 = _clamp(x + w, 0, w_img)
    y2 = _clamp(y + h, 0, h_img)
    x = _clamp(x, 0, w_img - 1)
    y = _clamp(y, 0, h_img - 1)
    if x >= x2 or y >= y2:
        return None, 0.0

    cell = bgr_image[y:y2, x:x2]
    if cell.size == 0:
        return None, 0.0

    # inner 40% = 30% margin on each side
    margin_x = int(cell.shape[1] * 0.30)
    margin_y = int(cell.shape[0] * 0.30)
    inner = cell[margin_y: cell.shape[0] - margin_y, margin_x: cell.shape[1] - margin_x]
    if inner.size == 0:
        return None, 0.0

    hsv = cv2.cvtColor(inner, cv2.COLOR_BGR2HSV)

    # Use median of all pixels (robust to reflections)
    h_vals = hsv[:, :, 0].astype(np.float32).reshape(-1)
    s_vals = hsv[:, :, 1].astype(np.float32).reshape(-1)
    v_vals = hsv[:, :, 2].astype(np.float32).reshape(-1)

    # Filter low-quality pixels
    mask = v_vals >= 35
    if mask.sum() < min_valid_pixels:
        return None, 0.0

    h_f = h_vals[mask]
    s_f = s_vals[mask]
    v_f = v_vals[mask]

    med_h = float(np.median(h_f))
    med_s = float(np.median(s_f))
    med_v = float(np.median(v_f))

    # Confidence: fraction of valid pixels
    conf = float(_clamp(mask.sum() / float(v_vals.shape[0]), 0.0, 1.0))
    return (med_h, med_s, med_v), conf


def extract_face_colors(
    image: np.ndarray,
    face_rect: Tuple[int, int, int, int],
) -> Tuple[List[str], float]:
    """
    Pipeline:
      1) CLAHE preprocess on the full face crop
      2) For each cell: take inner 40% region
      3) Compute median HSV for that inner region
      4) Classify via nearest HSV centroid (hue weighted 2x)
    """
    x, y, w, h = face_rect
    cell_w = w / 3.0
    cell_h = h / 3.0

    # Crop the face region once
    x2 = _clamp(x + w, 0, image.shape[1])
    y2 = _clamp(y + h, 0, image.shape[0])
    face_crop = image[y:y2, x:x2]
    if face_crop.size == 0:
        return ["W"] * 9, 0.0

    # CLAHE preprocessing (LAB space)
    lab = cv2.cvtColor(face_crop, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    l_eq = clahe.apply(l)
    norm_bgr = cv2.cvtColor(cv2.merge([l_eq, a, b]), cv2.COLOR_LAB2BGR)

    # HSV centroids for nearest-neighbor classification.
    # Hue is in [0..179] (OpenCV).
    COLOR_CENTROIDS = {
        "W": (0.0, 15.0, 220.0),
        "Y": (28.0, 200.0, 210.0),
        "R": (5.0, 220.0, 175.0),
        "O": (13.0, 220.0, 195.0),
        "B": (112.0, 200.0, 175.0),
        "G": (75.0, 175.0, 155.0),
    }

    def classify_color(hv: float, sv: float, vv: float) -> Tuple[str, float]:
        best_color = "W"
        best_dist = float("inf")
        for color, (ch, cs, cv_) in COLOR_CENTROIDS.items():
            # red wrap-around handling
            hue_diff = min(abs(hv - ch), 179 - abs(hv - ch))
            dist = (hue_diff * 2) ** 2 + (sv - cs) ** 2 + (vv - cv_) ** 2
            if dist < best_dist:
                best_dist = dist
                best_color = color
        # Convert distance to [0..1] confidence
        conf = 1.0 / (1.0 + best_dist / 20000.0)
        return best_color, float(conf)

    colors: List[str] = []
    conf_sum = 0.0

    # Each cell rect is computed inside the face_crop
    for row in range(3):
        for col in range(3):
            cx1 = int(col * cell_w)
            cy1 = int(row * cell_h)
            cx2 = int((col + 1) * cell_w)
            cy2 = int((row + 1) * cell_h)

            cell_rect = (
                cx1,
                cy1,
                max(1, cx2 - cx1),
                max(1, cy2 - cy1),
            )

            hsv_triplet, sample_conf = _sample_cell_hsv(norm_bgr, cell_rect)
            if hsv_triplet is None:
                colors.append("W")
                continue

            h_val, s_val, v_val = hsv_triplet
            classified, class_conf = classify_color(h_val, s_val, v_val)

            colors.append(classified)
            conf_sum += max(0.0, min(1.0, sample_conf * class_conf))

    global_conf = conf_sum / 9.0
    return colors, float(global_conf)


def scan_single_face_with_confidence(
    image: np.ndarray,
    face_name: str,
) -> Tuple[Optional[List[str]], float]:
    """
    Returns:
      (colors or None, confidence_0_1)
    """
    # Face contour -> square crop
    face_rect = find_cube_face_contour(image)

    if face_rect is None:
        h, w = image.shape[:2]
        size = min(h, w) // 2
        cx, cy = w // 2, h // 2
        face_rect = (cx - size // 2, cy - size // 2, size, size)

    face_rect_sq = _rect_to_square_with_padding(image, face_rect, padding_ratio=0.14)

    colors, global_conf = extract_face_colors(image, face_rect_sq)

    # If confidence is low, fallback to centered square (often better than a bad contour box)
    if global_conf < 0.35:
        h, w = image.shape[:2]
        size = int(min(h, w) * 0.58)
        cx, cy = w // 2, h // 2
        fallback = (cx - size // 2, cy - size // 2, size, size)
        fallback_sq = _rect_to_square_with_padding(image, fallback, padding_ratio=0.10)
        colors, global_conf = extract_face_colors(image, fallback_sq)

    # Still ensure length=9
    if not isinstance(colors, list) or len(colors) != 9:
        return None, 0.0

    return colors, float(global_conf)


def scan_single_face(image: np.ndarray, face_name: str) -> Optional[List[str]]:
    """
    Backward compatible wrapper: returns only colors.
    """
    colors, _conf = scan_single_face_with_confidence(image, face_name)
    return colors
