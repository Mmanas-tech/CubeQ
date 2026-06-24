import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from core.cube import ALL_FACES, SOLVED_STATE, create_solved


def detect_color_from_hsv(h: float, s: float, v: float) -> Optional[str]:
    if v < 30:
        return None
    if s < 25 and v > 150:
        return 'W'
    if 10 <= h <= 45 and s > 50 and v > 60:
        return 'Y'
    if 25 <= h <= 95 and s > 35:
        return 'G'
    if 90 <= h <= 140 and s > 35:
        return 'B'
    if 3 <= h <= 25 and s > 55:
        return 'O'
    if (0 <= h <= 12 or 165 <= h <= 180) and s > 55:
        return 'R'
    return None


def extract_face_colors(image: np.ndarray, face_rect: Tuple[int, int, int, int]) -> Tuple[List[str], int]:
    x, y, w, h = face_rect
    cell_w = w // 3
    cell_h = h // 3
    colors = []
    recognized = 0

    for row in range(3):
        for col in range(3):
            cx = x + col * cell_w + cell_w // 2
            cy = y + row * cell_h + cell_h // 2

            margin_x = max(cell_w // 3, 2)
            margin_y = max(cell_h // 3, 2)
            y1 = max(0, cy - margin_y)
            y2 = min(image.shape[0], cy + margin_y)
            x1 = max(0, cx - margin_x)
            x2 = min(image.shape[1], cx + margin_x)
            roi = image[y1:y2, x1:x2]

            if roi.size == 0:
                colors.append('W')
                continue

            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            h_mean = np.mean(hsv_roi[:, :, 0])
            s_mean = np.mean(hsv_roi[:, :, 1])
            v_mean = np.mean(hsv_roi[:, :, 2])

            color = detect_color_from_hsv(h_mean, s_mean, v_mean)
            if color:
                recognized += 1
            colors.append(color or 'W')

    return colors, recognized


def find_cube_face_contour(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 30, 120)

    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=3)
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
            if 0.5 <= aspect <= 2.0 and area > best_area:
                best_area = area
                best = (x, y, w, h)

    return best


def scan_single_face(image: np.ndarray, face_name: str) -> Optional[List[str]]:
    face_rect = find_cube_face_contour(image)

    if face_rect is None:
        h, w = image.shape[:2]
        size = min(h, w) // 2
        cx, cy = w // 2, h // 2
        face_rect = (cx - size // 2, cy - size // 2, size, size)

    colors, recognized = extract_face_colors(image, face_rect)

    if recognized < 2:
        h, w = image.shape[:2]
        size = min(h, w) // 2
        cx, cy = w // 2, h // 2
        face_rect = (cx - size // 2, cy - size // 2, size, size)
        colors, recognized = extract_face_colors(image, face_rect)

    return colors
